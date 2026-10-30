# related work map: eidolon

status: verified core set, 20 references, 3 claimable gaps.
date: 2026-10-30.
scope: de-anonymization, behavioral biometrics, k-anonymity and differential privacy, synthetic data validity, anomaly detection, reproducibility.
sources read: `paper/preprint.md` section 2 and section 5.5, `paper/references.bib`, all `.txt` files in `refs/`, crossref and openalex records for the 20 DOIs, web search for the eckersley2010 and chen2021 abstracts.
verification rule: a DOI appears in this file only after a resolver returned metadata that match the listed authors, year, title and venue. crossref endpoint: `https://api.crossref.org/works/<DOI>`. openalex endpoint: `https://api.openalex.org/works/https://doi.org/<DOI>`. query date: 2026-10-30. no DOI is inferred from a title, a bib entry or a search snippet.
scope limit: the 20 items are a core map, not a systematic review. absence statements below are limited to this set and to the `refs/` documents read for this note. publication status: `shumailov2023` is an arXiv preprint; `chen2021` is a comment article; the remaining 18 are journal or conference publications.

## 0. summary table

| id | cluster | authors | year | title | venue | DOI | resolver |
|---|---|---|---|---|---|---|---|
| `narayanan2008` | de-anonymization | arvind narayanan; vitaly shmatikov | 2008 | robust de-anonymization of large sparse datasets | IEEE symposium on security and privacy (S&P), pp. 111-125 | 10.1109/SP.2008.33 | crossref |
| `de_montjoye2013` | de-anonymization | yves-alexandre de montjoye; césar a. hidalgo; michel verleysen; vincent d. blondel | 2013 | unique in the crowd: the privacy bounds of human mobility | scientific reports 3: 1376 | 10.1038/srep01376 | crossref |
| `rocher2019` | de-anonymization | luc rocher; julien m. hendrickx; yves-alexandre de montjoye | 2019 | estimating the success of re-identifications in incomplete datasets using generative models | nature communications 10: 3069 | 10.1038/s41467-019-10933-3 | crossref |
| `benitez2010` | health re-identification | kathleen benitez; bradley malin | 2010 | evaluating re-identification risks with respect to the HIPAA privacy rule | journal of the american medical informatics association 17(2): 169-177 | 10.1136/jamia.2009.000026 | crossref |
| `sweeney2002` | k-anonymity | latanya sweeney | 2002 | k-anonymity: a model for protecting privacy | international journal of uncertainty, fuzziness and knowledge-based systems 10(5): 557-570 | 10.1142/S0218488502001648 | crossref |
| `machanavajjhala2007` | k-anonymity | ashwin machanavajjhala; daniel kifer; johannes gehrke; muthuramakrishnan venkitasubramaniam | 2007 | l-diversity: privacy beyond k-anonymity | ACM transactions on knowledge discovery from data 1(1): 3 | 10.1145/1217299.1217302 | crossref |
| `dwork2006` | differential privacy | cynthia dwork | 2006 | differential privacy | international colloquium on automata, languages and programming (ICALP), pp. 1-12 | 10.1007/11787006_1 | crossref |
| `monrose1997` | behavioral biometrics | fabian monrose; aviel d. rubin | 1997 | authentication via keystroke dynamics | ACM conference on computer and communications security (CCS), pp. 48-56 | 10.1145/266420.266434 | crossref |
| `killourhy2009` | behavioral biometrics | kevin s. killourhy; roy a. maxion | 2009 | comparing anomaly-detection algorithms for keystroke dynamics | IEEE/IFIP international conference on dependable systems and networks (DSN), pp. 125-134 | 10.1109/DSN.2009.5270346 | crossref |
| `frank2013` | behavioral biometrics | mario frank; ralf biedert; eugene ma; ivan martinovic; dawn song | 2013 | touchalytics: on the applicability of touchscreen input as a behavioral biometric for continuous authentication | IEEE transactions on information forensics and security 8(1): 136-148 | 10.1109/TIFS.2012.2225048 | crossref |
| `eckersley2010` | behavioral biometrics | peter eckersley | 2010 | how unique is your web browser? | privacy enhancing technologies symposium (PETS), pp. 1-18 | 10.1007/978-3-642-14527-8_1 | crossref |
| `goncalves2020` | synthetic data | andre goncalves; priyadip ray; braden soper; jennifer stevens; linda coyle; ana paula sales | 2020 | generation and evaluation of synthetic patient data | BMC medical research methodology 20: 108 | 10.1186/s12874-020-00977-1 | crossref |
| `chen2021` | synthetic data | richard j. chen; ming y. lu; tiffany y. chen; drew f. k. williamson; faisal mahmood | 2021 | synthetic data in machine learning for medicine and healthcare | nature biomedical engineering 5(6): 493-497 | 10.1038/s41551-021-00751-8 | crossref |
| `shumailov2023` | synthetic data | ilia shumailov; zakhar shumaylov; yiren zhao; yarin gal; nicolas papernot; ross anderson | 2023 | the curse of recursion: training on generated data makes models forget | arXiv preprint arXiv:2305.17493 | 10.48550/arXiv.2305.17493 | openalex |
| `liu2008` | anomaly detection | fei tony liu; kai ming ting; zhi-hua zhou | 2008 | isolation forest | IEEE international conference on data mining (ICDM), pp. 413-422 | 10.1109/ICDM.2008.17 | crossref |
| `chandola2009` | anomaly detection | varun chandola; arindam banerjee; vipin kumar | 2009 | anomaly detection: a survey | ACM computing surveys 41(3): 1-58 | 10.1145/1541880.1541882 | crossref |
| `ruff2021` | anomaly detection | lukas ruff; jacob r. kauffmann; robert a. vandermeulen; gregoire montavon; wojciech samek; marius kloft; thomas g. dietterich; klaus-robert muller | 2021 | a unifying review of deep and shallow anomaly detection | proceedings of the IEEE 109(5): 756-795 | 10.1109/JPROC.2021.3052449 | crossref |
| `peng2011` | reproducibility | roger d. peng | 2011 | reproducible research in computational science | science 334(6060): 1226-1227 | 10.1126/science.1213847 | crossref |
| `sandve2013` | reproducibility | geir kjetil sandve; anton nekrutenko; james taylor; eivind hovig | 2013 | ten simple rules for reproducible computational research | PLoS computational biology 9(10): e1003285 | 10.1371/journal.pcbi.1003285 | crossref |
| `munafo2017` | reproducibility | marcus r. munafò; brian a. nosek; dorothy v. m. bishop; katherine s. button; christopher d. chambers; nathalie percie du sert; uri simonsohn; eric-jan wagenmakers; jennifer j. ware; john p. a. ioannidis | 2017 | a manifesto for reproducible science | nature human behaviour 1: 0021 | 10.1038/s41562-016-0021 | crossref |

