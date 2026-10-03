"""Konu 4 genel uygulaması: bir veri setinin merkezini ve göreli konumları özetlemek.

Ders notlarındaki adımlar (§4.2–§4.12) aynı numaralarla, verisi değiştirilebilir biçimde yazılır. Notlarda her adımın
kendi küçük veri seti vardır; genel uygulamada aynı ölçüler tek bir sayısal değişken üzerinde hesaplanır. Ağırlıklı
ortalama (Adım 3) kategorik bir sütunun gruplarıyla, geometrik ortalama (Adım 9) dönemlik yüzde değişimlerle kurulur.
Alternatif örnek kurgusal bir kira veri setidir; "kendi verini yükle" seçeneğinde aynı adımlar öğrencinin dosyasıyla
kurulur.
Notlardaki uygulama (``core.labs.konu04``) değişmez.

Uç değer (Adım 2): en büyük gözlem x_max + 3(x_max − x_min) yapılır; notlardaki 26 → 56 aynı kuralla çıkar.
Yüzdelikler notlardaki kuralla hesaplanır: L_p = (p/100)(n + 1), tam sayı değilse doğrusal ara değer.

Metindeki sayılar, "=" ile "≈" ayrımı ve "ortalama veride gözlenir mi" gibi yargılar verinin kesin ondalık
değerlerinden kurulur (``ornek.kesin``); tablolar ve kontroller uygulamanın kayan noktalı hesabıdır. Gösterim basamağı:
veriden doğrudan gelen değerler (toplam, en küçük, en büyük, mod) verinin basamağı d ile; medyan, yüzdelik ve çeyrekler
kesin değerleriyle (en çok d + 2 basamak); bölmeyle bulunan değerler (ortalamalar) en az 2, d + 1 ve 3 anlamlı
basamakla yazılır. Gösterilen anlamlı basamak 15'i aşmaz (kayan noktalı hesabın güvenilir basamağı).
"""

from __future__ import annotations

import math
from decimal import ROUND_CEILING, ROUND_FLOOR, Context, Decimal, localcontext
from functools import cache

import numpy as np
import pandas as pd

from core.labs import expr as E
from core.labs import kendi_veri as K
from core.labs.ornek import (
    Case,
    CustomLab,
    Role,
    SeparateColumn,
    TopicVariants,
    free_name,
    kesin,
    kesin_esit,
    kesin_yuvarla,
    kisa,
    md,
    ondalik,
    ondalik_tex,
    sayilar,
    with_app_values,
    yarim_basamak,
)
from core.labs.ornek_konu03 import MAX_DOTS, data_decimals, significant
from core.labs.spec import (
    BarChart,
    CellTarget,
    Check,
    CompleteCases,
    Count,
    Derive,
    DotPlot,
    GroupSummary,
    Histogram,
    InlineData,
    LabSpec,
    LabStep,
    NoteRef,
    Percentile,
    ReplaceMax,
    Scalar,
    ScalarTable,
    ScalarTarget,
    ShowFrame,
    Statistic,
)

TITLE = "Merkezi eğilim ve konum ölçülerini hesaplamak"
SAYISAL, GRUP, BUYUME = "sayisal", "grup", "buyume"
OUTLIER = 3
"""Uç değer: en büyük gözlem, değişim aralığının üç katı kadar büyütülür (notlarda 26 + 3 × 10 = 56)."""
NARROW = Decimal("0.5")
"""Adım 10: türetilen sette her gözlem ortalamaya olan uzaklığının yarısına çekilir."""
HISTOGRAM_BINS = 30
MAX_LISTED = 10
"""Ortalama ve medyan açıklamasında değerler bu sayıya kadar tek tek yazılır."""
MAX_MODES = 5
PRECISION = 15
"""Metinde gösterilen en çok anlamlı basamak."""
_EXACT = Context(prec=60)

ALT_ROWS = (
    (25, "2+1"), (18, "1+1"), (32, "3+1"), (22, "2+1"), (15, "1+1"), (27, "2+1"), (42, "3+1"), (20, "1+1"),
    (25, "2+1"), (35, "3+1"), (17.5, "1+1"), (28, "2+1"), (22, "1+1"), (30, "3+1"), (25, "2+1"),
)
"""Kurgusal veri: bir mahallede kiraya verilen 15 dairenin aylık kirası (bin TL) ve oda sayısı, ilan sırasıyla."""
ALT_GROWTH = (("1. yıl", 45), ("2. yıl", 30), ("3. yıl", 18), ("4. yıl", 12))
"""Kurgusal veri: aynı mahallede ortalama kiranın son dört yıldaki yıllık artışı (%)."""
ALT_LABELS = {
    "kira": "Aylık kira (bin TL)",
    "oda": "Oda sayısı",
    "yil": "Yıl",
    "artis": "Yıllık kira artışı (%)",
}
STORY = (
    "Kurgusal veri: bir mahallede kiraya verilen 15 dairenin aylık kirası (bin TL) ve oda sayısı; ayrıca mahallede "
    "ortalama kiranın son dört yıldaki yıllık artışı (%)."
)


# --- Kesin değerler ve yazım ---------------------------------------------------------------

def _room(value: Decimal) -> int:
    """``PRECISION`` anlamlı basamağa sığan en çok ondalık basamak."""

    if value.is_zero():
        return PRECISION
    return max(0, PRECISION - 1 - value.adjusted())


def _exact_digits(value: Decimal) -> int:
    """Kesin değerin (medyan, yüzdelik, konum) bütün ondalık basamakları; güvenilir sınır içinde."""

    places = 0 if value.is_zero() else max(0, -value.normalize(_EXACT).as_tuple().exponent)
    return min(places, _room(value))


def _mean_digits(value: Decimal, d: int) -> int:
    """Bölmeyle bulunan değerin (ortalama gibi) gösterim basamağı: en az 2, verinin basamağından bir fazla ve 3 anlamlı
    basamak; değer iki gösterimin tam ortasındaysa bir basamak daha (``yarim_basamak``)."""

    base = max(2, d + 1, significant(float(value), 3))
    return min(yarim_basamak(value, base), _room(value))


def _exact_data(values, d: int) -> list[Decimal]:
    """Verinin metindeki kesin değerleri: kısa ondalık yazım, d basamakta (d en büyük değerin 15 anlamlı basamağıyla
    sınırlı; yalnız kayan nokta gürültüsü kesilir). Bütün metin hesapları bu değerlerle yapılır."""

    return [kesin_yuvarla(kesin(value), d) for value in values]


def _math(value: Decimal, digits: int) -> str:
    return ondalik_tex(value, digits)


def _term(value: Decimal, digits: int) -> str:
    """İşlemin sağındaki sayı (matematik içinde): negatifse parantezle."""

    shown = _math(value, digits)
    return f"({shown})" if shown.startswith("−") else shown


