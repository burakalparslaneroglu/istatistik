"""Konu 8 genel uygulaması: kesikli rassal değişken, olasılık fonksiyonu, beklenen değer, varyans ve ortak dağılım.

Ders notlarındaki adımlar (§8.3–§8.14) aynı numaralarla, verisi değiştirilebilir biçimde yazılır. Kesikli sayısal
sütun $X$'in göreli frekansları olasılık fonksiyonu olur (Adım 1–8 ve 12; Adım 4 bu yolu açıkça gösterir). Notlardaki
sabit örnekler veriden türetilir: Adım 2'nin geçersiz tablosu verinin dağılımından kurulur, Adım 6'nın uzun dönem
yorumu dosya sırasıyla birikimli ortalamadır, Adım 8'in ikinci dağılımı aynı ortalamayla kütlesi en küçük ve en büyük
değere taşınmış dağılımdır. İkinci kesikli sütun $Y$ seçilirse ortak dağılım (Adım 9–11) $X$ ve $Y$'den kurulur.
Adım 12'nin birim katkısı ve sabit maliyeti öğrencinin seçtiği değerlerdir. Alternatif örnek kurgusal bir çiçekçinin
100 günlük online siparişleridir. Notlardaki uygulama (``core.labs.konu08``) değişmez.
"""

from __future__ import annotations

import math
from decimal import Decimal
from fractions import Fraction
from functools import cache

import pandas as pd

from core.labs import expr as E
from core.labs import kendi_veri as K
from core.labs.ornek import (
    Case,
    CustomLab,
    Role,
    Setting,
    TopicVariants,
    free_name,
    kesin,
    kesir_ayirt,
    kesir_basamak,
    kesir_esit,
    kesir_isaret,
    kesir_metin,
    kesir_ortak_basamak,
    kesir_sayi,
    kesir_tex,
    kesir_yarimda,
    liste,
    md,
    ondalik,
    ondalik_tex,
    sayilar,
    with_app_values,
)
from core.labs.spec import (
    TOTAL,
    BarChart,
    CellTarget,
    Check,
    CompleteCases,
    CrossTab,
    Derive,
    Event,
    FrequencyTable,
    GroupSummary,
    HeatMap,
    InlineData,
    LabSpec,
    LabStep,
    LineChart,
    NoteRef,
    Scalar,
    ScalarTarget,
    ShowFrame,
    Statistic,
    TableTarget,
)
from core.labs.tables import decimal_places

TITLE = "Kesikli olasılık dağılımlarını, beklenen değeri, varyansı ve ortak dağılımı uygulamak"
KESIKLI, IKINCI = "kesikli", "ikinci"
KATKI, SABIT = "katki", "sabit"
PAIR_FRAME = "ciftler"
MAX_VALUES, MAX_Y_VALUES = 20, 10
MAX_ABS, MAX_DECIMALS = 10 ** 6, 4
EARLY = 10
"""Adım 6: birikimli ortalamanın ilk gözlemlerdeki dalgalanması bu kadar gözlemle gösterilir."""

ALT_DAYS = (
    (0, 0), (3, 1), (3, 2), (2, 2), (2, 1), (4, 4), (2, 2), (2, 2), (3, 2), (2, 2),
    (2, 1), (5, 4), (1, 1), (4, 2), (1, 1), (3, 2), (0, 0), (4, 3), (1, 1), (2, 0),
    (1, 0), (2, 2), (4, 2), (2, 2), (2, 2), (1, 1), (5, 5), (3, 1), (0, 0), (1, 0),
    (2, 2), (3, 3), (4, 2), (4, 3), (1, 1), (3, 2), (1, 1), (0, 0), (3, 3), (3, 3),
    (1, 1), (1, 1), (2, 1), (5, 3), (3, 2), (2, 1), (5, 3), (2, 2), (1, 1), (3, 2),
    (3, 2), (5, 5), (2, 0), (5, 3), (2, 1), (2, 0), (2, 1), (4, 3), (3, 3), (2, 2),
    (5, 4), (1, 1), (5, 4), (4, 4), (3, 2), (4, 3), (3, 1), (0, 0), (1, 1), (3, 1),
    (3, 3), (4, 4), (3, 2), (4, 3), (3, 2), (2, 1), (4, 2), (2, 2), (2, 1), (4, 4),
    (2, 2), (1, 1), (3, 1), (0, 0), (2, 2), (3, 3), (4, 2), (2, 2), (3, 1), (1, 0),
    (2, 1), (3, 3), (2, 2), (1, 0), (1, 0), (0, 0), (3, 3), (2, 1), (0, 0), (4, 3),
)
"""Kurgusal veri: bir çiçekçinin 100 iş günü; her satır bir gün (online sipariş sayısı, aynı gün teslim edilen)."""
ALT_LABELS = {"siparis": "Online sipariş sayısı", "teslim": "Aynı gün teslim edilen"}
ALT_SETTINGS = {KATKI: 150, SABIT: 200}
STORY = (
    "Kurgusal veri: bir çiçekçinin 100 iş gününde gelen online sipariş sayısı ve bunlardan aynı gün teslim "
    "edilenlerin sayısı; her sipariş 150 TL katkı sağlar, günlük sabit maliyet 200 TL."
)


# --- Yardımcılar -------------------------------------------------------------------------

def _scalar(name: str, label: str, decimals: int = 0) -> Check:
    return Check(label, ScalarTarget(name), 0.0, decimals)


def _missing(step: int, title: str, note: str) -> LabStep:
    return LabStep(number=step, title=title, note=NoteRef(note),
                   explanation=("Bu adım için yukarıdaki veri panelinden “İkinci kesikli değişken Y” rolüne bir "
                                "sütun seçin (ör. siparişlerden teslim edilenlerin sayısı)."))


def _blocked(step: int, title: str, note: str, reason: str) -> LabStep:
    return LabStep(number=step, title=title, note=NoteRef(note), explanation=reason)


def _number(value: float) -> int | float:
    """Tam sayı değerli ondalık (3.0) koda ve ekrana tam sayı olarak yazılır."""

    value = float(value)
    return int(value) if value.is_integer() else value


def _exact(value: float) -> Fraction:
    return Fraction(kesin(value))


def _x(value: float) -> str:
    """Değerin düzyazıdaki yazımı (2; 2,5; −1)."""

    return ondalik(kesin(value))


def _xt(value: float) -> str:
    """Değerin matematik ifadesindeki yazımı (2{,}5)."""

    return ondalik_tex(kesin(value))


COLUMN_EXACT = 6
"""Hesaplanan bir tablo sütununda en çok bu kadar ondalıkla tam yazılabilen değerler tam gösterilir."""


def _column_digits(values) -> int:
    """Hesaplanan bir tablo sütununun basamağı, kesin değerlerden; tablo bu basamakla gösterilir
    (``ShowFrame.decimals``) ve metin aynı basamakla anar. Değerlerin hepsi en çok 6 ondalıkla tam yazılabiliyorsa tam (en az 2); değilse en az 4
    basamak ve en küçük değerin 3 anlamlı basamağı (en çok 13 anlamlı basamak), tam yazılabilen değerler yine tam
    (27,281982421875 gibi uzun bir kesin değer ise 4 basamakla). Bu basamakta tam yarımda kalan bir değer varsa bir
    basamak daha."""

    values = list(values)
    places = [next((d for d in range(COLUMN_EXACT + 1) if (value * 10 ** d).denominator == 1), None)
              for value in values]
    exact = [place for place in places if place is not None]
    if len(exact) == len(values):
        digits = max(2, *exact)
    else:
        nonzero = [abs(float(value)) for value in values if value != 0]
        cap = max(0, 12 - math.floor(math.log10(max(nonzero))))
        digits = max([min(cap, max(4, 2 - math.floor(math.log10(min(nonzero))))), *exact])
    digits = min(digits, 15)
    while digits < 15 and any(kesir_yarimda(value, digits) for value in values):
        digits += 1
    return digits


def _scale(value: Fraction) -> int:
    """Veriden hesaplanan büyüklüğün (ortalama, varyans, kovaryans) basamağı: en çok 4 basamakla tam yazılabiliyorsa
    tam, değilse 4; küçük değerlerde en az 3 anlamlı basamak (en çok 12). Böylece 0,0025 adımlı bir değişkenin
    varyansı (≈ 0,0000042) metinde ve metrikte 0 görünmez. Büyük değerlerde en çok 13 anlamlı basamak: 10¹¹
    düzeyindeki bir varyansın son basamakları kayan nokta gürültüsüdür (o basamakta tam yarım varsa bir basamak
    eksik)."""

    if value == 0:
        return kesir_basamak(value)
    magnitude = math.floor(math.log10(abs(float(value))))
    digits = kesir_basamak(value, min(12, max(4, 2 - magnitude)))
    cap = max(0, 12 - magnitude)
    if digits > cap:
        scaled = abs(value) * 10 ** (cap + 1)
        digits = cap - 1 if cap > 0 and scaled.denominator == 1 and scaled.numerator % 10 == 5 else cap
    return digits


def _eq(value: Fraction, digits: int | None = None) -> str:
    digits = kesir_basamak(value) if digits is None else digits
    return f"{kesir_isaret(value, digits)} {kesir_tex(value, digits)}"


def _plain(value: Fraction, digits: int | None = None) -> str:
    """Düzyazıda "= 0,35" ya da "≈ 0,3333"."""

    digits = kesir_basamak(value) if digits is None else digits
    return f"{kesir_esit(value, digits)} {kesir_sayi(value, digits)}"


def _xp(value: float) -> str:
    """Çıkarmadaki değer, matematik ifadesinde: negatifse parantez içinde (μ − (−3))."""

    text = _xt(value)
    return f"({text})" if float(value) < 0 else text


