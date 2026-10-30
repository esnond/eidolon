#!/usr/bin/env python3
"""eidolon feature extraction, idu, anomaly scores. deterministic."""
import argparse
import json
import math
import os

import numpy as np
import pandas as pd
from scipy.stats import skew
from sklearn.covariance import LedoitWolf
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

DTYPES = {
    "patient_id": "int32", "group": "int8", "day": "int16", "t_s": "int32",
    "action_seq": "int16", "interval_ms": "int32", "session_dur_s": "int16",
    "action_id": "int8", "section_id": "int8", "is_repeat": "int8",
    "session_idx": "int8", "day_of_week": "int8", "is_weekend": "int8",
}

CATEGORIES = {
    "temporal": ["t_mean_h", "t_sd_h", "t_circ_mean_h", "t_circ_r",
                 "first_event_h", "last_event_h", "sessions_per_day",
                 "sessions_sd", "weekend_start_shift_h", "night_frac",
                 "morning_frac", "evening_frac"],
    "sequence": ["action_entropy", "transition_entropy", "self_transition_rate",
                 "repeat_rate", "backtrack_rate", "unique_actions",
                 "seq_len_mean", "seq_len_sd", "section_entropy"]
                + [f"action_{i}_frac" for i in range(8)],
    "interval": ["interval_mean_log", "interval_median_log", "interval_sd_log",
                 "interval_cv", "interval_iqr_log", "interval_skew",
                 "interval_autocorr1", "short_frac", "long_frac", "burstiness"],
    "dynamic": ["n_events", "n_sessions", "daily_events_mean", "daily_events_sd",
                "daily_events_cv", "daily_sessions_mean", "daily_sessions_sd",
                "trend_slope", "higuchi_fd", "missing_day_frac",
                "activity_stability", "daily_start_sd_h"],
}
FEATURE_NAMES = [f for cat in CATEGORIES.values() for f in cat]


def higuchi_fd(x, kmax=3):
    x = np.asarray(x, dtype=float)
    n = len(x)
    if n < 4 or np.allclose(x, x[0]):
        return 0.0
    lk = []
    kvals = []
    for k in range(1, kmax + 1):
        lm = []
        for m in range(k):
            idx = np.arange(m, n, k)
            if len(idx) < 2:
                continue
            length = np.sum(np.abs(np.diff(x[idx])))
            norm = (n - 1) / ((len(idx) - 1) * k)
            lm.append(length * norm)
        if lm:
            lk.append(np.mean(lm))
            kvals.append(k)
    if len(lk) < 2 or any(v <= 0 for v in lk):
        return 0.0
    slope = np.polyfit(np.log(1.0 / np.asarray(kvals)), np.log(lk), 1)[0]
    return float(slope)


def entropy(counts):
    p = np.asarray(counts, dtype=float)
    total = p.sum()
    if total <= 0:
        return 0.0
    p = p / total
    p = p[p > 0]
    return float(-np.sum(p * np.log(p)))