def _about(value: Decimal, digits: int, prefix: str = "") -> str:
    """Düzyazıdaki sayı; yuvarlanmışsa başında "yaklaşık" (``prefix``: ör. yüzde işareti)."""

    text = prefix + ondalik(value, digits)
    return text if kesin_esit(value, digits) == "=" else f"yaklaşık {text}"


def _percentile(ordered: list[Decimal], p: int, rule: str = "ders") -> tuple[Decimal, Decimal]:
    """Kesin yüzdelik ve konumu. ``ders``: L_p = (p/100)(n + 1), uçlarda en küçük ya da en büyük gözlem (notlar).
    ``yazilim``: numpy ve R'nin varsayılanı, konum 1 + (p/100)(n − 1)."""

    n = len(ordered)
    with localcontext(_EXACT):
        share = Decimal(p) / 100
        location = share * (n + 1) if rule == "ders" else 1 + share * (n - 1)
        if location <= 1:
            return ordered[0], location
        if location >= n:
            return ordered[-1], location
        k = int(location)
        a, b = ordered[k - 1], ordered[k]
        return a + (location - k) * (b - a), location


# --- Yardımcılar -------------------------------------------------------------------------

def _scalar(name: str, label: str, decimals: int = 0) -> Check:
    return Check(label, ScalarTarget(name), 0.0, decimals)


def _missing(step: int, title: str, note: str, roles: str) -> LabStep:
    return LabStep(number=step, title=title, note=NoteRef(note),
                   explanation=f"Bu adım için yukarıdaki veri panelinden şu rol için sütun seçin: {roles}.")


def _blocked(step: int, title: str, note: str, reason: str) -> LabStep:
    return LabStep(number=step, title=title, note=NoteRef(note), explanation=reason)


def _complete(case: Case, columns: tuple[str, ...], name: str, comment: str):
    """Seçilen sütunların hepsinde değeri olan gözlemler; boş hücre yoksa ana veri kullanılır."""

    subset = case.data.dropna(subset=list(columns)).reset_index(drop=True)
    if len(subset) == len(case.data):
        return case.frame, subset, ()
    return name, subset, (CompleteCases(name, case.frame, columns, comment),)


def _axis(low: float, high: float) -> tuple[float, float]:
    """İki grafiğin ortak yatay ekseni: en küçük ve en büyük değerin biraz dışında, kolay okunan sınırlar. Çok büyük
    değerlerde kolay sınır kayan noktalı sayıda gözlemle çakışabilir; o zaman sınır bir adım dışarı itilir."""

    low_d, high_d = kesin(low), kesin(high)
    with localcontext(_EXACT):
        span = high_d - low_d
        pad = span / 20 if span > 0 else Decimal(1)
        step = Decimal(1).scaleb(pad.adjusted())
        lower = ((low_d - pad) / step).to_integral_value(rounding=ROUND_FLOOR) * step
        upper = ((high_d + pad) / step).to_integral_value(rounding=ROUND_CEILING) * step
    lower_f, upper_f = float(lower), float(upper)
    if not lower_f < low:
        lower_f = math.nextafter(low, -math.inf)
    if not upper_f > high:
        upper_f = math.nextafter(high, math.inf)
    return lower_f, upper_f


def _spread_plot(case: Case, frame: str, column: str, x_label: str, title: str,
                 references: tuple[tuple[str, str], ...], x_range: tuple[float, float] | None, n: int,
                 low: float, high: float, range_note: str | None = None):
    """Nokta grafiği; büyük veride (n > 300) aynı başvuru çizgileriyle histogram. ``range_note``: sabit yatay eksenin
    koddaki açıklaması (verilmezse "karşılaştırılan grafiklerde aynı yatay eksen")."""

    if n <= MAX_DOTS:
        if range_note is not None:
            return DotPlot(frame, column, x_label, title, references=references, x_range=x_range,
                           range_note=range_note)
        return DotPlot(frame, column, x_label, title, references=references, x_range=x_range)
    lower, upper = x_range if x_range is not None else _axis(low, high)
    return Histogram(frame, ((column, "Gözlemler"),), HISTOGRAM_BINS, lower, upper, title, x_label,
                     references=references, y_label="Gözlem sayısı", hover_unit="gözlem")


# --- Ortak hesaplar ------------------------------------------------------------------------

def _context(case: Case) -> dict:
    x = case.roles[SAYISAL]
    values = case.data[x].astype(float)
    n = len(values)
    d = data_decimals(values)
    xs = _exact_data(values, d)
    ordered = sorted(xs)
    with localcontext(_EXACT):
        total = sum(xs, Decimal(0))
        mean = total / n
        middle = n // 2
        median = ordered[middle] if n % 2 else (ordered[middle - 1] + ordered[middle]) / 2
        low, high = ordered[0], ordered[-1]
        outlier = high + OUTLIER * (high - low)
        new_total = total - high + outlier
        new_mean = new_total / n
        shift = (outlier - high) / n
        narrow_median = mean + NARROW * (median - mean)
    low_f, high_f = float(values.min()), float(values.max())
    outlier_f = high_f + OUTLIER * (high_f - low_f)  # uygulamanın hesabıyla aynı sıra (eksen sınırları için)
    taken = set(case.data.columns) | set(case.labels)
    return {
        "x": x, "values": values, "n": n, "d": d, "label": case.label(SAYISAL), "xs": xs, "ordered": ordered,
        "total": total, "mean": mean, "median": median, "low": low, "high": high, "outlier": outlier,
        "new_total": new_total, "new_mean": new_mean, "shift": shift, "narrow_median": narrow_median,
        "mean_digits": _mean_digits(mean, d), "median_digits": _exact_digits(median),
        "new_mean_digits": _mean_digits(new_mean, d),
        "low_f": low_f, "high_f": high_f, "outlier_f": outlier_f,
        "outlier_axis": _axis(low_f, outlier_f), "axis": _axis(low_f, high_f),
        "narrow": free_name(f"{x}_dar", taken), "factor": free_name("faktor", taken),
    }


# --- Adımlar -------------------------------------------------------------------------------

