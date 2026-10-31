# adversarial review of paper/DRAFT.md

date: 2026-10-31
reviewer role: adversary, hostile methods and security reviewer
scope: `paper/DRAFT.md`, checked against `results/verdicts.json`, `results/corrections.json`, `results/within/models.json`, `results/within/postonly.json`, `results/verification.json`, `results/robustness2.json`, `results/methodologist_checks.json`.

## verdict

the draft is publishable as a synthetic methods and negative results paper after the fixes below. it is not a demonstration on real patients, not a proof about masking in general, and not a privacy guarantee. the draft already states this; the remaining risk is reader overgeneralization from the title and headline numbers.

## objections and responses

| id | objection | severity | response | status |
|---|---|---|---|---|
| a1 | all data are synthetic; external validity is absent | high | stated in abstract, methods and limitation 1; causal claim limited to the generator | accepted, no fix needed |
| a2 | g3 is a deterministic quantized construct, not natural masking | critical | g5 counterfactual with the same affine parameters; g3 and g5 differ in determinism and quantization, so the cause is not fully isolated | accepted, limitation 2 |
| a3 | within-subject top1 at chance is only transfer failure | critical | pre-only and post-only controls added; g6 post-only 0.085, 17x chance; g7 1-4x chance; claim narrowed to transfer failure plus residual in-domain identification | accepted, draft section 2.3 |
| a4 | class counts and model capacity differ across groups | high | matched 150-class sensitivity; per-model results reported; rf selected on g1 validation and is a tie | accepted, limitation 5 and 6 |
| a5 | many analyses were added after the primary results | high | g5, matched, within, open-set, detectability and effective classes are labeled exploratory; h1-h7 verdicts unchanged | accepted, limitation 7 |
| a6 | h4 uniqueness-identifiability association is weak and model-dependent | high | downgraded to exploratory; per-model rho 0.167-0.211; consensus inflation stated | accepted, section 2.5 |
| a7 | h5 is underpowered and was called refuted | high | relabeled not supported/inconclusive; ci includes zero; within-patient r2 negative | accepted, section 2.5 |
| a8 | open-set g3 auc 0.993 looks like individual signature | high | explained as window duplication; within-profile auc 0.5; g7 eer 0.455 is the relevant open-set result | accepted, section 2.4 |
| a9 | anomaly score is one-sided; g7 and g4 are separated in the low direction | medium | two-sided auc g7 0.933 and g4 0.847 reported; detector choice stated | accepted, limitation 9 |
| a10 | exact-profile ceiling is a bound only for profile-based classifiers | medium | stated as exact-profile ceiling; rf and hgb equal it; no claim beyond that bound | accepted, section 2.2 |
| a11 | preregistration is self-reported, no external timestamp, no public DOI | high | stated in limitation 12; provenance file records the boundary; public deposit pending | accepted, cannot be fixed without human action |
| a12 | prior manuscript in refs/ with the same hypothesis is undisclosed | high | stated in limitation 12; disclosure before submission is a human decision | accepted, pending |
| a13 | g6 and g7 are different patients, so deterministic versus stochastic is between-subject | medium | stated in limitation 4; only pre/post is within-patient | accepted |
| a14 | g5 top1 0.100 is 15x chance and is not privacy | medium | stated in honesty check and section 2.4; profile uniqueness restored, residual identification remains | accepted |
| a15 | rank-1 refutation is construction-dependent | medium | limited to g3 uniform-s; g6 post-only 1.553 and 0.771 reported | accepted, section 2.5 |

## rejected objections

- "the paper should not report negative results because they weaken the story": rejected. the negative results are the contribution; hiding them would be cherry-picking.
- "remove the synthetic limitation from the abstract": rejected. the limitation is part of the claim.
- "drop the within-subject experiment because post-only is not at chance": rejected. post-only is exactly why the claim was narrowed; the experiment is informative.

## fixes applied after this review

1. abstract no longer says the mask destroys identity; it says pre-to-post transfer fails and residual identification is template-bound or concentration-bound.
2. h2 equality language removed; per-model heterogeneity and rf tie are explicit.
3. h4 consensus inflation and per-model rhos added.
4. h5 labeled not supported, not refuted.
5. open-set g3 duplication and within-profile auc 0.5 added.
6. g5 residual 15x chance added.
7. anomaly two-sided auc and idu_cohort composition note added.
8. exploratory status placed next to every post hoc block.

## residual risks

- real-world validation absent; the paper is a simulation study.
- g3 and g5 do not separate determinism from quantization.
- within mask scalar concentration is a design artifact.
- no public DOI, external preregistration, or named authors yet.
- hgb is underfit; h7 remains inconclusive.

none of these is hidden in the draft. the author must decide whether to submit as a simulation paper or collect real data first.

## pass 2 note, 2026-10-31

re-reviewed `paper/DRAFT.md` after the second `/paper` run. changes checked: h5 post hoc power 0.354 and mde dz 0.285, h4 per-model bootstrap ci, g5 seed2, confirmatory versus exploratory table, main cohort wording, chance row and table captions.

no new overclaim found. the underpowered h5 and the weak h4 are now explicit, g5 residual 15x chance is explicit, and the exploratory labels travel with every post hoc block. residual risks are unchanged: synthetic data, g3 construct, g5 determinism versus quantization, mask scalar concentration, partial seed coverage, no public doi and no external preregistration.

## pass 3 note, 2026-10-31

reviewed `paper/DRAFT_EN.md` against `paper/DRAFT.md` and the results files. the english draft keeps the same numbers, the same five honesty statuses, the same exploratory labels and the same limitations. no translation drift found: h2 is not described as equality, h5 is not described as refuted, rank-1 is not described as confirmed, and within-subject is described as transfer failure with post-only residual identification. the mechanical gate checks both files and passes.

residual risks unchanged: synthetic data, g3 construct, g5 determinism versus quantization, mask scalar concentration, partial seed coverage, no public doi, no external preregistration, prior manuscript disclosure pending.
