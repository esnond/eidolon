#!/usr/bin/env python3
"""closed-set re-identification models. deterministic, single threaded."""
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import time

import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, balanced_accuracy_score,
                             f1_score, roc_auc_score, top_k_accuracy_score)
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

from eidolon_features import CATEGORIES, FEATURE_NAMES


def make_model(name):
    if name == "dummy":
        return DummyClassifier(strategy="stratified", random_state=42)
    if name == "logreg":
        return LogisticRegression(C=1.0, solver="lbfgs", max_iter=1200,
                                  tol=1e-3, n_jobs=1)
    if name == "rf":
        return RandomForestClassifier(n_estimators=250, max_features="sqrt",
                                      min_samples_leaf=1, n_jobs=1,
                                      random_state=42)
    if name == "hgb":
        return HistGradientBoostingClassifier(
            max_iter=60, learning_rate=0.1, max_leaf_nodes=15,
            min_samples_leaf=5, early_stopping=False, random_state=42)
    if name == "mlp":
        return MLPClassifier(hidden_layer_sizes=(128, 64), activation="relu",
                             solver="adam", alpha=1e-3, batch_size=64,
                             learning_rate_init=1e-3, max_iter=350,
                             early_stopping=True, validation_fraction=0.15,
                             n_iter_no_change=20, random_state=42)
    raise ValueError(name)


def score_model(y_true, y_pred, proba, classes):
    out = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro",
                                  zero_division=0)),
        "top5": float(top_k_accuracy_score(y_true, proba, k=5, labels=classes)),
        "chance": float(1.0 / len(classes)),
        "n_classes": int(len(classes)),
    }
    try:
        out["auc"] = float(roc_auc_score(y_true, proba, multi_class="ovr",
                                         average="macro", labels=classes))
    except ValueError:
        out["auc"] = float("nan")
    idx = np.searchsorted(classes, y_true)
    out["prob_true_mean"] = float(np.mean(proba[np.arange(len(y_true)), idx]))
    return out


def cluster_ci(df, value="correct", n_boot=2000, seed=42):
    rng = np.random.default_rng(seed)
    pat = df.groupby("patient_id")[value].mean().to_numpy(float)
    vals = [float(np.mean(rng.choice(pat, size=len(pat), replace=True)))
            for _ in range(n_boot)]
    return [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))]


def run_group(feats, group, model_names, out_dir):
    d = feats[feats["group"] == group]
    train = d[d["window"] <= 5]
    test = d[d["window"] >= 6]
    xtr = train[FEATURE_NAMES].to_numpy(float)
    xte = test[FEATURE_NAMES].to_numpy(float)
    ytr = train["patient_id"].to_numpy(int)
    yte = test["patient_id"].to_numpy(int)
    scaler = StandardScaler().fit(xtr)
    xtr = scaler.transform(xtr)
    xte = scaler.transform(xte)
    classes = np.unique(ytr)
    results = {}
    preds = []
    for name in model_names:
        t0 = time.time()
        model = make_model(name)
        model.fit(xtr, ytr)
        pred = model.predict(xte)
        proba = model.predict_proba(xte)
        classes_model = model.classes_
        if not np.array_equal(classes_model, classes):
            full = np.zeros((len(xte), len(classes)))
            for j, c in enumerate(classes_model):
                full[:, np.searchsorted(classes, c)] = proba[:, j]
            proba = full
        rec = score_model(yte, pred, proba, classes)
        rec["seconds"] = round(time.time() - t0, 2)
        rec["n_train"] = int(len(ytr))
        rec["n_test"] = int(len(yte))
        rec["group"] = int(group)
        rec["model"] = name
        idx = np.searchsorted(classes, yte)
        ptrue = proba[np.arange(len(yte)), idx]
        correct = (pred == yte).astype(int)
        part = pd.DataFrame({
            "patient_id": yte, "group": group, "window": test["window"].to_numpy(),
            "model": name, "y_true": yte, "y_pred": pred, "correct": correct,
            "prob_true": ptrue,
        })
        rec["accuracy_ci95"] = cluster_ci(part)
        preds.append(part)
        results[name] = rec
        print(f"g{group} {name}: acc={rec['accuracy']:.4f} "
              f"ci={rec['accuracy_ci95']} top5={rec['top5']:.4f} "
              f"auc={rec['auc']:.4f} t={rec['seconds']}s", flush=True)
    pred_df = pd.concat(preds, ignore_index=True)
    pred_df.to_csv(os.path.join(out_dir, f"predictions_g{group}.csv"), index=False)
    return results, pred_df


def rf_importance(feats, group, out_dir):
    d = feats[feats["group"] == group]
    train = d[d["window"] <= 5]
    test = d[d["window"] >= 6]
    xtr_raw = train[FEATURE_NAMES].to_numpy(float)
    xte_raw = test[FEATURE_NAMES].to_numpy(float)
    scaler = StandardScaler().fit(xtr_raw)
    xtr = scaler.transform(xtr_raw)
    xte = scaler.transform(xte_raw)
    ytr = train["patient_id"].to_numpy(int)
    yte = test["patient_id"].to_numpy(int)
    rf = RandomForestClassifier(n_estimators=250, max_features="sqrt",
                                n_jobs=1, random_state=42).fit(xtr, ytr)
    imp = permutation_importance(rf, xte, yte, n_repeats=5, random_state=42,
                                 scoring="accuracy", n_jobs=1)
    df = pd.DataFrame({
        "group": group, "feature": FEATURE_NAMES,
        "perm_mean": imp.importances_mean, "perm_sd": imp.importances_std,
        "impurity": rf.feature_importances_,
    })
    df["category"] = df["feature"].map(
        {f: cat for cat, fs in CATEGORIES.items() for f in fs})
    df.to_csv(os.path.join(out_dir, f"importance_g{group}.csv"), index=False)
    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--features", default="results/features.csv")
    ap.add_argument("--out-dir", default="results")
    ap.add_argument("--groups", default="1,2,3,4")
    ap.add_argument("--models", default="dummy,logreg,rf,hgb,mlp")
    args = ap.parse_args()
    feats = pd.read_csv(args.features)
    feats = feats.dropna(subset=FEATURE_NAMES)
    groups = [int(x) for x in args.groups.split(",")]
    models = args.models.split(",")
    all_results = {}
    all_preds = []
    importances = []
    for group in groups:
        res, preds = run_group(feats, group, models, args.out_dir)
        all_results[str(group)] = res
        all_preds.append(preds)
    if 1 in groups:
        importances.append(rf_importance(feats, 1, args.out_dir))
    if 3 in groups:
        importances.append(rf_importance(feats, 3, args.out_dir))
    if importances:
        pd.concat(importances, ignore_index=True).to_csv(
            os.path.join(args.out_dir, "importance.csv"), index=False)
    pd.concat(all_preds, ignore_index=True).to_csv(
        os.path.join(args.out_dir, "predictions.csv"), index=False)
    with open(os.path.join(args.out_dir, "models.json"), "w",
              encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)
    print(json.dumps(all_results, indent=2))


if __name__ == "__main__":
    main()
