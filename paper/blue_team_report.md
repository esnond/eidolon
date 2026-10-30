# blue team verification: eidolon v1.2.0

scope: annotated tag v1.2.0, commit 8ea02bebb074ba77f247eea145e783f1247892e2, release/eidolon-v1.2.0.tar.gz, paper/preprint.md.

date: 2026-10-30.

environment: linux x86_64, cc 14.2.0-19 (debian), python 3.13.5, numpy 2.5.4, pandas 3.1.0, scikit-learn 1.9.1, scipy 1.18.1, matplotlib 3.11.2. the worktree was clean at the start; git status showed no tracked modifications. the python environment hash in results/manifest.txt matches the current pip freeze hash a2c2da16ce0c3f959559076d8839b84bf98a3c5f1359def9de419f1ecf10dc8e.

## verdict table

| check | exact command | observed | verdict |
|---|---|---|---|
| primary determinism | `cd /home/esnond/echo && make check` | `DETERMINISM_PASS`; both runs sha256 `7841bd667c35ee437eea9d1c58016990c081ed022d8f042389fb356b487ce1a9`; `make_check_exit=0` | PASS |
| g5 isolation | `cd /home/esnond/echo && sh tools/check_g5.sh ./eidolon_gen 20261030` | `G5_ISOLATION_PASS`; regenerated g5 prefix is byte identical to `data/cohort.csv` | PASS |
| within g1 prefix | `cmp <(awk -F, 'NR==1 || $1<200' data/within.csv) <(awk -F, 'NR==1 || $1<200' data/cohort.csv)` | identical; sha256 of both extracted prefixes `d8128f8cdd740e2f8c709b9aee45af38dff49ee36e3a0c71c6a063d6d42946b6`; 709,756 g1 events plus header | PASS |
| manifest checksums | `grep -E '^[0-9a-f]{64}  ' results/manifest.txt > /tmp/h && sha256sum -c /tmp/h` | 105 hashes, every line `OK`, exit 0; binary `35ec3e...`, cohort `7841bd...`, environment hash match | PASS |
| python tests | `cd /home/esnond/echo && sh tests/run_tests.sh` | 7 tests, `OK`, exit 0; one non fatal sklearn skew precision warning | PASS |
| sanitizer tests | `cd <extracted-release> && make test` | asan and ubsan build and tiny cohort run, exit 0 | PASS |
| release tarball | `sha256sum -c release/eidolon-v1.2.0.sha256`; extract; `sha256sum -c` inside; `make`; checks | tarball sha `f46d2689ddbe73719e23f2de9cad4d6ac23d34422d303e6bff2d28d36cfbbe91` OK; 122 files; no refs, release, .git, binary, object files, seed.stamp, pycache; internal manifest 105/105 OK; fresh build binary `35ec3e...`; determinism and g5 pass | PASS |
| full pipeline rerun | `cd <extracted-release> && make analysis` | all published main, g5 and within CSV artifacts except `results/table4_models.csv` byte identical; that file differs only in its `seconds` column; all non timing JSON numeric fields identical; all eight figures identical | PASS |
| seed2 rerun | `python3 python/eidolon_features.py --csv data/seed2/cohort.csv --out-dir results/seed2_rerun` and `python3 python/eidolon_models.py ... --models logreg,rf` | features, patient metrics, predictions byte identical; model metrics identical except `seconds` | PASS |
| preprint key numbers | see section 7 | central claims match results; table 6 top 7 selection fails; h5 difference and p use a different estimand than table 5 | FAIL |
| artifact and document consistency | see section 8 | results/verdicts.json h1b p and row count wrong; paper/deviations.md denies two analyses that are present | FAIL |

## 1. primary determinism

command:

```sh
cd /home/esnond/echo
make check
```

observed:

```text
sh tools/check_determinism.sh ./eidolon_gen 20261030 --against-published
DETERMINISM_PASS
7841bd667c35ee437eea9d1c58016990c081ed022d8f042389fb356b487ce1a9  /tmp/tmp.POuT8AZDcd/run1.csv
7841bd667c35ee437eea9d1c58016990c081ed022d8f042389fb356b487ce1a9  /tmp/tmp.POuT8AZDcd/run2.csv
sh tools/check_g5.sh ./eidolon_gen 20261030
G5_ISOLATION_PASS
make_check_exit=0
```

