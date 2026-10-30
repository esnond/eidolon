#!/usr/bin/env python3
"""within-subject switch: pre days 1-45, post days 46-90."""
import json
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
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


def main():
    feats = pd.read_csv(os.path.join(OUT, "features.csv"))
    out = {"groups": {}, "drift": {}, "n_patients": {}}
    preds = []
    for grp in (1, 6, 7):
        d = feats[feats.group == grp]
        tr = d[d.window <= 4]
        te = d[d.window >= 6]
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
            rec[name] = {
                "accuracy": float(accuracy_score(yte, pred)),
                "ci95": cluster_ci(part),
                "top5": float(top_k_accuracy_score(yte, proba, k=5,
                                                   labels=classes)),
                "chance": float(1.0 / len(classes)),
                "n_train": int(len(ytr)), "n_test": int(len(yte)),
            }
            preds.append(part)
        out["groups"][str(grp)] = rec
        out["n_patients"][str(grp)] = int(d.patient_id.nunique())

    # pre/post drift in g1-reference pca space, fit on g1 pre windows
    x = feats[FEATURE_NAMES].to_numpy(float)
    scaler = StandardScaler().fit(
        feats[(feats.group == 1) & (feats.window <= 4)][FEATURE_NAMES].to_numpy(float))
    zs = scaler.transform(x)
    pca = PCA(n_components=20, whiten=True, random_state=42).fit(
        zs[(feats.group == 1) & (feats.window <= 4).to_numpy()])
    z = pca.transform(zs)
    frame = feats[["patient_id", "group", "window"]].copy()
    frame["z"] = list(z)
    for grp in (1, 6, 7):
        d = frame[frame.group == grp]
        dist = []
        for pid, g in d.groupby("patient_id"):
            pre = np.mean(np.vstack(g[g.window <= 4].z.to_numpy()), axis=0)
            post = np.mean(np.vstack(g[g.window >= 6].z.to_numpy()), axis=0)
            dist.append(float(np.linalg.norm(post - pre)))
        out["drift"][str(grp)] = {
            "mean": float(np.mean(dist)), "sd": float(np.std(dist, ddof=1)),
            "n": int(len(dist)),
            "ci95": [float(np.percentile(np.random.default_rng(42).choice(
                dist, size=(5000, len(dist)), replace=True).mean(axis=1), 2.5)),
                float(np.percentile(np.random.default_rng(42).choice(
                    dist, size=(5000, len(dist)), replace=True).mean(axis=1), 97.5))],
        }
    pd.concat(preds, ignore_index=True).to_csv(
        os.path.join(OUT, "predictions.csv"), index=False)
    with open(os.path.join(OUT, "models.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
