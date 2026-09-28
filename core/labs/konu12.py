"""Konu 12 uygulaması: örneklem ortalamasının ve oranının örnekleme dağılımı, standart hata, sonlu anakütle
düzeltmesi.

Ders notlarının çözümlü örnekleri: §12.6 (σ = 15; Şekil 12.6), §12.7 (σ = 20; Tablo 12.2, Şekil 12.7), §12.9 (dolum
ortalaması; Şekil 12.9), §12.10 (p = 0,40; Şekil 12.10), §12.11 (N = 400, n = 100, σ = 20; Şekil 12.11) ve §12.15
(bütünleştirici uygulama). Buradaki her ``Check`` notlarda basılı bir sayıdır. §12.1–12.5, §12.13 ve §12.14
kavramsaldır. Merkezi Limit Teoremi (§12.8, Şekil 12.8) ve tutarlılık (§12.12, Şekil 12.13) Sezgi sekmesindeki
Deney 2 ve Deney 1'dir: örneklem ortalamasının davranışı tekrarlı örneklemeyle görülür.
"""

from __future__ import annotations

from core.labs import expr as E
from core.labs.spec import (
    BarChart,
    CellTarget,
    Check,
    DensityCompare,
    DensityPlot,
    Derive,
    InlineData,
    LabSpec,
    LabStep,
    LineChart,
    NoteRef,
    Scalar,
    ScalarTable,
    ScalarTarget,
    ShowFrame,
    Support,
)


def _scalar(name: str, expected: float, label: str, decimals: int) -> Check:
    return Check(label, ScalarTarget(name), expected, decimals)


def _table(z) -> E.Expr:
    """Tablo değeri: Φ(z) dört ondalık basamağa yuvarlanır (Konu 11'deki standart normal tablo)."""

    return E.roundto(E.normcdf(z), 4)


