#!/usr/bin/env python3
"""publication figures with ci95 error bars. deterministic."""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve

OUT = "results"
FIG = os.path.join(OUT, "figures")
COLORS = {1: "#1b6ca8", 2: "#d98c1f", 3: "#b3312c", 4: "#4c4c4c"}
LABELS = {1: "g1 natural", 2: "g2 moderate", 3: "g3 intense", 4: "g4 random"}


def ci_from_stats(stats, key):
    rec = stats[key]
    return rec["mean"], rec["mean"] - rec["ci95"][0], rec["ci95"][1] - rec["mean"]


def box_with_ci(ax, data, positions, colors, labels):
    bp = ax.boxplot(data, positions=positions, widths=0.55, patch_artist=True,
                    showfliers=False, medianprops={"color": "black", "lw": 1})
    for patch, c in zip(bp["boxes"], colors):
        patch.set_facecolor(c)
        patch.set_alpha(0.35)
    for pos, vals, c in zip(positions, data, colors):
        mean = np.mean(vals)
        sd = np.std(vals, ddof=1)
        half = 1.96 * sd / np.sqrt(len(vals))
        ax.errorbar(pos, mean, yerr=half, fmt="o", color=c, capsize=4,
                    markersize=5, lw=1.2)
    ax.set_xticks(positions)
    ax.set_xticklabels(labels)


def fig1(pm, stats):
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.6))
    for ax, col, title in ((axes[0], "idu_nat", "a. distance to natural manifold"),
                           (axes[1], "idu_cohort", "b. distance to cohort neighbours")):
        data = [pm.loc[pm.group == g, col].to_numpy() for g in (1, 2, 3, 4)]
        box_with_ci(ax, data, [1, 2, 3, 4],
                    [COLORS[g] for g in (1, 2, 3, 4)],
                    [f"g{g}\nn={len(data[g-1])}" for g in (1, 2, 3, 4)])
        ax.set_title(title, loc="left", fontsize=9)
        ax.set_ylabel("knn distance (sd units)")
        ax.grid(axis="y", alpha=0.25, lw=0.5)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig1_idu.png"), dpi=220)
    plt.close(fig)


def fig2(models):
    groups = [1, 2, 3, 4]
    names = ["dummy", "logreg", "rf", "hgb", "mlp"]
    fig, ax = plt.subplots(figsize=(7.4, 3.8))
    width = 0.15
    x = np.arange(len(groups))
    for j, name in enumerate(names):
        vals = [models[str(g)][name]["accuracy"] for g in groups]
        lo = [models[str(g)][name]["accuracy"] - models[str(g)][name]["accuracy_ci95"][0]
              for g in groups]
        hi = [models[str(g)][name]["accuracy_ci95"][1] - models[str(g)][name]["accuracy"]
              for g in groups]
        ax.bar(x + (j - 2) * width, vals, width, label=name,
               color=plt.cm.viridis(j / 4.0), alpha=0.85)
        ax.errorbar(x + (j - 2) * width, vals, yerr=[lo, hi], fmt="none",
                    ecolor="black", elinewidth=0.7, capsize=2)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{LABELS[g]}\nn={models[str(g)]['rf']['n_train'] // 5}, "
                        f"chance={1.0 / models[str(g)]['rf']['n_classes']:.3f}"
                        for g in groups], fontsize=7.5)
    ax.set_ylabel("closed set accuracy")
    ax.set_ylim(0, 0.95)
    ax.legend(ncol=5, fontsize=7.5, frameon=False, loc="upper center",
              bbox_to_anchor=(0.5, 1.13))
    ax.grid(axis="y", alpha=0.25, lw=0.5)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig2_accuracy.png"), dpi=220)
    plt.close(fig)


def fig3(pm, pred, stats):
    acc = pred[pred.model != "dummy"].groupby(["patient_id", "group"],
                                              as_index=False)["correct"].mean()
    m = pm.merge(acc, on=["patient_id", "group"])
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    for g in (1, 2, 3, 4):
        d = m[m.group == g]
        ax.scatter(d.idu_nat, d.correct, s=12, alpha=0.55, color=COLORS[g],
                   label=f"{LABELS[g]} (n={len(d)})", edgecolors="none")
    for g in (1, 3):
        d = m[m.group == g]
        coef = np.polyfit(d.idu_nat, d.correct, 1)
        xx = np.linspace(d.idu_nat.min(), d.idu_nat.max(), 50)
        ax.plot(xx, np.polyval(coef, xx), color=COLORS[g], lw=1.2)
    h4 = stats["hypotheses"]["h4"]["within"]["1"]
    ax.text(0.02, 0.97, f"g1 spearman rho={h4['rho']:.3f} "
                        f"[{h4['ci95'][0]:.3f}, {h4['ci95'][1]:.3f}], n={h4['n']}",
            transform=ax.transAxes, fontsize=7.5, va="top")
    ax.set_xlabel("idu_nat (knn distance, sd units)")
    ax.set_ylabel("mean correct re-identification")
    ax.legend(fontsize=7, frameon=False)
    ax.grid(alpha=0.25, lw=0.5)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig3_unique_ident.png"), dpi=220)
    plt.close(fig)


