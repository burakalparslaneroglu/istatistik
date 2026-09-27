"""Konu 6 Sezgi deneyleri: veri üretim süreci bilinen kontrollü simülasyonlar.

Deney 1  Göreli frekans: oran olasılığa yaklaşır mı?          (Notlar §6.5, Şekil 6.6)
Deney 2  İki zar: klasik olasılık ve simülasyon                 (Notlar §6.2, §6.5)
Deney 3  Toplama kuralı: ortak kısım neden çıkarılır?            (Notlar §6.9)

Deney 1'in varsayılan ayarları (p = 0,15, n = 100, tohum 217) notlardaki Şekil 6.6'yı birebir üretir.
"""

from __future__ import annotations

from core.labs import expr as E
from core.labs.runner import LabState
from core.labs.sezgi import Parameters, SimExperiment, SimMetric, SimParameter, number, percent, plain
from core.labs.spec import (
    Derive,
    Draw,
    DrawCategory,
    Event,
    FrequencyTable,
    GroupedBarChart,
    JoinColumns,
    LineChart,
    NewSample,
    NoteRef,
    Outcomes,
    Scalar,
    ScalarTable,
    Statistic,
)

SEED = 217
TOPIC = "konu06"


# --- Deney 1: göreli frekans ------------------------------------------------------------------

CHECKPOINTS = (10, 100, 1000)


def _build_frequency(parameters: Parameters) -> tuple:
    n, p = int(parameters["n"]), round(float(parameters["p"]), 2)
    return (
        NewSample("islem", n, SEED),
        Draw("islem", "u", "uniform", 0, 1, "u ~ Tekdüze(0, 1)"),
        Derive("islem", "gecikme", E.compare("lt", E.var("u"), p), "Gecikme: u < p ise 1, değilse 0"),
        Derive("islem", "k", E.seq(E.var("u")), "İşlem sırası k = 1, 2, …, n"),
        Derive("islem", "oran", E.cummean(E.var("gecikme")), "Birikimli gecikme oranı: ilk k işlemdeki gecikme / k"),
        Statistic("islem", "gecikme", "sum", "gecikme_sayisi", "Gecikme sayısı", decimals=0),
        Statistic("islem", "gecikme", "mean", "son_oran", "n işlemdeki gecikme oranı", decimals=4),
        Scalar("p", E.const(p), "Gerçek gecikme olasılığı p", decimals=2),
        LineChart("islem", "k", "oran", "Gözlenen işlem sayısı", "Gecikme göreli frekansı",
                  "Birikimli gecikme oranı ve gerçek olasılık", references=(("p", "Gerçek olasılık p"),),
                  markers=False),
    )


def _frequency_dgp(parameters: Parameters) -> tuple[str, ...]:
    n, p = int(parameters["n"]), round(float(parameters["p"]), 2)
    return (
        rf"G_k = \begin{{cases}} 1 & u_k < p \\ 0 & \text{{aksi hâlde}} \end{{cases}}, \qquad "
        rf"u_k \sim \text{{Tekdüze}}(0,\ 1), \qquad p = {number(p, 2)}, \qquad n = {n}",
        r"\hat{p}_k = \frac{G_1 + G_2 + \cdots + G_k}{k} \qquad \text{(ilk } k \text{ işlemdeki gecikme oranı)}",
    )


def _ratio_at(state: LabState, k: int) -> float | None:
    ratios = state.frames["islem"]["oran"]
    return float(ratios.iloc[k - 1]) if k <= len(ratios) else None


def _frequency_metrics(state: LabState, parameters: Parameters) -> tuple[SimMetric, ...]:
    n, p = int(parameters["n"]), round(float(parameters["p"]), 2)
    items = []
    for k in CHECKPOINTS:
        value = _ratio_at(state, k)
        if value is not None and k < n:
            items.append(SimMetric(f"İlk {k} işlemde oran", plain(value, 3), f"p = {plain(p, 2)} ile karşılaştırın."))
    items.append(SimMetric(f"{n} işlemde oran", plain(state.scalars["son_oran"], 3),
                           f"{int(state.scalars['gecikme_sayisi'])} gecikme / {n} işlem."))
    items.append(SimMetric("|oran − p|", plain(abs(state.scalars["son_oran"] - p), 3),
                           "Son oranın gerçek olasılıktan uzaklığı."))
    return tuple(items)


