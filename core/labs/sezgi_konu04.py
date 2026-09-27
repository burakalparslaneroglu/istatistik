"""Konu 4 Sezgi deneyleri: veri üretim süreci bilinen kontrollü simülasyonlar.

Deney 1  Uç değer: ortalama mı, medyan mı?                 (Notlar §4.3, §4.6)
Deney 2  Yüzdelik kuralı: ders kuralı ve yazılım            (Notlar §4.8)
Deney 3  Bileşik büyüme: aritmetik mi, geometrik mi?        (Notlar §4.10)
"""

from __future__ import annotations

from core.labs import expr as E
from core.labs.runner import LabState
from core.labs.sezgi import Parameters, SimExperiment, SimMetric, SimParameter, number, percent, plain
from core.labs.spec import (
    Derive,
    DotPlot,
    Draw,
    DrawCategory,
    Groups,
    Histogram,
    MapCodes,
    MonteCarlo,
    NewSample,
    NoteRef,
    Percentile,
    Scalar,
    ScalarTable,
    Statistic,
)

SEED = 217
TOPIC = "konu04"


# --- Deney 1: uç değer ------------------------------------------------------------------

BASE, SPREAD = 22, 3
"""Olağan günlerde satış N(22, 3²), tam sayıya (bin TL) yuvarlanır; notlardaki satış verisine benzer."""


def _build_outlier(parameters: Parameters) -> tuple:
    n, k, delta = int(parameters["n"]), int(parameters["k"]), int(parameters["delta"])
    usual = E.rounded(E.add(BASE, E.mul(SPREAD, E.var("z"))))
    sales = E.add(E.mul(E.sub(1, E.var("uc")), usual), E.mul(E.var("uc"), BASE + delta))
    return (
        NewSample("gun", n, SEED),
        Groups("gun", "tur", ("Olağan", "Uç"), (n - k, k), "İlk n − k gün olağan, son k gün uç değerli"),
        MapCodes("gun", "tur", "uc", (("Olağan", 0), ("Uç", 1)), "Uç = 1, Olağan = 0"),
        Draw("gun", "z", "normal", 0, 1, "Standart normal çekiliş"),
        Derive("gun", "gelir", sales, "Günlük satış geliri (bin TL)"),
        Statistic("gun", "gelir", "mean", "ortalama", "Ortalama", decimals=2),
        Statistic("gun", "gelir", "median", "medyan", "Medyan", decimals=2),
        Scalar("fark", E.sub(E.ref("ortalama"), E.ref("medyan")), "Ortalama − medyan", decimals=2),
        Scalar("beklenen_kayma", E.div(E.mul(k, delta), n), "Uç değerlerin ortalamaya beklenen katkısı kΔ/n",
               decimals=2),
        DotPlot("gun", "gelir", "Satış geliri (bin TL)", "Günlük satışlar: medyan ve ortalama",
                references=(("medyan", "Medyan"), ("ortalama", "Ortalama"))),
    )


def _outlier_dgp(parameters: Parameters) -> tuple[str, ...]:
    n, k, delta = int(parameters["n"]), int(parameters["k"]), int(parameters["delta"])
    return (
        rf"\text{{Olağan gün: }} X = \text{{yuvarla}}({BASE} + {SPREAD}Z), \qquad Z \sim N(0,\ 1)",
        rf"\text{{Uç gün: }} X = {BASE} + \Delta = {BASE + delta}, \qquad k = {k} \text{{ gün}}, \qquad n = {n}",
    )


def _outlier_metrics(state: LabState, parameters: Parameters) -> tuple[SimMetric, ...]:
    s = state.scalars
    return (
        SimMetric("Ortalama", plain(s["ortalama"], 2), "Bütün günlerin satış ortalaması (bin TL)."),
        SimMetric("Medyan", plain(s["medyan"], 2), "Sıralanmış satışların ortadaki değeri (bin TL)."),
        SimMetric("Ortalama − medyan", plain(s["fark"], 2), "Uç değerler ortalamayı medyandan ne kadar uzaklaştırdı?"),
        SimMetric("Beklenen kayma kΔ/n", plain(s["beklenen_kayma"], 2),
                  "DGP: k uç günün ortalamaya ekleyeceği yaklaşık miktar."),
    )


