# paper preparation workflow

project: eidolon
date: 2026-10-31
version: 1.3.0
status: stages executed by orchestrator; agent spawn blocked by provider twice (unusual activity), retry after 75 s also blocked. the workflow was executed directly on the repository, the block is logged here.

outputs: `paper/DRAFT.md` (corrected draft), this report, `results/methodologist_checks.json`.

## stage 1. prioritizer

### keep list, ordered by narrative importance

| rank | block | why it stays | status |
|---|---|---|---|
| 1 | h1 and h1b: anomaly versus uniqueness, g3 template collapse | central result; separates two constructs the original theory conflated | confirmatory, preregistered |
| 2 | within-subject g6/g7 with pre-only and post-only controls | strongest causal evidence; same patient before and after mask; separates transfer failure from identity destruction | exploratory, added after primary |
| 3 | g5 stochastic counterfactual | separates the affine parameter map from the deterministic emitter; explains why g3 collapses | exploratory |
| 4 | h2 per-model heterogeneity and matched 150-class sensitivity | prevents the false claim that g2 and g3 are equal; shows model dependence | confirmatory plus exploratory |
| 5 | open-set verification and mask detectability | answers the known or unknown question; shows both masks are detectable, for different reasons | exploratory |
| 6 | h3 anomaly detection with univariate triviality | explains that anomaly auc 1.000 is a threshold, not a rank-1 signature | confirmatory, but trivially satisfied |
| 7 | h6 rank-1 refutation | negative result, preregistered criterion failed | confirmatory, refuted |
| 8 | h5 forecast without within-patient skill | negative control; removes the long-horizon prediction claim | confirmatory, not supported |
| 9 | h4 uniqueness-identifiability association inside g1 | small and inconsistent per model; keep only as exploratory | downgraded |
| 10 | h7 g4 control | inconclusive; keep in limitations and supplement | inconclusive |
| 11 | seed 20261031 | robustness for idu and logreg/rf; g3 invariant by construction | partial |

### cut or condense

| block | action | reason |
|---|---|---|
| full 24-parameter table | move to supplement | methods already longer than the journal norm |
| feature importance section | supplement only | secondary to the central claim |
| forecast learning curve | supplement only | no skill; the curve does not change the conclusion |
| per-model table beyond logreg, rf, mlp, hgb | supplement | four models suffice to show heterogeneity |
| matched 100-class g4 analysis | cut | g4 has n=100 and answers h7 separately; mixing with h2 confuses the estimand |
| raw event examples | supplement | not needed for the argument |
| Uglanova citations | keep in introduction and discussion | contextual, not evidence for the results |

### three defensible headline claims

1. deterministic masking produces an anomalous template, not a unique identity: 150 patients collapse into 58 profiles, rf and hgb top1 equal the exact-profile ceiling 0.3867, and anomaly auc 1.000 is reproducible with a single regularity feature.
2. stochastic intense masking with the same affine parameters restores profile uniqueness (600 of 600) and hides open-set identity (eer 0.455 against chance 0.497), but remains detectable through reduced action entropy (auc 0.921-0.942).
3. the strong paradox is refuted: rank-1 fails at 2.380 and 0.500, pre-to-post transfer falls to chance for both masks, and the residual in-domain identification is template-bound (g6 0.085, 17x chance) or concentration-bound (g7 1-4x chance), not a unique signature.

### must be labeled exploratory or dropped

- g5, matched 150, per-model h2, within g6/g7, post-only/pre-only, open-set, detectability, effective classes.
- h4 must be downgraded to exploratory and reported with per-model rhos.
- h7 must stay inconclusive, not refuted.
- the long-horizon prediction limit is dropped.

## stage 2. methodologist

### claim validation

