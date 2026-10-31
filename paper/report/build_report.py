#!/usr/bin/env python3
"""собирает pdf отчёт eidolon из paper/preprint.md.

запуск:
    PYTHONPATH=tmp_check/pdflib python3 paper/report/build_report.py

зависимости: weasyprint 65.1, markdown, matplotlib.
шрифты pt serif, pt sans, pt mono скачиваются в paper/report/.cache/fonts
при первом запуске, лицензия sil ofl 1.1.
"""

from __future__ import annotations

import base64
import html
import re
import shutil
import sys
import urllib.request
from pathlib import Path

import markdown
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

matplotlib.rcParams["mathtext.fontset"] = "stix"
matplotlib.rcParams["svg.fonttype"] = "path"

ROOT = Path(__file__).resolve().parents[2]
REPORT = Path(__file__).resolve().parent
BUILD = REPORT / "build"
CACHE = REPORT / ".cache"
FONT_DIR = CACHE / "fonts"
EQ_DIR = BUILD / "eq"
PREPRINT = ROOT / "paper" / "preprint.md"

DATE = "2026-10-31"
PDF_NAME = f"eidolon-report-ru-{DATE}.pdf"
HTML_NAME = f"eidolon-report-ru-{DATE}.html"

FONT_FILES = {
    "PT_Serif-Web-Regular.ttf": ("ptserif", "PT_Serif-Web-Regular.ttf"),
    "PT_Serif-Web-Bold.ttf": ("ptserif", "PT_Serif-Web-Bold.ttf"),
    "PT_Serif-Web-Italic.ttf": ("ptserif", "PT_Serif-Web-Italic.ttf"),
    "PT_Serif-Web-BoldItalic.ttf": ("ptserif", "PT_Serif-Web-BoldItalic.ttf"),
    "PT_Sans-Web-Regular.ttf": ("ptsans", "PT_Sans-Web-Regular.ttf"),
    "PT_Sans-Web-Bold.ttf": ("ptsans", "PT_Sans-Web-Bold.ttf"),
    "PT_Sans-Web-Italic.ttf": ("ptsans", "PT_Sans-Web-Italic.ttf"),
    "PT_Sans-Web-BoldItalic.ttf": ("ptsans", "PT_Sans-Web-BoldItalic.ttf"),
    "PT_Mono-Web-Regular.ttf": ("ptmono", "PTM55FT.ttf"),
    "OFL-PTSerif.txt": ("ptserif", "OFL.txt"),
    "OFL-PTSans.txt": ("ptsans", "OFL.txt"),
    "OFL-PTMono.txt": ("ptmono", "OFL.txt"),
}

FONT_CSS = [
    ("PT Serif", "PT_Serif-Web-Regular.ttf", 400, "normal"),
    ("PT Serif", "PT_Serif-Web-Bold.ttf", 700, "normal"),
    ("PT Serif", "PT_Serif-Web-Italic.ttf", 400, "italic"),
    ("PT Serif", "PT_Serif-Web-BoldItalic.ttf", 700, "italic"),
    ("PT Sans", "PT_Sans-Web-Regular.ttf", 400, "normal"),
    ("PT Sans", "PT_Sans-Web-Bold.ttf", 700, "normal"),
    ("PT Sans", "PT_Sans-Web-Italic.ttf", 400, "italic"),
    ("PT Sans", "PT_Sans-Web-BoldItalic.ttf", 700, "italic"),
    ("PT Mono", "PT_Mono-Web-Regular.ttf", 400, "normal"),
]

FIG_CAPTIONS = {
    "1": "idu_nat и idu_cohort по группам. панель a показывает расстояние до естественного многообразия, панель b показывает расстояние до окон других пациентов. g3 отделён в a и коллапсирует в b.",
    "2": "closed-set top1 по группам и моделям. доверительные интервалы получены кластерным bootstrap по пациентам, 2000 ресэмплов.",
    "3": "связь уникальности и идентифицируемости. внутри g1 связь положительная, но объяснённая дисперсия мала; смешение групп даёт близкую к нулю общую корреляцию.",
    "4": "прогноз следующего дня. панель a показывает точность по горизонтам, панель b показывает кривую обучения chaos когорты.",
    "5": "top 10 permutation importance для g1. sequence признаки дают суммарно 0.446, temporal 0.113, interval 0.091.",
    "6": "anomaly roc для g2, g3 и g4 против g1. g3 достигает auc 1.000, но тот же результат даёт один признак регулярности.",
    "7": "стохастическая интенсивная группа g5 против g3. те же 24 аффинных параметра, натуральный эмиттер: профили остаются уникальными, аномальность умеренная.",
    "8": "within-subject переключение g6 и g7. панель a показывает сдвиг профиля, панель b показывает идентификацию после переключения.",
}

