# results: индекс артефактов

все числа в препринте взяты из файлов ниже. `features.csv` содержит nan в `idu_nat` и `idu_cohort` для обучающих окон: эти метрики определены только для тестовых окон 6-9. `stats.json` содержит машинные вердикты, `verdicts.json` содержит итоговую интерпретацию с учётом robustness.

## таблицы

| файл | соответствует таблице препринта | содержание |
|---|---|---|
| `table1_cohort.csv` | таблица 2 | размеры групп, idu_nat, idu_cohort, anomaly |
| `table2_behavior.csv` | таблица 3 | поведенческие признаки, mean, sd, count |
| `table3_groups.csv` | текст раздела 4.3 | pairwise сравнения idu_nat и consensus accuracy |
| `table4_models.csv` | таблица 4 | accuracy, ci95, top5, auc, chance по моделям |
| `table5_importance.csv` | таблица 6 | permutation importance для g1 |
| `table6_forecast.csv` | таблица 5 | прогноз events и mean_start, r2, within r2 |

## ключевые файлы

| файл | содержание |
|---|---|
| `verdicts.json` | итоговые вердикты h1..h7, безопасные и небезопасные формулировки |
| `stats.json` | kruskal, mann-whitney, cohen d, ci95, holm, power |
| `robustness.json` | коллизии g3, одномерные auc, idu_cohort, patient-level h7, held-out reference, holm по 7 |
| `models.json` | метрики пяти моделей по четырём группам |
| `predictions.csv` | предсказания тестовых окон, 12 000 строк |
| `forecast.json` | прогноз events и mean_start, baselines, within r2, learning curve |
| `forecast_patient.csv` | per-patient accuracy по горизонтам |
| `patient_metrics.csv` | агрегаты idu_nat, idu_cohort, anomaly, mahalanobis по пациентам |
| `rank1.json` | participation ratio и lambda1 share по группам |
| `seed_replication.json` | сид 20261030 против 20261031 |
| `corrections.json` | per-model g2/g3, plurality ceiling, g5 сравнение |
| `matched.json` | matched 150-class sensitivity, выбор primary classifier |
| `g5/` | признаки, модели и метрики стохастической интенсивной группы |
| `within/` | within-subject features, models, drift, predictions |
| `figures/fig7_g5.png` | g3 против g5: idu_nat и top1 |
| `figures/fig8_within.png` | within-subject drift и identification |
| `manifest.txt` | sha256, компилятор, cflags, сид, окружение, determinism |
| `figures/` | шесть png с ci95, где применимо |

## известные ограничения артефакта

- g3 не использует rng и инвариантен к сиду; его 58 уникальных профилей и top5=1.0 являются свойством конструкции.
- g4 это daily re-randomized natural, не чистый white noise.
- число классов различается: 200, 150, 150, 100.
- `hgb` недообучен на g1 и g2.
- прогноз одношаговый, within-patient r2 отрицательный.
- pytorch не использован, нейросеть это sklearn mlpclassifier.
