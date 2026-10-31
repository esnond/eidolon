# аномальность без уникальности: детерминированная маскировка в синтетической когорте

project: eidolon
version: 1.3.0
date: 2026-10-31
status: submission draft after methodologist and adversary passes. `paper/preprint.md` remains the full record.

## аннотация

проверялась гипотеза, что интенсивная маскировка цифрового поведения создаёт плоский аномальный профиль, который одновременно уникален и потому легче идентифицируется. построен детерминированный генератор на c99. основная когорта: 600 виртуальных пациентов, 90 дней, 24 скрытых параметра, 1 991 067 событий. четыре основные группы: естественное поведение (n=200), умеренная маскировка (n=150), интенсивная детерминированная маскировка (n=150), ежедневно перерандомизированный контроль (n=100). дополнительные exploratory группы: стохастическая интенсивная g5 (n=150) и within-subject g6/g7 (по 200 пациентов, естественные дни 1-45, маскированные 46-90).

результат смешанный. расстояние до естественного многообразия растёт: 3.825, 5.084, 17.096 и 3.449 для g1..g4. уникальность внутри когорты падает: 3.858, 2.900, 0.065 и 3.009. детерминированная маска сжимает 150 пациентов в 58 профилей, доля уникальных 0.0967, потолок точного шаблона 0.3867; random forest и hist gradient boosting дают ровно 0.3867. стохастическая маска g5 с теми же аффинными параметрами даёт 600 из 600 уникальных профилей и top1 0.100 [0.075, 0.130]. within-subject переключение ломает перенос: natural control 0.751 [0.711, 0.789], детерминированная маска 0.005 [0.000, 0.015], стохастическая 0.004 [0.000, 0.009] при chance 0.005; drift 2.238, 18.372 и 3.989. внутри маскированной области детерминированная маска оставляет 17x chance через 17 шаблонов, стохастическая 1-4x chance из за концентрации маскированных параметров.

rank-1 опровергнут на g3: participation ratio 2.380, доля первой компоненты 0.500. сильная формулировка парадокса не подтверждена. подтверждены: аномальность детерминированной маски, падение переноса идентичности и остаточная идентифицируемость, ограниченная шаблоном или концентрацией масок, а не уникальной подписью.

## abstract (english)

we tested whether intense masking of digital behavior creates a flat anomalous profile that is simultaneously unique and therefore easier to identify. a deterministic c99 generator produced 600 synthetic patients over 90 days with 24 latent parameters and 1,991,067 events in four main groups plus exploratory stochastic and within-subject groups. distance to the natural manifold rose from 3.825 to 5.084 to 17.096, while within-cohort uniqueness fell from 3.858 to 2.900 to 0.065. deterministic masking collapsed 150 patients into 58 profiles; the exact-profile ceiling was 0.3867 and random forest and hist gradient boosting reached it exactly. a stochastic mask with the same affine parameters produced 600 of 600 unique profiles and top1 0.100 [0.075, 0.130]. a within-subject switch broke pre-to-post transfer: natural control 0.751 [0.711, 0.789], deterministic mask 0.005 [0.000, 0.015], stochastic mask 0.004 [0.000, 0.009] at chance 0.005. the preregistered rank-1 criterion was refuted (participation ratio 2.380, first-component share 0.500). the strong paradox is not supported; the data support anomaly without uniqueness, transfer failure, and residual identification bounded by templates or mask concentration.

## 1. методы

### 1.1 дизайн

основная когорта: 600 пациентов, 90 дней, окна по 10 дней. обучение на окнах 1-5, тест на окнах 6-9. exploratory g5: 150 пациентов с теми же аффинными интенсивными параметрами, что у g3, но с натуральным стохастическим эмиттером. within-subject: 200 natural control, 200 g6, 200 g7; у g6 и g7 дни 1-45 естественные, дни 46-90 маскированные; обучение на окнах 1-4, тест на 6-9, окно 5 исключено.

**таблица 1. группы.**

| группа | n | режим |
|---|---|---|
| g1 | 200 | естественное поведение |
| g2 | 150 | умеренная маскировка |
| g3 | 150 | детерминированная интенсивная маскировка |
| g4 | 100 | ежедневная перерандомизация натуральных параметров |
| g5 | 150 | интенсивные аффинные параметры, натуральный эмиттер, exploratory |
| g6 | 200 | natural до дня 45, затем детерминированная маска, exploratory |
| g7 | 200 | natural до дня 45, затем стохастическая маска, exploratory |

**таблица 2. статус анализов.**

