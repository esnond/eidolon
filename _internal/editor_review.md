# editor review: eidolon preprint

review date: 2026-10-30
target venues: VAK journal, bioRxiv
source files read: README.md, paper/preprint.md, paper/deviations.md, results/verdicts.json, results/stats.json, results/forecast.json, results/models.json, results/manifest.txt, paper/references.bib, hypotheses.md
status: not submission ready. the scientific record is auditable and the negative results are reported; the author, ethics, data, code, and license layer is absent.

## (a) publication readiness checklist

### a1. authorship and front matter

| item | status | evidence | action |
|---|---|---|---|
| title, abstract, keywords | present | preprint.md has Russian and English abstracts, keywords in both languages | add the metadata fields required by the target journal; verify word limits |
| author names and order | missing, blocking | front matter says "author: исследовательский проект eidolon"; this is a project label, not a person | insert full names and author order |
| affiliations | missing, blocking | no department, institution, city, or country | insert one affiliation per author and map superscripts |
| ORCID iDs | missing, blocking | none | insert one ORCID iD per author |
| corresponding author | missing, blocking | none | insert name, affiliation, email, postal address |
| author contributions | missing, before posting | none | insert a CRediT statement |
| funding | missing, blocking | none | insert funder and grant number, or "no specific grant" |
| competing interests | missing, blocking | none | insert a statement for every author |
| acknowledgements | missing, low | none | insert names and roles, or state none |
| all authors approve submission | missing, blocking | none | obtain written approval and record the date |

### a2. ethics, data, code, and license

| item | status | evidence | action |
|---|---|---|---|
| ethics statement | missing, blocking | README says no real patients; preprint has no ethics section | insert the synthetic data statement in (b) and confirm it with the institution |
| consent for publication | not applicable, state it | synthetic data only | add "not applicable" to the ethics section |
| synthetic data statement | present, move | README and limitations say data are synthetic | repeat the statement in the abstract, methods, and ethics section |
| data availability | partial, blocking | data files and manifest exist; no public URL or DOI | insert the statement in (b) with repository URL and DOIs |
| code availability | partial, blocking | src/, python/, tools/, Makefile exist; no public URL or DOI | insert the statement in (b) with repository URL and DOI |
| license | missing, blocking | no LICENSE file in the repository or release archive | add the MIT and CC BY 4.0 wording in (c) |
| DOI for archives | missing, blocking | no code, data, or release DOI | mint archive DOIs or use stable repository URLs; insert the placeholders in (b) |
| DOI for this preprint | not yet assigned | the venue assigns the preprint or article DOI | insert [DOI for this preprint] after assignment |
| preprint disclosure | partial, before posting | status line says "preprint draft, not peer reviewed"; no venue or DOI | add venue, date, DOI, or state "not posted" |
| clinical trial registration | not applicable, state it | synthetic data only | add "not applicable" |
| reporting guideline | not applicable, verify | no clinical study or systematic review | state "not applicable" or follow the target journal requirement |

### a3. manuscript and reproducibility