def _outlier_takeaway(state: LabState, parameters: Parameters) -> str:
    n, k, delta = int(parameters["n"]), int(parameters["k"]), int(parameters["delta"])
    if k == 0 or delta == 0:
        return ("Uç değer yok: ortalama ile medyan birbirine yakın. Uç değerli gün sayısını ya da uç değerlerin "
                "büyüklüğünü artırın (§4.3).")
    if 2 * k >= n:
        return ("Uç değerli günler günlerin yarısına ulaştı: medyan da uç değerlere kayıyor. Medyan ancak uç "
                "değerler azınlıktayken onların büyüklüğüne duyarsızdır (§4.6).")
    return (
        f"{k} uç gün ortalamayı yaklaşık kΔ/n = {plain(k * delta / n, 2)} bin TL yukarı çekiyor; medyan olağan "
        "günlerin ortasında kalıyor. Ortalama bütün büyüklükleri kullanır, medyan sıralamadaki konuma dayanır. "
        "Tipik günü betimlemek için medyan, toplamla ilgili sorular için ortalama bilgilendiricidir (§4.6)."
    )


OUTLIER = SimExperiment(
    topic_key=TOPIC,
    number=1,
    title="Uç değer: ortalama mı, medyan mı?",
    question="Birkaç olağan dışı yüksek satış günü ortalamayı ve medyanı ne kadar değiştirir?",
    note=NoteRef("4.6", objects=("Şekil 4.6",)),
    parameters=(
        SimParameter("delta", "Uç değerin büyüklüğü Δ (bin TL)", 0, 100, 30, 5,
                     "Uç günde satış 22 + Δ bin TL'dir. Notlardaki örnekte 26 yerine 56 (Δ = 34).",
                     integer=True, decimals=0),
        SimParameter("k", "Uç değerli gün sayısı k", 0, 10, 1, 1, "Olağan dışı yüksek satış yapılan gün sayısı.",
                     integer=True, decimals=0),
        SimParameter("n", "Gün sayısı n", 20, 200, 30, 10, "Gözlenen gün sayısı.", integer=True, decimals=0),
    ),
    dgp=_outlier_dgp,
    dgp_note="Olağan günlerin satışları 22 bin TL civarındadır; son k gün olağan dışı yüksek satış yapılır.",
    look_at=(
        "**Nokta grafiği** — uç günler sağda ayrı durur; medyan ve ortalama çizgilerinin konumu.",
        "**Ortalama − medyan** — uç değerlerin ortalamayı ne kadar çektiği; kΔ/n ile karşılaştırın.",
    ),
    build=_build_outlier,
    metrics=_outlier_metrics,
    takeaway=_outlier_takeaway,
    labels=(("gelir", "Satış geliri (bin TL)"),),
)


# --- Deney 2: yüzdelik kuralı -------------------------------------------------------------

SCORE_MEAN, SCORE_SD = 50, 10


def _build_percentile(parameters: Parameters) -> tuple:
    n, p = int(parameters["n"]), int(parameters["p"])
    return (
        NewSample("sinav", n, SEED),
        Draw("sinav", "z", "normal", 0, 1, "Standart normal çekiliş"),
        Derive("sinav", "puan", E.add(SCORE_MEAN, E.mul(SCORE_SD, E.var("z"))), "Sınav puanı"),
        Percentile("sinav", "puan", p, "P_ders", f"{p}. yüzdelik, ders kuralı", location="L_ders"),
        Percentile("sinav", "puan", p, "P_yazilim", f"{p}. yüzdelik, yazılım varsayılanı", location="L_yazilim",
                   method="yazilim"),
        Scalar("fark", E.sub(E.ref("P_ders"), E.ref("P_yazilim")), "İki kuralın farkı", decimals=2),
        Scalar("P_anakutle", E.add(SCORE_MEAN, E.mul(SCORE_SD, E.norminv(p / 100))),
               f"Anakütlenin {p}. yüzdeliği (DGP)", decimals=2),
        ScalarTable(
            (
                ("Konum, ders kuralı: (p/100)(n + 1)", E.ref("L_ders")),
                ("Konum, yazılım varsayılanı: 1 + (p/100)(n − 1)", E.ref("L_yazilim")),
                ("Yüzdelik, ders kuralı", E.ref("P_ders")),
                ("Yüzdelik, yazılım varsayılanı", E.ref("P_yazilim")),
                ("Anakütle yüzdeliği (DGP)", E.ref("P_anakutle")),
            ),
            "kurallar",
        ),
        DotPlot("sinav", "puan", "Sınav puanı", "Örneklem ve iki kuralın yüzdeliği",
                references=(("P_ders", "Ders kuralı"), ("P_yazilim", "Yazılım varsayılanı"))),
    )