TABLE_TEXT = {"1", "7", "9"}

TEX = {
    "rng": r"$x \leftarrow x \oplus (x \gg 12),\quad x \leftarrow x \oplus (x \ll 25),\quad x \leftarrow x \oplus (x \gg 27)$",
    "rng_mul": r"$u_t = 2685821657736338717 \cdot x_t \quad (\mathrm{mod}\ 2^{64})$",
    "polar": r"$u,v \sim U(-1,1),\quad s=u^2+v^2,\quad 0<s<1$",
    "normal": r"$z_1=u\sqrt{-2\ln s/s},\quad z_2=v\sqrt{-2\ln s/s}$",
    "poisson": r"$k=\min\{n:u_1u_2\cdots u_n \leq e^{-\lambda}\}-1$",
    "lognorm": r"$r_j=b\,\exp(\sigma z_j)\,F_t,\quad \sigma=\frac{1}{2}(p_{13}+p_{14})(1.5-p_{19})c$",
    "ar": r"$f_t^{(j)}=\phi_j f_{t-1}^{(j)}+\sqrt{1-\phi_j^2}\,\varepsilon_t,\quad F_t=\exp(0.12(f_t^{(1)}+f_t^{(2)}+f_t^{(3)}))$",
    "natural": r"$\theta_k=\mathrm{clip}\left(\mu_k+\sigma_k(0.75 z_k+0.45 g_{c(k)}),L_k,H_k\right)$",
    "mask": r"$s_i=\frac{1}{24}\sum_{k=1}^{24}\frac{\theta_{ik}-L_k}{H_k-L_k}$",
    "affine": r"$\theta'_{ik}=L_k+s_i(H_k-L_k)$",
    "idu": r"$\mathrm{IDU}_{\mathrm{nat}}(x)=\frac{1}{10}\sum_{r=1}^{10}\left\|W(x-x_{(r)})\right\|_2$",
    "plurality": r"$C=\frac{1}{N}\sum_{i=1}^{N}\max_{p}\frac{n_{i,p}}{n_{C(i)}}$",
    "cohen": r"$d=\frac{\bar{x}_1-\bar{x}_2}{s_p},\quad s_p=\sqrt{\frac{(n_1-1)s_1^2+(n_2-1)s_2^2}{n_1+n_2-2}}$",
    "dz": r"$d_z=\bar{d}/s_d$",
    "holm": r"$p_{(k)}^{adj}=\min(1,\max_{j\leq k}(m-j+1)p_{(j)})$",
    "pr": r"$\mathrm{PR}=\left(\sum_j\lambda_j\right)^2/\sum_j\lambda_j^2,\quad \ell_1=\lambda_1/\sum_j\lambda_j$",
    "auc": r"$\mathrm{AUC}=P(s^+>s^-)+\frac{1}{2}P(s^+=s^-)$",
    "boot": r"$\hat{\theta}^{*b}=\theta(\{i_1^{*b},\ldots,i_n^{*b}\})$",
    "r2": r"$R^2=1-\sum_t(y_t-\hat{y}_t)^2/\sum_t(y_t-\bar{y})^2$",
}

