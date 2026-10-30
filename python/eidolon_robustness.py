#!/usr/bin/env python3
"""robustness checks requested by adversarial review. read only inputs."""
import json
import os
from collections import Counter

import numpy as np
import pandas as pd
from scipy.stats import binomtest, kruskal, mannwhitneyu, spearmanr, wilcoxon
from sklearn.covariance import LedoitWolf
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from sklearn.metrics import roc_auc_score
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

from eidolon_features import FEATURE_NAMES

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


def cluster_auc(df, score_col, n_boot=1000, seed=42):
    y = (df["group"] != 1).astype(int).to_numpy()
    score = df[score_col].to_numpy(float)
    auc = float(roc_auc_score(y, score))
    groups = {pid: sub for pid, sub in df.groupby("patient_id")}
    pids = np.array(list(groups.keys()))
    rng = np.random.default_rng(seed)
    boot = []
    for _ in range(n_boot):
        pick = rng.choice(pids, size=len(pids), replace=True)
        sub = pd.concat([groups[p] for p in pick], ignore_index=True)
        yy = (sub["group"] != 1).astype(int).to_numpy()
        boot.append(roc_auc_score(yy, sub[score_col].to_numpy(float)))
    return auc, [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))]


def collision_stats(feats, group):
    d = feats[(feats.group == group) & (feats.window >= 6)]
    x = np.round(d[FEATURE_NAMES].to_numpy(float), 6)
    keys = [tuple(row) for row in x]
    counts = Counter(keys)
    sizes = np.array([counts[k] for k in keys], float)
    pids = d.patient_id.to_numpy()
    plurality = 0.0
    for i, k in enumerate(keys):
        idx = [j for j, kk in enumerate(keys) if kk == k]
        pc = Counter(pids[idx])
        plurality += max(pc.values()) / len(idx)
    plurality /= len(keys)
    per_patient = d.groupby("patient_id").size().to_numpy()
    return {
        "windows": int(len(d)),
        "distinct_profiles": int(len(counts)),
        "largest_collision": int(sizes.max()),
        "median_collision": float(np.median(sizes)),
        "profile_fraction": float(len(counts) / len(d)),
        "plurality_ceiling": float(plurality),
        "patients": int(d.patient_id.nunique()),
        "windows_per_patient": float(np.mean(per_patient)),
    }


def heldout_reference(feats):
    x = feats[FEATURE_NAMES].to_numpy(float)
    x = np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)
    g1_train = (feats.group == 1) & (feats.window <= 5)
    ref_patients = feats.loc[g1_train, "patient_id"].unique()[:100]
    ref = g1_train & feats.patient_id.isin(ref_patients).to_numpy()
    scaler = StandardScaler().fit(x[ref])
    zs = scaler.transform(x)
    pca = PCA(n_components=20, whiten=True, random_state=42).fit(zs[ref])
    z = pca.transform(zs)
    nn = NearestNeighbors(n_neighbors=10).fit(z[ref])
    dist = nn.kneighbors(z, return_distance=True)[0].mean(axis=1)
    iso = IsolationForest(n_estimators=400, random_state=42, n_jobs=1).fit(z[ref])
    anom = -iso.score_samples(z)
    out = {}
    test = feats.window >= 6
    for g in (1, 2, 3, 4):
        mask = test & (feats.group == g).to_numpy()
        out[str(g)] = {"n": int(mask.sum()),
                       "idu_nat_mean": float(np.mean(dist[mask])),
                       "anomaly_mean": float(np.mean(anom[mask]))}
    return out