| семейство | анализы | статус |
|---|---|---|
| confirmatory | h1..h7, primary seed 20261030 | пререгистрированы в hypotheses.md |
| exploratory | g5, matched 150, within g6/g7, post-only и pre-only, open-set, detectability, effective classes | добавлены после основного анализа, не меняют h1..h7 |
| robustness | seed 20261031 для logreg и rf, g3 seed invariance | частичная репликация |

### 1.2 генератор

c99, xorshift64*, 24 параметра на пациента, без внешних библиотек. g3 строит 24 параметра как аффинную функцию одного s и генерирует детерминированный квантованный поток без rng. g5 использует ту же аффинную карту, но натуральный марковский эмиттер. within-subject маска строится из собственных 24 параметров пациента через s, равный среднему нормализованных параметров. csv контракт заморожен, все поля целые.

### 1.3 признаки и метрики

51 признак в четырёх категориях: временные, последовательностные, интервальные, динамические. две разные метрики: `idu_nat`, расстояние до 10 ближайших окон естественной обучающей выборки в 20-компонентном whitened pca пространстве, и `idu_cohort`, расстояние до 10 ближайших окон других пациентов. `idu_nat` измеряет аномальность, `idu_cohort` измеряет уникальность внутри когорты; они не взаимозаменяемы.

идентификация: closed-set top1 и top5, chance 1/число классов. open-set verification на парах окон: same-patient против different-patient, auc и eer. within-subject: pre-to-post перенос, pre-only и post-only контроли, drift между pre и post центроидами. статистика: кластерный bootstrap по пациентам, cohen d или dz, holm для семейств, 2000 ресэмплов.

### 1.4 воспроизводимость

сид 20261030, второй сид 20261031 для logreg и rf. два прогона генератора совпадают байт в байт; primary cohort sha256 `7841bd667c35ee437eea9d1c58016990c081ed022d8f042389fb356b487ce1a9`. manifest содержит хеши бинарника, csv, json и графиков. локальный bitwise replay проверен на одном компиляторе и libm; кросс-машинная эквивалентность не заявляется. python окружение зафиксировано версиями, не hash-locked wheels.

## 2. результаты

### 2.1 аномальность и уникальность

| метрика | g1 | g2 | g3 | g4 |
|---|---:|---:|---:|---:|
| idu_nat | 3.825 | 5.084 | 17.096 | 3.449 |
| idu_cohort | 3.858 | 2.900 | 0.065 | 3.009 |
| anomaly auc против g1 | 0.500 | 0.956 [0.933, 0.975] | 1.000 [1.000, 1.000] | 0.153 [0.109, 0.199] |

h1 подтверждена для аномальности: g3 против g1, cohen d=-13.16 [-14.33, -12.43], kruskal p=1.36e-94, holm 9.53e-94, n=600. h1b опровергнута: g3 наименее уникален внутри когорты, 0.065 [0.054, 0.078]. аномалия g3 тривиальна: десять отдельных признаков, включая interval_cv, higuchi_fd и repeat_rate, дают auc 1.000. g4 ниже 0.5 по одностороннему anomaly score, но двусторонний auc g4 0.847, то есть детектор отличает и слишком гладкие профили.

### 2.2 идентификация и гетерогенность моделей

**таблица 3. closed-set top1, mean [ci95].**

| модель | g1 | g2 | g3 | g4 |
|---|---:|---:|---:|---:|
| logreg | 0.769 [0.735, 0.803] | 0.382 [0.338, 0.427] | 0.293 [0.227, 0.363] | 0.015 [0.003, 0.030] |
| rf | 0.818 [0.784, 0.850] | 0.395 [0.350, 0.442] | 0.387 [0.310, 0.460] | 0.025 [0.010, 0.043] |
| mlp | 0.686 [0.648, 0.725] | 0.313 [0.270, 0.358] | 0.192 [0.135, 0.255] | 0.013 [0.003, 0.023] |
| hgb | 0.135 [0.109, 0.163] | 0.063 [0.045, 0.083] | 0.387 [0.307, 0.467] | 0.010 [0.003, 0.020] |
| chance | 0.005 | 0.0067 | 0.0067 | 0.010 |

g1 резко выше g2 и g3. строгий порядок g1 > g2 > g3 не установлен: per-model тесты g2 против g3 дают logreg +0.088 (p_holm 3.3e-5), mlp +0.122 (4.7e-8), hgb -0.323 (2.3e-5), rf +0.008 (p=0.112). среднее по моделям p=0.870 не является тестом равенства. matched анализ на 150 классах выбирает rf на валидации g1 и даёт g1 0.820, g2 0.395, g3 0.387; гетерогенность сохраняется.

