# anomaly without uniqueness: deterministic masking in a synthetic cohort

project: eidolon
version: 1.3.0
date: 2026-10-31
status: english submission draft after the methodologist and adversary passes. `paper/DRAFT.md` is the russian version; `paper/preprint.md` remains the full record.

## abstract

we tested whether intense masking of digital behavior creates a flat anomalous profile that is simultaneously unique and therefore easier to identify. a deterministic c99 generator produced a primary cohort of 600 synthetic patients over 90 days, with 24 latent parameters and 1,991,067 events. the four main groups were natural behavior (n=200), moderate masking (n=150), intense deterministic masking (n=150), and a daily re-randomized control (n=100). exploratory groups were a stochastic intense group g5 (n=150) and a within-subject switch g6/g7 (200 patients each, natural days 1-45, masked days 46-90).

the result is mixed. distance to the natural manifold rose from 3.825 to 5.084 to 17.096 to 3.449 for g1 to g4. within-cohort uniqueness fell from 3.858 to 2.900 to 0.065 to 3.009. deterministic masking collapsed 150 patients into 58 profiles, with a profile fraction of 0.0967 and an exact-profile ceiling of 0.3867; random forest and hist gradient boosting reached exactly 0.3867. a stochastic mask g5 with the same affine parameters produced 600 of 600 unique profiles and top1 0.100 [0.075, 0.130]. the within-subject switch broke pre-to-post transfer: natural control 0.751 [0.711, 0.789], deterministic mask 0.005 [0.000, 0.015], stochastic mask 0.004 [0.000, 0.009] at chance 0.005; drift was 2.238, 18.372 and 3.989. inside the masked domain the deterministic mask left 17x chance through 17 templates, while the stochastic mask left 1-4x chance because the mask scalar concentrated in [0.30, 0.64], mean 0.4948, sd 0.0543.

the preregistered rank-1 criterion was refuted on g3: participation ratio 2.380 and first-component share 0.500. the strong paradox is not supported. the data support anomaly without uniqueness, failure of identity transfer, and residual identification bounded by templates or mask concentration, not by a unique signature.

## 1. methods

### 1.1 design

primary cohort: 600 patients, 90 days, 10-day windows. training on windows 1-5, test on windows 6-9. exploratory g5: 150 patients with the same affine intense parameters as g3 but a natural stochastic emitter. within-subject: 200 natural controls, 200 g6, 200 g7; g6 and g7 are natural on days 1-45 and masked on days 46-90; training on windows 1-4, test on 6-9, window 5 excluded.

**table 1. groups.**

| group | n | regime |
|---|---|---|
| g1 | 200 | natural behavior |
| g2 | 150 | moderate masking |
| g3 | 150 | deterministic intense masking |
| g4 | 100 | daily re-randomization of natural parameters |
| g5 | 150 | intense affine parameters, natural emitter, exploratory |
| g6 | 200 | natural until day 45, then deterministic mask, exploratory |
| g7 | 200 | natural until day 45, then stochastic mask, exploratory |

**table 2. analysis status.**

| family | analyses | status |
|---|---|---|
| confirmatory | h1..h7, primary seed 20261030 | preregistered in hypotheses.md |
| exploratory | g5, matched 150, within g6/g7, post-only and pre-only, open-set, detectability, effective classes | added after the primary analysis, do not change h1..h7 |
| robustness | seed 20261031 for logreg and rf, g3 seed invariance | partial replication |

### 1.2 generator

c99, xorshift64*, 24 parameters per patient, no external libraries. g3 builds 24 parameters as an affine function of one scalar s and emits a deterministic quantized stream without rng. g5 uses the same affine map but a natural markov emitter. the within-subject mask is built from the patient's own 24 parameters through s, the mean of normalized parameters. the csv contract is frozen and all fields are integers.

### 1.3 features and metrics

51 features in four categories: temporal, sequence, interval, dynamic. two distinct metrics: `idu_nat`, the distance to the 10 nearest windows of the natural training reference in a 20-component whitened pca space, and `idu_cohort`, the distance to the 10 nearest windows of other patients. `idu_nat` measures anomaly, `idu_cohort` measures within-cohort uniqueness; they are not interchangeable.

identification: closed-set top1 and top5, chance 1/number of classes. open-set verification on window pairs: same-patient against different-patient, auc and eer. within-subject: pre-to-post transfer, pre-only and post-only controls, drift between pre and post centroids. statistics: patient-level cluster bootstrap, cohen d or dz, holm within families, 2000 resamples.