def main():
    feats = pd.read_csv(os.path.join(OUT, "features.csv"))
    pm = pd.read_csv(os.path.join(OUT, "patient_metrics.csv"))
    pred = pd.read_csv(os.path.join(OUT, "predictions.csv"))
    models = json.load(open(os.path.join(OUT, "models.json")))
    seed2 = json.load(open(os.path.join(OUT, "seed_replication.json")))
    out = {"collisions": {}, "univariate_anomaly": {}, "idu_cohort": {},
           "h7_patient_level": {}, "h3_window_auc": {},
           "heldout_g1_reference": {}, "multiplicity_7": {}}

    for g in (1, 2, 3, 4):
        out["collisions"][str(g)] = collision_stats(feats, g)

    test = feats[feats.window >= 6].copy()
    for feat in FEATURE_NAMES:
        a = test[test.group == 1][feat].to_numpy(float)
        b = test[test.group == 3][feat].to_numpy(float)
        auc = float(roc_auc_score(np.r_[np.zeros(len(a)), np.ones(len(b))],
                                  np.r_[a, b]))
        out["univariate_anomaly"][feat] = float(max(auc, 1 - auc))
    out["univariate_anomaly"] = dict(sorted(
        out["univariate_anomaly"].items(), key=lambda kv: kv[1], reverse=True)[:10])

    for g in (2, 3, 4):
        d = test[test.group.isin([1, g])][["patient_id", "group", "anomaly"]]
        auc, ci = cluster_auc(d, "anomaly")
        out["h3_window_auc"][f"g{g}_vs_g1"] = {"auc": auc, "ci95": ci,
                                                "n_windows": int(len(d))}

    for g in (1, 2, 3, 4):
        v = pm[pm.group == g].idu_cohort.to_numpy()
        out["idu_cohort"][str(g)] = {
            "mean": float(np.mean(v)), "sd": float(np.std(v, ddof=1)),
            "n": int(len(v)),
            "ci95": [float(np.percentile(np.random.default_rng(42).choice(
                v, size=(5000, len(v)), replace=True).mean(axis=1), 2.5)),
                float(np.percentile(np.random.default_rng(42).choice(
                    v, size=(5000, len(v)), replace=True).mean(axis=1), 97.5))],
        }
    pairs = [(1, 2), (1, 3), (2, 3)]
    raw = []
    for a, b in pairs:
        aa = pm[pm.group == a].idu_cohort.to_numpy()
        bb = pm[pm.group == b].idu_cohort.to_numpy()
        raw.append(mannwhitneyu(aa, bb).pvalue)
    adj = holm(raw)
    out["idu_cohort"]["pairwise"] = [
        {"a": a, "b": b, "p": float(p), "p_holm": float(pa)}
        for (a, b), p, pa in zip(pairs, raw, adj)]

    acc = pred[pred.model != "dummy"]
    pat = acc.groupby(["patient_id", "group"], as_index=False)["correct"].mean()
    pat = pat.rename(columns={"correct": "consensus_accuracy"})
    m = pm.merge(pat, on=["patient_id", "group"])
    d = m[m.group == 1]
    rho, p = spearmanr(d.idu_cohort, d.consensus_accuracy)
    out["idu_cohort"]["h4_cohort"] = {"rho": float(rho), "p": float(p),
                                      "n": int(len(d))}

    g4 = pred[(pred.group == 4)]
    raw = []
    for name in models["4"].keys():
        sub = g4[g4.model == name]
        anycorrect = sub.groupby("patient_id")["correct"].max()
        k = int(anycorrect.sum())
        n = int(len(anycorrect))
        chance = models["4"][name]["chance"]
        p_any = 1.0 - (1.0 - chance) ** 4
        bt = binomtest(k, n, p_any, alternative="greater")
        raw.append(bt.pvalue)
        out["h7_patient_level"][name] = {
            "patients_any_correct": k, "n_patients": n,
            "expected_any_chance": n * p_any,
            "p": float(bt.pvalue),
            "seed2_accuracy": seed2["20261031"]["accuracy"]["4"].get(name),
            "primary_accuracy": models["4"][name]["accuracy"],
        }
    adj = holm(raw)
    for (name, rec), pa in zip(out["h7_patient_level"].items(), adj):
        rec["p_holm_5_models"] = float(pa)

    out["heldout_g1_reference"] = heldout_reference(feats)

    pvals = [
        float(kruskal(*[pm.loc[pm.group == g, "idu_nat"] for g in (1, 2, 3)]).pvalue),
        float(mannwhitneyu(pat.loc[pat.group == 2, "consensus_accuracy"],
                           pat.loc[pat.group == 3, "consensus_accuracy"]).pvalue),
        float(mannwhitneyu(pm.loc[pm.group == 3, "anomaly"],
                           pm.loc[pm.group == 1, "anomaly"]).pvalue),
        float(spearmanr(m.loc[m.group == 1, "idu_nat"],
                        m.loc[m.group == 1, "consensus_accuracy"]).pvalue),
        float(wilcoxon(
            pd.read_csv(os.path.join(OUT, "forecast_patient.csv")).query(
                "cohort=='chaos' and target=='events' and horizon=='days_31_60'"
            ).sort_values("patient_id")["accuracy"].to_numpy(),
            pd.read_csv(os.path.join(OUT, "forecast_patient.csv")).query(
                "cohort=='chaos' and target=='events' and horizon=='days_61_90'"
            ).sort_values("patient_id")["accuracy"].to_numpy()).pvalue),
        1.0,
        float(out["h7_patient_level"]["rf"]["p_holm_5_models"]),
    ]
    adj = holm(pvals)
    names = ["h1", "h2", "h3", "h4", "h5", "h6", "h7"]
    out["multiplicity_7"] = {
        name: {"p": float(p), "p_holm": float(pa)}
        for name, p, pa in zip(names, pvals, adj)}

    with open(os.path.join(OUT, "robustness.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
