"""Konu 3 Sezgi deneyleri: veri üretim süreci bilinen kontrollü simülasyonlar.

Deney 1  Sınıf genişliği histogramı nasıl değiştirir?   (Notlar §3.8)
Deney 2  Dağılımın biçimi: simetrik mi, çarpık mı?       (Notlar §3.9)
Deney 3  Kümülatif yüzde: kaçı eşiğin altında?           (Notlar §3.10)
"""

from __future__ import annotations

from core.labs import expr as E
from core.labs.runner import LabState
from core.labs.sezgi import Parameters, SimExperiment, SimMetric, SimParameter, number, percent, plain
from core.labs.spec import (
    ClassHistogram,
    ClassTable,
    Derive,
    Draw,
    DrawCategory,
    LineChart,
    MapCodes,
    NewSample,
    NoteRef,
    Scalar,
    Statistic,
)

SEED = 217
TOPIC = "konu03"
AXIS = "Ulaşım süresi (dakika)"


def _without_total(table):
    return table.drop(index="Toplam", errors="ignore")


def _peak_count(counts) -> int:
    """Histogramdaki tepe sayısı: iki komşusundan da yüksek olan (eşit yükseklikteki bitişik sınıflar
    tek tepe sayılır) sınıf grupları. Kenarların dışı 0 kabul edilir."""

    values = [0, *[int(value) for value in counts], 0]
    peaks, index = 0, 1
    while index < len(values) - 1:
        end = index
        while end + 1 < len(values) - 1 and values[end + 1] == values[index]:
            end += 1
        if values[index] > values[index - 1] and values[index] > values[end + 1]:
            peaks += 1
        index = end + 1
    return peaks


# --- Deney 1: sınıf genişliği ----------------------------------------------------------

NEAR_SHARE = 0.6
NEAR = (25, 5)
FAR = (50, 6)
"""Yakın oturanlar N(25, 5), uzak oturanlar N(50, 6): gerçek dağılımın iki tepesi vardır."""


def _build_width(parameters: Parameters) -> tuple:
    n, width = int(parameters["n"]), int(parameters["h"])
    far = E.var("uzak")
    near_time = E.add(NEAR[0], E.mul(NEAR[1], E.var("z")))
    far_time = E.add(FAR[0], E.mul(FAR[1], E.var("z")))
    time = E.add(E.mul(E.sub(1, far), near_time), E.mul(far, far_time))
    return (
        NewSample("ogrenci", n, SEED),
        DrawCategory("ogrenci", "bolge", ("Yakın", "Uzak"), (((), (NEAR_SHARE, round(1 - NEAR_SHARE, 4))),),
                     "Öğrencinin oturduğu bölge"),
        MapCodes("ogrenci", "bolge", "uzak", (("Yakın", 0), ("Uzak", 1)), "Uzak = 1, Yakın = 0"),
        Draw("ogrenci", "z", "normal", 0, 1, "Standart normal çekiliş"),
        Derive("ogrenci", "sure", E.maximum(E.rounded(time), 1), "Ulaşım süresi: tam dakikaya yuvarlanır"),
        ClassTable("ogrenci", "sure", "siniflar", width, ("frekans", "yuzde")),
        ClassHistogram("siniflar", "frekans", AXIS, "Frekans", f"Sınıf genişliği {width} dakika"),
    )


def _width_dgp(parameters: Parameters) -> tuple[str, ...]:
    return (
        rf"P(\text{{Yakın}}) = {number(NEAR_SHARE, 1)}: \quad X \sim N({NEAR[0]},\ {NEAR[1]}^2)",
        rf"P(\text{{Uzak}}) = {number(1 - NEAR_SHARE, 1)}: \quad X \sim N({FAR[0]},\ {FAR[1]}^2)",
        rf"h = {int(parameters['h'])} \text{{ dakika}}, \qquad n = {int(parameters['n'])}",
    )


def _width_metrics(state: LabState, parameters: Parameters) -> tuple[SimMetric, ...]:
    table = _without_total(state.tables["siniflar"])
    busiest = str(table["frekans"].idxmax())
    return (
        SimMetric("Sınıf sayısı", f"{len(table)}", "En küçük ve en büyük değeri kapsayan h genişliğinde sınıflar."),
        SimMetric("En yoğun sınıf", busiest, "Frekansı en yüksek sınıf."),
        SimMetric("Histogramdaki tepe", f"{_peak_count(table['frekans'])}",
                  "İki komşusundan da yüksek dikdörtgen grubu sayısı."),
        SimMetric("Gerçek dağılımda tepe", "2", "DGP: yakın ve uzak oturanların iki ayrı yoğunlaşması."),
    )


