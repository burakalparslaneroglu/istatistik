"""Konu 3 uygulaması: nicel bir veri setini sınıflara ayırmak, grafiklerle göstermek ve raporlamak.

Ders notlarının çözümlü örnekleri: §3.1 (Tablo 3.1), §3.2 (yaklaşık sınıf genişliği), §3.3 (Tablo 3.2),
§3.4 (Tablo 3.3), §3.5 (orta noktalar), §3.6 (Şekil 3.5), §3.7 (Şekil 3.6), §3.8 (Şekil 3.8), §3.10
(Tablo 3.4, Şekil 3.10), §3.11 (gövde–yaprak) ve §3.12 (Şekil 3.12). Buradaki her ``Check`` notlarda
basılı bir sayıdır; değer notlardan kopyalanmıştır, hesaplanmamıştır.
"""

from __future__ import annotations

from core.labs import expr as E
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

FRAME = "ulasim"
VARIABLE = "sure"

TRAVEL_TIMES = (
    12, 13, 15, 17, 18, 18, 20, 22,
    23, 24, 25, 25, 26, 27, 28, 29,
    30, 31, 32, 33, 34, 35, 35, 36,
    37, 38, 39, 40, 42, 44, 46, 48,
    50, 52, 55, 58, 62, 66, 70, 76,
)
"""Tablo 3.1: 40 öğrencinin kampüse tek yönlü ulaşım süresi (dakika), notlardaki satır düzeniyle."""

CLASSES = ("10 ≤ x < 20", "20 ≤ x < 30", "30 ≤ x < 40", "40 ≤ x < 50", "50 ≤ x < 60", "60 ≤ x < 70",
           "70 ≤ x < 80")
FREQUENCIES = (6, 10, 11, 5, 4, 2, 2)
"""Tablo 3.2."""
RELATIVE = (0.150, 0.250, 0.275, 0.125, 0.100, 0.050, 0.050)
PERCENT = (15.0, 25.0, 27.5, 12.5, 10.0, 5.0, 5.0)
"""Tablo 3.3."""
MIDPOINTS = (15, 25, 35, 45, 55, 65, 75)
"""§3.5."""
WIDTH_5 = (2, 4, 4, 6, 5, 6, 3, 2, 2, 2, 1, 1, 1, 1)
WIDTH_20 = (16, 16, 6, 2)
"""Şekil 3.8: 5 ve 20 dakikalık sınıflarla histogram yükseklikleri."""
CUMULATIVE = (6, 16, 27, 32, 36, 38, 40)
CUMULATIVE_RELATIVE = (0.150, 0.400, 0.675, 0.800, 0.900, 0.950, 1.000)
CUMULATIVE_PERCENT = (15.0, 40.0, 67.5, 80.0, 90.0, 95.0, 100.0)
"""Tablo 3.4."""
STEM_LEAVES = (
    ("1", "2 3 5 7 8 8"), ("2", "0 2 3 4 5 5 6 7 8 9"), ("3", "0 1 2 3 4 5 5 6 7 8 9"), ("4", "0 2 4 6 8"),
    ("5", "0 2 5 8"), ("6", "2 6"), ("7", "0 6"),
)
"""§3.11: gövde (onlar basamağı) ve yapraklar."""

AXIS = "Ulaşım süresi (dakika)"


def _labels(lower: int, width: int, count: int) -> tuple[str, ...]:
    return tuple(f"{lower + width * i} ≤ x < {lower + width * (i + 1)}" for i in range(count))


def _cells(table: str, rows, column: str, values, decimals: int, name: str) -> tuple[Check, ...]:
    return tuple(
        Check(f"{name}: {row}", TableTarget(table, row, column), value, decimals) for row, value in zip(rows, values)
    )


def _scalar(name: str, expected: float, label: str, decimals: int) -> Check:
    return Check(label, ScalarTarget(name), expected, decimals)