EQ_NOTES = [
    ("rng", "xorshift64*, шаг генератора. состояние x обновляется тремя сдвигами и xor; начальное состояние получает splitmix64 из сида. реализация: src/rng.c."),
    ("rng_mul", "выходное слово умножается на 2685821657736338717 по модулю 2^64; равномерное число берётся из старших 53 бит."),
    ("polar", "метод марсалья для нормального распределения. пара u, v повторяется, пока точка не попадёт в единичный круг; s это квадрат радиуса."),
    ("normal", "два независимых нормальных числа из одной пары. второе сохраняется как spare и возвращается при следующем вызове."),
    ("poisson", "пуассоновское число событий, алгоритм кнута. произведение равномерных чисел сравнивается с exp(-lambda); ограничение k < 100 защищает от зацикливания."),
    ("lognorm", "интервал между действиями. b это p12, sigma зависит от p13, p14, p19 и множителя chaos c; F_t это общий 1/f фактор дня."),
    ("ar", "сумма трёх ar(1) процессов с phi из p21, 0.95 и 0.99; экспонента от суммы даёт медленный 1/f множитель F_t."),
    ("natural", "естественные параметры. mu_k это середина диапазона, sigma_k=(H_k-L_k)/6; z_k и общий фактор g_c(k) дают корреляцию внутри группы признаков, clip удерживает значение в диапазоне."),
    ("mask", "скаляр маски. среднее 24 нормализованных параметров пациента; для g6 и g7 он вычисляется из собственных параметров до переключения."),
    ("affine", "интенсивная маска. все 24 параметра становятся аффинной функцией одного s; для g3 и g5 s равномерен, поэтому профили шаблонны."),
    ("idu", "расстояние до естественного многообразия. x это 20-компонентный whitened pca вектор, x_(r) это r-е ближайшее окно естественной обучающей выборки, W это матрица отбеливания."),
    ("plurality", "потолок top1 при точном совпадении профилей. C(i) это множество окон с тем же округлённым вектором, n_i,p число окон пациента p в C(i), N общее число окон."),
    ("cohen", "стандартизованная разность средних. s_p это объединённое стандартное отклонение; для парных сравнений используется d_z."),
    ("dz", "парная стандартизованная разность: среднее индивидуальных разностей, делённое на их стандартное отклонение."),
    ("holm", "поправка holm для семейства m тестов. p_(k) это k-й упорядоченный p-value; adj-значения монотонны и ограничены единицей."),
    ("pr", "participation ratio и доля первой компоненты. lambda_j это объяснённая дисперсия pca; порог h6 был pr < 2.0 и ell_1 > 0.80."),
    ("auc", "площадь под roc. вероятность, что положительный score выше отрицательного, плюс половина вероятности совпадения."),
    ("boot", "кластерный bootstrap по пациентам. b-я репликация resample-ит пациентов с возвращением, метрика пересчитывается на реплике; ci это перцентили 2.5 и 97.5."),
    ("r2", "within-patient коэффициент детерминации. y_t это наблюдённое значение, y-hat_t прогноз, y-bar среднее пациента; отрицательное значение означает хуже среднего."),
]

STATUS_ROWS = [
    ("детерминированная маска аномальна", "подтверждено", "idu_nat 17.096 против 3.825, d=-13.16", "синтетика, g3 конструкт", "ok"),
    ("детерминированная маска не уникальна", "подтверждено", "idu_cohort 0.065, 58 профилей, потолок 0.3867", "синтетика", "ok"),
    ("сильный парадокс rank-1 уникальности", "опровергнуто", "pr 2.380, lambda1 0.500", "для g3 при равномерном s", "no"),
    ("g2 против g3 монотонно", "не установлено", "per-model p расходятся, rf tie", "классы и модели различаются", "mid"),
    ("маска уничтожает идентичность", "опровергнуто", "pre-to-post 0.005, post-only g6 0.085", "сильная форма; перенос сломан, информация остаётся", "no"),
    ("стохастическая маска скрывает личность", "подтверждено", "open-set eer 0.455 против 0.497 у g4", "в маскированной области; маска обнаружима по action_entropy", "ok"),
    ("прогноз ограничен горизонтом", "не поддержано", "0.496 против 0.481, p=0.172, r2 отрицательный", "underpowered", "mid"),
    ("g4 контроль на уровне шанса", "неопределённо", "0.025 и 0.0075 на двух сидах", "один сид выше порога", "gray"),
    ("уникальность предсказывает идентификацию", "поисковый", "consensus 0.275, per-model 0.167-0.211", "слабый и нестабильный эффект", "info"),
    ("артефакт воспроизводим", "локально подтверждено", "sha256, manifest, tests", "локальный compiler и libm, без doi", "ok"),
]

NEGATIVES = [
    ("rank-1 на наблюдаемых признаках", "participation ratio 2.380 и доля первой компоненты 0.500 при порогах 2.0 и 0.80. латентная конструкция g3 одномерна по s, но 51 наблюдаемый признак нелинейны и квантованы."),
    ("строгий порядок g1 > g2 > g3", "logreg и mlp дают g2 > g3 (p_holm 3.3e-5 и 4.7e-8), hist gradient boosting даёт g3 > g2 (p_holm 2.3e-5), random forest не различает (p=0.112). среднее по моделям p=0.870 не является тестом неразличимости."),
    ("маска уничтожает идентичность", "pre-to-post перенос падает до chance у обеих масок, но post-only g6 даёт 0.085, то есть 17x chance через 17 шаблонов, а g7 даёт 0.005-0.020. маска ломает перенос, а не стирает информацию."),
    ("прогноз ограничен горизонтом", "chaos accuracy 0.496 [0.472, 0.505] и 0.481 [0.448, 0.488], парная разность 0.0204 [-0.0049, 0.0446], p=0.172, dz=0.160. within-patient r2 отрицательный, тест underpowered."),
    ("g4 является чистым контролем на уровне шанса", "rf 0.025 [0.010, 0.043] на первом сиде и 0.0075 [0.000, 0.018] на втором; patient-level p_holm 0.087 по пяти моделям и 0.348 по семи тестам. статус h7 неопределённый."),
]

