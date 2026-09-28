"""Konu 11 uygulaması: normal olasılıklar, ters normal, binomun normal yaklaştırması ve üstel dağılım.

Ders notlarının çözümlü örnekleri: §11.1 (Tablo 11.1, Şekil 11.1), §11.2 (sol kuyruk ve simetri), §11.3 (sağ kuyruk
ve iki değer arası), §11.4 (özgün ölçek, N(70, 10²)), §11.5 (Tablo 11.2 ve üst %10 eşiği), §11.7 (Şekil 11.7),
§11.8.1 (tam 12 hatalı fatura), §11.10 (üstel dağılım, μ = 15), §11.11 (Poisson–üstel bağlantısı) ve §11.13
(bütünleştirici uygulama). Buradaki her ``Check`` notlarda basılı bir sayıdır. §11.6, §11.9 ve §11.12 kavramsaldır.

Tablo kuralı: notlar Φ değerlerini standart normal tablodan okur. Tablo, z'yi iki ondalık basamağa, Φ(z)'yi dört
ondalık basamağa yuvarlar; uygulama da aynı yuvarlamayı yapar (ör. 0,8944 − 0,3085 = 0,5859). Yuvarlamasız sonuç
ayrıca gösterilir.
"""

from __future__ import annotations

from core.labs import expr as E
from core.labs.spec import (
    CellTarget,
    Check,
    DensityPlot,
    Derive,
    InlineData,
    LabSpec,
    LabStep,
    NoteRef,
    PmfWithDensity,
    Scalar,
    ScalarTarget,
    ShowFrame,
    Support,
)

EXAM_MEAN, EXAM_SD = 70, 10
"""§11.4 ve §11.5: sınav puanları X ~ N(70, 10²)."""
PERCENTILES = (0.025, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95)
"""Tablo 11.2'nin sol kümülatif olasılıkları."""
TABLE_ROWS = (0.5, 1.0, 1.2, 1.5)
"""Tablo 11.1'in satırları; sütunlar 0,00–0,05."""


def _scalar(name: str, expected: float, label: str, decimals: int) -> Check:
    return Check(label, ScalarTarget(name), expected, decimals)


def _table(z) -> E.Expr:
    """Tablo değeri: Φ(z) dört ondalık basamağa yuvarlanır (notlardaki standart normal tablo)."""

    return E.roundto(E.normcdf(z), 4)


def _z(x: float, mean: float, sd: float) -> E.Expr:
    return E.div(E.sub(x, mean), sd)


def _column(offset: int) -> Derive:
    z = E.var("z_satir") if offset == 0 else E.add(E.var("z_satir"), offset / 100)
    return Derive("ztablo", f"s0{offset}", _table(z), f"Sütun 0,0{offset}: Φ(z), dört basamak")


