"""Konu 10 Sezgi deneyleri: veri üretim süreci bilinen kontrollü simülasyonlar.

Deney 1  Normal dağılım: μ eğriyi taşır, σ genişletir                          (Notlar §10.6–10.8, Şekil 10.7–10.9)
Deney 2  Tek-düze dağılım: olasılık aralığın uzunluğuyla orantılıdır            (Notlar §10.2–10.3, Şekil 10.4)
Deney 3  z-dönüşümü: ortak N(0, 1) ölçeği, korunan alan                         (Notlar §10.9–10.12, Şekil 10.13)

Notlarda simülasyonla üretilmiş bir şekil yoktur. Varsayılan ayarlar notların örnekleridir: Deney 1 ve 3'te sınav
puanı N(70, 10²) (§10.8, §10.12), Deney 2'de U(120, 140) ve 128–136 dakika aralığı (Şekil 10.4). Normal eğri
altındaki alanlar Konu 11'in konusudur; deneyler yalnız 68–95–99,7 kuralının paylarını kullanır.
"""

from __future__ import annotations

from core.labs import expr as E
from core.labs.runner import LabState
from core.labs.sezgi import Parameters, SimExperiment, SimMetric, SimParameter, plain
from core.labs.spec import (
    DensityPlot,
    Derive,
    Draw,
    Histogram,
    JoinColumns,
    NewSample,
    NoteRef,
    Scalar,
    ScalarTable,
    Statistic,
)

SEED = 217
TOPIC = "konu10"
EMPIRICAL = (0.683, 0.954, 0.997)
"""68–95–99,7 kuralı: μ ± σ, μ ± 2σ ve μ ± 3σ içindeki yaklaşık olasılıklar (§10.8)."""


def _short(value: float, decimals: int = 3) -> str:
    """Sondaki sıfırları atılmış düz metin sayı (4; 0,5; 132,5)."""

    text = f"{value:.{decimals}f}".rstrip("0").rstrip(".")
    return text.replace(".", ",").replace("-", "−")


def _tex(value: float, decimals: int = 3) -> str:
    return _short(value, decimals).replace(",", "{,}").replace("−", "-")


def _signless(value: float, decimals: int = 3) -> str:
    """Yuvarlanınca sıfır olan küçük negatif değer "−0,000" değil "0,000" yazılır."""

    return plain(round(value, decimals) + 0.0, decimals)


def _within(variable: str, centre: float | int, half_width: float | int):
    """|değişken − merkez| ≤ yarı genişlik göstergesi (1: aralıkta)."""

    return E.compare("le", E.absolute(E.sub(E.var(variable), centre)), half_width)


def _whole(value: float) -> float | int:
    """Tam sayı değerler tam sayı olarak (kodda 132.0 yerine 132 yazılır)."""

    return int(value) if float(value).is_integer() else value


# --- Deney 1: μ ve σ -------------------------------------------------------------------------

X_RANGE = (0, 140)
Y_MAX = 0.10
"""Eksenler sabittir: μ ∈ [50, 90], σ ∈ [4, 15] için μ ± 3σ yatay eksenin içindedir; σ = 4'te tepe
1/(4√(2π)) ≈ 0,0997 < 0,10."""


def _normal_settings(parameters: Parameters) -> tuple[int, int, int]:
    return int(parameters["mu"]), int(parameters["sigma"]), int(parameters["n"])


