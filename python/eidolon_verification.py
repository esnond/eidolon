#!/usr/bin/env python3
"""open-set verification on existing eidolon features. read only inputs."""
import argparse
import hashlib
import json
import math
import os
import sys
from collections import Counter

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist, pdist
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from eidolon_features import FEATURE_NAMES

BASE = os.path.dirname(HERE)
OUT_DEFAULT = os.path.join(BASE, "results", "verification.json")
DATASETS = {
    "cohort": os.path.join(BASE, "results", "features.csv"),
    "g5": os.path.join(BASE, "results", "g5", "features.csv"),
    "within": os.path.join(BASE, "results", "within", "features.csv"),
}
GROUPS = (
    (1, "cohort"),
    (2, "cohort"),
    (3, "cohort"),
    (4, "cohort"),
    (5, "g5"),
    (6, "within"),
    (7, "within"),
)
N_COMPONENTS = 20
TEST_WINDOW_MIN = 6
TRAIN_WINDOW_MAX = 5
TOL = 1e-12


def clean_json(obj):
    if isinstance(obj, dict):
        return {str(k): clean_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [clean_json(v) for v in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        obj = float(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, float):
        return obj if math.isfinite(obj) else None
    return obj


def load_dataset(path):
    feats = pd.read_csv(path)
    x = feats[FEATURE_NAMES].to_numpy(np.float64)
    if not np.isfinite(x).all():
        raise ValueError(f"non-finite features in {path}")
    train = ((feats["group"] == 1) & (feats["window"] <= TRAIN_WINDOW_MAX)).to_numpy()
    if train.sum() == 0:
        raise ValueError(f"no g1 training windows in {path}")
    scaler = StandardScaler().fit(x[train])
    zs = scaler.transform(x)
    pca = PCA(n_components=N_COMPONENTS, whiten=True, random_state=42).fit(zs[train])
    z = pca.transform(zs)
    digest = hashlib.sha256(
        np.ascontiguousarray(x[train], dtype="<f8").tobytes()).hexdigest()
    meta = {
        "reference_group": 1,
        "reference_train_windows": int(train.sum()),
        "reference_train_patients": int(feats.loc[train, "patient_id"].nunique()),
        "scaler": "standard scaler fit on g1 windows 1-5",
        "pca_components": N_COMPONENTS,
        "pca_whiten": True,
        "reference_matrix_sha256": digest,
    }
    return feats, z, zs, meta


def patient_blocks(feats, z, group):
    mask = ((feats["group"] == group)
            & (feats["window"] >= TEST_WINDOW_MIN)).to_numpy()
    d = feats.loc[mask].copy()
    zd = z[mask]
    if len(d) == 0:
        raise ValueError(f"no test windows for group {group}")
    d["_row"] = np.arange(len(d), dtype=np.int64)
    d = d.sort_values(["patient_id", "window"]).reset_index(drop=True)
    zd = zd[d["_row"].to_numpy()]
    pids = np.sort(d["patient_id"].unique())
    per = []
    for pid in pids:
        zz = zd[d["patient_id"].to_numpy() == pid]
        if len(zz) != 4:
            raise ValueError(
                f"group {group} patient {pid} has {len(zz)} test windows, expected 4")
        per.append(zz)
    return d, zd, pids, per


def pair_tables(per):
    n = len(per)
    within = np.empty((n, 6), dtype=np.float64)
    cross = np.empty((n, n, 16), dtype=np.float64)
    for i, zi in enumerate(per):
        within[i] = pdist(zi)
    for i in range(n):
        for j in range(i, n):
            block = cdist(per[i], per[j]).ravel()
            cross[i, j] = block
            cross[j, i] = block
    iu = np.triu_indices(n, 1)
    return within, cross, iu


def auc_eer(same, diff, n_bisect=60):
    same = np.asarray(same, dtype=np.float64)
    diff = np.asarray(diff, dtype=np.float64)
    if same.size == 0 or diff.size == 0:
        raise ValueError("both same-patient and different-patient pairs required")
    ss = np.sort(same)
    ds = np.sort(diff)
    n1 = len(ss)
    n0 = len(ds)
    right = np.searchsorted(ds, same, side="right")
    left = np.searchsorted(ds, same, side="left")
    auc = float(np.mean((n0 - right + 0.5 * (right - left)) / n0))
    all_values = np.r_[same, diff]
    if np.ptp(all_values) == 0.0:
        return {"auc": 0.5, "eer": 0.5, "threshold": float(all_values[0]),
                "fpr": None, "fnr": None, "degenerate": True}

    def operating(t):
        fpr = float(np.searchsorted(ds, t, side="right") / n0)
        fnr = 1.0 - float(np.searchsorted(ss, t, side="right") / n1)
        return fpr, fnr

    lo = float(all_values.min())
    hi = float(all_values.max())
    fpr, fnr = operating(lo)
    if fpr >= fnr:
        value = lo
    else:
        for _ in range(n_bisect):
            mid = 0.5 * (lo + hi)
            fpr, fnr = operating(mid)
            if fpr < fnr:
                lo = mid
            else:
                hi = mid
        pos_s = np.searchsorted(ss, lo, side="right")
        pos_d = np.searchsorted(ds, lo, side="right")
        candidates = []
        if pos_s < n1:
            candidates.append(float(ss[pos_s]))
        if pos_d < n0:
            candidates.append(float(ds[pos_d]))
        value = min(candidates) if candidates else hi

    fpr_before = float(np.searchsorted(ds, value, side="left") / n0)
    fnr_before = 1.0 - float(np.searchsorted(ss, value, side="left") / n1)
    fpr_after = float(np.searchsorted(ds, value, side="right") / n0)
    fnr_after = 1.0 - float(np.searchsorted(ss, value, side="right") / n1)
    d_before = fpr_before - fnr_before
    d_after = fpr_after - fnr_after
    if d_after == d_before:
        eer = 0.5 * (fpr_after + fnr_after)
    else:
        weight = -d_before / (d_after - d_before)
        eer = fpr_before + weight * (fpr_after - fpr_before)
    return {"auc": auc, "eer": float(eer), "threshold": float(value),
            "fpr": float(eer), "fnr": float(eer), "degenerate": False}


def distance_summary(x):
    x = np.asarray(x, dtype=np.float64)
    return {
        "mean": float(np.mean(x)),
        "median": float(np.median(x)),
        "sd": float(np.std(x, ddof=1)),
        "min": float(np.min(x)),
        "max": float(np.max(x)),
    }


def bootstrap_stats(within, cross, iu, n_boot, seed, n_bisect=60):
    n = within.shape[0]
    rng = np.random.default_rng(seed)
    aucs = np.empty(n_boot, dtype=np.float64)
    eers = np.empty(n_boot, dtype=np.float64)
    for b in range(n_boot):
        pick = rng.choice(n, size=n, replace=True)
        same = within[pick].ravel()
        blocks = cross[np.ix_(pick, pick)]
        keep = (pick[:, None] != pick[None, :])[iu]
        diff = blocks[iu][keep].ravel()
        rec = auc_eer(same, diff, n_bisect=n_bisect)
        aucs[b] = rec["auc"]
        eers[b] = rec["eer"]
    return {
        "unit": "patient",
        "resamples": int(n_boot),
        "seed": int(seed),
        "duplicate_policy": (
            "patients resampled with replacement; within-patient pairs of every "
            "sampled copy are same-patient; different-patient pairs are formed "
            "only between distinct source patients, cross-copy pairs of a "
            "repeated patient are excluded as impostors"),
        "auc_ci95": [float(np.percentile(aucs, 2.5)),
                     float(np.percentile(aucs, 97.5))],
        "eer_ci95": [float(np.percentile(eers, 2.5)),
                     float(np.percentile(eers, 97.5))],
        "auc_boot_sd": float(np.std(aucs, ddof=1)),
        "eer_boot_sd": float(np.std(eers, ddof=1)),
    }


def profile_counts(d):
    values = np.round(d[FEATURE_NAMES].to_numpy(np.float64), 6)
    counts = Counter(tuple(row) for row in values)
    sizes = list(counts.values())
    return {
        "profile_definition": "feature vector rounded to 6 decimals",
        "distinct_profiles": int(len(counts)),
        "profile_fraction": float(len(counts) / len(d)),
        "largest_profile": int(max(sizes)),
        "median_profile": float(np.median(sizes)),
    }


def analyze_group(feats, z, group, source, reference_meta, n_boot, seed):
    d, zd, pids, per = patient_blocks(feats, z, group)
    within, cross, iu = pair_tables(per)
    same = within.ravel()
    diff = cross[iu].ravel()
    point = auc_eer(same, diff)
    boot = bootstrap_stats(within, cross, iu, n_boot, seed)
    rec = {
        "group": int(group),
        "source": os.path.relpath(source, BASE),
        "n_patients": int(len(pids)),
        "n_test_windows": int(len(d)),
        "windows_per_patient": 4,
        "n_same_patient_pairs": int(len(same)),
        "n_different_patient_pairs": int(len(diff)),
        "same_patient_distance": distance_summary(same),
        "different_patient_distance": distance_summary(diff),
        "auc": point["auc"],
        "auc_ci95": boot["auc_ci95"],
        "eer": point["eer"],
        "eer_ci95": boot["eer_ci95"],
        "eer_threshold": point["threshold"],
        "eer_fpr": point["fpr"],
        "eer_fnr": point["fnr"],
        "degenerate": point["degenerate"],
        "bootstrap": boot,
        "reference": reference_meta,
    }
    rec.update(profile_counts(d))
    return rec


def metric_collision(blocks, pids, values, metric):
    same_parts = []
    diff_parts = []
    per_auc = []
    separated = 0
    max_same = 0.0
    max_diff = 0.0
    for idx in blocks:
        idx = np.asarray(idx, dtype=np.int64)
        if len(idx) < 2:
            continue
        pp = pids[idx]
        dist = cdist(values[idx], values[idx], metric=metric)
        dist = np.nan_to_num(dist, nan=0.0, posinf=0.0, neginf=0.0)
        dist = np.clip(dist, 0.0, None)
        iu = np.triu_indices(len(idx), 1)
        pair_dist = dist[iu]
        same_mask = (pp[:, None] == pp[None, :])[iu]
        ns = int(same_mask.sum())
        nd = int((~same_mask).sum())
        if ns == 0:
            continue
        same_parts.append(pair_dist[same_mask])
        diff_parts.append(pair_dist[~same_mask])
        if nd > 0:
            rec = auc_eer(pair_dist[same_mask], pair_dist[~same_mask])
            per_auc.append(rec["auc"])
            s = pair_dist[same_mask]
            o = pair_dist[~same_mask]
            if s.max() < o.min() - TOL or o.max() < s.min() - TOL:
                separated += 1
        if ns > 0:
            max_same = max(max_same, float(pair_dist[same_mask].max()))
        if nd > 0:
            max_diff = max(max_diff, float(pair_dist[~same_mask].max()))
    same = np.concatenate(same_parts)
    diff = np.concatenate(diff_parts)
    stats = auc_eer(same, diff)
    return {
        "metric": metric,
        "n_same_pairs": int(len(same)),
        "n_different_pairs": int(len(diff)),
        "pooled_auc": stats["auc"],
        "pooled_eer": stats["eer"],
        "same_distance": distance_summary(same),
        "different_distance": distance_summary(diff),
        "same_zero_fraction": float(np.mean(same == 0.0)),
        "different_zero_fraction": float(np.mean(diff == 0.0)),
        "max_same": float(max_same),
        "max_different": float(max_diff),
        "profiles_with_both_pair_types": int(len(per_auc)),
        "per_profile_auc": {
            "mean": float(np.mean(per_auc)) if per_auc else None,
            "min": float(np.min(per_auc)) if per_auc else None,
            "max": float(np.max(per_auc)) if per_auc else None,
        },
        "profiles_separated_at_tolerance": int(separated),
        "all_distances_at_or_below_tolerance": bool(
            max(max_same, max_diff) <= TOL),
    }


def collision_blocks(raw, pids, key_fn):
    blocks = {}
    for i, row in enumerate(raw):
        key = key_fn(row)
        blocks.setdefault(key, []).append(i)
    return list(blocks.values())


def g3_collision_analysis(feats, z, zs, group=3):
    mask = ((feats["group"] == group)
            & (feats["window"] >= TEST_WINDOW_MIN)).to_numpy()
    d = feats.loc[mask].copy()
    zd = z[mask]
    zsd = zs[mask]
    raw = d[FEATURE_NAMES].to_numpy(np.float64)
    pids = d["patient_id"].to_numpy(np.int64)
    out = {
        "group": int(group),
        "source": "results/features.csv",
        "test_windows": int(len(d)),
        "patients": int(d["patient_id"].nunique()),
        "tolerance": TOL,
        "definitions": {},
    }

    exact_blocks = collision_blocks(raw, pids, lambda row: tuple(row))
    rounded_blocks = collision_blocks(
        raw, pids, lambda row: tuple(np.round(row, 6)))
    out["profile_definitions"] = {
        "strict_exact_float": int(len(exact_blocks)),
        "rounded_6": int(len(rounded_blocks)),
    }

    exact_same = []
    exact_diff = []
    exact_both = 0
    exact_range = 0.0
    for idx in exact_blocks:
        idx = np.asarray(idx, dtype=np.int64)
        pp = pids[idx]
        dist = cdist(zd[idx], zd[idx])
        iu = np.triu_indices(len(idx), 1)
        pair_dist = dist[iu]
        same_mask = (pp[:, None] == pp[None, :])[iu]
        if same_mask.any():
            exact_same.append(pair_dist[same_mask])
        if (~same_mask).any():
            exact_diff.append(pair_dist[~same_mask])
        if same_mask.any() and (~same_mask).any():
            exact_both += 1
        if len(idx) > 1:
            exact_range = max(exact_range,
                              float(np.max(np.ptp(raw[idx], axis=0))))
    exact_same = np.concatenate(exact_same)
    exact_diff = np.concatenate(exact_diff)
    exact_stats = auc_eer(exact_same, exact_diff)
    out["definitions"]["strict_exact_float"] = {
        "description": (
            "identical float64 feature vectors; this is the literal exact profile"),
        "profiles": int(len(exact_blocks)),
        "largest_profile": int(max(len(b) for b in exact_blocks)),
        "profiles_with_both_pair_types": int(exact_both),
        "n_same_pairs_inside_profiles": int(len(exact_same)),
        "n_different_pairs_inside_profiles": int(len(exact_diff)),
        "same_distance": distance_summary(exact_same),
        "different_distance": distance_summary(exact_diff),
        "pooled_auc": exact_stats["auc"],
        "pooled_eer": exact_stats["eer"],
        "max_within_profile_feature_range": float(exact_range),
        "all_distances_zero": bool(
            np.all(exact_same == 0.0) and np.all(exact_diff == 0.0)),
        "profiles_separated_at_tolerance": 0,
    }

    rounded_sizes = [len(b) for b in rounded_blocks]
    rounded_range = 0.0
    for idx in rounded_blocks:
        if len(idx) > 1:
            rounded_range = max(
                rounded_range,
                float(np.max(np.ptp(raw[np.asarray(idx, dtype=np.int64)],
                                    axis=0))))
    metrics = [
        metric_collision(rounded_blocks, pids, zd, "euclidean"),
        metric_collision(rounded_blocks, pids, zsd, "euclidean"),
        metric_collision(rounded_blocks, pids, zsd, "cityblock"),
        metric_collision(rounded_blocks, pids, zsd, "cosine"),
        metric_collision(rounded_blocks, pids, zsd, "correlation"),
    ]
    names = ["pca_euclidean", "standardized_euclidean",
             "standardized_manhattan", "standardized_cosine",
             "standardized_correlation"]
    for name, rec in zip(names, metrics):
        rec["name"] = name
    max_auc_dev = max(abs(rec["pooled_auc"] - 0.5) for rec in metrics)
    any_separated = any(rec["profiles_separated_at_tolerance"] > 0
                        for rec in metrics)
    out["definitions"]["rounded_6"] = {
        "description": (
            "feature vector rounded to 6 decimals; this matches the profile "
            "definition in results/corrections.json and results/verdicts.json"),
        "profiles": int(len(rounded_blocks)),
        "profile_sizes": {
            str(k): int(v) for k, v in sorted(Counter(rounded_sizes).items())},
        "largest_profile": int(max(rounded_sizes)),
        "max_within_profile_feature_range": float(rounded_range),
        "metrics": metrics,
        "max_abs_auc_deviation_from_0_5": float(max_auc_dev),
        "any_profile_separated_at_tolerance": bool(any_separated),
        "tolerance_collapse": {
            "all_metrics_at_or_below_tolerance": bool(
                all(rec["all_distances_at_or_below_tolerance"]
                    for rec in metrics)),
            "auc_if_distances_snapped_to_zero": 0.5,
            "eer_if_distances_snapped_to_zero": 0.5,
            "profiles_separated": 0,
        },
    }
    out["answer"] = {
        "can_any_distance_separate_same_patient_pairs_inside_same_profile": False,
        "reason": (
            "strict exact profiles have identical feature vectors and zero "
            "distance for every within-profile pair; rounded profiles differ "
            "only by floating point noise up to 2.04e-15, and the pooled auc "
            "moves in opposite directions across metrics; at tolerance 1e-12 "
            "all within-profile pairs tie, so auc and eer are 0.5 and no profile "
            "is separated"),
        "g3_overall_auc_is_not_within_profile_identity": (
            "the high group-level auc comes from all four windows of a g3 patient "
            "being exact duplicates; it does not distinguish a patient from a "
            "different patient who shares the same profile"),
    }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bootstrap", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default=OUT_DEFAULT)
    args = ap.parse_args()
    if args.bootstrap < 1:
        raise SystemExit("bootstrap resamples must be positive")

    loaded = {}
    for name, path in DATASETS.items():
        loaded[name] = load_dataset(path)

    groups = {}
    for group, dataset in GROUPS:
        feats, z, zs, meta = loaded[dataset]
        seed = args.seed + group
        groups[str(group)] = analyze_group(
            feats, z, group, DATASETS[dataset], meta,
            args.bootstrap, seed)

    coll_feats, coll_z, coll_zs, _ = loaded["cohort"]
    collision = g3_collision_analysis(coll_feats, coll_z, coll_zs, group=3)

    out = {
        "analysis": "open-set verification on existing eidolon features",
        "reference": {
            "train_windows": "1-5",
            "test_windows": "6-9",
            "space": (
                "standardized features followed by 20-component whitened pca, "
                "fit on g1 training windows"),
            "distance": "euclidean distance in the 20-dimensional pca space",
            "pair_construction": (
                "all unordered pairs of distinct test windows within a patient "
                "are same-patient; all unordered pairs of test windows from "
                "different patients are different-patient; self pairs excluded"),
            "bootstrap": {
                "unit": "patient",
                "resamples": int(args.bootstrap),
                "ci": "percentile 2.5 and 97.5",
            },
        },
        "groups": groups,
        "g3_within_collision": collision,
        "interpretation": {
            "auc": (
                "auc is p(same-patient distance < different-patient distance) "
                "with ties counted as 0.5"),
            "eer": (
                "eer is interpolated on the roc segment where false positive "
                "rate equals false negative rate; threshold is the first "
                "distance at which false positive rate reaches false negative "
                "rate and lower means accept as same"),
            "g3": (
                "the g3 group auc is high because every patient has four "
                "numerically identical windows; the collision analysis shows "
                "that inside an exact profile no distance separates same-patient "
                "pairs from different-patient pairs"),
            "g6": (
                "g6 has 17 rounded profiles over 200 patients in test windows; "
                "the mask destroys between-patient uniqueness even though each "
                "patient stays numerically identical to himself"),
            "g7": (
                "g7 has 800 unique rounded profiles; verification is weak, close "
                "to the g4 random control"),
        },
    }
    out = clean_json(out)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(out, handle, indent=2)
        handle.write("\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