additional regeneration with the exact documented flags produced byte identical files for all four published data sets. the sha256 values match results/manifest.txt:

```text
7841bd667c35ee437eea9d1c58016990c081ed022d8f042389fb356b487ce1a9  data/cohort.csv
86be22873cf47b2859a2b7a643cac0533759f809d1c1a93cfd6f09f4d49dbea0  data/chaos.csv
c93e22d8aaf83df5950f45cdb79de79cba87eeb6e365dcf2a6799af483aadd26  data/g5.csv
432b0fad2053bba04210833f217641216bdca691ecbab63784dc24a533141a88  data/within.csv
```

seed2 was also regenerated with `--seed 20261031`; sha256 `a925cfd8e142765011a70d136726f90177fdcbcb8bf03d26fa7c739eac98256b`, identical to `data/seed2/cohort.csv`. g3 rows in the primary and seed2 cohorts are identical, while g1, g2 and g4 rows differ, which supports the claim that g3 is seed invariant by construction.

## 2. g5 isolation

command:

```sh
cd /home/esnond/echo
sh tools/check_g5.sh ./eidolon_gen 20261030
```

observed: `G5_ISOLATION_PASS`. the script regenerates the g5 file and compares its first `wc -l data/cohort.csv` lines with `data/cohort.csv`. the comparison covers the whole g1, g2, g3 and g4 prefix, not only g1, g2 and g4. the claim in PROVENANCE.md is therefore supported and slightly understated.

## 3. within g1 prefix identity

command:

```sh
cd /home/esnond/echo
cmp <(awk -F, 'NR==1 || $1<200' data/within.csv) \
    <(awk -F, 'NR==1 || $1<200' data/cohort.csv)
awk -F, 'NR==1 || $1<200' data/within.csv | sha256sum
```

observed: no `cmp` output, exit 0, and sha256 `d8128f8cdd740e2f8c709b9aee45af38dff49ee36e3a0c71c6a063d6d42946b6`. the g1 block contains 709,756 events plus one header line. the same result holds for a freshly generated `data/within.csv`, so the prefix identity is a property of the RNG stream, not of the shipped file only.

## 4. manifest checksums

command:

```sh
cd /home/esnond/echo
grep -E '^[0-9a-f]{64}  ' results/manifest.txt > /tmp/h
wc -l < /tmp/h
sha256sum -c /tmp/h
```

observed: 105 hashes, every line `OK`, exit 0. the manifest header also verifies:

```text
# binary_sha256: 35ec3e93bc5943ec9d4aba7474c50ec7fadeec0897352320114e498c9bb021ef
# determinism: PASS (cmp data/cohort.csv vs replay)
# cohort_sha256: 7841bd667c35ee437eea9d1c58016990c081ed022d8f042389fb356b487ce1a9
# python_env_sha256: a2c2da16ce0c3f959559076d8839b84bf98a3c5f1359def9de419f1ecf10dc8e
```

`sha256sum eidolon_gen` equals the recorded binary hash. `python3 -m pip freeze | sort | sha256sum` equals the recorded environment hash. the manifest does not hash itself, which is expected.

## 5. python tests

command:

```sh
cd /home/esnond/echo
sh tests/run_tests.sh
```

observed: 7 tests in 3.314 s, `OK`, exit 0. coverage includes byte identical tiny generation, frozen csv header, integer fields, group counts and patient id range, 51 feature columns, finite feature values, empty window guard, and strict finite json in `results/*.json`. one non fatal warning appears in `eidolon_features.py` from `skew` on nearly identical data; it does not fail a test.

`make test` in the extracted release also passed. it compiles with `-fsanitize=address,undefined -O1 -g`, runs a tiny cohort with a cleared `LD_PRELOAD`, and exits 0.

## 6. release tarball integrity

commands:

```sh
cd /home/esnond/echo
sha256sum -c release/eidolon-v1.2.0.sha256
tar -tzf release/eidolon-v1.2.0.tar.gz | wc -l
T=$(mktemp -d)
tar -xzf release/eidolon-v1.2.0.tar.gz -C "$T"
cd "$T"
grep -E '^[0-9a-f]{64}  ' results/manifest.txt > /tmp/h
sha256sum -c /tmp/h
make
sha256sum eidolon_gen
sh tools/check_determinism.sh ./eidolon_gen 20261030 --against-published
sh tools/check_g5.sh ./eidolon_gen 20261030
make test
```

observed: tarball sha `f46d2689ddbe73719e23f2de9cad4d6ac23d34422d303e6bff2d28d36cfbbe91` matches the sidecar. 122 regular files. no `refs/`, `release/`, `.git/`, `eidolon_gen`, `*.o`, `seed.stamp` or `__pycache__` entries. the manifest inside the tarball verifies 105/105. a fresh build from the tarball produces binary sha `35ec3e93bc5943ec9d4aba7474c50ec7fadeec0897352320114e498c9bb021ef`, exactly the manifest value. determinism and g5 checks pass inside the extracted tree. `make test` passes.

the tarball is not gpg signed. the sha256 sidecar is self attested. the annotated tag v1.2.0 exists locally and points to commit 8ea02be..., but no signed tag or external witness was verified.

## 7. preprint key numbers against results files

the following groups were checked field by field with a relative tolerance of `1e-9`; rounding to the precision printed in the preprint was accepted.

| claim group | source file | observed | verdict |
|---|---|---|---|
| cohort size, event counts, per patient means | `data/cohort.csv`, `results/cohort_summary.json` | 600 patients, 1,991,067 events; g1 200/709,756/3548.78; g2 150/535,612/3570.75; g3 150/394,650/2631.00; g4 100/351,049/3510.49; g5 150/554,257/3695.05 | PASS |
| table 2 idu_nat, idu_cohort, anomaly | `results/patient_metrics.csv`, `results/robustness.json`, `results/table1_cohort.csv` | idu_nat 3.825, 5.084, 17.096, 3.449, 5.223; idu_cohort 3.858, 2.900, 0.065, 3.009, 3.407; anomaly 0.438, 0.488, 0.654, 0.415, 0.478 | PASS |
| table 4 and 4b model metrics | `results/models.json`, `results/corrections.json` | all accuracy, ci95, top5 and per model g2/g3 p_holm values match; logreg 3.27e-5, mlp 4.67e-8, hgb 2.26e-5, rf 0.1121 | PASS |
| anomaly auc, patient and window | `results/stats.json`, `results/robustness.json` | patient 0.956, 1.000, 0.153; window 0.901, 1.000, 0.250; ten univariate auc values equal 1.0 | PASS |
| collisions and plurality ceiling | `results/robustness.json`, `results/corrections.json` | 58 profiles over 600 windows, largest 16, median 12, fraction 0.09667, ceiling 0.38667 | PASS |
| rank-1 | `results/rank1.json`, `results/seed2/rank1.json` | g3 pr 2.37996, lambda1 0.50007; posthoc 2.15461 and 0.66612; seed2 2.38104 and 0.51898; g5 1.94444 and 0.69164 | PASS |
| forecast table 5 values | `results/forecast.json`, `results/forecast_patient.csv` | all accuracy, ci95, within r2 and chaos mean_start values match to the printed precision | PASS |
| importance category sums and g3 impurity | `results/importance.csv` | sequence 0.44625, temporal 0.11275, interval 0.09125, dynamic -0.01250; g3 first_event_h 0.05112, t_circ_r 0.10483, t_mean_h 0.10918 | PASS |
| seed2 replication values | `results/seed_replication.json`, `results/seed2/models.json` | idu_nat 3.845, 5.016, 16.735, 3.498; all logreg and rf accuracies and ci95 match | PASS |
| g5 section | `results/corrections.json`, `results/g5/models.json` | 600/600 profiles, idu_nat 5.22347, idu_cohort 3.40714, anomaly auc 0.62893, rf 0.100 [0.075, 0.130], logreg 0.040, mlp 0.043, hgb 0.040, top5 0.413 | PASS |
| within subject table 9 | `results/within/models.json`, `results/within/patient_metrics.csv` | drift 2.238, 18.372, 3.989; rf 0.751, 0.005, 0.004; logreg 0.728, 0.000, 0.010; mlp 0.605, 0.000, 0.010; hgb 0.119, 0.005, 0.005; post idu and auc values match | PASS |
| held-out reference | `results/robustness.json` | 4.10094, 5.28661, 16.50799, 3.66525 | PASS |
| table 3 behavioral means | `results/table2_behavior.csv` | values match, but the table is computed on test windows 6 to 9 only; see residual risk | PASS with caveat |
| table 6 top 7 permutation importance | `results/table5_importance.csv`, `results/importance.csv` | listed values exist, but the listed set is not the top 7; see 7.1 | FAIL |
| h5 difference and p | `results/forecast.json`, `results/stats.json` | 0.0204 and p=0.172 belong to paired patient level means, not to the aggregate 0.496 and 0.481 values; see 7.2 | FAIL |