### 1.4 reproducibility

seed 20261030, second seed 20261031 for logreg and rf. two generator runs are byte identical; primary cohort sha256 `7841bd667c35ee437eea9d1c58016990c081ed022d8f042389fb356b487ce1a9`. the manifest records hashes of the binary, csv, json and figures. local bitwise replay is verified on one compiler and libm; cross-platform equivalence is not claimed. the python environment is pinned by versions, not by hash-locked wheels.

## 2. results

### 2.1 anomaly and uniqueness

| metric | g1 | g2 | g3 | g4 |
|---|---:|---:|---:|---:|
| idu_nat | 3.825 | 5.084 | 17.096 | 3.449 |
| idu_cohort | 3.858 | 2.900 | 0.065 | 3.009 |
| anomaly auc against g1 | 0.500 | 0.956 [0.933, 0.975] | 1.000 [1.000, 1.000] | 0.153 [0.109, 0.199] |

h1 is supported for anomaly: g3 against g1, cohen d=-13.16 [-14.33, -12.43], kruskal p=1.36e-94, holm 9.53e-94, n=600. h1b is refuted: g3 is the least unique group, 0.065 [0.054, 0.078]. the g3 anomaly is trivial: ten single features, including interval_cv, higuchi_fd and repeat_rate, reach auc 1.000. g4 is below 0.5 on the one-sided anomaly score, but the two-sided auc for g4 is 0.847, so a detector that flags both overly regular and overly smooth profiles separates it.

### 2.2 identification and model heterogeneity

**table 3. closed-set top1, mean [ci95].**

| model | g1 | g2 | g3 | g4 |
|---|---:|---:|---:|---:|
| logreg | 0.769 [0.735, 0.803] | 0.382 [0.338, 0.427] | 0.293 [0.227, 0.363] | 0.015 [0.003, 0.030] |
| rf | 0.818 [0.784, 0.850] | 0.395 [0.350, 0.442] | 0.387 [0.310, 0.460] | 0.025 [0.010, 0.043] |
| mlp | 0.686 [0.648, 0.725] | 0.313 [0.270, 0.358] | 0.192 [0.135, 0.255] | 0.013 [0.003, 0.023] |
| hgb | 0.135 [0.109, 0.163] | 0.063 [0.045, 0.083] | 0.387 [0.307, 0.467] | 0.010 [0.003, 0.020] |
| chance | 0.005 | 0.0067 | 0.0067 | 0.010 |

g1 is far above g2 and g3. the strict order g1 > g2 > g3 is not established: per-model tests of g2 against g3 give logreg +0.088 (p_holm 3.3e-5), mlp +0.122 (4.7e-8), hgb -0.323 (2.3e-5), rf +0.008 (p=0.112). the average across models p=0.870 is not a test of equality. a matched 150-class analysis selects rf on g1 validation and gives g1 0.820, g2 0.395, g3 0.387; the heterogeneity remains.

g3 ceiling: 58 profiles over 600 windows, profile fraction 0.0967, exact-profile top1 ceiling 0.3867. rf and hgb reach 0.3867, so there is no residual individual signal above the exact profile. g3 top5 is 1.000; this follows from the maximum collision of 16, not from an individual signature.

### 2.3 within-subject switch

**table 4. within-subject.**

| group | drift | pre-only logreg | pre-to-post rf | post-only logreg | post-only rf | post profiles |
|---|---:|---:|---:|---:|---:|---:|
| g1 natural | 2.238 [2.173, 2.303] | 0.600 | 0.751 [0.711, 0.789] | 0.570 | 0.463 | 800 of 800 |
| g6 deterministic | 18.372 [18.250, 18.487] | 0.543 | 0.005 [0.000, 0.015] | 0.0825 | 0.085 | 17 of 800 |
| g7 stochastic | 3.989 [3.869, 4.119] | 0.525 | 0.004 [0.000, 0.009] | 0.005 | 0.020 | 800 of 800 |

pre-to-post transfer is absent for both masks. this is not identity destruction: inside the masked domain g6 gives 0.085, exactly the 17-template ceiling, 17x chance; patient-level p=3.1e-12 for logreg and 3.2e-12 for rf. g7 gives 0.005-0.020, only rf and hgb slightly above chance (p=0.0010 and 0.0158), logreg at chance (p=0.594). the reason is that the mask scalar s concentrates in [0.30, 0.64], mean 0.4948, sd 0.0543, against uniform [0, 1] in g3 and g5. masks are similar across patients, while the within-patient emitter variability is large.

