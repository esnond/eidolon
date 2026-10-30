#!/usr/bin/env python3
"""group statistics, effect sizes, ci95, multiplicity. deterministic."""
import json
import math
import os

import numpy as np
import pandas as pd
from scipy.stats import (binomtest, kruskal, mannwhitneyu, nct, rankdata,
                         spearmanr, t, wilcoxon)
from sklearn.metrics import roc_auc_score

from eidolon_features import CATEGORIES, FEATURE_NAMES

OUT = "results"


def holm(pvals):
    p = np.asarray(pvals, float)
    order = np.argsort(p)
    m = len(p)
    adj = np.empty(m)
    prev = 0.0
    for rank, idx in enumerate(order):
        val = (m - rank) * p[idx]
        val = max(val, prev)
        adj[idx] = min(val, 1.0)
        prev = adj[idx]
    return adj


def summarize(x, n_boot=5000, seed=42):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    if len(x) == 0:
        return {"mean": float("nan"), "sd": float("nan"), "n": 0,
                "ci95": [float("nan"), float("nan")]}
    rng = np.random.default_rng(seed)
    boot = [float(np.mean(rng.choice(x, size=len(x), replace=True)))
            for _ in range(n_boot)]
    return {"mean": float(np.mean(x)), "sd": float(np.std(x, ddof=1)),
            "n": int(len(x)), "ci95": [float(np.percentile(boot, 2.5)),
                                       float(np.percentile(boot, 97.5))]}


def cohen_d(a, b, n_boot=2000, seed=42):
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    n1, n2 = len(a), len(b)
    pooled = np.sqrt(((n1 - 1) * np.var(a, ddof=1)
                      + (n2 - 1) * np.var(b, ddof=1)) / (n1 + n2 - 2))
    d = float((np.mean(a) - np.mean(b)) / pooled) if pooled > 0 else float("nan")
    rng = np.random.default_rng(seed)
    boot = []
    for _ in range(n_boot):
        aa = rng.choice(a, size=n1, replace=True)
        bb = rng.choice(b, size=n2, replace=True)
        p = np.sqrt(((n1 - 1) * np.var(aa, ddof=1)
                     + (n2 - 1) * np.var(bb, ddof=1)) / (n1 + n2 - 2))
        boot.append((np.mean(aa) - np.mean(bb)) / p if p > 0 else 0.0)
    return {"d": d, "ci95": [float(np.percentile(boot, 2.5)),
                             float(np.percentile(boot, 97.5))]}


def auc_ci(y, score, n_boot=1000, seed=42):
    y = np.asarray(y, int)
    score = np.asarray(score, float)
    auc = float(roc_auc_score(y, score))
    rng = np.random.default_rng(seed)
    pos = np.where(y == 1)[0]
    neg = np.where(y == 0)[0]
    boot = []
    for _ in range(n_boot):
        ip = rng.choice(pos, size=len(pos), replace=True)
        ineg = rng.choice(neg, size=len(neg), replace=True)
        yy = np.r_[np.ones(len(ip)), np.zeros(len(ineg))]
        ss = np.r_[score[ip], score[ineg]]
        boot.append(roc_auc_score(yy, ss))
    return {"auc": auc, "ci95": [float(np.percentile(boot, 2.5)),
                                 float(np.percentile(boot, 97.5))],
            "n_pos": int(len(pos)), "n_neg": int(len(neg))}


def spearman_ci(x, y, n_boot=4000, seed=42):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    rho, p = spearmanr(x, y)
    rng = np.random.default_rng(seed)
    boot = []
    for _ in range(n_boot):
        idx = rng.choice(len(x), size=len(x), replace=True)
        boot.append(spearmanr(x[idx], y[idx]).statistic)
    return {"rho": float(rho), "p": float(p),
            "ci95": [float(np.percentile(boot, 2.5)),
                     float(np.percentile(boot, 97.5))], "n": int(len(x))}


