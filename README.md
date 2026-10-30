# eidolon

синтетическое исследование парадокса детерминированной анонимности: 600 виртуальных пациентов, 90 дней, 24 скрытых параметра, четыре основные группы поведения плюс exploratory стохастическая интенсивная группа g5, повторная идентификация и прогноз активности.

## статус

исходная гипотеза проверена в пререгистрированной форме и подтверждена только частично. интенсивная маскировка g3 повышает расстояние до естественного многообразия (idu_nat 17.10 против 3.83 у g1), но не повышает уникальность внутри когорты: idu_cohort 0.065, минимум среди групп. g3 коллапсирует в 58 уникальных векторов признаков на 600 тестовых окон; максимальная коллизия 16 окон. строгая формулировка "rank-1 аномальный и уникальный профиль" опровергнута: participation ratio 2.38, lambda1 share 0.50. строгий порядок идентифицируемости g1 > g2 > g3 не выполнен, но per-model тесты разнонаправлены: logreg и mlp дают g2 > g3, hgb даёт g3 > g2, rf tie. среднее по моделям p=0.870 не является тестом неразличимости. g5 с теми же интенсивными параметрами и натуральным эмиттером даёт 600 из 600 уникальных профилей, anomaly auc 0.629 и rf top1 0.100.

подробные вердикты: [results/verdicts.json](results/verdicts.json). отклонения от пререгистрации: [paper/deviations.md](paper/deviations.md). препринт: [paper/preprint.md](paper/preprint.md).

## состав

| путь | содержание |
|---|---|
| `src/` | c99 генератор, xorshift64*, без внешних зависимостей |
| `python/` | признаки, idu, модели, прогноз, статистика, графики |
| `data/` | cohort.csv, chaos.csv, g5.csv, within.csv, seed2/cohort.csv |
| `results/` | таблицы, json, графики, manifest |
| `paper/` | препринт и отклонения |
| `refs/` | исходные документы проекта |

## сборка

```sh
make
./eidolon_gen --seed 20261030 --out data/cohort.csv
./eidolon_gen --seed 20261030 --out data/chaos.csv --chaos --n1 100 --n2 0 --n3 0 --n4 0
./eidolon_gen --seed 20261030 --out data/g5.csv --n1 200 --n2 150 --n3 150 --n4 100 --n5 150
./eidolon_gen --seed 20261030 --out data/within.csv --n1 200 --n2 0 --n3 0 --n4 0 --n5 0 --n6 200 --n7 200
```

флаги: `-std=c99 -pedantic -Wall -Wextra -Werror -O2 -ffp-contract=off`. линковка: `-lm`. санитайзеры: `make test` (asan и ubsan, ld_preload очищается).

## csv contract

header заморожен, версия 1. все поля целые, разделитель `,`, десятичная точка не используется.

```
patient_id,group,day,t_s,action_seq,interval_ms,session_dur_s,action_id,section_id,is_repeat,session_idx,day_of_week,is_weekend
```

| колонка | единица | смысл |
|---|---|---|
| patient_id | id | 0..599 |
| group | 1..7 | 1 natural, 2 moderate, 3 intense deterministic, 4 daily re-randomized, 5 stochastic intense, 6 deterministic switch, 7 stochastic switch |
| day | день | 1..90 |
| t_s | секунда суток | 0..86399 |
| action_seq | номер | позиция события в сессии, 1..n |
| interval_ms | мс | интервал с предыдущим событием, 0 для первого |
| session_dur_s | с | длительность сессии |
| action_id | 0..7 | тип действия |
| section_id | 0..5 | раздел |
| is_repeat | 0/1 | совпадение с предыдущим действием |
| session_idx | 1..n | номер сессии в дне |
| day_of_week | 1..7 | 1 понедельник |
| is_weekend | 0/1 | day_of_week >= 6 |

## группы

| группа | n | генератор |
|---|---|---|
| g1 natural | 200 | 24 параметра, марковские действия, логнормальные интервалы, 1/f фактор, циркадный и недельный ритм |
| g2 moderate | 150 | параметры сжаты к среднему в 0.55, шум в действиях, интервалах, времени и длительности |
| g3 intense | 150 | 24 параметра аффинны одному s, событийный поток детерминирован и квантован, без rng |
| g4 random | 100 | ежедневная повторная выборка натуральных параметров, без устойчивой идентичности |
| g5 stochastic intense | 150 | те же 24 аффинных параметра, что у g3, но натуральный стохастический эмиттер; exploratory, отдельный файл |
| g6 deterministic switch | 200 | дни 1-45 natural, дни 46-90 детерминированная маска g3; within-subject, отдельный файл |
| g7 stochastic switch | 200 | дни 1-45 natural, дни 46-90 стохастическая маска; within-subject, отдельный файл |

исходный протокол содержит 500 в одном разделе и суммы 200+150+150+100=600 в другом. принято 600 по детальным размерам групп; конфликт зафиксирован в `hypotheses.md` и `paper/deviations.md`.

## воспроизведение

полный контур: `make analysis`. отдельные шаги:

