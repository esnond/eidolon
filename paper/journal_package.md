# journal submission package

project: eidolon
artifact version: 1.2.0
package date: 2026-10-30
status: draft for author completion. placeholders in square brackets are not filled. no author names, affiliations, emails, ORCID identifiers, repository DOIs or reference DOIs were invented.

source material: `paper/preprint.md`, `results/verdicts.json`, `README.md`, `NOTICE`, `PROVENANCE.md`, `CITATION.cff`, `results/manifest.txt`, `requirements.txt`.

## 1. english title

anomaly without uniqueness: deterministic masking in a synthetic cohort of 600 patients

the title is lowercase by project style. apply the journal's required capitalization at typesetting. the title matches `NOTICE` and `CITATION.cff`.

## 2. english abstract

removing direct identifiers from records does not remove timing, sequence and interval information. we tested whether intense technical masking of digital behavior creates a flat rank-1 profile that is paradoxically easier to flag as an anomaly than natural variability. a deterministic c99 generator produced 600 synthetic patients over 90 days, with 24 latent parameters and 1,991,067 events, in four groups: natural (n=200), moderate masking (n=150), intense deterministic masking (n=150) and a daily resampled control (n=100), plus an exploratory stochastic intense group g5 (n=150). we computed 51 features in windows of 10 days, measured anomaly as distance to the natural manifold and uniqueness as distance to 10 cohort neighbours, and ran closed set identification with five models and a cluster bootstrap over patients. distance to the natural manifold rose from 3.825 to 5.084 to 17.096 across g1 to g3, while within cohort uniqueness fell from 3.858 to 2.900 to 0.065; g3 collapsed into 58 distinct feature vectors in 600 test windows. random forest top1 was 0.818 [0.784, 0.850] for g1, 0.395 [0.350, 0.442] for g2, 0.387 [0.310, 0.460] for g3 and 0.025 [0.010, 0.043] for g4. per model comparisons of g2 and g3 disagreed in direction. the preregistered rank-1 criterion was refuted (participation ratio 2.380, share of the first component 0.500). g5, with the same intense parameters and a stochastic emitter, gave 600 of 600 unique profiles and top1 0.100 [0.075, 0.130]. deterministic masking produced an anomalous template, not a unique identity; the strong paradox is limited to the deterministic regime.

word count: 250 (abstract body only, excluding this line and keywords; whitespace token count).

keywords: digital anonymity, reidentification, synthetic cohort, behavioral biometrics, anomaly detection, reproducibility.

note: all data are synthetic. the abstract does not claim generalization to real patients or to stochastic masking. the exploratory status of g5 and the within patient switch is stated in the manuscript.

abstract selection note: the 250 word limit excludes two negative results that remain mandatory in the manuscript: the forecast hypothesis h5 is refuted (the apparent decline in chaos accuracy has a confidence interval that includes zero, p=0.172, and within patient r2 is negative; reconcile the table discrepancy listed in section 10) and the g4 control is inconclusive (rf 0.025 on the primary seed, 0.0075 on the second seed, patient level p_holm 0.087 over five models). do not drop them from the results section or from the cover letter discussion.

## 3. authors and affiliations, placeholders

the current project attribution is "eidolon project contributors" (`NOTICE`, `CITATION.cff`). this is a collective label, not a person. journals require named individuals who can approve the submission and take accountability, so the collective label cannot serve as the author list. the table below is a layout placeholder; add or remove rows to match the final author list.

| order | role | placeholder | status |
|---|---|---|---|
| 1 | first author | [author 1 full name] | missing |
| 2 | coauthor | [author 2 full name] | missing |
| 3 | coauthor | [author 3 full name] | missing |
| corresponding | corresponding author | [full name, email, postal address, telephone if required] | missing |

affiliations:

1. [affiliation 1: institution, department, city, country]
2. [affiliation 2: institution, department, city, country]

identifiers:

- ORCID for each author: [ORCID identifier, not supplied]
- author degrees, positions and titles as required by the journal: [not supplied]
- author contributions in CRediT or journal format: [not supplied]
- equal contribution, corresponding author and present address notes: [not supplied]

## 4. cover letter skeleton

[submission date]

[editor full name]
[editor role]
[journal name]
[journal postal address]

dear [editor name],

we submit the manuscript "anomaly without uniqueness: deterministic masking in a synthetic cohort of 600 patients" for consideration as a [article type] in [journal name].

