"""Konu 1 Sezgi deneyleri: veri üretim süreci bilinen kontrollü simülasyonlar.

Deney 1  Sıralı kategorilere sayı kodu vermek          (Notlar §1.4)
Deney 2  Gözlemsel çalışma ve deney                    (Notlar §1.6)
Deney 3  Büyük ama yanlı örneklem, küçük ama rastgele  (Notlar §1.8)
"""

from __future__ import annotations

import numpy as np

from core.labs import expr as E
from core.labs.runner import LabState
from core.labs.sezgi import Parameters, SimExperiment, SimMetric, SimParameter, number, plain
from core.labs.spec import (
    BarChart,
    CrossTab,
    Derive,
    Draw,
    DrawCategory,
    GroupedBarChart,
    Groups,
    GroupSummary,
    Histogram,
    MapCodes,
    MonteCarlo,
    NewSample,
    NoteRef,
    Scalar,
    ScalarTable,
    Statistic,
)

SEED = 217
TOPIC = "konu01"


# --- Deney 1: sıralı kategoriler ve sayı kodları ------------------------------------

LEVELS = ("Düşük", "Orta", "Yüksek")
PROB_A = (0.05, 0.75, 0.20)
PROB_B = (0.40, 0.20, 0.40)
"""A şubesinde yanıtlar ortada toplanır; B şubesinde müşteriler kutuplaşmıştır."""


def _code_mean(probabilities: tuple[float, ...], top: float) -> float:
    return probabilities[0] * 1 + probabilities[1] * 2 + probabilities[2] * top


CROSSING = (_code_mean(PROB_B, 0) - _code_mean(PROB_A, 0)) / (PROB_A[2] - PROB_B[2])
"""Anakütlede iki şubenin kod ortalamasının eşitlendiği c değeri: 3,75."""


def _build_codes(parameters: Parameters) -> tuple:
    n, top = int(parameters["n"]), round(float(parameters["c"]), 4)
    return (
        NewSample("anket", 2 * n, SEED),
        Groups("anket", "sube", ("A", "B"), (n, n), "İlk n müşteri A şubesinde, sonraki n müşteri B şubesinde"),
        DrawCategory(
            "anket", "memnuniyet", LEVELS, ((("A",), PROB_A), (("B",), PROB_B)),
            "Şubeye göre memnuniyet düzeyi", by=("sube",),
        ),
        MapCodes("anket", "memnuniyet", "kod_123", (("Düşük", 1), ("Orta", 2), ("Yüksek", 3)),
                 "Alışılmış kodlama: 1, 2, 3"),
        MapCodes("anket", "memnuniyet", "kod_12c", (("Düşük", 1), ("Orta", 2), ("Yüksek", top)),
                 f"Aynı sırayı koruyan başka bir kodlama: 1, 2, {E.format_number(top)}"),
        CrossTab("anket", "sube", "memnuniyet", "dagilim", ("A", "B"), LEVELS, percent="satir"),
        GroupedBarChart(
            "dagilim", "Memnuniyet düzeyi", "Şube içindeki yüzde",
            "Şubelere göre memnuniyet dağılımı (kodlamadan bağımsız)", series="satir", decimals=1,
        ),
        GroupSummary(
            "anket", "sube", (("ort_123", "kod_123", "mean"), ("ort_12c", "kod_12c", "mean")),
            "ortalamalar", ("A", "B"),
        ),
    )


def _codes_dgp(parameters: Parameters) -> tuple[str, ...]:
    return (
        r"\text{Şube A: } P(\text{Düşük},\ \text{Orta},\ \text{Yüksek}) = (0{,}05;\ 0{,}75;\ 0{,}20)",
        r"\text{Şube B: } P(\text{Düşük},\ \text{Orta},\ \text{Yüksek}) = (0{,}40;\ 0{,}20;\ 0{,}40)",
        rf"\text{{Kodlar: }} (1,\ 2,\ 3) \ \text{{ve}}\ (1,\ 2,\ c), \qquad c = {number(parameters['c'], 2)}",
    )