### 7.1 table 6 is not the top 7

the preprint says "top 7 permutation importance для g1" and lists, in order:

```text
seq_len_mean      0.0775 +- 0.0061
first_event_h     0.0765 +- 0.0071
action_1_frac     0.0503 +- 0.0024
action_7_frac     0.0468 +- 0.0050
interval_iqr_log  0.0380 +- 0.0050
interval_sd_log   0.0363 +- 0.0019
t_sd_h            0.0320 +- 0.0048
```

exact extraction command:

```sh
cd /home/esnond/echo
python3 - <<'PY'
import pandas as pd
imp = pd.read_csv("results/importance.csv")
g1 = imp[imp.group == 1].sort_values("perm_mean", ascending=False).head(12)
for rank, row in enumerate(g1.itertuples(), 1):
    print(rank, row.feature, f"{row.perm_mean:.5f}", f"{row.perm_sd:.5f}")
PY
```

observed output:

```text
1  seq_len_mean      0.07750  0.00607
2  first_event_h     0.07650  0.00713
3  action_1_frac     0.05025  0.00242
4  action_7_frac     0.04675  0.00504
5  action_6_frac     0.04625  0.00379
6  action_4_frac     0.04425  0.00551
7  action_2_frac     0.04375  0.00766
8  action_0_frac     0.04125  0.00576
9  action_5_frac     0.03875  0.00818
10 interval_iqr_log  0.03800  0.00504
11 interval_sd_log   0.03625  0.00194
12 t_sd_h            0.03200  0.00485
```

the three values printed as ranks 5 to 7 are actually ranks 10 to 12. ranks 5 to 7 are `action_6_frac`, `action_4_frac` and `action_2_frac`. the individual numbers are correct, the selection and the word "наибольший" are not. the main conclusion of the section, that sequence features dominate, still holds, but the table must be corrected.

smallest fix: replace the seven rows in table 6 and the sentence in section 4.8 with the actual top 7 from `results/table5_importance.csv`, or state a different selection rule explicitly. no change to the analysis is needed.

### 7.2 h5 uses two different estimands

`results/forecast.json` gives the aggregate next day accuracy for chaos events:

```text
days 31-60: 0.49591307362881853
days 61-90: 0.48078775139114294
aggregate difference: 0.015125322237675598
```

`results/stats.json` h5 gives the paired patient level values:

```text
mean_a: 0.48910646294142474
mean_b: 0.46873893506776630
mean_diff: 0.020367527873658406
ci95: [-0.0048676212698082495, 0.04456704061903107]
wilcoxon p: 0.17224834720781323
cohen dz: 0.15987734438063905
```

`results/forecast_patient.csv` confirms that 0.4891 and 0.4687 are the per patient means. the preprint section 4.7 and table 7 place 0.496 and 0.481 next to "различие 0.0204" and p=0.172, but 0.0204 is not the difference of those two aggregate values. the aggregate difference is 0.0151. the negative conclusion of h5 is unchanged, because both the paired test and the aggregate values show no significant decline, but the estimand must be stated.

exact extraction command:

```sh
cd /home/esnond/echo
python3 - <<'PY'
import json
f = json.load(open("results/forecast.json"))["chaos"]["events"]
s = json.load(open("results/stats.json"))["hypotheses"]["h5"]["chaos"]["events"]
print("aggregate", f["days_31_60"]["accuracy"], f["days_61_90"]["accuracy"],
      "diff", f["days_31_60"]["accuracy"] - f["days_61_90"]["accuracy"])
print("paired", s["mean_a"], s["mean_b"], "diff", s["mean_diff"],
      "ci", s["diff_ci95"], "p", s["wilcoxon_p"], "dz", s["cohen_dz"])
PY
```