TABLES = [
    ("1", "24 скрытых параметра генератора."),
    ("2", "когорта и основные метрики."),
    ("3", "поведенческие признаки по группам, mean ± sd."),
    ("4", "closed-set accuracy, mean [ci95], кластерный bootstrap по пациентам."),
    ("4b", "per-model g2 против g3, patient level."),
    ("5", "прогноз next-day, accuracy = 1 - mae/mean."),
    ("6", "top 10 permutation importance для g1."),
    ("7", "вердикты h1..h7."),
    ("7b", "open-set verification, auc и eer."),
    ("8", "within-subject switch."),
    ("9", "артефакты и их содержание."),
]

FIGURES = [
    ("1", FIG_CAPTIONS["1"]),
    ("2", FIG_CAPTIONS["2"]),
    ("3", FIG_CAPTIONS["3"]),
    ("4", FIG_CAPTIONS["4"]),
    ("5", FIG_CAPTIONS["5"]),
    ("6", FIG_CAPTIONS["6"]),
    ("7", FIG_CAPTIONS["7"]),
    ("8", FIG_CAPTIONS["8"]),
]


def ensure_fonts() -> None:
    FONT_DIR.mkdir(parents=True, exist_ok=True)
    fallback = ROOT / "tmp_check" / "report_assets" / "fonts"
    for name, (folder, remote) in FONT_FILES.items():
        target = FONT_DIR / name
        if target.exists() and target.stat().st_size > 1000:
            continue
        if (fallback / name).exists():
            shutil.copyfile(fallback / name, target)
            continue
        url = f"https://raw.githubusercontent.com/google/fonts/main/ofl/{folder}/{remote}"
        print(f"fonts: download {name}")
        urllib.request.urlretrieve(url, target)
        if target.stat().st_size < 1000:
            raise RuntimeError(f"font download failed: {name}")


def font_css() -> str:
    parts = []
    for family, name, weight, style in FONT_CSS:
        data = base64.b64encode((FONT_DIR / name).read_bytes()).decode("ascii")
        parts.append(
            '@font-face{font-family:"%s";src:url(data:font/ttf;base64,%s) format("truetype");'
            "font-weight:%d;font-style:%s;}" % (family, data, weight, style)
        )
    return "\n".join(parts)


def render_equations() -> dict[str, str]:
    EQ_DIR.mkdir(parents=True, exist_ok=True)
    paths: dict[str, str] = {}
    for key, tex in TEX.items():
        path = EQ_DIR / f"{key}.svg"
        fig = plt.figure(figsize=(10.0, 1.1))
        fig.text(0.01, 0.5, tex, fontsize=15.5, va="center", ha="left", color="#1d1a22")
        fig.savefig(
            path,
            bbox_inches="tight",
            pad_inches=0.035,
            transparent=True,
            format="svg",
        )
        plt.close(fig)
        paths[key] = data_uri(path)
    return paths


def data_uri(path: Path) -> str:
    suffix = path.suffix.lower()
    mime = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".svg": "image/svg+xml",
    }[suffix]
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def equation_html(eqs: dict[str, str]) -> str:
    out = []
    for i, (key, note) in enumerate(EQ_NOTES, start=1):
        out.append(
            '<div class="eq-block">'
            '<div class="equation">'
            f'<img src="{eqs[key]}" alt="формула {i}">'
            f'<span class="eqnum">({i})</span>'
            "</div>"
            f'<p class="eq-note">{html.escape(note)}</p>'
            "</div>"
        )
    return "\n".join(out)


def figure_list_html() -> str:
    items = "\n".join(
        f'<li><a href="#fig-{num}"><span class="item-label">рисунок {num}.</span> '
        f"{html.escape(cap.split('.')[0])}</a></li>"
        for num, cap in FIGURES
    )
    return f"<ul>{items}</ul>"


def table_list_html() -> str:
    items = "\n".join(
        f'<li><a href="#tab-{num}"><span class="item-label">таблица {num}.</span> '
        f"{html.escape(cap)}</a></li>"
        for num, cap in TABLES
    )
    return f"<ul>{items}</ul>"


def toc_html(tokens: list[dict]) -> str:
    out = ['<ul class="toc-list">']

    def walk(items: list[dict], parent_level: int = 0) -> None:
        for item in items:
            level = int(item.get("level", 2))
            if level > 3:
                if item.get("children"):
                    walk(item["children"], level)
                continue
            cls = "lvl2" if level == 2 else "lvl3"
            out.append(
                f'<li class="{cls}"><a href="#{item["id"]}">{item["name"]}</a></li>'
            )
            if item.get("children"):
                walk(item["children"], level)

    walk(tokens)
    out.append("</ul>")
    return "\n".join(out)