def _sample_crossing(state: LabState) -> float:
    """Örneklem yüzdeleriyle iki şubenin kod ortalamasını eşitleyen c."""

    share = state.tables["dagilim"] / 100
    a, b = share.loc["A"], share.loc["B"]
    return float((b["Düşük"] + 2 * b["Orta"] - a["Düşük"] - 2 * a["Orta"]) / (a["Yüksek"] - b["Yüksek"]))


def _leader(table, column: str) -> str:
    a, b = table.loc["A", column], table.loc["B", column]
    return "A" if a > b else "B"


def _codes_metrics(state: LabState, parameters: Parameters) -> tuple[SimMetric, ...]:
    table = state.tables["ortalamalar"]
    return (
        SimMetric("Önde olan şube, kod 1-2-3", _leader(table, "ort_123"),
                  "Kod ortalaması daha yüksek olan şube (1, 2, 3 kodlamasıyla)."),
        SimMetric("Önde olan şube, kod 1-2-c", _leader(table, "ort_12c"),
                  "Kod ortalaması daha yüksek olan şube (1, 2, c kodlamasıyla)."),
        SimMetric("Sıralamanın değiştiği c", plain(_sample_crossing(state), 2),
                  "Bu örneklemde iki şubenin kod ortalamasını eşitleyen c değeri. "
                  f"Anakütlede {plain(CROSSING, 2)}."),
    )


def _codes_takeaway(state: LabState, parameters: Parameters) -> str:
    crossing = _sample_crossing(state)
    text = (
        "İki kodlama da Düşük < Orta < Yüksek sırasını korur; yanıtlar ve yüzdeler hiç değişmez. "
        "Değişen tek şey \"Yüksek\" ile \"Orta\" arasındaki aralığın varsayılan büyüklüğüdür. "
    )
    if parameters["c"] > crossing:
        text += (
            f"c = {plain(parameters['c'], 2)} ile B şubesi önde görünüyor; 1-2-3 kodlamasında A öndeydi. "
            "Hangi şubenin \"daha memnun\" olduğu verideki bilgiden değil, keyfî kod aralığından geliyor."
        )
    else:
        text += (
            f"c = {plain(parameters['c'], 2)} henüz sıralamanın değiştiği {plain(crossing, 2)} değerinin altında. "
            "c'yi artırın: aynı yanıtlarla sıralama tersine döner."
        )
    return text + " Ordinal veride sıralama anlamlıdır; eşit aralık varsayımı değildir (§1.4)."


ORDINAL_CODES = SimExperiment(
    topic_key=TOPIC,
    number=1,
    title="Sıralı kategorilere sayı kodu vermek",
    question=(
        "Memnuniyet gibi sıralı (ordinal) kategorilere 1, 2, 3 kodu verip ortalamasını almak iki şubeyi "
        "karşılaştırmak için güvenilir mi?"
    ),
    note=NoteRef("1.4", objects=("Tablo 1.2",)),
    parameters=(
        SimParameter("n", "Her şubede müşteri sayısı", 100, 2000, 500, 100,
                     "Her şubede ankete yanıt veren müşteri sayısı.", integer=True, decimals=0),
        SimParameter("c", "\"Yüksek\" kategorisinin kodu c", 3.0, 10.0, 6.0, 0.25,
                     "c = 3 iken iki kodlama aynıdır. Her c > 2 değeri Düşük < Orta < Yüksek sırasını korur."),
    ),
    dgp=_codes_dgp,
    dgp_note=(
        "A şubesinde müşterilerin çoğu orta düzeyde memnun; B şubesinde müşteriler kutuplaşmış: çok sayıda "
        "düşük ve çok sayıda yüksek. Kodlar yalnız kategorilerin sırasını gösteren etiketlerdir."
    ),
    look_at=(
        "**Grafik** — şube içindeki yüzdeler. Kodlamadan bağımsızdır: c'yi değiştirmek grafiği değiştirmez.",
        "**Ortalama tablosu** — aynı yanıtların iki farklı kodlamayla ortalaması.",
        "**Sıralamanın değiştiği c** — iki şubenin kod ortalamasının eşitlendiği değer; c bunu aşınca "
        "önde görünen şube değişir.",
    ),
    build=_build_codes,
    metrics=_codes_metrics,
    takeaway=_codes_takeaway,
    tables=(("ortalamalar", "Şubelere göre kod ortalamaları"), ("dagilim", "Şube içindeki yüzdeler")),
    labels=(
        ("sube", "Şube"),
        ("ort_123", "Ortalama, kod 1-2-3"),
        ("ort_12c", "Ortalama, kod 1-2-c"),
        ("memnuniyet", "Memnuniyet"),
    ),
)