def _percentile_dgp(parameters: Parameters) -> tuple[str, ...]:
    n, p = int(parameters["n"]), int(parameters["p"])
    return (
        rf"X \sim N({SCORE_MEAN},\ {SCORE_SD}^2), \qquad n = {n}, \qquad p = {p}",
        rf"L_p = \frac{{p}}{{100}}(n + 1) = {number(p / 100 * (n + 1), 2)} \quad \text{{(ders)}}, \qquad "
        rf"1 + \frac{{p}}{{100}}(n - 1) = {number(1 + p / 100 * (n - 1), 2)} \quad \text{{(yazılım)}}",
    )


def _percentile_metrics(state: LabState, parameters: Parameters) -> tuple[SimMetric, ...]:
    s = state.scalars
    p = int(parameters["p"])
    return (
        SimMetric(f"P{p} (ders)", plain(s["P_ders"], 2), "Lₚ = (p/100)(n + 1) konumunda doğrusal ara değer."),
        SimMetric(f"P{p} (yazılım)", plain(s["P_yazilim"], 2),
                  "numpy ve R varsayılanı: 1 + (p/100)(n − 1) konumunda doğrusal ara değer."),
        SimMetric("Fark", plain(s["fark"], 2), "Ders kuralı − yazılım varsayılanı (puan)."),
        SimMetric(f"Anakütle P{p}", plain(s["P_anakutle"], 2), "DGP'deki gerçek yüzdelik: 50 + 10 Φ⁻¹(p/100)."),
    )


def _percentile_takeaway(state: LabState, parameters: Parameters) -> str:
    n, p = int(parameters["n"]), int(parameters["p"])
    gap = abs(state.scalars["fark"])
    shift = plain(2 * p / 100 - 1, 1)
    if p == 50:
        text = "p = 50'de iki kural aynı konumu verir: ikisi de medyandır. "
    else:
        text = (f"n = {n} ve p = {p} için iki kuralın yüzdelikleri {plain(gap, 2)} puan farklı. Konum farkı "
                f"(ders − yazılım) her n için 2p/100 − 1 = {shift} sıradır; mutlak değeri p = 50'den uzaklaştıkça "
                "büyür. Yüzdelik farkı yaklaşık olarak bu sıra farkı ile komşu gözlemler arasındaki uzaklığın "
                "çarpımıdır; n büyüdükçe gözlemler sıklaştığı için küçülür. ")
    return text + ("Farklı yazılımların farklı sonuç vermesi hata değildir; bu derste tutarlılık için "
                   "Lₚ = (p/100)(n + 1) kuralı kullanılır (§4.8).")