def cover_html() -> str:
    return """
<section class="cover">
  <table class="cover-topline"><tr>
    <td><span class="cover-mark">eidolon</span></td>
    <td class="right">исследовательский артефакт · ревизия 1</td>
  </tr></table>
  <div class="cover-main">
    <p class="cover-kicker">отчёт для научного руководителя</p>
    <h1 class="cover-title">аномальность<br>без уникальности</h1>
    <p class="cover-sub">детерминированная маскировка в синтетической когорте 600 пациентов: генератор, измерения, отрицательные результаты и границы воспроизводимости</p>
    <div class="cover-rule"></div>
    <table class="cover-stats">
      <tr>
        <td><div class="cover-num">600</div><div class="cover-label">виртуальных пациентов</div></td>
        <td><div class="cover-num">90</div><div class="cover-label">дней наблюдения</div></td>
        <td><div class="cover-num">1 991 067</div><div class="cover-label">событий</div></td>
        <td><div class="cover-num">51</div><div class="cover-label">поведенческий признак</div></td>
      </tr>
    </table>
  </div>
  <div class="cover-foot">
    <div><b>31 октября 2026</b> · проект eidolon · preprint draft, not peer reviewed</div>
    <div>sha256 основной когорты: <span style="font-family:'PT Mono';font-size:6.8pt">7841bd667c35ee437eea9d1c58016990c081ed022d8f042389fb356b487ce1a9</span></div>
    <div>подготовлено при участии ии; декларация и границы воспроизводимости внутри</div>
  </div>
</section>
"""


def summary_html() -> str:
    return """
<section class="frontpage">
  <h1 class="front-title">резюме для научного руководителя</h1>
  <p class="front-lead">отчёт фиксирует проверку гипотезы о парадоксе детерминированной анонимности в синтетической когорте 600 виртуальных пациентов. работа доведена до воспроизводимого артефакта: генератор на c99, 51 признак, пять моделей, восемь рисунков, одиннадцать таблиц, манифест и гейты. сильная гипотеза не подтверждена. подтверждена более узкая формулировка: детерминированная маскировка делает профиль аномальным и легко обнаружимым, но не уникальным.</p>

  <table class="cards">
    <tr>
      <td><div class="card"><div class="card-num">17.096</div><div class="card-label">idu_nat группы g3 против 3.825 у g1: расстояние до естественного многообразия</div></div></td>
      <td><div class="card"><div class="card-num">0.065</div><div class="card-label">idu_cohort группы g3 против 3.858 у g1: уникальность внутри когорты падает</div></div></td>
      <td><div class="card"><div class="card-num">58</div><div class="card-label">уникальных векторов g3 на 600 тестовых окон, максимальная коллизия 16</div></div></td>
    </tr>
    <tr>
      <td><div class="card"><div class="card-num">0.387</div><div class="card-label">top1 g3 у random forest, ровно потолок 58/150; top5 достигает 1.000</div></div></td>
      <td><div class="card"><div class="card-num">0.100</div><div class="card-label">top1 группы g5 с теми же параметрами и натуральным эмиттером</div></div></td>
      <td><div class="card"><div class="card-num">0.005</div><div class="card-label">pre-to-post перенос после маски против 0.751 у natural control</div></div></td>
    </tr>
  </table>

  <h2 style="margin-top:3mm">главный результат</h2>
  <p>детерминированная маска g3 уходит от естественного многообразия и сжимается в 58 повторяющихся векторов. потолок точности при точном совпадении шаблона равен 58/150=0.3867, и две модели упираются в него. стохастическая g5 с теми же параметрами и натуральным эмиттером даёт 600 из 600 уникальных профилей, anomaly auc 0.629 и top1 0.100. коллапс связан с детерминированным квантованным эмиттером, а не с интенсивностью маскировки как таковой.</p>
  <p>within-subject переключение подтверждает механизм. natural control сохраняет перенос 0.751, обе маски ломают его до 0.005 и 0.004 при chance 0.005. внутри маскированной области g6 оставляет 17 шаблонов и 0.085, то есть 17x chance, а g7 оставляет 800 уникальных профилей и 0.005-0.020. маска разрушает перенос, но не стирает информацию: остаточная идентифицируемость держится на шаблоне и концентрации масок.</p>

  <div class="callout">
    <div class="callout-title">что подтверждено</div>
    <p>рост аномальности в детерминированном режиме, падение идентифицируемости относительно g1 и малая связь уникальности с идентифицируемостью внутри g1: rho 0.275 [0.151, 0.394], r2 0.076. эффект слабый и нестабильный по моделям.</p>
  </div>

  <div class="callout warn">
    <div class="callout-title">что опровергнуто</div>
    <p>rank-1 на наблюдаемых признаках: pr 2.380, lambda1 0.500 при порогах 2.0 и 0.80. строгий порядок g1 &gt; g2 &gt; g3: per-model тесты разнонаправлены. сильная формулировка о том, что маска уничтожает идентичность, не подтверждена: post-only g6 даёт 0.085. ограничение прогноза горизонтом: разность 0.0204, p=0.172, тест underpowered.</p>
  </div>

  <div class="callout">
    <div class="callout-title">чего работа не утверждает</div>
    <p>внешней валидности на реальных пациентах, кросс-машинного битвайз реплея, подтверждения h5 и h7, новизны без систематического обзора, формального рецензирования. публичный doi, авторские метаданные и депозит не оформлены.</p>
  </div>
</section>
"""