# --- Deney 2: gözlemsel çalışma ve deney --------------------------------------------

def _mean_where(frame: str, variable: str, group: str, value: int, name: str, comment: str) -> Statistic:
    return Statistic(frame, variable, "mean", name, comment, where=(group, value), decimals=2)


def _build_design(parameters: Parameters) -> tuple:
    n = int(parameters["n"])
    gamma, tau = round(float(parameters["gamma"]), 4), round(float(parameters["tau"]), 4)
    frame = "ogrenci"
    motivation, noise = E.var("motivasyon"), E.var("e")

    def score(treated: str) -> E.Expr:
        return E.add(E.add(E.add(60, E.mul(tau, E.var(treated))), E.mul(8, motivation)), noise)

    return (
        NewSample(frame, n, SEED),
        Draw(frame, "motivasyon", "normal", 0, 1, "Gözlenmeyen motivasyon M"),
        Draw(frame, "u", "normal", 0, 1, "Katılım kararındaki diğer etkenler"),
        Derive(frame, "katilim_gozlem", E.compare("gt", E.add(E.mul(gamma, motivation), E.var("u")), 0),
               "Gözlemsel çalışma: öğrenci programa katılıp katılmayacağına kendisi karar verir"),
        Draw(frame, "v", "uniform", 0, 1, "Yazı-tura için tekdüze sayı"),
        Derive(frame, "katilim_deney", E.compare("lt", E.var("v"), 0.5),
               "Deney: katılımı yazı-tura belirler"),
        Draw(frame, "e", "normal", 0, 5, "Puandaki diğer etkenler"),
        Derive(frame, "puan_gozlem", score("katilim_gozlem"), "Gözlemsel çalışmada sınav puanı"),
        Derive(frame, "puan_deney", score("katilim_deney"), "Deneyde sınav puanı"),
        _mean_where(frame, "puan_gozlem", "katilim_gozlem", 1, "puan_g1", "Gözlemsel: katılanların ortalama puanı"),
        _mean_where(frame, "puan_gozlem", "katilim_gozlem", 0, "puan_g0",
                    "Gözlemsel: katılmayanların ortalama puanı"),
        _mean_where(frame, "puan_deney", "katilim_deney", 1, "puan_d1", "Deney: katılanların ortalama puanı"),
        _mean_where(frame, "puan_deney", "katilim_deney", 0, "puan_d0", "Deney: katılmayanların ortalama puanı"),
        _mean_where(frame, "motivasyon", "katilim_gozlem", 1, "mot_g1", "Gözlemsel: katılanların motivasyonu"),
        _mean_where(frame, "motivasyon", "katilim_gozlem", 0, "mot_g0", "Gözlemsel: katılmayanların motivasyonu"),
        _mean_where(frame, "motivasyon", "katilim_deney", 1, "mot_d1", "Deney: katılanların motivasyonu"),
        _mean_where(frame, "motivasyon", "katilim_deney", 0, "mot_d0", "Deney: katılmayanların motivasyonu"),
        Scalar("fark_gozlem", E.sub(E.ref("puan_g1"), E.ref("puan_g0")), "Gözlemsel çalışmada puan farkı", 2),
        Scalar("fark_deney", E.sub(E.ref("puan_d1"), E.ref("puan_d0")), "Deneyde puan farkı", 2),
        ScalarTable(
            (
                ("Gerçek etki τ", E.const(tau)),
                ("Gözlemsel çalışma", E.ref("fark_gozlem")),
                ("Deney", E.ref("fark_deney")),
            ),
            "farklar",
        ),
        BarChart("farklar", "deger", "Karşılaştırma", "Puan farkı",
                 "Katılan − katılmayan puan farkı: gerçek etki ve iki tasarım", decimals=1),
        ScalarTable(
            (
                ("Gözlemsel çalışma", E.sub(E.ref("mot_g1"), E.ref("mot_g0"))),
                ("Deney", E.sub(E.ref("mot_d1"), E.ref("mot_d0"))),
            ),
            "denge",
        ),
    )