def _build_normal(parameters: Parameters) -> tuple:
    mu, sigma, n = _normal_settings(parameters)
    return (
        NewSample("veri", n, SEED),
        Draw("veri", "x", "normal", mu, sigma, "X ~ N(μ, σ²)"),
        Derive("veri", "bir_sigma", _within("x", mu, sigma), "X, μ ± σ aralığında mı? (1: evet)"),
        Derive("veri", "iki_sigma", _within("x", mu, 2 * sigma), "X, μ ± 2σ aralığında mı? (1: evet)"),
        Statistic("veri", "x", "mean", "ortalama", "Gözlemlerin ortalaması x̄", decimals=2),
        Statistic("veri", "x", "std", "s", "Gözlemlerin standart sapması s", decimals=2),
        Statistic("veri", "bir_sigma", "mean", "pay_1", "μ ± σ içindeki gözlemlerin payı", decimals=3),
        Statistic("veri", "iki_sigma", "mean", "pay_2", "μ ± 2σ içindeki gözlemlerin payı", decimals=3),
        DensityPlot("normal", mu, sigma, X_RANGE, "Normal yoğunluk: μ ± σ aralığının altındaki alan", "x",
                    shade=((mu - sigma, mu + sigma),), references=((mu, f"μ = {mu}"),), y_max=Y_MAX),
        Histogram("veri", (("x", "Gözlemler"),), 70, X_RANGE[0], X_RANGE[1], "Gözlemlerin histogramı", "x",
                  references=((mu - sigma, "μ − σ"), (mu + sigma, "μ + σ")), y_label="Gözlem sayısı"),
    )


def _normal_dgp(parameters: Parameters) -> tuple[str, ...]:
    mu, sigma, n = _normal_settings(parameters)
    return (
        rf"X \sim N(\mu, \sigma^2), \qquad \mu = {mu},\ \sigma = {sigma}, \qquad n = {n}",
        r"f(x) = \frac{1}{\sigma\sqrt{2\pi}} \exp\!\left[-\frac{1}{2}\left(\frac{x - \mu}{\sigma}\right)^2\right], "
        r"\qquad P(\mu - \sigma \le X \le \mu + \sigma) \approx 0{,}683",
    )


def _normal_metrics(state: LabState, parameters: Parameters) -> tuple[SimMetric, ...]:
    mu, sigma, _ = _normal_settings(parameters)
    s = state.scalars
    return (
        SimMetric("Ortalama x̄", plain(s["ortalama"], 2), f"DGP: μ = {mu}."),
        SimMetric("Standart sapma s", plain(s["s"], 2), f"DGP: σ = {sigma}."),
        SimMetric("μ ± σ içindeki pay", plain(s["pay_1"], 3), "Normal dağılımda yaklaşık 0,683."),
        SimMetric("μ ± 2σ içindeki pay", plain(s["pay_2"], 3), "Normal dağılımda yaklaşık 0,954."),
    )


def _normal_takeaway(state: LabState, parameters: Parameters) -> str:
    mu, sigma, _ = _normal_settings(parameters)
    s = state.scalars
    text = (
        "μ eğriyi biçimini değiştirmeden yatay eksende taşır; σ büyüdükçe eğri genişler ve basıklaşır, çünkü eğrinin "
        "altındaki toplam alan her zaman 1'dir (§10.6, §10.7). μ ve σ ne olursa olsun gözlemlerin yaklaşık %68,3'ü "
        f"μ ± σ, %95,4'ü μ ± 2σ aralığındadır; bu ayarda paylar {plain(s['pay_1'], 3)} ve {plain(s['pay_2'], 3)} "
        f"(§10.8). Örneklemin ortalaması {plain(s['ortalama'], 2)} ve standart sapması {plain(s['s'], 2)}, "
        "DGP'nin μ ve σ değerlerine yakındır. "
    )
    if (mu, sigma) == (70, 10):
        text += "Bu ayar notlardaki sınav puanı modelidir: yaklaşık %68,3'ü 60–80, %95,4'ü 50–90 aralığında."
    else:
        text += "μ = 70 ve σ = 10 notlardaki sınav puanı modelidir (§10.8)."
    return text


