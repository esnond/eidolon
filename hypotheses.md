# eidolon: пререгистрация гипотез

registered_at: 2026-10-30T16:39:05Z
status: frozen before cohort generation
author: orchestrator, project eidolon

## 1. дизайн и конфликт протокола

исходный протокол содержит внутреннее противоречие: в разделе 2 указано 500 виртуальных пациентов, в разделе 4 суммы групп 200+150+150+100=600. принято решение: использовать детальные размеры групп, n=600. причина: размер группы задаёт мощность парных сравнений, а сумма 600 не меняет вычислительную стоимость. все отчёты содержат фактические n.

группы: g1 естественное поведение (n=200), g2 умеренная маскировка (n=150), g3 интенсивная маскировка (n=150), g4 случайный контроль (n=100). наблюдение 90 дней. единица анализа идентификации: окно 10 дней. обучение: окна 1-5 (дни 1-50), тест: окна 6-9 (дни 51-90).

## 2. операциональные определения

- accuracy: доля верных ответов closed-set классификатора внутри группы, 150-200 классов, chance=1/n_group.
- idu_nat: среднее расстояние до k=10 ближайших окон естественной референсной выборки (обучение g1) в пространстве 20 главных компонент, whitened, стандартизованные признаки. мера удалённости от естественного многообразия.
- idu_cohort: среднее расстояние до k=10 ближайших окон всех пациентов, кроме собственных, в том же пространстве. мера индивидуальной различимости внутри когорты.
- anomaly: средний score isolation forest, обученного только на обучающих окнах g1. auc считается для пар g2/g1, g3/g1, g4/g1 на тестовых окнах.
- rank1: participation ratio pr=(sum lambda)^2/sum(lambda^2) и доля первой компоненты lambda1/sum lambda для матрицы признаков группы после стандартизации на g1.
- forecast accuracy: 1 - mae/mean(target), target = число событий следующего дня; модель ridge с лагами 1-7, скользящим средним 7 дней и sin/cos дня недели, пер-пациентная z-нормировка по дням 1-30. горизонты: дни 31-60 и 61-90.

## 3. гипотезы

| id | prediction | falsification | primary test |
|---|---|---|---|
| h1 | idu_nat: g3 > g2 > g1, минимум g3-g1 cohen d >= 0.8 | порядок нарушен или d < 0.5 | kruskal-wallis, pairwise mann-whitney, cohen d, bootstrap ci95 |
| h2 | accuracy: g1 > g2 > g3, g3 выше chance | g3 <= chance или порядок обратный | cluster bootstrap ci95, permutation test |
| h3 | anomaly auc(g3 vs g1) >= 0.80 | auc < 0.65 или ci95 включает 0.50 | roc auc, patient bootstrap ci95 |
| h4 | внутри g1 idu_nat положительно связан с вероятностью верной идентификации: spearman rho >= 0.20 | rho <= 0 или p >= 0.05 после holm | spearman, bootstrap ci95 |
| h5 | в chaos-когорте forecast accuracy падает с горизонтом: days 31-60 > days 61-90; в g3 остаётся высокой | падения нет или g3 падает так же | paired bootstrap по пациентам, cohen d |
| h6 | g3 имеет rank-1 профиль: participation ratio < 2.0 и lambda1 share > 0.80 | pr >= 2.0 или lambda1 share <= 0.80 | pca на стандартизованных признаках |
| h7 | g4 accuracy не выше chance + 2 биномиальных sd | g4 выше порога | binomial test, permutation |

## 4. мультипликативность и мощность

первичные гипотезы h1-h7. поправка holm внутри семейства из 7 тестов. парные сравнения групп: 3 пары на метрику, поправка holm внутри метрики. априорная мощность для d=0.5, alpha=0.05/7, n=150 на группу: расчёт в python/experiment_stats.py, порог power>=0.80. если наблюдаемая мощность ниже 0.80, результат помечается "underpowered".

## 5. остановка и отчётность

один основной сид 20261030. сид 20261031 используется для проверки устойчивости коэффициента вариации idu и accuracy logistic regression. все сиды репортятся. никакие модели не удаляются после просмотра результатов. g3 не подгоняется под ожидаемый знак эффекта: если accuracy g3 выше g1, это репортится как опровержение h2.

## 6. ограничения, зафиксированные до запуска

- данные синтетические; биологическая правдоподобность ограничена 24 параметрами и марковской моделью действий;
- closed-set идентификация не равна юридической верификации личности;
- idu зависит от выбора референсной популяции и метрики расстояния;
- g3 является конструктом "детерминированная маскировка", а не наблюдением реальных пользователей;
- эффекты размера группы и числа классов не полностью отделимы от интенсивности маскировки;
- прогноз next-day events не равен прогнозу полной последовательности действий.

## addendum 2026-10-30T17:40:00Z

- ссылка `python/experiment_stats.py` в разделе 4 устарела: расчёт мощности находится в `python/eidolon_stats.py`, функция `power_t`. файл не переименовывался, пререгистрация не редактировалась.
- уточнение к разделу 1: в протоколе раздел 4 содержит три группы 200+150+150=500, контроль 100 описан отдельно в разделе 13. сумма 600 получается из детальных размеров, а не из одного раздела. решение о 600 и конфликт зафиксированы в `paper/deviations.md`.
- все отклонения от зарегистрированных тестов перечислены в `paper/deviations.md`; h2, h5, h6, h7 репортятся как опровергнутые или неопределённые, а не как подтверждённые.

## addendum 2026-10-30T18:00:00Z: exploratory sensitivity after primary analysis

status: exploratory, not confirmatory. this addendum was written after the primary results were known and does not change h1-h7.

- g5 stochastic intense: 150 patients, same 24 affine intense parameters as g3, natural stochastic emitter. question: is the g3 template collapse caused by the deterministic emitter or by parameter extremity. primary endpoint: plurality ceiling and rf top1. a result with 600 of 600 unique profiles, plurality ceiling 1.0 and rf top1 near chance supports the emitter explanation; a result with shared profiles and top1 near the g3 ceiling supports the parameter explanation.
- matched 150-class sensitivity: g1 reduced to 150 patients by a fixed random seed, g2 and g3 already have 150. one primary classifier selected on g1 validation and applied unchanged. question: does the g2/g3 difference survive equal class count and training size. both per-model and selected-model results are reported.
- per-model correction: the average across four models is not a test and is not used for h2. per-model patient-level mann-whitney with holm is primary.
- plurality correction: profile fraction is distinct_profiles/windows; the exact-profile top1 ceiling is (1/n) sum_i max_j n_{p(i),j}/n_{p(i)}. the window value 0.0967 is not compared with patient-level top1.
- within-subject switch: 200 natural control, 200 g6 deterministic switch, 200 g7 stochastic switch. the same patient is natural on days 1-45 and masked on days 46-90. train on windows 1-4, test on windows 6-9, window 5 excluded. primary endpoint: rf top1 for the same 200 classes; secondary: drift between pre and post centroids. if g6 or g7 top1 stays above 0.50, identity persists through the mask; if it falls to chance, the mask destroys individual identity. this analysis is exploratory and was specified after the g5 result.
