# eidolon: отклонения от пререгистрации и post hoc решения

registered_at: 2026-10-30T16:39:05Z
analysis_completed: 2026-10-30T18:45:00Z

исходный текст `hypotheses.md` не переписывался после запуска; в конец добавлены exploratory addenda. ниже перечислены все отклонения и решения, принятые после просмотра данных, с указанием статуса.

| id | зарегистрировано | выполнено | статус | причина |
|---|---|---|---|---|
| d1 | 500 пациентов в разделе 2 протокола | 600 пациентов: 200+150+150+100 | deviation | детальные размеры групп задают мощность; сумма 600, конфликт зафиксирован |
| d2 | h2 проверяется permutation test | mann-whitney по patient-level consensus и per-model | deviation | permutation не даёт новой информации при 200 классах; consensus помечен exploratory |
| d3 | h3 auc на тестовых окнах | patient-level auc primary, window-level auc sensitivity | deviation | окна одного пациента зависимы; обе единицы репортятся |
| d4 | h4 holm по семейству 7 | holm по 4 корреляциям, затем holm по 7 primary | deviation | сначала семейство корреляций, затем глобальная поправка |
| d5 | h5 accuracy падает с горизонтом | one-step ridge, accuracy=1-mae/mean, baselines, within-patient r2 | deviation | исходная метрика не является skill score; добавлены baselines, h5 опровергнута |
| d6 | h6 participation ratio <2.0, lambda1>0.80 | те же пороги на 51 признаке, 20 pca | deviation | pca 20 не меняет g3, потому что ранг g3 ниже 20; добавлен post hoc spearman diagnostic |
| d7 | h7 chance + 2 binomial sd, permutation | window-level binomial, patient-level binomial, holm 5 и 7, seed2 | deviation | окна зависимы; patient-level primary, seed2 репликация |
| d8 | idu = f(t,s,f,r,c,v) | idu_nat и idu_cohort, k=10, pca 20 | operationalization | две разные конструкции: аномалия и уникальность; обе репортятся |
| d9 | 4 модели | 5 моделей, включая dummy | extension | dummy нужен как chance baseline |
| d10 | pytorch для nn | sklearn MLPClassifier | deviation | pytorch отсутствует в окружении; sklearn mlp детерминирован, 51 признак и 200 классов |
| d11 | g3 rank-1 | латентные 24 параметра rank-1, наблюдаемые 51 признаки pr=2.38 | negative result | линейная pca не сохраняет нелинейную одномерную кривую; h6 опровергнута |
| d12 | g4 pure white noise | daily re-randomized natural | deviation | сохранены натуральные маргиналы, убрана устойчивая идентичность; g4 переименован |
| d13 | 90 дней, дни 1-30 train, 31-60 и 61-90 test | то же, one-step target | deviation | прогноз next-day, не 30-дневный горизонт |
| d14 | seed 20261030 + 20261031 для idu cv и logreg | seed2: idu, logreg, rf | partial | g3 инвариантен к сиду; hgb/mlp на seed2 не запускались |
| d15 | четыре группы | добавлена exploratory g5: те же аффинные интенсивные параметры, натуральный стохастический эмиттер | exploratory | отделяет детерминированный эмиттер от интенсивности параметров |
| d16 | h2 по среднему четырёх моделей | per-model patient-level тесты и matched 150-class sensitivity | correction | среднее скрывает противоположные знаки: logreg/MLP g2>g3, hgb g3>g2, rf tie |
| d17 | collision ceiling 0.0967 | profile fraction 0.0967, plurality ceiling 0.3867 | correction | 0.0967 это оконная доля, а не потолок top1; rf/hgb top1 равен 0.3867 |
| d18 | четыре группы | within-subject g6/g7: 200 natural, 200 deterministic switch, 200 stochastic switch | exploratory | причинная проверка на одном пациенте, дни 1-45 natural, 46-90 mask |
| d19 | closed-set top1 | open-set verification, post-only и pre-only контроли, mask detectability, effective classes | extension | reviewer gate: closed-set не отвечает на вопрос известный/новый; post-only отделяет перенос от уничтожения идентичности |

## post hoc анализы

- коллизии g3: 600 тестовых окон, 58 уникальных векторов, максимальная коллизия 16, profile fraction 0.0967, plurality ceiling 0.3867.
- одномерные auc g3 vs g1: 10 признаков достигают auc 1.0, включая interval_cv, higuchi_fd, repeat_rate.
- held-out reference: scaler, pca, knn и isolation forest обучены на 100 пациентах g1, оценены на остальных 100 g1 и на g2/g3/g4. направления сохранены: idu_nat 4.10 / 5.29 / 16.51 / 3.67.
- patient-level h7: rf 9/100 пациентов с хотя бы одним верным окном против ожидания 3.94, p=0.0174, holm 5 моделей 0.087, holm 7 тестов 0.348; seed2 rf 0.0075.
- global holm по 7: значимы h1, h3, h4; h2, h5, h6, h7 не значимы после поправки.
- per-model g2/g3: logreg и mlp дают g2>g3, hgb g3>g2, rf tie; среднее по моделям не является тестом.
- plurality ceiling: g3 profile fraction 0.0967, patient-level exact-profile ceiling 0.3867, rf и hgb top1 равны 0.3867.
- g5: 600 из 600 уникальных профилей, idu_nat 5.223, idu_cohort 3.407, anomaly auc 0.629, rf top1 0.100.

## что не делалось

- не запускался полный permutation null для g4 rf.
- стохастический вариант g3 построен в v1.1.0 как g5; within-subject переключение построено в v1.2.0 как g6/g7; см d15 и d18.
- не выполнялась настройка hgb; модель оставлена как зарегистрированный слабый классификатор.
- не использовался pytorch.
- не проверялась воспроизводимость на другой машине; только локальный bitwise replay.