observed output:

```text
aggregate 0.49591307362881853 0.48078775139114294 diff 0.015125322237675598
paired 0.48910646294142474 0.4687389350677663 diff 0.020367527873658406 ci [-0.0048676212698082495, 0.04456704061903107] p 0.17224834720781323 dz 0.15987734438063905
```

smallest fix: in `paper/preprint.md` section 4.7, table 5, table 7 and the abstract, label 0.4959 and 0.4808 as aggregate accuracy, and label 0.4891 and 0.4687 as paired patient level means. report 0.0204, ci95 and p=0.172 only for the paired comparison, or add the corresponding test for the aggregate difference. no reanalysis of the data is required.

### 7.3 table 3 is a test window subset

`results/table2_behavior.csv` is generated by `eidolon_stats.py` with `feats[feats.window >= 6]`. the values in preprint table 3 match that file. the full nine window means differ, for example g1 events per window is 394.31 for all windows and 394.90 for test windows. the preprint does not state the subset. this is a clarity defect, not a wrong number. smallest fix: add "test windows 6 to 9" to the table 3 caption.

### 7.4 table 7 mixes test statistics and families

the numbers in table 7 are traceable, but the table places p_holm values from the global seven test family next to effect sizes from pairwise tests. for h1, p_holm 9.5e-94 is the holm adjusted kruskal wallis p, while d=-13.16 is the mann whitney g1 vs g3 effect with p_holm 3.14e-57. for h4, p_holm 0.00041 is the global family, while `results/verdicts.json` reports 0.00033 for the within g1 family. the values are correct in their own families, but the table does not say which family each cell uses. smallest fix: add a column or footnote naming the test and family for each row. this does not affect the verdicts.

## 8. artifact and document consistency

these are not preprint number failures, but they are v1.2.0 release defects.

### 8.1 results/verdicts.json h1b p value

`results/verdicts.json` h1b evidence says:

```text
g1_vs_g3_p_holm: 6.5e-54
```

`results/robustness.json` idu_cohort pairwise g1 vs g3 gives:

```text
p: 1.0379048684323186e-57
p_holm: 3.113714605296956e-57
```

6.5e-54 is the idu_nat g1 vs g2 p_holm from `results/stats.json`, not the idu_cohort g1 vs g3 value. the preprint table 7 uses "n/a" for h1b, so the preprint is not affected. the artifact is.

### 8.2 results/verdicts.json row count

`results/verdicts.json` artifacts says `rows: 1991068`. `data/cohort.csv` has 1,991,067 data rows plus one header, and `results/cohort_summary.json` says `rows: 1991067`. the preprint says 1,991,067 events, which is correct. the verdicts field is header inclusive or simply wrong.

exact extraction command:

```sh
cd /home/esnond/echo
python3 - <<'PY'
import json
v = json.load(open("results/verdicts.json"))
r = json.load(open("results/robustness.json"))
print("h1b p_holm", v["hypotheses"]["h1b"]["evidence"]["g1_vs_g3_p_holm"])
print("rows", v["artifacts"]["rows"])
print([x for x in r["idu_cohort"]["pairwise"] if x["a"] == 1 and x["b"] == 3])
PY
```

observed output:

```text
h1b p_holm 6.5e-54
rows 1991068
[{'a': 1, 'b': 3, 'p': 1.0379048684323186e-57, 'p_holm': 3.113714605296956e-57}]
```

### 8.3 paper/deviations.md denies analyses that were done

`paper/deviations.md` lines 43 and 44 say:

```text
- не строился стохастический вариант g3.
- не проводился within-subject эксперимент с переключением естественного поведения в маскировку.
```

both statements contradict the same release. g5 is the stochastic intense counterfactual, documented in d15 and used in preprint section 4.11. g6 and g7 are the within subject switch, documented in d18 and used in preprint section 4.12. the "what was not done" section is stale and must be corrected. this is the most serious documentation defect because deviations.md is the preregistration audit trail.