def fig4(forecast):
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.6))
    ax = axes[0]
    for target, color in (("events", "#1b6ca8"), ("mean_start", "#d98c1f")):
        for cohort, alpha in (("chaos", 1.0), ("g1", 1.0)):
            src = forecast["chaos"][target] if cohort == "chaos" else forecast["cohort"][target]["1"]
            vals = [src["days_31_60"]["accuracy"], src["days_61_90"]["accuracy"]]
            ci = [src["days_31_60"]["accuracy_ci95"], src["days_61_90"]["accuracy_ci95"]]
            ax.errorbar([0.02 if cohort == "chaos" else 0.0, 1.02 if cohort == "chaos" else 1.0],
                        vals, yerr=[[v - c[0] for v, c in zip(vals, ci)],
                                    [c[1] - v for v, c in zip(vals, ci)]],
                        marker="o", capsize=3, color=color, alpha=alpha,
                        label=f"{target}, {cohort}")
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["days 31-60", "days 61-90"])
    ax.set_ylabel("forecast accuracy (1 - mae/mean)")
    ax.set_title("a. horizon", loc="left", fontsize=9)
    ax.legend(fontsize=6.5, frameon=False)
    ax.grid(axis="y", alpha=0.25, lw=0.5)
    ax = axes[1]
    for target, color in (("events", "#1b6ca8"), ("mean_start", "#d98c1f")):
        rows = forecast["curve"][target]
        vals = [r["accuracy"] for r in rows]
        lo = [r["accuracy"] - r["accuracy_ci95"][0] for r in rows]
        hi = [r["accuracy_ci95"][1] - r["accuracy"] for r in rows]
        ax.errorbar([r["days_train"] for r in rows], vals, yerr=[lo, hi],
                    marker="o", color=color, capsize=3, label=target)
    ax.set_xlabel("training days")
    ax.set_ylabel("forecast accuracy")
    ax.set_title("b. learning curve, chaos cohort", loc="left", fontsize=9)
    ax.legend(fontsize=7, frameon=False)
    ax.grid(alpha=0.25, lw=0.5)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig4_forecast.png"), dpi=220)
    plt.close(fig)


def fig5(imp):
    d = imp[imp.group == 1].sort_values("perm_mean", ascending=False).head(12)
    d = d.iloc[::-1]
    cat_colors = {"temporal": "#1b6ca8", "sequence": "#d98c1f",
                  "interval": "#b3312c", "dynamic": "#4c4c4c"}
    fig, ax = plt.subplots(figsize=(6.6, 4.4))
    ax.barh(np.arange(len(d)), d.perm_mean, xerr=d.perm_sd, capsize=2,
            color=[cat_colors[c] for c in d.category], alpha=0.85)
    ax.set_yticks(np.arange(len(d)))
    ax.set_yticklabels(d.feature, fontsize=7.5)
    ax.set_xlabel("permutation importance (accuracy drop)")
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in cat_colors.values()]
    ax.legend(handles, cat_colors.keys(), fontsize=7, frameon=False,
              loc="lower right")
    ax.grid(axis="x", alpha=0.25, lw=0.5)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig5_importance.png"), dpi=220)
    plt.close(fig)


def fig6(pm, stats):
    fig, ax = plt.subplots(figsize=(5.2, 4.2))
    for g, color in ((2, COLORS[2]), (3, COLORS[3]), (4, COLORS[4])):
        d = pm[pm.group.isin([1, g])]
        y = (d.group == g).astype(int)
        fpr, tpr, _ = roc_curve(y, d.anomaly)
        rec = stats["hypotheses"]["h3"]["anomaly"][f"g{g}_vs_g1"]
        ax.plot(fpr, tpr, color=color, lw=1.5,
                label=f"g{g} vs g1: auc={rec['auc']:.3f} "
                      f"[{rec['ci95'][0]:.3f}, {rec['ci95'][1]:.3f}]")
    ax.plot([0, 1], [0, 1], color="grey", lw=0.8, ls="--")
    ax.set_xlabel("false positive rate")
    ax.set_ylabel("true positive rate")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.01)
    ax.legend(fontsize=7, frameon=False, loc="lower right")
    ax.grid(alpha=0.25, lw=0.5)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig6_anomaly_roc.png"), dpi=220)
    plt.close(fig)


def main():
    os.makedirs(FIG, exist_ok=True)
    pm = pd.read_csv(os.path.join(OUT, "patient_metrics.csv"))
    pred = pd.read_csv(os.path.join(OUT, "predictions.csv"))
    models = json.load(open(os.path.join(OUT, "models.json")))
    stats = json.load(open(os.path.join(OUT, "stats.json")))
    forecast = json.load(open(os.path.join(OUT, "forecast.json")))
    imp = pd.read_csv(os.path.join(OUT, "importance.csv"))
    fig1(pm, stats)
    fig2(models)
    fig3(pm, pred, stats)
    fig4(forecast)
    fig5(imp)
    fig6(pm, stats)
    print("figures written")


if __name__ == "__main__":
    main()
