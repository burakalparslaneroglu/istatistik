"""Konu 3 genel uygulaması: nicel bir dağılımı sınıflamak, çizmek ve raporlamak.

Ders notlarındaki adımlar (§3.1–§3.12) aynı numaralarla, verisi değiştirilebilir biçimde yazılır. Alternatif örnek
kurgusal bir kafe anketidir (50 müşterinin memnuniyet puanı); "kendi verini yükle" seçeneğinde aynı adımlar öğrencinin
dosyasıyla kurulur. Notlardaki uygulama (``core.labs.konu03``) değişmez.

Sınıflar notlardaki ve ASW'deki kuralla kurulur: yaklaşık genişlik (en büyük − en küçük)/k kolay bir değere (1; 2; 2,5
ya da 5 × 10^m) yukarı yuvarlanır ve verinin biriminden (ör. tam sayı veride 1) küçük olamaz; ilk sınıf en küçük değeri
içeren genişlik katından başlar ve sınıflar en büyük değeri kapsar. Bu sayılar ondalık aritmetikle hesaplanır; böylece
0,1 + 0,2 gibi kayan nokta hataları sınıf sınırına girmez.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from decimal import ROUND_FLOOR, Decimal
from functools import cache

import numpy as np
import pandas as pd

from core.labs import expr as E
from core.labs import kendi_veri as K
from core.labs import tables as T
from core.labs.ornek import (
    Case,
    CustomLab,
    Role,
    Setting,
    TopicVariants,
    esit,
    kesin,
    kesin_esit,
    kisa,
    liste,
    md,
    ondalik,
    ondalik_tex,
    sayilar,
    tex,
    with_app_values,
    yarim_basamak,
    yuzde,
)
from core.labs.spec import (
    TOTAL,
    Check,
    ClassHistogram,
    ClassTable,
    Count,
    DotPlot,
    InlineData,
    LabSpec,
    LabStep,
    LineChart,
    NoteRef,
    Scalar,
    ScalarTarget,
    Statistic,
    StemLeaf,
    TableTarget,
)

TITLE = "Nicel bir dağılımı sınıflamak, çizmek ve raporlamak"
SAYISAL = "sayisal"
SINIF = "k"
NICE = (Decimal(1), Decimal(2), Decimal("2.5"), Decimal(5))
"""Kolay okunan genişlikler: 1, 2, 2,5 ve 5'in 10'un kuvvetleriyle çarpımı (ör. 0,25; 10; 50)."""
MAX_DOTS = 300
"""Nokta grafiği ve gövde–yaprak gösterimi küçük ve orta büyüklükteki veri setleri içindir (notlar §3.6, §3.11)."""
MAX_STEMS = 20
"""Gövde–yaprak gösteriminde en çok gövde (satır) sayısı; yaprak birimi buna göre seçilir."""
MAX_DECIMALS = 30
"""Verinin ondalık basamağı için üst sınır; asıl sınır, en büyük değerin 15 anlamlı basamağıdır (``data_decimals``)."""

ALT_SCORES = (
    52, 79, 86, 84, 83, 87, 92, 95, 38, 75,
    61, 91, 82, 55, 82, 89, 73, 85, 94, 85,
    86, 88, 91, 69, 66, 84, 47, 96, 89, 90,
    44, 87, 99, 88, 58, 74, 89, 88, 85, 80,
    78, 68, 81, 64, 97, 93, 77, 71, 76, 79,
)
"""Kurgusal veri: bir kafede kısa bir ankete katılan 50 müşterinin 0–100 arası memnuniyet puanı (anket sırasıyla)."""
ALT_LABEL = "Memnuniyet puanı"
ALT_K = 7
STORY = (
    "Kurgusal veri: bir kafede kısa bir ankete katılan 50 müşterinin 0–100 arası memnuniyet puanı. Puanlar yüksek "
    "değerlerde toplanır, düşük puanlar seyrektir; notlardaki ulaşım süresinin tersine dağılım sola çarpıktır."
)


# --- Sınıflar ------------------------------------------------------------------------------

_decimal = kesin
"""Kayan noktalı sayının kısa ondalık yazımı (0.30000000000000004 değil, dosyadaki gibi 0.3)."""


def _places15(value: float) -> int:
    """Değeri 15 anlamlı basamakla tam gösteren ondalık basamak (0,1000001 → 7; 0,30000000000000004 → 1)."""

    value = float(value)
    if value == 0 or not math.isfinite(value):
        return 0
    return max(0, -Decimal(f"{value:.15g}").normalize().as_tuple().exponent)


def data_decimals(values: pd.Series) -> int:
    """Verideki ondalık basamak sayısı d: bütün değerleri tam gösteren en küçük d (her değerin 15 anlamlı basamaklı
    yazımından). Böylece 0,1000001 gibi değerler tam yazılır; kayan nokta gürültüsü (0,1 + 0,2 =
    0,30000000000000004) basamak saymaz. Değerler 10^d ile çarpılınca tam sayı olarak güvenle tutulabilmeli
    (10^15'in altında); gerekirse d küçültülür."""

    x = values.to_numpy(dtype=float)
    digits = min(MAX_DECIMALS, max((_places15(value) for value in x), default=0))
    top = float(np.abs(x).max()) if len(x) else 0.0
    while digits > 0 and top * 10.0 ** digits >= 1e15:
        digits -= 1
    return digits


def significant(value: float, count: int = 3) -> int:
    """``count`` anlamlı basamak için gereken ondalık basamak (0,0000262 → 7; 9,14 → 2)."""

    value = abs(float(value))
    if value == 0 or not math.isfinite(value):
        return 0
    return max(0, count - 1 - math.floor(math.log10(value)))


def suggested_classes(n: int) -> int:
    """Önerilen sınıf sayısı: ⌈1 + log₂ n⌉ (Sturges kuralı), 5–20 aralığında (ASW'nin 5–20 sınıf önerisi)."""

    return min(20, max(5, math.ceil(1 + math.log2(max(n, 1)))))


def nice_width(raw: Decimal, unit: Decimal) -> Decimal:
    """``raw`` değerinden küçük olmayan ilk kolay genişlik (1, 2, 2,5 ya da 5 × 10^m); verinin biriminden küçük
    olamaz (tam sayı veride en az 1)."""

    if raw <= 0:
        return unit
    exponent = raw.adjusted()
    for power in (exponent - 1, exponent, exponent + 1):
        for factor in NICE:
            candidate = factor.scaleb(power)
            if candidate >= raw:
                return max(candidate, unit)
    return max(Decimal(10).scaleb(exponent + 1), unit)


def class_count(low: Decimal, high: Decimal, lower: Decimal, width: Decimal) -> int:
    """``lower``'dan başlayan ``width`` genişliğindeki sınıfların en büyük değeri kapsayan en küçük sayısı."""

    return int(((high - lower) / width).to_integral_value(rounding=ROUND_FLOOR)) + 1


@dataclass(frozen=True)
class Classes:
    """Sınıflandırma: ``k`` yaklaşık genişliğin paydası, ``raw`` yaklaşık genişlik, ``width`` kolay değere yuvarlanmış
    genişlik h, ``lower`` ilk sınıfın alt sınırı a, ``count`` oluşan sınıf sayısı, ``unit`` verinin birimi 10^−d."""

    k: int
    raw: Decimal
    width: Decimal
    lower: Decimal
    count: int
    unit: Decimal
    decimals: int
    low: Decimal
    high: Decimal

    def edges(self, width: Decimal | None = None) -> np.ndarray:
        width = self.width if width is None else width
        return T.class_edges(None, float(width), float(self.lower), self.count_for(width))

    def count_for(self, width: Decimal) -> int:
        return class_count(self.low, self.high, self.lower, width)


def classes_for(values: pd.Series, k: int) -> Classes:
    """Notlardaki kural: h = (en büyük − en küçük)/k değerinin kolay bir değere yukarı yuvarlanması; a, en küçük değeri
    içeren h katı (⌊min/h⌋·h); sınıf sayısı en büyük değeri kapsayacak kadar."""

    decimals = data_decimals(values)
    unit = Decimal(1).scaleb(-decimals)
    low, high = _decimal(values.min()), _decimal(values.max())
    raw = (high - low) / k
    width = nice_width(raw, unit)
    lower = (low / width).to_integral_value(rounding=ROUND_FLOOR) * width
    return Classes(k, raw, width, lower, class_count(low, high, lower, width), unit, decimals, low, high)


# --- Yazım yardımcıları --------------------------------------------------------------------

def _dtext(value: Decimal | float) -> str:
    """Ondalık sayının Türkçe yazımı (2,5; 10; −0,25); gereksiz sıfır yok."""

    return ondalik(value if isinstance(value, Decimal) else _decimal(value))


def _dtex(value: Decimal | float) -> str:
    return _dtext(value).replace(",", "{,}")


def _term(value: Decimal | float) -> str:
    """İşlemin sağındaki sayı: negatifse parantez içinde (76 − (−3))."""

    return f"({_dtex(value)})" if value < 0 else _dtex(value)


def _labels(edges: np.ndarray) -> list[str]:
    return [f"{T.boundary_label(a)} ≤ x < {T.boundary_label(b)}" for a, b in zip(edges[:-1], edges[1:])]


def _interval(a: float, b: float) -> str:
    """Matematik içinde bir sınıf: $10 \\leq x < 20$."""

    return f"{_dtex(a)} \\leq x < {_dtex(b)}"


def _scalar(name: str, label: str, decimals: int = 0) -> Check:
    return Check(label, ScalarTarget(name), 0.0, decimals)


def _cells(table: str, rows: list[str], column: str, decimals: int, name: str) -> tuple[Check, ...]:
    return tuple(Check(f"{name}: {row}", TableTarget(table, row, column), 0.0, decimals) for row in rows)


def _frequencies(values: pd.Series, edges: np.ndarray) -> np.ndarray:
    return pd.cut(values, bins=edges, right=False).value_counts(sort=False).to_numpy()


def _modal(labels: list[str], counts: np.ndarray) -> tuple[list[str], int]:
    top = int(counts.max())
    return [label for label, count in zip(labels, counts) if count == top], top


def _places(value: Decimal) -> int:
    """Ondalık sayının basamak sayısı (1,25 → 2; 10 → 0)."""

    return max(0, -int(value.normalize().as_tuple().exponent))


def _about_percent(value: float, decimals: int = 1) -> str:
    """Düzyazıdaki yüzde: yuvarlanmışsa başında "yaklaşık" (11/12 → yaklaşık %91,7; 20/50 → %40)."""

    text = yuzde(value, decimals)
    return text if esit(value, decimals) == "=" else f"yaklaşık {text}"


def _class_text(labels: list[str]) -> str:
    """Sınıf adları metinde (tablodaki ad "-2 ≤ x < 0"; metinde tipografik eksiyle)."""

    return liste([md(label.replace("-", "−")) for label in labels])


# --- Adımlar -------------------------------------------------------------------------------

def _context(case: Case) -> dict:
    """Adımların ortak hesapları: değişken, sınıflar, sınıf frekansları."""

    x = case.roles[SAYISAL]
    values = case.data[x].astype(float)
    settings = case.extra.get("settings") or {}
    k = int(settings.get(SINIF) or case.extra.get("k") or suggested_classes(len(values)))
    classes = classes_for(values, k)
    edges = classes.edges()
    labels = _labels(edges)
    counts = _frequencies(values, edges)
    return {"x": x, "values": values, "classes": classes, "edges": edges, "labels": labels, "counts": counts,
            "n": len(values), "label": case.label(SAYISAL), "d": classes.decimals}


def _table(case: Case, ctx: dict, result: str, columns: tuple[str, ...], *, width: Decimal | None = None,
           totals: bool = False, row_labels: str = "sinif") -> ClassTable:
    classes = ctx["classes"]
    width = classes.width if width is None else width
    return ClassTable(case.frame, ctx["x"], result, float(width), columns, lower=float(classes.lower),
                      classes=classes.count_for(width), totals=totals, row_labels=row_labels)


def _step1(case: Case, ctx: dict) -> LabStep:
    n, d, label = ctx["n"], ctx["d"], ctx["label"]
    intro = case.extra.get("read_text") or f"“{md(label)}” sütunundaki {n} değer okunur; her değer bir gözlemdir."
    return LabStep(
        number=1,
        title="Ham nicel veri",
        note=NoteRef("3.1"),
        explanation=(
            f"{intro} Ham tablo bütün değerleri korur; fakat {n} sayıya tek tek bakarak dağılımın nerede "
            "yoğunlaştığını görmek kolay değildir."
        ),
        operations=(
            *case.load,
            Statistic(case.frame, ctx["x"], "count", "n", "Gözlem sayısı n", decimals=0),
            Statistic(case.frame, ctx["x"], "min", "en_kucuk", "En küçük değer", decimals=d),
            Statistic(case.frame, ctx["x"], "max", "en_buyuk", "En büyük değer", decimals=d),
        ),
        checks=(_scalar("n", "Gözlem sayısı"), _scalar("en_kucuk", "En küçük değer", d),
                _scalar("en_buyuk", "En büyük değer", d)),
        takeaway=(
            "Nicel veride sınıflar veriyle birlikte hazır gelmez: sayısal ekseni hangi aralıklara böleceğimize "
            "biz karar veririz (§3.1)."
        ),
    )


def _step2(case: Case, ctx: dict) -> LabStep:
    classes, d = ctx["classes"], ctx["d"]
    k, raw, width, lower = classes.k, classes.raw, classes.width, classes.lower
    digits = yarim_basamak(raw, min(10, max(2, d + 1, significant(float(raw)))))
    shown = ondalik(raw, digits)
    about = shown if kesin_esit(raw, digits) == "=" else f"yaklaşık {shown}"
    forced = raw < classes.unit  # yaklaşık genişlik verinin biriminden dar: bu genişlik kullanılamaz (bkz. Adım 8)
    rounding = (
        f"Yaklaşık genişlik zaten kolay bir değerdir: $h = {_dtex(width)}$."
        if width == raw else
        "Sonuç kolay yorumlanan bir değere (1; 2; 2,5 ya da 5'in 10'un bir kuvvetiyle çarpımı) yukarı yuvarlanır: "
        f"$h = {_dtex(width)}$."
    )
    if forced:
        rounding += f" Veriler {_dtext(classes.unit)} biriminde kaydedildiği için genişlik bu birimden küçük seçilmez."
    sample = f"${_interval(lower, lower + width)}$ ve ${_interval(lower + width, lower + 2 * width)}$"
    if forced:
        takeaway = (f"Veriler {_dtext(classes.unit)} biriminde olduğu için {about} genişliğindeki "
                    f"sınıfların bir kısmı boş kalabilirdi; {_dtext(width)} genişliği {sample} gibi sınıflar verir. "
                    "Tek bir doğru sınıf sayısı yoktur (§3.2).")
    elif width == raw:
        takeaway = (f"Yaklaşık genişlik {_dtext(width)} zaten kolay okunan bir değerdir; sınıflar {sample} "
                    "biçimindedir. Tek bir doğru sınıf sayısı yoktur (§3.2).")
    else:
        takeaway = (f"{about[0].upper() + about[1:]} genişliğindeki sınıflar da kullanılabilir; {_dtext(width)} "
                    f"hem veriyi kapsar hem de {sample} gibi okunması kolay sınırlar verir. Tek bir doğru sınıf sayısı "
                    "yoktur (§3.2).")
    count_text = (f"{classes.count} sınıf oluşur" if classes.count == k else
                  f"{classes.count} sınıf oluşur (yuvarlama ve alt sınırın h katı olması yüzünden sınıf sayısı "
                  "k'dan farklı olabilir)")
    chooser = (" Sınıf sayısını veri panelinden değiştirebilirsiniz." if case.source == "kendi" else "")
    return LabStep(
        number=2,
        title="Yaklaşık sınıf genişliği",
        note=NoteRef("3.2"),
        explanation=(
            f"Yaklaşık sınıf genişliği, en büyük ve en küçük değer arasındaki farkın sınıf sayısına bölünmesidir: "
            f"$({_dtex(classes.high)} - {_term(classes.low)})/{k} = {_dtex(classes.high - classes.low)}/{k} "
            f"{kesin_esit(raw, digits)} {ondalik_tex(raw, digits)}$. {rounding} İlk sınıfın alt sınırı "
            f"$a = {_dtex(lower)}$: en küçük değeri içeren $h$ katı. En büyük değeri kapsamak için {count_text}."
            f"{chooser}"
        ),
        operations=(
            Scalar("aralik", E.sub(E.ref("en_buyuk"), E.ref("en_kucuk")), "En büyük − en küçük değer", decimals=d),
            Scalar("yaklasik_genislik", E.div(E.ref("aralik"), k), f"Yaklaşık sınıf genişliği ({k} sınıf)",
                   decimals=digits),
        ),
        checks=(_scalar("aralik", "En büyük − en küçük değer", d),
                _scalar("yaklasik_genislik", "Yaklaşık sınıf genişliği", digits)),
        takeaway=takeaway,
    )


def _step3(case: Case, ctx: dict) -> LabStep:
    edges, labels, counts, n = ctx["edges"], ctx["labels"], ctx["counts"], ctx["n"]
    modal, top = _modal(labels, counts)
    shown = [_interval(a, b) for a, b in zip(edges[:-1], edges[1:])]
    middle = "$, $".join(shown) if len(shown) <= 3 else f"{shown[0]}$, ${shown[1]}$, …, ${shown[-1]}"
    boundary = (f" Böylece {_dtext(edges[1])} değerindeki bir gözlem yalnız ikinci sınıfa girer." if len(labels) > 1
                else "")
    empty = int((counts == 0).sum())
    lead = (f"en yoğun sınıf {_class_text(modal)} ve bu sınıfta {top} gözlem var" if len(modal) == 1 else
            f"en yoğun sınıflar {_class_text(modal)}; her birinde {top} gözlem var")
    empty_text = f"; {empty} sınıfta hiç gözlem yok" if empty else ""
    return LabStep(
        number=3,
        title="Sınıf sınırları ve frekans dağılımı",
        note=NoteRef("3.3"),
        explanation=(
            f"Sınıflar ${middle}$ biçimindedir: alt sınır dahil, üst sınır hariç.{boundary} Her sınıfa düşen "
            f"gözlemler sayılır; frekansların toplamı $\\sum f_j = n = {n}$ olmalıdır."
        ),
        operations=(_table(case, ctx, "frekans_dagilimi", ("frekans",), totals=True),),
        checks=(
            *_cells("frekans_dagilimi", labels, "frekans", 0, "Frekans"),
            Check("Frekansların toplamı", TableTarget("frekans_dagilimi", TOTAL, "frekans"), 0.0, 0),
        ),
        takeaway=f"Ham veride hemen görülmeyen bilgi açığa çıkar: {lead}{empty_text} (§3.3).",
    )


def _step4(case: Case, ctx: dict) -> LabStep:
    labels, counts, n = ctx["labels"], ctx["counts"], ctx["n"]
    modal, top = _modal(labels, counts)
    share = top / n
    return LabStep(
        number=4,
        title="Göreli frekans ve yüzde frekans",
        note=NoteRef("3.4"),
        explanation=(
            "Kategorik veride kullandığımız dönüşümler nicel sınıflarda da aynıdır: göreli frekans $r_j = f_j/n$, "
            f"yüzde frekans $p_j = 100\\,r_j$. Örneğin {_class_text([modal[0]])} sınıfında "
            f"$r = {top}/{n} {esit(share, 3)} {tex(share, 3)}$ ve $p {esit(100 * share, 1)} \\%{tex(100 * share, 1)}$."
        ),
        operations=(_table(case, ctx, "tam_tablo", ("frekans", "goreli", "yuzde"), totals=True),),
        checks=(
            *_cells("tam_tablo", labels, "goreli", 3, "Göreli frekans"),
            *_cells("tam_tablo", labels, "yuzde", 1, "Yüzde frekans"),
            Check("Göreli frekansların toplamı", TableTarget("tam_tablo", TOTAL, "goreli"), 0.0, 3),
            Check("Yüzde frekansların toplamı", TableTarget("tam_tablo", TOTAL, "yuzde"), 0.0, 1),
        ),
        takeaway=(
            "Aynı örneklem içinde frekans yeterlidir; büyüklükleri farklı iki örneklemi karşılaştırırken göreli "
            "veya yüzde frekans kullanılır: 40 kişilik örneklemde 20 kişi %50, 200 kişilik örneklemde %10'dur (§3.4)."
        ),
    )


def _spread_values(values: pd.Series, a: float, b: float) -> list[float]:
    """Bir sınıftaki farklı değerlerden en çok üçü: en küçük, ortadaki ve en büyük."""

    inside = np.unique(values[(values >= a) & (values < b)].to_numpy(dtype=float))
    if len(inside) <= 3:
        return list(inside)
    return [inside[0], inside[len(inside) // 2], inside[-1]]


def _step5(case: Case, ctx: dict) -> LabStep:
    edges, labels, d = ctx["edges"], ctx["labels"], ctx["d"]
    index = 1 if len(labels) > 1 else 0
    a, b = edges[index], edges[index + 1]
    middle = (_decimal(a) + _decimal(b)) / 2  # ondalık aritmetik: 0,07500000000000001 gibi gürültü yok
    digits = max(_places(ctx["classes"].width / 2), _places(ctx["classes"].lower))
    example = None
    for position in [index, *range(len(labels))]:
        spread = _spread_values(ctx["values"], edges[position], edges[position + 1])
        if len(spread) >= 2:
            example = (labels[position], spread)
            break
    takeaway = ("Orta nokta sınıfı temsil eden bir özet değerdir; sınıftaki gözlemlerin bu değere eşit olduğu anlamına "
                "gelmez")
    if example is not None:
        shown = sayilar([kisa(value, d) for value in example[1]])
        takeaway += f". {_class_text([example[0]])} sınıfında {shown} gibi farklı değerler vardır"
    return LabStep(
        number=5,
        title="Sınıf orta noktası",
        note=NoteRef("3.5"),
        explanation=(
            "Sınıf orta noktası, alt ve üst sınırın tam ortasıdır: $m_j = (L_j + U_j)/2$. Örneğin "
            f"${_interval(a, b)}$ sınıfı için $m = ({_dtex(a)} + {_term(b)})/2 = {_dtex(middle)}$."
        ),
        operations=(_table(case, ctx, "orta_noktalar", ("orta_nokta", "frekans")),),
        checks=_cells("orta_noktalar", labels, "orta_nokta", digits, "Orta nokta"),
        takeaway=takeaway + " (§3.5).",
    )


def _repeated(values: pd.Series, limit: int = 3) -> tuple[list[tuple[float, int]], int]:
    """En çok tekrar eden değerler (en az iki kez gözlenen; eşitlikte küçük değer önce) ve listenin dışında kalıp son
    listelenen değerle aynı sıklıkta gözlenen değerlerin sayısı."""

    counts = values.value_counts()
    counts = counts[counts >= 2]
    ranked = [(float(value), int(count)) for value, count in
              sorted(counts.items(), key=lambda pair: (-int(pair[1]), float(pair[0])))]
    listed = ranked[:limit]
    rest = sum(1 for _, count in ranked[limit:] if listed and count == listed[-1][1])
    return listed, rest


def _repeat_text(items: list[tuple[float, int]], d: int) -> str:
    groups: dict[int, list[str]] = {}
    for value, count in items:
        groups.setdefault(count, []).append(kisa(value, d))
    parts = []
    for count, shown in groups.items():
        if len(shown) == 1:
            parts.append(f"{shown[0]} ({count} gözlem)")
        else:
            parts.append(f"{sayilar(shown)} (her biri {count} gözlem)")
    return "; ".join(parts)


def _step6(case: Case, ctx: dict) -> LabStep:
    x, values, n, d, label = ctx["x"], ctx["values"], ctx["n"], ctx["d"], ctx["label"]
    items, rest = _repeated(values)
    operations = []
    if n <= MAX_DOTS:
        operations.append(DotPlot(case.frame, x, label, f"Nokta grafiği: {n} gözlem"))
        plot_text = ""
    else:
        plot_text = (f" Bu veride n = {n}: noktalar okunamayacak kadar üst üste biner. Nokta grafiği küçük ve orta "
                     f"büyüklükteki veri setleri içindir (burada en çok {MAX_DOTS} gözlem); aynı bilgi Adım 7'deki "
                     "histogramda özetlenir.")
    checks = []
    for index, (value, _) in enumerate(items, start=1):
        shown = kisa(value, d)
        operations.append(Count(case.frame, f"tekrar_{index}", x, value, f"{shown} değerindeki gözlem sayısı"))
        checks.append(_scalar(f"tekrar_{index}", f"{shown} değerindeki gözlem sayısı"))
    if items:
        head = "En çok tekrar eden değer" if len(items) == 1 and not rest else "En çok tekrar eden değerler"
        repeat = f" {head}: {_repeat_text(items, d)}"
        repeat += f"; aynı sıklıkta {rest} değer daha var." if rest else "."
    else:
        repeat = " Bu veride her değer bir kez gözlenmiş; noktalar üst üste dizilmez."
    return LabStep(
        number=6,
        title="Nokta grafiği",
        note=NoteRef("3.6"),
        explanation=(
            "Nokta grafiğinde her gözlem kendi değerinin üzerinde bir noktadır; aynı değer birden fazla kez "
            f"gözlenmişse noktalar üst üste dizilir.{repeat}{plot_text}"
        ),
        operations=tuple(operations),
        checks=tuple(checks),
        takeaway=(
            "Nokta grafiği tek tek gözlem değerlerini büyük ölçüde görünür tutar; bu nedenle özellikle örneklem "
            "küçükken yararlıdır (§3.6)."
        ),
    )


def _step7(case: Case, ctx: dict) -> LabStep:
    edges, labels, counts, label = ctx["edges"], ctx["labels"], ctx["counts"], ctx["label"]
    classes = ctx["classes"]
    modal, _ = _modal(labels, counts)
    joined = ""
    if len(labels) > 1:
        joined = (f" Sütun grafiğinden farkı şudur: ${_interval(edges[1], edges[2])}$ sınıfı "
                  f"${_interval(edges[0], edges[1])}$ sınıfının hemen devamıdır, dikdörtgenler arasında boşluk "
                  "yoktur.")
    where = (f"En yüksek dikdörtgen {_class_text(modal)} sınıfındadır." if len(modal) == 1 else
             f"En yüksek dikdörtgenler {_class_text(modal)} sınıflarındadır.")
    shape = case.extra.get("histogram_text", "")
    return LabStep(
        number=7,
        title="Histogram",
        note=NoteRef("3.7"),
        explanation=(
            "Histogram, Adım 3'teki sınıfları sayısal eksende bitişik dikdörtgenlerle gösterir. Sınıflar eşit "
            f"genişlikte olduğu için her dikdörtgenin yüksekliği sınıfın frekansıdır.{joined}"
        ),
        operations=(
            ClassHistogram("frekans_dagilimi", "frekans", label, "Frekans",
                           f"Histogram: sınıf genişliği {_dtext(classes.width)}"),
        ),
        takeaway=(
            f"{where}{(' ' + shape) if shape else ''} Histogram tek tek değerleri göstermez; dağılımın genel "
            "yoğunlaşmasını daha hızlı gösterir (§3.7)."
        ),
    )


def _widths(classes: Classes) -> tuple[Decimal, Decimal, Decimal, bool]:
    """Karşılaştırılan üç genişlik: h/2, h, 2h; h/2 verinin biriminden küçükse h, 2h, 4h."""

    half = classes.width / 2
    if half >= classes.unit:
        return half, classes.width, classes.width * 2, True
    return classes.width, classes.width * 2, classes.width * 4, False


def _step8(case: Case, ctx: dict) -> LabStep:
    classes, label = ctx["classes"], ctx["label"]
    narrow, middle, wide, halved = _widths(classes)
    lower = classes.lower
    tables = {narrow: "genislik_dar", middle: "frekans_dagilimi", wide: "genislik_genis"}
    if not halved:
        tables = {narrow: "frekans_dagilimi", middle: "genislik_orta", wide: "genislik_genis"}
    operations = []
    checks: list[Check] = []
    for width, table in tables.items():
        if table == "frekans_dagilimi":
            continue
        operations.append(_table(case, ctx, table, ("frekans",), width=width))
        rows = _labels(classes.edges(width))
        checks += _cells(table, rows, "frekans", 0, f"Genişlik {_dtext(width)}")
    for width, table in tables.items():
        operations.append(ClassHistogram(table, "frekans", label, "Frekans", f"Sınıf genişliği {_dtext(width)}"))
    wide_edges = classes.edges(wide)
    last = _interval(wide_edges[-2], wide_edges[-1])
    unit_text = ("" if halved else
                 f" Veriler {_dtext(classes.unit)} biriminde kaydedildiği için {_dtext(classes.width)} genişliğinden "
                 "dar sınıf kullanılmaz.")
    return LabStep(
        number=8,
        title="Histogramın sınıf genişliğine duyarlılığı",
        note=NoteRef("3.8"),
        explanation=(
            f"Aynı veri {sayilar([_dtext(narrow), _dtext(middle), _dtext(wide)])} genişliğindeki sınıflarla özetlenir."
            f"{unit_text} Sınıflar yine {_dtext(lower)} değerinden başlar; {_dtext(wide)} genişliğinde son sınıf "
            f"${last}$ olur."
        ),
        operations=tuple(operations),
        checks=tuple(checks),
        takeaway=(
            "Dar sınıflar yerel küçük değişimleri öne çıkarır; geniş sınıflar dağılımı kaba özetler ve bazı tepeleri "
            "gizleyebilir. Sınıf genişliği yorumdan önce kontrol edilmesi gereken bir grafik tercihidir (§3.8)."
        ),
    )


def _cumulative_target(counts: np.ndarray) -> int | None:
    """Okuma örneği için sınıf: kümülatif payı %80'e ilk ulaşan ama %100'ün altında kalan sınıf; böyle bir sınıf
    yoksa %100'ün altındaki son sınıf. Bütün gözlemler tek sınıftaysa ``None``."""

    shares = 100 * np.cumsum(counts) / counts.sum()
    below = [index for index, share in enumerate(shares) if share < 100 - 1e-9]
    if not below:
        return None
    return next((index for index in below if shares[index] >= 80 - 1e-9), below[-1])


def _cumulative_text(edges: np.ndarray, counts: np.ndarray) -> str:
    """“x < 50 olan gözlemlerin payı %80” biçiminde okuma örneği."""

    target = _cumulative_target(counts)
    if target is None:
        return "bütün gözlemler tek sınıfta"
    share = 100 * counts[:target + 1].sum() / counts.sum()
    return f"x < {_dtext(edges[target + 1])} olan gözlemlerin payı {_about_percent(share)}"


def _cumulative_example(counts: np.ndarray) -> int:
    """Örnek sınıf: kümülatif payın ilk kez %50'ye ulaştığı sınıf (en az ikinci sınıf, varsa)."""

    shares = np.cumsum(counts) / counts.sum()
    index = int(np.argmax(shares >= 0.5 - 1e-12))
    return max(index, 1) if len(counts) > 1 else 0


def _step9(case: Case, ctx: dict) -> LabStep:
    edges, counts = ctx["edges"], ctx["counts"]
    uppers = [f"x < {T.boundary_label(b)}" for b in edges[1:]]
    index = _cumulative_example(counts)
    terms = [str(int(value)) for value in counts[:index + 1]]
    total = int(counts[:index + 1].sum())
    if len(terms) <= 4:
        sum_text = " + ".join(terms)
    else:
        sum_text = f"{terms[0]} + {terms[1]} + \\cdots + {terms[-1]}"
    subscript = index + 1
    return LabStep(
        number=9,
        title="Kümülatif dağılımlar",
        note=NoteRef("3.10"),
        explanation=(
            "Kümülatif frekans, bir sınıfın üst sınırına kadar olan bütün frekansların toplamıdır: "
            "$F_j = f_1 + f_2 + \\cdots + f_j$. Örneğin "
            f"{_dtext(edges[index + 1])} değerinden küçük gözlemlerin sayısı "
            f"$F_{{{subscript}}} = {sum_text} = {total}$. "
            f"Satır adındaki $x < {_dtex(edges[index + 1])}$, “{_dtext(edges[index + 1])} değerinden küçük” demektir."
        ),
        operations=(
            _table(case, ctx, "kumulatif", ("kumulatif_frekans", "kumulatif_goreli", "kumulatif_yuzde"),
                   row_labels="ust"),
            LineChart("kumulatif", "ust", "kumulatif_yuzde", "Sınıfın üst sınırı", "Kümülatif yüzde",
                      "Kümülatif yüzde eğrisi"),
        ),
        checks=(
            *_cells("kumulatif", uppers, "kumulatif_frekans", 0, "Kümülatif frekans"),
            *_cells("kumulatif", uppers, "kumulatif_goreli", 3, "Kümülatif göreli frekans"),
            *_cells("kumulatif", uppers, "kumulatif_yuzde", 1, "Kümülatif yüzde"),
        ),
        takeaway=(
            "Kümülatif değerler azalamaz ve son değer %100'dür. Tablo “-den az” biçimindeki soruları doğrudan "
            f"cevaplar: {_cumulative_text(edges, counts)} (§3.10)."
        ),
    )


def stem_unit(values: pd.Series, decimals: int) -> int | None:
    """Yaprak birimi 10^e: en çok ``MAX_STEMS`` gövde veren en ince birim (verinin biriminden ince değil). Değerler
    tam sayılara güvenle çevrilemiyorsa ``None`` (adım açıklamayla atlanır). Yaprak birimi cinsinden değerler 2³¹'in
    altında kalmalı: üretilen Python kodundaki ``astype(int)`` Windows'ta numpy 1.x ile 32 bitliktir."""

    for unit in range(-decimals, 17):
        try:
            whole = T.stem_leaf_units(values, decimals, unit)
        except ValueError:
            return None
        stems = whole // 10
        if int(stems.max() - stems.min()) + 1 <= MAX_STEMS:
            return unit if int(whole.max()) < 2 ** 31 else None
    return None


def _step10(case: Case, ctx: dict) -> LabStep:
    title, note = "Gövde–yaprak gösterimi", NoteRef("3.11")
    values, n, d, label = ctx["values"], ctx["n"], ctx["d"], ctx["label"]
    if (values < 0).any():
        return LabStep(number=10, title=title, note=note, explanation=(
            f"Gövde–yaprak gösterimi bu derste negatif olmayan değerlerle kurulur; “{md(label)}” sütununda negatif "
            "değerler var. Dağılımın biçimi Adım 7'deki histogramda görülür."
        ))
    if n > MAX_DOTS:
        return LabStep(number=10, title=title, note=note, explanation=(
            f"Gövde–yaprak gösterimi küçük ve orta büyüklükteki veri setleri içindir; n = {n} gözlemde satırlar "
            f"yüzlerce yaprak içerir. Bu adım en çok {MAX_DOTS} gözlem için gösterilir; dağılımın biçimi Adım 7'deki "
            "histogramda görülür."
        ))
    unit = stem_unit(values, d)
    if unit is None:
        return LabStep(number=10, title=title, note=note, explanation=(
            f"“{md(label)}” sütunundaki değerler gövde–yaprak gösterimi için tam sayılara güvenle çevrilemiyor (çok "
            "büyük değerler ya da çok fazla ondalık basamak). Dağılımın biçimi Adım 7'deki histogramda görülür."
        ))
    whole = T.stem_leaf_units(values, d, unit)
    stems_all = whole // 10
    stems = [str(stem) for stem in range(int(stems_all.min()), int(stems_all.max()) + 1)]
    sample = float(np.sort(values.to_numpy(dtype=float))[n // 2])
    sample_whole = int(T.stem_leaf_units(pd.Series([sample]), d, unit)[0])
    stem, leaf = sample_whole // 10, sample_whole % 10
    shown = Decimal(sample_whole).scaleb(unit)
    place = T.stem_leaf_place(unit)
    if unit == 0 and d == 0:
        rule = "Yaprak birler basamağı, gövde ondan önceki basamaklardır"
    else:
        rule = (f"Yaprak birimi {T.stem_unit_text(unit)}: yaprak {place}, gövde ondan önceki basamaklardır; daha küçük "
                "basamaklar atılır (kesilir, yuvarlanmaz)")
    key = f"Anahtar: ${stem} \\mid {leaf} = {_dtex(shown)}$"
    if _decimal(sample) != shown:
        key += f" ({kisa(sample, d)} değeri böyle gösterilir)"
    classes = ctx["classes"]
    aligned = classes.width == Decimal(1).scaleb(unit + 1) and classes.count == len(stems)
    if aligned:
        counts = ", ".join(str(int(value)) for value in ctx["counts"])
        takeaway = (f"Yaprak sayıları Adım 3'teki sınıf frekanslarıyla aynıdır ({counts}): gövde–yaprak gösterimi "
                    "histogramın biçimini verirken ham değerleri de korur (§3.11).")
    else:
        takeaway = ("Gövde–yaprak gösterimi histogram gibi dağılımın biçimini verir; buna ek olarak ham değerleri "
                    "(yaprak birimine kadar) korur (§3.11).")
    return LabStep(
        number=10,
        title=title,
        note=note,
        explanation=(
            f"{rule}; yapraklar her satırda küçükten büyüğe dizilir. {key}. Bir gövdedeki yaprak sayısı, o gövdeye "
            "düşen gözlem sayısıdır."
        ),
        operations=(StemLeaf(case.frame, ctx["x"], "govde_yaprak", decimals=d, unit=unit),),
        checks=_cells("govde_yaprak", stems, "yaprak_sayisi", 0, "Yaprak sayısı, gövde"),
        takeaway=takeaway,
    )


def _step11(case: Case, ctx: dict) -> LabStep:
    classes, labels, counts, n, d, label = (ctx["classes"], ctx["labels"], ctx["counts"], ctx["n"], ctx["d"],
                                            ctx["label"])
    modal, top = _modal(labels, counts)
    share = _about_percent(100 * top / n)
    concentration = (f"{_class_text(modal)}, {top} gözlem, {share}" if len(modal) == 1 else
                     f"{_class_text(modal)}, her biri {top} gözlem, {share}")
    shape = case.extra.get("shape_text") or (
        "genel görünüm (histogramın simetrik mi, sağa mı, sola mı çarpık olduğunu §3.9'daki tanımlarla siz yorumlayın)"
    )
    return LabStep(
        number=11,
        title="Bütünleştirici uygulama: dağılımı raporlamak",
        note=NoteRef("3.12"),
        explanation=(
            f"Rapor sırası: {case.extra.get('variable_text') or f'değişken (“{md(label)}”)'}; ham aralık "
            f"({kisa(float(classes.low), d)} ile {kisa(float(classes.high), d)} arası); sınıflandırma "
            f"({_dtext(classes.width)} genişliğinde {classes.count} sınıf); temel yoğunlaşma ({concentration}); "
            f"{shape}; kümülatif bilgi ({_cumulative_text(ctx['edges'], counts)}) ve sınır (sonuçlar yalnız bu {n} "
            f"{case.unit} için geçerlidir). "
            "Yüzde histogramı frekans histogramıyla aynı biçimdedir; değişen yalnız dikey eksendir."
        ),
        operations=(
            ClassHistogram("tam_tablo", "yuzde", label, "Gözlemlerin yüzdesi", "Yüzde frekans histogramı",
                           labels=True, percent=True, decimals=1),
        ),
        takeaway=(
            "Yüzde ekseni farklı büyüklükteki örneklemleri karşılaştırmayı kolaylaştırır. Daha geniş bir topluluğa "
            "genelleme, örneklemin nasıl seçildiğine bağlıdır (§3.12)."
        ),
    )


def _labelable(edge: float) -> bool:
    """Sınıf sınırı iki dilde aynı metinle yazılabilir mi: 0 ya da [10⁻⁴, 10¹⁰) aralığında ve en çok 10 anlamlı
    basamak (Python ``.10g`` ile R ``formatC(format = "fg", digits = 10)`` yalnız bu durumda aynı metni verir)."""

    if edge == 0:
        return True
    low, high = LABEL_RANGE
    return low <= abs(edge) < high and float(T.boundary_label(edge).replace(",", ".")) == float(edge)


def _labels_ok(classes: Classes) -> bool:
    """Adım 3–8'deki bütün sınıf sınırları (h/2, h, 2h ya da h, 2h, 4h genişlikleriyle) iki dilde aynı yazılabilir."""

    return all(_labelable(edge) for width in _widths(classes)[:3] for edge in classes.edges(width))


def _working_counts(values: pd.Series) -> list[int]:
    """Sınırları yazılabilen sınıf sayıları (kaydırıcının aralığında)."""

    setting = SETTINGS[0]
    return [k for k in range(setting.minimum, setting.maximum + 1) if _labels_ok(classes_for(values, k))]


def check_labels(case: Case, classes: Classes) -> None:
    """Seçilen sınıf sayısıyla bütün sınıf sınırları okunur ve iki dilde aynı yazılabilmeli; yazılamıyorsa
    sınırları yazılabilen sınıf sayıları önerilir (hata kaydırıcının altında görünür). Hiçbir sınıf sayısının
    çalışmadığı veri ``validate`` içinde, kaydırıcıdan önce reddedilir."""

    if _labels_ok(classes):
        return
    working = _working_counts(case.data[case.roles[SAYISAL]].astype(float))
    advice = (f"Şu sınıf sayılarından birini seçin: {liste([str(k) for k in working])}." if working else
              "Verileri uygun bir birimle ölçekleyin.")
    raise K.UploadError(f"“{case.label(SAYISAL)}” sütunundaki değerlerle bu sınıf sayısında ({classes.k}) sınıf "
                        f"sınırları iki dilde aynı yazılamıyor (çok büyük, çok küçük ya da çok basamaklı). {advice}")


def build(case: Case) -> LabSpec:
    """Konu 3 uygulamasını verilen veriyle kurar; kontrollerin beklenen değerleri uygulamanın hesabıdır."""

    ctx = _context(case)
    check_labels(case, ctx["classes"])
    steps = (_step1(case, ctx), _step2(case, ctx), _step3(case, ctx), _step4(case, ctx), _step5(case, ctx),
             _step6(case, ctx), _step7(case, ctx), _step8(case, ctx), _step9(case, ctx), _step10(case, ctx),
             _step11(case, ctx))
    spec = LabSpec(
        topic_key="konu03",
        title=TITLE,
        note_section="3",
        steps=steps,
        labels=tuple(case.labels.items()),
        source=case.source,
    )
    return with_app_values(spec)


# --- Alternatif örnek ve kendi verin ---------------------------------------------------------

def alternative_case() -> Case:
    data = pd.DataFrame({"puan": ALT_SCORES})
    return Case(
        source="alternatif",
        load=(InlineData("anket", ("puan",), tuple((value,) for value in ALT_SCORES),
                         "Kurgusal veri: 50 müşterinin memnuniyet puanı (0–100)", layout=10),),
        frame="anket",
        data=data,
        roles={SAYISAL: "puan"},
        labels={"puan": ALT_LABEL},
        unit="müşteri",
        extra={
            "k": ALT_K,
            "read_text": ("Kafenin kısa anketine katılan 50 müşterinin memnuniyet puanı, anket sırasıyla satır başına "
                          "on değer olarak yazılır. Her değer bir müşterinin 0–100 arasında verdiği puandır."),
            "histogram_text": "Düşük puanlara doğru uzanan sol kuyruk seyrektir.",
            "variable_text": "değişken ve ölçek (memnuniyet puanı, 0–100)",
            "shape_text": ("genel görünüm (puanlar 70–100 aralığında yoğunlaşıyor; düşük puanlara doğru uzun ve seyrek "
                           "bir kuyruk var: dağılım sola çarpık)"),
        },
    )


@cache
def alternative() -> LabSpec:
    return build(alternative_case())


def sample() -> pd.DataFrame:
    """Örnek dosya: alternatif örneğin verisi, Türkçe sütun adıyla."""

    return pd.DataFrame({ALT_LABEL: ALT_SCORES})


LABEL_RANGE = (1e-4, 1e10)
"""Sınıf sınırları bu aralıkta (ya da 0) olmalı: daha büyük ya da küçük sınırları Python üstel yazar (2e+11), R yazmaz;
iki dilin tablo satır adları ayrılırdı. Böyle verilerde öğrenciden birim değiştirmesi istenir (ör. milyon TL)."""


def validate(case: Case) -> None:
    """Sınıf sayısından bağımsız denetimler: en az iki farklı değer ve 10¹⁰'un altında değerler (son sınıfın üst
    sınırı en büyük değerden büyüktür). Sınıf sayısına bağlı denetim ``build`` içindedir (``check_labels``)."""

    values = case.data[case.roles[SAYISAL]].astype(float)
    label = case.label(SAYISAL)
    if values.nunique() < 2:
        raise K.UploadError(f"“{label}” sütununda bütün değerler aynı; sınıflandırma için en az iki farklı değer "
                            "gerekir.")
    top = float(values.abs().max())
    if top >= LABEL_RANGE[1]:
        raise K.UploadError(f"“{label}” sütunundaki değerler sınıf sınırlarını okunur yazmak için çok büyük. "
                            "Verileri uygun bir birimle ölçekleyin (ör. bin TL ya da milyon TL).")
    if _working_counts(values):
        return
    classes = classes_for(values, suggested_classes(len(values)))
    if any(0 < abs(edge) < LABEL_RANGE[0] for edge in classes.edges()):
        factor = 10 ** max(1, math.ceil(-math.log10(top)))
        raise K.UploadError(f"“{label}” sütunundaki değerler sınıf sınırlarını yazmak için çok küçük: sınırlar "
                            "0,0001'in altına düşüyor ve iki dilde aynı yazılamıyor (sınıf sayısını değiştirmek "
                            f"yetmez). Değerleri {factor} ile çarpın, yani daha küçük bir birimle yazın (ör. milyon "
                            "TL yerine bin TL).")
    raise K.UploadError(f"“{label}” sütunundaki değerler sınıf sınırlarını yazmak için çok basamaklı: sınırlar 10'dan "
                        "fazla anlamlı basamak gerektiriyor ve iki dilde aynı yazılamıyor (sınıf sayısını değiştirmek "
                        "yetmez). Değerlerden ortak bir sayı çıkarın ya da değerleri daha az basamakla yuvarlayın.")


ROLES = (
    Role(SAYISAL, "Sayısal değişken", "sayisal", True, tuple(range(1, 12)),
         "Sınıflanacak nicel değişken (ör. süre, puan, gelir)."),
)

SETTINGS = (
    Setting(
        SINIF, "Sınıf sayısı k", 5, 20, lambda data, roles: suggested_classes(len(data)),
        "Adım 2'deki yaklaşık genişliğin paydası. Öneri ⌈1 + log₂ n⌉ (Sturges kuralı). Genişlik 1; 2; 2,5 ya da "
        "5 × 10ᵐ değerine yukarı yuvarlandığı için oluşan sınıf sayısı k'dan biraz farklı olabilir.",
        steps=(2, 3, 4, 5, 7, 8, 9, 11),
    ),
)

CUSTOM = CustomLab(
    roles=ROLES,
    build=build,
    sample=sample,
    intro=(
        "Sayısal bir sütun içeren bir Excel (.xlsx) ya da CSV dosyası yükleyin ve sınıflanacak değişkeni seçin. Değeri "
        "boş olan satırlar analizden çıkarılır. Sınıf sayısını kaydırıcıyla değiştirebilirsiniz; genişlik ve ilk "
        "sınıfın alt sınırı verinizden notlardaki kuralla kurulur."
    ),
    min_rows=10,
    validate=validate,
    settings=SETTINGS,
)

VARIANTS = TopicVariants(alternative=alternative, story=STORY, custom=CUSTOM)