## 1. de-anonymization and health re-identification

- `narayanan2008`: statistical de-anonymization of high-dimensional micro-data; netflix prize dataset with 500,000 subscribers; IMDb used as background knowledge; attacks robust to perturbation and incomplete background knowledge. use: supports the premise that removing names does not remove identity in sparse activity records. limit: no subject-side masking, no health logs, no separation of anomaly from uniqueness.
- `de_montjoye2013`: 15 months of mobility data, 1.5 million individuals; four spatio-temporal points identify 95% of individuals; uniqueness decays approximately as the 1/10 power of resolution. use: direct warrant for measuring uniqueness inside a cohort; motivates `idu_cohort`. limit: mobility traces, not EHR navigation; sampling and resolution are curator-side controls; no behavioral masking.
- `rocher2019`: generative copula model; 210 populations; AUC 0.84-0.97 for individual uniqueness; 99.98% of americans re-identified with 15 demographic attributes. use: shows that incomplete or sampled data remain re-identifiable; supports the rejection of sampling as anonymity. limit: demographic attributes, not action sequences; no masking; no health logs.
- `benitez2010`: HIPAA safe harbor and limited dataset policies; voter registration attack; risk metrics include expected number of re-identifications, proportion in a group of size g or less, and monetary cost per re-identification. use: health-specific de-identification risk; supports the medical motivation. limit: policy-level analysis, not behavioral biometrics; no synthetic cohort; no anomaly score.

## 2. k-anonymity and differential privacy

- `sweeney2002`: formal k-anonymity; each record is indistinguishable from at least k-1 other records; re-identification attacks on releases that adhere to k-anonymity unless accompanying policies are applied. use: baseline curator-side model; defines the k parameter that the paper's section 5.5 invokes. limit: no subject-side behavior change; l-diversity later shows that k-anonymity alone is insufficient.
- `machanavajjhala2007`: two attacks on k-anonymity, low diversity of sensitive attributes and adversary background knowledge; proposes l-diversity. use: shows that k-anonymity is not a sufficient privacy criterion; supports the paper's move to a different threat model rather than a larger k. limit: still a curator-side release model; no behavioral masking.
- `dwork2006`: formal differential privacy; limits the influence of one record on the output of a query or release mechanism. use: defines the formal guarantee; clarifies that differential privacy is a property of the release mechanism, not of the data subject's behavior. limit: no model of deliberate behavior change before data collection; no utility analysis for behavioral features.