def status_html() -> str:
    rows = []
    for claim, status, evidence, boundary, cls in STATUS_ROWS:
        rows.append(
            f"<tr><td>{html.escape(claim)}</td>"
            f'<td><span class="pill {cls}">{html.escape(status)}</span></td>'
            f"<td>{html.escape(evidence)}</td>"
            f"<td>{html.escape(boundary)}</td></tr>"
        )
    negs = "\n".join(
        f"<li><b>{html.escape(title)}.</b> {html.escape(body)}</li>"
        for title, body in NEGATIVES
    )
    return f"""
<section class="frontpage">
  <h1 class="front-title">статус утверждений</h1>
  <p class="small">таблица собрана из раздела honesty check в paper/DRAFT.md. статус относится к синтетической когорте и указанным тестам; он не переносится на реальные данные без отдельного исследования.</p>
  <table class="status-table">
    <thead><tr><th>утверждение</th><th>статус</th><th>основание</th><th>граница</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>

  <h2>каталог опровержений</h2>
  <p class="small">отрицательные результаты не спрятаны в приложении. каждый пункт сформулирован как отказ от более сильной версии исходной гипотезы и подкреплён числом из results/.</p>
  <ol class="neg-list">{negs}</ol>
</section>
"""


def provenance_html() -> str:
    return """
<section class="frontpage">
  <h1 class="front-title">провенанс, границы, декларация об ии</h1>

  <h3 style="margin-top:1mm">провенанс артефакта</h3>
  <table class="prov">
    <tr><td>коммит</td><td><span class="mono">a307c68</span> плюс рабочее дерево: правки подписей таблиц 7b и 8, легенды рисунка 6 и сборки pdf; числа и данные не менялись</td></tr>
    <tr><td>тег</td><td><span class="mono">v1.3.0</span> на коммите <span class="mono">a13a256</span></td></tr>
    <tr><td>бинарник</td><td><span class="mono">sha256 04449ca1fe428c686a877a90c96026378add130da17b350b0c0ae86f312cc569</span></td></tr>
    <tr><td>когорта</td><td><span class="mono">sha256 7841bd667c35ee437eea9d1c58016990c081ed022d8f042389fb356b487ce1a9</span></td></tr>
    <tr><td>манифест</td><td><span class="mono">results/manifest.txt</span>, 165 строк, сгенерирован 2026-10-31T00:54:26Z; <span class="mono">paper/report/</span> исключён как производная вёрстка</td></tr>
    <tr><td>релиз</td><td><span class="mono">release/eidolon-v1.3.0.tar.gz</span>, <span class="mono">sha256 7127db326c2503de8057d1bf874917473a8e056ae8528acc23464dff8d12483d</span>; собран до файлов воркфлоу статьи, pdf в него не входит</td></tr>
    <tr><td>гейты</td><td><span class="mono">make check</span>: DETERMINISM_PASS, G5_ISOLATION_PASS; <span class="mono">make paper</span>: PAPER_GATE_PASS, 2 файла, 18 чисел, 5 статусов</td></tr>
  </table>

  <h3>границы воспроизводимости</h3>
  <div class="callout warn">
    <p>bitwise replay проверен локально на одном компиляторе и одной libm. кросс-машинная эквивалентность не заявляется. python окружение зафиксировано версиями, но не hash-locked wheels.</p>
    <p>пререгистрация self-reported, без внешней метки времени. публичного doi, депозита и авторских метаданных нет. формальное рецензирование не проводилось.</p>
    <p>в refs/ лежит предыдущая рукопись с той же гипотезой. её статус и права нужно раскрыть до подачи; в отчёте она не цитируется как опубликованная работа.</p>
    <p>релизный архив v1.3.0 предшествует файлам paper/workflow. перед подачей манифест, релиз и тег нужно пересобрать после фиксации текста.</p>
  </div>

  <h3>декларация об использовании ии</h3>
  <p class="small">проект eidolon выполнен иначе, чем proteus: инженерия, анализ и текст подготовлены ии-агентами под прямым управлением человека. это заявлено прямо, потому что скрывать было бы нечестно.</p>
  <table class="status-table">
    <thead><tr><th>кто</th><th>что сделал</th></tr></thead>
    <tbody>
      <tr><td>агенты</td><td>генератор на c99, пайплайн признаков, моделей, прогноза и статистики, тесты, инструменты сборки; прогон всех измерений; драфт препринта; два круга adversarial review и методологический аудит, которые привели к опровержению сильной гипотезы.</td></tr>
      <tr><td>человек</td><td>постановка задачи, исходная гипотеза и исходные документы, размеры групп, сиды, приёмка или отклонение каждой ревизии, ответственность за весь контент.</td></tr>
      <tr><td>ии не делал</td><td>не работал с реальными пациентами и персональными данными, не выбирал пороги post hoc ради желаемого знака, не удалял неудобные результаты.</td></tr>
    </tbody>
  </table>
  <p class="small">единственный ответственный за содержание человек. контакт и citation data ожидают заполнения в CITATION.cff.</p>
</section>
"""


