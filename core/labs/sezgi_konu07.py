"""Konu 7 Sezgi deneyleri: veri üretim süreci bilinen kontrollü simülasyonlar.

Deney 1  Koşulun yönü: P(S | M) ile P(M | S)                    (Notlar §7.4, Şekil 7.4)
Deney 2  Bağımsızlık: koşul oranı değiştiriyor mu?               (Notlar §7.5, Şekil 7.5)
Deney 3  Temel oran: alarm ne kadar güvenilir?                   (Notlar §7.12, Tablo 7.5, Şekil 7.12)

Varsayılan ayarlar notlardaki örneklerin olasılıklarıdır (mağaza: 0,60, 0,30, 0,20; ekspres teslimat: 0,40;
alarm: 0,02, 0,90, 0,05). Örneklem sayıları rastgele çekiliş farkı kadar notlardaki sayılardan ayrılır.
"""

from __future__ import annotations

import math

from core.labs import expr as E
from core.labs.runner import LabState
from core.labs.sezgi import Parameters, SimExperiment, SimMetric, SimParameter, number, plain
from core.labs.spec import (
    BarChart,
    CrossTab,
    Derive,
    DrawCategory,
    Event,
    GroupedBarChart,
    LineChart,
    MosaicChart,
    NewSample,
    NoteRef,
    Outcomes,
    Scalar,
    ScalarTable,
    Statistic,
)

SEED = 217
TOPIC = "konu07"


def _share(value: float, decimals: int = 3) -> str:
    """Örneklem oranı; koşul grubu boşsa oran tanımsızdır."""

    return plain(value, decimals) if math.isfinite(value) else "tanımsız"


def _probability(parameters: Parameters, key: str) -> float:
    return round(float(parameters[key]), 3)


# --- Deney 1: koşulun yönü ---------------------------------------------------------------------

DEVICES = ("Mobil", "Masaüstü")
OUTCOMES = ("Satın aldı", "Satın almadı")


def _direction_truth(parameters: Parameters) -> tuple[float, float, float, float]:
    """DGP'den P(M), P(S | M), P(S) ve P(M | S) = P(M ∩ S)/P(S)."""

    pm, psm, psd = (_probability(parameters, key) for key in ("pM", "pSM", "pSD"))
    ps = pm * psm + (1 - pm) * psd
    return pm, psm, ps, pm * psm / ps


def _build_direction(parameters: Parameters) -> tuple:
    n = int(parameters["n"])
    pm, psm, psd = (_probability(parameters, key) for key in ("pM", "pSM", "pSD"))
    _, _, ps, pms = _direction_truth(parameters)
    return (
        NewSample("ziyaret", n, SEED),
        DrawCategory("ziyaret", "cihaz", DEVICES, (((), (pm, round(1 - pm, 10))),), "Cihaz: P(M) olasılıkla mobil"),
        DrawCategory(
            "ziyaret", "satin", OUTCOMES,
            ((("Mobil",), (psm, round(1 - psm, 10))), (("Masaüstü",), (psd, round(1 - psd, 10)))),
            "Satın alma: cihaz türüne göre koşullu olasılıkla", by=("cihaz",),
        ),
        CrossTab("ziyaret", "cihaz", "satin", "sayilar", DEVICES, OUTCOMES, margins=True, decimals=0),
        MosaicChart("sayilar", "Cihaz türü (sütun genişliği: ziyaretçi payı)", "Sütun içindeki pay",
                    "Örneklemde cihaz ve satın alma: mozaik"),
        Event("ziyaret", "S", "satin", ("Satın aldı",), "S: satın aldı"),
        Event("ziyaret", "M", "cihaz", ("Mobil",), "M: mobil"),
        Statistic("ziyaret", "S", "mean", "oran_S", "Satın alanların oranı", decimals=3),
        Statistic("ziyaret", "S", "mean", "oran_S_M", "Mobiller içinde satın alanların oranı", where=("M", 1),
                  decimals=3),
        Statistic("ziyaret", "M", "mean", "oran_M_S", "Satın alanlar içinde mobillerin oranı", where=("S", 1),
                  decimals=3),
        ScalarTable(
            (
                ("P(S | M): DGP", E.const(psm)),
                ("Mobiller içinde satın alan: örneklem", E.ref("oran_S_M")),
                ("P(M | S) = P(M ∩ S)/P(S): DGP", E.const(round(pms, 10))),
                ("Satın alanlar içinde mobil: örneklem", E.ref("oran_M_S")),
                ("P(S): DGP", E.const(round(ps, 10))),
                ("Satın alan: örneklem", E.ref("oran_S")),
            ),
            "yon",
            decimals=3,
        ),
    )


