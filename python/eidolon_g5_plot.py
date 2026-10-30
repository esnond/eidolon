#!/usr/bin/env python3
"""g5 sensitivity figure: uniqueness/anomaly and identification."""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT = "results"
COL = {1: "#1b6ca8", 3: "#b3312c", 5: "#6a3d9a"}


def mean_ci(x):
    x = np.asarray(x, float)
    rng = np.random.default_rng(42)
    boot = [np.mean(rng.choice(x, len(x), replace=True)) for _ in range(3000)]
    return np.mean(x), np.percentile(boot, 2.5), np.percentile(boot, 97.5)


def main():
    pm = pd.read_csv(os.path.join(OUT, "patient_metrics.csv"))
    g5 = pd.read_csv(os.path.join(OUT, "g5", "patient_metrics.csv"))
    pm = pd.concat([pm, g5[g5.group == 5]], ignore_index=True)
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.6))
    ax = axes[0]
    for i, g in enumerate((1, 3, 5)):
        vals = pm[pm.group == g].idu_nat.to_numpy()
        mean, lo, hi = mean_ci(vals)
        ax.bar(i, mean, color=COL[g], alpha=0.8,
               yerr=[[mean - lo], [hi - mean]], capsize=4)
        ax.text(i, mean + 0.8, f"n={len(vals)}", ha="center", fontsize=7)
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(["g1\nnatural", "g3\ndeterministic", "g5\nstochastic"])
    ax.set_ylabel("idu_nat (sd units)")
    ax.set_title("a. distance to natural manifold", loc="left", fontsize=9)
    ax.grid(axis="y", alpha=0.25, lw=0.5)
    ax = axes[1]
    m3 = json.load(open(os.path.join(OUT, "models.json")))["3"]
    m5 = json.load(open(os.path.join(OUT, "g5", "models.json")))["5"]
    names = ["logreg", "rf", "mlp", "hgb"]
    x = np.arange(len(names))
    for j, (g, m) in enumerate(((3, m3), (5, m5))):
        vals = [m[n]["accuracy"] for n in names]
        lo = [m[n]["accuracy"] - m[n]["accuracy_ci95"][0] for n in names]
        hi = [m[n]["accuracy_ci95"][1] - m[n]["accuracy"] for n in names]
        ax.bar(x + (j - 0.5) * 0.36, vals, 0.36, color=COL[g], alpha=0.85,
               yerr=[lo, hi], capsize=2, label=f"g{g}")
    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=7.5)
    ax.set_ylabel("closed set accuracy")
    ax.set_title("b. identification, 150 classes", loc="left", fontsize=9)
    ax.legend(fontsize=7, frameon=False)
    ax.grid(axis="y", alpha=0.25, lw=0.5)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "figures", "fig7_g5.png"), dpi=220)
    print("fig7 written")


if __name__ == "__main__":
    main()