def paper_head_html() -> str:
    return """
<div class="paper-head">
  <p class="paper-kicker">preprint draft · не прошло рецензирование · проект eidolon</p>
  <h1 class="paper-title">аномальность без уникальности</h1>
  <p class="paper-sub">детерминированная маскировка в синтетической когорте 600 пациентов</p>
  <p class="paper-meta">90 дней · 24 скрытых параметра · 1 991 067 событий · 51 признак · 5 моделей · сид 20261030</p>
</div>
"""


def colophon_html() -> str:
    return """
<section class="frontpage">
  <h1 class="front-title">колофон</h1>
  <p>отчёт собран из <code>paper/preprint.md</code> без изменения чисел и вердиктов. добавлены титул, служебное резюме, статус утверждений, провенанс, список рисунков и таблиц, а также раздел 3.9 с формальными определениями, которых в препринте не было в явном виде.</p>
  <p>типографика: pt serif для основного текста, pt sans для заголовков и таблиц, pt mono для идентификаторов. шрифты распространяются по лицензии sil ofl 1.1, копии лицензий лежат в <code>paper/report/.cache/fonts/</code>. вёрстка: weasyprint 65.1, формулы: matplotlib mathtext, stix.</p>
  <p>лицензии артефакта: код mit, статья и синтетические данные cc by 4.0, см. <code>LICENSE</code>, <code>LICENSE-CC-BY-4.0</code>, <code>NOTICE</code>. исходные документы в <code>refs/</code> не распространяются.</p>
  <p>дата сборки: 31 октября 2026. pdf sha256 записан рядом с файлом в <code>.sha256</code>. исходный коммит: <code>a307c68</code>.</p>
  <div class="callout">
    <div class="callout-title">как читать отчёт</div>
    <p>разделы 1-3 описывают постановку, генератор и метрики. раздел 4 содержит все результаты и вердикты. разделы 5-7 обсуждают механизм, ограничения и практический вывод. служебная часть в начале предназначена для быстрой проверки: резюме, статус утверждений, провенанс и границы.</p>
  </div>
</section>
"""


def strip_front_matter(text: str) -> str:
    marker = "## аннотация"
    idx = text.find(marker)
    if idx < 0:
        raise RuntimeError("preprint: no '## аннотация' marker")
    return text[idx:]


def add_appendix_table_caption(text: str) -> str:
    marker = "## приложение b. артефакты\n\n| файл | содержание |"
    replacement = (
        "## приложение b. артефакты\n\n"
        "**таблица 9. артефакты и их содержание.**\n\n"
        "| файл | содержание |"
    )
    if marker not in text:
        raise RuntimeError("preprint: appendix b table marker not found")
    return text.replace(marker, replacement, 1)


def insert_equations(text: str, eqs: dict[str, str]) -> str:
    marker = "## 4. результаты"
    if marker not in text:
        raise RuntimeError("preprint: no section 4 marker")
    block = (
        "### 3.9 формальный аппарат\n\n"
        "ниже собраны определения, на которых держатся числа отчёта. формулы приведены "
        "в том виде, в каком они реализованы в `src/` и `python/`; нумерация (1)-(19) "
        "используется только в этом разделе.\n\n"
        + equation_html(eqs)
        + "\n\n"
    )
    return text.replace(marker, block + marker, 1)


def convert_markdown(text: str) -> tuple[str, list[dict]]:
    md = markdown.Markdown(
        extensions=["tables", "fenced_code", "toc", "sane_lists"],
        extension_configs={"toc": {"permalink": False, "toc_depth": "2-3"}},
    )
    body = md.convert(text)
    return body, md.toc_tokens