### 8.4 hypotheses.md references a missing script

`hypotheses.md` says the power calculation is in `python/experiment_stats.py`. that file does not exist. the power is computed by `power_t` in `python/eidolon_stats.py`, and the value 0.9467 matches the preprint 0.947. smallest fix: update the path. also, h5 is registered with a paired bootstrap and cohen d, while the reported p is a wilcoxon p; the bootstrap ci and dz are present, so the deviation is small, but it is not listed in deviations.md.

### 8.5 manifest is a snapshot, not a byte reproducible file set

`make analysis` inside the extracted tarball regenerated all published numeric artifacts, but it also created six files that are absent from the published `results/` and from the manifest: `results/predictions_g1.csv` to `results/predictions_g4.csv`, `results/importance_g1.csv` and `results/importance_g3.csv`. the rerun manifest therefore has 111 hashes, not 105. in addition, `models.json`, `stats.json`, `g5/models.json` and `table4_models.csv` contain wall clock `seconds` fields, so their hashes change on every run even when every metric is identical. the published manifest is internally valid for the shipped files, but it is not a byte reproducible description of what `make analysis` produces. smallest fix: either ship the per group files and regenerate the manifest, or stop generating them; and move timing fields out of hashed result files.

## 9. residual risks

1. cross platform bitwise replay is unverified. the replay is local, with one compiler and one libm. PROVENANCE.md already labels this UNCERTAIN. the code uses `exp`, `log`, `pow`, `sin` and `sqrt`; cross platform last digit equality is not claimed.
2. the preregistration timestamp is self reported. there is no external timestamp authority, no OSF or zenodo deposit, and no independent witness for the original hypotheses.md text.
3. the release tarball is not gpg signed. the sha256 sidecar and the manifest are self attested. the annotated tag v1.2.0 exists locally, but no signed tag or remote witness was verified.
4. the python environment is pinned by version numbers, not by hash locked wheels. the current environment hash matches the manifest, but a different BLAS, CPU or package build can change last digits.
5. table 3 values are test window values and the caption does not say so. full window means differ slightly.
6. table 7 mixes global family p_holm values with pairwise effect sizes and within family values. the numbers are traceable, but the estimand labels are missing.
7. results/verdicts.json has two wrong fields: the h1b p_holm and the row count. the preprint is not affected, but the artifact is cited from README.md.
8. paper/deviations.md has stale "what was not done" bullets that contradict g5 and within subject analyses. this is a credibility risk for the preregistration audit trail.
9. hypotheses.md references a missing `python/experiment_stats.py` and does not log the switch from a paired bootstrap p to a wilcoxon p for h5.
10. the worktree gained an untracked `paper/journal_package.md` at 21:58 local during verification, from a parallel process. it is not in the v1.2.0 tarball and not covered by the manifest. the verification applies to the tagged tree and the tarball, not to that file.

## 10. what is closed

the core v1.2.0 reproducibility claims are closed on this machine. the generator is deterministic for all published data sets, g5 preserves the g1 to g4 raw prefix, within preserves the g1 prefix, the manifest verifies 105/105, the python tests and sanitizers pass, the tarball verifies and rebuilds to the recorded binary, and a full `make analysis` rerun reproduces every published main, g5 and within csv and figure, except the `seconds` column in table4_models.csv, and every non timing json numeric field. the seed2 replication also reproduces.

the central scientific claims survive the numeric cross check: idu_nat rises to g3, idu_cohort collapses in g3, g3 collapses into 58 profiles, rank-1 is refuted on observed features, g5 restores uniqueness with the same parameters, within subject masking destroys identification, and the forecast has no within patient skill. the two preprint reporting defects do not overturn these claims.

## 11. summary

summary: 6 closed, 2 narrowed, 4 open, 4 unverified.

the single finding that most needs the owner's attention: the h5 estimand mismatch in paper/preprint.md, because a p value and a difference of 0.0204 are attached to table values 0.496 and 0.481 whose difference is 0.0151. the negative h5 verdict survives, but the estimand must be stated before submission. the stale paper/deviations.md bullets are the most urgent documentation correction, because they falsely state that g5 and the within subject switch were not done.