NORMAL_SHAPE = SimExperiment(
    topic_key=TOPIC,
    number=1,
    title="Normal dağılım: μ eğriyi taşır, σ genişletir",
    question="Normal dağılımın ortalaması ve standart sapması değişince eğri ve ondan çekilen gözlemler nasıl değişir; "
             "μ ± σ ve μ ± 2σ aralıklarına düşen gözlemlerin payı neden değişmez?",
    note=NoteRef("10.8", objects=("Şekil 10.7", "Şekil 10.8", "Şekil 10.9")),
    parameters=(
        SimParameter("mu", "Ortalama μ", 50, 90, 70, 5, "Notlardaki sınav puanı örneğinde μ = 70.", integer=True,
                     decimals=0),
        SimParameter("sigma", "Standart sapma σ", 4, 15, 10, 1, "Notlardaki sınav puanı örneğinde σ = 10.",
                     integer=True, decimals=0),
        SimParameter("n", "Gözlem sayısı n", 100, 10000, 1000, 100, "N(μ, σ²) dağılımından bağımsız çekilişler.",
                     integer=True, decimals=0),
    ),
    dgp=_normal_dgp,
    dgp_note=(
        "Gözlemler N(μ, σ²) dağılımından birbirinden bağımsız çekilir; tohum 217'dir. Eksenler kaydırıcılarla "
        "değişmez: eğrinin kaydığı, genişlediği ve basıklaştığı doğrudan görülür."
    ),
    look_at=(
        "**Yoğunluk eğrisi** — μ değişince eğrinin yeri, σ değişince genişliği ve yüksekliği; boyalı alan μ ± σ.",
        "**Histogram** — gözlemler eğrinin biçimini izler; μ − σ ile μ + σ arasındaki sütunlar gözlemlerin "
        "yaklaşık üçte ikisini taşır.",
    ),
    build=_build_normal,
    metrics=_normal_metrics,
    takeaway=_normal_takeaway,
    labels=(("x", "x"),),
)


# --- Deney 2: tek-düze dağılım ve aralık uzunluğu --------------------------------------------------

LOWER, UPPER = 120, 140
"""Şekil 10.4: uçuş süresi X ~ U(120, 140); yoğunluk 1/20 = 0,05."""


def _uniform_settings(parameters: Parameters) -> tuple[float | int, float | int, int]:
    return _whole(round(float(parameters["c"]), 1)), _whole(round(float(parameters["h"]), 1)), int(parameters["n"])


def _build_uniform(parameters: Parameters) -> tuple:
    centre, half, n = _uniform_settings(parameters)
    low, high = _whole(centre - half), _whole(centre + half)
    return (
        NewSample("ucus", n, SEED),
        Draw("ucus", "x", "uniform", LOWER, UPPER, "X ~ U(120, 140): uçuş süresi (dakika)"),
        Derive("ucus", "aralikta", _within("x", centre, half), "X, c ± h aralığında mı? (1: evet)"),
        Derive("ucus", "tam_c", E.compare("eq", E.var("x"), centre), "X tam olarak c'ye eşit mi? (1: evet)"),
        Statistic("ucus", "aralikta", "mean", "pay", "Aralıktaki uçuşların payı", decimals=3),
        Statistic("ucus", "tam_c", "sum", "tam_c_sayisi", "Tam olarak c süren uçuş sayısı", decimals=0),
        Scalar("P_aralik", E.div(E.sub(high, low), E.sub(UPPER, LOWER)),
               "(üst uç − alt uç)/(b − a) = 2h/20: uzunluk oranı, (10.4)", decimals=3),
        DensityPlot("uniform", LOWER, UPPER, (115, 145), "U(120, 140): olasılık dikdörtgenin alanıdır",
                    "Uçuş süresi (dakika)", shade=((low, high),)),
        Histogram("ucus", (("x", "Uçuşlar"),), 20, LOWER, UPPER, "Uçuş sürelerinin histogramı", "Uçuş süresi (dakika)",
                  references=((low, "c − h"), (high, "c + h")), y_label="Uçuş sayısı"),
    )


def _uniform_dgp(parameters: Parameters) -> tuple[str, ...]:
    centre, half, n = _uniform_settings(parameters)
    return (
        rf"X \sim U(120, 140), \qquad f(x) = \frac{{1}}{{140 - 120}} = 0{{,}}05, \qquad c = {_tex(centre)},\ "
        rf"h = {_tex(half)}, \qquad n = {n}",
        rf"P(c - h \le X \le c + h) = \frac{{2h}}{{20}} = {_tex(2 * half / 20)}, \qquad P(X = c) = 0",
    )