def _step1(case: Case, ctx: dict) -> LabStep:
    x, n, d, label = ctx["x"], ctx["n"], ctx["d"], ctx["label"]
    total, mean, digits = ctx["total"], ctx["mean"], ctx["mean_digits"]
    shown_total = _math(total, d)
    if n <= MAX_LISTED:
        terms = " + ".join(_term(value, d) if index else _math(value, d) for index, value in enumerate(ctx["xs"]))
        formula = (f"$({terms})/{n} {kesin_esit(total, d)} {shown_total}/{n} {kesin_esit(mean, digits)} "
                   f"{_math(mean, digits)}$")
    else:
        formula = (f"$\\sum x_i {kesin_esit(total, d)} {shown_total}$ ve $n = {n}$ olduğundan $\\bar{{x}} "
                   f"{kesin_esit(total, d)} {shown_total}/{n} {kesin_esit(mean, digits)} {_math(mean, digits)}$")
    intro = case.extra.get("read_text") or f"“{md(label)}” sütunundaki {n} değer okunur."
    observed = mean in set(ctx["xs"])
    where = ("bu değer veride de gözlenen bir değerdir; yine de ortalama" if observed else
             "bu değer gözlemler arasında yoktur. Ortalama")
    plot = ("Nokta grafiğinde ortalama, bütün noktaları dengede tutan destek noktası gibi düşünülebilir."
            if n <= MAX_DOTS else
            "Histogramda ortalama, bütün çubukları dengede tutan destek noktası gibi düşünülebilir.")
    return LabStep(
        number=1,
        title="Aritmetik ortalama",
        note=NoteRef("4.2"),
        explanation=f"{intro} Ortalama $\\bar{{x}} = \\sum x_i / n$ ile bulunur: {formula}. {plot}",
        operations=(
            *case.load,
            Statistic(case.frame, x, "sum", "toplam", "Değerlerin toplamı", decimals=d),
            Statistic(case.frame, x, "count", "n", "Gözlem sayısı n", decimals=0),
            Scalar("ortalama", E.div(E.ref("toplam"), E.ref("n")), "Ortalama x̄", decimals=digits),
            _spread_plot(case, case.frame, x, label, "Ortalama bir denge noktasıdır", (("ortalama", "Ortalama"),),
                         None, n, ctx["low_f"], ctx["high_f"]),
        ),
        checks=(_scalar("toplam", "Değerlerin toplamı", d), _scalar("ortalama", "Ortalama", digits)),
        takeaway=(
            f"Ortalama {_about(mean, digits)}; {where} gözlemlerin toplamını korur, “en sık görülen” veya “ortadaki "
            "gözlem” anlamına gelmez (§4.2)."
        ),
    )


def _step2(case: Case, ctx: dict) -> LabStep:
    x, n, d, label = ctx["x"], ctx["n"], ctx["d"], ctx["label"]
    low, high, outlier = ctx["low"], ctx["high"], ctx["outlier"]
    total, new_total, new_mean, shift = ctx["total"], ctx["new_total"], ctx["new_mean"], ctx["shift"]
    digits, new_digits = ctx["mean_digits"], ctx["new_mean_digits"]
    shift_digits = _mean_digits(shift, d)
    frame = "veri_uc"
    return LabStep(
        number=2,
        title="Uç değerin ortalamaya etkisi",
        note=NoteRef("4.3"),
        explanation=(
            f"En büyük gözlem {ondalik(high, d)} yerine ${_math(high, d)} + 3 \\times ({_math(high, d)} - "
            f"{_term(low, d)}) {kesin_esit(outlier, d)} {_math(outlier, d)}$ olsun. Toplam {_about(total, d)} "
            f"değerinden {_about(new_total, d)} değerine çıkar ve ortalama ${_math(new_total, d)}/{n} "
            f"{kesin_esit(new_mean, new_digits)} {_math(new_mean, new_digits)}$ olur: tek bir gözlemin değişmesi "
            f"ortalamayı {_about(ctx['mean'], digits)} değerinden {_about(new_mean, new_digits)} değerine taşır. "
            f"Artış, değişimin gözlem sayısına bölümüdür: $({_math(outlier, d)} - {_term(high, d)})/{n} "
            f"{kesin_esit(shift, shift_digits)} {_math(shift, shift_digits)}$; gözlem sayısı büyüdükçe tek bir "
            "gözlemin etkisi küçülür."
        ),
        operations=(
            Statistic(case.frame, x, "min", "en_kucuk", "En küçük değer", decimals=d),
            Statistic(case.frame, x, "max", "en_buyuk", "En büyük değer", decimals=d),
            Scalar("uc_deger", E.add(E.ref("en_buyuk"), E.mul(OUTLIER, E.sub(E.ref("en_buyuk"), E.ref("en_kucuk")))),
                   "Yeni en büyük değer", decimals=d),
            ReplaceMax(frame, case.frame, x, "uc_deger", "Uç değerli veri"),
            Statistic(frame, x, "sum", "toplam_uc", "Uç değerli toplam", decimals=d),
            Scalar("ortalama_uc", E.div(E.ref("toplam_uc"), E.ref("n")), "Yeni ortalama x̄", decimals=new_digits),
            _spread_plot(case, frame, x, label, "Tek bir büyük değer ortalamayı sağa çeker",
                         (("ortalama_uc", "Yeni ortalama"), ("ortalama", "İlk ortalama")), ctx["outlier_axis"], n,
                         ctx["low_f"], ctx["outlier_f"]),
        ),
        checks=(_scalar("uc_deger", "Yeni en büyük değer", d), _scalar("toplam_uc", "Uç değerli toplam", d),
                _scalar("ortalama_uc", "Uç değerli ortalama", new_digits)),
        takeaway=(
            "Ortalama uç değerlere duyarlıdır. Bu, ortalamanın yanlış olduğu anlamına gelmez; amaç tipik bir gözlemi "
            "betimlemekse medyana da bakılmalıdır (§4.3)."
        ),
    )


def group_names(case: Case) -> dict[str, str]:
    """Adım 3'ün grup çerçevesindeki sütun adları; dosyadaki sütun adlarıyla çakışmaz (etiketleri karışmaz)."""

    taken = set(case.data.columns) | set(case.labels)
    names = {}
    for key in ("n", "ortalama", "agirlik", "katki", "agirlik_yuzde"):
        names[key] = free_name(key, taken)
        taken.add(names[key])
    return names