def _frequency_takeaway(state: LabState, parameters: Parameters) -> str:
    n, p = int(parameters["n"]), round(float(parameters["p"]), 2)
    final = state.scalars["son_oran"]
    early = _ratio_at(state, min(10, n))
    text = (
        f"İlk {min(10, n)} işlemde oran {plain(early, 3)}, {n} işlemde {plain(final, 3)}; gerçek olasılık "
        f"{plain(p, 2)}. Az gözlemde oran belirgin biçimde oynar; gözlem arttıkça p çevresinde daha dar bir bantta "
        "kalır. Göreli frekans yöntemi olasılığı bu uzun dönem oranıyla tahmin eder (§6.5). "
    )
    if n == 100 and p == 0.15:
        text += ("Bu ayarlar notlardaki Şekil 6.6'nın veri üretim sürecidir: ilk dokuz işlemde gecikme yok, son oran "
                 "16/100 = 0,16.")
    else:
        text += "Varsayılan ayarlar (p = 0,15, n = 100) notlardaki Şekil 6.6'yı üretir."
    return text


RELATIVE_FREQUENCY = SimExperiment(
    topic_key=TOPIC,
    number=1,
    title="Göreli frekans: oran olasılığa yaklaşır mı?",
    question="Her işlemin p olasılıkla geciktiği bir süreçte, gözlenen gecikme oranı işlem sayısı arttıkça nasıl "
             "davranır?",
    note=NoteRef("6.5", objects=("Şekil 6.6",)),
    parameters=(
        SimParameter("p", "Gecikme olasılığı p", 0.05, 0.95, 0.15, 0.05, "Notlardaki örnekte p = 0,15.",
                     decimals=2),
        SimParameter("n", "İşlem sayısı n", 20, 2000, 100, 10, "Notlardaki Şekil 6.6'da n = 100.", integer=True,
                     decimals=0),
    ),
    dgp=_frequency_dgp,
    dgp_note=(
        "Her işlem birbirinden bağımsız olarak p olasılıkla gecikir: u ~ Tekdüze(0, 1) çekilir, u < p ise işlem "
        "gecikmiştir. Tohum 217'dir; p = 0,15 ve n = 100 notlardaki Şekil 6.6'yı birebir üretir."
    ),
    look_at=(
        "**Çizgi grafiği** — birikimli oranın ilk işlemlerdeki dalgalanması ve p çevresine yerleşmesi.",
        "**Kontrol noktaları** — ilk 10, 100 ve 1000 işlemdeki oran.",
    ),
    build=_build_frequency,
    metrics=_frequency_metrics,
    takeaway=_frequency_takeaway,
    labels=(("k", "Gözlenen işlem sayısı"), ("oran", "Gecikme göreli frekansı")),
)


# --- Deney 2: iki zar ---------------------------------------------------------------------------

DIE = (1, 2, 3, 4, 5, 6)
SUMS = tuple(range(2, 13))