### 2.4 open-set, detectability, effective classes

**table 5. open-set verification.**

| group | open-set auc | eer |
|---|---:|---:|
| g1 | 0.894 [0.878, 0.909] | 0.178 [0.163, 0.195] |
| g2 | 0.689 [0.669, 0.711] | 0.368 [0.350, 0.385] |
| g3 | 0.993 [0.992, 0.995] | 0.0125 [0.0102, 0.0153] |
| g4 | 0.502 [0.486, 0.517] | 0.497 [0.483, 0.515] |
| g5 | 0.795 [0.782, 0.809] | 0.273 [0.258, 0.286] |
| g6 post | 0.951 [0.944, 0.957] | 0.0874 [0.0773, 0.0996] |
| g7 post | 0.558 [0.544, 0.571] | 0.455 [0.444, 0.468] |

the g3 auc 0.993 measures window duplication: inside one exact profile all pairs have zero distance, auc 0.5, eer 0.5. g7 eer 0.455 is close to g4 0.497, so the stochastic mask hides individuality in the open-set sense. g5 0.795 and g6 0.951 remain above the random control.

detectability: interval_cv gives auc 1.000 for g3 and g6; for g5 and g7 the core regularity panel gives 0.529 and 0.512, but action_entropy gives 0.921 and 0.942. effective classes: hill2 52.08 for g3 over 150 patients, 10.11 for g6 over 200, 150 for g5 and 200 for g7. the stochastic mask hides identity but reveals the fact of masking.

### 2.5 negative results

- h5: paired difference in chaos accuracy 0.0204 [-0.0049, 0.0446], p=0.172, dz=0.160, n=100; post hoc paired t approximation gives achieved power 0.354 for dz=0.160 and mde dz=0.285 for power 0.80. within-patient r2 is negative and skill against the patient mean is negative. the hypothesis is not supported and underpowered; no long-horizon claim is made.
- h6: participation ratio 2.380, lambda1 0.500, thresholds 2.0 and 0.80. g6 post-only is 1.553 and 0.771; the g6 pre/post mixture is 1.468 and 0.811. rank-1 is not supported for g3 uniform-s and depends on the construction.
- h7: rf 0.025 [0.010, 0.043] on the primary seed, 0.0075 [0.000, 0.018] on the second; patient-level p_holm 0.087 over five models and 0.348 over seven tests. the status is inconclusive.
- h4: consensus rho 0.275 [0.151, 0.394] is inflated by averaging; per-model rho for idu_nat is 0.167 [0.022, 0.299], 0.193 [0.056, 0.321], 0.211 [0.076, 0.340], 0.175 [0.035, 0.307], all ci include 0.20. the status is exploratory, a small and unstable effect.
- g4: two-sided anomaly auc 0.847, open-set auc 0.502; the control is not pure white noise.

### 2.6 replication

seed 20261031: idu_nat 3.845, 5.016, 16.735, 3.498; logreg and rf top1 are stable, delta ci include 0; g3 is seed invariant by construction. g5 seed2: idu_nat 5.258 against 5.223, idu_cohort 3.475 against 3.407, rf top1 0.122 against 0.100, delta ci [-0.020, 0.062]. within seed2: drift and top1 stable, maximum relative idu shift 2.7%, except g6 idu_cohort near zero. hgb and mlp were not run on the second seed.

## 3. limitations

1. all data are synthetic; 24 parameters and a markov model are not a biological model. external validity is absent.
2. g3 is a deterministic quantized construct. g5 separates the affine parameter map from the emitter but does not fully separate determinism from quantization.
3. the within-subject mask g6/g7 is built from the mean of 24 parameters, so s concentrates. this explains the residual g6 identification and the weak g7 result, but it is a design property.
4. g6 and g7 are independent patients, not two masks of one person. the g6 against g7 comparison is between-subject; only pre/post is within-patient.
5. class counts differ: g1 200, g2/g3/g5 150, g4 100. the matched 150 analysis covers g1/g2/g3 but not g4 and g5.
6. hgb is underfit on g1 and g2; per-model results matter more than the average. rf selection on g1 validation is not neutral.
7. g5, matched, within, open-set, detectability, effective classes and post-only controls were added after the primary analysis and are exploratory. h1..h7 are not revised.
8. h4 is small and unstable; h5 is not supported and underpowered; h7 is inconclusive.
9. the anomaly score is one-sided; the two-sided auc is 0.933 for g7 and 0.847 for g4. a detector that flags both overly regular and overly smooth profiles separates both groups.
10. idu_cohort depends on cohort composition; cross-file comparisons need a same-file g1 baseline.
11. bitwise replay is verified locally on one compiler and libm; cross-platform equivalence and hash-locked python environment are not verified.
12. preregistration is self-reported, without an external timestamp. there is no public doi and no author metadata yet. a prior manuscript with the same hypothesis exists in refs/; its status must be disclosed before submission.

