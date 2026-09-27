"""Konu 2 Sezgi deneyleri: veri üretim süreci bilinen kontrollü simülasyonlar.

Deney 1  Frekans mı, yüzde mi?                     (Notlar §2.3)
Deney 2  Satır yüzdesi mi, sütun yüzdesi mi?        (Notlar §2.8)
Deney 3  Simpson paradoksu: bileşim etkisi          (Notlar §2.11)
"""

from __future__ import annotations

from core.labs.runner import LabState
from core.labs.sezgi import Parameters, SimExperiment, SimMetric, SimParameter, number, percent, plain
from core.labs.spec import (
    CompareBarChart,
    CrossTab,
    DrawCategory,
    GroupedBarChart,
    Groups,
    NewSample,
    NoteRef,
)

SEED = 217
TOPIC = "konu02"


# --- Deney 1: frekans ve yüzde --------------------------------------------------------

MODES = ("Otobüs", "Raylı sistem", "Yürüme", "Özel araç", "Bisiklet")
P_CENTRAL = (0.40, 0.25, 0.15, 0.125, 0.075)
"""Merkez kampüs: notlardaki 40 öğrencinin yüzdeleri (Tablo 2.3)."""
P_NEW = (0.20, 0.10, 0.10, 0.45, 0.15)
"""Yeni kampüs: şehir dışında, toplu taşıma bağlantısı zayıf."""


def _build_campus(parameters: Parameters) -> tuple:
    central, new = int(parameters["n_merkez"]), int(parameters["n_yeni"])
    return (
        NewSample("ogrenci", central + new, SEED),
        Groups("ogrenci", "kampus", ("Merkez", "Yeni"), (central, new),
               "İlk öğrenciler Merkez, sonrakiler Yeni kampüste"),
        DrawCategory(
            "ogrenci", "arac", MODES, ((("Merkez",), P_CENTRAL), (("Yeni",), P_NEW)),
            "Kampüse göre ulaşım biçimi", by=("kampus",),
        ),
        CrossTab("ogrenci", "kampus", "arac", "frekanslar", ("Merkez", "Yeni"), MODES, margins=True),
        CrossTab("ogrenci", "kampus", "arac", "yuzdeler", ("Merkez", "Yeni"), MODES, percent="satir"),
        GroupedBarChart("frekanslar", "Ulaşım biçimi", "Öğrenci sayısı", "Frekanslar: kaç öğrenci?",
                        series="satir"),
        GroupedBarChart("yuzdeler", "Ulaşım biçimi", "Kampüs içindeki yüzde", "Yüzdeler: toplamın ne kadarı?",
                        series="satir", decimals=1),
    )


def _campus_dgp(parameters: Parameters) -> tuple[str, ...]:
    return (
        r"\text{Merkez: } P(\text{Otobüs},\ \text{Raylı sistem},\ \text{Yürüme},\ \text{Özel araç},\ \text{Bisiklet}) "
        r"= (0{,}40;\ 0{,}25;\ 0{,}15;\ 0{,}125;\ 0{,}075)",
        r"\text{Yeni: } P(\text{Otobüs},\ \text{Raylı sistem},\ \text{Yürüme},\ \text{Özel araç},\ \text{Bisiklet}) "
        r"= (0{,}20;\ 0{,}10;\ 0{,}10;\ 0{,}45;\ 0{,}15)",
        rf"n_{{\text{{Merkez}}}} = {int(parameters['n_merkez'])}, \qquad n_{{\text{{Yeni}}}} = "
        rf"{int(parameters['n_yeni'])}",
    )


def _campus_metrics(state: LabState, parameters: Parameters) -> tuple[SimMetric, ...]:
    counts, shares = state.tables["frekanslar"], state.tables["yuzdeler"]
    return (
        SimMetric("Özel araç, Merkez (frekans)", f"{counts.loc['Merkez', 'Özel araç']:.0f}",
                  "Merkez kampüste özel araçla gelen öğrenci sayısı."),
        SimMetric("Özel araç, Yeni (frekans)", f"{counts.loc['Yeni', 'Özel araç']:.0f}",
                  "Yeni kampüste özel araçla gelen öğrenci sayısı."),
        SimMetric("Özel araç, Merkez (%)", percent(shares.loc["Merkez", "Özel araç"]),
                  "Merkez kampüs öğrencileri içinde özel araç payı."),
        SimMetric("Özel araç, Yeni (%)", percent(shares.loc["Yeni", "Özel araç"]),
                  "Yeni kampüs öğrencileri içinde özel araç payı."),
    )