def _width_takeaway(state: LabState, parameters: Parameters) -> str:
    peaks = _peak_count(_without_total(state.tables["siniflar"])["frekans"])
    width = int(parameters["h"])
    if peaks == 2:
        text = (f"{width} dakikalık sınıflarla gerçek dağılımdaki iki yoğunlaşma (yaklaşık 25 ve 50 dakika) "
                "görünüyor.")
    elif peaks < 2:
        text = (f"{width} dakikalık sınıflar iki grubu birleştiriyor: histogram tek tepeli görünüyor, oysa "
                "veriyi üreten süreçte iki yoğunlaşma var.")
    else:
        text = (f"{width} dakikalık sınıflarda {peaks} tepe var; gerçek dağılımda iki tepe vardır. Fazlası dar "
                "sınıflardaki rastgele dalgalanmadır; öğrenci sayısını artırın, dalgalanma azalır.")
    return text + " Sınıf genişliği yorumun parçasıdır; histogramı okumadan önce kontrol edilir (§3.8)."


CLASS_WIDTH = SimExperiment(
    topic_key=TOPIC,
    number=1,
    title="Sınıf genişliği histogramı nasıl değiştirir?",
    question="Aynı veri farklı sınıf genişlikleriyle özetlenince histogram dağılımın gerçek biçimini gösterir mi?",
    note=NoteRef("3.8", objects=("Şekil 3.8",)),
    parameters=(
        SimParameter("h", "Sınıf genişliği h (dakika)", 2, 20, 10, 1,
                     "Notlarda 5, 10 ve 20 dakika karşılaştırılır.", integer=True, decimals=0),
        SimParameter("n", "Öğrenci sayısı", 50, 2000, 400, 50,
                     "Ulaşım süresi ölçülen öğrenci sayısı.", integer=True, decimals=0),
    ),
    dgp=_width_dgp,
    dgp_note=(
        "Öğrencilerin %60'ı kampüse yakın, %40'ı uzak oturur; iki grubun ulaşım süreleri farklı merkezlerde "
        "toplanır. Süreler tam dakikaya yuvarlanır. İlk sınıf en kısa süreyi içeren h katından başlar."
    ),
    look_at=(
        "**Histogram** — dar sınıflar rastgele dalgalanmaları da tepe gibi gösterir; geniş sınıflar iki "
        "yoğunlaşmayı tek tepede birleştirebilir.",
        "**Tepe sayısı** — histogramda görünen tepeleri gerçek dağılımdaki iki tepeyle karşılaştırın.",
    ),
    build=_build_width,
    metrics=_width_metrics,
    takeaway=_width_takeaway,
    tables=(("siniflar", "Sınıflara göre frekans ve yüzde"),),
    labels=(("bolge", "Bölge"), ("sure", AXIS)),
)


# --- Deney 2: dağılım biçimi ------------------------------------------------------------

def _shape_parameters(parameters: Parameters) -> tuple[float, float]:
    """Beta(a, b): a = 5 + 3s, b = 5 − 3s. s < 0 sağa çarpık, s > 0 sola çarpık, s = 0 simetrik."""

    shift = round(float(parameters["s"]), 2)
    return round(5 + 3 * shift, 4), round(5 - 3 * shift, 4)


def _build_shape(parameters: Parameters) -> tuple:
    a, b = _shape_parameters(parameters)
    return (
        NewSample("ogrenci", int(parameters["n"]), SEED),
        Draw("ogrenci", "oran", "beta", a, b, "Beta dağılımından 0 ile 1 arasında bir oran"),
        Derive("ogrenci", "puan", E.mul(100, E.var("oran")), "Sınav puanı (0–100)"),
        ClassTable("ogrenci", "puan", "siniflar", 10, ("frekans", "yuzde"), lower=0, classes=10),
        ClassHistogram("siniflar", "yuzde", "Sınav puanı", "Öğrencilerin yüzdesi", "Sınav puanlarının dağılımı",
                       labels=True, percent=True, decimals=1),
    )


def _shape_dgp(parameters: Parameters) -> tuple[str, ...]:
    a, b = _shape_parameters(parameters)
    return (
        r"\text{Puan} = 100 \times B, \qquad B \sim \text{Beta}(a,\ b)",
        rf"a = 5 + 3s = {number(a, 1)}, \qquad b = 5 - 3s = {number(b, 1)}, \qquad n = {int(parameters['n'])}",
    )


def _tails(state: LabState) -> tuple[str, float, float]:
    table = _without_total(state.tables["siniflar"])
    scores = state.frames["ogrenci"]["puan"]
    busiest = table["frekans"].idxmax()
    middle = (table.loc[busiest, "alt"] + table.loc[busiest, "ust"]) / 2
    return str(busiest), float(middle - scores.min()), float(scores.max() - middle)