```sh
make check
make manifest
python3 python/eidolon_features.py --csv data/cohort.csv --out-dir results
python3 python/eidolon_models.py --groups 1,2,3,4 --models dummy,logreg,rf,hgb,mlp
python3 python/eidolon_forecast.py --cohort data/cohort.csv --chaos data/chaos.csv --out-dir results
python3 python/eidolon_stats.py
python3 python/eidolon_robustness.py
python3 python/eidolon_corrections.py
python3 python/eidolon_matched.py
python3 python/eidolon_features.py --csv data/within.csv --out-dir results/within
python3 python/eidolon_within.py
python3 python/eidolon_plots.py
python3 python/eidolon_g5_plot.py
python3 python/eidolon_within_plot.py
python3 -m unittest discover -s tests
```

второй сид:

```sh
./eidolon_gen --seed 20261031 --out data/seed2/cohort.csv
python3 python/eidolon_features.py --csv data/seed2/cohort.csv --out-dir results/seed2
python3 python/eidolon_models.py --features results/seed2/features.csv --out-dir results/seed2 --groups 1,2,3,4 --models logreg,rf
python3 python/eidolon_features.py --csv data/g5.csv --out-dir results/g5
python3 python/eidolon_models.py --features results/g5/features.csv --out-dir results/g5 --groups 1,5 --models dummy,logreg,rf,hgb,mlp
python3 python/eidolon_corrections.py
python3 python/eidolon_matched.py
```

## детерминизм

два прогона с сидом 20261030 дают битвайз идентичный csv. sha256:

```
7841bd667c35ee437eea9d1c58016990c081ed022d8f042389fb356b487ce1a9  data/cohort.csv
```

`make check` запускает `cmp`; `make manifest` пишет `results/manifest.txt` с sha256 бинарника, csv, json, графиков, компилятором, cflags, сидом и хешем python окружения.

## ключевые числа

| метрика | g1 | g2 | g3 | g4 | g5 |
|---|---|---|---|---|---|
| idu_nat, mean | 3.825 | 5.084 | 17.096 | 3.449 | 5.223 |
| idu_cohort, mean | 3.858 | 2.900 | 0.065 | 3.009 | 3.407 |
| anomaly auc vs g1 | 0.500 | 0.956 | 1.000 | 0.153 | 0.629 |
| rf top1, mean [ci95] | 0.818 [0.784, 0.850] | 0.395 [0.350, 0.442] | 0.387 [0.310, 0.460] | 0.025 [0.010, 0.043] | 0.100 [0.075, 0.130] |
| logreg top1, mean [ci95] | 0.769 [0.735, 0.803] | 0.382 [0.338, 0.427] | 0.293 [0.227, 0.363] | 0.015 [0.003, 0.030] | 0.040 [0.025, 0.057] |
| chance | 0.005 | 0.0067 | 0.0067 | 0.010 | 0.0067 |

прогноз next-day events: g1 accuracy 0.494 [0.478, 0.501], g2 0.483 [0.464, 0.490], g3 1.000, g4 0.448 [0.423, 0.463], chaos 0.496 [0.472, 0.505] на днях 31-60 и 0.481 [0.448, 0.488] на днях 61-90. within-patient r2 отрицательный во всех недетерминированных группах, поэтому это не skill score, а one-step forecast без навыка.

## ограничения

- данные синтетические; 24 параметра и марковская модель действий не являются биологической моделью.
- g3 это детерминированный конструкт, а не наблюдение реальной маскировки; 58 уникальных профилей и отсутствие rng делают его manipulation check. g5 показывает, что коллапс исчезает при натуральном эмиттере с теми же параметрами.
- g4 это daily re-randomized natural, не чистый white noise из протокола.
- число классов и обучающих окон различается между группами: g1 200 классов и 1000 окон, g2/g3 150 и 750, g4 100 и 500. сравнение top1 между группами ограничено этим.
- hgb недообучен на g1 и g2; per-model результаты важнее среднего по моделям. среднее скрывает противоположные знаки g2/g3.
- idu_nat зависит от референсной выборки; held-out reference на 100 пациентах g1 даёт те же направления: 4.10 / 5.29 / 16.51 / 3.67.
- прогноз одношаговый; within-patient r2 отрицательный, claim о долгосрочном пределе снят.
- rank-1 опровергнут на наблюдаемых признаках; латентная конструкция g3 аффинна одному s, но 51 признак не линеен по s. g5 даёт participation ratio 1.944 и lambda1 0.692, ближе к низкоразмерному, но всё ещё не rank-1.
- g3: 58 профилей на 600 окон, profile fraction 0.0967, plurality ceiling 0.3867; rf и hgb top1 равны 0.3867, то есть остаточного индивидуального сигнала выше точного шаблона нет.
- pytorch не использован; нейросеть это sklearn MLPClassifier. окружение зафиксировано в requirements.txt.
- основной сид 20261030, репликация 20261031 для logreg и rf; g3 инвариантен к сиду.
- within-subject: natural control rf top1 0.751, детерминированная маска 0.005, стохастическая 0.004 при chance 0.005; drift 2.238 / 18.372 / 3.989. это причинный аргумент, но только для двух синтетических масок.

## лицензия и данные

код: MIT, см. `LICENSE`. статья, README и синтетические csv: CC BY 4.0, см. `LICENSE-CC-BY-4.0`. файлы в `refs/` не лицензируются этим проектом и исключены из release tarball. реальные пациенты не использовались. подробности в `NOTICE`.