def _table3(value: Fraction) -> str:
    """Üç basamaklı tablodaki olasılık, düzyazıda: tablonun kayan noktalı değeri nasıl yuvarlıyorsa öyle
    (3/7 ≈ 0,429)."""

    return f"{kesir_esit(value, 3)} {ondalik(Decimal(f'{float(value):.3f}'))}"


def _root(value: Fraction) -> Fraction | None:
    """Kesrin kesin karekökü: pay ve payda tam kareyse kesir, değilse ``None`` (√0,25 = 0,5; √2 kesir değildir)."""

    if value < 0:
        return None
    top, bottom = math.isqrt(value.numerator), math.isqrt(value.denominator)
    if top * top == value.numerator and bottom * bottom == value.denominator:
        return Fraction(top, bottom)
    return None


def _root_text(square: Fraction, sign: int = 1, digits: int = 3) -> tuple[str, int]:
    """Karekökle bulunan değerin (σ, ρ) düzyazıdaki yazımı ve metriğin basamağı. Basamak en az ``digits``; küçük
    değerlerde en az 3 anlamlı basamak (en çok 12). Kesin bir kesirse "= 0,5" (tam yarımda bir basamak daha), değilse
    metrik gibi "≈ 0,707"."""

    value = sign * math.sqrt(float(square))
    if value != 0:  # küçük değerlerde en az 3 anlamlı basamak (en çok 12)
        digits = min(12, max(digits, 2 - math.floor(math.log10(abs(value)))))
    root = _root(square)
    if root is not None:
        root *= sign
        places = kesir_basamak(root, digits, digits)
        return f"{kesir_esit(root, places)} {kesir_sayi(root, places)}", places
    return f"≈ {ondalik(Decimal(f'{value:.{digits}f}'))}", digits


def _linear(a: int, b: int, variable: str, tex: bool = False) -> str:
    """aX − b yazımı: a = 1 iken yalnız X, b = 0 iken sabit terim yok (150X − 200; X − 200; 150X)."""

    head = variable if a == 1 else f"{a}{variable}"
    if b == 0:
        return head
    return f"{head} {'-' if tex else '−'} {b}"


def _pair_text(px: float, py: float) -> str:
    """(x, y) çiftinin düzyazıdaki yazımı; ondalık virgüllü bir değer varsa ayırıcı noktalı virgül (2,5; 1)."""

    first, second = _x(px), _x(py)
    return f"({first}{'; ' if ',' in first + second else ', '}{second})"


def _pair_tex(px: float, py: float) -> str:
    first, second = _xt(px), _xt(py)
    return f"({first}{'; ' if '{,}' in first + second else ', '}{second})"


def _settings(case: Case) -> dict[str, int]:
    chosen = dict(ALT_SETTINGS)
    chosen.update(case.extra.get("settings") or {})
    return chosen


def _distribution(values: pd.Series) -> dict:
    """Ampirik dağılım: değerler (küçükten büyüğe), sayılar, kesin olasılıklar ve momentler."""

    counts = values.value_counts().sort_index()
    n = int(counts.sum())
    points = tuple(_number(value) for value in counts.index)
    f = {point: Fraction(int(count), n) for point, count in zip(points, counts)}
    exact = {point: _exact(point) for point in points}
    mean = sum((exact[point] * f[point] for point in points), Fraction(0))
    variance = sum(((exact[point] - mean) ** 2 * f[point] for point in points), Fraction(0))
    top = max(f.values())
    modes = [point for point in points if f[point] == top]
    return {"points": points, "counts": {point: int(count) for point, count in zip(points, counts)}, "n": n,
            "f": f, "exact": exact, "mean": mean, "variance": variance, "modes": modes}


def _context(case: Case) -> dict:
    x = case.roles[KESIKLI]
    dist = _distribution(case.data[x].astype(float))
    taken = set(case.data.columns) | set(case.labels)
    names = {}
    for key in ("sayi", "f", "bilinen", "en_kucuk_mu", "en_buyuk_mu", "g", "olay", "xf", "sira", "birikimli",
                "sapma_kare", "agirlikli_kare", "f_B", "xf_B", "kare_B", "agirlik", "x_f", "y_f", "xy_f", "capraz",
                "x_kare", "y_kare", "X_hucre", "Y_hucre", "hucre", "kar", "kar_f", "zarar"):
        names[key] = free_name(key, taken)
        taken.add(names[key])
    return {"x": x, "label": case.label(KESIKLI), "dist": dist, "names": names, "n": len(case.data),
            "settings": _settings(case), "f_digits": kesir_ortak_basamak(*dist["f"].values())}


def _pair(case: Case, ctx: dict) -> dict | None:
    """Adım 9–11'in iki kesikli değişkeni: ikinci sütunda değeri olan gözlemler."""

    if not case.has(IKINCI):
        return None
    x, y = ctx["x"], case.roles[IKINCI]
    data = case.data.dropna(subset=[x, y]).reset_index(drop=True)
    if len(data) == len(case.data):
        frame, load = case.frame, ()
    else:
        frame = PAIR_FRAME
        load = (CompleteCases(PAIR_FRAME, case.frame, (x, y), "X ve Y'si olan gözlemler"),)
    result = {"y": y, "label": case.label(IKINCI), "frame": frame, "load": load, "n": len(data),
              "skipped": len(case.data) - len(data)}
    if len(data) < 2 or data[x].nunique() < 2 or data[y].nunique() < 2:
        result["problem"] = ("X ve Y'si olan gözlemlerde iki değişkenin de en az iki farklı değeri olmalı; ortak "
                             "dağılım, kovaryans ve korelasyon bu veriyle kurulamaz.")
        return result
    xs, ys = data[x].astype(float), data[y].astype(float)
    dist_x, dist_y = _distribution(xs), _distribution(ys)
    pairs = pd.Series(list(zip((_number(value) for value in xs), (_number(value) for value in ys)))).value_counts()
    n = len(data)
    joint = {pair: Fraction(int(count), n) for pair, count in pairs.items()}
    top = max(joint.values())
    cells = sorted(pair for pair, value in joint.items() if value == top)  # eşitlikte hepsi
    cell = cells[0]
    ex, ey = dist_x["mean"], dist_y["mean"]
    exy = sum((_exact(px) * _exact(py) * value for (px, py), value in joint.items()), Fraction(0))
    covariance = exy - ex * ey
    independent = all(joint.get((px, py), Fraction(0)) == dist_x["f"][px] * dist_y["f"][py]
                      for px in dist_x["points"] for py in dist_y["points"])
    result.update({"dist_x": dist_x, "dist_y": dist_y, "joint": joint, "cell": cell, "cells": cells, "exy": exy,
                   "covariance": covariance, "independent": independent})
    return result


# --- Adımlar -------------------------------------------------------------------------------

def _value_list(points: tuple) -> str:
    """Olası değerler: sekize kadar tek tek, daha fazlasında en küçüğü ve en büyüğü (aralar düzenli olmayabilir; "0, 1,
    …, 30" yazımı aradaki bütün değerleri ima ederdi)."""

    if len(points) > 8:
        return f"en küçüğü {_x(points[0])}, en büyüğü {_x(points[-1])}"
    return sayilar([_x(point) for point in points])


def _step1(case: Case, ctx: dict) -> LabStep:
    dist, names, x = ctx["dist"], ctx["names"], ctx["x"]
    mode = dist["modes"][0]
    f_mode = dist["f"][mode]
    digits = ctx["f_digits"]
    lead = case.extra.get("read_text") or f"Dosyanızdaki {dist['n']} gözlem okunur."
    if len(dist["modes"]) == 1:
        highest = f"en yüksek sütun x = {_x(mode)} değerindedir"
    else:
        highest = f"en yüksek sütunlar x = {sayilar([_x(point) for point in dist['modes']])} değerlerindedir"
    return LabStep(
        number=1,
        title="Olasılık fonksiyonu: f(x) = P(X = x)",
        note=NoteRef("8.3", objects=("Tablo 8.1", "Şekil 8.3")),
        explanation=(
            f"{lead} Rastgele seçilen bir gözlemin “{md(ctx['label'])}” değeri $X$ olsun; $X$'in {len(dist['points'])} "
            f"olası değeri vardır ({_value_list(dist['points'])}). Bu uygulamada olasılık fonksiyonu verinin göreli "
            "frekanslarıdır: $f(x) = P(X = x)$, $x$ değerini alan gözlemlerin payıdır (Adım 4 bu yolu ayrıntılı "
            "gösterir). Tablonun her satırı bir olası değer, o değeri alan gözlem sayısı ve değerin olasılığıdır."
        ),
        operations=(
            *case.load,
            Statistic(case.frame, x, "count", "n_veri", "Gözlem sayısı n", decimals=0),
            GroupSummary(case.frame, x, ((names["sayi"], x, "count"),), "dagilim", dist["points"], decimals=0,
                         as_frame=True),
            Derive("dagilim", names["f"], E.div(E.var(names["sayi"]), E.ref("n_veri")),
                   "f(x) = P(X = x): x değerini alan gözlemlerin payı"),
            ShowFrame("dagilim", (x, names["sayi"], names["f"]), "Olasılık fonksiyonu: değer, gözlem sayısı ve f(x)",
                      decimals=((names["f"], digits),)),
            BarChart("dagilim", names["f"], f"{ctx['label']}, x", "f(x) = P(X = x)", "Olasılık dağılımı",
                     x=x, decimals=min(digits, 3)),
            Statistic("dagilim", names["f"], "value", "f_mod", f"f({_x(mode)}) = P(X = {_x(mode)})",
                      where=(x, mode), decimals=kesir_basamak(f_mode)),
        ),
        checks=(
            _scalar("n_veri", "Gözlem sayısı n"),
            _scalar("f_mod", f"f({_x(mode)}) = P(X = {_x(mode)})", kesir_basamak(f_mode)),
        ),
        takeaway=(
            f"Rastgele seçilen bir gözlemin değerinin tam {_x(mode)} olma olasılığı {kesir_metin(f_mode)}. Sütun "
            f"grafiğinde yatay eksen olası değerleri, sütun yüksekliği olasılıklarını gösterir; {highest}. En olası "
            "değer ile beklenen değer aynı kavram değildir; beklenen değer Adım 5'te hesaplanır (§8.3)."
        ),
    )