def _build_dice(parameters: Parameters) -> tuple:
    n = int(parameters["n"])
    face = "Zar: ⌊6u⌋ + 1 (1, …, 6 eşit olasılıklı)"
    return (
        Outcomes("iki_zar", (("birinci", DIE), ("ikinci", DIE)), "Klasik yöntem: 36 eşit olasılıklı zar çifti"),
        Derive("iki_zar", "toplam", E.add(E.var("birinci"), E.var("ikinci")), "Zar çiftinin toplamı"),
        FrequencyTable("iki_zar", "toplam", "klasik", SUMS),
        NewSample("atis", n, SEED),
        Draw("atis", "u1", "uniform", 0, 1, "Birinci zar için u ~ Tekdüze(0, 1)"),
        Draw("atis", "u2", "uniform", 0, 1, "İkinci zar için u ~ Tekdüze(0, 1)"),
        Derive("atis", "birinci", E.add(E.floor(E.mul(6, E.var("u1"))), 1), face),
        Derive("atis", "ikinci", E.add(E.floor(E.mul(6, E.var("u2"))), 1), face),
        Derive("atis", "toplam", E.add(E.var("birinci"), E.var("ikinci")), "Atılan iki zarın toplamı"),
        FrequencyTable("atis", "toplam", "simulasyon", SUMS),
        JoinColumns("karsilastirma", (("Klasik olasılık", "klasik", "goreli"),
                                      ("Simülasyon oranı", "simulasyon", "goreli")), decimals=3),
        GroupedBarChart("karsilastirma", "İki zarın toplamı", "Olasılık / göreli frekans",
                        "Klasik olasılık ve simülasyondaki oran", series="sutun", decimals=3, labels=False),
    )


def _dice_dgp(parameters: Parameters) -> tuple[str, ...]:
    n = int(parameters["n"])
    return (
        rf"Z_j = \lfloor 6u_j \rfloor + 1, \qquad u_j \sim \text{{Tekdüze}}(0,\ 1), \qquad "
        rf"T = Z_1 + Z_2, \qquad n = {n} \text{{ atış}}",
        r"P(T = t) = \frac{\text{toplamı } t \text{ olan zar çifti sayısı}}{36}",
    )


def _dice_metrics(state: LabState, parameters: Parameters) -> tuple[SimMetric, ...]:
    table = state.tables["karsilastirma"]
    gaps = (table["Simülasyon oranı"] - table["Klasik olasılık"]).abs()
    return (
        SimMetric("P(toplam 7)", plain(table.loc[7, "Klasik olasılık"], 3), "Klasik yöntem: 6/36."),
        SimMetric("Simülasyonda toplam 7", plain(table.loc[7, "Simülasyon oranı"], 3), "Atışlardaki göreli frekans."),
        SimMetric("P(toplam 2)", plain(table.loc[2, "Klasik olasılık"], 3), "Klasik yöntem: 1/36."),
        SimMetric("En büyük fark", plain(float(gaps.max()), 3),
                  "11 toplam içinde |oran − olasılık| farkının en büyüğü."),
    )


def _dice_takeaway(state: LabState, parameters: Parameters) -> str:
    n = int(parameters["n"])
    table = state.tables["karsilastirma"]
    gap = float((table["Simülasyon oranı"] - table["Klasik olasılık"]).abs().max())
    return (
        f"{n} atışta oranlar klasik olasılıklardan en çok {plain(gap, 3)} uzaklaşıyor. 11 toplam eşit olasılıklı "
        "değildir: 7 en sık (6/36), 2 ve 12 en seyrek (1/36) görülür. Klasik yöntemde olasılık eşit olasılıklı zar "
        "çiftleri sayılarak bulunur; simülasyondaki oran bu olasılığın göreli frekans tahminidir ve atış arttıkça ona "
        "yaklaşır (§6.2, §6.5)."
    )


TWO_DICE = SimExperiment(
    topic_key=TOPIC,
    number=2,
    title="İki zar: klasik olasılık ve simülasyon",
    question="İki zarın toplamı için sayarak bulunan olasılıklar, zarları gerçekten atınca gözlenen oranlarla "
             "uyuşur mu?",
    note=NoteRef("6.2", objects=("Şekil 6.2",)),
    parameters=(
        SimParameter("n", "Atış sayısı n", 36, 7200, 360, 36, "Her atışta iki zar birlikte atılır.", integer=True,
                     decimals=0),
    ),
    dgp=_dice_dgp,
    dgp_note=(
        "İki zar adil ve birbirinden bağımsızdır: her yüz 1/6 olasılıklıdır. Klasik olasılıklar 36 zar çiftinden "
        "sayılır; simülasyon aynı zarları n kez atar."
    ),
    look_at=(
        "**Sütun grafiği** — her toplam için klasik olasılık ve simülasyondaki oran yan yana.",
        "**Tablo** — 11 toplamın olasılıkları ve oranları.",
    ),
    build=_build_dice,
    metrics=_dice_metrics,
    takeaway=_dice_takeaway,
    tables=(("karsilastirma", "Klasik olasılık ve simülasyon oranı"),),
    labels=(("toplam", "İki zarın toplamı"),),
)