def _step3(case: Case, ctx: dict) -> LabStep:
    title, note = "Ağırlıklı ortalama", "4.4"
    if not case.has(GRUP):
        return _missing(3, title, note, "“Grup sütunu (kategorik)”, ör. bölüm ya da oda sayısı")
    x, g, d = ctx["x"], case.roles[GRUP], ctx["d"]
    g_label = case.label(GRUP)
    names = group_names(case)
    count, mean, weight, part, percent = (names[key] for key in ("n", "ortalama", "agirlik", "katki", "agirlik_yuzde"))
    frame, data, load = _complete(case, (x, g), "veri_grup",
                                  "Ağırlıklı ortalama için iki sütunda da değeri olan gözlemler")
    groups = data[g].astype(str).to_numpy()
    found = set(groups)
    order = tuple(item for item in case.orders[g] if item in found)
    sizes = dict.fromkeys(order, 0)
    sums = dict.fromkeys(order, Decimal(0))
    used = len(data)
    with localcontext(_EXACT):
        for value, group in zip(_exact_data(data[x].astype(float), d), groups):
            sizes[group] += 1
            sums[group] += value
        means = {group: sums[group] / sizes[group] for group in order}
        parts = {group: sums[group] / used for group in order}  # wⱼ x̄ⱼ = (nⱼ/n)(Σⱼ x/nⱼ)
        weighted = sum(sums.values(), Decimal(0)) / used
        simple = sum(means.values(), Decimal(0)) / len(order)
        first = order[0]
        first_weight = Decimal(sizes[first]) / used
    group_digits = max(_mean_digits(value, d) for value in (*means.values(), *parts.values()))
    weighted_digits, simple_digits = _mean_digits(weighted, d), _mean_digits(simple, d)
    weight_digits = _mean_digits(first_weight, 2)
    skipped = len(case.data) - used
    if skipped:
        base = f"bu adımdaki {used} gözlemin ortalamasıdır ({skipped} gözlemde grup sütunu boş)"
        whose = "bu gözlemlerin"
    else:
        base = "Adım 1'deki ortalamaya eşittir"
        whose = "bütün gözlemlerin"
    simple_text = _about(simple, simple_digits)
    if len(set(sizes.values())) == 1:
        compare = ("Grup büyüklükleri eşit olduğu için grup ortalamalarının basit ortalaması da aynı sonucu verir "
                   f"({simple_text}).")
    elif simple == weighted:
        compare = (f"Grup ortalamalarının basit ortalaması da bu veride aynı sonucu verir ({simple_text}); grup "
                   "büyüklükleri farklı olduğu için bu genel bir kural değildir.")
    else:
        compare = (f"Grup ortalamalarının basit ortalaması ({simple_text}) ise her grubu aynı ağırlıkla sayar; grup "
                   "büyüklükleri farklı olduğu için iki sonuç ayrılır.")
    checks = []
    for index, group in enumerate(order, start=1):
        checks.append(Check(f"{group}: grup ortalaması", CellTarget("gruplar", mean, index), 0.0, group_digits))
        checks.append(Check(f"{group}: katkı wⱼ x̄ⱼ", CellTarget("gruplar", part, index), 0.0, group_digits))
    checks += [_scalar("toplam_agirlik", "Ağırlıkların toplamı", 2),
               _scalar("agirlikli_ortalama", "Ağırlıklı ortalama", weighted_digits),
               _scalar("basit_ortalama", "Grup ortalamalarının basit ortalaması", simple_digits)]
    return LabStep(
        number=3,
        title=title,
        note=NoteRef(note),
        explanation=(
            f"“{md(g_label)}” sütununun her grubu için ortalama $\\bar{{x}}_j$ hesaplanır. Ağırlık grubun payıdır, "
            "$w_j = n_j/n$; katkı $w_j \\bar{x}_j$ ve ağırlıklı ortalama "
            "$\\bar{x}_w = \\sum w_j \\bar{x}_j / \\sum w_j$. "
            f"Örneğin {md(first)} grubunda $n_j = {sizes[first]}$ ve $w = {sizes[first]}/{used} "
            f"{kesin_esit(first_weight, weight_digits)} {_math(first_weight, weight_digits)}$. Ağırlıkların toplamı 1 "
            "olduğundan payda 1'dir."
        ),
        operations=(
            *load,
            GroupSummary(frame, g, ((count, x, "count"), (mean, x, "mean")), "gruplar", order,
                         decimals=group_digits, as_frame=True),
            Statistic("gruplar", count, "sum", "toplam_n", "Gözlem sayısı n", decimals=0),
            Derive("gruplar", weight, E.div(E.var(count), E.ref("toplam_n")), "Ağırlık wⱼ = nⱼ / n"),
            Derive("gruplar", part, E.mul(E.var(weight), E.var(mean)), "Katkı wⱼ x̄ⱼ"),
            Statistic("gruplar", part, "sum", "toplam_katki", "Katkıların toplamı", decimals=weighted_digits),
            Statistic("gruplar", weight, "sum", "toplam_agirlik", "Ağırlıkların toplamı Σwⱼ", decimals=2),
            Scalar("agirlikli_ortalama", E.div(E.ref("toplam_katki"), E.ref("toplam_agirlik")),
                   "Ağırlıklı ortalama x̄w", decimals=weighted_digits),
            Statistic("gruplar", mean, "mean", "basit_ortalama", "Basit ortalama (gruplar)", decimals=simple_digits),
            ShowFrame("gruplar", (g, count, mean, weight, part), "Gruplar: gözlem sayısı, ortalama, ağırlık ve katkı"),
            Derive("gruplar", percent, E.mul(100, E.var(weight)), "Ağırlık yüzde olarak"),
            BarChart("gruplar", percent, g_label, "Ağırlık (%)", "Her grubun ağırlığı", x=g, percent=True,
                     decimals=1),
        ),
        checks=tuple(checks),
        takeaway=(
            f"Ağırlıklı ortalama ({_about(weighted, weighted_digits)}) {base}: grup ortalamaları grup büyüklükleriyle "
            f"ağırlıklandırılınca {whose} ortalaması geri gelir. {compare} Ağırlıklar 0,25 biçiminde kullanılıyorsa "
            "bir kez daha 100'e bölünmez (§4.4)."
        ),
    )


def _sorted_text(values: list[Decimal], positions: tuple[int, ...], d: int) -> str:
    """Sıralı değerler; ortadaki değer(ler) çerçeveli (notlardaki gibi)."""

    items = [f"\\boxed{{{_math(value, d)}}}" if index in positions else _math(value, d)
             for index, value in enumerate(values, start=1)]
    return "$" + ",\\quad ".join(items) + "$"