def _step2(case: Case, ctx: dict) -> LabStep:
    dist, names, x = ctx["dist"], ctx["names"], ctx["x"]
    points = dist["points"]
    low, high = points[0], points[-1]
    f_high = dist["f"][high]
    known = 1 - f_high
    f, g = names["f"], names["g"]
    g_low = dist["f"][low] + 2 * f_high
    digits = ctx["f_digits"]
    g_digits = max(digits, kesir_basamak(g_low))
    others = [f"f({_xt(point)})" for point in points[:-1]]
    if len(others) == 1:
        known_terms = others[0]
    elif len(others) <= 4:
        known_terms = "(" + " + ".join(others) + ")"
    else:  # aralar düzenli olmayabilir: "f(0) + ⋯ + f(30)" aradaki bütün değerleri ima ederdi
        known_terms = f"\\sum_{{x < {_xt(high)}}} f(x)"
    return LabStep(
        number=2,
        title="Geçerli bir olasılık dağılımının koşulları",
        note=NoteRef("8.4", objects=("Şekil 8.4",)),
        explanation=(
            "Kesikli bir olasılık fonksiyonu iki koşulu birlikte sağlamalıdır: bütün $x$ değerleri için "
            "$f(x) \\geq 0$ ve $\\sum_x f(x) = 1$. Bir olasılık eksik bırakıldığında ikinci koşuldan bulunur: en "
            f"büyük değerin olasılığı bilinmeseydi $P(X = {_xt(high)}) = 1 - {known_terms}$ olurdu. Karşı örnek "
            f"olarak tablonun son olasılığı eksi işaretle yazılsın ve fark ilk değere eklensin: $g({_xt(high)}) = "
            f"-f({_xt(high)})$, $g({_xt(low)}) = f({_xt(low)}) + 2f({_xt(high)})$. İki tabloda da toplam 1'dir; en "
            "küçük olasılık iki tabloyu ayırır."
        ),
        operations=(
            Statistic("dagilim", f, "sum", "f_toplam", "Σ f(x)", decimals=2),
            Statistic("dagilim", f, "min", "f_en_kucuk", "En küçük f(x)",
                      decimals=kesir_basamak(min(dist["f"].values()))),
            Statistic("dagilim", x, "min", "x_en_kucuk", "En küçük değer", decimals=max(0, decimal_places(low))),
            Statistic("dagilim", x, "max", "x_en_buyuk", "En büyük değer", decimals=max(0, decimal_places(high))),
            Derive("dagilim", names["bilinen"], E.compare("lt", E.var(x), E.ref("x_en_buyuk")),
                   "En büyük değerden küçük x'ler: olasılıkları bilinen değerler"),
            Statistic("dagilim", f, "sum", "bilinen_toplam", "Bilinen olasılıkların toplamı",
                      where=(names["bilinen"], 1), decimals=kesir_basamak(known)),
            Scalar("f_eksik", E.sub(1, E.ref("bilinen_toplam")), f"P(X = {_x(high)}) = 1 − bilinen toplam",
                   decimals=kesir_basamak(f_high)),
            Derive("dagilim", names["en_kucuk_mu"], E.compare("eq", E.var(x), E.ref("x_en_kucuk")),
                   "En küçük değerin göstergesi"),
            Derive("dagilim", names["en_buyuk_mu"], E.compare("eq", E.var(x), E.ref("x_en_buyuk")),
                   "En büyük değerin göstergesi"),
            Derive("dagilim", g,
                   E.sub(E.var(f), E.mul(E.mul(2, E.ref("f_eksik")),
                                         E.sub(E.var(names["en_buyuk_mu"]), E.var(names["en_kucuk_mu"])))),
                   "Karşı örnek g(x): son olasılık eksi işaretle, fark ilk değerde"),
            Statistic("dagilim", g, "sum", "g_toplam", "Karşı örnek: Σ g(x)", decimals=2),
            Statistic("dagilim", g, "min", "g_en_kucuk", "Karşı örnek: en küçük g(x)", decimals=kesir_basamak(f_high)),
            BarChart("dagilim", f, "x", "Olasılık", "Geçerli: bütün f(x) ≥ 0 ve Σ f(x) = 1", x=x,
                     decimals=min(digits, 3)),
            BarChart("dagilim", g, "x", "Olasılık", "Geçersiz: Σ g(x) = 1 ama bir olasılık negatif", x=x,
                     decimals=min(g_digits, 3)),
        ),
        checks=(
            _scalar("f_toplam", "Σ f(x)", 2),
            _scalar("f_eksik", f"Eksik olasılık P(X = {_x(high)})", kesir_basamak(f_high)),
            _scalar("g_toplam", "Karşı örnek: Σ g(x) = 1", 2),
            _scalar("g_en_kucuk", "Karşı örnek: en küçük g(x) negatif", kesir_basamak(f_high)),
        ),
        takeaway=(
            "Verinin dağılımında hiçbir olasılık negatif değildir ve toplam 1'dir. Eksik olasılık "
            f"{kesir_metin(f_high)} çıkar; bu, x = {_x(high)} değerinin göreli frekansıdır. Karşı örnekte toplam 1 "
            f"olduğu hâlde x = {_x(high)} değerindeki olasılık negatiftir: tek bir koşulun sağlanması yetmez, iki "
            "koşul birlikte denetlenir. Bir tablodaki sayılar otomatik olarak olasılık kabul edilmez (§8.4)."
        ),
    )


def _threshold(dist: dict):
    """Adım 3'ün eşiği: en olası değer. Olay kesin (eşik en küçük değer) ya da tek değerli (eşik en büyük değer)
    olacaksa komşu değer. Yalnız iki farklı değer varsa en büyük değer: iki değeri birden içeren olay kesin olurdu."""

    mode, points = dist["modes"][0], dist["points"]
    if len(points) == 2 or mode == points[0]:
        return points[1]
    if mode == points[-1]:
        return points[-2]
    return mode


def _step3(case: Case, ctx: dict) -> LabStep:
    dist, names, x = ctx["dist"], ctx["names"], ctx["x"]
    t = _threshold(dist)
    members = tuple(point for point in dist["points"] if point >= t)
    p_event = sum((dist["f"][point] for point in members), Fraction(0))
    if len(members) <= 6:
        members_tex = ", ".join(_xt(point) for point in members)
        event = f"$\\{{X \\geq {_xt(t)}\\}} = \\{{{members_tex}\\}}$ biçiminde yazılır"
    else:  # aralar düzenli olmayabilir: değerler tek tek ya da üç noktayla yazılmaz
        event = (f"$\\{{X \\geq {_xt(t)}\\}}$ biçiminde yazılır ve {len(members)} değer içerir (en küçüğü {_x(t)}, en "
                 f"büyüğü {_x(members[-1])})")
    terms = (" + ".join(f"f({_xt(point)})" for point in members) if len(members) <= 4 else
             f"\\sum_{{x \\geq {_xt(t)}}} f(x)")
    single = ("" if len(members) > 1 else
              " Bu veride X yalnız iki farklı değer alır: iki değeri birden içeren olay kesin olay olurdu (olasılığı "
              "1), bu yüzden buradaki olay tek bir değer içerir.")
    return LabStep(
        number=3,
        title="Birden fazla değer içeren olayın olasılığı",
        note=NoteRef("8.5", objects=("Şekil 8.5",)),
        explanation=(
            f"“En az {_x(t)}” olayı {event}. Olasılık fonksiyonu tek bir değerin olasılığını verir; birden fazla değer "
            f"içeren olayın olasılığı ilgili değerlerin olasılıkları toplanarak bulunur: $P(X \\geq {_xt(t)}) = "
            f"{terms}$. Olayın gösterge sütunu olaya giren değerlerde 1, diğerlerinde 0'dır.{single}"
        ),
        operations=(
            Event("dagilim", names["olay"], x, members, f"X ≥ {_x(t)}: en az {_x(t)}"),
            ShowFrame("dagilim", (x, names["f"], names["olay"]), "Olasılıklar ve olayın gösterge sütunu",
                      decimals=((names["f"], ctx["f_digits"]),)),
            Statistic("dagilim", names["f"], "sum", "P_olay", f"P(X ≥ {_x(t)})", where=(names["olay"], 1),
                      decimals=kesir_basamak(p_event)),
        ),
        checks=(
            _scalar("P_olay", f"P(X ≥ {_x(t)})", kesir_basamak(p_event)),
        ),
        takeaway=(
            f"Rastgele seçilen bir gözlemin değerinin en az {_x(t)} olma olasılığı {kesir_metin(p_event)}. Kesikli "
            f"değişkende P(X ≥ {_x(t)}) ile P(X > {_x(t)}) aynı değildir: eşitsizlikteki eşitlik çizgisi {_x(t)} "
            "değerini olaya katar (§8.5)."
        ),
    )