STEPS = (
    LabStep(
        number=1,
        title="Standart normal tablo: Φ(z) = P(Z ≤ z)",
        note=NoteRef("11.1", objects=("Tablo 11.1", "Şekil 11.1", "(11.1)")),
        explanation=(
            "$Z \\sim N(0, 1)$ için $\\Phi(z) = P(Z \\leq z)$, $z$'nin solunda kalan kümülatif alandır (Denklem 11.1). "
            "Tablonun satırı $z$'nin birler basamağı ve ilk ondalığı, sütunu ikinci ondalığıdır: $z = 1{,}25$ için "
            "satır 1,2, sütun 0,05. Tablo 11.1 aşağıda Φ fonksiyonuyla kurulur; değerler tablodaki gibi dört "
            "ondalık basamağa yuvarlanır."
        ),
        operations=(
            InlineData("ztablo", ("z_satir",), tuple((value,) for value in TABLE_ROWS),
                       "Tablo 11.1'in satırları: z'nin birler basamağı ve ilk ondalığı"),
            *(_column(offset) for offset in range(6)),
            ShowFrame("ztablo", ("z_satir", *(f"s0{offset}" for offset in range(6))),
                      "Tablo 11.1: standart normal kümülatif tablo kesiti"),
            Scalar("Phi_1", _table(1), "Φ(1,00): satır 1,0, sütun 0,00", decimals=4),
            Scalar("Phi_125", _table(1.25), "Φ(1,25): satır 1,2, sütun 0,05", decimals=4),
            DensityPlot("normal", 0, 1, (-3.8, 3.8), "Φ(1) = P(Z ≤ 1): 1'in solundaki alan", "z", y_label="φ(z)",
                        shade=((-3.8, 1),)),
        ),
        checks=(
            _scalar("Phi_1", 0.8413, "Φ(1,00)", 4),
            _scalar("Phi_125", 0.8944, "Φ(1,25)", 4),
            Check("Tablo 11.1: satır 0,5, sütun 0,00", CellTarget("ztablo", "s00", 1), 0.6915, 4),
            Check("Tablo 11.1: satır 1,0, sütun 0,02", CellTarget("ztablo", "s02", 2), 0.8461, 4),
            Check("Tablo 11.1: satır 1,5, sütun 0,03", CellTarget("ztablo", "s03", 4), 0.9370, 4),
        ),
        takeaway=(
            "Φ(1,00) = 0,8413: standart normal bir değişkenin 1'in altında kalma olasılığı yaklaşık %84,13'tür. "
            "Φ(z) bir olasılıktır (alan); z ise konumdur. Bazı tablolar 0 ile z arasındaki alanı ya da kuyruk "
            "alanını verir; bu derste temel tablo sol kümülatif alandır (§11.1)."
        ),
    ),
    LabStep(
        number=2,
        title="Sol kuyruk ve simetri",
        note=NoteRef("11.2", objects=("Şekil 11.2", "(11.2)", "(11.3)")),
        explanation=(
            "Sol kuyruk olasılığı doğrudan tablodan okunur: $P(Z \\leq z_0) = \\Phi(z_0)$ (Denklem 11.2). Negatif "
            "$z$ için simetri kullanılır: $\\Phi(-z) = 1 - \\Phi(z)$ (Denklem 11.3)."
        ),
        operations=(
            Scalar("P_sol_15", _table(1.5), "P(Z ≤ 1,50) = Φ(1,50)", decimals=4),
            Scalar("Phi_eksi_1", E.sub(1, E.ref("Phi_1")), "Φ(−1,00) = 1 − Φ(1,00): simetri", decimals=4),
            Scalar("Phi_eksi_1_dogrudan", _table(E.neg(1)), "Φ(−1,00): Φ fonksiyonundan doğrudan", decimals=4),
            DensityPlot("normal", 0, 1, (-3.8, 3.8), "Sol kuyruk: P(Z ≤ 1,5)", "z", y_label="φ(z)",
                        shade=((-3.8, 1.5),)),
        ),
        checks=(
            _scalar("P_sol_15", 0.9332, "P(Z ≤ 1,50)", 4),
            _scalar("Phi_eksi_1", 0.1587, "Φ(−1,00) = 1 − 0,8413", 4),
            _scalar("Phi_eksi_1_dogrudan", 0.1587, "Φ(−1,00)", 4),
        ),
        takeaway=(
            "P(Z ≤ 1,50) = 0,9332. Eğri 0 çevresinde simetrik olduğu için −1'in solundaki alan 1'in sağındaki alana "
            "eşittir: Φ(−1) = 1 − 0,8413 = 0,1587. Negatif z için sol alan 0,50'den küçüktür (§11.2)."
        ),
    ),
    LabStep(
        number=3,
        title="Sağ kuyruk ve iki değer arası",
        note=NoteRef("11.3", objects=("Şekil 11.3", "(11.4)", "(11.5)")),
        explanation=(
            "Tablo sol alanı verdiği için sağ kuyrukta tümleyen kullanılır: $P(Z > z_0) = 1 - \\Phi(z_0)$ "
            "(Denklem 11.4). İki değer arasındaki alan iki sol alanın farkıdır: "
            "$P(a \\leq Z \\leq b) = \\Phi(b) - \\Phi(a)$ (Denklem 11.5)."
        ),
        operations=(
            Scalar("P_sag_1", E.sub(1, E.ref("Phi_1")), "P(Z > 1) = 1 − Φ(1)", decimals=4),
            Scalar("Phi_eksi_05", _table(E.neg(0.5)), "Φ(−0,50)", decimals=4),
            Scalar("P_arasi", E.sub(E.ref("Phi_125"), E.ref("Phi_eksi_05")),
                   "P(−0,50 ≤ Z ≤ 1,25) = Φ(1,25) − Φ(−0,50)", decimals=4),
            Scalar("P_arasi_yuvarlamasiz", E.sub(E.normcdf(1.25), E.normcdf(E.neg(0.5))),
                   "Aynı alan, yuvarlanmamış Φ değerleriyle", decimals=4),
            DensityPlot("normal", 0, 1, (-3.8, 3.8), "İki değer arası: P(−0,5 ≤ Z ≤ 1,25)", "z", y_label="φ(z)",
                        shade=((-0.5, 1.25),)),
        ),
        checks=(
            _scalar("P_sag_1", 0.1587, "P(Z > 1)", 4),
            _scalar("Phi_eksi_05", 0.3085, "Φ(−0,50)", 4),
            _scalar("P_arasi", 0.5859, "P(−0,50 ≤ Z ≤ 1,25) = 0,8944 − 0,3085", 4),
        ),
        takeaway=(
            "Büyük sol alandan küçük sol alan çıkarılınca aradaki şerit kalır: 0,8944 − 0,3085 = 0,5859. "
            "Yuvarlanmamış Φ değerleriyle sonuç 0,5858'dir; fark tablonun dört basamağa yuvarlanmasından gelir. "
            "Sürekli dağılımda < ile ≤ aynı olasılığı verir, çünkü tek bir noktanın olasılığı sıfırdır (§11.3)."
        ),
    ),
    LabStep(
        number=4,
        title="Özgün ölçekte normal olasılık",
        note=NoteRef("11.4", objects=("Şekil 11.4",)),
        explanation=(
            "Sınav puanları $X \\sim N(70, 10^2)$ olsun. Dört adım: istenen alanı belirle, sınırları "
            "$z = (x - \\mu)/\\sigma$ ile standartlaştır, $\\Phi(z)$ değerlerini bul, sol / sağ / aralık işlemini "
            "tamamla."
        ),
        operations=(
            Scalar("z_85", _z(85, EXAM_MEAN, EXAM_SD), "x = 85: z = (85 − 70)/10", decimals=1),
            Scalar("P_85_alti", _table(E.ref("z_85")), "P(X ≤ 85) = Φ(1,5)", decimals=4),
            Scalar("P_85_ustu", E.sub(1, E.ref("P_85_alti")), "P(X > 85) = 1 − Φ(1,5)", decimals=4),
            Scalar("z_60", _z(60, EXAM_MEAN, EXAM_SD), "x = 60: z = (60 − 70)/10", decimals=0),
            Scalar("z_80", _z(80, EXAM_MEAN, EXAM_SD), "x = 80: z = (80 − 70)/10", decimals=0),
            Scalar("P_60_80", E.sub(_table(E.ref("z_80")), _table(E.ref("z_60"))),
                   "P(60 ≤ X ≤ 80) = Φ(1) − Φ(−1)", decimals=4),
            DensityPlot("normal", EXAM_MEAN, EXAM_SD, (30, 110), "N(70, 10²): 60–80 aralığının alanı ve x = 85",
                        "Sınav puanı", shade=((60, 80),), references=((85, "x = 85: z = 1,5"),)),
        ),
        checks=(
            _scalar("z_85", 1.5, "z(85)", 1),
            _scalar("P_85_alti", 0.9332, "P(X ≤ 85)", 4),
            _scalar("P_85_ustu", 0.0668, "P(X > 85)", 4),
            _scalar("P_60_80", 0.6826, "P(60 ≤ X ≤ 80) = 0,8413 − 0,1587", 4),
        ),
        takeaway=(
            "Puanın 85 veya daha düşük olma olasılığı 0,9332, 85'in üzerinde olma olasılığı 0,0668'dir; aynı z değeri "
            "sorunun yönüne göre farklı alan işlemi gerektirir. İki ham sınır için iki ayrı z hesaplanır: "
            "P(60 ≤ X ≤ 80) = 0,6826. z bulmak işlemin sonu değildir; olasılık, uygun alanın hesaplanmasıdır (§11.4)."
        ),
    ),
    LabStep(
        number=5,
        title="Ters normal: olasılıktan eşik değere",
        note=NoteRef("11.5", objects=("Tablo 11.2", "Şekil 11.5")),
        explanation=(
            "Bu kez yön tersinedir: olasılık → $z$ → $x$. Solunda $p$ alan bulunan $z$ değeri $\\Phi^{-1}(p)$'dir "
            "(Tablo 11.2). Özgün ölçeğe dönüş $x = \\mu + z\\sigma$'dır. Üst %10'luk gruba giriş eşiğinin solunda "
            "%90 alan vardır."
        ),
        operations=(
            InlineData("yuzdelik", ("p",), tuple((value,) for value in PERCENTILES),
                       "Tablo 11.2'nin sol kümülatif olasılıkları"),
            Derive("yuzdelik", "z", E.roundto(E.norminv(E.var("p")), 3), "z = Φ⁻¹(p), üç ondalık basamak"),
            ShowFrame("yuzdelik", ("p", "z"), "Tablo 11.2: yaygın sol kümülatif olasılıklar ve z değerleri"),
            Scalar("z_90", E.roundto(E.norminv(0.90), 3), "Üst %10: sol alan 0,90 → z", decimals=3),
            Scalar("esik_90", E.add(EXAM_MEAN, E.mul(E.ref("z_90"), EXAM_SD)), "x = μ + zσ = 70 + 1,282 × 10",
                   decimals=2),
            DensityPlot("normal", 0, 1, (-3.6, 3.6), "Üst %10'u ayıran eşik: z = 1,282", "z", y_label="φ(z)",
                        shade=((1.282, 3.6),), references=((1.282, "z = 1,282"),)),
        ),
        checks=(
            Check("Tablo 11.2: p = 0,025", CellTarget("yuzdelik", "z", 1), -1.96, 2),
            Check("Tablo 11.2: p = 0,05", CellTarget("yuzdelik", "z", 2), -1.645, 3),
            Check("Tablo 11.2: p = 0,10", CellTarget("yuzdelik", "z", 3), -1.282, 3),
            Check("Tablo 11.2: p = 0,25", CellTarget("yuzdelik", "z", 4), -0.674, 3),
            Check("Tablo 11.2: p = 0,50", CellTarget("yuzdelik", "z", 5), 0, 3),
            Check("Tablo 11.2: p = 0,75", CellTarget("yuzdelik", "z", 6), 0.674, 3),
            Check("Tablo 11.2: p = 0,90", CellTarget("yuzdelik", "z", 7), 1.282, 3),
            Check("Tablo 11.2: p = 0,95", CellTarget("yuzdelik", "z", 8), 1.645, 3),
            _scalar("esik_90", 82.82, "Üst %10 eşiği", 2),
        ),
        takeaway=(
            "Solunda %90 alan bulunan z yaklaşık 1,282'dir; N(70, 10²) için eşik 70 + 1,282 × 10 = 82,82 puandır: "
            "yaklaşık 82,8'in üzerindeki puanlar en yüksek %10'dadır. z = 0 medyana (50. yüzdeliğe) karşılık gelir "
            "(§11.5)."
        ),
    ),
    LabStep(
        number=6,
        title="Binom dağılımının normal yaklaştırması",
        note=NoteRef("11.7", objects=("Şekil 11.7", "(11.6)")),
        explanation=(
            "$X \\sim \\mathrm{Bin}(n, p)$ için $\\mu = np$ ve $\\sigma = \\sqrt{np(1 - p)}$'dir. Binom dağılımı "
            "yeterince çan biçimine yaklaştığında aynı ortalama ve standart sapmalı normal dağılım yaklaşık model "
            "olur. Pratik koşul: $np \\geq 5$ ve $n(1 - p) \\geq 5$ (Denklem 11.6). Örnek: $n = 20$, $p = 0{,}5$."
        ),
        operations=(
            Scalar("np_20", E.mul(20, 0.5), "np = 20 × 0,5", decimals=0),
            Scalar("nq_20", E.mul(20, E.sub(1, 0.5)), "n(1 − p) = 20 × 0,5", decimals=0),
            Scalar("sigma_20", E.sqrt(E.mul(E.ref("np_20"), E.sub(1, 0.5))), "σ = √(np(1 − p))", decimals=5),
            Support("bin20", "x", 0, 20, "Başarı sayısı x = 0, 1, …, 20"),
            Derive("bin20", "f", E.dbinom(E.var("x"), 20, 0.5), "P(X = x), X ~ Bin(20, 0,5)"),
            Derive("bin20", "g", E.dnorm(E.var("x"), E.ref("np_20"), E.ref("sigma_20")),
                   "Aynı ortalama ve standart sapmalı normal yoğunluk"),
            ShowFrame("bin20", ("x", "f", "g"), "Binom olasılıkları ve normal yoğunluk"),
            PmfWithDensity("bin20", "x", "f", "normal", "np_20", "sigma_20", "Başarı sayısı, x", "Olasılık / yoğunluk",
                           "Bin(20, 0,5) ve aynı ortalama ile standart sapmalı normal eğri",
                           bar_label="Binom: P(X = x)", curve_label="Normal yaklaşım"),
        ),
        checks=(
            _scalar("np_20", 10, "np", 0),
            _scalar("nq_20", 10, "n(1 − p)", 0),
            _scalar("sigma_20", 2.23607, "σ = √5", 5),
            Check("P(X = 10)", CellTarget("bin20", "f", 11), 0.176197, 6),
            Check("Normal eğrinin tepesi f(10)", CellTarget("bin20", "g", 11), 0.17841, 5),
        ),
        takeaway=(
            "np = 10 ≥ 5 ve n(1 − p) = 10 ≥ 5: yaklaşım koşulları sağlanır ve iki şekil birbirine yakındır. Yine de "
            "binom yalnız tam sayılarda olasılık taşır, normal eğri süreklidir; bu yüzden yaklaşık hesapta süreklilik "
            "düzeltmesi gerekir. Yalnız n'in büyük olması yetmez: p sıfıra ya da bire çok yakınsa dağılım çarpık "
            "kalabilir (§11.7)."
        ),
    ),
    LabStep(
        number=7,
        title="Süreklilik düzeltmesi: tam 12 hatalı fatura",
        note=NoteRef("11.8.1", objects=("Şekil 11.8", "Tablo 11.3")),
        explanation=(
            "Faturaların %10'unda hata var ve 100 bağımsız fatura inceleniyor: $X \\sim \\mathrm{Bin}(100, 0{,}10)$. "
            "Normal yaklaşım $Y \\sim N(10, 3^2)$'dir. Binomda $X = 12$ tek bir çubuktur; normal eğride tek noktanın "
            "alanı sıfırdır. Çubuk $0{,}5$ birim genişletilir: $P(X = 12) \\approx P(11{,}5 < Y < 12{,}5)$. "
            "Sınırlar standartlaştırılıp tablodan okunur (z iki basamak, Φ dört basamak)."
        ),
        operations=(
            Scalar("np_f", E.mul(100, 0.10), "np = 100 × 0,10", decimals=0),
            Scalar("nq_f", E.mul(100, 0.90), "n(1 − p) = 100 × 0,90", decimals=0),
            Scalar("sigma_f", E.sqrt(E.mul(E.ref("np_f"), 0.90)), "σ = √(np(1 − p))", decimals=0),
            Scalar("z1_f", E.roundto(_z(11.5, E.ref("np_f"), E.ref("sigma_f")), 2), "z₁ = (11,5 − 10)/3", decimals=2),
            Scalar("z2_f", E.roundto(_z(12.5, E.ref("np_f"), E.ref("sigma_f")), 2), "z₂ = (12,5 − 10)/3 ≈ 0,83",
                   decimals=2),
            Scalar("Phi_z1", _table(E.ref("z1_f")), "Φ(0,50)", decimals=4),
            Scalar("Phi_z2", _table(E.ref("z2_f")), "Φ(0,83)", decimals=4),
            Scalar("P_12_yaklasik", E.sub(E.ref("Phi_z2"), E.ref("Phi_z1")), "P(X = 12) ≈ Φ(0,83) − Φ(0,50)",
                   decimals=4),
            Scalar("P_12_yuvarlamasiz",
                   E.sub(E.normcdf(_z(12.5, E.ref("np_f"), E.ref("sigma_f"))),
                         E.normcdf(_z(11.5, E.ref("np_f"), E.ref("sigma_f")))),
                   "Aynı yaklaşım, yuvarlanmamış z ile", decimals=4),
            Scalar("P_12_binom", E.dbinom(12, 100, 0.10), "Tam binom olasılığı P(X = 12)", decimals=4),
            Support("bin100", "x", 0, 25, "Hatalı fatura sayısı x = 0, 1, …, 25 (P(X > 25) çok küçük)"),
            Derive("bin100", "f", E.dbinom(E.var("x"), 100, 0.10), "P(X = x), X ~ Bin(100, 0,10)"),
            PmfWithDensity("bin100", "x", "f", "normal", "np_f", "sigma_f", "Hatalı fatura sayısı, x",
                           "Olasılık / yoğunluk",
                           "X = 12'nin normal yaklaşımdaki karşılığı: 11,5–12,5 aralığının alanı",
                           bar_label="Binom: P(X = x)", curve_label="Normal yaklaşım N(10, 3²)",
                           shade=((11.5, 12.5),)),
        ),
        checks=(
            _scalar("np_f", 10, "np", 0),
            _scalar("nq_f", 90, "n(1 − p)", 0),
            _scalar("sigma_f", 3, "σ", 0),
            _scalar("z1_f", 0.50, "z₁", 2),
            _scalar("z2_f", 0.83, "z₂", 2),
            _scalar("Phi_z1", 0.6915, "Φ(0,50)", 4),
            _scalar("Phi_z2", 0.7967, "Φ(0,83)", 4),
            _scalar("P_12_yaklasik", 0.1052, "P(X = 12) ≈ 0,7967 − 0,6915", 4),
        ),
        takeaway=(
            "Tablo değerleriyle yaklaşık olasılık 0,1052'dir. Yuvarlanmamış z₂ = 0,8333 ile sonuç 0,1062, tam binom "
            "olasılığı 0,0988'dir: sonuç yaklaşıktır. Süreklilik düzeltmesinin yönünü ezberlemek yerine olayın "
            "kapsadığı tam sayı çubuklarının dış kenarlarını 0,5 genişletin (§11.8, Tablo 11.3)."
        ),
        code_note=(
            "Tablo kuralı kodda roundto ile yazılır: z iki, Φ(z) dört ondalık basamağa yuvarlanır (Python np.round, "
            "R round)."
        ),
    ),
    LabStep(
        number=8,
        title="Üstel dağılım: bekleme ve tamamlanma süreleri",
        note=NoteRef("11.10", objects=("Şekil 11.10", "(11.8)", "(11.9)", "(11.10)")),
        explanation=(
            "Bir yükleme işleminin tamamlanma süresi ortalaması $\\mu = 15$ dakika olan üstel dağılıma sahip olsun: "
            "$X \\sim \\mathrm{Exp}(\\mu)$, $f(x) = (1/\\mu)e^{-x/\\mu}$. Kümülatif olasılık "
            "$P(X \\leq x_0) = 1 - e^{-x_0/\\mu}$ (Denklem 11.8), sağ kuyruk $P(X > x_0) = e^{-x_0/\\mu}$'dür "
            "(Denklem 11.9). Aralık olasılığı iki kümülatif olasılığın farkıdır."
        ),
        operations=(
            Scalar("P_6", E.sub(1, E.exp(E.neg(E.div(6, 15)))), "P(X ≤ 6) = 1 − e^(−6/15)", decimals=4),
            Scalar("P_18", E.sub(1, E.exp(E.neg(E.div(18, 15)))), "P(X ≤ 18) = 1 − e^(−18/15)", decimals=4),
            Scalar("P_6_18", E.sub(E.ref("P_18"), E.ref("P_6")), "P(6 < X ≤ 18) = P(X ≤ 18) − P(X ≤ 6)",
                   decimals=4),
            DensityPlot("exponential", 15, 15, (0, 60), "Üstel dağılım, μ = 15 dakika: P(X ≤ 18)",
                        "Tamamlanma süresi (dakika)", shade=((0, 18),), references=((6, "x = 6"),)),
        ),
        checks=(
            _scalar("P_6", 0.3297, "P(X ≤ 6)", 4),
            _scalar("P_18", 0.6988, "P(X ≤ 18)", 4),
            _scalar("P_6_18", 0.3691, "P(6 < X ≤ 18) = 0,6988 − 0,3297", 4),
        ),
        takeaway=(
            "İşlemlerin yaklaşık %33'ü 6 dakikada, %70'i 18 dakikada tamamlanır; 6 ile 18 dakika arası 0,3691'dir. "
            "Üstel dağılımda ortalama ile standart sapma eşittir: E(X) = σ = 15 dakika (Denklem 11.10). Üstel "
            "rassal değişken bir olay sayısı değil, negatif olmayan bir süredir (§11.10)."
        ),
    ),
    LabStep(
        number=9,
        title="Poisson–üstel ilişkisi: sayı mı, süre mi?",
        note=NoteRef("11.11", objects=("Şekil 11.11", "(11.11)")),
        explanation=(
            "Bir gişeye saatte ortalama $\\lambda = 12$ müşteri geliyor. Bir saatteki geliş sayısı Poisson, ardışık "
            "iki geliş arasındaki süre üsteldir. Ortalama bekleme $\\mu = 1/\\lambda$ saattir (Denklem 11.11); "
            "birimler dakikaya çevrilir: $60/12$ dakika."
        ),
        operations=(
            Scalar("mu_gise", E.div(60, 12), "μ = 1/λ saat = 60/12 dakika", decimals=0),
            Scalar("P_10_uzun", E.exp(E.neg(E.div(10, E.ref("mu_gise")))), "P(X > 10) = e^(−10/5)", decimals=4),
            DensityPlot("exponential", 5, 5, (0, 30), "Ardışık iki geliş arasındaki süre, μ = 5 dakika: P(X > 10)",
                        "Bekleme süresi (dakika)", shade=((10, 30),)),
        ),
        checks=(
            _scalar("mu_gise", 5, "Ortalama bekleme (dakika)", 0),
            _scalar("P_10_uzun", 0.1353, "P(X > 10) = e^(−2)", 4),
        ),
        takeaway=(
            "Saatte 12 geliş, gelişler arasında ortalama 5 dakika demektir. Bir sonraki müşteriye kadar 10 dakikadan "
            "uzun bekleme olasılığı e^(−2) ≈ 0,1353'tür. \"Bir saatte kaç olay?\" Poisson'a, \"bir sonraki olaya "
            "kadar ne kadar süre?\" üstele yönlendirir (§11.11)."
        ),
    ),
    LabStep(
        number=10,
        title="Bütünleştirici uygulama: müşteri gelişleri ve satışlar",
        note=NoteRef("11.13"),
        explanation=(
            "Bir işletmeye saatte ortalama 8 müşteri geliyor: bir saatteki müşteri sayısı $N$ Poisson, bir sonraki "
            "gelişe kadar geçen süre $T$ üsteldir. Günlük satış $X \\sim N(500, 80^2)$'dir. Aynı işletmede farklı "
            "sorular farklı dağılımlar gerektirir."
        ),
        operations=(
            Scalar("mu_T", E.div(60, 8), "Ortalama bekleme 60/8 dakika", decimals=1),
            Scalar("P_T_10", E.exp(E.neg(E.div(10, E.ref("mu_T")))), "P(T > 10) = e^(−10/7,5)", decimals=4),
            Scalar("z_600", _z(600, 500, 80), "z = (600 − 500)/80", decimals=2),
            Scalar("P_600", E.sub(1, _table(E.ref("z_600"))), "P(X > 600) = 1 − Φ(1,25)", decimals=4),
            DensityPlot("exponential", 7.5, 7.5, (0, 45), "Bir sonraki müşteriye kadar süre T, μ = 7,5 dakika",
                        "Bekleme süresi (dakika)", shade=((10, 45),), references=((10, "t = 10 dakika"),)),
            DensityPlot("normal", 500, 80, (260, 740), "Günlük satış X ~ N(500, 80²): P(X > 600)", "Günlük satış",
                        shade=((600, 740),), references=((600, "600: z = 1,25"),)),
        ),
        checks=(
            _scalar("mu_T", 7.5, "Ortalama bekleme", 1),
            _scalar("P_T_10", 0.2636, "P(T > 10)", 4),
            _scalar("z_600", 1.25, "z(600)", 2),
            _scalar("P_600", 0.1056, "P(X > 600) = 1 − 0,8944", 4),
        ),
        takeaway=(
            "Bir sonraki müşteriye kadar 10 dakikadan fazla bekleme olasılığı 0,2636, günlük satışın 600'ü aşma "
            "olasılığı 0,1056'dır. N sayıdır ve kesiklidir; T ve X süreklidir. Dağılım seçimi değişkenin adından değil "
            "veri üretim mekanizmasından gelir (§11.12, §11.13)."
        ),
    ),
)

KONU11_LAB = LabSpec(
    topic_key="konu11",
    title="Normal olasılıkları, binomun normal yaklaştırmasını ve üstel dağılımı uygulamak",
    note_section="11",
    steps=STEPS,
    labels=(
        ("z_satir", "z satırı"),
        ("s00", "0,00"),
        ("s01", "0,01"),
        ("s02", "0,02"),
        ("s03", "0,03"),
        ("s04", "0,04"),
        ("s05", "0,05"),
        ("p", "P(Z ≤ z)"),
        ("z", "z"),
        ("x", "x"),
        ("f", "P(X = x)"),
        ("g", "Normal yoğunluk f(x)"),
    ),
)