потолок g3: 58 профилей на 600 окон, доля уникальных 0.0967, точный потолок top1 0.3867. rf и hgb достигают 0.3867, то есть остаточного индивидуального сигнала выше шаблона нет. top5 g3 1.000; это следствие максимальной коллизии 16, а не индивидуальной подписи.

### 2.3 within-subject переключение

**таблица 4. within-subject.**

| группа | drift | pre-only logreg | pre-to-post rf | post-only logreg | post-only rf | post профилей |
|---|---:|---:|---:|---:|---:|---:|
| g1 natural | 2.238 [2.173, 2.303] | 0.600 | 0.751 [0.711, 0.789] | 0.570 | 0.463 | 800 из 800 |
| g6 deterministic | 18.372 [18.250, 18.487] | 0.543 | 0.005 [0.000, 0.015] | 0.0825 | 0.085 | 17 из 800 |
| g7 stochastic | 3.989 [3.869, 4.119] | 0.525 | 0.004 [0.000, 0.009] | 0.005 | 0.020 | 800 из 800 |

pre-to-post перенос отсутствует у обеих масок. это не уничтожение идентичности: внутри маскированной области g6 даёт 0.085, ровно потолок 17 шаблонов, 17x chance; patient-level p=3.1e-12 для logreg и 3.2e-12 для rf. g7 даёт 0.005-0.020, только rf и hgb немного выше chance (p=0.0010 и 0.0158), logreg на chance (p=0.594). причина g7: маска-скаляр s концентрируется в [0.30, 0.64], среднее 0.4948, sd 0.0543, против равномерного [0, 1] у g3 и g5. маски всех пациентов похожи друг на друга, а внутри-пациентная вариативность эмиттера велика.

### 2.4 open-set, обнаружимость, эффективные классы

**таблица 5. open-set verification.**

| группа | open-set auc | eer |
|---|---:|---:|
| g1 | 0.894 [0.878, 0.909] | 0.178 [0.163, 0.195] |
| g2 | 0.689 [0.669, 0.711] | 0.368 [0.350, 0.385] |
| g3 | 0.993 [0.992, 0.995] | 0.0125 [0.0102, 0.0153] |
| g4 | 0.502 [0.486, 0.517] | 0.497 [0.483, 0.515] |
| g5 | 0.795 [0.782, 0.809] | 0.273 [0.258, 0.286] |
| g6 post | 0.951 [0.944, 0.957] | 0.0874 [0.0773, 0.0996] |
| g7 post | 0.558 [0.544, 0.571] | 0.455 [0.444, 0.468] |

g3 auc 0.993 измеряет дубликацию окон: внутри одного точного профиля все пары имеют нулевое расстояние, auc 0.5, eer 0.5. g7 eer 0.455 близок к g4 0.497, то есть стохастическая маска скрывает индивидуальность в open-set смысле. g5 0.795 и g6 0.951 остаются выше случайного контроля.

обнаружимость: interval_cv даёт auc 1.000 для g3 и g6; для g5 и g7 ядро регулярных признаков даёт 0.529 и 0.512, но action_entropy даёт 0.921 и 0.942. эффективные классы: hill2 52.08 для g3 на 150 пациентов, 10.11 для g6 на 200, 150 для g5 и 200 для g7. стохастическая маска прячет личность, но выдаёт факт маскировки.

### 2.5 отрицательные результаты

- h5: парная разность chaos accuracy 0.0204 [-0.0049, 0.0446], p=0.172, dz=0.160, n=100; post hoc paired t approximation: achieved power 0.354 для dz=0.160, mde dz=0.285 для power 0.80. within-patient r2 отрицательный, skill относительно среднего пациента отрицательный. гипотеза не поддержана и underpowered; длинный горизонт не заявляется.
- h6: participation ratio 2.380, lambda1 0.500, порог 2.0 и 0.80. g6 post-only 1.553 и 0.771, g6 pre/post mixture 1.468 и 0.811. rank-1 не поддерживается для g3 uniform-s и зависит от конструкции.
- h7: rf 0.025 [0.010, 0.043] на основном сиде, 0.0075 [0.000, 0.018] на втором; patient-level p_holm 0.087 по 5 моделям и 0.348 по 7 тестам. статус inconclusive.
- h4: consensus rho 0.275 [0.151, 0.394] inflated by averaging; per-model rho для idu_nat 0.167 [0.022, 0.299], 0.193 [0.056, 0.321], 0.211 [0.076, 0.340], 0.175 [0.035, 0.307], все 95% ci включают 0.20, три из четырёх точечных значений ниже 0.20. статус exploratory, малый и нестабильный эффект.
- g4: двусторонний anomaly auc 0.847, open-set auc 0.502; контроль не является чистым white noise.

