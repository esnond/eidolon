#!/usr/bin/env python3
"""next-day forecast of daily activity and mean start time. deterministic."""
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import math

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score

DTYPES = {"patient_id": "int32", "group": "int8", "day": "int16",
          "t_s": "int32", "interval_ms": "int32", "session_idx": "int8"}
FEATS = ["lag1", "lag2", "lag3", "lag4", "lag5", "lag6", "lag7",
         "roll_mean", "roll_sd", "sessions_lag", "mean_iv_lag",
         "dow_sin", "dow_cos", "mu", "sd"]
PATIENT_ROWS = []


def daily_table(path):
    df = pd.read_csv(path, dtype=DTYPES)
    df["iv_pos"] = df["interval_ms"].where(df["interval_ms"] > 0)
    d = df.groupby(["patient_id", "group", "day"], as_index=False).agg(
        events=("t_s", "size"), sessions=("session_idx", "nunique"),
        mean_iv=("iv_pos", "mean"), mean_start=("t_s", "mean"))
    full = []
    for (pid, grp), g in d.groupby(["patient_id", "group"], sort=False):
        idx = pd.DataFrame({"day": np.arange(1, 91), "patient_id": pid,
                            "group": grp})
        idx = idx.merge(g, on=["patient_id", "group", "day"], how="left")
        tr = idx[idx["day"] <= 30]
        fill_iv = tr["mean_iv"].median()
        fill_start = tr["mean_start"].mean()
        idx["events"] = idx["events"].fillna(0.0)
        idx["sessions"] = idx["sessions"].fillna(0.0)
        idx["mean_iv"] = idx["mean_iv"].fillna(fill_iv)
        idx["mean_start"] = idx["mean_start"].fillna(fill_start)
        idx["mean_start"] = idx["mean_start"] / 3600.0
        idx["dow"] = ((idx["day"] - 1) % 7) + 1
        full.append(idx)
    return pd.concat(full, ignore_index=True)


def design(d, days_train, target):
    rows = []
    for (pid, grp), g in d.groupby(["patient_id", "group"], sort=False):
        g = g.sort_values("day")
        y = g[target].to_numpy(float)
        ses = g["sessions"].to_numpy(float)
        miv = g["mean_iv"].to_numpy(float)
        dow = g["dow"].to_numpy(int)
        tr = np.arange(0, days_train)
        mu = float(np.mean(y[tr]))
        sd = float(np.std(y[tr]))
        if sd <= 1e-9:
            sd = 1.0
        mus = float(np.mean(ses[tr]))
        sds = float(np.std(ses[tr])) if np.std(ses[tr]) > 0 else 1.0
        mumi = float(np.mean(miv[tr]))
        sdmi = float(np.std(miv[tr])) if np.std(miv[tr]) > 0 else 1.0
        for t in range(7, 90):
            rows.append([pid, grp, t + 1,
                         (y[t - 1] - mu) / sd, (y[t - 2] - mu) / sd,
                         (y[t - 3] - mu) / sd, (y[t - 4] - mu) / sd,
                         (y[t - 5] - mu) / sd, (y[t - 6] - mu) / sd,
                         (y[t - 7] - mu) / sd,
                         (np.mean(y[t - 7:t]) - mu) / sd,
                         np.std(y[t - 7:t]) / sd,
                         (ses[t - 1] - mus) / sds, (miv[t - 1] - mumi) / sdmi,
                         np.sin(2 * np.pi * dow[t] / 7),
                         np.cos(2 * np.pi * dow[t] / 7), mu, sd, y[t]])
    cols = ["patient_id", "group", "day", "lag1", "lag2", "lag3", "lag4",
            "lag5", "lag6", "lag7", "roll_mean", "roll_sd",
            "sessions_lag", "mean_iv_lag", "dow_sin", "dow_cos", "mu", "sd",
            "y"]
    return pd.DataFrame(rows, columns=cols)


def metrics(test, pred):
    y = test["y"].to_numpy(float)
    mae = float(mean_absolute_error(y, pred))
    mean_y = float(np.mean(y))
    r2 = float(r2_score(y, pred)) if np.std(y) > 1e-9 else float("nan")
    return {"mae": mae, "mean_target": mean_y,
            "accuracy": float(1.0 - mae / max(mean_y, 1e-9)),
            "r2": r2, "n": int(len(y))}


def within_patient_r2(test, pred):
    vals = []
    for pid in np.unique(test["patient_id"]):
        mask = (test["patient_id"] == pid).to_numpy()
        y = test.loc[mask, "y"].to_numpy(float)
        p = np.asarray(pred)[mask]
        if np.std(y) > 1e-9:
            vals.append(float(r2_score(y, p)))
        elif np.mean(np.abs(y - p)) < 1e-6:
            vals.append(1.0)
    return float(np.mean(vals)), float(np.std(vals)), len(vals)