def _campus_takeaway(state: LabState, parameters: Parameters) -> str:
    counts, shares = state.tables["frekanslar"], state.tables["yuzdeler"]
    more_count = counts.loc["Merkez", "Özel araç"] > counts.loc["Yeni", "Özel araç"]
    more_share = shares.loc["Merkez", "Özel araç"] > shares.loc["Yeni", "Özel araç"]
    if more_count != more_share:
        text = (
            "Frekansa göre özel araç Merkez'de daha yaygın görünüyor; yüzdeye göre ise Yeni kampüste çok daha "
            "yaygın. İki ifade de doğrudur ama farklı soruları cevaplar: frekans \"kaç öğrenci?\", yüzde "
            "\"öğrencilerin ne kadarı?\"."
            if more_count else
            "Bu büyüklüklerde frekans ve yüzde farklı yönü gösteriyor: frekans kampüs büyüklüğünü, yüzde "
            "kampüs içindeki payı yansıtır."
        )
    else:
        text = (
            "Şu an frekans ve yüzde aynı yönü gösteriyor. Merkez kampüsü büyütüp Yeni kampüsü küçültün: "
            "yüzdeler yerinde kalırken frekanslar grup büyüklüğüyle değişir."
        )
    return text + " Büyüklükleri farklı grupları karşılaştırırken yüzde kullanılır (§2.3)."


FREQUENCY_OR_PERCENT = SimExperiment(
    topic_key=TOPIC,
    number=1,
    title="Frekans mı, yüzde mi?",
    question="Büyüklükleri farklı iki kampüsün ulaşım alışkanlıkları frekansla mı, yüzdeyle mi karşılaştırılmalı?",
    note=NoteRef("2.3", objects=("Tablo 2.3",)),
    parameters=(
        SimParameter("n_merkez", "Merkez kampüste öğrenci sayısı", 200, 3000, 2000, 100,
                     "Ankete yanıt veren Merkez kampüs öğrencileri.", integer=True, decimals=0),
        SimParameter("n_yeni", "Yeni kampüste öğrenci sayısı", 100, 3000, 300, 100,
                     "Ankete yanıt veren Yeni kampüs öğrencileri.", integer=True, decimals=0),
    ),
    dgp=_campus_dgp,
    dgp_note=(
        "Merkez kampüsün olasılıkları notlardaki 40 öğrencinin yüzdeleridir. Yeni kampüs şehir dışındadır; "
        "öğrencilerin çoğu özel araçla gelir."
    ),
    look_at=(
        "**Frekans grafiği** — her kampüste kaç öğrenci; büyük kampüs neredeyse her kategoride önde.",
        "**Yüzde grafiği** — her kampüsün kendi içindeki paylar; kampüs büyüklüğünden bağımsız.",
    ),
    build=_build_campus,
    metrics=_campus_metrics,
    takeaway=_campus_takeaway,
    tables=(("frekanslar", "Frekanslar"), ("yuzdeler", "Kampüs içindeki yüzdeler")),
    labels=(("kampus", "Kampüs"), ("arac", "Ulaşım biçimi")),
)


# --- Deney 2: satır ve sütun yüzdeleri ------------------------------------------------

DEPARTMENTS = ("İktisat", "İşletme")
MATERIALS = ("Basılı", "Dijital", "Her ikisi")
PREFERENCES = ((("İktisat",), (0.30, 0.45, 0.25)), (("İşletme",), (0.50, 0.40, 0.10)))
"""Tablo 2.5'in satır yüzdeleri."""


def _expected_column_share(share: float) -> float:
    """Dijital tercih edenler içinde İktisat payı (DGP'den): π·0,45 / (π·0,45 + (1 − π)·0,40)."""

    return 100 * share * 0.45 / (share * 0.45 + (1 - share) * 0.40)


