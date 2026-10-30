#!/usr/bin/env python3
"""within-subject figure: drift and post-switch identification."""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = "results"
COL = {1: "#1b6ca8", 6: "#b3312c", 7: "#6a3d9a"}
LAB = {1: "g1 natural", 6: "g6 deterministic", 7: "g7 stochastic"}


def main():
    m = json.load(open(os.path.join(OUT, "within", "models.json")))
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.6))
    ax = axes[0]
    for i, g in enumerate((1, 6, 7)):
        r = m["drift"][str(g)]
        ax.bar(i, r["mean"], color=COL[g], alpha=0.85,
               yerr=[[r["mean"] - r["ci95"][0]], [r["ci95"][1] - r["mean"]]],
               capsize=4)
        ax.text(i, r["mean"] + 0.6, f"n={r['n']}", ha="center", fontsize=7)
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels([LAB[g] for g in (1, 6, 7)], fontsize=8)
    ax.set_ylabel("pre to post drift (sd units)")
    ax.set_title("a. profile change, same patient", loc="left", fontsize=9)
    ax.grid(axis="y", alpha=0.25, lw=0.5)
    ax = axes[1]
    names = ["logreg", "rf", "mlp", "hgb"]
    x = np.arange(len(names))
    for j, g in enumerate((1, 6, 7)):
        vals = [m["groups"][str(g)][n]["accuracy"] for n in names]
        lo = [m["groups"][str(g)][n]["accuracy"]
              - m["groups"][str(g)][n]["ci95"][0] for n in names]
        hi = [m["groups"][str(g)][n]["ci95"][1]
              - m["groups"][str(g)][n]["accuracy"] for n in names]
        ax.bar(x + (j - 1) * 0.26, vals, 0.26, color=COL[g], alpha=0.85,
               yerr=[lo, hi], capsize=2, label=LAB[g])
    ax.axhline(0.005, color="black", lw=0.8, ls="--")
    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=7.5)
    ax.set_ylabel("closed set accuracy")
    ax.set_title("b. identification after switch", loc="left", fontsize=9)
    ax.legend(fontsize=6.5, frameon=False)
    ax.grid(axis="y", alpha=0.25, lw=0.5)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "figures", "fig8_within.png"), dpi=220)
    print("fig8 written")


if __name__ == "__main__":
    main()