def _uniform_metrics(state: LabState, parameters: Parameters) -> tuple[SimMetric, ...]:
    centre, half, n = _uniform_settings(parameters)
    s = state.scalars
    return (
        SimMetric("Aralık", f"{_short(centre - half)}–{_short(centre + half)}" if half else _short(centre),
                  "c − h ile c + h (dakika); h = 0 ise tek nokta."),
        SimMetric("P(c − h ≤ X ≤ c + h)", plain(s["P_aralik"], 3), "Uzunluk oranı 2h/20."),
        SimMetric("Simülasyondaki pay", plain(s["pay"], 3), f"n = {n} uçuştan aralığa düşenlerin oranı."),
        SimMetric("Tam c süren uçuş", str(int(s["tam_c_sayisi"])), "Tek bir noktanın olasılığı sıfırdır, (10.1)."),
    )


def _uniform_takeaway(state: LabState, parameters: Parameters) -> str:
    centre, half, _ = _uniform_settings(parameters)
    s = state.scalars
    if half == 0:
        text = (
            "h = 0 iken aralık tek bir noktadır: genişlik sıfır olduğu için alan da sıfırdır ve P(X = c) = 0 "
            f"(§10.2). Simülasyonda tam olarak c = {_short(centre)} dakika süren uçuş sayısı "
            f"{int(s['tam_c_sayisi'])}. Bu, c'nin imkânsız olduğu anlamına gelmez; sürekli modelde olasılık "
            "yalnız pozitif uzunluklu aralıklara düşer. "
        )
    else:
        text = (
            f"Aralığın uzunluğu 2h = {_short(2 * half)} dakika olduğundan olasılık {_short(2 * half)}/20 = "
            f"{plain(s['P_aralik'], 3)}; simülasyonda aralığa düşen uçuşların payı {plain(s['pay'], 3)}. Merkez c "
            "değişince, aralık [120, 140] içinde kaldıkça olasılık değişmez: eşit uzunluktaki alt aralıkların "
            "olasılıkları eşittir (§10.3). h küçüldükçe olasılık sıfıra iner; h = 0'da aralık tek bir noktadır "
            "(§10.2). "
        )
    if (centre, half) == (132, 4):
        text += "Bu ayar Şekil 10.4'teki P(128 ≤ X ≤ 136) = 0,40 hesabıdır."
    else:
        text += "c = 132 ve h = 4 Şekil 10.4'teki 128–136 aralığıdır."
    return text


UNIFORM_INTERVAL = SimExperiment(
    topic_key=TOPIC,
    number=2,
    title="Tek-düze dağılım: olasılık aralığın uzunluğuyla orantılıdır",
    question="Uçuş süresi 120 ile 140 dakika arasında tek-düze dağılıyorsa, bir aralığa düşen uçuşların payı "
             "aralığın yerine mi, uzunluğuna mı bağlıdır; aralık tek bir noktaya daraldığında ne olur?",
    note=NoteRef("10.3", objects=("Şekil 10.4", "(10.4)")),
    parameters=(
        SimParameter("c", "Aralığın merkezi c (dakika)", 125, 135, 132, 1, "Şekil 10.4: 128–136 aralığı, c = 132.",
                     integer=True, decimals=0),
        SimParameter("h", "Yarı genişlik h (dakika)", 0, 5, 4, 0.5,
                     "Aralık c − h ile c + h arasıdır; h = 0 tek bir noktadır.", decimals=1),
        SimParameter("n", "Uçuş sayısı n", 100, 10000, 1000, 100, "U(120, 140) dağılımından bağımsız çekilişler.",
                     integer=True, decimals=0),
    ),
    dgp=_uniform_dgp,
    dgp_note=(
        "Uçuş süreleri U(120, 140) dağılımından birbirinden bağımsız çekilir; tohum 217'dir. Kaydırıcıların "
        "sınırları aralığın her zaman [120, 140] içinde kalmasını sağlar."
    ),
    look_at=(
        "**Yoğunluk grafiği** — boyalı dikdörtgenin alanı: yükseklik 0,05 × genişlik 2h.",
        "**Histogram ve metrikler** — aralığa düşen uçuşların payı; c'yi kaydırıp h'yi sabit tutun, sonra h'yi "
        "sıfıra indirin.",
    ),
    build=_build_uniform,
    metrics=_uniform_metrics,
    takeaway=_uniform_takeaway,
    labels=(("x", "Uçuş süresi (dakika)"),),
)