def _direction_dgp(parameters: Parameters) -> tuple[str, ...]:
    n = int(parameters["n"])
    pm, psm, psd = (_probability(parameters, key) for key in ("pM", "pSM", "pSD"))
    _, _, ps, pms = _direction_truth(parameters)
    return (
        rf"P(M) = {number(pm, 2)}, \qquad P(S \mid M) = {number(psm, 2)}, \qquad P(S \mid D) = {number(psd, 2)}, "
        rf"\qquad n = {n}",
        rf"P(S) = P(M)P(S \mid M) + P(D)P(S \mid D) = {number(ps, 3)}, \qquad "
        rf"P(M \mid S) = \frac{{P(M \cap S)}}{{P(S)}} = {number(pms, 3)}",
    )


def _direction_metrics(state: LabState, parameters: Parameters) -> tuple[SimMetric, ...]:
    s = state.scalars
    _, psm, ps, pms = _direction_truth(parameters)
    return (
        SimMetric("Mobiller içinde satın alan", _share(s["oran_S_M"]), f"DGP: P(S | M) = {plain(psm, 2)}."),
        SimMetric("Satın alanlar içinde mobil", _share(s["oran_M_S"]), f"DGP: P(M | S) = {plain(pms, 3)}."),
        SimMetric("Satın alan (tümü)", _share(s["oran_S"]), f"DGP: P(S) = {plain(ps, 3)}."),
    )


def _direction_takeaway(state: LabState, parameters: Parameters) -> str:
    s = state.scalars
    pm, psm, _, pms = _direction_truth(parameters)
    counts = state.tables["sayilar"]
    joint = int(counts.loc["Mobil", "Satın aldı"])
    text = (
        f"Aynı ortak hücre, mobil ve satın alan {joint} ziyaretçi, iki farklı paydaya bölünür: mobil ziyaretçilere "
        f"bölününce {_share(s['oran_S_M'])}, satın alanlara bölününce {_share(s['oran_M_S'])}. İlki P(S | M) = "
        f"{plain(psm, 2)}, ikincisi P(M | S) = {plain(pms, 3)} olasılığının tahminidir. Dikey çizginin sağındaki "
        "olay karşılaştırma grubunu belirler (§7.4). "
    )
    if math.isclose(psm, pms):
        text += ("Bu ayarlarda iki koşullu olasılık eşittir: P(S | M) = P(M ∩ S)/P(M) ile P(M | S) = P(M ∩ S)/P(S) "
                 "yalnız P(M) = P(S) olduğunda aynıdır.")
    elif (pm, psm, _probability(parameters, "pSD")) == (0.6, 0.3, 0.2):
        text += "Varsayılan ayarlar notlardaki mağazanın olasılıklarıdır: P(S | M) = 0,30, P(M | S) = 180/260 ≈ 0,692."
    return text


DIRECTION = SimExperiment(
    topic_key=TOPIC,
    number=1,
    title="Koşulun yönü: P(S | M) ile P(M | S)",
    question="Mobil ziyaretçilerin satın alma oranı ile satın alanlar içinde mobil ziyaretçilerin oranı aynı "
             "soruya mı cevap verir?",
    note=NoteRef("7.4", objects=("Şekil 7.4",)),
    parameters=(
        SimParameter("pM", "Mobil payı P(M)", 0.10, 0.90, 0.60, 0.05, "Notlardaki mağazada 600/1000 = 0,60.",
                     decimals=2),
        SimParameter("pSM", "Mobilde satın alma P(S | M)", 0.05, 0.95, 0.30, 0.05, "Notlarda 180/600 = 0,30.",
                     decimals=2),
        SimParameter("pSD", "Masaüstünde satın alma P(S | D)", 0.05, 0.95, 0.20, 0.05, "Notlarda 80/400 = 0,20.",
                     decimals=2),
        SimParameter("n", "Ziyaretçi sayısı n", 100, 20000, 1000, 100, "Notlardaki mağazada 1000 ziyaretçi.",
                     integer=True, decimals=0),
    ),
    dgp=_direction_dgp,
    dgp_note=(
        "Her ziyaretçi P(M) olasılıkla mobil, aksi hâlde masaüstü cihazdan gelir. Satın alma olasılığı cihaza "
        "bağlıdır: mobilde P(S | M), masaüstünde P(S | D). Tohum 217'dir; ziyaretçiler birbirinden bağımsızdır."
    ),
    look_at=(
        "**Mozaik** — sütun genişliği cihaz payı, sütun içindeki yükseklik o cihazda satın alma payı.",
        "**Yön tablosu** — aynı ortak hücrenin iki farklı paydaya bölünmesi: P(S | M) ve P(M | S).",
    ),
    build=_build_direction,
    metrics=_direction_metrics,
    takeaway=_direction_takeaway,
    tables=(("sayilar", "Örneklemdeki sayılar"), ("yon", "İki koşullu olasılık: DGP ve örneklem")),
    labels=(("cihaz", "Cihaz türü"), ("satin", "Satın alma durumu")),
)