| claim | evidence | ci, effect, n | issue | verdict |
|---|---|---|---|---|
| h1 idu_nat g3 > g2 > g1 | 3.825, 5.084, 17.096, n=600 | d=-13.16 [-14.33, -12.43], kruskal p=1.36e-94, holm 9.53e-94 | idu_nat is anomaly distance, not uniqueness | supported for anomaly |
| h1b idu_cohort g3 > g2 > g1 | 3.858, 2.900, 0.065, n=600 | g3 ci [0.054, 0.078] | p values differ across files (6.5e-54 against 3.1e-57); cite means and ci, not p | refuted |
| h2 strict order g1 > g2 > g3 | rf 0.818, 0.395, 0.387; logreg 0.769, 0.382, 0.293; mlp 0.686, 0.313, 0.192; hgb 0.135, 0.063, 0.387 | per-model p_holm 3.3e-5, 4.7e-8, 2.3e-5, 0.112 | average p=0.870 hides opposite signs; selected rf is a tie | not established as order; heterogeneity supported |
| h3 anomaly auc g3 vs g1 >= 0.80 | patient auc 1.000; window 1.000 | 10 univariate features also auc 1.000 | multivariate claim is trivial | supported, trivial |
| h4 idu and identification inside g1 | consensus rho 0.275 [0.151, 0.394], p_holm 0.00033 | per model idu_nat rho 0.167 [0.022, 0.299], 0.193 [0.056, 0.321], 0.211 [0.076, 0.340], 0.175 [0.035, 0.307]; all ci include 0.20 | 3 of 4 point estimates below 0.20; consensus inflated by averaging | downgraded to exploratory, weak |
| h5 chaos forecast declines with horizon | aggregate 0.496 against 0.481; paired 0.489 against 0.469 | diff 0.0204 [-0.0049, 0.0446], p=0.172, dz=0.160, n=100; achieved power 0.354, mde dz 0.285 for power 0.80 | ci includes zero and a meaningful decline; no skill; underpowered | not supported or inconclusive, not refuted |
| h6 rank-1 | pr 2.380, lambda1 0.500, n=1350 windows | posthoc 2.155 and 0.666; seed2 2.381 and 0.519 | construction dependent; g6 pre/post mixture gives 1.468 and 0.811, post-only 1.553 and 0.771 | refuted for g3 uniform-s; not universal |
| h7 g4 control | rf 0.025 [0.010, 0.043]; seed2 0.0075 [0.000, 0.018] | patient level p_holm 0.087 over 5 models, 0.348 over 7 | one seed above threshold, one at chance | inconclusive |
| within pre-to-post transfer | 0.751 [0.711, 0.789], 0.005 [0.000, 0.015], 0.004 [0.000, 0.009] | n=200 per group, chance 0.005 | cross-domain transfer failure, not identity destruction | transfer failure supported |
| within post-only | g6 0.085 [0.050, 0.128]; g7 0.020 [0.008, 0.035] rf | g6 17 profiles, ceiling 0.085; g7 800 profiles; patient-level g6 p 3.1e-12, g7 rf p 0.0010 | residual identification in-domain; g7 weak | supported as template and concentration effects |
| open-set | g1 0.894, g2 0.689, g3 0.993, g4 0.502, g5 0.795, g6 0.951, g7 0.558 | all with cluster ci; g3 within-profile auc 0.5 | g3 auc measures duplication | g3 duplication; g7 hides identity |
| g5 | 600 of 600 profiles; rf 0.100 [0.075, 0.130] | idu_nat 5.223, idu_cohort 3.407, anomaly auc 0.629 | 0.100 is 15x chance, not privacy | profile uniqueness restored, residual identification remains |

### required_fixes

| id | severity | fix | applied |
|---|---|---|---|
| m1 | critical | replace "mask destroys identity" with "pre-to-post transfer fails; post-only residual identification is template-bound or concentration-bound" | yes |
| m2 | major | downgrade h4 to exploratory; report per-model rhos; do not call it confirmed | yes |
| m3 | major | call h5 "not supported or inconclusive", not refuted; label underpowered | yes |
| m4 | major | remove any g2 approximately g3 equality claim; report per-model heterogeneity and selected rf tie | yes |
| m5 | major | state that g3 open-set auc 0.993 measures duplicate windows; inside a profile auc 0.5 | yes |
| m6 | major | state that g5 top1 0.100 is 15x chance; not a privacy guarantee | yes |
| m7 | minor | limit rank-1 refutation to the g3 uniform-s construction; report g6 post-only 1.553 and 0.771 | yes |
| m8 | major | label g5, matched, within, open-set, detectability and effective classes exploratory; no upgrade of h1-h7 | yes |
| m9 | major | report seed coverage: primary plus seed2 logreg/rf; g3 invariant; hgb and mlp not replicated; within seed2 exists for logreg/rf | yes, partial |
| m10 | minor | report anomaly one-sided and two-sided auc: g7 0.933, g4 0.847 | yes |
| m11 | minor | state that idu_cohort depends on cohort composition; use same-file g1 baseline | yes |
| m12 | minor | regenerate manifest and release after the draft edits | pending author review; the release is not rebuilt for an unreviewed draft |
| m13 | minor | disclose the prior manuscript in refs/ and its unknown status before submission | pending, human decision |

## stage 3. editor