STEPS = (
    LabStep(
        number=1,
        title="Örneklem ortalaması: aynı merkez, daha dar dağılım",
        note=NoteRef("12.6", objects=("Şekil 12.6", "(12.2)", "(12.3)")),
        explanation=(
            "Anakütle ortalaması $\\mu = 50$, standart sapması $\\sigma = 15$ olsun. Basit rassal örneklemlerde "
            "$E(\\bar X) = \\mu$ (Denklem 12.2) ve $\\sigma_{\\bar X} = \\sigma/\\sqrt n$'dir (Denklem 12.3); "
            "$\\sigma_{\\bar X}$ ortalamanın standart hatasıdır. Şekil 12.6'daki gibi $X$ ile $n = 4$ ve $n = 25$ "
            "için $\\bar X$'in normal dağılımları aynı eksende çizilir."
        ),
        operations=(
            Scalar("se_4", E.div(15, E.sqrt(4)), "σ_X̄ = 15/√4", decimals=1),
            Scalar("se_25", E.div(15, E.sqrt(25)), "σ_X̄ = 15/√25", decimals=0),
            DensityCompare(
                (
                    ("normal", 50, 15, "Bireysel X: σ = 15"),
                    ("normal", 50, "se_4", "X̄, n = 4: SH = 7,5"),
                    ("normal", 50, "se_25", "X̄, n = 25: SH = 3"),
                ),
                (20, 80), "Örneklem ortalamasının aynı merkezde daha dar dağılımı", "Değer", y_label="Yoğunluk",
            ),
        ),
        checks=(
            _scalar("se_4", 7.5, "Standart hata, n = 4", 1),
            _scalar("se_25", 3, "Standart hata, n = 25", 0),
        ),
        takeaway=(
            "Bütün eğrilerin merkezi 50'dir; değişen unsur yayılımdır. n = 4'te standart hata 7,5, n = 25'te 3'tür: "
            "n büyüdükçe olası örneklem ortalamaları μ çevresinde daha sık toplanır. Standart hata bireysel "
            "gözlemlerin standart sapması değil, örneklem ortalamalarının standart sapmasıdır (§12.6)."
        ),
    ),
    LabStep(
        number=2,
        title="Örneklem büyüklüğü ve kesinlik",
        note=NoteRef("12.7", objects=("Tablo 12.2", "Şekil 12.7")),
        explanation=(
            "$\\sigma = 20$ için standart hata $20/\\sqrt n$'dir. $n$ paydada karekök içinde olduğu için örneklem "
            "büyüklüğünü iki katına çıkarmak standart hatayı yarıya indirmez; yarıya indirmek için $n$ yaklaşık dört "
            "katına çıkarılmalıdır."
        ),
        operations=(
            InlineData("se_tablo", ("n",), ((4,), (25,), (100,), (400,)), "Tablo 12.2'nin örneklem büyüklükleri"),
            Derive("se_tablo", "kok_n", E.sqrt(E.var("n")), "√n"),
            Derive("se_tablo", "se", E.div(20, E.var("kok_n")), "σ_X̄ = 20/√n"),
            ShowFrame("se_tablo", ("n", "kok_n", "se"), "Tablo 12.2: σ = 20 için örneklem büyüklüğü ve standart hata"),
            Support("se_egri", "n", 1, 400, "n = 1, 2, …, 400"),
            Derive("se_egri", "se", E.div(20, E.sqrt(E.var("n"))), "σ_X̄ = 20/√n"),
            LineChart("se_egri", "n", "se", "Örneklem büyüklüğü n", "Standart hata σ/√n",
                      "σ = 20 iken örneklem büyüklüğü arttıkça standart hatanın azalması", markers=False),
        ),
        checks=(
            Check("Tablo 12.2: n = 4", CellTarget("se_tablo", "se", 1), 10, 0),
            Check("Tablo 12.2: n = 25", CellTarget("se_tablo", "se", 2), 4, 0),
            Check("Tablo 12.2: n = 100", CellTarget("se_tablo", "se", 3), 2, 0),
            Check("Tablo 12.2: n = 400", CellTarget("se_tablo", "se", 4), 1, 0),
        ),
        takeaway=(
            "n 4'ten 400'e çıkınca standart hata 10'dan 1'e iner; her dört katlık artış standart hatayı yarıya "
            "indirir. Eğri başta hızlı, sonra yavaş düşer: azalan marjinal kazanç. Büyük n örnekleme belirsizliğini "
            "azaltır, ama sistematik ölçüm veya kapsama hatasını düzeltmez (§12.7)."
        ),
    ),
    LabStep(
        number=3,
        title="Örneklem ortalamasıyla olasılık: dolum miktarı",
        note=NoteRef("12.9", objects=("Şekil 12.9", "(12.5)")),
        explanation=(
            "Dolum miktarının anakütle ortalaması $\\mu = 500$ ml, standart sapması $\\sigma = 60$ ml; örneklem "
            "büyüklüğü $n = 36$. Örnekleme dağılımı normal ya da yaklaşık normal olduğunda "
            "$Z = (\\bar X - \\mu)/(\\sigma/\\sqrt n)$'dir (Denklem 12.5): paydada $\\sigma$ değil standart hata "
            "vardır. Φ değerleri Konu 11'deki tablodan okunur."
        ),
        operations=(
            Scalar("se_dolum", E.div(60, E.sqrt(36)), "σ_X̄ = 60/√36", decimals=0),
            Scalar("z_490", E.div(E.sub(490, 500), E.ref("se_dolum")), "x̄ = 490: z = (490 − 500)/10", decimals=0),
            Scalar("z_510", E.div(E.sub(510, 500), E.ref("se_dolum")), "x̄ = 510: z = (510 − 500)/10", decimals=0),
            Scalar("P_dolum", E.sub(_table(E.ref("z_510")), _table(E.ref("z_490"))),
                   "P(490 ≤ X̄ ≤ 510) = Φ(1) − Φ(−1)", decimals=4),
            DensityPlot("normal", 500, 10, (465, 535), "n = 36: örneklem ortalamasının 490–510 ml aralığında olması",
                        "Örneklem ortalaması x̄ (ml)", y_label="Yoğunluk", shade=((490, 510),)),
        ),
        checks=(
            _scalar("se_dolum", 10, "σ_X̄", 0),
            _scalar("z_490", -1, "z(490)", 0),
            _scalar("z_510", 1, "z(510)", 0),
            _scalar("P_dolum", 0.6826, "P(490 ≤ X̄ ≤ 510)", 4),
        ),
        takeaway=(
            "36 ürünün ortalamasının 490–510 ml arasında olma olasılığı yaklaşık 0,6826'dır. Tek bir ürünün aynı "
            "aralıkta olması başka bir olaydır: bireysel X için standart sapma 60 ml, X̄ için 10 ml'dir (§12.9)."
        ),
    ),
    LabStep(
        number=4,
        title="Örneklem oranının örnekleme dağılımı",
        note=NoteRef("12.10", objects=("Şekil 12.10", "(12.7)", "(12.8)")),
        explanation=(
            "Anakütle oranı $p = 0{,}40$ olsun. Örneklem oranı $\\hat p = x/n$ için $E(\\hat p) = p$ (Denklem 12.7) "
            "ve $\\sigma_{\\hat p} = \\sqrt{p(1 - p)/n}$'dir (Denklem 12.8). $np \\geq 5$ ve $n(1 - p) \\geq 5$ "
            "sağlandığında dağılım yaklaşık normaldir. $n = 25$ ve $n = 100$ karşılaştırılır."
        ),
        operations=(
            Scalar("se_p25", E.sqrt(E.div(E.mul(0.4, 0.6), 25)), "σ_p̂ = √(0,40 × 0,60/25)", decimals=3),
            Scalar("se_p100", E.sqrt(E.div(E.mul(0.4, 0.6), 100)), "σ_p̂ = √(0,40 × 0,60/100)", decimals=3),
            DensityCompare(
                (
                    ("normal", 0.4, "se_p25", "n = 25: SH ≈ 0,098"),
                    ("normal", 0.4, "se_p100", "n = 100: SH ≈ 0,049"),
                ),
                (0.05, 0.75), "p = 0,40: örneklem büyüdükçe p̂ dağılımının daralması", "Örneklem oranı p̂",
                y_label="Yoğunluk",
            ),
        ),
        checks=(
            _scalar("se_p25", 0.098, "σ_p̂, n = 25", 3),
            _scalar("se_p100", 0.049, "σ_p̂, n = 100", 3),
        ),
        takeaway=(
            "İki dağılımın merkezi 0,40'tır; n dört katına çıkınca standart hata 0,098'den 0,049'a, yani yarıya iner. "
            "n = 25 için np = 10 ve n(1 − p) = 15, n = 100 için 40 ve 60: normal yaklaşım koşulları iki durumda da "
            "sağlanır (§12.10)."
        ),
    ),
    LabStep(
        number=5,
        title="Sonlu anakütle düzeltmesi",
        note=NoteRef("12.11", objects=("Şekil 12.11", "(12.4)")),
        explanation=(
            "Sonlu bir anakütleden yerine koymadan örnekleme yapılırken $n/N > 0{,}05$ ise standart hata "
            "$\\sqrt{(N - n)/(N - 1)}$ çarpanıyla düzeltilir (Denklem 12.4). Örnek: $N = 400$, $n = 100$, "
            "$\\sigma = 20$; örnekleme oranı $100/400 = 0{,}25$."
        ),
        operations=(
            Scalar("se_sonsuz", E.div(20, E.sqrt(100)), "Düzeltmesiz σ/√n = 20/√100", decimals=0),
            Scalar("fpc", E.sqrt(E.div(E.sub(400, 100), E.sub(400, 1))), "√((N − n)/(N − 1)) = √(300/399)",
                   decimals=3),
            Scalar("se_sonlu", E.mul(E.ref("fpc"), E.ref("se_sonsuz")), "Düzeltilmiş standart hata", decimals=2),
            ScalarTable((("Düzeltmesiz", E.ref("se_sonsuz")), ("Sonlu anakütle", E.ref("se_sonlu"))), "fpc_tablo",
                        decimals=2),
            BarChart("fpc_tablo", "deger", "Standart hata hesabı", "Standart hata",
                     "N = 400, n = 100, σ = 20: sonlu anakütle düzeltmesinin etkisi", decimals=2),
        ),
        checks=(
            _scalar("se_sonsuz", 2, "Düzeltmesiz standart hata", 0),
            _scalar("fpc", 0.867, "Düzeltme faktörü", 3),
            _scalar("se_sonlu", 1.73, "Düzeltilmiş standart hata", 2),
        ),
        takeaway=(
            "Anakütlenin dörtte birini gözlediğimiz için geride kalan belirsizlik azalır: standart hata 2'den 1,73'e "
            "iner. Düzeltme faktörü 1'den büyük olamaz; n/N çok küçükse 1'e yaklaşır ve iki standart hata neredeyse "
            "aynıdır (§12.11)."
        ),
    ),
    LabStep(
        number=6,
        title="Bütünleştirici uygulama: harcama ve memnuniyet",
        note=NoteRef("12.15", objects=("Şekil 12.16",)),
        explanation=(
            "Bir perakende işletmesinde işlem başına harcamanın anakütle ortalaması $\\mu = 600$ TL, standart sapması "
            "$\\sigma = 120$ TL, memnun müşteri oranı $p = 0{,}64$'tür. İşletme her ay $n = 100$ müşterilik basit "
            "rassal örneklem seçer. Ortalama harcama ve memnuniyet oranının örnekleme dağılımlarının merkezi ve "
            "standart hatası hesaplanır."
        ),
        operations=(
            Scalar("se_harcama", E.div(120, E.sqrt(100)), "σ_X̄ = 120/√100", decimals=0),
            Scalar("se_memnun", E.sqrt(E.div(E.mul(0.64, 0.36), 100)), "σ_p̂ = √(0,64 × 0,36/100)", decimals=3),
            Scalar("np_m", E.mul(100, 0.64), "np = 100 × 0,64", decimals=0),
            Scalar("nq_m", E.mul(100, 0.36), "n(1 − p) = 100 × 0,36", decimals=0),
            DensityPlot("normal", 600, 12, (552, 648), "n = 100: ortalama harcamanın örnekleme dağılımı",
                        "Örneklem ortalaması x̄ (TL)", y_label="Yoğunluk", references=((600, "μ = 600 TL"),)),
        ),
        checks=(
            _scalar("se_harcama", 12, "σ_X̄", 0),
            _scalar("se_memnun", 0.048, "σ_p̂", 3),
            _scalar("np_m", 64, "np", 0),
            _scalar("nq_m", 36, "n(1 − p)", 0),
        ),
        takeaway=(
            "Aylık örneklem ortalaması 600 TL çevresinde 12 TL standart hatayla, memnuniyet oranı 0,64 çevresinde "
            "0,048 standart hatayla dağılır; np = 64 ve n(1 − p) = 36 olduğu için p̂ yaklaşık normaldir. Standart hata "
            "ikinci dönemde güven aralığı ve hipotez testinin temel ölçüsüdür (§12.15)."
        ),
    ),
)

KONU12_LAB = LabSpec(
    topic_key="konu12",
    title="Örnekleme dağılımlarını, standart hatayı ve sonlu anakütle düzeltmesini uygulamak",
    note_section="12",
    steps=STEPS,
    labels=(
        ("n", "n"),
        ("kok_n", "√n"),
        ("se", "Standart hata σ/√n"),
        ("deger", "Standart hata"),
    ),
)