# --- Deney 2: bağımsızlık ------------------------------------------------------------------------

PAYMENTS = ("Kart", "Diğer")
DELIVERIES = ("Ekspres", "Standart")


def _build_independence(parameters: Parameters) -> tuple:
    n = int(parameters["n"])
    pk, pek, ped = (_probability(parameters, key) for key in ("pK", "pEK", "pED"))
    return (
        NewSample("siparis", n, SEED),
        DrawCategory("siparis", "odeme", PAYMENTS, (((), (pk, round(1 - pk, 10))),), "Ödeme: P(K) olasılıkla kart"),
        DrawCategory(
            "siparis", "teslimat", DELIVERIES,
            ((("Kart",), (pek, round(1 - pek, 10))), (("Diğer",), (ped, round(1 - ped, 10)))),
            "Teslimat: ödeme türüne göre koşullu olasılıkla", by=("odeme",),
        ),
        CrossTab("siparis", "odeme", "teslimat", "satir_yuzde", PAYMENTS, DELIVERIES, percent="satir", decimals=1),
        GroupedBarChart("satir_yuzde", "Ödeme türü", "Grup içindeki yüzde",
                        "Ödeme türüne göre teslimat: yüzde 100 yığılmış", series="sutun", stacked=True, decimals=1),
        Event("siparis", "E", "teslimat", ("Ekspres",), "E: ekspres teslimat"),
        Event("siparis", "K", "odeme", ("Kart",), "K: kartla ödeme"),
        Derive("siparis", "E_ve_K", E.mul(E.var("E"), E.var("K")), "E ∩ K: ekspres ve kart"),
        Statistic("siparis", "E", "mean", "oran_E", "Ekspres oranı: tüm siparişler", decimals=3),
        Statistic("siparis", "E", "mean", "oran_E_K", "Ekspres oranı: kartla ödeyenler", where=("K", 1), decimals=3),
        Statistic("siparis", "E", "mean", "oran_E_D", "Ekspres oranı: diğer ödemeler", where=("K", 0), decimals=3),
        Statistic("siparis", "K", "mean", "oran_K", "Kart oranı", decimals=3),
        Statistic("siparis", "E_ve_K", "mean", "oran_EK", "E ∩ K oranı", decimals=3),
        Scalar("carpim", E.mul(E.ref("oran_E"), E.ref("oran_K")), "E oranı × K oranı", decimals=3),
        ScalarTable(
            (
                ("Ekspres: tüm siparişler", E.ref("oran_E")),
                ("Ekspres: kartla ödeyenler", E.ref("oran_E_K")),
                ("Ekspres: diğer ödemeler", E.ref("oran_E_D")),
                ("E ∩ K oranı", E.ref("oran_EK")),
                ("E oranı × K oranı", E.ref("carpim")),
            ),
            "bagimsizlik",
            decimals=3,
        ),
    )


def _independence_dgp(parameters: Parameters) -> tuple[str, ...]:
    n = int(parameters["n"])
    pk, pek, ped = (_probability(parameters, key) for key in ("pK", "pEK", "pED"))
    pe = pk * pek + (1 - pk) * ped
    relation = "=" if math.isclose(pek, ped) else r"\neq"
    return (
        rf"P(K) = {number(pk, 2)}, \qquad P(E \mid K) = {number(pek, 2)}, \qquad P(E \mid K^c) = {number(ped, 2)}, "
        rf"\qquad n = {n}",
        rf"P(E) = P(K)P(E \mid K) + P(K^c)P(E \mid K^c) = {number(pe, 3)}, \qquad P(E \mid K) {relation} P(E)",
    )