the study asks whether intense technical masking of digital behavior creates a flat rank-1 profile that is easier to detect as an anomaly than natural variability. a deterministic c99 generator produced 600 synthetic patients, 90 days and 1,991,067 events in four groups, with an exploratory fifth group. the manuscript reports positive and negative results: anomaly rises and uniqueness collapses in the deterministic mask, the preregistered rank-1 criterion is refuted, per model identification tests disagree in direction, and the same intense parameters with a stochastic emitter do not collapse. we do not claim generalization to real patients or to masking in general.

the work fits [journal name] because [one or two sentences on scope, readership and prior work in the journal; insert verified examples only].

the manuscript is not published and is not under consideration elsewhere [confirm]. all authors approved the submission [confirm]. the data are synthetic, and no ethics approval or consent was required [confirm against journal policy]. competing interests: [none declared; confirm]. funding: [confirm; add grant numbers if any]. data and code statements are in the manuscript; no public repository DOI exists at submission [confirm or insert DOI]. a preprint [is / is not] posted at [preprint DOI or remove this sentence]. suggested reviewers: [name, affiliation, email], [name, affiliation, email], [name, affiliation, email]; excluded reviewers: [names, if any]. all suggested reviewers are supplied by the authors and have no known conflict [confirm].

manuscript length: [word count], [number of figures], [number of tables], [number of supplementary files].

sincerely,
[corresponding author full name]
[affiliation]
[email]
[ORCID identifier]

## 5. VAK checklist

this is a working checklist, not a legal interpretation of VAK rules. exact requirements change. verify each item against the current VAK regulation and against the target journal's author guidelines. entries marked UNCERTAIN are not supported by the project material.

| item | required content | current state | action |
|---|---|---|---|
| journal listing | target journal included in the VAK list for the declared specialty | no target journal selected | select and verify; UNCERTAIN until checked |
| branch of science and specialty code | [code] | missing | supply per journal |
| UDC index | [UDC] | missing | assign with the journal |
| russian title, abstract, keywords | russian text | present in `paper/preprint.md` | align with the final english abstract and journal length limit |
| english title, abstract, keywords | english text | present in this package | check journal word limit and translation |
| author list | full names, degrees, positions, affiliations, postal addresses, countries | collective label only | supply named authors and affiliations |
| corresponding author | name, email, postal address | missing | supply |
| ORCID | identifier for each author | missing | supply |
| author contributions | CRediT or journal wording | missing | supply |
| conflict of interest | statement from every author | preprint says none declared | confirm and adapt wording |
| funding | statement and grant numbers | preprint says not declared | confirm; add numbers if any |
| ethics statement | synthetic data statement and waiver wording | preprint has a synthetic statement | adapt to journal wording; confirm that no approval is required |
| data availability | statement or repository link | drafted in section 7 | insert into manuscript |
| code availability | statement or repository link | drafted in section 8 | insert into manuscript |
| references | journal style, DOIs where available | bibliography exists; DOIs absent | add DOIs without inventing them |
| preprint disclosure | state whether a preprint exists | no preprint DOI in the project material | decide and disclose |
| copyright and license | journal agreement and license compatibility | code MIT, text and data CC BY 4.0 | check compatibility with any copyright transfer |
| reviewer suggestions | names, affiliations, emails, conflicts | missing | supply |
| anonymized version | manuscript without author identifiers | not prepared | prepare if the journal uses double blind review |
| plagiarism and self citation check | report or confirmation | not performed | run before submission |
| russian language editing | checked text | not verified | arrange |
| supplementary material | figures, tables, data dictionary | figures and tables exist inside the preprint | assemble per journal |
| word and figure limits | counts against journal limits | not computed for journal format | compute |
| VAK rule on preprints | effect of posting on eligibility | UNCERTAIN | verify current regulation |
| public deposit | repository and DOI | none | create a deposit and insert the DOI |

## 6. bioRxiv checklist

verify each item against the current bioRxiv submission instructions. do not rely on this list as a normative source.