PERCENTILE_RULE = SimExperiment(
    topic_key=TOPIC,
    number=2,
    title="Yüzdelik kuralı: ders kuralı ve yazılım",
    question="Aynı veride ders kuralı ile yazılımların varsayılan kuralı neden farklı yüzdelik verir ve fark ne "
             "zaman küçülür?",
    note=NoteRef("4.8", objects=("Şekil 4.8",)),
    parameters=(
        SimParameter("p", "Yüzdelik p", 10, 90, 60, 5, "Notlardaki örnekte p = 60.", integer=True, decimals=0),
        SimParameter("n", "Gözlem sayısı n", 9, 60, 12, 1, "Notlardaki örnekte n = 12.", integer=True, decimals=0),
    ),
    dgp=_percentile_dgp,
    dgp_note=(
        "Puanlar normal dağılımdan çekilir. p en az 10, n en az 9 olduğu için iki konum da 1 ile n arasındadır; "
        "yüzdelik her zaman iki komşu gözlem arasında ara değerle bulunur."
    ),
    look_at=(
        "**Konumlar** — ders kuralı (p/100)(n + 1), yazılım varsayılanı 1 + (p/100)(n − 1).",
        "**Nokta grafiği** — iki kuralın yüzdeliği ve örneklemdeki gözlemler.",
    ),
    build=_build_percentile,
    metrics=_percentile_metrics,
    takeaway=_percentile_takeaway,
    tables=(("kurallar", "Konumlar ve yüzdelikler"),),
    labels=(("puan", "Sınav puanı"),),
)


# --- Deney 3: bileşik büyüme --------------------------------------------------------------

INVESTORS = 400


def _equal_years_growth(change: float) -> float:
    """Artış ve azalış yılları eşit sayıdaysa yıllık bileşik değişim (%): (√(1 − (x/100)²) − 1) × 100."""

    return 100 * ((1 - (change / 100) ** 2) ** 0.5 - 1)


def _investor(years: int, change: int) -> tuple:
    return (
        NewSample("yillar", years, None),
        DrawCategory("yillar", "yon", ("Artış", "Azalış"), (((), (0.5, 0.5)),), "Her yıl yarı olasılıkla artış"),
        MapCodes("yillar", "yon", "isaret", (("Artış", 1), ("Azalış", -1)), "Artış = +1, Azalış = −1"),
        Derive("yillar", "degisim", E.mul(change, E.var("isaret")), "Yıllık yüzde değişim"),
        Derive("yillar", "faktor", E.add(1, E.div(E.var("degisim"), 100)), "Büyüme faktörü 1 + değişim/100"),
        Statistic("yillar", "degisim", "mean", "aritmetik", "Yüzde değişimlerin aritmetik ortalaması", decimals=2),
        Statistic("yillar", "faktor", "prod", "carpim", "Faktörlerin çarpımı", decimals=4),
    )


def _build_growth(parameters: Parameters) -> tuple:
    years, change = int(parameters["T"]), int(parameters["x"])
    geometric = E.mul(100, E.sub(E.power(E.ref("carpim"), 1 / years), 1))
    return (
        MonteCarlo(
            "yatirimcilar",
            INVESTORS,
            SEED,
            _investor(years, change),
            (
                ("aritmetik", E.ref("aritmetik")),
                ("geometrik", geometric),
                ("son_deger", E.mul(100, E.ref("carpim"))),
                ("kayip", E.compare("lt", E.ref("carpim"), 1)),
            ),
            "Her tekrar bir yatırımcı: 100 TL, T yıl boyunca her yıl yarı olasılıkla %x artar ya da azalır",
        ),
        Histogram(
            "yatirimcilar",
            (("aritmetik", "Aritmetik ortalama"), ("geometrik", "Bileşik (geometrik) değişim")),
            40,
            -change - 1,
            change + 1,
            f"{INVESTORS} yatırımcıda yıllık ortalama değişim",
            "Yıllık değişim (%)",
            references=((0.0, "Aritmetik: beklenen 0"),
                        (round(_equal_years_growth(change), 6), "Eşit artış–azalışta bileşik")),
        ),
    )


def _growth_dgp(parameters: Parameters) -> tuple[str, ...]:
    years, change = int(parameters["T"]), int(parameters["x"])
    return (
        rf"r_t = \begin{{cases}} +{change} & \text{{olasılık }} 1/2 \\ -{change} & \text{{olasılık }} 1/2 "
        rf"\end{{cases}}, \qquad g_t = 1 + \frac{{r_t}}{{100}}, \qquad T = {years}",
        rf"G = (g_1 g_2 \cdots g_T)^{{1/T}}, \qquad \text{{son değer}} = 100\, G^{{T}}, \qquad "
        rf"{INVESTORS} \text{{ yatırımcı}}",
    )