def _design_dgp(parameters: Parameters) -> tuple[str, ...]:
    return (
        r"M_i \sim N(0,1)\ \text{(gözlenmeyen motivasyon)}, \qquad u_i \sim N(0,1), \qquad e_i \sim N(0,\ 5^2)",
        rf"\text{{Gözlemsel çalışma: }} D_i = 1\{{\gamma M_i + u_i > 0\}}, \qquad \gamma = "
        rf"{number(parameters['gamma'], 2)}",
        r"\text{Deney: } D_i = 1\{V_i < 0{,}5\}, \qquad V_i \sim \text{Tekdüze}(0,1)\ \text{(yazı-tura)}",
        rf"Y_i = 60 + \tau D_i + 8 M_i + e_i, \qquad \tau = {number(parameters['tau'], 1)}",
    )


def _design_metrics(state: LabState, parameters: Parameters) -> tuple[SimMetric, ...]:
    balance = state.tables["denge"]["deger"]
    return (
        SimMetric("Gerçek etki τ", plain(parameters["tau"], 1), "Programın puana gerçek etkisi; DGP'den bilinir."),
        SimMetric("Gözlemsel çalışmada fark", plain(state.scalars["fark_gozlem"], 2),
                  "Katılanların ortalama puanı eksi katılmayanlarınki."),
        SimMetric("Deneyde fark", plain(state.scalars["fark_deney"], 2),
                  "Katılımı yazı-tura belirlediğinde aynı karşılaştırma."),
        SimMetric("Motivasyon farkı (gözlemsel)", plain(float(balance.iloc[0]), 2),
                  "Gözlemsel çalışmada katılanların ortalama motivasyonu eksi katılmayanlarınki."),
    )


def _design_takeaway(state: LabState, parameters: Parameters) -> str:
    if parameters["gamma"] == 0:
        return (
            "γ = 0: motivasyon katılım kararını etkilemiyor. Bu durumda gözlemsel çalışmadaki gruplar da "
            "motivasyon bakımından benzerdir ve iki tasarımın farkı gerçek etkiye yakındır. γ'yı artırın."
        )
    return (
        "Gözlemsel çalışmada daha motive öğrenciler programı daha sık seçer; katılanların puanı hem programın "
        "etkisini hem de yüksek motivasyonu taşır. Bu yüzden fark gerçek etkiden büyüktür. Deneyde katılımı "
        "yazı-tura belirlediği için iki grubun motivasyonu benzerdir ve fark gerçek etkiye yakındır. "
        "Birlikte hareket etmek, neden–sonuç ilişkisi kanıtı değildir (§1.6)."
    )


DESIGN = SimExperiment(
    topic_key=TOPIC,
    number=2,
    title="Gözlemsel çalışma ve deney",
    question=(
        "Ek çalışma programına katılan öğrencilerin puanı daha yüksekse, program puanı artırıyor mu? "
        "Aynı karşılaştırma gözlemsel çalışmada ve deneyde ne verir?"
    ),
    note=NoteRef("1.6"),
    parameters=(
        SimParameter("n", "Öğrenci sayısı", 200, 5000, 2000, 200,
                     "Örneklem büyüdükçe iki tasarımın sonucu da daha az dalgalanır.", integer=True, decimals=0),
        SimParameter("gamma", "Motivasyonun katılıma etkisi γ", 0.0, 2.0, 1.0, 0.1,
                     "γ = 0 iken katılım kararı motivasyondan bağımsızdır.", decimals=1),
        SimParameter("tau", "Programın gerçek etkisi τ (puan)", 0.0, 10.0, 5.0, 0.5,
                     "Programa katılmanın sınav puanına gerçek etkisi.", decimals=1),
    ),
    dgp=_design_dgp,
    dgp_note=(
        "N(0,1), ortalaması 0 olan çan biçimli bir dağılımdır (Konu 10). 1{·} koşul doğruysa 1, değilse 0 "
        "değerini alır. Gerçek veride motivasyon gözlenmez; burada veriyi biz ürettiğimiz için gerçek etki "
        "τ'yu biliyoruz."
    ),
    look_at=(
        "**Grafik** — katılanların ortalama puanı eksi katılmayanlarınki: gerçek etki, gözlemsel çalışma ve deney.",
        "**Motivasyon farkı** — iki grup, puanı etkileyen ama gözlenmeyen motivasyon bakımından benzer mi?",
    ),
    build=_build_design,
    metrics=_design_metrics,
    takeaway=_design_takeaway,
    tables=(("denge", "Katılanlar ile katılmayanlar arasındaki motivasyon farkı"),),
)


