"""Konu 10 uygulaması: sürekli rassal değişken, tek-düze ve normal dağılım, z-dönüşümü.

Ders notlarının çözümlü örnekleri: §10.3 (uçuş süresi U(120, 140); Şekil 10.4), §10.4 (U(0, 0,5); Şekil 10.5), §10.5 ve
§10.8 (N(70, 10²): simetri ve 68–95–99,7 kuralı; Şekil 10.9), §10.10 (sınav puanı; Denklem 10.8–10.9), §10.11 (iki
sınav), §10.12 (standartlaştırma alanı korur; Şekil 10.13) ve §10.14 (dolum miktarı N(500, 10²); Şekil 10.15).
Buradaki her ``Check`` notlarda basılı bir sayıdır; değer notlardan kopyalanmıştır, hesaplanmamıştır. §10.1–10.2,
§10.6–10.7, §10.9 ve §10.13 kavramsaldır; μ ve σ'nın eğriye etkisi Sezgi sekmesindeki Deney 1'dir.

Normal eğri altındaki alanlar Konu 11'e kadar tablo (Φ) ile hesaplanmaz: burada alan, eğrinin altını 0,01 genişliğinde
dikdörtgenlere bölüp dikdörtgen alanlarını (yükseklik × genişlik) toplayarak bulunur. Olasılık = eğri altındaki alan.
"""

from __future__ import annotations

from core.labs import expr as E
from core.labs.spec import (
    BarChart,
    CellTarget,
    Check,
    DensityPlot,
    Derive,
    InlineData,
    LabSpec,
    LabStep,
    NoteRef,
    Rectangles,
    Scalar,
    ScalarTarget,
    ShowFrame,
    Statistic,
)

FLIGHT = (120, 140)
"""§10.3: uçuş süresi X ~ U(120, 140) dakika; incelenen aralık 128–136."""
EXAM_MEAN, EXAM_SD = 70, 10
"""§10.8 ve §10.10: sınav puanları X ~ N(70, 10²)."""
EXAMS = (("A", 78, 70, 4), ("B", 88, 80, 8))
"""§10.11: öğrencinin iki sınavdaki puanı, sınıf ortalaması ve standart sapması."""
FILL_MEAN, FILL_SD = 500, 10
"""§10.14: dolum miktarı X ~ N(500, 10²) ml."""
WIDTH = 0.01
"""Alan hesabında dikdörtgen genişliği (özgün ölçekte)."""


def _scalar(name: str, expected: float, label: str, decimals: int) -> Check:
    return Check(label, ScalarTarget(name), expected, decimals)


def _between(low: float, high: float) -> E.Expr:
    """Gösterge: low ≤ x ≤ high ise 1, değilse 0."""

    return E.mul(E.compare("ge", E.var("x"), low), E.compare("le", E.var("x"), high))


def _z(x: float, mean: float, sd: float) -> E.Expr:
    return E.div(E.sub(x, mean), sd)