def _step4(case: Case, ctx: dict) -> LabStep:
    dist, x = ctx["dist"], ctx["x"]
    mode = dist["modes"][0]
    count, n = dist["counts"][mode], dist["n"]
    checks = [Check(f"f({_x(point)}) = {dist['counts'][point]}/{n}", TableTarget("ampirik", point, "goreli"), 0.0,
                    kesir_basamak(dist["f"][point])) for point in dist["points"]]
    return LabStep(
        number=4,
        title="Veriden olasılık dağılımına: ampirik dağılım",
        note=NoteRef("8.6", objects=("Tablo 8.2", "Şekil 8.6")),
        explanation=(
            f"Her gözlemin değeri bir gerçekleşmedir. “{md(ctx['label'])}” sütununda $n = {n}$ gözlem vardır. "
            "Göreli frekanslar, $f(x) = (x \\text{ değerini alan gözlem sayısı})/n$, gelecekteki tipik bir gözlem için "
            "olasılık değerlendirmesi olarak kullanılır. Adım 1'deki olasılık fonksiyonu ve grafiği bu tablodan gelir."
        ),
        operations=(
            FrequencyTable(case.frame, x, "ampirik", dist["points"], totals=True),
        ),
        checks=(
            *checks,
            Check("Gözlem sayısı", TableTarget("ampirik", TOTAL, "frekans"), 0.0, 0),
            Check("Göreli frekansların toplamı", TableTarget("ampirik", TOTAL, "goreli"), 0.0, 2),
        ),
        takeaway=(
            f"x = {_x(mode)} değeri {count} gözlemde görülür: f({_x(mode)}) = {count}/{n} "
            f"{_table3(dist['f'][mode])}. Ampirik olasılıklar geçmiş veriyi özetler. "
            "Koşullar (kapasite, fiyat politikası, müşteri tabanı) değişirse eski göreli frekanslar yeni dönemi iyi "
            "temsil etmeyebilir; dağılımın güncellenmesi gerekir (§8.6)."
        ),
    )


def _step5(case: Case, ctx: dict) -> LabStep:
    dist, names, x = ctx["dist"], ctx["names"], ctx["x"]
    mean = dist["mean"]
    products = {point: dist["exact"][point] * dist["f"][point] for point in dist["points"]}
    digits = _scale(mean)
    observed = ("Bu veride E(X), X'in olası değerlerinden biridir; bu bir zorunluluk değildir." if mean in
                dist["exact"].values() else
                "Bu veride E(X), X'in alabileceği değerlerden biri değildir; olmak zorunda da değildir.")
    return LabStep(
        number=5,
        title="Beklenen değer: olasılık ağırlıklı ortalama",
        note=NoteRef("8.7", objects=("Tablo 8.3", "Şekil 8.7")),
        explanation=(
            "Kesikli $X$'in beklenen değeri $E(X) = \\mu_X = \\sum_x x f(x)$ ile tanımlanır: her olası değer "
            "gerçekleşme olasılığıyla ağırlıklandırılır ve çarpımlar toplanır. Ampirik dağılımda bu toplam verinin "
            "aritmetik ortalamasına eşittir: her değer kendi gözlem sayısı kadar sayılmış olur."
        ),
        operations=(
            Derive("dagilim", names["xf"], E.mul(E.var(x), E.var(names["f"])), "x f(x): değer × olasılık"),
            ShowFrame("dagilim", (x, names["f"], names["xf"]), "Beklenen değerin hesabı",
                      decimals=((names["f"], ctx["f_digits"]),
                                (names["xf"], _column_digits(products.values())))),
            Statistic("dagilim", names["xf"], "sum", "E_X", "E(X) = Σ x f(x)", decimals=digits),
            Statistic(case.frame, x, "mean", "x_ortalama", "Verinin aritmetik ortalaması x̄", decimals=digits),
        ),
        checks=(
            *(Check(f"x f(x), x = {_x(point)}", CellTarget("dagilim", names["xf"], index), 0.0,
                    _scale(products[point]))
              for index, point in enumerate(dist["points"], start=1)),
            _scalar("E_X", "E(X) = Σ x f(x)", digits),
            _scalar("x_ortalama", "x̄ = E(X)", digits),
        ),
        takeaway=(
            f"E(X) {_plain(mean, digits)}. Beklenen değer tek bir gözlemin değeri değildir; aynı koşullardaki çok "
            f"sayıda gözlem boyunca ortalamanın hangi düzey çevresinde olacağını söyler. {observed} Olasılık ağırlıklı "
            "denge merkezidir (§8.7)."
        ),
    )


def _step6(case: Case, ctx: dict) -> LabStep:
    dist, names, x = ctx["dist"], ctx["names"], ctx["x"]
    values = case.data[x].astype(float).tolist()
    n = len(values)
    early = min(EARLY, n)
    early_mean = sum((_exact(value) for value in values[:early]), Fraction(0)) / early
    first = _exact(values[0])
    digits = _scale(dist["mean"])
    early_digits = _scale(early_mean)
    sira, birikimli = names["sira"], names["birikimli"]
    order = "dosyadaki" if case.source == "kendi" else "veri setindeki"
    rising = all(a <= b for a, b in zip(values, values[1:]))
    falling = all(a >= b for a, b in zip(values, values[1:]))
    if rising or falling:  # sıralı dosya: birikimli ortalama dalgalanmaz, tek yönden yaklaşır
        side, arranged = ("aşağıdan", "küçükten büyüğe") if rising else ("yukarıdan", "büyükten küçüğe")
        pattern = (f"Gözlemler {order} sırada {arranged} dizili olduğu için çizgi dalgalanmaz, E(X)'e {side} tek "
                   "yönden yaklaşır; bu davranış sıralamanın sonucudur, uzun dönem yorumu gözlemlerin gerçekleşme "
                   "sırasıyla yapılır. Son nokta bütün gözlemlerin ortalamasıdır ve ampirik dağılımda tanım gereği "
                   "E(X)'e eşittir.")
    else:
        pattern = ("Gözlem sayısı arttıkça tek bir gözlemin ortalamayı değiştirme payı küçülür; dalgalanma bu yüzden "
                   "azalır. Son nokta bütün gözlemlerin ortalamasıdır ve ampirik dağılımda tanım gereği E(X)'e "
                   "eşittir; bu yüzden asıl görülecek olan dalgalanmanın azalmasıdır.")
    return LabStep(
        number=6,
        title="Beklenen değer ve uzun dönem ortalaması",
        note=NoteRef("8.8"),
        explanation=(
            "Beklenen değer “tek seferlik bir tahmin” değildir: aynı süreç tekrarlandıkça gerçekleşen değerlerin "
            f"ortalaması beklenen değer çevresinde istikrar kazanma eğilimindedir. Gözlemler {order} sırayla tek tek "
            "eklensin: $k$. noktadaki değer ilk $k$ gözlemin ortalamasıdır. Kesikli çizgi $E(X)$'tir (Adım 5)."
        ),
        operations=(
            Derive(case.frame, sira, E.seq(E.var(x)), "Gözlemin sırası 1, 2, …, n"),
            Derive(case.frame, birikimli, E.cummean(E.var(x)), "İlk k gözlemin ortalaması"),
            LineChart(case.frame, sira, birikimli, f"Gözlem sırası ({order} sıra)", "O ana kadarki ortalama",
                      "Birikimli ortalama ve beklenen değer", references=(("E_X", "E(X)"),), markers=n <= 40),
        ),
        checks=(
            Check(f"İlk {early} gözlemin ortalaması", CellTarget(case.frame, birikimli, early), 0.0, early_digits),
            Check(f"Bütün {n} gözlemin ortalaması = E(X)", CellTarget(case.frame, birikimli, n), 0.0, digits),
        ),
        takeaway=(
            f"Çizgi ilk gözlemin değerinden ({kesir_sayi(first, kesir_basamak(first, 4, 0))}) başlar; ilk {early} "
            f"gözlemin ortalaması {kesir_metin(early_mean, early_digits)}. {pattern} Bilinen bir dağılımdan yapılan "
            "bağımsız çekilişlerle aynı davranışı Sezgi sekmesindeki Deney 1 gösterir (§8.8)."
        ),
    )


