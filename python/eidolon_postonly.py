#!/usr/bin/env python3
"""post-only and pre-only controls for the within-subject design."""
import json
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import pandas as pd
from collections import Counter
from scipy.stats import binomtest
from sklearn.metrics import accuracy_score, top_k_accuracy_score
from sklearn.preprocessing import StandardScaler

from eidolon_features import FEATURE_NAMES
from eidolon_models import make_model

OUT = "results/within"
MODELS = ["logreg", "rf", "mlp", "hgb"]


def cluster_ci(df, n_boot=2000, seed=42):
    rng = np.random.default_rng(seed)
    pat = df.groupby("patient_id")["correct"].mean().to_numpy(float)
    vals = [float(np.mean(rng.choice(pat, size=len(pat), replace=True)))
            for _ in range(n_boot)]
    return [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))]


def exact_upper_zero(n, alpha=0.05):
    return float(1.0 - (alpha / 100.0) ** 0 if n == 0 else 1.0)


def run_split(feats, grp, train_w, test_w):
    d = feats[feats.group == grp]
    tr = d[d.window.isin(train_w)]
    te = d[d.window.isin(test_w)]
    scaler = StandardScaler().fit(tr[FEATURE_NAMES].to_numpy(float))
    xtr = scaler.transform(tr[FEATURE_NAMES].to_numpy(float))
    xte = scaler.transform(te[FEATURE_NAMES].to_numpy(float))
    ytr = tr.patient_id.to_numpy(int)
    yte = te.patient_id.to_numpy(int)
    rec = {}
    for name in MODELS:
        model = make_model(name).fit(xtr, ytr)
        pred = model.predict(xte)
        proba = model.predict_proba(xte)
        classes = model.classes_
        part = pd.DataFrame({
            "patient_id": yte, "group": grp, "model": name,
            "correct": (pred == yte).astype(int),
        })
        any_correct = part.groupby("patient_id")["correct"].max()
        k = int(any_correct.sum())
        n = int(len(any_correct))
        rec[name] = {
            "accuracy": float(accuracy_score(yte, pred)),
            "ci95": cluster_ci(part),
            "top5": float(top_k_accuracy_score(yte, proba, k=5, labels=classes)),
            "n_train": int(len(ytr)), "n_test": int(len(yte)),
            "patients_any_correct": k, "n_patients": n,
            "chance": float(1.0 / len(classes)),
        }
        if k == 0:
            rec[name]["exact_upper_95"] = float(
                1.0 - 0.05 ** (1.0 / n)) if n else 1.0
        else:
            rec[name]["exact_upper_95"] = None
    return rec


def profile_stats(feats, grp, windows):
    d = feats[(feats.group == grp) & (feats.window.isin(windows))]
    x = np.round(d[FEATURE_NAMES].to_numpy(float), 6)
    keys = [tuple(r) for r in x]
    counts = Counter(keys)
    pids = d.patient_id.to_numpy()
    sizes = {}
    for i, k in enumerate(keys):
        idx = [j for j, kk in enumerate(keys) if kk == k]
        pc = Counter(pids[idx])
        sizes[k] = max(pc.values()) / len(idx)
    return {
        "windows": int(len(d)), "distinct_profiles": int(len(counts)),
        "patients": int(d.patient_id.nunique()),
        "profile_fraction": float(len(counts) / len(d)),
        "largest_collision": int(max(counts.values())),
        "plurality_ceiling": float(np.mean([sizes[k] for k in keys])),
    }


def main():
    feats = pd.read_csv(os.path.join(OUT, "features.csv"))
    out = {"post_only": {}, "pre_only": {}, "domain_adapt": {},
           "profiles": {}}
    for grp in (1, 6, 7):
        out["post_only"][str(grp)] = run_split(feats, grp, [6, 7], [8, 9])
        out["pre_only"][str(grp)] = run_split(feats, grp, [1, 2], [3, 4])
        out["profiles"][str(grp)] = {
            "post": profile_stats(feats, grp, [6, 7, 8, 9]),
            "pre": profile_stats(feats, grp, [1, 2, 3, 4]),
        }
    with open(os.path.join(OUT, "postonly.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