# --- Deney 3: temsil gücü -------------------------------------------------------------

POPULATION_CAR_SHARE = 0.2
CAR_MEAN, CAR_SD = 20.0, 6.0
OTHER_MEAN, OTHER_SD = 45.0, 12.0
POPULATION_MEAN = POPULATION_CAR_SHARE * CAR_MEAN + (1 - POPULATION_CAR_SHARE) * OTHER_MEAN
"""Anakütle ortalaması μ = 0,2 × 20 + 0,8 × 45 = 40 dakika."""
REPS = 200


def _sample(frame: str, size: int, car_share: float, name: str) -> tuple:
    car = E.var("arac")
    return (
        NewSample(frame, size, None),
        Draw(frame, "v", "uniform", 0, 1, "Tekdüze sayı"),
        Derive(frame, "arac", E.compare("lt", E.var("v"), car_share), f"Özel araçla gelir mi? (olasılık {car_share})"),
        Draw(frame, "sure_arac", "normal", CAR_MEAN, CAR_SD, "Özel araçla ulaşım süresi"),
        Draw(frame, "sure_diger", "normal", OTHER_MEAN, OTHER_SD, "Diğer ulaşım biçimleriyle süre"),
        Derive(frame, "sure", E.add(E.mul(car, E.var("sure_arac")), E.mul(E.sub(1, car), E.var("sure_diger"))),
               "Öğrencinin ulaşım süresi (dakika)"),
        Statistic(frame, "sure", "mean", name, "Örneklem ortalaması", decimals=2),
    )


def _build_representation(parameters: Parameters) -> tuple:
    share = round(float(parameters["q"]), 4)
    biased, random_size = int(parameters["n_yanli"]), int(parameters["n_rastgele"])
    return (
        MonteCarlo(
            "tekrarlar",
            REPS,
            SEED,
            _sample("yanli", biased, share, "yanli_ort") + _sample("rastgele", random_size, POPULATION_CAR_SHARE,
                                                                   "rastgele_ort"),
            (("yanli_ort", E.ref("yanli_ort")), ("rastgele_ort", E.ref("rastgele_ort"))),
            "Her tekrarda iki örneklem çekilir: otoparkta yapılan yanlı anket ve rastgele seçilmiş öğrenciler",
        ),
        Histogram(
            "tekrarlar",
            (
                ("yanli_ort", f"Yanlı örneklem (n = {biased})"),
                ("rastgele_ort", f"Rastgele örneklem (n = {random_size})"),
            ),
            80,
            15,
            55,
            f"{REPS} tekrarda örneklem ortalamaları",
            "Örneklem ortalaması (dakika)",
            references=((POPULATION_MEAN, "Anakütle ortalaması μ = 40"),),
        ),
    )


def _representation_dgp(parameters: Parameters) -> tuple[str, ...]:
    return (
        r"\text{Anakütle: öğrencilerin } \%20\text{'si özel araçla gelir}; \qquad \mu = 0{,}2 \times 20 + 0{,}8 "
        r"\times 45 = 40 \text{ dakika}",
        r"\text{Süre: özel araç } N(20,\ 6^2), \qquad \text{diğer } N(45,\ 12^2)",
        rf"\text{{Yanlı örneklem (otopark anketi): özel araç payı }} q = {number(parameters['q'], 2)}, "
        rf"\quad n = {int(parameters['n_yanli'])}",
        rf"\text{{Rastgele örneklem: özel araç payı }} 0{{,}}20, \quad n = {int(parameters['n_rastgele'])}",
    )