def _step7(case: Case, ctx: dict) -> LabStep:
    dist, names, x = ctx["dist"], ctx["names"], ctx["x"]
    variance = dist["variance"]
    digits = _scale(variance)
    deviations = {point: (dist["exact"][point] - dist["mean"]) ** 2 for point in dist["points"]}
    weighted = {point: deviations[point] * dist["f"][point] for point in dist["points"]}
    top = max(weighted.values())
    top_digits = _column_digits(weighted.values())  # tablodaki (x − μ)² f(x) sütunu gibi
    biggest = [point for point in dist["points"] if weighted[point] == top]  # eşitlikte hepsi
    farthest = [point for point in dist["points"] if deviations[point] == max(deviations.values())]
    which_big = f"x = {sayilar([_x(point) for point in biggest])}"
    if biggest == farthest and len(biggest) == 1:
        contribution = f"En büyük katkı merkezden en uzak değerden gelir ({which_big}): {kesir_metin(top, top_digits)}"
    elif biggest == farthest:
        contribution = (f"En büyük katkı merkezden en uzak değerlerden gelir ({which_big}); her birinin katkısı "
                        f"{kesir_metin(top, top_digits)}")
    else:
        far = (f"x = {_x(farthest[0])} merkezden en uzak değerdir" if len(farthest) == 1 else
               f"x = {sayilar([_x(point) for point in farthest])} merkezden en uzak değerlerdir")
        big = (f"{which_big} değerinden gelir ({kesir_metin(top, top_digits)})" if len(biggest) == 1 else
               f"{which_big} değerlerinden gelir (her biri {kesir_metin(top, top_digits)})")
        contribution = f"Bir değerin katkısı hem uzaklığına hem olasılığına bağlıdır: {far}, ama en büyük katkı {big}"
    sd_text, sd_digits = _root_text(variance)
    return LabStep(
        number=7,
        title="Varyans ve standart sapma",
        note=NoteRef("8.9", objects=("Tablo 8.4",)),
        explanation=(
            "Varyans olası değerlerin beklenen değerden uzaklıklarının karelerinin olasılık ağırlıklı toplamıdır: "
            "$\\operatorname{Var}(X) = \\sigma_X^2 = \\sum_x (x - \\mu_X)^2 f(x)$; standart sapma $\\sigma_X = "
            "\\sqrt{\\operatorname{Var}(X)}$ ile bulunur. Ampirik dağılımda bu, paydası $n$ olan ortalamadır; Konu "
            "5'teki örneklem varyansı $s^2$ paydada $n - 1$ kullanır: $\\operatorname{Var}(X) = (n - 1)s^2/n$."
        ),
        operations=(
            Derive("dagilim", names["sapma_kare"], E.power(E.sub(E.var(x), E.ref("E_X")), 2),
                   "(x − μ)²: beklenen değerden uzaklığın karesi"),
            Derive("dagilim", names["agirlikli_kare"], E.mul(E.var(names["sapma_kare"]), E.var(names["f"])),
                   "(x − μ)² f(x)"),
            ShowFrame("dagilim", (x, names["f"], names["sapma_kare"], names["agirlikli_kare"]), "Varyansın hesabı",
                      decimals=((names["f"], ctx["f_digits"]),
                                (names["sapma_kare"], _column_digits(deviations.values())),
                                (names["agirlikli_kare"], top_digits))),
            Statistic("dagilim", names["agirlikli_kare"], "sum", "Var_X", "Var(X) = Σ (x − μ)² f(x)",
                      decimals=digits),
            Scalar("sd_X", E.sqrt(E.ref("Var_X")), "Standart sapma σ = √Var(X)", decimals=sd_digits),
            Statistic(case.frame, x, "var", "s_kare", "Örneklem varyansı s²",
                      decimals=_scale(variance * ctx["n"] / (ctx["n"] - 1))),
            Scalar("Var_s", E.div(E.mul(E.ref("s_kare"), E.sub(E.ref("n_veri"), 1)), E.ref("n_veri")),
                   "(n − 1)s²/n", decimals=digits),
        ),
        checks=(
            _scalar("Var_X", "Var(X) = Σ (x − μ)² f(x)", digits),
            _scalar("sd_X", "σ = √Var(X)", sd_digits),
            _scalar("Var_s", "(n − 1)s²/n = Var(X)", digits),
        ),
        takeaway=(
            f"Var(X) {_plain(variance, digits)}, σ {sd_text}. Standart sapma X ile aynı birimdedir; bu yüzden yorumu "
            f"daha kolaydır. {contribution} (§8.9)."
        ),
    )


def _step8(case: Case, ctx: dict) -> LabStep:
    dist, names, x = ctx["dist"], ctx["names"], ctx["x"]
    points = dist["points"]
    low, high = points[0], points[-1]
    mean = dist["mean"]
    span = dist["exact"][high] - dist["exact"][low]
    p_high = (mean - dist["exact"][low]) / span
    var_b = (mean - dist["exact"][low]) * (dist["exact"][high] - mean)
    var_a = dist["variance"]
    start = max(_scale(var_a), _scale(var_b))
    cap = max(start, 12 - math.floor(math.log10(float(max(var_a, var_b)))))  # en çok 13 anlamlı basamak
    digits = kesir_ayirt(var_a, var_b, start=start, maximum=cap)  # Var(B) > Var(A) farklı görünsün
    b_digits = kesir_ortak_basamak(p_high, 1 - p_high)  # tablodaki f_B sütunu ve metin
    if len(points) == 2:
        verdict = ("Verinizde yalnız iki farklı değer olduğu için B, A'nın aynısıdır: varyanslar eşittir. Daha çok "
                   "farklı değeri olan bir sütunda B'nin varyansı A'nınkinden büyük olur.")
    elif kesir_sayi(var_a, digits) == kesir_sayi(var_b, digits):  # fark gösterilen basamağın altında
        verdict = (f"B'nin olasılık kütlesi uç değerlere taşınmıştır: Var(B) {_plain(var_b, digits)} ile Var(A) bu "
                   f"basamakta aynı görünür, ama Var(B) daha büyüktür: Var(B) − Var(A) "
                   f"{_plain(var_b - var_a, _scale(var_b - var_a))}. Aynı aralıkta ve aynı ortalamayla varyansı en "
                   "büyük dağılım budur.")
    else:
        verdict = (f"B'nin olasılık kütlesi uç değerlere taşınmıştır: Var(B) {_plain(var_b, digits)} > Var(A) "
                   f"{_plain(var_a, digits)}. Aynı aralıkta ve aynı ortalamayla varyansı en büyük dağılım budur.")
    f_b = names["f_B"]
    indicator_low = E.compare("eq", E.var(x), E.ref("x_en_kucuk"))
    indicator_high = E.compare("eq", E.var(x), E.ref("x_en_buyuk"))
    width = E.sub(E.ref("x_en_buyuk"), E.ref("x_en_kucuk"))
    return LabStep(
        number=8,
        title="Aynı beklenen değer, farklı değişkenlik",
        note=NoteRef("8.10", objects=("Tablo 8.5", "Şekil 8.10")),
        explanation=(
            f"$A$ verinin dağılımıdır (Adım 1). $B$ aynı değer ekseninde yalnız en küçük ({_x(low)}) ve en büyük "
            f"({_x(high)}) değerleri alır; olasılıklar ortalama aynı kalacak biçimde seçilir: "
            f"$f_B({_xt(high)}) = (\\mu - {_xp(low)})/({_xt(high)} - {_xp(low)}) {_eq(p_high, b_digits)}$ ve "
            f"$f_B({_xt(low)}) = 1 - f_B({_xt(high)})$. İki dağılım aynı eksende yazılır; dağılımın almadığı değerin "
            "olasılığı 0'dır. Beklenen değer ve varyans Adım 5 ve Adım 7'deki formüllerle bulunur."
        ),
        operations=(
            Derive("dagilim", f_b,
                   E.add(E.mul(indicator_low, E.div(E.sub(E.ref("x_en_buyuk"), E.ref("E_X")), width)),
                         E.mul(indicator_high, E.div(E.sub(E.ref("E_X"), E.ref("x_en_kucuk")), width))),
                   "B: kütle en küçük ve en büyük değerde, ortalama aynı"),
            Derive("dagilim", names["xf_B"], E.mul(E.var(x), E.var(f_b)), "x f_B(x)"),
            Statistic("dagilim", names["xf_B"], "sum", "E_B", "E(B)", decimals=_scale(mean)),
            Derive("dagilim", names["kare_B"], E.mul(E.power(E.sub(E.var(x), E.ref("E_B")), 2), E.var(f_b)),
                   "(x − μ_B)² f_B(x)"),
            Statistic("dagilim", names["kare_B"], "sum", "Var_B", "Var(B)", decimals=digits),
            ShowFrame("dagilim", (x, names["f"], f_b), "A ve B aynı değer ekseninde",
                      decimals=((names["f"], ctx["f_digits"]), (f_b, b_digits))),
            BarChart("dagilim", names["f"], "Değer", "Olasılık", "Dağılım A: verinin dağılımı", x=x,
                     decimals=min(ctx["f_digits"], 3)),
            BarChart("dagilim", f_b, "Değer", "Olasılık", "Dağılım B: kütle uç değerlerde", x=x,
                     decimals=min(b_digits, 3)),
        ),
        checks=(
            Check(f"f_B({_x(high)})", CellTarget("dagilim", f_b, len(points)), 0.0, kesir_basamak(p_high)),
            _scalar("E_B", "E(B) = E(A)", _scale(mean)),
            _scalar("Var_B", "Var(B) = (μ − en küçük)(en büyük − μ)", digits),
        ),
        takeaway=(
            f"İki dağılımın merkezi aynıdır: E(A) = E(B) {_plain(mean, _scale(mean))}. {verdict} Beklenen değer tek "
            "başına belirsizliği ölçmez; iktisadi uygulamalarda bu fark “aynı ortalama sonuç, farklı belirsizlik” "
            "biçiminde önem taşır (§8.10)."
        ),
    )


def _pair_digits(pair: dict) -> int:
    """Ortak olasılık tablosunun ortak basamağı (iç hücreler ve kenarlar; tam yarımda bir basamak daha)."""

    values = [*pair["joint"].values(), *pair["dist_x"]["f"].values(), *pair["dist_y"]["f"].values()]
    return kesir_ortak_basamak(*values)