def _build_denominator(parameters: Parameters) -> tuple:
    n, share = int(parameters["n"]), round(float(parameters["pi"]), 4)
    return (
        NewSample("ogrenci", n, SEED),
        DrawCategory("ogrenci", "bolum", DEPARTMENTS, (((), (share, round(1 - share, 4))),),
                     "Öğrencinin bölümü: İktisat olasılığı π"),
        DrawCategory("ogrenci", "materyal", MATERIALS, PREFERENCES, "Bölüme göre materyal tercihi", by=("bolum",)),
        CrossTab("ogrenci", "bolum", "materyal", "satir_yuzde", DEPARTMENTS, MATERIALS, percent="satir"),
        CrossTab("ogrenci", "bolum", "materyal", "sutun_yuzde", DEPARTMENTS, MATERIALS, percent="sutun"),
        GroupedBarChart("satir_yuzde", "Materyal tercihi", "Bölüm içindeki yüzde",
                        "Satır yüzdeleri: her bölüm kendi içinde", series="satir", decimals=1),
        GroupedBarChart("sutun_yuzde", "Materyal tercihi", "Tercih içindeki yüzde",
                        "Sütun yüzdeleri: her tercihin bölüm bileşimi", series="satir", stacked=True, decimals=1),
    )


def _denominator_dgp(parameters: Parameters) -> tuple[str, ...]:
    return (
        rf"P(\text{{İktisat}}) = \pi = {number(parameters['pi'], 2)}, \qquad n = {int(parameters['n'])}",
        r"\text{İktisat: } P(\text{Basılı},\ \text{Dijital},\ \text{Her ikisi}) = (0{,}30;\ 0{,}45;\ 0{,}25)",
        r"\text{İşletme: } P(\text{Basılı},\ \text{Dijital},\ \text{Her ikisi}) = (0{,}50;\ 0{,}40;\ 0{,}10)",
    )


def _denominator_metrics(state: LabState, parameters: Parameters) -> tuple[SimMetric, ...]:
    rows, columns = state.tables["satir_yuzde"], state.tables["sutun_yuzde"]
    return (
        SimMetric("İktisat içinde Dijital (satır %)", percent(rows.loc["İktisat", "Dijital"]),
                  "Payda: İktisat öğrencilerinin sayısı. DGP'de %45."),
        SimMetric("İşletme içinde Dijital (satır %)", percent(rows.loc["İşletme", "Dijital"]),
                  "Payda: İşletme öğrencilerinin sayısı. DGP'de %40."),
        SimMetric("Dijital içinde İktisat (sütun %)", percent(columns.loc["İktisat", "Dijital"]),
                  "Payda: dijital tercih eden öğrencilerin sayısı."),
        SimMetric("DGP'den beklenen sütun %", percent(_expected_column_share(parameters["pi"])),
                  "π·0,45 / (π·0,45 + (1 − π)·0,40): bölüm büyüklüğüne bağlıdır."),
    )


def _denominator_takeaway(state: LabState, parameters: Parameters) -> str:
    return (
        "π'yi değiştirin: satır yüzdeleri yerinde kalır, çünkü her bölümün kendi içindeki tercihi değişmiyor. "
        "Sütun yüzdeleri ise bölümlerin büyüklüğüyle birlikte değişir: dijital tercih edenlerin çoğunun "
        "İktisat öğrencisi olması, İktisat'ın kalabalık olmasından da kaynaklanır. \"İktisat öğrencilerinin "
        "yüzde kaçı dijital tercih ediyor?\" ile \"Dijital tercih edenlerin yüzde kaçı İktisat öğrencisi?\" "
        "farklı sorulardır; payda soruyu belirler (§2.8)."
    )


ROW_OR_COLUMN = SimExperiment(
    topic_key=TOPIC,
    number=2,
    title="Satır yüzdesi mi, sütun yüzdesi mi?",
    question=(
        "Bölümlerin büyüklüğü değişirse satır yüzdeleri ve sütun yüzdeleri nasıl değişir? Hangisi \"bölüm "
        "içindeki tercihi\" anlatır?"
    ),
    note=NoteRef("2.8", objects=("Tablo 2.5",)),
    parameters=(
        SimParameter("pi", "İktisat öğrencilerinin payı π", 0.1, 0.9, 0.67, 0.01,
                     "Notlardaki örnekte 60 öğrencinin 40'ı İktisat'tadır (π ≈ 0,67)."),
        SimParameter("n", "Öğrenci sayısı", 200, 5000, 1000, 100,
                     "Ankete yanıt veren öğrenci sayısı.", integer=True, decimals=0),
    ),
    dgp=_denominator_dgp,
    dgp_note="Her bölümün kendi içindeki tercih olasılıkları Tablo 2.5'teki satır yüzdeleridir ve π'den bağımsızdır.",
    look_at=(
        "**Satır yüzdeleri** — her bölüm kendi içinde %100'e tamamlanır.",
        "**Sütun yüzdeleri** — her materyal tercihinin bölüm bileşimi; her sütun %100'e tamamlanır.",
    ),
    build=_build_denominator,
    metrics=_denominator_metrics,
    takeaway=_denominator_takeaway,
    tables=(("satir_yuzde", "Satır yüzdeleri"), ("sutun_yuzde", "Sütun yüzdeleri")),
    labels=(("bolum", "Bölüm"), ("materyal", "Materyal")),
)