def _classes(result: str, columns: tuple[str, ...], *, width: int = 10, classes: int = 7,
             totals: bool = False, row_labels: str = "sinif") -> ClassTable:
    return ClassTable(FRAME, VARIABLE, result, width, columns, lower=10, classes=classes, totals=totals,
                      row_labels=row_labels)


STEPS = (
    LabStep(
        number=1,
        title="Ham nicel veri",
        note=NoteRef("3.1", objects=("Tablo 3.1",)),
        explanation=(
            "Tablo 3.1'deki 40 ulaşım süresi notlardaki gibi satır başına sekiz değer olarak yazılır. Her değer "
            "bir öğrencinin kampüse tek yönlü ulaşım süresidir (dakika). Ham tablo bütün değerleri korur; fakat "
            "40 sayıya tek tek bakarak dağılımın nerede yoğunlaştığını görmek kolay değildir."
        ),
        operations=(
            InlineData(FRAME, (VARIABLE,), tuple((value,) for value in TRAVEL_TIMES),
                       "Tablo 3.1: 40 öğrencinin kampüse ulaşım süresi (dakika)", layout=8),
            Statistic(FRAME, VARIABLE, "count", "n", "Gözlem sayısı n", decimals=0),
            Statistic(FRAME, VARIABLE, "min", "en_kucuk", "En küçük değer (dakika)", decimals=0),
            Statistic(FRAME, VARIABLE, "max", "en_buyuk", "En büyük değer (dakika)", decimals=0),
        ),
        checks=(
            _scalar("n", 40, "Gözlem sayısı", 0),
            _scalar("en_kucuk", 12, "En küçük değer", 0),
            _scalar("en_buyuk", 76, "En büyük değer", 0),
        ),
        takeaway=(
            "Nicel veride sınıflar veriyle birlikte hazır gelmez: sayısal ekseni hangi aralıklara böleceğimize "
            "biz karar veririz (§3.1)."
        ),
    ),
    LabStep(
        number=2,
        title="Yaklaşık sınıf genişliği",
        note=NoteRef("3.2"),
        explanation=(
            "Yaklaşık sınıf genişliği, en büyük ve en küçük değer arasındaki farkın sınıf sayısına "
            "bölünmesidir: $(76 - 12)/7 = 64/7$. Sonuç uygulamada kolay yorumlanan bir değere yuvarlanır; "
            "notlarda 10 dakika seçilir ve sınıflar 10'dan başlar."
        ),
        operations=(
            Scalar("aralik", E.sub(E.ref("en_buyuk"), E.ref("en_kucuk")), "En büyük − en küçük değer", decimals=0),
            Scalar("yaklasik_genislik", E.div(E.ref("aralik"), 7), "Yaklaşık sınıf genişliği (7 sınıf)",
                   decimals=2),
        ),
        checks=(
            _scalar("aralik", 64, "En büyük − en küçük değer", 0),
            _scalar("yaklasik_genislik", 9.14, "Yaklaşık sınıf genişliği 64/7", 2),
        ),
        takeaway=(
            "9,14 dakikalık sınıflar da kullanılabilir; 10 dakika hem veriyi kapsar hem de 10–20, 20–30 gibi "
            "okunması kolay sınırlar verir. Tek bir doğru sınıf sayısı yoktur (§3.2)."
        ),
    ),
    LabStep(
        number=3,
        title="Sınıf sınırları ve frekans dağılımı",
        note=NoteRef("3.3", objects=("Tablo 3.2",)),
        explanation=(
            "Sınıflar $10 \\leq x < 20$, $20 \\leq x < 30$, …, $70 \\leq x < 80$ biçimindedir: alt sınır dahil, "
            "üst sınır hariç. Böylece 20 dakikalık bir gözlem yalnız ikinci sınıfa girer. Her sınıfa düşen "
            "gözlemler sayılır; frekansların toplamı $\\sum f_j = n$ olmalıdır."
        ),
        operations=(_classes("frekans_dagilimi", ("frekans",), totals=True),),
        checks=(
            *_cells("frekans_dagilimi", CLASSES, "frekans", FREQUENCIES, 0, "Frekans"),
            Check("Frekansların toplamı", TableTarget("frekans_dagilimi", TOTAL, "frekans"), 40, 0),
        ),
        takeaway=(
            "Ham veride hemen görülmeyen bilgi açığa çıkar: en yoğun sınıf 30–40 dakikadan az aralığıdır (11 "
            "gözlem); 60 dakika ve üzeri seyrektir (§3.3)."
        ),
    ),
    LabStep(
        number=4,
        title="Göreli frekans ve yüzde frekans",
        note=NoteRef("3.4", objects=("Tablo 3.3",)),
        explanation=(
            "Kategorik veride kullandığımız dönüşümler nicel sınıflarda da aynıdır: göreli frekans "
            "$r_j = f_j/n$, yüzde frekans $p_j = 100\\,r_j$. Örneğin 30–40 dakikadan az sınıfında "
            "$r = 11/40 = 0{,}275$ ve $p = \\%27{,}5$'tir."
        ),
        operations=(_classes("tam_tablo", ("frekans", "goreli", "yuzde"), totals=True),),
        checks=(
            *_cells("tam_tablo", CLASSES, "goreli", RELATIVE, 3, "Göreli frekans"),
            *_cells("tam_tablo", CLASSES, "yuzde", PERCENT, 1, "Yüzde frekans"),
            Check("Göreli frekansların toplamı", TableTarget("tam_tablo", TOTAL, "goreli"), 1.000, 3),
            Check("Yüzde frekansların toplamı", TableTarget("tam_tablo", TOTAL, "yuzde"), 100.0, 1),
        ),
        takeaway=(
            "Aynı örneklem içinde frekans yeterlidir; büyüklükleri farklı iki örneklemi karşılaştırırken göreli "
            "veya yüzde frekans kullanılır: 40 kişilik örneklemde 20 kişi %50, 200 kişilik örneklemde %10'dur "
            "(§3.4)."
        ),
    ),
    LabStep(
        number=5,
        title="Sınıf orta noktası",
        note=NoteRef("3.5"),
        explanation=(
            "Sınıf orta noktası, alt ve üst sınırın tam ortasıdır: $m_j = (L_j + U_j)/2$. Örneğin "
            "$20 \\leq x < 30$ sınıfı için $m = (20 + 30)/2 = 25$ dakika."
        ),
        operations=(_classes("orta_noktalar", ("orta_nokta", "frekans")),),
        checks=_cells("orta_noktalar", CLASSES, "orta_nokta", MIDPOINTS, 0, "Orta nokta"),
        takeaway=(
            "Orta nokta sınıfı temsil eden bir özet değerdir; sınıftaki gözlemlerin bu değere eşit olduğu "
            "anlamına gelmez. 20–30 sınıfında 20, 22 ve 29 gibi farklı değerler vardır (§3.5)."
        ),
    ),
    LabStep(
        number=6,
        title="Nokta grafiği",
        note=NoteRef("3.6", objects=("Şekil 3.5",)),
        explanation=(
            "Nokta grafiğinde her gözlem kendi değerinin üzerinde bir noktadır; aynı değer birden fazla kez "
            "gözlenmişse noktalar üst üste dizilir. 18, 25 ve 35 dakikada ikişer gözlem vardır."
        ),
        operations=(
            DotPlot(FRAME, VARIABLE, AXIS, "Nokta grafiği: 40 ulaşım süresi"),
            Count(FRAME, "tekrar_18", VARIABLE, 18, "18 dakikadaki gözlem sayısı"),
            Count(FRAME, "tekrar_25", VARIABLE, 25, "25 dakikadaki gözlem sayısı"),
            Count(FRAME, "tekrar_35", VARIABLE, 35, "35 dakikadaki gözlem sayısı"),
        ),
        checks=(
            _scalar("tekrar_18", 2, "18 dakikadaki gözlem sayısı", 0),
            _scalar("tekrar_25", 2, "25 dakikadaki gözlem sayısı", 0),
            _scalar("tekrar_35", 2, "35 dakikadaki gözlem sayısı", 0),
        ),
        takeaway=(
            "Nokta grafiği tek tek gözlem değerlerini büyük ölçüde görünür tutar; bu nedenle özellikle "
            "örneklem küçükken yararlıdır (§3.6)."
        ),
    ),
    LabStep(
        number=7,
        title="Histogram",
        note=NoteRef("3.7", objects=("Şekil 3.6",)),
        explanation=(
            "Histogram, Tablo 3.2'deki sınıfları sayısal eksende bitişik dikdörtgenlerle gösterir. Sınıflar eşit "
            "genişlikte olduğu için her dikdörtgenin yüksekliği sınıfın frekansıdır. Sütun grafiğinden farkı "
            "şudur: 20–30 aralığı 10–20 aralığının hemen devamıdır, dikdörtgenler arasında boşluk yoktur."
        ),
        operations=(
            ClassHistogram("frekans_dagilimi", "frekans", AXIS, "Frekans", "Histogram: 10 dakikalık sınıflar"),
        ),
        takeaway=(
            "En yüksek dikdörtgen 30 ≤ x < 40 sınıfındadır; 40 dakikadan sonra frekanslar genel olarak azalır. "
            "Histogram tek tek değerleri göstermez; dağılımın genel yoğunlaşmasını daha hızlı gösterir (§3.7)."
        ),
    ),
    LabStep(
        number=8,
        title="Histogramın sınıf genişliğine duyarlılığı",
        note=NoteRef("3.8", objects=("Şekil 3.8",)),
        explanation=(
            "Aynı veri 5, 10 ve 20 dakikalık sınıflarla özetlenir. Sınıflar yine 10'dan başlar; 20 dakikalık "
            "sınıflarda son sınıf $70 \\leq x < 90$ olur."
        ),
        operations=(
            _classes("genislik_5", ("frekans",), width=5, classes=14),
            _classes("genislik_20", ("frekans",), width=20, classes=4),
            ClassHistogram("genislik_5", "frekans", AXIS, "Frekans", "Sınıf genişliği 5 dakika"),
            ClassHistogram("frekans_dagilimi", "frekans", AXIS, "Frekans", "Sınıf genişliği 10 dakika"),
            ClassHistogram("genislik_20", "frekans", AXIS, "Frekans", "Sınıf genişliği 20 dakika"),
        ),
        checks=(
            *_cells("genislik_5", _labels(10, 5, 14), "frekans", WIDTH_5, 0, "5 dakikalık sınıf"),
            *_cells("genislik_20", _labels(10, 20, 4), "frekans", WIDTH_20, 0, "20 dakikalık sınıf"),
        ),
        takeaway=(
            "Dar sınıflar yerel küçük değişimleri öne çıkarır; geniş sınıflar dağılımı kaba özetler ve 30–40 "
            "aralığındaki tepeyi gizler. Sınıf genişliği yorumdan önce kontrol edilmesi gereken bir grafik "
            "tercihidir (§3.8)."
        ),
    ),
    LabStep(
        number=9,
        title="Kümülatif dağılımlar",
        note=NoteRef("3.10", objects=("Tablo 3.4", "Şekil 3.10")),
        explanation=(
            "Kümülatif frekans, bir sınıfın üst sınırına kadar olan bütün frekansların toplamıdır: "
            "$F_j = f_1 + f_2 + \\cdots + f_j$. Örneğin ulaşım süresi 40 dakikadan kısa olan öğrenci sayısı "
            "$F_3 = 6 + 10 + 11 = 27$'dir. "
            "Satır adındaki $x < 40$, \"40 dakikadan az\" demektir."
        ),
        operations=(
            _classes("kumulatif", ("kumulatif_frekans", "kumulatif_goreli", "kumulatif_yuzde"), row_labels="ust"),
            LineChart("kumulatif", "ust", "kumulatif_yuzde", "Üst sınır (dakika)", "Kümülatif yüzde",
                      "Kümülatif yüzde eğrisi"),
        ),
        checks=(
            *_cells("kumulatif", tuple(f"x < {u}" for u in range(20, 90, 10)), "kumulatif_frekans", CUMULATIVE, 0,
                    "Kümülatif frekans"),
            *_cells("kumulatif", tuple(f"x < {u}" for u in range(20, 90, 10)), "kumulatif_goreli",
                    CUMULATIVE_RELATIVE, 3, "Kümülatif göreli frekans"),
            *_cells("kumulatif", tuple(f"x < {u}" for u in range(20, 90, 10)), "kumulatif_yuzde",
                    CUMULATIVE_PERCENT, 1, "Kümülatif yüzde"),
        ),
        takeaway=(
            "Kümülatif değerler azalamaz ve son değer %100'dür. Tablo \"en fazla\", \"-den az\" gibi soruları "
            "doğrudan cevaplar: öğrencilerin %80'inin ulaşım süresi 50 dakikadan kısadır (§3.10)."
        ),
    ),
    LabStep(
        number=10,
        title="Gövde–yaprak gösterimi",
        note=NoteRef("3.11"),
        explanation=(
            "Onlar basamağı gövde, birler basamağı yapraktır; yapraklar her satırda küçükten büyüğe dizilir. "
            "Anahtar: $3 \\mid 5 = 35$ dakika. Bir gövdedeki yaprak sayısı, o onluktaki gözlem sayısıdır."
        ),
        operations=(StemLeaf(FRAME, VARIABLE, "govde_yaprak"),),
        checks=_cells("govde_yaprak", tuple(stem for stem, _ in STEM_LEAVES), "yaprak_sayisi",
                      tuple(len(leaves.split()) for _, leaves in STEM_LEAVES), 0, "Yaprak sayısı, gövde"),
        takeaway=(
            "Yaprak sayıları 10 dakikalık sınıfların frekanslarıyla aynıdır (6, 10, 11, 5, 4, 2, 2): gövde–yaprak "
            "gösterimi histogramın biçimini verirken ham değerleri de korur (§3.11)."
        ),
    ),
    LabStep(
        number=11,
        title="Bütünleştirici uygulama: dağılımı raporlamak",
        note=NoteRef("3.12", objects=("Şekil 3.12",)),
        explanation=(
            "Rapor sırası: değişken ve birim (tek yönlü ulaşım süresi, dakika); ham aralık (12–76 dakika); "
            "sınıflandırma (10 dakika genişliğinde yedi sınıf); temel yoğunlaşma (30 ≤ x < 40, 11 gözlem, "
            "%27,5); genel görünüm (40 dakikanın üzerinde frekanslar azalıyor); kümülatif bilgi (öğrencilerin "
            "%80'i 50 dakikadan kısa) ve sınır (sonuçlar yalnız gözlenen 40 öğrenciyi betimler). Yüzde "
            "histogramı frekans histogramıyla aynı biçimdedir; değişen yalnız dikey eksendir."
        ),
        operations=(
            ClassHistogram("tam_tablo", "yuzde", AXIS, "Öğrencilerin yüzdesi",
                           "Yüzde frekans histogramı", labels=True, percent=True, decimals=1),
        ),
        takeaway=(
            "Yüzde ekseni farklı büyüklükteki örneklemleri karşılaştırmayı kolaylaştırır. Daha geniş bir öğrenci "
            "kitlesine genelleme, örneklemin nasıl seçildiğine bağlıdır (§3.12)."
        ),
    ),
)

KONU03_LAB = LabSpec(
    topic_key="konu03",
    title="Nicel bir dağılımı sınıflamak, çizmek ve raporlamak",
    note_section="3",
    steps=STEPS,
    labels=((VARIABLE, AXIS),),
)