def _step4(case: Case, ctx: dict) -> LabStep:
    x, n, d = ctx["x"], ctx["n"], ctx["d"]
    ordered, median, digits = ctx["ordered"], ctx["median"], ctx["median_digits"]
    if n % 2:
        position = (n + 1) // 2
        positions = (position,)
        rule = f"$n = {n}$ tek olduğu için medyan sıralı verinin {position}. değeridir: ${_math(median, digits)}$."
        result = "Gözlem sayısı tek olduğu için medyan veride gözlenen bir değerdir."
    else:
        position = n // 2
        positions = (position, position + 1)
        a, b = ordered[position - 1], ordered[position]
        rule = (f"$n = {n}$ çift olduğu için medyan ortadaki iki değerin, {position}. ve {position + 1}. değerlerin "
                f"ortalamasıdır: $({_math(a, d)} + {_term(b, d)})/2 {kesin_esit(median, digits)} "
                f"{_math(median, digits)}$.")
        observed = median in set(ordered)
        result = ("Çift sayıda gözlemde medyan veri setinde gözlenmiş bir değer olmak zorunda değildir"
                  + ("; bu veride gözlenen bir değerdir." if observed else "; bu veride gözlenmemiştir."))
    listing = f" Sıralı veri: {_sorted_text(ordered, positions, d)}." if n <= 15 else ""
    return LabStep(
        number=4,
        title="Medyan",
        note=NoteRef("4.5"),
        explanation=(
            "Medyan sıralanmış verinin ortasındaki konumdur: $n$ tek ise tam ortadaki gözlem, $n$ çift ise ortadaki "
            f"iki gözlemin ortalaması. Medyandan önce veri mutlaka sıralanır. {rule}{listing}"
        ),
        operations=(Statistic(case.frame, x, "median", "medyan", "Medyan", decimals=digits),),
        checks=(_scalar("medyan", "Medyan", digits),),
        takeaway=f"{result} Medyan büyüklükten çok sıralamadaki konuma dayanır (§4.5).",
    )


def _step5(case: Case, ctx: dict) -> LabStep:
    x, d, label = ctx["x"], ctx["d"], ctx["label"]
    median, median_digits = ctx["median"], ctx["median_digits"]
    digits, new_digits = ctx["mean_digits"], ctx["new_mean_digits"]
    return LabStep(
        number=5,
        title="Ortalama ve medyanın karşılaştırılması",
        note=NoteRef("4.6"),
        explanation=(
            f"Medyan {_about(median, median_digits)}, ortalama {_about(ctx['mean'], digits)}. En büyük gözlem "
            f"{_about(ctx['outlier'], d)} olduğunda ortalama {_about(ctx['new_mean'], new_digits)} değerine çıkar; "
            f"medyan yine {_about(median, median_digits)}."
        ),
        operations=(
            Statistic("veri_uc", x, "median", "medyan_uc", "Uç değerli medyan", decimals=median_digits),
            ScalarTable(
                (
                    ("İlk veri: ortalama", E.ref("ortalama")),
                    ("İlk veri: medyan", E.ref("medyan")),
                    ("Uç değerle: ortalama", E.ref("ortalama_uc")),
                    ("Uç değerle: medyan", E.ref("medyan_uc")),
                ),
                "karsilastirma",
                decimals=max(digits, median_digits, new_digits),
            ),
            _spread_plot(case, "veri_uc", x, label, "Uç değer karşısında medyan ve ortalama",
                         (("medyan_uc", "Medyan"), ("ortalama_uc", "Ortalama")), ctx["outlier_axis"], ctx["n"],
                         ctx["low_f"], ctx["outlier_f"]),
        ),
        checks=(_scalar("medyan_uc", "Uç değerli medyan", median_digits),),
        takeaway=(
            "Ortalama bütün büyüklükleri kullandığı için sağa kayar; medyan sıradaki konuma dayandığı için değişmez. "
            "Sağa çarpık gelir, servet veya konut fiyatında ikisini birlikte raporlamak daha bilgilendiricidir (§4.6)."
        ),
    )


def _step6(case: Case, ctx: dict) -> LabStep:
    x, values, d = ctx["x"], ctx["values"], ctx["d"]
    counts = values.value_counts()
    top = int(counts.max())
    modes = sorted(float(value) for value in counts[counts == top].index)
    distinct = len(counts)
    operations = [Statistic(case.frame, x, "mode_freq", "mod_frekansi", "En yüksek frekans", decimals=0)]
    checks = [_scalar("mod_frekansi", "En yüksek frekans")]
    if len(modes) == distinct:
        times = "bir kez" if top == 1 else f"{top} kez"
        text = (f"Bütün değerler aynı sıklıkta ({times}) gözlenir: ayırt edici bir mod yoktur." +
                (" Sürekli ölçülen değişkenlerde bu durum olağandır; Konu 3'teki en yoğun sınıf bu durumda yararlı bir "
                 "özettir." if top == 1 else ""))
    elif len(modes) == 1:
        others = int(counts[counts < top].max())
        shown = ondalik(kesin(modes[0]), d)
        operations.insert(0, Statistic(case.frame, x, "mode", "mod", "Mod", decimals=d))
        checks.insert(0, _scalar("mod", "Mod", d))
        text = f"{shown} değeri {top} kez gözlenir; diğer değerler en çok {others} kez. Mod {shown}."
    else:
        shown = [ondalik(kesin(value), d) for value in modes[:MAX_MODES]]
        for index, (value, number) in enumerate(zip(modes, shown), start=1):
            operations.append(Count(case.frame, f"mod_{index}", x, value, f"{number} değerinin frekansı"))
            checks.append(_scalar(f"mod_{index}", f"{number} değerinin frekansı"))
        kind = "Veri iki modludur." if len(modes) == 2 else f"Veri çok modludur ({len(modes)} mod)."
        if len(modes) > MAX_MODES:
            separator = "; " if any("," in number for number in shown) else ", "
            listed = f"{separator.join(shown)} ve diğer {len(modes) - MAX_MODES} değerin her biri {top} kez gözlenir."
        else:
            listed = f"{sayilar(shown)} değerlerinin her biri {top} kez gözlenir."
        text = f"{listed} {kind}"
    has_mode = len(modes) < distinct
    plot = "Adım 1'deki nokta grafiğinde mod en yüksek yığındır." if ctx["n"] <= MAX_DOTS and has_mode else ""
    return LabStep(
        number=6,
        title="Mod",
        note=NoteRef("4.7"),
        explanation=f"Mod en yüksek frekansla gözlenen değerdir. {text} {plot}".strip(),
        operations=tuple(operations),
        checks=tuple(checks),
        takeaway=(
            "Bir veri setinde bir mod, birden fazla mod veya hiç ayırt edici mod bulunmayabilir. Mod, en sık tercih "
            "edilen ödeme yöntemi gibi nominal kategorik veride de anlamlıdır (§4.7)."
        ),
    )


def _location_text(ordered: list[Decimal], p: int, d: int) -> str:
    """Yüzdelik konumu ve değeri: L_p = (p/100)(n + 1), komşu iki gözlem arasında doğrusal ara değer."""

    n = len(ordered)
    value, location = _percentile(ordered, p)
    digits = _exact_digits(value)
    head = (f"$L_{{{p}}} = {_math(Decimal(p) / 100, 2)} \\times {n + 1} = "
            f"{_math(location, _exact_digits(location))}$")
    if location <= 1:
        return f"{head}; konum 1 ya da altında olduğu için $P_{{{p}}}$ en küçük gözlemdir"
    if location >= n:
        return f"{head}; konum n ya da üstünde olduğu için $P_{{{p}}}$ en büyük gözlemdir"
    k = int(location)
    fraction = location - k
    if fraction == 0:
        return f"{head} tam sayı olduğundan $P_{{{p}}}$ sıralı verinin {k}. değeridir: ${_math(value, digits)}$"
    a, b = ordered[k - 1], ordered[k]
    return (f"{head}: {k}. değer {ondalik(a, d)}, {k + 1}. değer {ondalik(b, d)} olduğundan "
            f"$P_{{{p}}} = {_math(a, d)} + {_math(fraction, 2)}\\,({_math(b, d)} - {_term(a, d)}) "
            f"{kesin_esit(value, digits)} {_math(value, digits)}$")