def _independence_metrics(state: LabState, parameters: Parameters) -> tuple[SimMetric, ...]:
    s = state.scalars
    pek, ped = _probability(parameters, "pEK"), _probability(parameters, "pED")
    gap = s["oran_E_K"] - s["oran_E_D"]
    return (
        SimMetric("Ekspres: kartla ödeyenler", _share(s["oran_E_K"]), f"DGP: P(E | K) = {plain(pek, 2)}."),
        SimMetric("Ekspres: diğer ödemeler", _share(s["oran_E_D"]), f"DGP: P(E | Kᶜ) = {plain(ped, 2)}."),
        SimMetric("İki oranın farkı", _share(gap), f"DGP'deki fark: {plain(pek - ped, 2)}."),
        SimMetric("E ∩ K oranı", _share(s["oran_EK"]), f"E oranı × K oranı = {_share(s['carpim'])}."),
    )


def _independence_takeaway(state: LabState, parameters: Parameters) -> str:
    s = state.scalars
    pek, ped = _probability(parameters, "pEK"), _probability(parameters, "pED")
    gap = abs(s["oran_E_K"] - s["oran_E_D"])
    if math.isclose(pek, ped):
        return (
            f"DGP'de iki koşullu olasılık eşittir ({plain(pek, 2)}): ödeme bilgisi ekspres olasılığını değiştirmez, E "
            f"ile K bağımsızdır. Örneklemdeki iki oran yalnız rastgele çekiliş farkı kadar ayrışır (fark "
            f"{_share(gap)}); E ∩ K oranı ({_share(s['oran_EK'])}) oranların çarpımına ({_share(s['carpim'])}) "
            "yakındır. Bağımsız olaylar birlikte gerçekleşebilir: E ∩ K oranı sıfır değildir (§7.5, §7.6)."
        )
    return (
        f"DGP'de P(E | K) = {plain(pek, 2)} ile P(E | Kᶜ) = {plain(ped, 2)} farklıdır: ödeme bilgisi ekspres "
        f"olasılığını değiştirir, E ile K bağımlıdır. Yığılmış sütunlarda iki grubun iç bileşimi ayrışır; E ∩ K oranı "
        f"({_share(s['oran_EK'])}) oranların çarpımından ({_share(s['carpim'])}) uzaklaşır. P(E | Kᶜ)'yi P(E | K)'ye "
        "eşitleyince iki sütun aynı bileşime döner (§7.5, §7.7)."
    )


INDEPENDENCE = SimExperiment(
    topic_key=TOPIC,
    number=2,
    title="Bağımsızlık: koşul oranı değiştiriyor mu?",
    question="Kartla ödeme bilgisi, siparişin ekspres teslimat seçme olasılığını değiştiriyor mu?",
    note=NoteRef("7.5", objects=("Şekil 7.5",)),
    parameters=(
        SimParameter("pK", "Kart payı P(K)", 0.10, 0.90, 0.60, 0.05,
                     "Notlarda verilmez; deney için seçilmiş değer. Bağımsızlık sonucunu değiştirmez.", decimals=2),
        SimParameter("pEK", "Kartla ödeyenlerde ekspres P(E | K)", 0.05, 0.95, 0.40, 0.05, "Notlarda 0,40.",
                     decimals=2),
        SimParameter("pED", "Diğer ödemelerde ekspres P(E | Kᶜ)", 0.05, 0.95, 0.40, 0.05,
                     "P(E | K) ile eşitse E ile K bağımsızdır.", decimals=2),
        SimParameter("n", "Sipariş sayısı n", 100, 20000, 2000, 100, "Rastgele seçilen sipariş sayısı.",
                     integer=True, decimals=0),
    ),
    dgp=_independence_dgp,
    dgp_note=(
        "Her sipariş P(K) olasılıkla kartla ödenir. Ekspres teslimat olasılığı ödeme türüne göre P(E | K) ya da "
        "P(E | Kᶜ)'dir; ikisi eşitse ödeme türü teslimat seçimini etkilemez. Tohum 217'dir."
    ),
    look_at=(
        "**Yığılmış sütunlar** — kartla ve diğer yollarla ödeyenlerde ekspres payı aynı mı?",
        "**Bağımsızlık tablosu** — koşullu oranlar ve E ∩ K oranı ile oranların çarpımı.",
    ),
    build=_build_independence,
    metrics=_independence_metrics,
    takeaway=_independence_takeaway,
    tables=(("satir_yuzde", "Ödeme türüne göre teslimat (satır yüzdeleri)"),
            ("bagimsizlik", "Koşullu oranlar ve çarpım kontrolü")),
    labels=(("odeme", "Ödeme türü"), ("teslimat", "Teslimat")),
)


