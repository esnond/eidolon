#!/usr/bin/env python3
"""matched 150-class sensitivity: equal class count and training size."""
import json
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, top_k_accuracy_score
from sklearn.preprocessing import StandardScaler

from eidolon_features import FEATURE_NAMES
from eidolon_models import make_model

OUT = "results"
MODELS = ["logreg", "rf", "mlp", "hgb"]


def cluster_ci(df, n_boot=2000, seed=42):
    rng = np.random.default_rng(seed)
    pat = df.groupby("patient_id")["correct"].mean().to_numpy(float)
    vals = [float(np.mean(rng.choice(pat, size=len(pat), replace=True)))
            for _ in range(n_boot)]
    return [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))]


def fit_eval(xtr, ytr, xte, yte, model_name):
    model = make_model(model_name).fit(xtr, ytr)
    pred = model.predict(xte)
    proba = model.predict_proba(xte)
    classes = model.classes_
    if len(classes) != len(np.unique(ytr)):
        raise ValueError("missing class in training")
    return model, pred, proba


def main():
    feats = pd.read_csv(os.path.join(OUT, "features.csv"))
    rng = np.random.default_rng(20261030)
    g1_patients = feats[feats.group == 1].patient_id.unique()
    chosen = np.sort(rng.choice(g1_patients, size=150, replace=False))
    feats = feats[~((feats.group == 1) & (~feats.patient_id.isin(chosen)))]
    out = {"chosen_g1_patients": int(len(chosen)), "groups": {},
           "selection": {}, "primary": {}}
    preds = []
    data = {}
    for grp in (1, 2, 3):
        d = feats[feats.group == grp]
        tr = d[d.window <= 5]
        te = d[d.window >= 6]
        scaler = StandardScaler().fit(tr[FEATURE_NAMES].to_numpy(float))
        data[grp] = {
            "xtr": scaler.transform(tr[FEATURE_NAMES].to_numpy(float)),
            "xte": scaler.transform(te[FEATURE_NAMES].to_numpy(float)),
            "ytr": tr.patient_id.to_numpy(int),
            "yte": te.patient_id.to_numpy(int),
            "test": te,
        }

    # selection on g1 train windows 1-3 vs 4-5
    d1 = feats[feats.group == 1]
    s_tr = d1[d1.window <= 3]
    s_va = d1[d1.window.isin([4, 5])]
    sc = StandardScaler().fit(s_tr[FEATURE_NAMES].to_numpy(float))
    xtr = sc.transform(s_tr[FEATURE_NAMES].to_numpy(float))
    xva = sc.transform(s_va[FEATURE_NAMES].to_numpy(float))
    ytr = s_tr.patient_id.to_numpy(int)
    yva = s_va.patient_id.to_numpy(int)
    best = None
    for name in MODELS:
        model, pred, proba = fit_eval(xtr, ytr, xva, yva, name)
        classes = np.unique(ytr)
        acc = float(accuracy_score(yva, pred))
        top5 = float(top_k_accuracy_score(yva, proba, k=5, labels=classes))
        out["selection"][name] = {"val_top1": acc, "val_top5": top5}
        if best is None or acc > best[1]:
            best = (name, acc)
    out["selected_model"] = best[0]

    for grp in (1, 2, 3):
        d = data[grp]
        rec = {}
        for name in MODELS:
            model, pred, proba = fit_eval(d["xtr"], d["ytr"], d["xte"], d["yte"], name)
            classes = np.unique(d["ytr"])
            part = pd.DataFrame({
                "patient_id": d["yte"], "group": grp, "model": name,
                "correct": (pred == d["yte"]).astype(int),
            })
            rec[name] = {
                "accuracy": float(accuracy_score(d["yte"], pred)),
                "ci95": cluster_ci(part),
                "top5": float(top_k_accuracy_score(d["yte"], proba, k=5,
                                                   labels=classes)),
                "chance": float(1.0 / len(classes)),
                "n_train": int(len(d["ytr"])), "n_test": int(len(d["yte"])),
            }
            preds.append(part)
        out["groups"][str(grp)] = rec

    # primary selected model applied to all groups
    for grp in (1, 2, 3):
        d = data[grp]
        model, pred, proba = fit_eval(d["xtr"], d["ytr"], d["xte"], d["yte"],
                                      out["selected_model"])
        classes = np.unique(d["ytr"])
        part = pd.DataFrame({
            "patient_id": d["yte"], "group": grp,
            "model": out["selected_model"],
            "correct": (pred == d["yte"]).astype(int),
        })
        out["primary"][str(grp)] = {
            "accuracy": float(accuracy_score(d["yte"], pred)),
            "ci95": cluster_ci(part),
            "top5": float(top_k_accuracy_score(d["yte"], proba, k=5,
                                               labels=classes)),
        }
    pd.concat(preds, ignore_index=True).to_csv(
        os.path.join(OUT, "matched_predictions.csv"), index=False)
    with open(os.path.join(OUT, "matched.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