### 2.6 репликация

сид 20261031: idu_nat 3.845, 5.016, 16.735, 3.498; logreg и rf top1 стабильны, дельты ci включают 0; g3 инвариантен к сиду по построению. g5 seed2: idu_nat 5.258 против 5.223, idu_cohort 3.475 против 3.407, rf top1 0.122 против 0.100, delta ci [-0.020, 0.062]. within seed2: drift и top1 стабильны, максимальный относительный сдвиг idu 2.7%, кроме g6 idu_cohort вблизи нуля. hgb и mlp на втором сиде не запускались.

## 3. ограничения

1. данные синтетические; 24 параметра и марковская модель не являются биологической моделью. внешняя валидность отсутствует.
2. g3 является детерминированным квантованным конструктом. g5 отделяет аффинную карту параметров от эмиттера, но не разделяет детерминизм и квантование полностью.
3. within-subject маска g6/g7 строится из среднего 24 параметров, поэтому s концентрируется. это объясняет остаточную идентифицируемость g6 и слабую g7, но является свойством конструкции.
4. g6 и g7 являются независимыми пациентами, а не двумя масками одного человека. сравнение g6 против g7 between-subject; within только pre/post.
5. число классов различается: g1 200, g2/g3/g5 150, g4 100. matched 150 покрывает g1/g2/g3, но не g4 и g5.
6. hgb недообучен на g1 и g2; per-model результаты важнее среднего. выбор rf на валидации g1 не является нейтральным.
7. g5, matched, within, open-set, detectability, effective classes и post-only контроли добавлены после основного анализа и являются exploratory. h1-h7 не пересматриваются.
8. h4 малый и нестабильный; h5 не поддержана и underpowered; h7 inconclusive.
9. anomaly score односторонний; двусторонний auc g7 0.933 и g4 0.847. детектор, помечающий и слишком регулярные, и слишком гладкие профили, отделяет обе группы.
10. idu_cohort зависит от состава когорты; сравнения между файлами требуют same-file g1 baseline.
11. bitwise replay проверен локально на одном компиляторе и libm; кросс-машинная эквивалентность и hash-locked python окружение не проверены.
12. пререгистрация self-reported, без внешней метки времени. публичного DOI и авторских метаданных пока нет. в refs/ есть предыдущая рукопись с той же гипотезой, её статус нужно раскрыть до подачи.

## 4. honesty check

| claim | status | evidence | boundary |
|---|---|---|---|
| детерминированная маска аномальна | supported | idu_nat 17.096 против 3.825, d=-13.16 | синтетика, g3 конструкт |
| детерминированная маска не уникальна | supported | idu_cohort 0.065, 58 профилей, потолок 0.3867 | синтетика |
| сильный парадокс rank-1 уникальности | refuted | pr 2.380, lambda1 0.500 | для g3 uniform-s |
| g2 против g3 монотонно | not established | per-model p расходятся; rf tie | классы и модели различаются |
| маска уничтожает идентичность | refuted in strong form | pre-to-post 0.005, но post-only g6 0.085, g7 1-4x chance | перенос сломан, информация остаётся |
| стохастическая маска скрывает личность | supported in-domain | open-set eer 0.455 против 0.497 у g4 | маска обнаружима по action_entropy |
| прогноз ограничен горизонтом | not supported | diff 0.0204, ci включает 0, r2 отрицательный | underpowered |
| g4 контроль на уровне шанса | inconclusive | 0.025 и 0.0075 на двух сидах | один сид выше порога |
| уникальность предсказывает идентификацию | exploratory, weak | consensus 0.275, per-model 0.167-0.211 | малый эффект |
| артефакт воспроизводим | locally supported | sha256, manifest, tests | локальный compiler и libm, без публичного DOI |

## 5. команды воспроизведения

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
make manifest
```

## 6. источники

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
- угланова, н. н., мушников, д. л., костин, в. в. и др. (2010). информационная культура пациентов и пути ее повышения. вестник рудн, серия медицина, № 4, с. 367-371.
- угланова, н. н., мушников, д. л., поляков, б. а. (2020). информированность студентов медицинского вуза. вестник ивгма, т. 25, № 3-4.