# --- Deney 3: z-dönüşümü ve alanın korunması --------------------------------------------------------

K_VALUES = (1, 2, 3)


def _k_sigma(k: int) -> str:
    """kσ yazımı: k = 1 için yalnız σ."""

    return "σ" if k == 1 else f"{k}σ"


def _z_settings(parameters: Parameters) -> tuple[int, int, int]:
    return int(parameters["mu"]), int(parameters["sigma"]), int(parameters["n"])


def _build_z(parameters: Parameters) -> tuple:
    mu, sigma, n = _z_settings(parameters)
    shares = []
    for k in K_VALUES:
        shares += [
            Derive("puan", f"x_{k}", _within("x", mu, k * sigma), f"X, μ ± {_k_sigma(k)} aralığında mı? (1: evet)"),
            Derive("puan", f"z_{k}", _within("z", 0, k), f"z, −{k} ile {k} arasında mı? (1: evet)"),
            Statistic("puan", f"x_{k}", "mean", f"pay_x_{k}", f"μ ± {_k_sigma(k)} içindeki pay: özgün ölçek",
                      decimals=3),
            Statistic("puan", f"z_{k}", "mean", f"pay_z_{k}", f"|z| ≤ {k} içindeki pay: standart ölçek", decimals=3),
        ]
    labels = tuple(f"k = {k}" for k in K_VALUES)
    return (
        NewSample("puan", n, SEED),
        Draw("puan", "x", "normal", mu, sigma, "X ~ N(μ, σ²): özgün ölçek"),
        Derive("puan", "z", E.div(E.sub(E.var("x"), mu), sigma), "z = (x − μ)/σ, (10.8)"),
        Statistic("puan", "z", "mean", "z_ortalama", "z değerlerinin ortalaması", decimals=3),
        Statistic("puan", "z", "std", "z_s", "z değerlerinin standart sapması", decimals=3),
        *shares,
        ScalarTable(tuple(zip(labels, (E.ref(f"pay_x_{k}") for k in K_VALUES))), "ozgun", decimals=3),
        ScalarTable(tuple(zip(labels, (E.ref(f"pay_z_{k}") for k in K_VALUES))), "standart", decimals=3),
        ScalarTable(tuple(zip(labels, (E.const(value) for value in EMPIRICAL))), "ampirik", decimals=3),
        JoinColumns("paylar", (("Özgün ölçek: μ ± kσ", "ozgun", "deger"),
                               ("Standart ölçek: |z| ≤ k", "standart", "deger"),
                               ("Ampirik kural (yaklaşık)", "ampirik", "deger")), decimals=3),
        Histogram("puan", (("x", "Özgün ölçek"),), 40, mu - 5 * sigma, mu + 5 * sigma, "Özgün ölçek: x", "x",
                  references=((mu - sigma, "μ − σ"), (mu + sigma, "μ + σ")), y_label="Gözlem sayısı"),
        Histogram("puan", (("z", "Standart ölçek"),), 40, -5, 5, "Standart ölçek: z = (x − μ)/σ", "z",
                  references=((-1, "z = −1"), (1, "z = 1")), y_label="Gözlem sayısı"),
    )


def _z_dgp(parameters: Parameters) -> tuple[str, ...]:
    mu, sigma, n = _z_settings(parameters)
    return (
        rf"X \sim N(\mu, \sigma^2), \qquad \mu = {mu},\ \sigma = {sigma}, \qquad n = {n}, \qquad "
        r"z = \frac{x - \mu}{\sigma}",
        rf"P({mu - sigma} \le X \le {mu + sigma}) = P(-1 \le Z \le 1), \qquad Z \sim N(0, 1)",
    )