## 3. behavioral biometrics and device fingerprinting

- `monrose1997`: keystroke dynamics; 42 profiles; structured and unstructured typing tasks. use: early evidence that typing rhythm is an identity signal. limit: authentication with an enrollment phase, not de-anonymization of health logs; no masking.
- `killourhy2009`: 51 subjects, 400 passwords each, 14 detectors; repeatable evaluation procedure for keystroke dynamics. use: benchmark discipline and anomaly-detection framing for behavioral biometrics. limit: authentication, not closed-set re-identification across 100 to 200 classes; no synthetic data.
- `frank2013`: 30 behavioral touch features; median equal error rate 0% for intrasession authentication and 2-3% for intersession authentication. use: modern behavioral biometrics; supports the high identifiability of interaction traces. limit: smartphone touch, not EHR navigation; no masking; no anomaly and uniqueness split.
- `eckersley2010`: browser fingerprints; at least 18.1 bits of entropy; 94.2% of browsers with flash or java were unique in the sample; fingerprints change over time. use: device and configuration fingerprint uniqueness; supports the general uniqueness premise. limit: configuration and device attributes, not action sequences; no masking; no health context.

## 4. synthetic data validity

- `goncalves2020`: three classes of synthetic patient data generation, probabilistic models, classification-based imputation and GANs; quality metrics for generated records. use: synthetic patient data require utility and privacy evaluation; supports the generator validation requirement. limit: evaluates generated records, not bitwise replay; no behavioral re-identification.
- `chen2021`: comment on synthetic data in medicine and healthcare; opportunities and concerns about vulnerabilities and policy. use: synthetic data are not automatically valid or private; supports the caution in the preprint. limit: perspective, no experiment; no behavioral cohort.
- `shumailov2023`: model collapse; tails of the original distribution disappear when models are trained on generated data; demonstrated in VAE, GMM and LLM settings. use: synthetic data can lose distribution tails; supports the separation of generator artifacts from behavioral claims. limit: generative model training, not synthetic cohort design; no re-identification.

## 5. anomaly detection

- `liu2008`: isolation forest; isolates anomalies instead of profiling normal points; linear time complexity, low memory requirement and sub-sampling. use: the paper's anomaly score uses isolation forest trained on natural windows only; this is the method reference. limit: unsupervised anomaly detection, not identity; no uniqueness metric.
- `chandola2009`: survey and taxonomy of anomaly detection; key assumptions of each technique. use: anomaly detection is assumption-dependent; supports the caution that AUC 1.000 can be a regularity artifact. limit: general survey; no behavioral masking.
- `ruff2021`: unifying review of deep and shallow anomaly detection; common principles and implicit assumptions. use: modern context; supports the distinction between anomaly score and identity. limit: review; no re-identification.

## 6. reproducibility

- `peng2011`: reproducibility as a minimum standard when full independent replication is not possible. use: supports the manifest and replay claims. limit: general; no specific protocol for synthetic cohorts.
- `sandve2013`: ten rules for reproducible computational research, including provenance tracking, scripted analysis, version control, seed recording and public access to scripts and results. use: maps to the makefile, manifest, seeds and tests. limit: general; no behavioral benchmark.
- `munafo2017`: measures across methods, reporting and dissemination, reproducibility, evaluation and incentives. use: supports preregistration and negative-result reporting. limit: general; no synthetic data.

## 7. insertion map for preprint section 2