def _growth_summary(state: LabState) -> tuple[float, float, float]:
    table = state.tables["yatirimcilar"]
    return float(table["aritmetik"].mean()), float(table["geometrik"].mean()), float(100 * table["kayip"].mean())


def _growth_metrics(state: LabState, parameters: Parameters) -> tuple[SimMetric, ...]:
    arithmetic, geometric, losers = _growth_summary(state)
    return (
        SimMetric("Ort. aritmetik değişim", percent(arithmetic, 2),
                  "Yatırımcıların yıllık yüzde değişimlerinin basit ortalaması (yatırımcılar üzerinden ortalama)."),
        SimMetric("Ort. bileşik değişim", percent(geometric, 2),
                  "(G − 1) × 100: yatırımın yıllık ortalama bileşik değişimi (yatırımcılar üzerinden ortalama)."),
        SimMetric("Para kaybeden", percent(losers, 1), "Son değeri 100 TL'nin altında kalan yatırımcıların payı."),
        SimMetric("Eşit artış–azalışta", percent(_equal_years_growth(int(parameters["x"])), 2),
                  "Artış ve azalış yılları eşit sayıdaysa bileşik değişim: (√(1 − (x/100)²) − 1) × 100."),
    )


def _growth_takeaway(state: LabState, parameters: Parameters) -> str:
    change = int(parameters["x"])
    if change == 0:
        return "Değişim yok: aritmetik ve geometrik ortalama aynıdır, 100 TL yerinde kalır (§4.10)."
    arithmetic, geometric, losers = _growth_summary(state)
    return (
        f"Yıllık değişimlerin aritmetik ortalaması ortalamada {percent(arithmetic, 2)}, yani sıfıra yakın; ama "
        f"yatırımın bileşik değişimi {percent(geometric, 2)}; para kaybeden yatırımcıların payı "
        f"{percent(losers, 1)}. Bir yıl %{change} artıp bir yıl %{change} azalmak yerinde saymak değildir: "
        f"1,{change:02d} × 0,{100 - change:02d} < 1. Ardışık oranlar çarpımsal işler; ortalama bileşik büyüme "
        "geometrik ortalamayla ölçülür ve x büyüdükçe aritmetik ortalamadan uzaklaşır (§4.10)."
    )


COMPOUND_GROWTH = SimExperiment(
    topic_key=TOPIC,
    number=3,
    title="Bileşik büyüme: aritmetik mi, geometrik mi?",
    question="Her yıl yarı olasılıkla %x artan ya da %x azalan bir yatırımın ortalama büyümesi nasıl ölçülür?",
    note=NoteRef("4.10", objects=("Şekil 4.10",)),
    parameters=(
        SimParameter("x", "Yıllık değişimin büyüklüğü x (%)", 0, 50, 10, 5,
                     "Notlardaki örnekte %10 artış ve %10 azalış.", integer=True, decimals=0),
        SimParameter("T", "Yıl sayısı T", 10, 50, 20, 10, "Her yatırımcının yatırım süresi.", integer=True,
                     decimals=0),
    ),
    dgp=_growth_dgp,
    dgp_note=(
        "Her yıl bağımsız olarak yarı olasılıkla %x artış ya da %x azalış olur; başlangıç değeri 100 TL. Beklenen "
        "yüzde değişim sıfırdır. Artış ve azalış yılları eşit sayıdaysa yıllık bileşik değişim "
        "(√(1 − (x/100)²) − 1) × 100'dür: x = 10 için %−0,5 (notlardaki örnek)."
    ),
    look_at=(
        "**Histogram** — yatırımcıların aritmetik ortalama değişimi ile bileşik (geometrik) değişimi.",
        "**Para kaybedenler** — beklenen yüzde değişim sıfırken son değeri 100 TL'nin altında kalanların payı.",
    ),
    build=_build_growth,
    metrics=_growth_metrics,
    takeaway=_growth_takeaway,
)


KONU04_EXPERIMENTS = (OUTLIER, PERCENTILE_RULE, COMPOUND_GROWTH)