def extract_window(g):
    g = g.sort_values(["day", "session_idx", "action_seq"])
    day = g["day"].to_numpy(np.int32)
    t = g["t_s"].to_numpy(np.float64)
    a = g["action_id"].to_numpy(np.int32)
    sec = g["section_id"].to_numpy(np.int32)
    iv = g["interval_ms"].to_numpy(np.float64)
    key = day.astype(np.int64) * 16 + g["session_idx"].to_numpy(np.int64)
    rel = (day - 1) % 10
    sess_start = np.r_[True, key[1:] != key[:-1]]
    sess_id = np.cumsum(sess_start) - 1
    same = key[1:] == key[:-1]
    same2 = key[2:] == key[:-2]
    hours = t / 3600.0
    theta = 2.0 * math.pi * t / 86400.0
    c = float(np.mean(np.cos(theta)))
    s = float(np.mean(np.sin(theta)))
    r = float(math.hypot(c, s))
    circ_h = (math.atan2(s, c) * 24.0 / (2.0 * math.pi)) % 24.0
    de = np.bincount(rel, minlength=10).astype(float)
    ds = np.array([len(np.unique(sess_id[rel == d])) for d in range(10)], float)
    day_start = np.array([t[rel == d].mean() if np.any(rel == d) else np.nan
                          for d in range(10)], float)
    dow = g["day_of_week"].to_numpy(np.int32)
    weekend_days = np.array([np.any((rel == d) & (dow >= 6)) for d in range(10)])
    if weekend_days.any() and (~weekend_days).any():
        wshift = float((np.nanmean(day_start[weekend_days])
                        - np.nanmean(day_start[~weekend_days])) / 3600.0)
    else:
        wshift = 0.0
    counts = np.bincount(a, minlength=8).astype(float)
    af = counts / max(counts.sum(), 1.0)
    trans = np.zeros((8, 8), float)
    if np.any(same):
        np.add.at(trans, (a[:-1][same], a[1:][same]), 1.0)
    self_rate = float(np.mean(a[1:][same] == a[:-1][same])) if np.any(same) else 0.0
    back = float(np.mean(a[2:][same2] == a[:-2][same2])) if np.any(same2) else 0.0
    seq_lengths = np.bincount(sess_id).astype(float)
    pos = iv > 0
    liv = np.log1p(iv[pos]) if np.any(pos) else np.array([0.0])
    if np.any(pos) and np.std(liv) > 0:
        iskew = float(skew(liv))
        if not math.isfinite(iskew):
            iskew = 0.0
        iqr = float(np.percentile(liv, 75) - np.percentile(liv, 25))
        icv = float(np.std(iv[pos]) / max(np.mean(iv[pos]), 1e-9))
        burst = float((np.std(iv[pos]) - np.mean(iv[pos]))
                      / max(np.std(iv[pos]) + np.mean(iv[pos]), 1e-9))
    else:
        iskew = 0.0
        iqr = 0.0
        icv = 0.0
        burst = 0.0
    pair = same & (iv[1:] > 0) & (iv[:-1] > 0)
    if np.sum(pair) > 2 and np.std(iv[:-1][pair]) > 0 and np.std(iv[1:][pair]) > 0:
        iac = float(np.corrcoef(iv[:-1][pair], iv[1:][pair])[0, 1])
    else:
        iac = 0.0
    daily_mean = float(np.mean(de))
    daily_sd = float(np.std(de))
    daily_cv = float(daily_sd / max(daily_mean, 1e-9))
    slope = float(np.polyfit(np.arange(10, dtype=float), de, 1)[0])
    present = int(np.sum(de > 0))
    values = {
        "t_mean_h": float(np.mean(hours)), "t_sd_h": float(np.std(hours)),
        "t_circ_mean_h": float(circ_h), "t_circ_r": r,
        "first_event_h": float(np.nanmean([t[rel == d].min() / 3600.0
                                          for d in range(10) if np.any(rel == d)])),
        "last_event_h": float(np.nanmean([t[rel == d].max() / 3600.0
                                         for d in range(10) if np.any(rel == d)])),
        "sessions_per_day": float(np.mean(ds)), "sessions_sd": float(np.std(ds)),
        "weekend_start_shift_h": wshift,
        "night_frac": float(np.mean((hours < 6.0))),
        "morning_frac": float(np.mean((hours >= 6.0) & (hours < 12.0))),
        "evening_frac": float(np.mean((hours >= 18.0))),
        "action_entropy": entropy(counts), "transition_entropy": entropy(trans),
        "self_transition_rate": self_rate,
        "repeat_rate": float(np.mean(g["is_repeat"].to_numpy(float)[
            g["action_seq"].to_numpy() > 1])) if len(a) > 1 else 0.0,
        "backtrack_rate": back, "unique_actions": float(np.sum(counts > 0)),
        "seq_len_mean": float(np.mean(seq_lengths)),
        "seq_len_sd": float(np.std(seq_lengths)),
        "section_entropy": entropy(np.bincount(sec, minlength=6)),
        "interval_mean_log": float(np.mean(liv)),
        "interval_median_log": float(np.median(liv)),
        "interval_sd_log": float(np.std(liv)),
        "interval_cv": icv, "interval_iqr_log": iqr, "interval_skew": iskew,
        "interval_autocorr1": iac,
        "short_frac": float(np.mean(iv[pos] < 1000.0)) if np.any(pos) else 0.0,
        "long_frac": float(np.mean(iv[pos] > 60000.0)) if np.any(pos) else 0.0,
        "burstiness": burst, "n_events": float(len(g)),
        "n_sessions": float(len(seq_lengths)),
        "daily_events_mean": daily_mean, "daily_events_sd": daily_sd,
        "daily_events_cv": daily_cv,
        "daily_sessions_mean": float(np.mean(ds)),
        "daily_sessions_sd": float(np.std(ds)), "trend_slope": slope,
        "higuchi_fd": higuchi_fd(de), "missing_day_frac": float(1.0 - present / 10.0),
        "activity_stability": float(1.0 / (1.0 + daily_cv)),
        "daily_start_sd_h": float(np.nanstd(day_start) / 3600.0),
    }
    for i in range(8):
        values[f"action_{i}_frac"] = float(af[i])
    return values