| item | required content | current state | action |
|---|---|---|---|
| author accounts and approval | all authors approve posting | missing | collect approvals |
| author list | names, affiliations, corresponding email | collective label only | supply named authors |
| title and abstract | english text | present in sections 1 and 2 | paste after journal style check |
| subject category | one or more categories | missing | choose |
| license | license selection at posting | project text and data are CC BY 4.0 | select CC BY 4.0 for consistency, or record a different choice |
| competing interests | statement | preprint says none declared | confirm |
| funding | statement | preprint says not declared | confirm |
| ethics statement | synthetic data, no human subjects | draft in `paper/preprint.md` | insert |
| data availability | statement | drafted in section 7 | insert |
| code availability | statement | drafted in section 8 | insert |
| preprint DOI | assigned after posting | not assigned | record after posting |
| journal compatibility | target journal accepts preprints | target not selected | verify before posting |
| version and date | artifact version and posting date | artifact 1.2.0, 2026-10-30 | assign preprint version |
| screening | no personal data, no clinical images, no identifiable records | data are synthetic | confirm |
| figures and supplements | accepted formats and size limits | PNG figures and CSV results | check formats and size |
| references | complete list, DOIs where available | present; DOIs missing | add DOIs without inventing them |
| ORCID linkage | ORCID for authors | missing | supply |
| prior posting | disclose previous versions | none found in project material | confirm |
| full english manuscript | full text in english | missing; only a russian preprint and an english abstract exist | translate and prepare the full english text |
| reporting checklist | required checklist if any | none identified for a simulation study | confirm with the target journal |

## 7. data availability statement

draft for the manuscript:

all data are synthetic and are generated by the deterministic generator in `src/`. the primary cohort is produced with seed 20261030 by `./eidolon_gen --seed 20261030 --out data/cohort.csv`. the chaos, g5 and within patient cohorts use the flags recorded in `README.md` and `results/manifest.txt`. the primary cohort file has sha256 `7841bd667c35ee437eea9d1c58016990c081ed022d8f042389fb356b487ce1a9`. `results/manifest.txt` records the binary sha256, compiler, cflags, seed, python package versions, environment hash, per file sha256 and the determinism verdict. the replication uses seed 20261031. the release archive is `release/eidolon-v1.2.0.tar.gz`, with its sha256 in `release/eidolon-v1.2.0.sha256`. no public repository, dataset DOI or accession number exists at the time of writing; the archive is a local file and is not a citable public deposit. documents from third parties in `refs/` are not redistributed and are excluded from the release archive.

points the statement must not hide:

- bitwise replay was verified on one compiler and one libm. cross platform bitwise equality is UNCERTAIN and is not claimed (`PROVENANCE.md`).
- the python pipeline is pinned by package versions in `requirements.txt`, not by wheels locked by hash. reruns with a different BLAS, CPU or package build can differ in the last digits (`PROVENANCE.md`).
- the release archive is not signed with GPG, and its sha256 is attested by the project itself, not by an independent timestamp authority (`PROVENANCE.md`).

## 8. code availability statement

draft for the manuscript:

code is in `src/` (C99), `python/`, `tools/`, `tests/` and `Makefile`. build with `make`. the full pipeline runs with `make analysis`. the determinism check runs with `make check`. the manifest is written by `make manifest`. sanitizer tests run with `make test`. the environment is pinned by `requirements.txt`: numpy 2.5.4, pandas 3.1.0, scikit-learn 1.9.1, scipy 1.18.1 and matplotlib 3.11.2. pytorch was not used; the neural model is sklearn `MLPClassifier`. the code is released under the MIT license (`LICENSE`). no public code repository and no repository DOI exist at the time of writing.

## 9. license statements

from `NOTICE` and the license files:

- code in `src/`, `python/`, `tools/`, `tests/` and `Makefile`: MIT license, see `LICENSE`. copyright (c) 2026 eidolon project contributors.
- `paper/preprint.md`, `README.md`, `paper/deviations.md`, `paper/editor_review.md`, results tables and figures, and synthetic csv data generated by the generator: CC BY 4.0, see `LICENSE-CC-BY-4.0`.
- `refs/`: documents from third parties, not licensed by this project, excluded from `release/eidolon-v1.2.0.tar.gz`.

license gaps to resolve before submission:

- this file, `paper/journal_package.md`, is not named in `NOTICE`. the stated CC BY 4.0 scope names `paper/preprint.md`, not this file. assign a license explicitly or place this file under the same CC BY 4.0 terms by an updated notice.
- `LICENSE` names "eidolon project contributors" as the copyright holder. confirm that this collective label is acceptable to the publisher, or replace it with the named authors or institutions.
- the journal may require copyright transfer or an exclusive license. check whether the existing CC BY 4.0 grant on the preprint and data is compatible with the journal agreement. do not sign a transfer that conflicts with the stated license without a documented decision.
- figure files in `results/figures/` are covered by the CC BY 4.0 statement for results tables and figures. confirm this with the publisher if figures are reused from another source; no source is identified in the project material.
- the russian preprint and the english manuscript must carry the same license statement. update both if the license changes.

## 10. missing metadata