def _direction(parameters: Parameters) -> str:
    shift = round(float(parameters["s"]), 2)
    if shift < 0:
        return "Sağa"
    if shift > 0:
        return "Sola"
    return "Yok"


def _shape_metrics(state: LabState, parameters: Parameters) -> tuple[SimMetric, ...]:
    busiest, left, right = _tails(state)
    return (
        SimMetric("En yoğun sınıf", busiest, "Yüzdesi en yüksek puan sınıfı."),
        SimMetric("Sol kuyruk", f"{plain(left, 1)} puan",
                  "En yoğun sınıfın orta noktası ile en düşük puan arasındaki uzaklık."),
        SimMetric("Sağ kuyruk", f"{plain(right, 1)} puan",
                  "En yüksek puan ile en yoğun sınıfın orta noktası arasındaki uzaklık."),
        SimMetric("Çarpıklık (DGP)", _direction(parameters), "s < 0 sağa, s > 0 sola çarpık; s = 0 simetrik."),
    )


def _shape_takeaway(state: LabState, parameters: Parameters) -> str:
    busiest, left, right = _tails(state)
    if right > 1.3 * left:
        text = (f"Puanların çoğu {busiest} civarında; uzun ve seyrekleşen kuyruk yüksek puanlara uzanıyor: "
                "dağılım sağa çarpık (zor bir sınav).")
    elif left > 1.3 * right:
        text = (f"Puanların çoğu {busiest} civarında; uzun kuyruk düşük puanlara uzanıyor: dağılım sola "
                "çarpık (kolay bir sınav).")
    else:
        text = "İki kuyruk benzer uzunlukta: dağılım yaklaşık simetrik."
    return text + (" Çarpıklığın yönü gözlemlerin çoğunun bulunduğu tarafa göre değil, kuyruğun uzandığı yöne "
                   "göre adlandırılır (§3.9).")


DISTRIBUTION_SHAPE = SimExperiment(
    topic_key=TOPIC,
    number=2,
    title="Dağılımın biçimi: simetrik mi, çarpık mı?",
    question="Sınavın zorluğu değişince puan histogramının biçimi nasıl değişir ve çarpıklığın yönü nasıl okunur?",
    note=NoteRef("3.9", objects=("Şekil 3.9",)),
    parameters=(
        SimParameter("s", "Sınavın kolaylığı s", -1.0, 1.0, -0.6, 0.1,
                     "−1: çok zor sınav, 0: dengeli, 1: çok kolay sınav.", decimals=1),
        SimParameter("n", "Öğrenci sayısı", 100, 5000, 1000, 100,
                     "Sınava giren öğrenci sayısı.", integer=True, decimals=0),
    ),
    dgp=_shape_dgp,
    dgp_note=(
        "Beta dağılımı 0 ile 1 arasında değer üretir; puan 0–100 aralığındadır. a < b iken puanlar düşük "
        "bölgede yoğunlaşır, a > b iken yüksek bölgede; a = b iken dağılım simetriktir."
    ),
    look_at=(
        "**Histogram** — puanların yoğunlaştığı sınıf ve seyrekleşen uzun kuyruğun yönü.",
        "**Kuyruk uzunlukları** — en yoğun sınıftan en düşük ve en yüksek puana olan uzaklıklar.",
    ),
    build=_build_shape,
    metrics=_shape_metrics,
    takeaway=_shape_takeaway,
    tables=(("siniflar", "Puan sınıflarına göre frekans ve yüzde"),),
    labels=(("puan", "Sınav puanı"),),
)


# --- Deney 3: kümülatif yüzde ------------------------------------------------------------

MEAN, SD, FLOOR = 35, 12, 5
"""Ulaşım süresi N(35, 12²); 5 dakikadan kısa değerler 5 dakika sayılır."""


def _build_cumulative(parameters: Parameters) -> tuple:
    threshold = int(parameters["t"])
    return (
        NewSample("ogrenci", int(parameters["n"]), SEED),
        Draw("ogrenci", "z", "normal", 0, 1, "Standart normal çekiliş"),
        Derive("ogrenci", "sure", E.maximum(E.add(MEAN, E.mul(SD, E.var("z"))), FLOOR), "Ulaşım süresi (dakika)"),
        Derive("ogrenci", "esik_alti", E.compare("lt", E.var("sure"), threshold), f"{threshold} dakikadan kısa mı?"),
        Statistic("ogrenci", "esik_alti", "mean", "pay", "Eşiğin altındaki pay", decimals=3),
        Scalar("orneklem_yuzde", E.mul(100, E.ref("pay")), "Örneklemde eşiğin altındaki yüzde", decimals=1,
               percent=True),
        Scalar("dgp_yuzde", E.mul(100, E.normcdf(E.div(E.sub(threshold, MEAN), SD))),
               "DGP'de eşiğin altındaki yüzde", decimals=1, percent=True),
        ClassTable("ogrenci", "sure", "kumulatif", 10, ("kumulatif_frekans", "kumulatif_yuzde"), lower=0,
                   classes=10, row_labels="ust"),
        LineChart("kumulatif", "ust", "kumulatif_yuzde", "Üst sınır (dakika)", "Kümülatif yüzde",
                  "Kümülatif yüzde eğrisi"),
    )