def power_t(d, n, alpha):
    df = 2 * n - 2
    nc = abs(d) * np.sqrt(n / 2.0)
    crit = t.ppf(1 - alpha / 2.0, df)
    return float(1 - nct.cdf(crit, df, nc) + nct.cdf(-crit, df, nc))


def clean_json(obj):
    if isinstance(obj, dict):
        return {k: clean_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean_json(v) for v in obj]
    if isinstance(obj, float) and not math.isfinite(obj):
        return None
    return obj

def main():
    pm = pd.read_csv(os.path.join(OUT, "patient_metrics.csv"))
    pred = pd.read_csv(os.path.join(OUT, "predictions.csv"))
    models = json.load(open(os.path.join(OUT, "models.json")))
    rank1 = json.load(open(os.path.join(OUT, "rank1.json")))
    forecast = json.load(open(os.path.join(OUT, "forecast.json")))
    fp = pd.read_csv(os.path.join(OUT, "forecast_patient.csv"))
    feats = pd.read_csv(os.path.join(OUT, "features.csv"))
    imp = pd.read_csv(os.path.join(OUT, "importance.csv"))
    summary = json.load(open(os.path.join(OUT, "cohort_summary.json")))
    stats = {"cohort": summary, "hypotheses": {}}

    # h1 idu gradient
    h1 = {"groups": {}, "pairwise": []}
    for g in (1, 2, 3, 4):
        h1["groups"][str(g)] = summarize(pm.loc[pm.group == g, "idu_nat"])
    x = [pm.loc[pm.group == g, "idu_nat"].to_numpy() for g in (1, 2, 3)]
    kw = kruskal(*x)
    n = sum(len(v) for v in x)
    eta = (kw.statistic - 3 + 1) / (n - 3)
    h1["kruskal"] = {"H": float(kw.statistic), "p": float(kw.pvalue),
                     "eta_squared": float(eta), "n": int(n)}
    pairs = [(1, 2), (1, 3), (2, 3)]
    raw = []
    for a, b in pairs:
        aa = pm.loc[pm.group == a, "idu_nat"].to_numpy()
        bb = pm.loc[pm.group == b, "idu_nat"].to_numpy()
        u = mannwhitneyu(aa, bb, alternative="two-sided")
        raw.append(u.pvalue)
    adj = holm(raw)
    for (a, b), p, pa in zip(pairs, raw, adj):
        aa = pm.loc[pm.group == a, "idu_nat"].to_numpy()
        bb = pm.loc[pm.group == b, "idu_nat"].to_numpy()
        h1["pairwise"].append({"a": a, "b": b, "mean_a": float(np.mean(aa)),
                               "mean_b": float(np.mean(bb)),
                               "d": cohen_d(aa, bb), "p": float(p),
                               "p_holm": float(pa)})
    h1["g4_vs_g1"] = {"d": cohen_d(
        pm.loc[pm.group == 4, "idu_nat"], pm.loc[pm.group == 1, "idu_nat"])}
    h1["verdict"] = bool(
        h1["groups"]["3"]["mean"] > h1["groups"]["2"]["mean"]
        > h1["groups"]["1"]["mean"]
        and abs(h1["pairwise"][1]["d"]["d"]) >= 0.8)
    h1["note"] = ("idu_nat is distance to the natural manifold, not cohort "
                  "uniqueness; idu_cohort is reported in robustness.json and "
                  "shows the opposite direction for g3")
    stats["hypotheses"]["h1"] = h1

    # h2 closed set identification
    acc = pred[pred.model != "dummy"].copy()
    pat = acc.groupby(["patient_id", "group"], as_index=False)["correct"].mean()
    pat = pat.rename(columns={"correct": "consensus_accuracy"})
    h2 = {"consensus": {}, "models": {}, "pairwise": []}
    for g in (1, 2, 3, 4):
        h2["consensus"][str(g)] = summarize(
            pat.loc[pat.group == g, "consensus_accuracy"])
        h2["models"][str(g)] = models[str(g)]
    pairs = [(1, 2), (1, 3), (2, 3)]
    raw = []
    for a, b in pairs:
        aa = pat.loc[pat.group == a, "consensus_accuracy"].to_numpy()
        bb = pat.loc[pat.group == b, "consensus_accuracy"].to_numpy()
        raw.append(mannwhitneyu(aa, bb, alternative="two-sided").pvalue)
    adj = holm(raw)
    for (a, b), p, pa in zip(pairs, raw, adj):
        aa = pat.loc[pat.group == a, "consensus_accuracy"].to_numpy()
        bb = pat.loc[pat.group == b, "consensus_accuracy"].to_numpy()
        h2["pairwise"].append({"a": a, "b": b, "mean_a": float(np.mean(aa)),
                               "mean_b": float(np.mean(bb)),
                               "d": cohen_d(aa, bb), "p": float(p),
                               "p_holm": float(pa)})
    h2["verdict"] = False
    per = {}
    raw_per = []
    for model in sorted(acc.model.unique()):
        d = acc[acc.model == model].groupby("patient_id").agg(
            group=("group", "first"), correct=("correct", "mean")).reset_index()
        a = d[d.group == 2].correct.to_numpy()
        b = d[d.group == 3].correct.to_numpy()
        test = mannwhitneyu(a, b, alternative="two-sided")
        per[model] = {"g2_mean": float(np.mean(a)), "g3_mean": float(np.mean(b)),
                      "diff_g2_minus_g3": float(np.mean(a) - np.mean(b)),
                      "p": float(test.pvalue), "n2": int(len(a)),
                      "n3": int(len(b))}
        raw_per.append(test.pvalue)
    adj_per = holm(raw_per)
    for (model, rec), pa in zip(per.items(), adj_per):
        rec["p_holm"] = float(pa)
    h2["per_model_g2_g3"] = per
    h2["note"] = ("mean_model_accuracy is descriptive, not a test; per-model "
                  "tests disagree in direction. supported pattern is g1 >> g2/g3, "
                  "not a strict order and not g2 approximately g3.")
    stats["hypotheses"]["h2"] = h2

    # h3 anomaly auc
    h3 = {"anomaly": {}, "mahalanobis": {}}
    for name, col in (("anomaly", "anomaly"), ("mahalanobis", "mahalanobis")):
        for g in (2, 3, 4):
            d = pm[pm.group.isin([1, g])]
            y = (d.group == g).astype(int)
            h3[name][f"g{g}_vs_g1"] = auc_ci(y, d[col])
    h3["verdict"] = bool(
        h3["anomaly"]["g3_vs_g1"]["auc"] >= 0.80
        and h3["anomaly"]["g3_vs_g1"]["ci95"][0] > 0.50)
    stats["hypotheses"]["h3"] = h3

    # h4 uniqueness vs identification
    m = pm.merge(pat, on=["patient_id", "group"], how="left")
    h4 = {"overall": spearman_ci(m.idu_nat, m.consensus_accuracy), "within": {}}
    raw = []
    for g in (1, 2, 3, 4):
        d = m[m.group == g]
        h4["within"][str(g)] = spearman_ci(d.idu_nat, d.consensus_accuracy)
        raw.append(h4["within"][str(g)]["p"])
    adj = holm(raw)
    for g, pa in zip((1, 2, 3, 4), adj):
        h4["within"][str(g)]["p_holm"] = float(pa)
    h4["verdict"] = bool(
        h4["within"]["1"]["rho"] >= 0.20
        and h4["within"]["1"]["p_holm"] < 0.05)
    stats["hypotheses"]["h4"] = h4

    # h5 forecast degradation in chaos
    h5 = {"chaos": {}, "g1": {}, "verdict": False}
    for cohort in ("chaos", "g1"):
        for target in ("events", "mean_start"):
            d = fp[(fp.cohort == cohort) & (fp.target == target)]
            piv = d.pivot_table(index="patient_id", columns="horizon",
                                values="accuracy")
            a = piv["days_31_60"].to_numpy()
            b = piv["days_61_90"].to_numpy()
            diff = a - b
            rng = np.random.default_rng(42)
            boot = [float(np.mean(rng.choice(diff, size=len(diff), replace=True)))
                    for _ in range(4000)]
            dz = float(np.mean(diff) / np.std(diff, ddof=1)) if np.std(diff) > 0 else float("nan")
            rec = {"n": int(len(diff)), "mean_a": float(np.mean(a)),
                   "mean_b": float(np.mean(b)), "mean_diff": float(np.mean(diff)),
                   "diff_ci95": [float(np.percentile(boot, 2.5)),
                                 float(np.percentile(boot, 97.5))],
                   "cohen_dz": dz,
                   "wilcoxon_p": float(wilcoxon(a, b).pvalue)}
            h5[cohort][target] = rec
    h5["verdict"] = bool(
        h5["chaos"]["events"]["mean_diff"] > 0
        and h5["chaos"]["events"]["wilcoxon_p"] < 0.05)
    h5["global"] = {"cohort": forecast["cohort"], "chaos": forecast["chaos"]}
    stats["hypotheses"]["h5"] = h5

    # h6 rank one
    h6 = {"operational": rank1, "verdict": False,
          "posthoc_rank": {}}
    for g in (1, 2, 3, 4):
        d = feats[(feats.group == g) & (feats.window >= 6)]
        mat = d.groupby("patient_id")[FEATURE_NAMES].mean().to_numpy(float)
        mat = mat[:, np.std(mat, axis=0) > 1e-12]
        ranked = np.apply_along_axis(rankdata, 0, mat)
        corr = np.abs(np.corrcoef(ranked, rowvar=False))
        corr = np.nan_to_num(corr, nan=0.0)
        np.fill_diagonal(corr, 1.0)
        ev = np.linalg.eigvalsh(corr)
        ev = np.clip(ev, 0, None)
        h6["posthoc_rank"][str(g)] = {
            "spearman_abs_lambda1_share": float(ev[-1] / ev.sum()),
            "participation_ratio": float((ev.sum() ** 2) / np.sum(ev ** 2)),
        }
    h6["verdict"] = bool(
        rank1["3"]["participation_ratio"] < 2.0
        and rank1["3"]["lambda1_share"] > 0.80)
    stats["hypotheses"]["h6"] = h6

    # h7 random control
    h7 = {"models": {}, "verdict": True}
    raw = []
    for name, rec in models["4"].items():
        k = int(round(rec["accuracy"] * rec["n_test"]))
        test = binomtest(k, rec["n_test"], rec["chance"], alternative="greater")
        h7["models"][name] = {
            "accuracy": rec["accuracy"], "chance": rec["chance"],
            "risk_difference": rec["accuracy"] - rec["chance"],
            "p": float(test.pvalue), "n": rec["n_test"],
        }
        raw.append(test.pvalue)
    adj = holm(raw)
    for (name, rec), pa in zip(h7["models"].items(), adj):
        rec["p_holm"] = float(pa)
    h7["verdict"] = "inconclusive"
    h7["note"] = ("window-level holm is 0.039 for rf; patient-level holm is 0.087 "
                  "for five models and 0.348 for seven tests; seed2 rf is 0.0075; "
                  "overfitting is not stable, see robustness.json")
    stats["hypotheses"]["h7"] = h7

    # power
    stats["power"] = {
        "a_priori_d_0.5_n150_alpha_0.05_7": power_t(0.5, 150, 0.05 / 7),
        "achieved_h1_d": h1["pairwise"][1]["d"]["d"],
        "achieved_h1_power": power_t(h1["pairwise"][1]["d"]["d"], 150, 0.05 / 7),
        "note": "post hoc power is reported for interpretation only",
    }

    # tables
    t1 = []
    for g in (1, 2, 3, 4):
        d = pm[pm.group == g]
        t1.append({"group": g, "n_patients": int(len(d)),
                   "n_windows": int(d.n_windows.sum()),
                   "idu_nat_mean": d.idu_nat.mean(), "idu_nat_sd": d.idu_nat.std(),
                   "idu_cohort_mean": d.idu_cohort.mean(),
                   "anomaly_mean": d.anomaly.mean()})
    pd.DataFrame(t1).to_csv(os.path.join(OUT, "table1_cohort.csv"), index=False)
    beh = ["n_events", "sessions_per_day", "interval_mean_log", "interval_cv",
           "action_entropy", "higuchi_fd", "weekend_start_shift_h",
           "daily_events_cv"]
    t2 = feats[feats.window >= 6].groupby("group")[beh].agg(
        ["mean", "std", "count"])
    t2.to_csv(os.path.join(OUT, "table2_behavior.csv"))
    rows = []
    for metric in ("idu_nat", "consensus_accuracy"):
        src = pm if metric == "idu_nat" else pat
        for a, b in ((1, 2), (1, 3), (2, 3)):
            aa = src.loc[src.group == a, metric].to_numpy()
            bb = src.loc[src.group == b, metric].to_numpy()
            rows.append({"metric": metric, "a": a, "b": b,
                         "mean_a": np.mean(aa), "mean_b": np.mean(bb),
                         "cohen_d": cohen_d(aa, bb)["d"],
                         "d_ci_low": cohen_d(aa, bb)["ci95"][0],
                         "d_ci_high": cohen_d(aa, bb)["ci95"][1],
                         "mann_whitney_p": mannwhitneyu(aa, bb).pvalue})
    t3 = pd.DataFrame(rows)
    t3["p_holm"] = np.nan
    for metric in t3.metric.unique():
        mask = t3.metric == metric
        t3.loc[mask, "p_holm"] = holm(t3.loc[mask, "mann_whitney_p"])
    t3.to_csv(os.path.join(OUT, "table3_groups.csv"), index=False)
    t4 = []
    for g, recs in models.items():
        for name, r in recs.items():
            t4.append({"group": int(g), "model": name,
                       "accuracy": r["accuracy"],
                       "acc_ci_low": r["accuracy_ci95"][0],
                       "acc_ci_high": r["accuracy_ci95"][1],
                       "balanced_accuracy": r["balanced_accuracy"],
                       "macro_f1": r["macro_f1"], "top5": r["top5"],
                       "auc": r["auc"], "chance": r["chance"],
                       "n_train": r["n_train"], "n_test": r["n_test"],
                       "seconds": r["seconds"]})
    pd.DataFrame(t4).to_csv(os.path.join(OUT, "table4_models.csv"), index=False)
    t5 = imp[imp.group == 1].sort_values("perm_mean", ascending=False).head(15)
    t5.to_csv(os.path.join(OUT, "table5_importance.csv"), index=False)
    t6 = []
    for cohort in ("g1", "g2", "g3", "g4", "chaos"):
        for target in ("events", "mean_start"):
            if cohort.startswith("g"):
                src = forecast["cohort"][target].get(cohort[1:])
            else:
                src = forecast["chaos"][target]
            if src is None:
                continue
            for horizon, r in src.items():
                t6.append({"cohort": cohort, "target": target,
                           "horizon": horizon, "accuracy": r["accuracy"],
                           "acc_ci_low": r["accuracy_ci95"][0],
                           "acc_ci_high": r["accuracy_ci95"][1],
                           "r2": r["r2"],
                           "within_r2": r["within_patient_r2_mean"],
                           "mae": r["mae"], "mean_target": r["mean_target"]})
    pd.DataFrame(t6).to_csv(os.path.join(OUT, "table6_forecast.csv"), index=False)
    with open(os.path.join(OUT, "stats.json"), "w", encoding="utf-8") as f:
        json.dump(clean_json(stats), f, indent=2)
    print(json.dumps(stats["hypotheses"], indent=2))


if __name__ == "__main__":
    main()