# --- Deney 3: Simpson paradoksu -------------------------------------------------------

OUTCOMES = ("Dönüştü", "Dönüşmedi")
RATES = {("Kolay", "A"): 0.90, ("Kolay", "B"): 0.95, ("Zor", "A"): 0.10, ("Zor", "B"): 0.20}
"""Tablo 2.6'daki alt grup dönüşüm oranları."""


def _overall(design: str, easy_share: float) -> float:
    return 100 * (easy_share * RATES[("Kolay", design)] + (1 - easy_share) * RATES[("Zor", design)])


def _build_simpson(parameters: Parameters) -> tuple:
    n = int(parameters["n"])
    share_a, share_b = round(float(parameters["a_A"]), 4), round(float(parameters["a_B"]), 4)
    outcome_probabilities = tuple(
        ((group, design), (rate, round(1 - rate, 4))) for (group, design), rate in RATES.items()
    )
    return (
        NewSample("musteri", 2 * n, SEED),
        Groups("musteri", "tasarim", ("A", "B"), (n, n), "İlk n müşteri A, sonraki n müşteri B tasarımını görür"),
        DrawCategory(
            "musteri", "grup", ("Kolay", "Zor"),
            ((("A",), (share_a, round(1 - share_a, 4))), (("B",), (share_b, round(1 - share_b, 4)))),
            "Tasarıma göre müşteri grubu: tasarımlar gruplara farklı oranlarda gösterilir", by=("tasarim",),
        ),
        DrawCategory("musteri", "sonuc", OUTCOMES, outcome_probabilities,
                     "Gruba ve tasarıma göre dönüşüm", by=("grup", "tasarim")),
        CrossTab("musteri", "tasarim", "grup", "dagilim", ("A", "B"), ("Kolay", "Zor"), percent="satir"),
        CrossTab("musteri", "tasarim", "sonuc", "kolay_oran", ("A", "B"), OUTCOMES, percent="satir",
                 where=("grup", "Kolay")),
        CrossTab("musteri", "tasarim", "sonuc", "zor_oran", ("A", "B"), OUTCOMES, percent="satir",
                 where=("grup", "Zor")),
        CrossTab("musteri", "tasarim", "sonuc", "genel_oran", ("A", "B"), OUTCOMES, percent="satir"),
        CompareBarChart(
            (("Kolay grup", "kolay_oran"), ("Zor grup", "zor_oran"), ("Tüm gruplar", "genel_oran")),
            "Dönüştü", "Müşteri grubu", "Dönüşüm oranı (%)", "Tasarıma göre dönüşüm oranı: alt gruplar ve toplam",
        ),
    )


def _simpson_dgp(parameters: Parameters) -> tuple[str, ...]:
    return (
        r"P(\text{dönüşüm}) = \begin{cases} 0{,}90 \ (\text{Kolay, A}), & 0{,}95 \ (\text{Kolay, B}) \\ "
        r"0{,}10 \ (\text{Zor, A}), & 0{,}20 \ (\text{Zor, B}) \end{cases}",
        rf"P(\text{{Kolay}} \mid \text{{A}}) = a_A = {number(parameters['a_A'], 2)}, \qquad "
        rf"P(\text{{Kolay}} \mid \text{{B}}) = a_B = {number(parameters['a_B'], 2)}",
        rf"\text{{Her tasarım }} n = {int(parameters['n'])} \text{{ müşteriye gösterilir}}",
    )