| location | current citations | add from this map | reason |
|---|---|---|---|
| section 2, paragraph 1, re-identification | `narayanan2008`, `eckersley2010`, `monrose1997`, `kohno2005` | `de_montjoye2013`, `rocher2019`, `benitez2010` | behavioral uniqueness, incomplete-data risk, health context |
| section 2, new behavioral biometrics paragraph | `monrose1997`, `eckersley2010` | `killourhy2009`, `frank2013` | repeatable evaluation and modern touch biometrics |
| section 2, paragraph 2, privacy models | `sweeney2002`, `dwork2006` | `machanavajjhala2007` | k-anonymity has known attacks; do not present it as sufficient |
| section 2, paragraph 3, fractal behavior and anomaly | `shannon1948`, `mandelbrot1982`, `taleb2007`, `proteus2026` | `liu2008`, `chandola2009`, `ruff2021` | anomaly detection is a technical literature, not a metaphor |
| section 2, paragraph 4, synthetic data | `shumailov2023` | `goncalves2020`, `chen2021` | generator validation and medical synthetic data |
| section 2, new reproducibility paragraph | none | `peng2011`, `sandve2013`, `munafo2017` | artifact, manifest and negative-result reporting |
| section 5.5, privacy consequences | `sweeney2002`, `dwork2006` | none | replace consistent with orthogonal or complementary; the paper tests a different threat model |

## 8. three claimable gaps

### g1. subject-side masking is not a curator-side privacy model

gap: k-anonymity is a property of a released table [`sweeney2002`]; differential privacy is a property of a randomized query or release mechanism [`dwork2006`]. both assume a data holder that transforms or restricts data before release. the behavioral biometrics set measures identification from passive traces [`monrose1997`; `killourhy2009`; `frank2013`; `eckersley2010`]. within the 20-item verified set, no study manipulates the generative process of the data subject before the record is created and then measures re-identification under that manipulation.

paper evidence: g3 deterministic mask gives `idu_nat` 17.096 against g1 3.825, while `idu_cohort` falls to 0.065 against 3.858; g5 with the same 24 affine parameters but a stochastic emitter gives 600 of 600 unique profiles and RF top1 0.100; the within-subject switch gives drift 18.372 for g6 against 2.238 for the natural control. source: `paper/preprint.md` tables 2 and 9; `results/verdicts.json`.

claim: the paper can claim a controlled synthetic test of subject-side behavioral masking, a regime not modeled by curator-side k-anonymity and differential privacy.

do not claim: that k-anonymity or differential privacy are ineffective in general; that the result transfers to real patients; that subject-side masking is a privacy guarantee.

### g2. anomaly and uniqueness are separate endpoints

gap: anomaly detection evaluates scores, ranks or AUC [`liu2008`; `chandola2009`; `ruff2021`]; re-identification evaluates uniqueness, top1 or risk [`narayanan2008`; `de_montjoye2013`; `rocher2019`]. within the verified set, no study reports both endpoints on the same behavioral profiles under a masking manipulation.

paper evidence: g3 reaches anomaly AUC 1.000 against g1, but only 58 unique feature vectors after rounding to six decimals over 600 test windows, `idu_cohort` 0.065, and RF top1 0.387, equal to the exact-template ceiling 58/150 = 0.3867. g5 reaches anomaly AUC 0.629, `idu_cohort` 3.407, 600 of 600 unique profiles and RF top1 0.100. the dissociation is the central result. source: `paper/preprint.md` sections 4.4 and 4.11; `results/robustness.json`.

claim: the paper can claim that anomaly and uniqueness dissociate under deterministic masking: a profile can be maximally anomalous in the reported AUC comparison and the least unique among the reported groups.

do not claim: that AUC 1.000 is a complex signature; the paper's own robustness check shows that ten single features reach AUC 1.000. do not claim that anomaly detection is useless; it detects the mask, not the person.

### g3. synthetic behavioral benchmarks lack bitwise replay and negative-result reporting

gap: synthetic health data work evaluates utility and privacy of generated records [`goncalves2020`; `chen2021`]; model collapse shows that training on generated data can remove distribution tails [`shumailov2023`]; reproducibility work specifies rules and manifest practices [`peng2011`; `sandve2013`; `munafo2017`]. within the verified set, no behavioral re-identification benchmark combines a frozen CSV contract, a deterministic generator, a replay manifest and reported refutations.

paper evidence: C99 generator, 1,991,067 events, 600 patients, 90 days; SHA256 7841bd667c35ee437eea9d1c58016990c081ed022d8f042389fb356b487ce1a9; two seeds; 7 python tests; manifest with 105 hashes; h2, h5, h6 and h7 reported as refuted or inconclusive; g5 and within-subject analyses labeled exploratory. source: `results/manifest.txt`; `paper/blue_team_report.md`; `tests/run_tests.sh`.

claim: the paper can claim a bitwise-replayable synthetic behavioral cohort with preregistered hypotheses and explicit negative results.