| item | why it is needed | current state |
|---|---|---|
| author names | authorship and accountability | missing; only "eidolon project contributors" exists |
| affiliations with postal addresses and countries | title page and metadata | missing |
| corresponding author name, email and postal address | submission and correspondence | missing |
| ORCID for each author | journal and preprint metadata | missing |
| author order and equal contribution notes | title page | missing |
| CRediT or journal author contributions | declarations | missing |
| funding statement and grant numbers | declarations | preprint says not declared; confirm |
| competing interests confirmation from every author | declarations | preprint says none declared; confirm |
| ethics approval or waiver wording for the target journal | declarations | synthetic statement exists; journal wording missing |
| acknowledgements | declarations | missing |
| target journal and article type | cover letter and checklists | missing |
| editor name, role and address | cover letter | missing |
| submission date | cover letter | missing |
| manuscript identifier, if assigned | correspondence | missing |
| public code repository URL and DOI | code availability | missing |
| public data repository URL and DOI | data availability | missing |
| preprint DOI and posting date | disclosure | missing; no deposit exists |
| independent timestamp or signature for the preregistration | preregistration claim | missing; registration time is self reported |
| DOIs for the reference list | references | missing; do not invent |
| public source for the cited internal report `proteus (2026)` | references | internal path only, not publicly available |
| UDC index | VAK metadata | missing |
| specialty code and branch of science | VAK metadata | missing |
| russian and english keywords in journal format | metadata | present in the preprint; journal format not checked |
| reviewer suggestions and exclusions | submission | missing |
| anonymized manuscript version | peer review | not prepared |
| full english manuscript | preprint and journal submission | missing; only a russian preprint and an english abstract exist |
| word count, figure count and table count in journal format | submission limits | not computed |
| figure formats and resolution required by the journal | production | PNG files exist; journal requirements not checked |
| supplementary file list and data dictionary | production | results csv and README exist; package not assembled |
| license for `paper/journal_package.md` | license statement | not assigned |
| public release URL and independent hash attestation | availability | local archive only; hash is attested by the project |
| VAK rule on preprint posting | eligibility | UNCERTAIN; verify current regulation |
| event count unit | consistency across abstract, tables and json | preprint says 1,991,067 events; `cohort_summary.json` says rows 1991067; `verdicts.json` says rows 1991068; `data/cohort.csv` has 1,991,067 data rows plus the header. reconcile the wording and state the unit. |
| h5 chaos accuracy values | consistency of the refuted forecast claim | preprint table 5 reports 0.496 and 0.481, while `verdicts.json` reports means 0.4891 and 0.4687 and a difference of 0.0204. the difference matches the verdicts means, not the rounded table values. reconcile the estimand and the table before submission. |
| window count unit | consistency across tables | `results/cohort_summary.json` uses all windows per patient (g1 1800, g2 1350, g3 1350, g4 900); the preprint table 2 uses test windows (g1 800, g2 600, g3 600, g4 400). state which unit each table uses. |
| within patient experiment status | internal consistency | `paper/deviations.md` section "что не делалось" still says the within subject switch experiment was not performed, while preprint section 4.12 and `results/within/` report it. remove the stale line or explain the sequence. |
| table numbering | production | preprint table numbers skip from 7 to 9 and include table 4b. renumber before submission. |
| g4 description | methods accuracy | g4 is a daily resampled natural control, not pure white noise. the preprint discloses this; ensure the abstract and cover letter never call it white noise. |
| exploratory labels | claims | g5, the matched 150 class comparison, the within patient switch and the per model g2/g3 corrections are exploratory or post hoc. ensure every table and the abstract carry the label where needed. |
| p value units and correction family | statistics | some p values are reported with holm correction over 5 models and over 7 tests. state the family in every legend. |
| sample sizes for each reported mean and CI | statistics | present in the tables; confirm that every figure legend carries n and the bootstrap unit. |
| figure permissions | production | no third party figure was identified; confirm. |
| reporting checklist required by the target journal | submission | not selected; confirm whether any checklist applies to a simulation study. |
| public availability of the `refs/` sources | references | excluded from the release; cite public versions or mark as unavailable. |

## 11. readiness summary

ready to paste: title, english abstract, data and code availability drafts, license scope drafts.

blocked on authors: named authors, affiliations, corresponding author, ORCID, contributions, funding, competing interests, reviewer suggestions, target journal, cover letter addressees, public repository and DOI, full english manuscript, VAK metadata.

blocked on internal consistency: event count unit, window count unit, stale within subject note in `paper/deviations.md`, table numbering, license for this file.