def _step9(case: Case, ctx: dict, pair: dict | None) -> LabStep:
    title, note = "İki rassal değişken: ortak olasılık dağılımı", "8.11"
    if pair is None:
        return _missing(9, title, note)
    if "problem" in pair:
        return _blocked(9, title, note, pair["problem"])
    names, x, y, frame = ctx["names"], ctx["x"], pair["y"], pair["frame"]
    dist_x, dist_y = pair["dist_x"], pair["dist_y"]
    digits = _pair_digits(pair)
    cx, cy = pair["cell"]
    p_cell = kesir_metin(pair["joint"][pair["cell"]], digits)  # tablodaki basamakla
    cells = pair["cells"]
    if len(cells) == 1:
        modal = f"en olası çift (x, y) = {_pair_text(cx, cy)} ve olasılığı {p_cell}"
    elif len(cells) <= 3:
        modal = (f"en olası çiftler (x, y) = {liste([_pair_text(*cell) for cell in cells])}; her birinin olasılığı "
                 f"{p_cell}")
    else:
        modal = f"en yüksek olasılığı ({p_cell}) {len(cells)} çift paylaşır, ör. (x, y) = {_pair_text(cx, cy)}"
    skipped = (f" Y'si boş olan {pair['skipped']} gözlem bu adımda kullanılmaz; X'in marjinal dağılımı bu yüzden "
               "Adım 1'dekinden biraz farklı olabilir." if pair["skipped"] else
               " X'in marjinal dağılımı Adım 1'deki f(x) ile aynıdır.")
    zero = (len(dist_x["points"]) * len(dist_y["points"]) - len(pair["joint"]))
    zeros = (f" Veride hiç gözlenmeyen {zero} çiftin olasılığı 0'dır." if zero else "")
    checks = [
        Check(f"P(X = {_x(cx)}, Y = {_x(cy)}): en olası çift", TableTarget("ortak_tablo", cy, cx), 0.0,
              kesir_basamak(pair["joint"][pair["cell"]])),
        *(Check(f"P(X = {_x(point)})", TableTarget("ortak_tablo", TOTAL, point), 0.0,
                kesir_basamak(dist_x["f"][point])) for point in dist_x["points"]),
        *(Check(f"P(Y = {_x(point)})", TableTarget("ortak_tablo", point, TOTAL), 0.0,
                kesir_basamak(dist_y["f"][point])) for point in dist_y["points"]),
        Check("Ortak olasılıkların toplamı", TableTarget("ortak_tablo", TOTAL, TOTAL), 0.0, 2),
    ]
    return LabStep(
        number=9,
        title=title,
        note=NoteRef(note, objects=("Tablo 8.6", "Şekil 8.11")),
        explanation=(
            f"$X$ = “{md(ctx['label'])}”, $Y$ = “{md(pair['label'])}”. Her gözlem bir $(x, y)$ çiftidir; ortak "
            "olasılık $f(x, y) = P(X = x, Y = y)$, o çifti veren gözlemlerin payıdır. Her gözlem $1/n$ olasılık taşır "
            f"($n = {pair['n']}$); aynı çiftin olasılıkları toplanınca $f(x, y)$ bulunur. Çapraz tablonun iç hücreleri "
            "ortak olasılıklar, kenarları marjinal dağılımlardır (satırlar $Y$, sütunlar $X$)."
        ),
        operations=(
            *pair["load"],
            Statistic(frame, y, "count", "n_cift", "X ve Y'si olan gözlem sayısı", decimals=0),
            Derive(frame, names["agirlik"], E.div(1, E.ref("n_cift")), "Her gözlemin olasılığı 1/n"),
            CrossTab(frame, y, x, "ortak_tablo", dist_y["points"], dist_x["points"], margins=True, decimals=digits,
                     weights=names["agirlik"]),
            HeatMap("ortak_tablo", f"X: {ctx['label']}", f"Y: {pair['label']}", "Ortak olasılık dağılımı: ısı haritası",
                    decimals=min(digits, 3)),
        ),
        checks=tuple(checks),
        takeaway=(
            f"İç hücreler ortak olasılıklardır: {modal}. Alt satır X'in, sağ sütun Y'nin marjinal "
            f"dağılımıdır.{skipped}{zeros} Terimler Konu 7'deki ortak ve marjinal olay olasılıklarının devamıdır "
            "(§8.11)."
        ),
    )


U = 2.0 ** -53
"""Çift duyarlıklı kayan noktanın birim yuvarlama hatası."""
SUPERSCRIPT = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")


def _shortcut_error(pair: dict) -> tuple[float, float]:
    """E(XY) − E(X)E(Y) kayan noktayla hesaplanırken oluşabilecek hatanın üst sınırı (ikili [pairwise] toplama,
    çarpımlar ve çıkarma; iki kat pay) ve terimlerin büyüklüğü. Değerler büyükse E(XY) ile E(X)E(Y) birbirine çok yakın
    iki büyük sayıdır ve farkları anlamlı basamaklarını yitirir (999 997–999 999 arası değerlerde 10⁻³ düzeyinde)."""

    dist_x, dist_y = pair["dist_x"], pair["dist_y"]
    exy_abs = float(sum((abs(_exact(px) * _exact(py)) * value for (px, py), value in pair["joint"].items()),
                        Fraction(0)))
    ex_abs = float(sum((abs(dist_x["exact"][v]) * dist_x["f"][v] for v in dist_x["points"]), Fraction(0)))
    ey_abs = float(sum((abs(dist_y["exact"][v]) * dist_y["f"][v] for v in dist_y["points"]), Fraction(0)))
    ex, ey = abs(float(dist_x["mean"])), abs(float(dist_y["mean"]))
    accumulated = 2 * (25 + math.log2(max(pair["n"], 2))) * U
    error = accumulated * (exy_abs + ex * ey_abs + ey * ex_abs) + 2 * U * (exy_abs + ex * ey)
    return error, max(exy_abs, ex * ey)


def _near_half(value: Fraction, digits: int, margin: float) -> bool:
    """Kesin değer ``digits`` basamaktaki bir yuvarlama sınırına (…5) ``margin``'den yakın mı? O zaman kayan noktalı
    sonuç kesin değerden farklı yuvarlanabilir."""

    scaled = value * 10 ** digits
    return abs(float(scaled - math.floor(scaled)) - 0.5) * 10.0 ** -digits <= margin


def _step10(case: Case, ctx: dict, pair: dict | None) -> LabStep:
    title, note = "Ortak dağılımdan beklenen değer, kovaryans ve korelasyon", "8.12"
    if pair is None:
        return _missing(10, title, note)
    if "problem" in pair:
        return _blocked(10, title, note, pair["problem"])
    names, x, y, frame = ctx["names"], ctx["x"], pair["y"], pair["frame"]
    w = names["agirlik"]
    dist_x, dist_y = pair["dist_x"], pair["dist_y"]
    ex, ey, exy, cov = dist_x["mean"], dist_y["mean"], pair["exy"], pair["covariance"]
    vx, vy = dist_x["variance"], dist_y["variance"]
    d_ex, d_ey, d_exy = _scale(ex), _scale(ey), _scale(exy)
    d_cov, d_vx, d_vy = _scale(cov), _scale(vx), _scale(vy)
    rho_text, rho_digits = _root_text(cov * cov / (vx * vy), 1 if cov >= 0 else -1)  # ρ = 0, ±1 ya da ≈
    error, size = _shortcut_error(pair)
    shortcut = error <= 0.25 * 10.0 ** -d_cov and not _near_half(cov, d_cov, error)
    if cov > 0:
        direction = ("Kovaryans pozitiftir: X'in büyük değerleri Y'nin büyük değerleriyle birlikte görülme "
                     "eğilimindedir.")
    elif cov < 0:
        direction = "Kovaryans negatiftir: X büyükken Y küçük olma eğilimindedir."
    else:
        direction = "Kovaryans sıfırdır: doğrusal bir birlikte hareket yoktur."
    if shortcut:
        result = f"İki formül aynı sayıyı verir: Cov(X, Y) {_plain(cov, d_cov)}; ρ {rho_text}."
        short_ops = (Scalar("Cov_XY", E.sub(E.ref("E_XY"), E.mul(E.ref("E_X_ortak"), E.ref("E_Y"))),
                            "Cov(X, Y) = E(XY) − E(X)E(Y)", decimals=d_cov),)
        short_checks = (_scalar("Cov_XY", "Cov(X, Y) = E(XY) − E(X)E(Y)", d_cov),)
    else:  # büyük değerler: kısa yol formülü sayısal olarak güvenilmez
        power = str(round(math.log10(size))).translate(SUPERSCRIPT)  # büyüklük mertebesi: 9,99996·10¹¹ → 10¹²
        result = (f"Değerler büyük olduğu için kısa yol formülü E(XY) − E(X)E(Y), 10{power} düzeyindeki iki terimin "
                  "farkıdır; terimler birbirini büyük ölçüde götürdüğü için kayan noktalı hesapta farkın son "
                  "basamakları güvenilmez. Kovaryans bu yüzden tanım formülüyle hesaplanır: Cov(X, Y) "
                  f"{_plain(cov, d_cov)}; ρ {rho_text}. İki formül cebirsel olarak aynıdır; büyük değerlerde önce "
                  "ortalamadan sapmaları alan tanım formülü sayısal olarak güvenilirdir.")
        short_ops, short_checks = (), ()
    return LabStep(
        number=10,
        title=title,
        note=NoteRef(note),
        explanation=(
            "$E(X) = \\sum_x x\\,P(X = x)$; gözlem çerçevesinde bu, her gözlemde $x$'in gözlemin olasılığıyla ($1/n$) "
            "çarpılıp toplanmasına eşittir. Kovaryans $\\operatorname{Cov}(X, Y) = E[(X - \\mu_X)(Y - \\mu_Y)]$ ile "
            "tanımlanır; eşdeğer olarak $\\operatorname{Cov}(X, Y) = E(XY) - E(X)E(Y)$. Korelasyon ise $\\rho_{XY} "
            "= \\operatorname{Cov}(X, Y)/(\\sigma_X \\sigma_Y)$ ile bulunur."
        ),
        operations=(
            Derive(frame, names["x_f"], E.mul(E.var(x), E.var(w)), "x × gözlemin olasılığı"),
            Statistic(frame, names["x_f"], "sum", "E_X_ortak", "E(X)", decimals=d_ex),
            Derive(frame, names["y_f"], E.mul(E.var(y), E.var(w)), "y × gözlemin olasılığı"),
            Statistic(frame, names["y_f"], "sum", "E_Y", "E(Y)", decimals=d_ey),
            Derive(frame, names["xy_f"], E.mul(E.mul(E.var(x), E.var(y)), E.var(w)), "xy × gözlemin olasılığı"),
            Statistic(frame, names["xy_f"], "sum", "E_XY", "E(XY)", decimals=d_exy),
            *short_ops,
            Derive(frame, names["capraz"],
                   E.mul(E.mul(E.sub(E.var(x), E.ref("E_X_ortak")), E.sub(E.var(y), E.ref("E_Y"))), E.var(w)),
                   "(x − μX)(y − μY) × gözlemin olasılığı"),
            Statistic(frame, names["capraz"], "sum", "Cov_tanim", "Cov(X, Y) tanımdan: E[(X − μX)(Y − μY)]",
                      decimals=d_cov),
            Derive(frame, names["x_kare"], E.mul(E.power(E.sub(E.var(x), E.ref("E_X_ortak")), 2), E.var(w)),
                   "(x − μX)² × gözlemin olasılığı"),
            Statistic(frame, names["x_kare"], "sum", "Var_X_ortak", "Var(X)", decimals=d_vx),
            Derive(frame, names["y_kare"], E.mul(E.power(E.sub(E.var(y), E.ref("E_Y")), 2), E.var(w)),
                   "(y − μY)² × gözlemin olasılığı"),
            Statistic(frame, names["y_kare"], "sum", "Var_Y", "Var(Y)", decimals=d_vy),
            # ρ tanım formülündeki kovaryansla: büyük değerlerde de sayısal olarak güvenilir
            Scalar("rho_XY", E.div(E.ref("Cov_tanim"), E.sqrt(E.mul(E.ref("Var_X_ortak"), E.ref("Var_Y")))),
                   "ρ = Cov(X, Y)/(σX σY)", decimals=rho_digits),
        ),
        checks=(
            _scalar("E_X_ortak", "E(X)", d_ex),
            _scalar("E_Y", "E(Y)", d_ey),
            _scalar("E_XY", "E(XY)", d_exy),
            *short_checks,
            _scalar("Cov_tanim", "Cov(X, Y) tanım formülüyle", d_cov),
            _scalar("Var_X_ortak", "Var(X)", d_vx),
            _scalar("Var_Y", "Var(Y)", d_vy),
            _scalar("rho_XY", "ρ = Cov(X, Y)/(σX σY)", rho_digits),
        ),
        takeaway=(
            f"{direction} {result} Bunlar ampirik ortak dağılımın ölçüleridir ve paydaları n'dir: Konu 5'teki "
            "örneklem kovaryansı s_xy paydada n − 1 kullanır (Cov = (n − 1)s_xy/n); korelasyon ise iki tanımda "
            "aynıdır, ρ = r (§8.12)."
        ),
    )