def _z_metrics(state: LabState, parameters: Parameters) -> tuple[SimMetric, ...]:
    s = state.scalars
    return (
        SimMetric("z'nin ortalaması", _signless(s["z_ortalama"]), "Standart normalde μ_Z = 0."),
        SimMetric("z'nin standart sapması", plain(s["z_s"], 3), "Standart normalde σ_Z = 1."),
        SimMetric("μ ± σ ve |z| ≤ 1 payı", plain(s["pay_x_1"], 3),
                  f"İki ölçekte aynı gözlemler: {plain(s['pay_z_1'], 3)}."),
    )


def _z_takeaway(state: LabState, parameters: Parameters) -> str:
    mu, sigma, _ = _z_settings(parameters)
    s = state.scalars
    same = all(s[f"pay_x_{k}"] == s[f"pay_z_{k}"] for k in K_VALUES)
    text = (
        f"z = (x − {mu})/{sigma} dönüşümü her gözlemi ortalamadan kaç standart sapma uzakta olduğuyla yeniden yazar: "
        f"z'lerin ortalaması {_signless(s['z_ortalama'])}, standart sapması {plain(s['z_s'], 3)} (§10.9, §10.10). "
        "İki histogram aynı biçimdedir; yalnız yatay eksenin birimi değişmiştir. "
    )
    if same:
        text += (
            f"{mu - sigma}–{mu + sigma} aralığına düşen gözlemler tam olarak −1 ≤ z ≤ 1 aralığına düşenlerdir: iki "
            f"payın ikisi de {plain(s['pay_x_1'], 3)}. Standartlaştırma olasılık alanını değiştirmez, yalnız onu "
            "ortak N(0, 1) ölçeğine taşır (§10.12, (10.10)). "
        )
    if (mu, sigma) != (70, 10):
        text += "μ = 70 ve σ = 10 notlardaki P(60 ≤ X ≤ 80) = P(−1 ≤ Z ≤ 1) örneğidir."
    else:
        text += "Bu ayar notlardaki P(60 ≤ X ≤ 80) = P(−1 ≤ Z ≤ 1) örneğidir (Şekil 10.13)."
    return text


STANDARDIZATION = SimExperiment(
    topic_key=TOPIC,
    number=3,
    title="z-dönüşümü: ortak N(0, 1) ölçeği, korunan alan",
    question="Farklı ortalama ve standart sapmalı normal değişkenler z = (x − μ)/σ ile dönüştürülünce ne değişir, ne "
             "korunur? Bir aralığa düşen gözlemlerin payı dönüşümden etkilenir mi?",
    note=NoteRef("10.12", objects=("Şekil 10.13", "(10.10)")),
    parameters=(
        SimParameter("mu", "Ortalama μ", 40, 100, 70, 5, "Notlardaki örnek: N(70, 10²).", integer=True, decimals=0),
        SimParameter("sigma", "Standart sapma σ", 2, 20, 10, 1, "Notlardaki örnekte σ = 10.", integer=True,
                     decimals=0),
        SimParameter("n", "Gözlem sayısı n", 100, 10000, 1000, 100, "N(μ, σ²) dağılımından bağımsız çekilişler.",
                     integer=True, decimals=0),
    ),
    dgp=_z_dgp,
    dgp_note=(
        "Gözlemler N(μ, σ²) dağılımından birbirinden bağımsız çekilir ve her biri z = (x − μ)/σ ile standart ölçeğe "
        "taşınır; tohum 217'dir. Özgün ölçeğin histogramı μ ± 5σ aralığında çizilir."
    ),
    look_at=(
        "**İki histogram** — özgün ölçek ve standart ölçek aynı biçimdedir; μ ve σ değişince yalnız birinci "
        "grafiğin eksen değerleri değişir.",
        "**Pay tablosu** — μ ± kσ ile |z| ≤ k aralıklarına düşen gözlemlerin payları aynıdır.",
    ),
    build=_build_z,
    metrics=_z_metrics,
    takeaway=_z_takeaway,
    tables=(("paylar", "Aralıklara düşen gözlemlerin payı: iki ölçek ve ampirik kural"),),
    labels=(("x", "Özgün ölçek x"), ("z", "Standart ölçek z")),
)


KONU10_EXPERIMENTS = (NORMAL_SHAPE, UNIFORM_INTERVAL, STANDARDIZATION)