def _cumulative_dgp(parameters: Parameters) -> tuple[str, ...]:
    return (
        rf"X = \max(Z,\ {FLOOR}), \qquad Z \sim N({MEAN},\ {SD}^2)",
        rf"P(X < t) = \Phi\!\left(\frac{{t - {MEAN}}}{{{SD}}}\right), \qquad t = {int(parameters['t'])}, \qquad "
        rf"n = {int(parameters['n'])}",
    )


def _cumulative_metrics(state: LabState, parameters: Parameters) -> tuple[SimMetric, ...]:
    sample, truth = state.scalars["orneklem_yuzde"], state.scalars["dgp_yuzde"]
    threshold = int(parameters["t"])
    return (
        SimMetric(f"Örneklemde < {threshold} dk", percent(sample),
                  "Örneklemde eşikten kısa ulaşım süresine sahip öğrencilerin yüzdesi."),
        SimMetric(f"DGP'de < {threshold} dk", percent(truth), "Veriyi üreten süreçte bu olasılık: Φ((t − 35)/12)."),
        SimMetric("Fark", f"{plain(sample - truth, 1)} puan", "Örneklem yüzdesi − DGP yüzdesi."),
    )


def _cumulative_takeaway(state: LabState, parameters: Parameters) -> str:
    gap = abs(state.scalars["orneklem_yuzde"] - state.scalars["dgp_yuzde"])
    n = int(parameters["n"])
    text = (f"Kümülatif yüzde \"{int(parameters['t'])} dakikadan kısa kaç öğrenci?\" sorusunu doğrudan "
            "cevaplar; eğri hiçbir zaman azalmaz ve son noktada %100'e ulaşır. ")
    if gap > 5:
        text += (f"n = {n} öğrencilik örneklemde yüzde, veriyi üreten süreçteki değerden {plain(gap, 1)} puan "
                 "uzakta: küçük örneklemde kümülatif yüzdeler rastgele dalgalanır.")
    else:
        text += (f"n = {n} öğrencide örneklem yüzdesi süreçteki değere yakın (fark {plain(gap, 1)} puan). "
                 "Öğrenci sayısını değiştirin: örneklem küçüldükçe fark genellikle büyür, büyüdükçe küçülür.")
    return text + " Sonuç yalnız gözlenen öğrencileri betimler (§3.10)."


CUMULATIVE_SHARE = SimExperiment(
    topic_key=TOPIC,
    number=3,
    title="Kümülatif yüzde: kaçı eşiğin altında?",
    question="\"Öğrencilerin yüzde kaçı t dakikadan kısa sürede kampüse ulaşıyor?\" sorusunu kümülatif dağılım nasıl "
             "cevaplar ve örneklem büyüklüğü cevabı nasıl etkiler?",
    note=NoteRef("3.10", objects=("Tablo 3.4",)),
    parameters=(
        SimParameter("t", "Eşik t (dakika)", 10, 70, 40, 5, "\"t dakikadan az\" sorusunun eşiği.",
                     integer=True, decimals=0),
        SimParameter("n", "Öğrenci sayısı", 20, 2000, 40, 20,
                     "Notlardaki örnekte 40 öğrenci vardır.", integer=True, decimals=0),
    ),
    dgp=_cumulative_dgp,
    dgp_note=(f"Ulaşım süreleri ortalaması {MEAN}, standart sapması {SD} dakika olan normal dağılımdan çekilir; "
              f"{FLOOR} dakikadan kısa çekilişler {FLOOR} dakika sayılır. Bu yüzden formül t > {FLOOR} için "
              "geçerlidir (kaydırıcı en az 10'dur)."),
    look_at=(
        "**Kümülatif yüzde eğrisi** — her üst sınırın altında kalan öğrencilerin yüzdesi.",
        "**Örneklem ve DGP** — eşiğin altındaki yüzde; küçük örneklemde fark büyüyebilir.",
    ),
    build=_build_cumulative,
    metrics=_cumulative_metrics,
    takeaway=_cumulative_takeaway,
    tables=(("kumulatif", "Kümülatif dağılım"),),
    labels=(("sure", AXIS),),
)


KONU03_EXPERIMENTS = (CLASS_WIDTH, DISTRIBUTION_SHAPE, CUMULATIVE_SHARE)