METRIC_WIDTH = 28
"""Dörtlü metrik satırında başlığın sığdığı en çok karakter (1280 piksel genişlikte)."""
UNIT_WORDS = {"gün": ("her gün", "tek tek günlerde"), "gözlem": ("her gözlemde", "tek tek gözlemlerde")}


def _step11(case: Case, ctx: dict, pair: dict | None) -> LabStep:
    title, note = "Bağımsızlık: ortak olasılık ve marjinallerin çarpımı", "8.13"
    if pair is None:
        return _missing(11, title, note)
    if "problem" in pair:
        return _blocked(11, title, note, pair["problem"])
    names, x, y, frame = ctx["names"], ctx["x"], pair["y"], pair["frame"]
    w = names["agirlik"]
    cx, cy = pair["cell"]
    p_x, p_y = pair["dist_x"]["f"][cx], pair["dist_y"]["f"][cy]
    p_xy = pair["joint"][pair["cell"]]
    product = p_x * p_y
    apart = kesir_ayirt(p_xy, product)  # farklıysa gösterimde de farklı
    if pair["independent"]:
        verdict = ("Bu veride her hücrede ortak olasılık marjinallerin çarpımına eşittir: X ve Y bağımsızdır; "
                   "kovaryans da bu yüzden sıfırdır.")
    elif p_xy == product:
        verdict = ("Bu hücrede eşitlik sağlanır; ancak bağımsızlık bütün hücrelerde eşitlik ister ve bu veride en az "
                   "bir hücrede sağlanmaz: X ve Y bağımsız değildir.")
    else:
        verdict = (f"Ortak olasılık {kesir_metin(p_xy, apart)} iken bağımsızlık altında olması gereken çarpım "
                   f"{kesir_metin(product, apart)}; eşitlik sağlanmadığı için X ve Y bağımsız değildir.")
    vx, vy = _x(cx), _x(cy)
    which = ("En olası çiftin hücresinde" if len(pair["cells"]) == 1 else
             "Aynı olasılıklı en olası çiftlerden ilkinin hücresinde")
    titles = (f"P(X = {vx}): marjinal", f"P(Y = {vy}): marjinal", f"P(X = {vx}, Y = {vy}): ortak",
              f"Çarpım P(X = {vx})P(Y = {vy})")
    if max(len(item) for item in titles) > METRIC_WIDTH:  # uzun değerlerde başlıklar x* ve y* ile yazılır
        titles = ("P(X = x*): marjinal", "P(Y = y*): marjinal", "P(X = x*, Y = y*): ortak", "Çarpım P(X = x*)P(Y = y*)")
    return LabStep(
        number=11,
        title=title,
        note=NoteRef(note, objects=("Şekil 8.13",)),
        explanation=(
            "$X$ ve $Y$ bağımsızsa her $(x, y)$ çifti için $P(X = x, Y = y) = P(X = x)P(Y = y)$ olmalıdır. "
            f"{which}, $(x^*, y^*) = {_pair_tex(cx, cy)}$, ortak olasılık marjinal olasılıkların çarpımıyla "
            "karşılaştırılır. Marjinal olasılıklar ilgili gözlemlerin olasılıkları toplanarak bulunur."
        ),
        operations=(
            Event(frame, names["X_hucre"], x, (cx,), f"X = {vx}"),
            Event(frame, names["Y_hucre"], y, (cy,), f"Y = {vy}"),
            Derive(frame, names["hucre"], E.mul(E.var(names["X_hucre"]), E.var(names["Y_hucre"])),
                   f"X = {vx} ve Y = {vy}"),
            Statistic(frame, w, "sum", "P_X_hucre", titles[0], where=(names["X_hucre"], 1),
                      decimals=kesir_basamak(p_x)),
            Statistic(frame, w, "sum", "P_Y_hucre", titles[1], where=(names["Y_hucre"], 1),
                      decimals=kesir_basamak(p_y)),
            Statistic(frame, w, "sum", "P_hucre", titles[2], where=(names["hucre"], 1), decimals=apart),
            Scalar("carpim_hucre", E.mul(E.ref("P_X_hucre"), E.ref("P_Y_hucre")), titles[3], decimals=apart),
        ),
        checks=(
            _scalar("P_hucre", f"P(X = {vx}, Y = {vy})", apart),
            _scalar("P_X_hucre", f"P(X = {vx})", kesir_basamak(p_x)),
            _scalar("P_Y_hucre", f"P(Y = {vy})", kesir_basamak(p_y)),
            _scalar("carpim_hucre", f"P(X = {vx})P(Y = {vy})", apart),
        ),
        takeaway=(
            f"{verdict} Bağımsız iki rassal değişkenin kovaryansı sıfırdır (Adım 10). Tersi genel olarak doğru "
            "değildir; sıfır kovaryans bağımsızlığı garanti etmez (§8.13)."
        ),
    )


def _step12(case: Case, ctx: dict) -> LabStep:
    dist, names, x = ctx["dist"], ctx["names"], ctx["x"]
    settings = ctx["settings"]
    a, b = settings[KATKI], settings[SABIT]
    profits = {point: a * dist["exact"][point] - b for point in dist["points"]}
    expected = a * dist["mean"] - b
    loss = sum((dist["f"][point] for point in dist["points"] if profits[point] < 0), Fraction(0))
    digits = kesir_basamak(expected, 2, 0)
    profit_digits = max(kesir_basamak(value, 4, 0) for value in profits.values())
    story = case.extra.get("profit_text") or (f"Her birim {a} TL katkı sağlasın; sabit maliyet {b} TL olsun.")
    if loss == 0:
        risk = "Hiçbir değerde zarar oluşmaz: P(Π < 0) = 0."
    elif loss == 1:
        risk = "Her değerde zarar oluşur: P(Π < 0) = 1."
    else:
        losing = [point for point in dist["points"] if profits[point] < 0]
        where = (f"yalnız X = {_x(losing[0])} iken" if len(losing) == 1 else
                 f"X ≤ {_x(losing[-1])} iken")
        risk = (f"Zarar {where} oluşur: P(Π < 0) {_plain(loss)}.")
    every, single = UNIT_WORDS.get(case.unit, UNIT_WORDS["gözlem"])
    if expected > 0 and loss == 0:
        sign_text = "Zarar olmasa da kâr değerden değere değişir"
    elif expected > 0:
        sign_text = f"Pozitif beklenen kâr {every} kâr edileceği anlamına gelmez"
    elif max(profits.values()) > 0:
        sign_text = f"Beklenen kâr pozitif değildir; {single} yine de kâr edilebilir"
    else:
        sign_text = "Beklenen kâr pozitif değildir ve bu veride hiçbir değerde pozitif kâr oluşmaz"
    profit = _linear(a, b, "x")
    linear = f"E(Π) = {_linear(a, b, 'E(X)')}"
    return LabStep(
        number=12,
        title="Bütünleştirici uygulama: doğrusal kâr",
        note=NoteRef("8.14", objects=("Tablo 8.7",)),
        explanation=(
            f"{story} Kâr $\\Pi = {_linear(a, b, 'X', tex=True)}$ (TL) olarak tanımlanır; $X$'in her değerinde o "
            "değerin olasılığıyla gerçekleşir. Beklenen kâr kâr dağılımından ya da doğrusal dönüşüm kuralıyla, "
            "$E(aX - b) = aE(X) - b$, bulunur."
        ),
        operations=(
            Derive("dagilim", names["kar"], E.add(E.roundto(E.sub(E.mul(a, E.var(x)), b), 4), 0),
                   f"π = {profit} (TL); 4 basamağa yuvarlanıp 0 eklenir: kayan nokta artığı (−1e-14) ve −0 kalmaz"),
            ShowFrame("dagilim", (x, names["f"], names["kar"]), "Değerden kâra",
                      decimals=((names["f"], ctx["f_digits"]),
                                (names["kar"], _column_digits(profits.values())))),
            Derive("dagilim", names["kar_f"], E.mul(E.var(names["kar"]), E.var(names["f"])), "π f(x): kâr × olasılık"),
            Statistic("dagilim", names["kar_f"], "sum", "E_Pi", "E(Π): kâr dağılımından, TL", decimals=digits),
            Scalar("E_Pi_dogrusal", E.sub(E.mul(a, E.ref("E_X")), b), f"{linear}, TL", decimals=digits),
            # Kâr yuvarlanmış olduğu için başa baş değer (15 × 8,2 − 123 = 0) zarar sayılmaz.
            Derive("dagilim", names["zarar"], E.compare("lt", E.var(names["kar"]), 0), "Π < 0: zarar göstergesi"),
            Statistic("dagilim", names["f"], "sum", "P_zarar", "P(Π < 0)", where=(names["zarar"], 1),
                      decimals=kesir_basamak(loss)),
        ),
        checks=(
            *(Check(f"π = {profit}, x = {_x(point)}", CellTarget("dagilim", names["kar"], index), 0.0,
                    profit_digits) for index, point in enumerate(dist["points"], start=1)),
            _scalar("E_Pi", "E(Π)", digits),
            _scalar("E_Pi_dogrusal", linear, digits),
            _scalar("P_zarar", "P(Π < 0)", kesir_basamak(loss)),
        ),
        takeaway=(
            f"Beklenen kâr E(Π) {_plain(expected, digits)} TL; aynı sonuç E(aX − b) = aE(X) − b kuralıyla da bulunur. "
            f"{risk} {sign_text}; karar verirken beklenen kâr, zarar olasılığı ve yayılım birlikte değerlendirilir "
            "(§8.14)."
        ),
    )