def _step7(case: Case, ctx: dict) -> LabStep:
    x, n, d = ctx["x"], ctx["n"], ctx["d"]
    ordered = ctx["ordered"]
    value, location = _percentile(ordered, 60)
    digits = _exact_digits(value)
    software, _ = _percentile(ordered, 60, "yazilim")
    other = ("bu veride iki kural aynı sonucu verir" if software == value else
             f"bu veride {_about(software, _exact_digits(software))}")
    sign = "=" if kesin_esit(value, digits) == "=" else "≈"
    return LabStep(
        number=7,
        title="Yüzdelikler: göreli konum",
        note=NoteRef("4.8"),
        explanation=(
            "Bu derste yüzdelik konumu $L_p = \\frac{p}{100}(n + 1)$ ile bulunur; $L_p$ tam sayı değilse komşu iki "
            f"gözlem arasında doğrusal ara değer alınır. $n = {n}$ için {_location_text(ordered, 60, d)}."
        ),
        operations=(Percentile(case.frame, x, 60, "P60", "60. yüzdelik P₆₀", location="L60", decimals=digits),),
        checks=(_scalar("L60", "Konum L₆₀", _exact_digits(location)), _scalar("P60", "60. yüzdelik P₆₀", digits)),
        code_note=(
            "numpy'nin np.percentile ve R'nin quantile fonksiyonları varsayılan olarak başka bir kural kullanır "
            f"({other}). Notlardaki kural numpy'de method=\"weibull\", R'de type = 6 ile aynıdır; kod karışıklık "
            "olmasın diye kuralı açıkça yazar."
        ),
        takeaway=(
            "Bir sonucun 80. yüzdelikte olması değerin 80 olduğu anlamına gelmez; gözlemlerin yaklaşık %80'inin "
            f"altında kaldığı konumu anlatır. P₆₀ {sign} {ondalik(value, digits)} değerinin altında gözlemlerin "
            "yaklaşık %60'ı vardır (§4.8)."
        ),
    )


def _step8(case: Case, ctx: dict) -> LabStep:
    x, n, d, label = ctx["x"], ctx["n"], ctx["d"], ctx["label"]
    ordered = ctx["ordered"]
    (q1, l25), (q2, _), (q3, l75) = (_percentile(ordered, p) for p in (25, 50, 75))
    digits = max(_exact_digits(q1), _exact_digits(q2), _exact_digits(q3))
    with localcontext(_EXACT):
        lower_gap, upper_gap = q2 - q1, q3 - q2
    gap_digits = max(_exact_digits(lower_gap), _exact_digits(upper_gap))
    if lower_gap == upper_gap:
        gaps = f"Q₁ ile Q₂ arası ve Q₂ ile Q₃ arası aynı uzunluktadır, {_about(lower_gap, gap_digits)} birim"
    else:
        gaps = (f"Q₁ ile Q₂ arası {_about(lower_gap, gap_digits)}, Q₂ ile Q₃ arası {_about(upper_gap, gap_digits)} "
                "birimdir")
    return LabStep(
        number=8,
        title="Çeyrekler",
        note=NoteRef("4.9"),
        explanation=(
            "Çeyrekler özel yüzdeliklerdir: $Q_1 = P_{25}$, $Q_2 = P_{50}$ (medyan), $Q_3 = P_{75}$. "
            f"$n = {n}$ için {_location_text(ordered, 25, d)}. {_location_text(ordered, 75, d)}. $Q_2$ medyandır."
        ),
        operations=(
            Percentile(case.frame, x, 25, "Q1", "Birinci çeyrek Q₁", location="L25", decimals=digits),
            Percentile(case.frame, x, 50, "Q2", "İkinci çeyrek Q₂ (medyan)", location="L50", decimals=digits),
            Percentile(case.frame, x, 75, "Q3", "Üçüncü çeyrek Q₃", location="L75", decimals=digits),
            _spread_plot(case, case.frame, x, label, "Çeyrekler gözlemleri dört gruba ayırır",
                         (("Q1", "Q₁"), ("Q2", "Q₂"), ("Q3", "Q₃")), None, n, ctx["low_f"], ctx["high_f"]),
        ),
        checks=(
            _scalar("L25", "Konum L₂₅", _exact_digits(l25)),
            _scalar("Q1", "Birinci çeyrek Q₁", digits),
            _scalar("Q2", "İkinci çeyrek Q₂", digits),
            _scalar("L75", "Konum L₇₅", _exact_digits(l75)),
            _scalar("Q3", "Üçüncü çeyrek Q₃", digits),
        ),
        takeaway=(
            "Çeyrekler sayısal ekseni eşit uzunluklara değil, gözlemleri yaklaşık eşit sayıda dört gruba böler: "
            f"{gaps} (§4.9)."
        ),
    )


def _growth(case: Case) -> SeparateColumn | None:
    """Adım 9'un verisi: ayrı okunan yüzde değişim sütunu (alternatif örnekte satır içi veri)."""

    return (case.extra.get("separate") or {}).get(BUYUME)


def _chain(periods: int) -> str:
    """Faktörlerin çarpımı: g₁g₂, g₁g₂g₃ ya da g₁g₂⋯gₜ."""

    if periods <= 3:
        return " ".join(f"g_{index}" for index in range(1, periods + 1))
    return f"g_1 g_2 \\cdots g_{{{periods}}}"