do not claim: that the generator is biologically realistic; that the negative results generalize beyond the 24-parameter markov construction; that reproducibility alone establishes validity.

## 9. editorial notes on the current preprint

1. section 2 correctly says that k-anonymity and differential privacy assume protection by data organization, not by user action. section 5.5 then says the result is consistent with both frameworks. this is imprecise: the paper tests a different threat model. use orthogonal or complementary, not consistent, unless a formal mapping is added.
2. section 2 uses taleb 2007 as a warrant for anomaly detection. taleb is a conceptual book, not a detector. cite `liu2008`, `chandola2009` and `ruff2021` for the technical claim; keep taleb only as a metaphor if the venue permits.
3. section 2 uses shannon 1948 for the claim that structuring data reduces entropy and makes profiles detectable. shannon 1948 defines entropy and source coding; it does not establish detectability. mark the inferential step as the paper's own or remove the citation.
4. `paper/references.bib` has no DOIs and lowercase author fields. it is not a verified source. use the 20-item table in this file for submission metadata.
5. `proteus2026` is an internal report with a local path and no public DOI. it cannot be verified externally and should not be a related-work citation in a submission. replace it with a public reference or remove the claim.
6. the current section 2 has four paragraphs and covers model collapse but not anomaly detection as a technical literature, synthetic data validity evaluation or reproducibility. add the three clusters from this map; otherwise the artifact contribution has no literature anchor.

## 10. verification log and exclusions

- of the 20 core entries, 19 DOIs resolved through crossref on 2026-10-30. `shumailov2023` resolved through openalex because the arXiv DOI is not indexed by crossref. all metadata were compared against the resolver record, not against the preprint or `paper/references.bib`.
- no DOI in this file is inferred. if a resolver returned a different title or author set, the entry was dropped. no dropped entry is listed with a DOI.
- `kohno2005` is already cited in preprint section 2. full verified metadata: t. kohno; a. broido; k.c. claffy, 2005, remote physical device fingerprinting, IEEE transactions on dependable and secure computing 2(2): 93-108, DOI 10.1109/TDSC.2005.26, crossref. it is not counted in the 20-item core because the core prioritizes behavioral and synthetic clusters.
- shannon 1948, mandelbrot 1982 and taleb 2007 are conceptual or historical sources in the current preprint. they are outside the six clusters and are not counted. no DOI is asserted for them here.
- additional `refs/` items are not imported: backes et al. 2012, no complete citation in `refs/` and no match in an openalex title search in this pass; donoho 2000, no complete citation in `refs/`; varian 2004, kerr 2001, heisenberg 1927, pentland 2014 and prokopenko 2014, outside the six clusters or no DOI asserted. no claim is made about their existence or quality.
- the preprint's `paper/references.bib` contains 11 entries. six are in the 20-item core: `narayanan2008`, `dwork2006`, `sweeney2002`, `eckersley2010`, `monrose1997` and `shumailov2023`. `kohno2005` is verified and retained in the preprint. shannon 1948, mandelbrot 1982, taleb 2007 and `proteus2026` are outside the core for the reasons above.

## дополнение 2026-10-30: ивановская школа, поведение пациентов в информационной среде

- угланова н.н., мушников д.л., костин в.в., кизеев м.в., стволыгин а.в., наумов а.в. (2010). информационная культура пациентов и пути ее повышения. вестник рудн, серия медицина, № 4. 982 пациента в иваново, пять компонентов информационной культуры (этико-правовой, профилактический, ургентный, социальный, культура использования источников), связь с результативностью помощи. источник: journals.rudn.ru/medicine/article/view/2800, также cyberleninka.
- угланова н.н., мушников д.л., поляков б.а. (2020). информированность студентов медицинского вуза по вопросам профилактики новой коронавирусной инфекции. вестник ивгма, т. 25, № 3-4. 350 студентов, 78% узнали из соцсетей. источник: vestnik-ivgma.ru/issues/71/publications/1261.
- мушников д.л., поляков б.а., куканова н.н., краснова с.а., угланова н.н., сибирева и.и. (2009). медико-организационные технологии работы с пациентами. вестник рудн, серия медицина, № 3, начало с. 73. источник: journals.rudn.ru/medicine/article/view/2433.

позиции для цитирования: введение (поведение пациента в информационной среде), обсуждение 5.5 (цифровая гигиена через организационные механизмы). не цитировать в методах и результатах. точные страницы 2010 и конечная страница 2009 требуют уточнения по pdf.
