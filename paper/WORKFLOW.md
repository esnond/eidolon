# paper workflow

date: 2026-10-31
version: 1.3.0
command: `/paper`

## стадии

1. prioritizer: какие результаты идут в статью, что в supplementary. выход: keep/cut list и три headline claim.
2. methodologist: проверка ci, effect size, n, seeds, cherry-picking, reproducibility, manifest. выход: required_fixes.
3. editor: abstract, methods, results, limitations, reproduction commands. выход: `paper/DRAFT.md`.
4. adversary: враждебный ревью. выход: `paper/ADVERSARIAL_REVIEW.md`.
5. fixes: применить принятые, заполнить honesty check, обновить manifest и release после приёмки.

## файлы

| файл | роль |
|---|---|
| `paper/DRAFT.md` | русский черновик, honesty check |
| `paper/DRAFT_EN.md` | английский черновик, те же числа и honesty check |
| `paper/paper_preparation.md` | отчёт по стадиям и pass 2 |
| `paper/ADVERSARIAL_REVIEW.md` | враждебный ревью и ответы |
| `paper/TRANSLATION_STATUS.md` | статус русского и английского |
| `results/methodologist_checks.json` | power, per-model h4 ci, post-only patient tests |
| `tools/check_paper_claims.py` | механический гейт чисел, статусов и стиля |

## механический гейт

```sh
make paper
```

проверяет:

- ключевые числа обоих DRAFT против `results/verdicts.json`, `results/corrections.json`, `results/within/models.json`, `results/within/postonly.json`, `results/verification.json`, `results/robustness2.json`, `results/methodologist_checks.json`;
- наличие honesty check и допустимых статусов;
- наличие метки exploratory у g5, within, open-set и detectability;
- отсутствие длинного тире и ёлочек;
- существование файлов, на которые ссылается DRAFT.

## порядок запуска

```sh
make paper
make test-python
make check
```

после авторской приёмки:

```sh
make manifest
make release
```

## статус

- DRAFT: прошёл внутренний methodologist и adversary, ждёт авторского ревью.
- перевод: русский и английский DRAFT готовы, английский сайт пока нет.
- release: `eidolon-v1.3.0` остаётся последним проверенным; пересборка после приёмки DRAFT.