def build_features(path, out_features):
    df = pd.read_csv(path, dtype=DTYPES)
    df["window"] = ((df["day"] - 1) // 10 + 1).astype(np.int8)
    rows = []
    for (pid, win), g in df.groupby(["patient_id", "window"], sort=False):
        if len(g) == 0:
            raise ValueError(f"empty window: patient {pid}, window {win}")
        rec = {"patient_id": int(pid), "group": int(g["group"].iloc[0]),
               "window": int(win)}
        rec.update(extract_window(g))
        rows.append(rec)
    feats = pd.DataFrame(rows)
    feats = feats[["patient_id", "group", "window"] + FEATURE_NAMES]
    feats.to_csv(out_features, index=False)
    return feats, df


def compute_idu(feats, out_dir):
    x = feats[FEATURE_NAMES].to_numpy(np.float64)
    if not np.isfinite(x).all():
        raise ValueError("non-finite feature matrix before idu")
    x = np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)
    train = (feats["window"] <= 5).to_numpy()
    test = (feats["window"] >= 6).to_numpy()
    g1 = (feats["group"] == 1).to_numpy()
    base = train & g1
    scaler = StandardScaler().fit(x[base])
    zs = scaler.transform(x)
    pca = PCA(n_components=20, whiten=True, random_state=42).fit(zs[base])
    z = pca.transform(zs)
    nn_nat = NearestNeighbors(n_neighbors=10).fit(z[base])
    dnat = nn_nat.kneighbors(z, return_distance=True)[0].mean(axis=1)
    ztest = z[test]
    n_neighbors = min(50, len(ztest) - 1)
    nn_all = NearestNeighbors(n_neighbors=n_neighbors).fit(ztest)
    dist, idx = nn_all.kneighbors(ztest)
    pids = feats.loc[test, "patient_id"].to_numpy()
    dcoh = np.zeros(len(ztest))
    for i in range(len(ztest)):
        keep = pids[idx[i]] != pids[i]
        vals = dist[i][keep][:10]
        dcoh[i] = float(np.mean(vals)) if len(vals) else 0.0
    iso = IsolationForest(n_estimators=400, random_state=42, n_jobs=1).fit(z[base])
    anom = -iso.score_samples(z)
    lw = LedoitWolf().fit(z[base])
    diff = z - lw.location_
    md = np.sqrt(np.einsum("ij,jk,ik->i", diff, lw.precision_, diff))
    idu_nat = np.full(len(feats), np.nan)
    idu_coh = np.full(len(feats), np.nan)
    idu_nat[test] = dnat[test]
    idu_coh[test] = dcoh
    feats = feats.copy()
    feats["idu_nat"] = idu_nat
    feats["idu_cohort"] = idu_coh
    feats["anomaly"] = anom
    feats["mahalanobis"] = md
    feats.to_csv(os.path.join(out_dir, "features.csv"), index=False)
    patient = feats[test].groupby(["patient_id", "group"], as_index=False).agg(
        idu_nat=("idu_nat", "mean"), idu_cohort=("idu_cohort", "mean"),
        anomaly=("anomaly", "mean"), mahalanobis=("mahalanobis", "mean"),
        n_windows=("window", "size"))
    patient.to_csv(os.path.join(out_dir, "patient_metrics.csv"), index=False)
    ranks = {}
    for grp in (1, 2, 3, 4, 5, 6, 7):
        mask = (feats["group"] == grp).to_numpy()
        if mask.sum() < 2:
            continue
        p = PCA(n_components=min(20, mask.sum() - 1), random_state=42).fit(zs[mask])
        ev = p.explained_variance_ratio_
        ranks[str(grp)] = {
            "participation_ratio": float((ev.sum() ** 2) / np.sum(ev ** 2)),
            "lambda1_share": float(ev[0]),
            "n_windows": int(mask.sum()),
            "n_features": len(FEATURE_NAMES),
        }
    with open(os.path.join(out_dir, "rank1.json"), "w", encoding="utf-8") as f:
        json.dump(ranks, f, indent=2)
    return feats, patient, ranks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="data/cohort.csv")
    ap.add_argument("--out-dir", default="results")
    args = ap.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    feats, raw = build_features(args.csv, os.path.join(args.out_dir, "features_raw.csv"))
    feats, patient, ranks = compute_idu(feats, args.out_dir)
    summary = {
        "rows": int(len(raw)),
        "patients": int(raw["patient_id"].nunique()),
        "windows": int(len(feats)),
        "groups": {str(k): int(v) for k, v in raw.groupby("group")["patient_id"].nunique().items()},
        "rank1": ranks,
    }
    with open(os.path.join(args.out_dir, "cohort_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