def _step9(case: Case, ctx: dict) -> LabStep:
    title, note = "Geometrik ortalama ve bileşik büyüme", "4.10"
    growth = _growth(case)
    if growth is None:
        return _missing(9, title, note, "“Yüzde değişim (%)”, ör. yıllık büyüme ya da enflasyon")
    frame, column = growth.frame, growth.column
    rates = growth.values.to_numpy(dtype=float)
    if len(rates) < 2:
        return _blocked(9, title, note, "Geometrik ortalama için en az iki dönemin yüzde değişimi gerekir; seçilen "
                                        "sütunda yalnız bir dolu hücre var.")
    if np.any(rates <= -100):
        return _blocked(9, title, note, (
            "Yüzde değişimlerden biri −100 ya da daha küçük: büyüme faktörü 1 + r/100 pozitif olmalıdır. Sütunda "
            "yüzde değişimler (ör. 12 ya da −3,5) bulunmalı."
        ))
    d = data_decimals(pd.Series(rates))
    periods = len(rates)
    exact = _exact_data(rates, d)
    with localcontext(_EXACT):
        product = Decimal(1)
        for rate in exact:
            product *= 1 + rate / 100
        arithmetic = sum(exact, Decimal(0)) / periods
        final = 100 * product
    compound = 100 * (float(np.prod(1 + rates / 100)) ** (1 / periods) - 1)  # uygulamanın hesabıyla aynı sıra
    equal = len(set(exact)) == 1
    arithmetic_digits = _mean_digits(arithmetic, d)
    compound_digits = min(10, max(2, significant(compound, 3)))
    g_digits = compound_digits + 2
    final_digits = _mean_digits(final, 1)
    if equal:  # bütün oranlar eşitse bileşik büyüme tam bu orandır
        compound_text = _about(exact[0], compound_digits, "%")
        direction = "aritmetik ortalamaya eşittir"
    else:
        compound_text = f"yaklaşık %{kisa(compound, compound_digits)}"
        direction = "aritmetik ortalamadan küçüktür"
    listed = (f"Dönemlik yüzde değişimler {sayilar(['%' + ondalik(value, d) for value in exact])}; büyüme "
              "faktörleri " if periods <= 8 else f"{periods} dönemin yüzde değişimleri kullanılır; büyüme faktörleri ")
    lead = case.extra.get("growth_text") or (
        f"“{md(case.label(BUYUME))}” sütununun dolu hücreleri ({periods} dönem) dosyadaki sırayla okunur. ")
    chain = _chain(periods)
    return LabStep(
        number=9,
        title=title,
        note=NoteRef(note),
        explanation=(
            f"{lead}{listed}$g_t = 1 + r_t/100$. 100 birimlik bir başlangıç değeri {periods} dönem sonra "
            f"$100 \\times {chain}$ olur. Geometrik ortalama $G = ({chain})^{{1/{periods}}}$ ve ortalama bileşik "
            "büyüme oranı $(G - 1) \\times 100$'dür."
        ),
        operations=(
            *growth.load,
            Derive(frame, ctx["factor"], E.add(1, E.div(E.var(column), 100)), "Büyüme faktörü g = 1 + r/100"),
            Statistic(frame, column, "mean", "aritmetik_degisim", "Aritmetik ortalama (%)",
                      decimals=arithmetic_digits),
            Statistic(frame, ctx["factor"], "prod", "carpim", "Faktörlerin çarpımı", decimals=max(4, g_digits)),
            Statistic(frame, ctx["factor"], "count", "donem_sayisi", "Dönem sayısı", decimals=0),
            Scalar("son_deger", E.mul(100, E.ref("carpim")), "100 birimin son değeri", decimals=final_digits),
            Scalar("G", E.power(E.ref("carpim"), E.div(1, E.ref("donem_sayisi"))), "Geometrik ortalama G",
                   decimals=g_digits),
            Scalar("bilesik_buyume", E.mul(100, E.sub(E.ref("G"), 1)), "Ortalama bileşik büyüme",
                   decimals=compound_digits, percent=True),
        ),
        checks=(
            _scalar("aritmetik_degisim", "Yüzde değişimlerin aritmetik ortalaması", arithmetic_digits),
            _scalar("son_deger", "100 birimin dönem sonundaki değeri", final_digits),
            _scalar("G", "Geometrik ortalama G", g_digits),
            _scalar("bilesik_buyume", "Ortalama bileşik büyüme (%)", compound_digits),
        ),
        takeaway=(
            f"Yüzde değişimlerin aritmetik ortalaması {_about(arithmetic, arithmetic_digits, '%')}, ortalama bileşik "
            f"büyüme {compound_text}: bileşik büyüme {direction}. 100 birim {periods} dönem sonra "
            f"{_about(final, final_digits)} olur; ardışık büyüme oranları çarpımsal işler. Ortalama bileşik büyüme "
            "geometrik ortalamayla bulunur (§4.10)."
        ),
    )


def _step10(case: Case, ctx: dict) -> LabStep:
    x, n, d, label = ctx["x"], ctx["n"], ctx["d"], ctx["label"]
    narrow = ctx["narrow"]
    mean, median, digits = ctx["mean"], ctx["median"], ctx["mean_digits"]
    median_digits, narrow_median = ctx["median_digits"], ctx["narrow_median"]
    narrow_digits = _mean_digits(narrow_median, d)
    if median == mean:
        median_text = ("Bu veride medyan da ortalamaya eşit olduğu için iki setin medyanı da aynıdır "
                       f"({_about(median, median_digits)}).")
    else:
        median_text = (f"Medyan ise ortalamaya doğru yaklaşır: özgün veride {_about(median, median_digits)}, "
                       f"türetilen sette {_about(narrow_median, narrow_digits)}.")
    return LabStep(
        number=10,
        title="Aynı merkez, farklı dağılım",
        note=NoteRef("4.12"),
        explanation=(
            "Veriden ikinci bir set türetilir: her gözlem ortalamaya olan uzaklığının yarısına çekilir, "
            "$y_i = \\bar{x} + 0{,}5\\,(x_i - \\bar{x})$. İki setin ortalaması aynıdır "
            f"($\\bar{{x}} {kesin_esit(mean, digits)} {_math(mean, digits)}$); türetilen setin değerleri ortalama "
            f"çevresinde daha sık toplanır. {median_text}"
        ),
        operations=(
            Derive(case.frame, narrow,
                   E.add(E.ref("ortalama"), E.mul(float(NARROW), E.sub(E.var(x), E.ref("ortalama")))),
                   "Türetilen set: y = x̄ + 0,5 (x − x̄)"),
            Statistic(case.frame, narrow, "mean", "ortalama_dar", "Türetilen set: ortalama", decimals=digits),
            Statistic(case.frame, narrow, "median", "medyan_dar", "Türetilen set: medyan", decimals=narrow_digits),
            _spread_plot(case, case.frame, x, label, "Özgün veri", (("ortalama", "Ortalama"),), ctx["axis"], n,
                         ctx["low_f"], ctx["high_f"]),
            _spread_plot(case, case.frame, narrow, label, "Türetilen set: aynı ortalama, yarı yayılım",
                         (("ortalama_dar", "Ortalama"),), ctx["axis"], n, ctx["low_f"], ctx["high_f"]),
        ),
        checks=(
            _scalar("ortalama_dar", "Türetilen set: ortalama", digits),
            _scalar("medyan_dar", "Türetilen set: medyan", narrow_digits),
        ),
        takeaway=(
            "Tek bir konum ölçüsü dağılımın bütün özelliklerini göstermez. Bir sonraki konuda bu farkı değişkenlik ve "
            "yayılım ölçüleriyle sayısallaştıracağız (§4.12)."
        ),
    )