def _gap(table, row_a: str = "A", row_b: str = "B") -> float:
    return float(table.loc[row_b, "Dönüştü"] - table.loc[row_a, "Dönüştü"])


def _simpson_metrics(state: LabState, parameters: Parameters) -> tuple[SimMetric, ...]:
    return (
        SimMetric("Kolay grupta B − A", plain(_gap(state.tables["kolay_oran"]), 1) + " puan",
                  "Kolay müşteri grubunda iki tasarımın dönüşüm oranı farkı (yüzde puan)."),
        SimMetric("Zor grupta B − A", plain(_gap(state.tables["zor_oran"]), 1) + " puan",
                  "Zor müşteri grubunda iki tasarımın dönüşüm oranı farkı (yüzde puan)."),
        SimMetric("Tüm gruplarda B − A", plain(_gap(state.tables["genel_oran"]), 1) + " puan",
                  "Gruplar birleştirildiğinde fark. DGP'den beklenen: "
                  f"{plain(_overall('B', parameters['a_B']) - _overall('A', parameters['a_A']), 1)} puan."),
    )


def _simpson_takeaway(state: LabState, parameters: Parameters) -> str:
    easy, hard, overall = (_gap(state.tables[name]) for name in ("kolay_oran", "zor_oran", "genel_oran"))
    if easy > 0 and hard > 0 and overall < 0:
        return (
            "Simpson paradoksu: B iki grupta da daha yüksek, gruplar birleşince A daha yüksek görünüyor. "
            "Nedeni bileşimdir: A'nın müşterilerinin çoğu dönüşümün zaten yüksek olduğu kolay gruptadır. "
            "a_A ile a_B'yi birbirine yaklaştırın: paradoks kaybolur (§2.11)."
        )
    return (
        "Şu an toplam oran alt gruplardaki sonucu izliyor: tasarımlar gruplara benzer oranlarda gösterildiğinde "
        "bileşim karşılaştırmayı bozmaz. a_A'yı artırıp a_B'yi azaltın: toplam oran alt gruplardaki sonuçla "
        "ters yöne dönebilir (§2.11)."
    )


SIMPSON = SimExperiment(
    topic_key=TOPIC,
    number=3,
    title="Simpson paradoksu: bileşim etkisi",
    question=(
        "Bir reklam tasarımı her müşteri grubunda daha başarılıyken, bütün müşterilerde nasıl daha başarısız "
        "görünebilir?"
    ),
    note=NoteRef("2.11", objects=("Tablo 2.6",)),
    parameters=(
        SimParameter("a_A", "A tasarımını görenlerde kolay grup payı a_A", 0.05, 0.95, 0.91, 0.01,
                     "Notlardaki örnekte A'yı gören 110 müşterinin 100'ü kolay gruptadır (≈ 0,91)."),
        SimParameter("a_B", "B tasarımını görenlerde kolay grup payı a_B", 0.05, 0.95, 0.33, 0.01,
                     "Notlardaki örnekte B'yi gören 60 müşterinin 20'si kolay gruptadır (≈ 0,33)."),
        SimParameter("n", "Her tasarımı gören müşteri sayısı", 200, 5000, 1000, 100,
                     "Her tasarım bu kadar müşteriye gösterilir.", integer=True, decimals=0),
    ),
    dgp=_simpson_dgp,
    dgp_note=(
        "Alt gruplardaki dönüşüm olasılıkları Tablo 2.6'daki oranlardır: her iki grupta B daha başarılıdır. "
        "Kaydırıcılar yalnız tasarımların hangi gruba ne oranda gösterildiğini değiştirir."
    ),
    look_at=(
        "**Grafik** — kolay grup, zor grup ve bütün müşteriler için iki tasarımın dönüşüm oranı.",
        "**Bileşim tablosu** — her tasarımı gören müşterilerin kolay ve zor gruplara dağılımı.",
    ),
    build=_build_simpson,
    metrics=_simpson_metrics,
    takeaway=_simpson_takeaway,
    tables=(("dagilim", "Tasarımı görenlerin müşteri grubuna dağılımı (satır %)"),),
    labels=(("tasarim", "Tasarım"), ("grup", "Müşteri grubu"), ("sonuc", "Sonuç")),
)


KONU02_EXPERIMENTS = (FREQUENCY_OR_PERCENT, ROW_OR_COLUMN, SIMPSON)