STEPS = (
    LabStep(
        number=1,
        title="Tek-düze dağılım: olasılık dikdörtgenin alanıdır",
        note=NoteRef("10.3", objects=("Şekil 10.4",)),
        explanation=(
            "Bir uçuşun süresi 120 ile 140 dakika arasında tek-düze dağılsın: $X \\sim U(120, 140)$. Yoğunluk bu "
            "aralıkta sabittir, $f(x) = 1/(b - a)$. $P(128 \\leq X \\leq 136)$, yüksekliği $f(x)$ ve genişliği "
            "$136 - 128$ olan dikdörtgenin alanıdır; aynı sonuç uzunluk oranından da bulunur: "
            "$(d - c)/(b - a)$. Ortalama aralığın orta noktası $(a + b)/2$, varyans $(b - a)^2/12$'dir."
        ),
        operations=(
            Scalar("f_ucus", E.div(1, FLIGHT[1] - FLIGHT[0]), "f(x) = 1/(140 − 120)", decimals=2),
            Scalar("P_ucus", E.mul(136 - 128, E.ref("f_ucus")), "P(128 ≤ X ≤ 136) = (136 − 128) × f(x)", decimals=2),
            Scalar("P_ucus_oran", E.div(136 - 128, FLIGHT[1] - FLIGHT[0]), "(d − c)/(b − a): uzunluk oranı",
                   decimals=2),
            Scalar("mu_ucus", E.div(FLIGHT[0] + FLIGHT[1], 2), "μ = (a + b)/2", decimals=0),
            Scalar("var_ucus", E.div(E.power(FLIGHT[1] - FLIGHT[0], 2), 12), "σ² = (b − a)²/12", decimals=2),
            Scalar("sd_ucus", E.sqrt(E.ref("var_ucus")), "σ = √σ²", decimals=2),
            DensityPlot("uniform", FLIGHT[0], FLIGHT[1], (116, 144), "U(120, 140): 128–136 dakika aralığının alanı",
                        "Uçuş süresi (dakika)", shade=((128, 136),)),
        ),
        checks=(
            _scalar("f_ucus", 0.05, "f(x) = 1/20", 2),
            _scalar("P_ucus", 0.40, "P(128 ≤ X ≤ 136): dikdörtgenin alanı", 2),
            _scalar("P_ucus_oran", 0.40, "P(128 ≤ X ≤ 136): uzunluk oranı", 2),
            _scalar("mu_ucus", 130, "μ", 0),
            _scalar("var_ucus", 33.33, "σ² = 20²/12", 2),
            _scalar("sd_ucus", 5.77, "σ", 2),
        ),
        takeaway=(
            "Boyalı dikdörtgenin alanı 8 × (1/20) = 0,40'tır: uçuşların %40'ının 128–136 dakika sürmesi beklenir. "
            "Tek-düze dağılımda eşit uzunluktaki alt aralıkların olasılıkları eşittir; \"bütün değerler eşit "
            "olasılıklı\" demek yanlıştır, çünkü her tekil değerin olasılığı sıfırdır (§10.3)."
        ),
    ),
    LabStep(
        number=2,
        title="Yoğunluk yüksekliği olasılık değildir",
        note=NoteRef("10.4", objects=("Şekil 10.5",)),
        explanation=(
            "$X \\sim U(0, 0{,}5)$ ise yoğunluğun yüksekliği $f(x) = 1/0{,}5 = 2$'dir. Yükseklik 1'den büyüktür, ama "
            "olasılık kuralları yükseklik için değil alan için geçerlidir: toplam alan $0{,}5 \\times 2 = 1$'dir."
        ),
        operations=(
            Scalar("f_dar", E.div(1, 0.5), "f(x) = 1/0,5", decimals=0),
            Scalar("alan_dar", E.mul(0.5, E.ref("f_dar")), "Toplam alan = 0,5 × 2", decimals=0),
            DensityPlot("uniform", 0, 0.5, (-0.1, 0.65), "U(0, 0,5): yükseklik 2, toplam alan 1", "x",
                        shade=((0, 0.5),)),
        ),
        checks=(
            _scalar("f_dar", 2, "f(x) = 2", 0),
            _scalar("alan_dar", 1, "Toplam alan", 0),
        ),
        takeaway=(
            "Yoğunluk yüksekliği 2 olsa da dağılım geçerlidir; 0 ile 1 arasında olması gereken büyüklük alandır. "
            "Yüksekliğin 1'i aşamayacağı düşüncesi kesikli olasılık fonksiyonunu sürekli yoğunlukla karıştırmaktan "
            "gelir (§10.4)."
        ),
    ),
    LabStep(
        number=3,
        title="Normal eğri altındaki alanlar: 68–95–99,7 kuralı",
        note=NoteRef("10.8", objects=("Şekil 10.9",)),
        explanation=(
            "Sınav puanları $X \\sim N(70, 10^2)$ ile modellensin. Olasılık eğri altındaki alandır: 10–130 aralığı "
            "(μ ± 6σ) 0,01 genişliğinde 12 000 dikdörtgene bölünür, her dikdörtgenin alanı yükseklik $f(x)$ × "
            "genişlik 0,01'dir. Bir aralığın olasılığı, o aralıktaki dikdörtgenlerin alanları toplanarak bulunur. "
            "Φ tablosuyla alan hesabı Konu 11'in konusudur."
        ),
        operations=(
            Scalar("alt_1", E.sub(EXAM_MEAN, EXAM_SD), "μ − σ", decimals=0),
            Scalar("ust_1", E.add(EXAM_MEAN, EXAM_SD), "μ + σ", decimals=0),
            Scalar("alt_2", E.sub(EXAM_MEAN, E.mul(2, EXAM_SD)), "μ − 2σ", decimals=0),
            Scalar("ust_2", E.add(EXAM_MEAN, E.mul(2, EXAM_SD)), "μ + 2σ", decimals=0),
            Rectangles("izgara", "x", 10, 130, WIDTH, "N(70, 10²): 10–130 aralığı 0,01 genişliğinde dikdörtgenlere"),
            Derive("izgara", "f", E.dnorm(E.var("x"), EXAM_MEAN, EXAM_SD), "Dikdörtgenin yüksekliği f(x)"),
            Derive("izgara", "alan", E.mul(E.var("f"), WIDTH), "Dikdörtgenin alanı f(x) × 0,01"),
            Statistic("izgara", "alan", "sum", "alan_toplam", "Toplam alan", decimals=3),
            Derive("izgara", "sol", E.compare("le", E.var("x"), EXAM_MEAN), "x ≤ μ: ortalamanın solu"),
            Statistic("izgara", "alan", "sum", "alan_sol", "P(X ≤ 70): ortalamanın solundaki alan",
                      where=("sol", 1), decimals=3),
            Derive("izgara", "bir", _between(60, 80), "μ ± σ: 60 ≤ x ≤ 80"),
            Statistic("izgara", "alan", "sum", "alan_bir", "P(60 ≤ X ≤ 80): μ ± σ", where=("bir", 1), decimals=4),
            Derive("izgara", "iki", _between(50, 90), "μ ± 2σ: 50 ≤ x ≤ 90"),
            Statistic("izgara", "alan", "sum", "alan_iki", "P(50 ≤ X ≤ 90): μ ± 2σ", where=("iki", 1), decimals=4),
            Derive("izgara", "uc", _between(40, 100), "μ ± 3σ: 40 ≤ x ≤ 100"),
            Statistic("izgara", "alan", "sum", "alan_uc", "P(40 ≤ X ≤ 100): μ ± 3σ", where=("uc", 1), decimals=4),
            DensityPlot("normal", EXAM_MEAN, EXAM_SD, (30, 110), "N(70, 10²): μ ± σ aralığının alanı", "Sınav puanı",
                        shade=((60, 80),)),
        ),
        checks=(
            _scalar("alt_1", 60, "μ − σ", 0),
            _scalar("ust_1", 80, "μ + σ", 0),
            _scalar("alt_2", 50, "μ − 2σ", 0),
            _scalar("ust_2", 90, "μ + 2σ", 0),
            _scalar("alan_toplam", 1, "Eğri altındaki toplam alan", 0),
            _scalar("alan_sol", 0.50, "μ'nun solundaki alan", 2),
            _scalar("alan_bir", 0.683, "μ ± σ", 3),
            _scalar("alan_iki", 0.954, "μ ± 2σ", 3),
            _scalar("alan_uc", 0.997, "μ ± 3σ", 3),
        ),
        takeaway=(
            "Öğrencilerin yaklaşık %68,3'ünün 60–80, %95,4'ünün 50–90 aralığında olması beklenir. Dikdörtgenlerin "
            "toplamı eğri altındaki alana çok yakındır: toplam alan 1, simetri nedeniyle ortalamanın "
            "solundaki alan 0,50'dir. Kural yalnız yaklaşık normal (çan biçimli) dağılımlarda kullanılır (§10.5, "
            "§10.8)."
        ),
    ),
    LabStep(
        number=4,
        title="z-dönüşümü ve ters dönüşüm",
        note=NoteRef("10.10", objects=("(10.8)", "(10.9)")),
        explanation=(
            "$X \\sim N(\\mu, \\sigma^2)$ ise bir $x$ değeri $z = (x - \\mu)/\\sigma$ ile standart ölçeğe taşınır: "
            "$z$, değerin ortalamadan kaç standart sapma uzakta olduğunu söyler (Denklem 10.8). Ters yönde "
            "$x = \\mu + z\\sigma$'dır (Denklem 10.9). Sınav puanları $N(70, 10^2)$'dir."
        ),
        operations=(
            Scalar("z_85", _z(85, EXAM_MEAN, EXAM_SD), "x = 85: z = (85 − 70)/10", decimals=1),
            Scalar("z_55", _z(55, EXAM_MEAN, EXAM_SD), "x = 55: z = (55 − 70)/10", decimals=1),
            Scalar("x_eksi_2", E.add(EXAM_MEAN, E.mul(E.neg(2), EXAM_SD)), "z = −2: x = 70 + (−2)(10)", decimals=0),
            DensityPlot("normal", EXAM_MEAN, EXAM_SD, (30, 110), "Aynı uzaklık, zıt yön: z = ±1,5", "Sınav puanı",
                        references=((55, "x = 55: z = −1,5"), (85, "x = 85: z = 1,5"))),
        ),
        checks=(
            _scalar("z_85", 1.5, "z(85)", 1),
            _scalar("z_55", -1.5, "z(55)", 1),
            _scalar("x_eksi_2", 50, "x(z = −2)", 0),
        ),
        takeaway=(
            "85 puan ortalamanın 1,5 standart sapma üzerinde, 55 puan 1,5 standart sapma altındadır; iki değer "
            "merkeze eşit uzaklıktadır. z = −2 olan puan 50'dir. z birimsizdir ve bir yüzde değildir (§10.10)."
        ),
    ),
    LabStep(
        number=5,
        title="Farklı ölçeklerde göreli konum",
        note=NoteRef("10.11", objects=("Şekil 10.12",)),
        explanation=(
            "Bir öğrenci A sınavında 78 (sınıf ortalaması 70, standart sapma 4), B sınavında 88 (ortalama 80, "
            "standart sapma 8) almıştır. Ham puanlar farklı ölçeklerdedir; her puan kendi sınavının dağılımında "
            "$z = (x - \\mu)/\\sigma$ ile standartlaştırılır."
        ),
        operations=(
            InlineData("sinavlar", ("sinav", "puan", "ortalama", "std"), EXAMS,
                       "İki sınav: öğrencinin puanı, sınıf ortalaması ve standart sapma"),
            Derive("sinavlar", "z", E.div(E.sub(E.var("puan"), E.var("ortalama")), E.var("std")), "z = (x − μ)/σ"),
            ShowFrame("sinavlar", ("sinav", "puan", "ortalama", "std", "z"), "Ham puan ve göreli konum"),
            BarChart("sinavlar", "z", "Sınav", "z-skoru", "Göreli konum: kendi sınavında kaç standart sapma yukarıda",
                     x="sinav", decimals=0),
        ),
        checks=(
            Check("z_A = (78 − 70)/4", CellTarget("sinavlar", "z", 1), 2, 0),
            Check("z_B = (88 − 80)/8", CellTarget("sinavlar", "z", 2), 1, 0),
        ),
        takeaway=(
            "Ham puan B'de daha yüksektir (88 > 78), ama öğrenci A sınavında ortalamanın 2, B sınavında 1 standart "
            "sapma üzerindedir: kendi sınıfına göre A'daki performans daha sıra dışıdır. Farklı ölçekler ham farkla "
            "değil z-skoruyla karşılaştırılır (§10.11)."
        ),
    ),
    LabStep(
        number=6,
        title="Standartlaştırma alanı değiştirmez",
        note=NoteRef("10.12", objects=("Şekil 10.13", "(10.10)")),
        explanation=(
            "$X \\sim N(70, 10^2)$ için 60–80 aralığının uçları $z_1 = (60 - 70)/10 = -1$ ve "
            "$z_2 = (80 - 70)/10 = 1$'dir. Standart ölçekte $-1$–$1$ aralığı 0,001 genişliğinde dikdörtgenlere "
            "bölünür (özgün ölçekteki 0,01'lik dikdörtgenlerin karşılığı) ve alan Adım 3'teki gibi toplanır: "
            "$P(60 \\leq X \\leq 80) = P(-1 \\leq Z \\leq 1)$ (Denklem 10.10)."
        ),
        operations=(
            Scalar("z_alt", _z(60, EXAM_MEAN, EXAM_SD), "z₁ = (60 − 70)/10", decimals=0),
            Scalar("z_ust", _z(80, EXAM_MEAN, EXAM_SD), "z₂ = (80 − 70)/10", decimals=0),
            Rectangles("zizgara", "z", -1, 1, WIDTH / EXAM_SD, "Standart ölçek: −1–1 aralığı 0,001 genişliğinde "
                                                              "dikdörtgenlere"),
            Derive("zizgara", "f", E.dnorm(E.var("z"), 0, 1), "Standart normal yoğunluk f(z)"),
            Derive("zizgara", "alan", E.mul(E.var("f"), WIDTH / EXAM_SD), "Dikdörtgenin alanı f(z) × 0,001"),
            Statistic("zizgara", "alan", "sum", "alan_z", "P(−1 ≤ Z ≤ 1)", decimals=4),
            Scalar("alan_farki", E.absolute(E.sub(E.ref("alan_z"), E.ref("alan_bir"))),
                   "|Standart ölçekteki alan − özgün ölçekteki alan (Adım 3)|", decimals=6),
            DensityPlot("normal", 0, 1, (-4, 4), "Standart ölçek: −1–1 aralığının alanı", "z", y_label="f(z)",
                        shade=((-1, 1),)),
        ),
        checks=(
            _scalar("z_alt", -1, "z₁", 0),
            _scalar("z_ust", 1, "z₂", 0),
            _scalar("alan_z", 0.683, "P(−1 ≤ Z ≤ 1)", 3),
        ),
        takeaway=(
            "İki ölçekteki alan aynıdır (fark bilgisayarın yuvarlama hatası düzeyindedir): standartlaştırma yalnız "
            "yatay eksenin birimini değiştirir, olasılığı değiştirmez. Bütün normal dağılımlar ortak N(0, 1) "
            "ölçeğine taşınabildiği için Konu 11'de tek bir Φ tablosu yeterli olacaktır (§10.12)."
        ),
        code_note=(
            "Özgün ölçekte 0,01 genişliğindeki bir dikdörtgen standart ölçekte 0,01/10 = 0,001 genişliğindedir; "
            "yoğunluk da σ = 10 kat büyür. Bu yüzden iki toplam aynı sayıyı verir."
        ),
    ),
    LabStep(
        number=7,
        title="Bütünleştirici uygulama: dolum miktarı",
        note=NoteRef("10.14", objects=("Şekil 10.15",)),
        explanation=(
            "Bir içecek işletmesinde şişe dolum miktarı yaklaşık normal dağılsın: $X \\sim N(500, 10^2)$ ml. 510 ml "
            "ve 480 ml'nin $z$ değerleri ile ampirik kurala göre dolumların yaklaşık %95,4'ünün bulunduğu $\\mu \\pm "
            "2\\sigma$ aralığı hesaplanır; aralığın alanı dikdörtgenlerle doğrulanır."
        ),
        operations=(
            Scalar("z_510", _z(510, FILL_MEAN, FILL_SD), "510 ml: z = (510 − 500)/10", decimals=0),
            Scalar("z_480", _z(480, FILL_MEAN, FILL_SD), "480 ml: z = (480 − 500)/10", decimals=0),
            Scalar("dolum_alt", E.sub(FILL_MEAN, E.mul(2, FILL_SD)), "μ − 2σ", decimals=0),
            Scalar("dolum_ust", E.add(FILL_MEAN, E.mul(2, FILL_SD)), "μ + 2σ", decimals=0),
            Rectangles("dolum", "x", 480, 520, WIDTH, "480–520 ml aralığı 0,01 genişliğinde dikdörtgenlere"),
            Derive("dolum", "f", E.dnorm(E.var("x"), FILL_MEAN, FILL_SD), "Dikdörtgenin yüksekliği f(x)"),
            Derive("dolum", "alan", E.mul(E.var("f"), WIDTH), "Dikdörtgenin alanı f(x) × 0,01"),
            Statistic("dolum", "alan", "sum", "alan_dolum", "P(480 ≤ X ≤ 520)", decimals=4),
            DensityPlot("normal", FILL_MEAN, FILL_SD, (460, 540), "Dolum miktarı: μ ± 2σ ve z konumları",
                        "Dolum miktarı (ml)", shade=((480, 520),),
                        references=((480, "480 ml: z = −2"), (510, "510 ml: z = 1"))),
        ),
        checks=(
            _scalar("z_510", 1, "z(510)", 0),
            _scalar("z_480", -2, "z(480)", 0),
            _scalar("dolum_alt", 480, "μ − 2σ", 0),
            _scalar("dolum_ust", 520, "μ + 2σ", 0),
            _scalar("alan_dolum", 0.954, "P(480 ≤ X ≤ 520): yaklaşık %95,4", 3),
        ),
        takeaway=(
            "510 ml ortalamanın bir standart sapma üzerinde, 480 ml iki standart sapma altındadır. Dolumların yaklaşık "
            "%95,4'ü 480–520 ml aralığındadır. Tek bir değerin olasılığı sıfırdır: P(X = 500) = 0; simetri nedeniyle "
            "P(X < 500) = 0,50 (§10.14)."
        ),
    ),
)

KONU10_LAB = LabSpec(
    topic_key="konu10",
    title="Sürekli dağılımlarda alanı, normal eğriyi ve z-dönüşümünü uygulamak",
    note_section="10",
    steps=STEPS,
    labels=(
        ("x", "x"),
        ("z", "z"),
        ("f", "f"),
        ("alan", "Alan"),
        ("sinav", "Sınav"),
        ("puan", "Puan x"),
        ("ortalama", "Ortalama μ"),
        ("std", "Standart sapma σ"),
    ),
)