def build(case: Case) -> LabSpec:
    """Konu 4 uygulamasını verilen veriyle kurar; kontrollerin beklenen değerleri uygulamanın hesabıdır."""

    ctx = _context(case)
    steps = (_step1(case, ctx), _step2(case, ctx), _step3(case, ctx), _step4(case, ctx), _step5(case, ctx),
             _step6(case, ctx), _step7(case, ctx), _step8(case, ctx), _step9(case, ctx), _step10(case, ctx))
    labels = dict(case.labels)
    labels.setdefault(ctx["narrow"], f"{ctx['label']} (türetilen set)")
    labels.setdefault(ctx["factor"], "Büyüme faktörü")
    names = group_names(case)
    for key, text in (("n", "Gözlem sayısı nⱼ"), ("ortalama", "Ortalama x̄ⱼ"), ("agirlik", "Ağırlık wⱼ"),
                      ("katki", "Katkı wⱼ x̄ⱼ"), ("agirlik_yuzde", "Ağırlık (%)")):
        labels.setdefault(names[key], text)
    spec = LabSpec(
        topic_key="konu04",
        title=TITLE,
        note_section="4",
        steps=steps,
        labels=tuple(labels.items()),
        source=case.source,
    )
    return with_app_values(spec)


# --- Alternatif örnek ve kendi verin ---------------------------------------------------------

def alternative_case() -> Case:
    data = pd.DataFrame(list(ALT_ROWS), columns=["kira", "oda"])
    growth = InlineData("artislar", ("yil", "artis"), ALT_GROWTH,
                        "Kurgusal veri: mahallede ortalama kiranın yıllık artışı (%)")
    rates = pd.Series([value for _, value in ALT_GROWTH], name="artis", dtype=float)
    return Case(
        source="alternatif",
        load=(InlineData("kiralar", ("kira", "oda"), ALT_ROWS,
                         "Kurgusal veri: 15 dairenin aylık kirası (bin TL) ve oda sayısı"),),
        frame="kiralar",
        data=data,
        roles={SAYISAL: "kira", GRUP: "oda", BUYUME: "artis"},
        labels=ALT_LABELS,
        orders={"oda": ("1+1", "2+1", "3+1")},
        unit="daire",
        extra={
            "read_text": "Mahalledeki 15 kiralık dairenin aylık kirası (bin TL) ilan sırasıyla okunur.",
            "separate": {BUYUME: SeparateColumn((growth,), "artislar", "artis", rates)},
            "growth_text": "Mahallede ortalama kira son dört yılda her yıl arttı. ",
        },
    )


@cache
def alternative() -> LabSpec:
    return build(alternative_case())


def sample() -> pd.DataFrame:
    """Örnek dosya: alternatif örneğin verisi; yıllık artış sütunu dört değer içerir (diğer hücreler boş)."""

    growth = [value for _, value in ALT_GROWTH] + [None] * (len(ALT_ROWS) - len(ALT_GROWTH))
    return pd.DataFrame({
        ALT_LABELS["kira"]: [row[0] for row in ALT_ROWS],
        ALT_LABELS["oda"]: [row[1] for row in ALT_ROWS],
        ALT_LABELS["artis"]: growth,
    })


SPREAD = 1e-9
"""En küçük ile en büyük değerin farkı, değerlerin büyüklüğünün en az bu katı olmalı: daha dar bir yayılımı kayan
noktalı grafik eksenleri gösteremez (R'nin eksen hesabı göreli 10⁻¹⁰'un altında uyarı verir)."""


def validate(case: Case) -> None:
    """Konum ölçüleri için en az iki farklı değer gerekir (uç değer adımı en büyük değeri değiştirir); değerler
    büyüklüklerine göre birbirinden ayırt edilebilmeli."""

    values = case.data[case.roles[SAYISAL]].astype(float)
    if values.nunique() < 2:
        raise K.UploadError(f"“{case.label(SAYISAL)}” sütununda bütün değerler aynı; konum ölçüleri için en az iki "
                            "farklı değer gerekir.")
    low, high = float(values.min()), float(values.max())
    if high - low < SPREAD * max(abs(low), abs(high)):
        raise K.UploadError(f"“{case.label(SAYISAL)}” sütunundaki değerler büyüklüklerine göre birbirine çok yakın "
                            f"(en küçük {ondalik(kesin(low))}, en büyük {ondalik(kesin(high))}); grafikler bu farkı "
                            "gösteremez. Değerlerden ortak bir sayı çıkarın (ör. her değerden en küçük değeri) ya da "
                            "birimi değiştirin.")


ROLES = (
    Role(SAYISAL, "Sayısal değişken", "sayisal", True, (1, 2, 4, 5, 6, 7, 8, 10),
         "Ortalama, medyan, mod, yüzdelik ve çeyreklerin değişkeni (ör. kira, puan, süre)."),
    Role(GRUP, "Grup sütunu (kategorik)", "kategorik", False, (3,),
         "Ağırlıklı ortalama için gruplar (ör. bölüm, oda sayısı); ağırlık grubun gözlem payıdır.", levels=(2, 10),
         suggest=True),
    Role(BUYUME, "Yüzde değişim (%)", "sayisal", False, (9,),
         "Dönemlik yüzde değişimler (ör. yıllık büyüme ya da enflasyon, %); geometrik ortalama için. Sütunun yalnız "
         "dolu hücreleri, dosyadaki sırayla kullanılır; sütun diğerlerinden kısa olabilir.", separate=True),
)

CUSTOM = CustomLab(
    roles=ROLES,
    build=build,
    sample=sample,
    intro=(
        "Sayısal bir sütun içeren bir Excel (.xlsx) ya da CSV dosyası yükleyin. Sayısal değişken zorunludur; ağırlıklı "
        "ortalama (Adım 3) için kategorik bir grup sütunu, geometrik ortalama (Adım 9) için dönemlik yüzde değişim "
        "sütunu seçebilirsiniz. Sayısal değişkeni boş olan satırlar analizden çıkarılır; grup sütunundaki boş hücreler "
        "yalnız Adım 3'ü etkiler. Yüzde değişim sütunu ayrı okunur: yalnız dolu hücreleri, dosyadaki sırayla "
        "kullanılır."
    ),
    order_roles=(GRUP,),
    min_rows=5,
    validate=validate,
)

VARIANTS = TopicVariants(alternative=alternative, story=STORY, custom=CUSTOM)