def boot_ci(test, pred, n_boot=2000, seed=42):
    rng = np.random.default_rng(seed)
    test = test.reset_index(drop=True)
    pred = np.asarray(pred)
    accs = []
    r2s = []
    for pid in np.unique(test["patient_id"]):
        mask = (test["patient_id"] == pid).to_numpy()
        y = test.loc[mask, "y"].to_numpy(float)
        p = pred[mask]
        my = float(np.mean(y))
        if my > 1e-9:
            accs.append(float(1.0 - mean_absolute_error(y, p) / my))
        if np.std(y) > 1e-9:
            r2s.append(float(r2_score(y, p)))
    accs = np.asarray(accs)
    r2s = np.asarray(r2s)
    ba = [float(np.mean(rng.choice(accs, size=len(accs), replace=True)))
          for _ in range(n_boot)]
    br = [float(np.mean(rng.choice(r2s, size=len(r2s), replace=True)))
          for _ in range(n_boot)]
    return ([float(np.percentile(ba, 2.5)), float(np.percentile(ba, 97.5))],
            [float(np.percentile(br, 2.5)), float(np.percentile(br, 97.5))])


def run_one(d, target, label, days_train=30):
    data = design(d, days_train, target)
    train = data[data["day"] <= days_train]
    tests = {"days_31_60": data[(data["day"] > days_train) & (data["day"] <= 60)],
             "days_61_90": data[data["day"] > 60]}
    model = Ridge(alpha=1.0).fit(train[FEATS], train["y"])
    out = {}
    for name, test in tests.items():
        pred = model.predict(test[FEATS])
        rec = metrics(test, pred)
        y = test["y"].to_numpy(float)
        base_mean = test["mu"].to_numpy(float)
        base_persist = test["lag1"].to_numpy(float) * test["sd"].to_numpy(float) + base_mean
        rec["baseline_mean_mae"] = float(mean_absolute_error(y, base_mean))
        rec["baseline_persist_mae"] = float(mean_absolute_error(y, base_persist))
        rec["skill_vs_mean"] = float(1.0 - rec["mae"] / max(rec["baseline_mean_mae"], 1e-9))
        rec["skill_vs_persist"] = float(1.0 - rec["mae"] / max(rec["baseline_persist_mae"], 1e-9))
        mr2, sr2, nr2 = within_patient_r2(test, pred)
        rec["within_patient_r2_mean"] = mr2
        rec["within_patient_r2_sd"] = sr2
        rec["within_patient_r2_n"] = int(nr2)
        ci_acc, ci_r2 = boot_ci(test, pred)
        rec["accuracy_ci95"] = ci_acc
        rec["r2_ci95"] = ci_r2
        out[name] = rec
        for pid in np.unique(test["patient_id"]):
            mask = (test["patient_id"] == pid).to_numpy()
            y = test.loc[mask, "y"].to_numpy(float)
            p = pred[mask]
            my = float(np.mean(y))
            acc = (1.0 - mean_absolute_error(y, p) / my) if my > 1e-9 else float("nan")
            PATIENT_ROWS.append({
                "cohort": label, "target": target, "horizon": name,
                "patient_id": int(pid), "mae": float(mean_absolute_error(y, p)),
                "mean_target": my, "accuracy": float(acc),
            })
    return out


def run_curve(d, target):
    rows = []
    for k in (14, 21, 30):
        data = design(d, k, target)
        train = data[data["day"] <= k]
        test = data[(data["day"] > k) & (data["day"] <= 60)]
        model = Ridge(alpha=1.0).fit(train[FEATS], train["y"])
        pred = model.predict(test[FEATS])
        rec = metrics(test, pred)
        ci, _ = boot_ci(test, pred)
        rec["accuracy_ci95"] = ci
        mr2, _, _ = within_patient_r2(test, pred)
        rec["within_patient_r2_mean"] = mr2
        rec.update({"days_train": k})
        rows.append(rec)
    return rows


def clean_json(obj):
    if isinstance(obj, dict):
        return {k: clean_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean_json(v) for v in obj]
    if isinstance(obj, float) and not math.isfinite(obj):
        return None
    return obj

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cohort", default="data/cohort.csv")
    ap.add_argument("--chaos", default="data/chaos.csv")
    ap.add_argument("--out-dir", default="results")
    args = ap.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    cohort = daily_table(args.cohort)
    chaos = daily_table(args.chaos)
    out = {"targets": ["events", "mean_start"], "cohort": {}, "chaos": {},
           "curve": {}}
    for target in ("events", "mean_start"):
        out["cohort"][target] = {}
        for grp in (1, 2, 3, 4):
            sub = cohort[cohort["group"] == grp]
            out["cohort"][target][str(grp)] = run_one(sub, target, f"g{grp}")
        out["chaos"][target] = run_one(chaos, target, "chaos")
        out["curve"][target] = run_curve(chaos, target)
    with open(os.path.join(args.out_dir, "forecast.json"), "w",
              encoding="utf-8") as f:
        json.dump(clean_json(out), f, indent=2)
    rows = []
    for target, recs in out["curve"].items():
        for r in recs:
            rows.append({"target": target, **r})
    pd.DataFrame(rows).to_csv(
        os.path.join(args.out_dir, "forecast_curve.csv"), index=False)
    pd.DataFrame(PATIENT_ROWS).to_csv(
        os.path.join(args.out_dir, "forecast_patient.csv"), index=False)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