# --- Deney 3: temel oran ---------------------------------------------------------------------------

STATES = ("Sahte", "Sahte değil")
SIGNALS = ("Alarm", "Alarm yok")
BASE_RATES = tuple(round(0.005 * k, 3) for k in range(1, 101))
"""Temel oran ızgarası: 0,005, 0,010, …, 0,500."""


def _posterior(parameters: Parameters) -> float:
    pf, sens, fpr = (_probability(parameters, key) for key in ("pF", "sens", "fpr"))
    return pf * sens / (pf * sens + (1 - pf) * fpr)


def _build_base_rate(parameters: Parameters) -> tuple:
    n = int(parameters["n"])
    pf, sens, fpr = (_probability(parameters, key) for key in ("pF", "sens", "fpr"))
    rate = E.var("temel_oran")
    true_alarm = E.mul(sens, rate)
    return (
        NewSample("islem", n, SEED),
        DrawCategory("islem", "durum", STATES, (((), (pf, round(1 - pf, 10))),), "Gerçek durum: P(F) olasılıkla sahte"),
        DrawCategory(
            "islem", "sinyal", SIGNALS,
            ((("Sahte",), (sens, round(1 - sens, 10))), (("Sahte değil",), (fpr, round(1 - fpr, 10)))),
            "Alarm: gerçek duruma göre koşullu olasılıkla", by=("durum",),
        ),
        CrossTab("islem", "durum", "sinyal", "dogal", STATES, SIGNALS, margins=True, decimals=0),
        BarChart("dogal", "Alarm", "Gerçek durum", "Alarm alan işlem sayısı",
                 "Alarm alanlar: gerçek sahte ve yanlış alarm"),
        Event("islem", "F", "durum", ("Sahte",), "F: işlem sahte"),
        Event("islem", "A", "sinyal", ("Alarm",), "A: alarm verildi"),
        Statistic("islem", "A", "sum", "alarm_sayisi", "Alarm alan işlem", decimals=0),
        Statistic("islem", "F", "sum", "dogru_alarm", "Alarm alan sahte işlem", where=("A", 1), decimals=0),
        Statistic("islem", "F", "mean", "oran_F_A", "Alarm alanlar içinde sahte oranı", where=("A", 1), decimals=3),
        Scalar("sonsal", E.const(round(_posterior(parameters), 10)), "P(F | A): Bayes teoremiyle (DGP)", decimals=3),
        Outcomes("egri", (("temel_oran", BASE_RATES),), "Temel oran ızgarası: 0,005–0,50"),
        Derive("egri", "sonsal", E.div(true_alarm, E.add(true_alarm, E.mul(fpr, E.sub(1, rate)))),
               "P(F | A) = P(A | F)P(F) / [P(A | F)P(F) + P(A | Fᶜ)(1 − P(F))]"),
        LineChart("egri", "temel_oran", "sonsal", "Temel oran P(F)", "Alarm verildiğinde sahte olasılığı P(F | A)",
                  "Alarmın güvenilirliği temel orana bağlıdır",
                  references=(("sonsal", "Seçilen temel oranda P(F | A)"),), markers=False),
    )


def _base_rate_dgp(parameters: Parameters) -> tuple[str, ...]:
    n = int(parameters["n"])
    pf, sens, fpr = (_probability(parameters, key) for key in ("pF", "sens", "fpr"))
    return (
        rf"P(F) = {number(pf, 3)}, \qquad P(A \mid F) = {number(sens, 2)}, \qquad P(A \mid F^c) = {number(fpr, 2)}, "
        rf"\qquad n = {n}",
        rf"P(F \mid A) = \frac{{P(A \mid F)P(F)}}{{P(A \mid F)P(F) + P(A \mid F^c)P(F^c)}} = "
        rf"{number(_posterior(parameters), 3)}",
    )