# --- Deney 3: toplama kuralı --------------------------------------------------------------------

JOINT = ("A ve B", "Yalnız A", "Yalnız B", "Hiçbiri")


def _feasible(parameters: Parameters) -> tuple[float, float, float]:
    """P(A ∩ B), max(0, P(A) + P(B) − 1) ile min(P(A), P(B)) arasında olmak zorundadır; dışındaysa sınıra çekilir."""

    pa, pb, pab = (round(float(parameters[key]), 2) for key in ("pA", "pB", "pAB"))
    low, high = max(0.0, pa + pb - 1), min(pa, pb)
    return pa, pb, round(min(max(pab, low), high), 10)


def _build_addition(parameters: Parameters) -> tuple:
    n = int(parameters["n"])
    pa, pb, pab = _feasible(parameters)
    probabilities = tuple(round(value, 10) for value in (pab, pa - pab, pb - pab, 1 - pa - pb + pab))
    return (
        NewSample("kisi", n, SEED),
        DrawCategory("kisi", "durum", JOINT, (((), probabilities),), "Her kişi dört ortak sonuçtan birine düşer"),
        Event("kisi", "A", "durum", ("A ve B", "Yalnız A"), "A olayı"),
        Event("kisi", "B", "durum", ("A ve B", "Yalnız B"), "B olayı"),
        Derive("kisi", "A_ve_B", E.mul(E.var("A"), E.var("B")), "A ∩ B: ikisi birden"),
        Derive("kisi", "A_veya_B", E.maximum(E.var("A"), E.var("B")), "A ∪ B: en az biri"),
        Statistic("kisi", "A", "mean", "oran_A", "A'nın oranı", decimals=3),
        Statistic("kisi", "B", "mean", "oran_B", "B'nin oranı", decimals=3),
        Statistic("kisi", "A_ve_B", "mean", "oran_AB", "A ∩ B'nin oranı", decimals=3),
        Statistic("kisi", "A_veya_B", "mean", "oran_birlesim", "A ∪ B'nin oranı: doğrudan sayım", decimals=3),
        Scalar("kural", E.sub(E.add(E.ref("oran_A"), E.ref("oran_B")), E.ref("oran_AB")),
               "Toplama kuralı: A + B − A ∩ B oranları", decimals=3),
        Scalar("cift_sayim", E.add(E.ref("oran_A"), E.ref("oran_B")), "Yanlış hesap: A + B oranları", decimals=3),
        ScalarTable(
            (
                ("P(A ∪ B): toplama kuralıyla (DGP)", E.const(round(pa + pb - pab, 10))),
                ("A ∪ B oranı: doğrudan sayım", E.ref("oran_birlesim")),
                ("A + B − A ∩ B oranları", E.ref("kural")),
                ("A + B oranları (ortak kısım iki kez)", E.ref("cift_sayim")),
            ),
            "birlesim",
            decimals=3,
        ),
    )


def _addition_dgp(parameters: Parameters) -> tuple[str, ...]:
    n = int(parameters["n"])
    pa, pb, pab = _feasible(parameters)
    return (
        rf"P(A) = {number(pa, 2)}, \qquad P(B) = {number(pb, 2)}, \qquad P(A \cap B) = {number(pab, 2)}, "
        rf"\qquad n = {n}",
        rf"P(A \cup B) = P(A) + P(B) - P(A \cap B) = {number(pa + pb - pab, 2)}",
    )