## 4. honesty check

| claim | status | evidence | boundary |
|---|---|---|---|
| deterministic masking is anomalous | supported | idu_nat 17.096 against 3.825, d=-13.16 | synthetic, g3 construct |
| deterministic masking is not unique | supported | idu_cohort 0.065, 58 profiles, ceiling 0.3867 | synthetic |
| strong rank-1 unique paradox | refuted | pr 2.380, lambda1 0.500 | g3 uniform-s |
| g2 against g3 is monotone | not established | per-model p disagree; rf tie | class counts and models differ |
| masking destroys identity | refuted in strong form | pre-to-post 0.005, but post-only g6 0.085, g7 1-4x chance | transfer broken, information remains |
| stochastic mask hides identity | supported in-domain | open-set eer 0.455 against 0.497 for g4 | mask detectable by action_entropy |
| forecast is horizon-limited | not supported | diff 0.0204, ci includes 0, r2 negative | underpowered |
| g4 control is at chance | inconclusive | 0.025 and 0.0075 on two seeds | one seed above threshold |
| uniqueness predicts identification | exploratory, weak | consensus 0.275, per-model 0.167-0.211 | small effect |
| artifact is reproducible | locally supported | sha256, manifest, tests | local compiler and libm, no public doi |

## 5. reproduction commands

```sh
make
./eidolon_gen --seed 20261030 --out data/cohort.csv
./eidolon_gen --seed 20261030 --out data/g5.csv --n1 200 --n2 150 --n3 150 --n4 100 --n5 150
./eidolon_gen --seed 20261030 --out data/within.csv --n1 200 --n2 0 --n3 0 --n4 0 --n5 0 --n6 200 --n7 200
python3 python/eidolon_features.py --csv data/cohort.csv --out-dir results
python3 python/eidolon_models.py --groups 1,2,3,4 --models dummy,logreg,rf,hgb,mlp
python3 python/eidolon_features.py --csv data/g5.csv --out-dir results/g5
python3 python/eidolon_models.py --features results/g5/features.csv --out-dir results/g5 --groups 1,5 --models dummy,logreg,rf,hgb,mlp
python3 python/eidolon_features.py --csv data/within.csv --out-dir results/within
python3 python/eidolon_within.py
python3 python/eidolon_postonly.py
python3 python/eidolon_verification.py
python3 python/eidolon_robustness2.py
python3 python/eidolon_stats.py
python3 python/eidolon_robustness.py
python3 python/eidolon_corrections.py
python3 python/eidolon_matched.py
python3 python/eidolon_plots.py
python3 python/eidolon_g5_plot.py
python3 python/eidolon_within_plot.py
make test-python
make check
make paper
make manifest
```

## 6. references

- narayanan, a., shmatikov, v. (2008). robust de-anonymization of large sparse datasets.
- dwork, c. (2006). differential privacy.
- sweeney, l. (2002). k-anonymity: a model for protecting privacy.
- eckersley, p. (2010). how unique is your web browser?
- monrose, f., rubin, a. d. (1997). authentication via keystroke dynamics.
- kohno, t., broido, a., claffy, k. c. (2005). remote physical device fingerprinting.
- shannon, c. e. (1948). a mathematical theory of communication.
- mandelbrot, b. b. (1982). the fractal geometry of nature.
- taleb, n. n. (2007). the black swan.
- shumailov, i., et al. (2023). the curse of recursion.
- uglanova, n. n., mushnikov, d. l., kostin, v. v., et al. (2010). information culture of patients and ways to improve it. rudn journal of medicine, no. 4, pp. 367-371.
- uglanova, n. n., mushnikov, d. l., polyakov, b. a. (2020). awareness of medical students about covid-19 prevention. ivgma bulletin, vol. 25, no. 3-4.