def _representation_metrics(state: LabState, parameters: Parameters) -> tuple[SimMetric, ...]:
    table = state.tables["tekrarlar"]
    biased, random = table["yanli_ort"].to_numpy(), table["rastgele_ort"].to_numpy()
    closer = float(np.mean(np.abs(random - POPULATION_MEAN) < np.abs(biased - POPULATION_MEAN)))
    expected = parameters["q"] * CAR_MEAN + (1 - parameters["q"]) * OTHER_MEAN
    return (
        SimMetric("Anakütle ortalaması μ", "40,0", "Bütün öğrencilerin ortalama ulaşım süresi; DGP'den bilinir."),
        SimMetric("Yanlı örneklem ortalamaları", plain(float(biased.mean()), 1),
                  f"{REPS} tekrarın ortalaması. Yanlı anketin hedeflediği değer: {plain(expected, 1)}."),
        SimMetric("Rastgele örneklem ortalamaları", plain(float(random.mean()), 1), f"{REPS} tekrarın ortalaması."),
        SimMetric("Rastgele örneklemin μ'ye daha yakın olduğu tekrarlar", "%" + plain(100 * closer, 0),
                  "Aynı tekrarda iki örneklemden hangisinin ortalaması 40'a daha yakın?"),
    )


def _representation_takeaway(state: LabState, parameters: Parameters) -> str:
    if parameters["q"] <= POPULATION_CAR_SHARE:
        return (
            "q = 0,20: yanlı anket anakütleyle aynı bileşimde, artık yanlı değil. Bu durumda büyük örneklem "
            "küçük örneklemden daha iyidir: ortalamaları μ çevresinde daha dar toplanır."
        )
    return (
        "Yanlı örneklem büyük olduğu için ortalamaları birbirine çok yakındır (dar histogram); fakat yanlış yerde, "
        "μ = 40'ın altında toplanır. Rastgele örneklem küçük ve daha dağınıktır ama merkezi μ'dedir. Yanlı "
        "örneklemin büyüklüğünü artırın: histogram daralır ama yer değiştirmez. Örneklem büyüklüğü temsil "
        "gücünün yerini tutmaz (§1.8)."
    )


REPRESENTATION = SimExperiment(
    topic_key=TOPIC,
    number=3,
    title="Büyük ama yanlı örneklem, küçük ama rastgele örneklem",
    question=(
        "Öğrencilerin ortalama ulaşım süresini tahmin etmek için otoparkta 2.000 kişiye mi sormak daha iyi, "
        "rastgele seçilmiş 200 öğrenciye mi?"
    ),
    note=NoteRef("1.8"),
    parameters=(
        SimParameter("q", "Yanlı örneklemde özel araç payı q", 0.2, 1.0, 0.7, 0.05,
                     "q = 0,20 anakütledeki paydır; q büyüdükçe anket özel araçlıları fazla temsil eder.",
                     decimals=2),
        SimParameter("n_yanli", "Yanlı örneklem büyüklüğü", 500, 10000, 2000, 500,
                     "Otoparkta anket yanıtlayan öğrenci sayısı.", integer=True, decimals=0),
        SimParameter("n_rastgele", "Rastgele örneklem büyüklüğü", 50, 1000, 200, 50,
                     "Bütün öğrenciler arasından rastgele seçilenlerin sayısı.", integer=True, decimals=0),
    ),
    dgp=_representation_dgp,
    dgp_note=(
        f"Deney {REPS} kez tekrarlanır: her tekrarda iki yeni örneklem çekilir ve ortalamaları kaydedilir. "
        "N(20, 6²), ortalaması 20 dakika olan çan biçimli bir dağılımdır (Konu 10)."
    ),
    look_at=(
        "**Histogram** — her tekrarda hesaplanan örneklem ortalamaları. Dar histogram, tekrardan tekrara az "
        "değişen tahmin demektir.",
        "**Kesikli çizgi** — gerçek anakütle ortalaması μ = 40. Histogramın merkezi bu çizginin neresinde?",
    ),
    build=_build_representation,
    metrics=_representation_metrics,
    takeaway=_representation_takeaway,
)


KONU01_EXPERIMENTS = (ORDINAL_CODES, DESIGN, REPRESENTATION)