def _base_rate_metrics(state: LabState, parameters: Parameters) -> tuple[SimMetric, ...]:
    s = state.scalars
    alarms, true_alarms = int(s["alarm_sayisi"]), int(s["dogru_alarm"])
    return (
        SimMetric("Alarm alan işlem", str(alarms), "Örneklemde alarm verilen işlem sayısı."),
        SimMetric("Bunlardan gerçekten sahte", str(true_alarms), "Alarm alan sahte işlem sayısı."),
        SimMetric("Alarm alanlarda sahte oranı", _share(s["oran_F_A"]),
                  f"Bayes teoremiyle (DGP): P(F | A) = {plain(_posterior(parameters), 3)}."),
        SimMetric("Yanlış alarm sayısı", str(alarms - true_alarms), "Alarm alan ama sahte olmayan işlem."),
    )


def _base_rate_takeaway(state: LabState, parameters: Parameters) -> str:
    s = state.scalars
    pf, sens, fpr = (_probability(parameters, key) for key in ("pF", "sens", "fpr"))
    alarms, true_alarms = int(s["alarm_sayisi"]), int(s["dogru_alarm"])
    text = (
        f"Alarm alan {alarms} işlemin {true_alarms} tanesi gerçekten sahtedir: oran {_share(s['oran_F_A'])}; Bayes "
        f"teoremiyle P(F | A) = {plain(_posterior(parameters), 3)}. Eğri, alarm sistemi aynı kaldığında temel oran "
        "düştükçe alarmın güvenilirliğinin nasıl azaldığını gösterir: nadir bir olayda büyük \"sahte değil\" "
        "grubunun küçük bir yanlış alarm oranı bile sayıca çok alarm üretir (§7.12). "
    )
    if (pf, sens, fpr) == (0.02, 0.9, 0.05):
        text += ("Varsayılan ayarlar notlardaki örnektir: 10.000 işlemde beklenen 180 gerçek ve 490 yanlış alarm, "
                 "P(F | A) ≈ 0,269 (Tablo 7.5).")
    return text


BASE_RATE = SimExperiment(
    topic_key=TOPIC,
    number=3,
    title="Temel oran: alarm ne kadar güvenilir?",
    question="Sahte işlemlerin çoğunu yakalayan bir alarm verildiğinde işlemin gerçekten sahte olma olasılığı neye "
             "bağlıdır?",
    note=NoteRef("7.12", objects=("Tablo 7.5", "Şekil 7.12")),
    parameters=(
        SimParameter("pF", "Temel oran P(F)", 0.005, 0.50, 0.02, 0.005, "Notlarda işlemlerin %2'si sahte.",
                     decimals=3),
        SimParameter("sens", "Sahtede alarm P(A | F)", 0.50, 0.99, 0.90, 0.01, "Notlarda 0,90.", decimals=2),
        SimParameter("fpr", "Yanlış alarm P(A | Fᶜ)", 0.01, 0.30, 0.05, 0.01, "Notlarda 0,05.", decimals=2),
        SimParameter("n", "İşlem sayısı n", 1000, 100000, 10000, 1000, "Notlardaki doğal frekans tablosu 10.000 işlem.",
                     integer=True, decimals=0),
    ),
    dgp=_base_rate_dgp,
    dgp_note=(
        "Her işlem P(F) olasılıkla sahtedir. Sahte işlemde alarm olasılığı P(A | F), sahte olmayan işlemde "
        "P(A | Fᶜ)'dir (yanlış alarm). Tohum 217'dir. Eğri, seçilen alarm sistemiyle 0,005–0,50 aralığındaki temel "
        "oranlar için Bayes teoreminin sonucudur."
    ),
    look_at=(
        "**Sütun grafiği** — alarm alan işlemler içinde gerçek sahte ve yanlış alarm sayıları.",
        "**Eğri** — temel oran değiştikçe P(F | A); yatay çizgi seçilen temel orandaki değer.",
        "**Doğal frekans tablosu** — örneklemdeki sayılar (Tablo 7.5'in simülasyonu).",
    ),
    build=_build_base_rate,
    metrics=_base_rate_metrics,
    takeaway=_base_rate_takeaway,
    tables=(("dogal", "Doğal frekans tablosu (örneklem)"),),
    labels=(("durum", "Gerçek durum"), ("sinyal", "Alarm durumu"), ("temel_oran", "Temel oran P(F)"),
            ("sonsal", "P(F | A)")),
)


KONU07_EXPERIMENTS = (DIRECTION, INDEPENDENCE, BASE_RATE)