sections written in `paper/DRAFT.md`: abstract (russian and english), methods, results, limitations, honesty check, reproduction commands. the draft applies m1-m8 and m10-m11, labels all post hoc analyses exploratory, and does not upgrade any preregistered verdict. the full prior preprint remains in `paper/preprint.md`; the draft is the submission text after the methodologist pass.

## stage 4. adversary

full hostile review: `paper/ADVERSARIAL_REVIEW.md` (15 objections, 3 rejected, 8 fixes applied). summary:

| objection | response | residual risk |
|---|---|---|
| all data synthetic | stated in abstract and limitations; causal claim limited to generator | external validity absent |
| g3 is a deterministic construct | g5 counterfactual with same affine parameters; post-only controls | determinism and quantization are not fully separated |
| within top1 at chance is only transfer failure | post-only controls added; g6 0.085, g7 1-4x chance | mask s concentration is a design artifact |
| class counts differ across groups | matched 150-class sensitivity; per-model reporting | g4 and g5 not equally matched |
| model shopping | one rf selected on g1 validation; per-model results retained | hgb underfits g1 and g2 |
| many exploratory analyses | explicit exploratory labels; h1-h7 verdicts unchanged | garden of forking paths remains |
| h4 weak | downgraded to exploratory; per-model rhos 0.167-0.211 | small effect |
| h5 underpowered | labeled not supported; no long-horizon claim | the manipulation may be too weak |
| g3 open-set auc high | within-profile auc 0.5; duplication explained | readers may misread 0.993 |
| anomaly one-sided | two-sided auc reported: g7 0.933, g4 0.847 | detector choice matters |
| no public DOI, self-reported preregistration | provenance states the boundary; no claim of external registration | journal may reject |
| licenses and refs | MIT code, CC BY paper and data; refs excluded from release | prior manuscript disclosure pending |

## stage 5. fixes applied

- h4 downgraded, h5 relabeled, h2 equality removed, within and g5 and open-set interpretations narrowed.
- anomaly two-sided and idu_cohort composition notes added.
- exploratory status placed next to every post hoc block.
- honesty check table added to `paper/DRAFT.md`.
- honesty check table is filled in `paper/DRAFT.md` section 4.
- manifest and release are intentionally not regenerated for an unreviewed draft; `release/eidolon-v1.3.0` remains the last reviewed artifact. regenerate after author acceptance.
- pending human items: author metadata, public DOI, prior manuscript disclosure, external preregistration for future analyses.

## verdict

the draft is internally consistent with the results files and does not claim more than the data support. it is ready for author review as a submission draft, not for submission until the human metadata and disclosure items are closed.


## pass 2, 2026-10-31

trigger: `/paper` was rerun by the user on the current `paper/DRAFT.md`. agents were not spawned because the provider block from pass 1 could not be verified as lifted; the orchestrator executed the same stages directly.

changes applied in pass 2:

- h5 power analysis added: achieved power 0.354 for dz=0.160, n=100, alpha=0.05; mde dz=0.285 for power 0.80. the hypothesis is explicitly underpowered.
- h4 per-model bootstrap ci added; all four idu_nat ci include 0.20, three point estimates below 0.20.
- g5 seed2 added: idu_nat 5.258 against 5.223, idu_cohort 3.475 against 3.407, rf top1 0.122 against 0.100, delta ci [-0.020, 0.062].
- confirmatory versus exploratory table added to methods.
- main cohort wording clarified: 1 991 067 events refer to the primary 600 patient cohort, not to g5 and within.
- chance row added to the identification table.

no changes to the keep/cut list from pass 1. no new overclaims found. the draft remains a simulation and negative results paper. the same human blockers remain: author metadata, public doi, prior manuscript disclosure, external preregistration for future analyses, and release regeneration after acceptance.

## pass 3, 2026-10-31

trigger: third `/paper` run. the user asked whether everything is translated into two languages and whether the defense passed, then invoked the workflow again. the agent provider block was not retried; stages executed directly.

- prioritizer: keep/cut list unchanged. no new result block.
- methodologist: the same required fixes apply. key numbers and honesty statuses were checked in both languages by `make paper`.
- editor: full english draft written as `paper/DRAFT_EN.md`, sections abstract, methods, results, limitations, honesty check, reproduction commands. no russian claim was upgraded in translation.
- adversary: translation drift review added to `paper/ADVERSARIAL_REVIEW.md`; no new overclaim found.
- gate: `make paper` checks both drafts, 18 required numbers, 5 honesty statuses, forbidden punctuation and overclaim patterns. result `PAPER_GATE_PASS: 2 files, 18 numbers, 5 statuses`.
- status: bilingual draft complete. english project site, native proofread, author metadata and public doi remain.