def rewrite_images(body: str) -> str:
    def repl(match: re.Match) -> str:
        src = match.group(1)
        if src.startswith("data:"):
            return match.group(0)
        path = (ROOT / "paper" / src).resolve()
        if not path.exists():
            raise RuntimeError(f"image missing: {src} -> {path}")
        return match.group(0).replace(src, data_uri(path))

    return re.sub(r'src="([^"]+)"', repl, body)


def wrap_figures(body: str) -> str:
    pattern = re.compile(
        r'<p><img alt="(рисунок\s+\d+)" src="([^"]+)"\s*/?></p>', re.S
    )

    def repl(match: re.Match) -> str:
        alt, src = match.group(1), match.group(2)
        num = re.search(r"\d+", alt).group(0)
        cap = FIG_CAPTIONS[num]
        return (
            f'<figure id="fig-{num}"><img src="{src}" alt="{alt}">'
            f"<figcaption><b>рисунок {num}.</b> {html.escape(cap)}</figcaption></figure>"
        )

    return pattern.sub(repl, body)


def wrap_tables(body: str) -> str:
    pattern = re.compile(
        r"<p><strong>(таблица\s+\d+[a-z]?\.\s*[^<]*)</strong></p>\s*(<table>.*?</table>)",
        re.S,
    )

    def repl(match: re.Match) -> str:
        cap = match.group(1).strip()
        table = match.group(2)
        num = re.search(r"таблица\s+(\d+[a-z]?)", cap).group(1)
        cls = "text" if num in TABLE_TEXT else ""
        if table.count("<th") >= 6:
            cls = (cls + " wide").strip()
        table = table.replace("<table>", f'<table class="data {cls}">', 1)
        return (
            f'<div class="table-block {cls}" id="tab-{num}">'
            f'<p class="table-caption">{cap}</p>{table}</div>'
        )

    return pattern.sub(repl, body)


def fix_csv_contract(body: str) -> str:
    pattern = re.compile(r"<code>(patient_id,group,.*?)</code>", re.S)

    def repl(match: re.Match) -> str:
        text = match.group(1).replace(",", ",<wbr>")
        return f'<pre class="contract">{text}</pre>'

    return pattern.sub(repl, body, count=1)


def build_html() -> tuple[str, str]:
    ensure_fonts()
    eqs = render_equations()

    text = PREPRINT.read_text(encoding="utf-8")
    text = strip_front_matter(text)
    text = add_appendix_table_caption(text)
    text = insert_equations(text, eqs)
    body, toc_tokens = convert_markdown(text)
    body = rewrite_images(body)
    body = wrap_figures(body)
    body = wrap_tables(body)
    body = fix_csv_contract(body)

    css = font_css() + "\n" + (REPORT / "style.css").read_text(encoding="utf-8")

    document = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>аномальность без уникальности · отчёт eidolon</title>
<meta name="author" content="проект eidolon">
<meta name="description" content="отчёт для научного руководителя: детерминированная маскировка в синтетической когорте 600 пациентов">
<meta name="keywords" content="цифровая анонимность, повторная идентификация, синтетическая когорта, поведенческая биометрия, воспроизводимость">
<style>{css}</style>
</head>
<body>
{cover_html()}
{summary_html()}
{status_html()}
{provenance_html()}
<section class="toc">
  <h1 class="front-title">содержание</h1>
  {toc_html(toc_tokens)}
</section>
<section class="lists">
  <h1 class="front-title">рисунки и таблицы</h1>
  <table><tr>
    <td><h3>рисунки</h3>{figure_list_html()}</td>
    <td><h3>таблицы</h3>{table_list_html()}</td>
  </tr></table>
</section>
<main>
{paper_head_html()}
{body}
</main>
{colophon_html()}
</body>
</html>
"""
    return document, HTML_NAME


def main() -> int:
    BUILD.mkdir(parents=True, exist_ok=True)
    document, html_name = build_html()
    html_path = BUILD / html_name
    html_path.write_text(document, encoding="utf-8")
    print(f"html: {html_path} ({html_path.stat().st_size / 1e6:.2f} MB)")

    from weasyprint import HTML

    pdf_path = BUILD / PDF_NAME
    HTML(string=document, base_url=str(REPORT)).write_pdf(str(pdf_path))
    print(f"pdf: {pdf_path} ({pdf_path.stat().st_size / 1e6:.2f} MB)")

    import hashlib

    digest = hashlib.sha256(pdf_path.read_bytes()).hexdigest()
    (BUILD / (PDF_NAME + ".sha256")).write_text(
        f"{digest}  {PDF_NAME}\n", encoding="utf-8"
    )
    print(f"sha256: {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