| item | status | evidence | action |
|---|---|---|---|
| limitations | present | 12 items in section 6 | keep; do not shrink between drafts |
| negative results | present | h2, h5, h6, h7 are reported as refuted or inconclusive | keep; do not move them to supplementary material |
| statistics | partial, before posting | CI95, n, and effect sizes are present for most tests; p_holm families are ambiguous in table 7 | fix table 7 as in (d), fix 3; add the h7 binomial threshold and the observed 9/100 count |
| tables | partial, before posting | table 2 window count is ambiguous; table 7 mixes tests | fix as in (d), fixes 1 and 3 |
| figures | partial, before posting | six PNG files; first callout order is 1, 2, 3, 6, 4, 5 | fix as in (d), fix 4 |
| references | partial, blocking | no DOIs or stable URLs; one absolute local path | fix as in (d), fix 5 |
| reproducibility manifest | present | results/manifest.txt records SHA256, compiler, flags, seeds, Python environment, determinism PASS | archive the manifest with the release |
| archival release | partial, before posting | release/eidolon-v1.0.0.tar.gz, SHA256 19c105ecc532db5217f13ca5d026b2d553e0f6a995d412f1352bf6012ccc9a35; contains src/*.o and the compiled binary | mint a DOI; rebuild a clean archive without build artifacts |
| cover letter | missing, before posting | none | use the skeleton in (e) |
| suggested reviewers | missing, low | none | insert names and contacts, or state "we do not suggest reviewers" |

### a4. venue-specific checks

| item | status | evidence | action |
|---|---|---|---|
| VAK journal template | needs verification, blocking for VAK | Russian abstract is present; no UDC, Russian author metadata, or affiliation addresses | check the target journal template; add UDC, Russian title, abstract, keywords, author metadata, and affiliations |
| bioRxiv submission form | needs verification, blocking for bioRxiv | English abstract is present; no license, category, or author approval | check the current bioRxiv form; add license, category, author approval, funding, and competing interests |
| target journal preprint policy | needs verification | none | confirm that the target journal allows posting on bioRxiv |
| word count and figure limits | needs verification | six figures and seven tables | check the target journal limits and move excess material to supplementary files |
| supplementary file index | partial | results/README.md describes artifacts | add a submission-ready index with file names, formats, and sizes |
| duplicate submission check | missing, blocking | none | confirm that the manuscript is not under consideration elsewhere |

## (b) missing metadata

the preprint front matter, README, and release archive do not contain the fields below. insert placeholders before submission; do not invent values.

| field | current state | placeholder or wording to insert |
|---|---|---|
| author list | project label only | [author 1 full name], [author 2 full name], [author 3 full name] |
| affiliations | absent | [department, institution, city, country]; [department, institution, city, country] |
| ORCID iDs | absent | [ORCID iD, author 1]; [ORCID iD, author 2] |
| corresponding author | absent | [full name], [affiliation], [email], [postal address] |
| English title | absent; the front matter has a Russian title only | [English title] |
| DOI for this preprint | absent; the venue assigns it | [DOI for this preprint], insert after assignment |
| DOI for code | absent | [DOI for the code archive] |
| DOI for synthetic data | absent | [DOI for the synthetic data archive] |
| DOI for release archive | absent | [DOI for the release archive] |
| repository URL | absent; the front matter uses the local path /home/esnond/echo | [repository URL] |
| commit or version | version 1.0.0 exists; no commit SHA | [commit SHA] |
| ethics statement | absent | see the wording below |
| data availability statement | absent as a formal statement | see the wording below |
| code availability statement | absent as a formal statement | see the wording below |
| funding statement | absent | [funder, grant number] or [this research received no specific grant] |
| competing interests | absent | [the authors declare no competing interests] or [describe] |
| author contributions | absent | [initials]: conceptualization, methodology, software, formal analysis, writing (original draft), writing (review and editing), visualization. [initials]: [roles]. |
| acknowledgements | absent | [names, roles, institutions] or [none] |
| preprint venue and date | partial | [venue, date, DOI] or [not posted] |
| VAK metadata | partial; Russian title, abstract, and keywords are present; UDC, Russian author metadata, and affiliation addresses are absent | [UDC], [Russian author metadata], [Russian affiliation addresses] |
| bioRxiv category | absent | [bioRxiv category] |

### ethics statement, proposed wording

this study used only synthetic data generated by the deterministic C99 program eidolon_gen (version 1.0.0). no human participants, human tissue, or identifiable patient data were involved. in the authors' assessment, institutional review board approval was not required. [confirm with [institution] and insert the exact statement required by [journal].]

### data availability statement, proposed wording

the synthetic cohort, derived features, model outputs, and reproducibility manifest are available at [repository URL] and archived at [DOI for the synthetic data archive]. the release archive is release/eidolon-v1.0.0.tar.gz, SHA256 19c105ecc532db5217f13ca5d026b2d553e0f6a995d412f1352bf6012ccc9a35. the primary cohort is data/cohort.csv, SHA256 7841bd667c35ee437eea9d1c58016990c081ed022d8f042389fb356b487ce1a9. the chaos cohort is data/chaos.csv, SHA256 86be22873cf47b2859a2b7a643cac0533759f809d1c1a93cfd6f09f4d49dbea0. the replication cohort is data/seed2/cohort.csv, SHA256 a925cfd8e142765011a70d136726f90177fdcbcb8bf03d26fa7c739eac98256b. no real patient data are included.

### code availability statement, proposed wording

the generator and analysis code are available at [repository URL] and archived at [DOI for the code archive] under the MIT license. version 1.0.0. results/manifest.txt records compiler cc (Debian 14.2.0-19) 14.2.0, flags -std=c99 -pedantic -Wall -Wextra -Werror -O2 -ffp-contract=off, python 3.13.5, numpy 2.5.4, pandas 3.1.0, scikit-learn 1.9.1, scipy 1.18.1, and matplotlib 3.11.2. determinism check: pass; generator replay 2 s.

### metadata notes

- the current front matter field "repo: /home/esnond/echo" is a local absolute path. replace it with [repository URL].
- the current front matter field "author: исследовательский проект eidolon" is not a person. replace it with the author list.
- add the same metadata to the release archive, not only to the preprint.
- keep ORCID, affiliation, and corresponding author fields identical in the manuscript, repository, and submission system.

## (c) proposed license wording

### scope statement

use a split license. do not apply CC BY 4.0 to code and do not apply MIT to manuscript text.

- `src/`, `python/`, `tools/`, and `Makefile`: MIT.
- `paper/`, `results/` text, tables, figures, and JSON: CC BY 4.0.
- `data/` synthetic CSV files: CC BY 4.0.
- `refs/`: excluded. third-party documents retain their original terms. verify redistribution rights before public release.
- `release/` archive: distribute under the same split and include the LICENSE and NOTICE files.

### MIT license text for code

the standard legal text follows. keep its capitalization; do not apply the lowercase house style to a license.

```
MIT License

Copyright (c) 2026 [copyright holder]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### CC BY 4.0 wording for the paper

copyright (c) 2026 [copyright holder]. this preprint is licensed under a creative commons attribution 4.0 international license (CC BY 4.0). to view a copy of this license, visit https://creativecommons.org/licenses/by/4.0/. you are free to share and adapt the material for any purpose, even commercially, provided that you give appropriate credit, provide a link to the license, and indicate if changes were made. attribution: [author list], [title], [version], [DOI for this preprint].

### CC BY 4.0 wording for synthetic data

copyright (c) 2026 [copyright holder]. the synthetic cohort and derived data are licensed under CC BY 4.0. attribution: [author list], eidolon synthetic cohort, version 1.0.0, [DOI for the synthetic data archive]. no real patient data are included. the license does not apply to third-party documents in `refs/`.

### repository notice

except where otherwise noted, code in `src/`, `python/`, `tools/`, and the `Makefile` is licensed under the MIT license; text, tables, figures, and synthetic data in `paper/`, `results/`, and `data/` are licensed under CC BY 4.0. third-party documents in `refs/` are excluded and retain their original terms. the release archive follows the same split. add a LICENSE file and a NOTICE file with this scope statement.

### license notes

- confirm the license choice with all authors, the institution, and the funder before posting.
- check the target journal policy; some journals require CC BY 4.0, some allow it, and some do not.
- do not relicense third-party material in `refs/` without written permission.
- the release archive currently contains `src/*.o` and the compiled `eidolon_gen` binary. rebuild a clean archive from source and exclude build artifacts before minting a DOI.

## (d) five concrete consistency and style fixes

### fix 1: define the window count in table 2 and correct table 1 row 17

location: paper/preprint.md section 4.1 table 2; methods 3.1; limitations item 4; results/stats.json cohort block.

observed: table 2 lists 800, 600, 600, 400 windows. methods 3.1 say 9 windows per patient. limitations item 4 says 1000, 750, 750, 500 training windows. the table counts test windows 6-9 only: 200 x 4 = 800, 150 x 4 = 600, 100 x 4 = 400. stats.json reports 5400 total windows, with 1800, 1350, 1350, 900 per group.

fix: rename the table 2 column to "test windows (6-9)" and add a note: "training windows (1-5): 1000, 750, 750, 500; total windows: 5400." keep the numbers; they are correct for test windows. in table 1, row 17 describes `circadian_amp` as "амплитуда недельного времени"; change it to "амплитуда циркадной модуляции времени".

### fix 2: distinguish paired means from group means in the chaos forecast

location: paper/preprint.md section 4.7 and table 5; abstract; results/stats.json h5; results/forecast.json chaos.

observed: the text reports chaos events accuracy 0.496 [0.472, 0.505] for days 31-60 and 0.481 [0.448, 0.488] for days 61-90, then reports a difference of 0.0204 [-0.0049, 0.0446], p=0.172. the difference of the displayed means is 0.015, not 0.0204. stats.json h5 gives paired means 0.4891 and 0.4687, difference 0.0204. forecast.json gives group means 0.4959 and 0.4808.

fix: add one sentence: "the difference is the mean of per-patient paired differences (n=100 patients, 3000 windows per horizon), not the difference of the two displayed group means; the paired means are 0.4891 and 0.4687." alternatively, replace the displayed means with the paired means and label them. keep the CI95 and p value.

### fix 3: make table 7 self-contained for tests, effect direction, and correction families

location: paper/preprint.md table 7, section 4.3, section 4.10; results/stats.json; results/verdicts.json.

observed: table 7 mixes test statistics and correction families. examples: h1 reports p_holm 9.5e-94, which is 7 x the kruskal-wallis p 1.36e-94, while the pairwise g1 vs g3 mann-whitney p_holm is 3.14e-57. h2 reports 1.000 in table 7 but 0.870 in section 4.3; stats.json gives 0.8695 for the pairwise g2 vs g3 test. h4 reports 0.00041 in table 7 but 0.00033 in verdicts.json; stats.json gives 0.000325 for the within-g1 family. these are different families, not necessarily errors, but the table does not say so. the sentence in section 4.3 reports rho=0.275 for idu_nat and 0.387 for idu_cohort, then a single p=1.5e-8; that p belongs to idu_cohort, while idu_nat has p_holm 0.00033 within family or 0.00041 global.

fix: add columns `test`, `comparison`, `p_raw`, `p_holm within family`, and `p_holm global 7`; define each family in a footnote. state the direction of cohen d, for example d(g3 - g1) = -13.16. split the section 4.3 sentence into separate p values for idu_nat and idu_cohort. do not place a kruskal-wallis p and a pairwise mann-whitney p in the same column.

### fix 4: renumber figures in order of first citation

location: paper/preprint.md sections 4.2, 4.3, 4.4, 4.7, 4.8; results/figures/.

observed: the first callout order is figure 1, figure 2, figure 3, figure 6, figure 4, figure 5. figure 6 (anomaly ROC) is cited in section 4.4, before figure 4 (forecast) and figure 5 (importance) in sections 4.7 and 4.8.

fix: renumber anomaly ROC as figure 4, forecast as figure 5, and importance as figure 6. update callouts, captions, file names, and results/manifest.txt hashes after renaming. if renaming files is too costly for this draft, move the anomaly ROC callout after figure 5 and state the numbering rationale in the caption list.

### fix 5: replace local paths and incomplete references with persistent identifiers

location: paper/preprint.md "источники" entry `proteus (2026)`; paper/references.bib `@misc{proteus2026final}`; front matter `repo: /home/esnond/echo`; `shumailov et al., 2023`.

observed: the `proteus` entry contains the absolute local path `/home/esnond/proteus/paper/FINAL.md`. this is not a persistent identifier and will not resolve for readers. `shumailov et al., 2023` has no arXiv identifier. most entries have no DOI or stable URL.

fix: replace the local path with "unpublished internal report" or a public preprint DOI or URL. add the exact arXiv identifier for shumailov 2023 from the source. add DOIs or stable URLs for the other references. mark missing identifiers as `[identifier needed]`. if the internal report cannot be made public, remove it or move it to a clearly labeled unpublished note. replace the front matter `repo: /home/esnond/echo` with `[repository URL]`.

## (e) cover letter skeleton

```
[date]

[editor name]
[editorial office]
[journal name]
[address]

dear [editor name],

we submit [manuscript title] for consideration as a [research article or preprint] in [journal name].

the manuscript asks whether intense behavioral masking produces a profile that is both anomalous and unique. using a deterministic C99 generator, 600 synthetic patients, 90 days, 24 latent parameters, 1,991,067 events, 51 features, and five closed-set models, we find that intense masking increases distance to the natural manifold (idu_nat 17.096 vs 3.825 for natural behavior) but reduces within-cohort uniqueness (idu_cohort 0.065 vs 3.858; 58 distinct feature vectors over 600 test windows). the preregistered rank-1 criterion is refuted (participation ratio 2.380, lambda1 share 0.500). we report the negative results for the strict identifiability order and for next-day forecast skill.

the study uses only synthetic data. no human participants or identifiable patient data were involved. code will be released under the MIT license; the paper and synthetic data will be released under CC BY 4.0. update this sentence to the present tense after the LICENSE files are in place. the release includes a reproducibility manifest with SHA256 hashes, compiler flags, seeds 20261030 and 20261031, and a bitwise determinism check.

the manuscript is not under consideration elsewhere [confirm]. all authors have approved the submission [confirm]. we declare no competing interests [confirm]. funding: [funding statement]. data and code: [repository URL], [DOI for the code archive], [DOI for the synthetic data archive]. ethics: [statement from section b].

suggested reviewers: [name, affiliation, email], [name, affiliation, email], or "we do not suggest reviewers".

sincerely,
[corresponding author name]
[affiliation]
[email]
[ORCID iD]
```

for a VAK journal, prepare a Russian version of this skeleton and keep the same facts and placeholders. for bioRxiv, use the English version and add the bioRxiv category.

## order of operations

1. freeze the author list, affiliations, ORCID iDs, and corresponding author.
2. insert the ethics, data, code, funding, competing interests, and license statements.
3. apply fixes 1 to 5 in (d) and regenerate the tables and manifest.
4. rebuild a clean release archive without `src/*.o` and the compiled binary, then mint DOIs.
5. obtain all-author approval, post to bioRxiv or submit to the VAK journal, and record the date and DOI.
