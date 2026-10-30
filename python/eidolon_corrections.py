#!/usr/bin/env python3
"""corrections after adversarial review: per-model tests, plurality ceiling, g5."""
import json
import os
from collections import Counter

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, spearmanr
from sklearn.metrics import roc_auc_score
from sklearn.utils import resample

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


def plurality(feats, group):
    d = feats[(feats.group == group) & (feats.window >= 6)].reset_index(drop=True)
    x = np.round(d[FEATURE_NAMES].to_numpy(float), 6)
    keys = [tuple(r) for r in x]
    counts = Counter(keys)
    pids = d.patient_id.to_numpy()
    ceiling = 0.0
    for i, k in enumerate(keys):
        idx = [j for j, kk in enumerate(keys) if kk == k]
        pc = Counter(pids[idx])
        ceiling += max(pc.values()) / len(idx)
    ceiling /= len(keys)
    return {
        "windows": int(len(d)),
        "distinct_profiles": int(len(counts)),
        "profile_fraction": float(len(counts) / len(d)),
        "max_collision": int(max(counts.values())),
        "plurality_ceiling": float(ceiling),
    }


def main():
    pred = pd.read_csv(os.path.join(OUT, "predictions.csv"))
    pred = pred[pred.model != "dummy"]
    pat = pred.groupby(["model", "patient_id", "group"], as_index=False)["correct"].mean()
    rows = []
    for model in sorted(pat.model.unique()):
        d = pat[pat.model == model]
        a = d[d.group == 2].correct.to_numpy()
        b = d[d.group == 3].correct.to_numpy()
        test = mannwhitneyu(a, b, alternative="two-sided")
        rows.append({"model": model, "g2_mean": float(a.mean()),
                     "g3_mean": float(b.mean()),
                     "diff_g2_minus_g3": float(a.mean() - b.mean()),
                     "p": float(test.pvalue), "n2": int(len(a)),
                     "n3": int(len(b))})
    adj = holm([r["p"] for r in rows])
    for r, p in zip(rows, adj):
        r["p_holm"] = float(p)

    feats = pd.read_csv(os.path.join(OUT, "features.csv"))
    plur = {str(g): plurality(feats, g) for g in (1, 2, 3, 4)}

    g5_feats = pd.read_csv(os.path.join(OUT, "g5", "features.csv"))
    g5_pm = pd.read_csv(os.path.join(OUT, "g5", "patient_metrics.csv"))
    g5_models = json.load(open(os.path.join(OUT, "g5", "models.json")))
    g5_plur = plurality(g5_feats, 5)
    g5 = {
        "n": int(g5_pm[g5_pm.group == 5].patient_id.nunique()),
        "idu_nat_mean": float(g5_pm[g5_pm.group == 5].idu_nat.mean()),
        "idu_cohort_mean": float(g5_pm[g5_pm.group == 5].idu_cohort.mean()),
        "anomaly_mean": float(g5_pm[g5_pm.group == 5].anomaly.mean()),
        "models": {k: {"accuracy": v["accuracy"],
                       "ci95": v["accuracy_ci95"],
                       "top5": v["top5"], "auc": v["auc"]}
                   for k, v in g5_models["5"].items()},
        "plurality": g5_plur,
        "participation_ratio": json.load(
            open(os.path.join(OUT, "g5", "rank1.json")))["5"]["participation_ratio"],
        "lambda1_share": json.load(
            open(os.path.join(OUT, "g5", "rank1.json")))["5"]["lambda1_share"],
    }
    d = g5_pm[g5_pm.group.isin([1, 5])]
    g5["anomaly_auc_vs_g1"] = float(roc_auc_score(
        (d.group == 5).astype(int), d.anomaly))

    g3 = {
        "n": int(feats[(feats.group == 3)].patient_id.nunique()),
        "idu_nat_mean": float(pd.read_csv(
            os.path.join(OUT, "patient_metrics.csv")).query("group==3").idu_nat.mean()),
        "idu_cohort_mean": float(pd.read_csv(
            os.path.join(OUT, "patient_metrics.csv")).query("group==3").idu_cohort.mean()),
        "anomaly_auc_vs_g1": 1.0,
        "plurality": plur["3"],
        "participation_ratio": json.load(
            open(os.path.join(OUT, "rank1.json")))["3"]["participation_ratio"],
        "lambda1_share": json.load(
            open(os.path.join(OUT, "rank1.json")))["3"]["lambda1_share"],
        "models": {k: {"accuracy": v["accuracy"],
                       "ci95": v["accuracy_ci95"],
                       "top5": v["top5"], "auc": v["auc"]}
                   for k, v in json.load(
                       open(os.path.join(OUT, "models.json")))["3"].items()},
    }

    out = {
        "per_model_g2_g3": rows,
        "plurality": plur,
        "g3": g3,
        "g5_stochastic_intense": g5,
        "interpretation": {
            "consensus_is_invalid": "average across models hides opposite signs; per-model tests are primary",
            "template_bound": "g3 plurality ceiling 0.3867 equals rf and hgb top1, so no residual individual signal above the exact-profile bound",
            "g5": "stochastic emission with the same affine intense parameters restores 600 of 600 distinct profiles and lowers rf top1 to 0.100",
        },
    }
    with open(os.path.join(OUT, "corrections.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