def _addition_metrics(state: LabState, parameters: Parameters) -> tuple[SimMetric, ...]:
    s = state.scalars
    pa, pb, pab = _feasible(parameters)
    return (
        SimMetric("A ∪ B: doğrudan sayım", percent(100 * s["oran_birlesim"], 1), "En az birine sahip kişilerin oranı."),
        SimMetric("Toplama kuralıyla", percent(100 * s["kural"], 1),
                  "A, B ve A ∩ B oranlarından: A + B − A ∩ B. Doğrudan sayımla her zaman aynıdır."),
        SimMetric("A + B (yanlış)", percent(100 * s["cift_sayim"], 1), "Ortak kısım iki kez sayılır."),
        SimMetric("DGP: P(A ∪ B)", percent(100 * (pa + pb - pab), 1), "Toplama kuralıyla gerçek olasılık."),
    )


def _addition_takeaway(state: LabState, parameters: Parameters) -> str:
    s = state.scalars
    pa, pb, pab = _feasible(parameters)
    clamp = abs(pab - round(float(parameters["pAB"]), 2)) > 1e-9
    text = ""
    if clamp:
        text = (f"Seçilen P(A ∩ B) olanaksızdı; en yakın geçerli değer kullanıldı: P(A ∩ B) = {plain(pab, 2)}. Kesişim "
                "ne P(A)'dan ne P(B)'den büyük olabilir, ne de P(A) + P(B) − 1'den küçük. ")
    if pab == 0:
        return text + (
            "P(A ∩ B) = 0: A ve B ayrık olaylardır; toplama kuralı P(A ∪ B) = P(A) + P(B)'ye sadeleşir ve A + B "
            "hesabı da doğru sonuç verir. Ayrık olmak bağımsız olmak demek değildir (§6.9)."
        )
    return text + (
        f"Doğrudan sayılan A ∪ B oranı {plain(s['oran_birlesim'], 3)}; A + B − A ∩ B de aynı sayıyı verir, çünkü "
        f"her kişi tam bir kez sayılır. A + B ise {plain(s['cift_sayim'], 3)}: ortak kısım (yaklaşık "
        f"{plain(pab, 2)}) iki kez sayılmıştır. Toplama kuralı bu çift saymayı düzeltir (§6.9)."
    )


ADDITION_RULE = SimExperiment(
    topic_key=TOPIC,
    number=3,
    title="Toplama kuralı: ortak kısım neden çıkarılır?",
    question="P(A) ile P(B)'yi toplamak \"A veya B\" olasılığını neden fazla verir ve toplama kuralı bunu nasıl "
             "düzeltir?",
    note=NoteRef("6.9", objects=("Şekil 6.10",)),
    parameters=(
        SimParameter("pA", "P(A)", 0.05, 0.95, 0.40, 0.05, "Notlardaki örnekte ileri Excel: 0,40.", decimals=2),
        SimParameter("pB", "P(B)", 0.05, 0.95, 0.35, 0.05, "Notlardaki örnekte Python: 0,35.", decimals=2),
        SimParameter("pAB", "P(A ∩ B)", 0.0, 0.95, 0.15, 0.05,
                     "Notlardaki örnekte ikisi birden: 0,15. Olanaksız değer en yakın geçerli değere çekilir.",
                     decimals=2),
        SimParameter("n", "Kişi sayısı n", 100, 10000, 1000, 100, "Rastgele seçilen kişi sayısı.", integer=True,
                     decimals=0),
    ),
    dgp=_addition_dgp,
    dgp_note=(
        "Her kişi dört ortak sonuçtan birine düşer: A ve B, yalnız A, yalnız B, hiçbiri. Olasılıkları P(A ∩ B), "
        "P(A) − P(A ∩ B), P(B) − P(A ∩ B) ve 1 − P(A) − P(B) + P(A ∩ B)'dir."
    ),
    look_at=(
        "**Birleşim tablosu** — doğrudan sayım, toplama kuralı ve yanlış A + B hesabı.",
        "**Metrikler** — sayımla bulunan oran ile toplama kuralının her örneklemde aynı sayıyı vermesi.",
    ),
    build=_build_addition,
    metrics=_addition_metrics,
    takeaway=_addition_takeaway,
    tables=(("birlesim", "A ∪ B: üç hesap"),),
)


KONU06_EXPERIMENTS = (RELATIVE_FREQUENCY, TWO_DICE, ADDITION_RULE)