def build(case: Case) -> LabSpec:
    """Konu 8 uygulamasını verilen veriyle kurar; kontrollerin beklenen değerleri uygulamanın hesabıdır."""

    ctx = _context(case)
    pair = _pair(case, ctx)
    steps = (_step1(case, ctx), _step2(case, ctx), _step3(case, ctx), _step4(case, ctx), _step5(case, ctx),
             _step6(case, ctx), _step7(case, ctx), _step8(case, ctx), _step9(case, ctx, pair),
             _step10(case, ctx, pair), _step11(case, ctx, pair), _step12(case, ctx))
    names = ctx["names"]
    labels = dict(case.labels)
    for key, text in (("sayi", "Gözlem sayısı"), ("f", "f(x)"), ("bilinen", "Bilinen (x < en büyük)"),
                      ("en_kucuk_mu", "En küçük değer mi"), ("en_buyuk_mu", "En büyük değer mi"),
                      ("g", "g(x): karşı örnek"), ("olay", "Olay"), ("xf", "x f(x)"), ("sira", "Sıra"),
                      ("birikimli", "Birikimli ortalama"), ("sapma_kare", "(x − μ)²"),
                      ("agirlikli_kare", "(x − μ)² f(x)"), ("f_B", "f_B(x)"), ("xf_B", "x f_B(x)"),
                      ("kare_B", "(x − μ_B)² f_B(x)"), ("agirlik", "Gözlemin olasılığı 1/n"), ("x_f", "x × 1/n"),
                      ("y_f", "y × 1/n"), ("xy_f", "xy × 1/n"), ("capraz", "(x − μX)(y − μY)/n"),
                      ("x_kare", "(x − μX)²/n"), ("y_kare", "(y − μY)²/n"), ("X_hucre", "X hücresi"),
                      ("Y_hucre", "Y hücresi"), ("hucre", "Hücre"), ("kar", "Kâr π"), ("kar_f", "π f(x)"),
                      ("zarar", "Π < 0")):
        labels.setdefault(names[key], text)
    spec = LabSpec(
        topic_key="konu08",
        title=TITLE,
        note_section="8",
        steps=steps,
        labels=tuple(labels.items()),
        source=case.source,
    )
    return with_app_values(spec)


# --- Alternatif örnek ve kendi verin ---------------------------------------------------------

def _alternative_frame() -> pd.DataFrame:
    return pd.DataFrame(ALT_DAYS, columns=["siparis", "teslim"]).astype(float)


def alternative_case() -> Case:
    return Case(
        source="alternatif",
        load=(InlineData("gunler", ("siparis", "teslim"), ALT_DAYS,
                         "Kurgusal veri: 100 iş günü; online sipariş sayısı ve aynı gün teslim edilen"),),
        frame="gunler",
        data=_alternative_frame(),
        roles={KESIKLI: "siparis", IKINCI: "teslim"},
        labels=ALT_LABELS,
        unit="gün",
        extra={
            "settings": dict(ALT_SETTINGS),
            "read_text": ("Bir çiçekçinin 100 iş gününde gelen online sipariş sayısı ve bunlardan aynı gün teslim "
                          "edilenlerin sayısı kaydedilmiştir."),
            "profit_text": ("Her online sipariş 150 TL katkı sağlar; platform ve kurye için günlük sabit maliyet "
                            "200 TL'dir."),
        },
    )


@cache
def alternative() -> LabSpec:
    return build(alternative_case())


def sample() -> pd.DataFrame:
    """Örnek dosya: alternatif örneğin 100 günü, dosyadaki sırayla (Adım 6'nın birikimli ortalaması bu sırayı izler)."""

    return pd.DataFrame(ALT_DAYS, columns=["siparis", "teslim"]).rename(columns=ALT_LABELS)


def _check_discrete(values: pd.Series, label: str, limit: int) -> None:
    present = values.dropna().astype(float)
    distinct = present.nunique()
    if distinct < 2:
        raise K.UploadError(f"“{label}” sütununda en az iki farklı değer olmalı; olasılık dağılımı tek bir değerle "
                            "kurulamaz.")
    if distinct > limit:
        raise K.UploadError(f"“{label}” sütununda {distinct} farklı değer var; kesikli bir değişken için en çok "
                            f"{limit} farklı değer olmalı (ör. sayımlar). Az sayıda farklı değer alan bir sütun seçin.")
    if (present.abs() >= MAX_ABS).any():
        raise K.UploadError(f"“{label}” sütununda mutlak değerce 1.000.000 ya da daha büyük değerler var; bu uygulama "
                            "küçük değerli kesikli değişkenler içindir.")
    if any(decimal_places(value) > MAX_DECIMALS for value in present.unique()):
        raise K.UploadError(f"“{label}” sütununda dörtten fazla ondalık basamaklı değerler var; kesikli bir değişken "
                            "için en çok dört ondalık basamak kullanılabilir.")


def validate(case: Case) -> None:
    """X kesikli olmalı (2–20 farklı değer); Y seçildiyse X'ten farklı bir sütun ve 2–10 farklı değer."""

    _check_discrete(case.data[case.roles[KESIKLI]], case.label(KESIKLI), MAX_VALUES)
    if case.has(IKINCI):
        if case.roles[IKINCI] == case.roles[KESIKLI]:
            raise K.UploadError("X ve Y için iki farklı sütun seçin: bir değişkenin kendisiyle ortak dağılımı "
                                "köşegendeki hücrelerden ibarettir.")
        _check_discrete(case.data[case.roles[IKINCI]], case.label(IKINCI), MAX_Y_VALUES)


ROLES = (
    Role(KESIKLI, "Kesikli değişken X", "sayisal", True, (1, 2, 3, 4, 5, 6, 7, 8, 12),
         "Az sayıda farklı değer alan sayısal sütun (ör. sepetteki ürün sayısı, günlük sipariş sayısı); göreli "
         "frekansları olasılık fonksiyonu olur. En çok 20 farklı değer."),
    Role(IKINCI, "İkinci kesikli değişken Y", "sayisal", False, (9, 10, 11),
         "X ile birlikte gözlenen ikinci kesikli sütun (ör. teslim edilen sipariş sayısı); ortak dağılım X ve Y'den "
         "kurulur. En çok 10 farklı değer."),
)

SETTINGS = (
    Setting(KATKI, "Birim katkı a (TL)", 1, 1000, lambda data, roles: ALT_SETTINGS[KATKI],
            "X'in her birimi için kâra katkı.", steps=(12,)),
    Setting(SABIT, "Sabit maliyet b (TL)", 0, 10000, lambda data, roles: ALT_SETTINGS[SABIT],
            "Dönemlik sabit maliyet; kâr Π = aX − b.", steps=(12,)),
)

CUSTOM = CustomLab(
    roles=ROLES,
    build=build,
    sample=sample,
    intro=(
        "Kesikli bir sayısal sütun içeren bir Excel (.xlsx) ya da CSV dosyası yükleyin: sütunun göreli frekansları "
        "olasılık fonksiyonu olur (Adım 1–8 ve 12). İkinci bir kesikli sütun seçerseniz ortak dağılım, kovaryans ve "
        "bağımsızlık adımları (9–11) iki sütundan kurulur. Adım 12'nin birim katkısını ve sabit maliyetini "
        "kaydırıcılarla değiştirebilirsiniz. X'i boş olan satırlar analizden çıkarılır; Y'si boş olanlar yalnız "
        "Adım 9–11'de kullanılmaz."
    ),
    min_rows=5,
    validate=validate,
    settings=SETTINGS,
)

VARIANTS = TopicVariants(alternative=alternative, story=STORY, custom=CUSTOM)
