"""Konu 8 uygulaması: rassal değişkenler, kesikli olasılık dağılımları, beklenen değer, varyans ve ortak dağılım.

Ders notlarının çözümlü örnekleri: §8.3–8.5 ve §8.7, §8.9 (ek ürün sayısı; Tablo 8.1, 8.3, 8.4, Şekil 8.3–8.5),
§8.4 (eksik olasılık; geçerli ve geçersiz dağılım, Şekil 8.4), §8.6 (200 günün ampirik dağılımı; Tablo 8.2, Şekil
8.6), §8.8 (beklenen kâr), §8.10 (aynı beklenen değer, farklı varyans; Tablo 8.5, Şekil 8.10), §8.11–8.13 (teklif
talebi ve satış; Tablo 8.6, Şekil 8.11) ve §8.14 (talep ve günlük kâr; Tablo 8.7). Buradaki her ``Check`` notlarda
basılı bir sayıdır; değer notlardan kopyalanmıştır, hesaplanmamıştır. §8.1, §8.2 ve §8.15 hesap içermez; §8.8'deki
simülasyon (Şekil 8.8) Sezgi sekmesindeki Deney 1'in varsayılan ayarlarıdır.

Her satır rassal değişkenin bir olası değeridir (ortak dağılımda bir (x, y) çifti); ``f`` o değerin olasılığıdır.
Olay olasılıkları, beklenen değer ve varyans bu sütunun ağırlık olarak kullanıldığı toplamlardır.
"""

from __future__ import annotations

from core.labs import expr as E
from core.labs.spec import (
    BarChart,
    CellTarget,
    Check,
    CrossTab,
    Derive,
    Event,
    FrequencyTable,
    FromCounts,
    HeatMap,
    InlineData,
    LabSpec,
    LabStep,
    NoteRef,
    Scalar,
    ScalarTarget,
    ShowFrame,
    Statistic,
    TableTarget,
)

ADDON_PMF = ((0, 0.10), (1, 0.30), (2, 0.35), (3, 0.20), (4, 0.05))
"""§8.3 (Tablo 8.1): bir işlemde satın alınan ek ürün sayısı x ve f(x) = P(X = x)."""
MISSING_KNOWN = ((0, 0.20), (1, 0.35), (2, 0.30))
"""§8.4: bilinen üç olasılık; X yalnız 0, 1, 2 veya 3 olabilir."""
VALID_PMF = ((0, 0.15), (1, 0.35), (2, 0.30), (3, 0.20))
"""§8.4 (Şekil 8.4, solda): geçerli dağılım."""
INVALID_PMF = ((0, 0.25), (1, 0.45), (2, 0.40), (3, -0.10))
"""§8.4 (Şekil 8.4, sağda): toplamı 1 olan ama negatif olasılık içeren geçersiz tablo."""
ORDER_DAYS = ((0, 24), (1, 60), (2, 56), (3, 34), (4, 20), (5, 6))
"""§8.6 (Tablo 8.2): günlük büyük sipariş sayısı x ve gün sayısı; toplam 200 iş günü."""
PROJECT = ((-20, 0.15), (10, 0.35), (40, 0.35), (80, 0.15))
"""§8.8: yatırım projesinin ilk yıl kârı (bin TL) ve olasılığı."""
TWO_DISTRIBUTIONS = (
    (0, 0.25, 0.0),
    (1, 0.0, 0.25),
    (2, 0.50, 0.50),
    (3, 0.0, 0.25),
    (4, 0.25, 0.0),
)
"""§8.10 (Tablo 8.5): A 0, 2, 4 değerlerini; B 1, 2, 3 değerlerini 0,25, 0,50, 0,25 olasılıklarıyla alır. İki
dağılım aynı değer ekseninde (0–4) yazılır; dağılımın almadığı değerin olasılığı 0'dır."""
JOINT = (
    (0, 0, 0.25),
    (0, 1, 0.0),
    (0, 2, 0.0),
    (1, 0, 0.10),
    (1, 1, 0.25),
    (1, 2, 0.0),
    (2, 0, 0.05),
    (2, 1, 0.10),
    (2, 2, 0.25),
)
"""§8.11 (Tablo 8.6): teklif talebi sayısı x, satış sayısı y ve ortak olasılık f(x, y); Y > X olan çiftler
mümkün değildir (olasılık 0)."""
VALUES = (0, 1, 2)
"""§8.11: X ve Y'nin olası değerleri."""


def _scalar(name: str, expected: float, label: str, decimals: int) -> Check:
    return Check(label, ScalarTarget(name), expected, decimals)


def _addon_cells(column: str, expected: tuple[float, ...], label: str, decimals: int) -> tuple[Check, ...]:
    """Tablo 8.1 çerçevesinde bir sütunun her satırı için bir kontrol; satırlar x = 0, 1, 2, 3, 4 sırasıyladır ve
    ``label`` içindeki ``{x}`` bu değerle doldurulur."""

    return tuple(
        Check(label.format(x=x), CellTarget("ekurun", column, x + 1), value, decimals)
        for x, value in enumerate(expected)
    )


def _squared_deviation(value: str, mean: str) -> E.Expr:
    """(değer − ortalama)²: ``mean`` daha önce hesaplanmış skalerdir."""

    return E.power(E.sub(E.var(value), E.ref(mean)), 2)


STEPS = (
    LabStep(
        number=1,
        title="Olasılık fonksiyonu: f(x) = P(X = x)",
        note=NoteRef("8.3", objects=("Tablo 8.1", "Şekil 8.3")),
        explanation=(
            "Bir çevrim içi mağazada bir işlemde satın alınan ek ürün sayısı $X$; olası değerleri 0, 1, 2, 3 ve 4'tür. "
            "Olasılık dağılımı her olası değerin olasılığını verir (Tablo 8.1). Kesikli bir rassal değişkenin "
            "olasılık fonksiyonu $f(x) = P(X = x)$ ile gösterilir. Veri çerçevesinin her satırı bir olası değer ve "
            "onun olasılığıdır."
        ),
        operations=(
            InlineData("ekurun", ("x", "f"), ADDON_PMF, "Tablo 8.1: ek ürün sayısı x ve olasılığı f(x)"),
            BarChart("ekurun", "f", "Ek ürün sayısı, x", "f(x) = P(X = x)", "Ek ürün sayısının olasılık dağılımı",
                     x="x", decimals=2),
            Statistic("ekurun", "f", "value", "f_2", "f(2) = P(X = 2)", where=("x", 2), decimals=2),
        ),
        checks=(
            _scalar("f_2", 0.35, "f(2) = P(X = 2)", 2),
        ),
        takeaway=(
            "Rassal seçilen bir işlemde tam iki ek ürün satın alınma olasılığı %35'tir. Sütun grafiğinde yatay eksen "
            "olası değerleri, sütun yüksekliği olasılıklarını gösterir; en yüksek sütun x = 2'dedir. En olası değer "
            "ile beklenen değer aynı kavram değildir; beklenen değer Adım 5'te hesaplanır (§8.3)."
        ),
    ),
    LabStep(
        number=2,
        title="Geçerli bir olasılık dağılımının koşulları",
        note=NoteRef("8.4", objects=("Şekil 8.4",)),
        explanation=(
            "Kesikli bir olasılık fonksiyonu iki koşulu birlikte sağlamalıdır: bütün $x$ değerleri için "
            "$f(x) \\geq 0$ ve $\\sum_x f(x) = 1$. Bir olasılık eksik bırakıldığında ikinci koşuldan bulunur: "
            "$P(X = 0) = 0{,}20$, $P(X = 1) = 0{,}35$, $P(X = 2) = 0{,}30$ ve yalnız $X \\in \\{0, 1, 2, 3\\}$ "
            "mümkünse $P(X = 3) = 1 - (0{,}20 + 0{,}35 + 0{,}30)$. Şekil 8.4'teki iki tablonun ikisinde de toplam "
            "1'dir; en küçük değer iki tabloyu ayırır."
        ),
        operations=(
            Statistic("ekurun", "f", "sum", "f_toplam", "Tablo 8.1: Σ f(x)", decimals=2),
            Statistic("ekurun", "f", "min", "f_en_kucuk", "Tablo 8.1: en küçük f(x)", decimals=2),
            InlineData("eksik", ("x", "f"), MISSING_KNOWN, "Bilinen üç olasılık; X yalnız 0, 1, 2 veya 3 olabilir"),
            Statistic("eksik", "f", "sum", "bilinen_toplam", "Bilinen olasılıkların toplamı", decimals=2),
            Scalar("f_3", E.sub(1, E.ref("bilinen_toplam")), "P(X = 3) = 1 − (0,20 + 0,35 + 0,30)", decimals=2),
            InlineData("gecerli", ("x", "f"), VALID_PMF, "Şekil 8.4, solda: geçerli dağılım"),
            Statistic("gecerli", "f", "sum", "gecerli_toplam", "Geçerli tablo: Σ f(x)", decimals=2),
            Statistic("gecerli", "f", "min", "gecerli_en_kucuk", "Geçerli tablo: en küçük f(x)", decimals=2),
            InlineData("gecersiz", ("x", "f"), INVALID_PMF, "Şekil 8.4, sağda: geçersiz tablo"),
            Statistic("gecersiz", "f", "sum", "gecersiz_toplam", "Geçersiz tablo: Σ f(x)", decimals=2),
            Statistic("gecersiz", "f", "min", "gecersiz_en_kucuk", "Geçersiz tablo: en küçük f(x)", decimals=2),
            BarChart("gecerli", "f", "x", "Olasılık", "Geçerli: bütün f(x) ≥ 0 ve Σ f(x) = 1", x="x", decimals=2),
            BarChart("gecersiz", "f", "x", "Olasılık", "Geçersiz: Σ f(x) = 1 ama bir olasılık negatif", x="x",
                     decimals=2),
        ),
        checks=(
            _scalar("f_toplam", 1.00, "Tablo 8.3: Σ f(x)", 2),
            _scalar("f_3", 0.15, "Eksik olasılık P(X = 3)", 2),
            _scalar("gecerli_toplam", 1, "Şekil 8.4, geçerli: Σ f(x) = 1", 0),
            _scalar("gecersiz_toplam", 1, "Şekil 8.4, geçersiz: toplam 1 olsa da geçersiz", 0),
        ),
        takeaway=(
            "Tablo 8.1'deki olasılıkların hiçbiri negatif değildir ve toplamları 1,00'dır. Eksik olasılık 0,15'tir. "
            "Sağdaki tabloda toplam 1 olduğu hâlde x = 3'teki değer negatiftir: tek bir koşulun sağlanması yetmez, "
            "iki koşul birlikte denetlenir. Bir tablodaki sayılar otomatik olarak olasılık kabul edilmez (§8.4)."
        ),
    ),
    LabStep(
        number=3,
        title="Birden fazla değer içeren olayın olasılığı",
        note=NoteRef("8.5", objects=("Şekil 8.5",)),
        explanation=(
            "\"En az iki ek ürün\" olayı $\\{X \\geq 2\\} = \\{2, 3, 4\\}$ biçiminde yazılır. Olasılık fonksiyonu tek "
            "bir değerin olasılığını verir; birden fazla değer içeren olayın olasılığı ilgili değerlerin olasılıkları "
            "toplanarak bulunur: $P(X \\geq 2) = f(2) + f(3) + f(4)$. Olayın gösterge sütunu olaya giren değerlerde "
            "1, diğerlerinde 0'dır."
        ),
        operations=(
            Event("ekurun", "en_az_iki", "x", (2, 3, 4), "X ≥ 2: en az iki ek ürün"),
            ShowFrame("ekurun", ("x", "f", "en_az_iki"), "Olasılıklar ve olayın gösterge sütunu"),
            Statistic("ekurun", "f", "sum", "P_en_az_iki", "P(X ≥ 2) = f(2) + f(3) + f(4)", where=("en_az_iki", 1),
                      decimals=2),
        ),
        checks=(
            _scalar("P_en_az_iki", 0.60, "P(X ≥ 2) = 0,35 + 0,20 + 0,05", 2),
        ),
        takeaway=(
            "Rassal seçilen bir işlemin olasılığı %60 olan bölümünde en az iki ek ürün satın alınır. Kesikli "
            "değişkende P(X ≥ 2) ile P(X > 2) aynı değildir: eşitsizlikteki eşitlik çizgisi 2 değerini olaya katar "
            "(§8.5)."
        ),
    ),
    LabStep(
        number=4,
        title="Veriden olasılık dağılımına: ampirik dağılım",
        note=NoteRef("8.6", objects=("Tablo 8.2", "Şekil 8.6")),
        explanation=(
            "Bir işletme 200 iş gününde günlük büyük sipariş sayısını gözlemiştir: 24 günde 0, 60 günde 1, 56 günde "
            "2, 34 günde 3, 20 günde 4 ve 6 günde 5 sipariş. Her günün değeri bir gözlemdir. Göreli frekanslar, "
            "$f(x) = \\text{gün sayısı}/200$, gelecekteki tipik bir gün için olasılık değerlendirmesi olarak "
            "kullanılır (Tablo 8.2)."
        ),
        operations=(
            FromCounts("gunler", ("x",), ORDER_DAYS, "200 iş günü: günlük büyük sipariş sayısı x ve gün sayısı"),
            FrequencyTable("gunler", "x", "ampirik", (0, 1, 2, 3, 4, 5), totals=True),
            BarChart("ampirik", "goreli", "Günlük büyük sipariş sayısı", "Göreli frekans / olasılık",
                     "200 günden ampirik kesikli dağılım", decimals=2),
        ),
        checks=(
            Check("f(0) = 24/200", TableTarget("ampirik", 0, "goreli"), 0.12, 2),
            Check("f(1) = 60/200", TableTarget("ampirik", 1, "goreli"), 0.30, 2),
            Check("f(2) = 56/200", TableTarget("ampirik", 2, "goreli"), 0.28, 2),
            Check("f(3) = 34/200", TableTarget("ampirik", 3, "goreli"), 0.17, 2),
            Check("f(4) = 20/200", TableTarget("ampirik", 4, "goreli"), 0.10, 2),
            Check("f(5) = 6/200", TableTarget("ampirik", 5, "goreli"), 0.03, 2),
            Check("Gün sayısı", TableTarget("ampirik", "Toplam", "frekans"), 200, 0),
            Check("Göreli frekansların toplamı", TableTarget("ampirik", "Toplam", "goreli"), 1.00, 2),
        ),
        takeaway=(
            "2 büyük sipariş gözlenen 56 gün vardır: f(2) = 56/200 = 0,28. Ampirik olasılıklar geçmiş veriyi özetler. "
            "Kapasite, fiyat politikası veya müşteri tabanı değişirse eski göreli frekanslar yeni dönemi iyi temsil "
            "etmeyebilir; dağılımın güncellenmesi gerekir (§8.6)."
        ),
    ),
    LabStep(
        number=5,
        title="Beklenen değer: olasılık ağırlıklı ortalama",
        note=NoteRef("8.7", objects=("Tablo 8.3", "Şekil 8.7")),
        explanation=(
            "Kesikli $X$'in beklenen değeri $E(X) = \\mu_X = \\sum_x x f(x)$ ile tanımlanır: her olası değer "
            "gerçekleşme olasılığıyla ağırlıklandırılır ve çarpımlar toplanır. Tablo 8.3'ün son sütunu bu "
            "çarpımlardır."
        ),
        operations=(
            Derive("ekurun", "xf", E.mul(E.var("x"), E.var("f")), "x f(x): değer × olasılık"),
            ShowFrame("ekurun", ("x", "f", "xf"), "Tablo 8.3: beklenen değerin hesabı"),
            Statistic("ekurun", "xf", "sum", "E_X", "E(X) = Σ x f(x)", decimals=2),
        ),
        checks=(
            *_addon_cells("xf", (0.00, 0.30, 0.70, 0.60, 0.20), "x f(x), x = {x}", 2),
            _scalar("E_X", 1.80, "E(X) = Σ x f(x)", 2),
        ),
        takeaway=(
            "E(X) = 1,80 ek ürün. Tek bir işlemde 1,8 ürün gözlenemez; beklenen değer, aynı koşullardaki çok sayıda "
            "işlem boyunca ortalama ek ürün sayısının hangi düzey çevresinde olacağını söyler. Olasılık ağırlıklı "
            "denge merkezidir (Şekil 8.7) ve X'in alabileceği değerlerden biri olmak zorunda değildir (§8.7)."
        ),
    ),
    LabStep(
        number=6,
        title="Beklenen kâr ve uzun dönem yorumu",
        note=NoteRef("8.8"),
        explanation=(
            "Bir yatırım projesinin ilk yıl kârı $X$ (bin TL) $-20$, 10, 40 ve 80 değerlerini 0,15, 0,35, 0,35 ve "
            "0,15 olasılıklarıyla alır. Beklenen kâr aynı formülle bulunur: $E(X) = \\sum_x x f(x)$. Beklenen değer "
            "tek seferlik bir tahmin değildir; deney benzer koşullarda tekrarlandıkça gerçekleşen değerlerin "
            "ortalaması beklenen değer çevresinde istikrar kazanma eğilimindedir."
        ),
        operations=(
            InlineData("proje", ("kar", "f"), PROJECT, "Yatırım projesi: ilk yıl kârı (bin TL) ve olasılığı"),
            Derive("proje", "kar_f", E.mul(E.var("kar"), E.var("f")), "x f(x): kâr × olasılık"),
            ShowFrame("proje", ("kar", "f", "kar_f"), "Beklenen kârın hesabı"),
            Statistic("proje", "kar_f", "sum", "E_kar", "Beklenen kâr E(X), bin TL", decimals=1),
        ),
        checks=(
            _scalar("E_kar", 26.5, "E(X) = (−20)(0,15) + (10)(0,35) + (40)(0,35) + (80)(0,15)", 1),
        ),
        takeaway=(
            "Beklenen kâr 26,5 bin TL'dir; bu, projenin kesin olarak 26,5 bin TL kâr edeceğini göstermez, olası "
            "sonuçlar arasında 20 bin TL zarar da vardır. Uzun dönem yorumunu Sezgi sekmesindeki Deney 1 gösterir: "
            "varsayılan ayarlarla (tohum 217) Tablo 8.1'den yapılan 100 çekilişin birikimli ortalaması Şekil 8.8'deki "
            "yolu izler ve 1,77'de biter (§8.8)."
        ),
    ),
    LabStep(
        number=7,
        title="Varyans ve standart sapma",
        note=NoteRef("8.9", objects=("Tablo 8.4",)),
        explanation=(
            "Varyans olası değerlerin beklenen değerden uzaklıklarının karelerinin olasılık ağırlıklı toplamıdır: "
            "$\\operatorname{Var}(X) = \\sigma_X^2 = \\sum_x (x - \\mu_X)^2 f(x)$; standart sapma ise "
            "$\\sigma_X = \\sqrt{\\operatorname{Var}(X)}$ ile bulunur. Mantık Konu 5'teki varyansla aynıdır; burada "
            "kareli uzaklıkların ağırlığı gözlem frekansı değil, olasılık $f(x)$'tir. Ek ürün örneğinde "
            "$\\mu_X = 1{,}80$'dir (Adım 5)."
        ),
        operations=(
            Derive("ekurun", "sapma_kare", _squared_deviation("x", "E_X"),
                   "(x − μ)²: beklenen değerden uzaklığın karesi"),
            Derive("ekurun", "agirlikli_kare", E.mul(E.var("sapma_kare"), E.var("f")), "(x − μ)² f(x)"),
            ShowFrame("ekurun", ("x", "f", "sapma_kare", "agirlikli_kare"), "Tablo 8.4: varyansın hesabı"),
            Statistic("ekurun", "agirlikli_kare", "sum", "Var_X", "Var(X) = Σ (x − μ)² f(x)", decimals=3),
            Scalar("sd_X", E.sqrt(E.ref("Var_X")), "Standart sapma σ = √Var(X)", decimals=2),
        ),
        checks=(
            *_addon_cells("sapma_kare", (3.24, 0.64, 0.04, 1.44, 4.84), "(x − 1,80)², x = {x}", 2),
            *_addon_cells("agirlikli_kare", (0.324, 0.192, 0.014, 0.288, 0.242), "(x − 1,80)² f(x), x = {x}", 3),
            _scalar("Var_X", 1.060, "Var(X)", 3),
            _scalar("sd_X", 1.03, "σ = √1,06", 2),
        ),
        takeaway=(
            "Var(X) = 1,06 ürün², σ ≈ 1,03 ürün. Standart sapma X ile aynı birimdedir; bu yüzden yorumu daha "
            "kolaydır. Bir değerin katkısı hem uzaklığına hem olasılığına bağlıdır: x = 4 merkezden en uzak değerdir, "
            "ama olasılığı küçük olduğu için katkısı (0,242) x = 0'ınkinden (0,324) azdır (§8.9)."
        ),
    ),
    LabStep(
        number=8,
        title="Aynı beklenen değer, farklı değişkenlik",
        note=NoteRef("8.10", objects=("Tablo 8.5", "Şekil 8.10")),
        explanation=(
            "$A$ dağılımı 0, 2 ve 4 değerlerini; $B$ dağılımı 1, 2 ve 3 değerlerini 0,25, 0,50 ve 0,25 "
            "olasılıklarıyla alır (Tablo 8.5). İki dağılımı aynı değer ekseninde karşılaştırmak için 0'dan 4'e kadar "
            "bütün değerler yazılır; dağılımın almadığı değerin olasılığı 0'dır. Beklenen değer ve varyans Adım 5 ve "
            "Adım 7'deki formüllerle bulunur."
        ),
        operations=(
            InlineData("iki_dagilim", ("x", "f_A", "f_B"), TWO_DISTRIBUTIONS,
                       "Tablo 8.5: A ve B dağılımları aynı değer ekseninde"),
            Derive("iki_dagilim", "xf_A", E.mul(E.var("x"), E.var("f_A")), "x f_A(x)"),
            Statistic("iki_dagilim", "xf_A", "sum", "E_A", "E(A)", decimals=2),
            Derive("iki_dagilim", "kare_A", E.mul(_squared_deviation("x", "E_A"), E.var("f_A")),
                   "(x − μ_A)² f_A(x)"),
            Statistic("iki_dagilim", "kare_A", "sum", "Var_A", "Var(A)", decimals=2),
            Derive("iki_dagilim", "xf_B", E.mul(E.var("x"), E.var("f_B")), "x f_B(x)"),
            Statistic("iki_dagilim", "xf_B", "sum", "E_B", "E(B)", decimals=2),
            Derive("iki_dagilim", "kare_B", E.mul(_squared_deviation("x", "E_B"), E.var("f_B")),
                   "(x − μ_B)² f_B(x)"),
            Statistic("iki_dagilim", "kare_B", "sum", "Var_B", "Var(B)", decimals=2),
            BarChart("iki_dagilim", "f_A", "Değer", "Olasılık", "Dağılım A: daha yaygın", x="x", decimals=2),
            BarChart("iki_dagilim", "f_B", "Değer", "Olasılık", "Dağılım B: daha yoğun", x="x", decimals=2),
        ),
        checks=(
            _scalar("E_A", 2, "E(A)", 0),
            _scalar("Var_A", 2.00, "Var(A)", 2),
            _scalar("E_B", 2, "E(B)", 0),
            _scalar("Var_B", 0.50, "Var(B)", 2),
        ),
        takeaway=(
            "İki dağılımın merkezi 2'dir, ama A'nın olasılık kütlesi uç değerlere (0 ve 4) taşınmıştır: "
            "Var(A) = 2 > 0,5 = Var(B). Beklenen değer tek başına belirsizliği ölçmez; iktisadi uygulamalarda bu fark "
            "\"aynı ortalama sonuç, farklı belirsizlik\" biçiminde önem taşır (§8.10)."
        ),
    ),
    LabStep(
        number=9,
        title="İki rassal değişken: ortak olasılık dağılımı",
        note=NoteRef("8.11", objects=("Tablo 8.6", "Şekil 8.11")),
        explanation=(
            "Günlük kurumsal teklif talebi sayısı $X$, bu taleplerden satışa dönüşenlerin sayısı $Y$ olsun; "
            "$X, Y \\in \\{0, 1, 2\\}$ ve $Y > X$ mümkün değildir. Her $(x, y)$ çifti bir satırdır; ortak olasılık "
            "$f(x, y) = P(X = x, Y = y)$ ile gösterilir. Ortak olasılıklarla ağırlıklı çapraz tablo iç hücrelere "
            "ortak olasılıkları, kenarlara marjinal dağılımları yazar (Tablo 8.6: satırlar $Y$, sütunlar $X$)."
        ),
        operations=(
            InlineData("teklif", ("x", "y", "fxy"), JOINT,
                       "Tablo 8.6: teklif talebi x, satış y ve ortak olasılık f(x, y)"),
            CrossTab("teklif", "y", "x", "ortak_tablo", VALUES, VALUES, margins=True, decimals=2, weights="fxy"),
            HeatMap("ortak_tablo", "X: teklif talebi sayısı", "Y: satış sayısı",
                    "Ortak olasılık dağılımı: ısı haritası", decimals=2),
        ),
        checks=(
            Check("P(X = 2, Y = 1)", TableTarget("ortak_tablo", 1, 2), 0.10, 2),
            Check("P(X = 0)", TableTarget("ortak_tablo", "Toplam", 0), 0.25, 2),
            Check("P(X = 1)", TableTarget("ortak_tablo", "Toplam", 1), 0.35, 2),
            Check("P(X = 2)", TableTarget("ortak_tablo", "Toplam", 2), 0.40, 2),
            Check("P(Y = 0)", TableTarget("ortak_tablo", 0, "Toplam"), 0.40, 2),
            Check("P(Y = 1)", TableTarget("ortak_tablo", 1, "Toplam"), 0.35, 2),
            Check("P(Y = 2)", TableTarget("ortak_tablo", 2, "Toplam"), 0.25, 2),
            Check("Ortak olasılıkların toplamı", TableTarget("ortak_tablo", "Toplam", "Toplam"), 1.00, 2),
        ),
        takeaway=(
            "İç hücreler ortak olasılıklardır: örneğin P(X = 2, Y = 1) = 0,10. Alt satır X'in, sağ sütun Y'nin "
            "marjinal dağılımıdır; terminoloji Konu 7'deki ortak ve marjinal olay olasılıklarının devamıdır. Sıfır "
            "hücreleri mantıksal kısıttan gelir: hiç teklif talebi yokken satış gerçekleşemez (§8.11)."
        ),
    ),
    LabStep(
        number=10,
        title="Ortak dağılımdan beklenen değer, kovaryans ve korelasyon",
        note=NoteRef("8.12"),
        explanation=(
            "$E(X) = \\sum_x x\\,P(X = x)$; ortak tabloda bu, her satırda $x$'in ortak olasılıkla çarpılıp "
            "toplanmasına eşittir. Kovaryans $\\operatorname{Cov}(X, Y) = E[(X - \\mu_X)(Y - \\mu_Y)]$ ile "
            "tanımlanır; eşdeğer olarak $\\operatorname{Cov}(X, Y) = E(XY) - E(X)E(Y)$. Korelasyon ise "
            "$\\rho_{XY} = \\operatorname{Cov}(X, Y)/(\\sigma_X \\sigma_Y)$ ile bulunur."
        ),
        operations=(
            Derive("teklif", "x_f", E.mul(E.var("x"), E.var("fxy")), "x f(x, y)"),
            Statistic("teklif", "x_f", "sum", "E_teklif", "E(X): teklif talebi", decimals=2),
            Derive("teklif", "y_f", E.mul(E.var("y"), E.var("fxy")), "y f(x, y)"),
            Statistic("teklif", "y_f", "sum", "E_satis", "E(Y): satış", decimals=2),
            Derive("teklif", "xy_f", E.mul(E.mul(E.var("x"), E.var("y")), E.var("fxy")), "xy f(x, y)"),
            Statistic("teklif", "xy_f", "sum", "E_XY", "E(XY) = Σ Σ xy f(x, y)", decimals=2),
            Scalar("Cov_XY", E.sub(E.ref("E_XY"), E.mul(E.ref("E_teklif"), E.ref("E_satis"))),
                   "Cov(X, Y) = E(XY) − E(X)E(Y)", decimals=4),
            Derive("teklif", "capraz",
                   E.mul(E.mul(E.sub(E.var("x"), E.ref("E_teklif")), E.sub(E.var("y"), E.ref("E_satis"))),
                         E.var("fxy")),
                   "(x − μX)(y − μY) f(x, y)"),
            Statistic("teklif", "capraz", "sum", "Cov_tanim", "Cov(X, Y) tanımdan: E[(X − μX)(Y − μY)]",
                      decimals=4),
            Derive("teklif", "x_kare", E.mul(_squared_deviation("x", "E_teklif"), E.var("fxy")),
                   "(x − μX)² f(x, y)"),
            Statistic("teklif", "x_kare", "sum", "Var_teklif", "Var(X)", decimals=4),
            Derive("teklif", "y_kare", E.mul(_squared_deviation("y", "E_satis"), E.var("fxy")),
                   "(y − μY)² f(x, y)"),
            Statistic("teklif", "y_kare", "sum", "Var_satis", "Var(Y)", decimals=4),
            Scalar("rho_XY", E.div(E.ref("Cov_XY"), E.sqrt(E.mul(E.ref("Var_teklif"), E.ref("Var_satis")))),
                   "ρ = Cov(X, Y)/(σX σY)", decimals=3),
        ),
        checks=(
            _scalar("E_teklif", 1.15, "E(X) = 0(0,25) + 1(0,35) + 2(0,40)", 2),
            _scalar("E_satis", 0.85, "E(Y) = 0(0,40) + 1(0,35) + 2(0,25)", 2),
            _scalar("E_XY", 1.45, "E(XY)", 2),
            _scalar("Cov_XY", 0.4725, "Cov(X, Y) = 1,45 − (1,15)(0,85)", 4),
            _scalar("Cov_tanim", 0.4725, "Cov(X, Y) tanım formülüyle", 4),
            _scalar("Var_teklif", 0.6275, "Var(X)", 4),
            _scalar("Var_satis", 0.6275, "Var(Y)", 4),
            _scalar("rho_XY", 0.753, "ρ = 0,4725/(√0,6275 √0,6275)", 3),
        ),
        takeaway=(
            "Kovaryans pozitiftir (0,4725): daha yüksek teklif talebi sayısı daha yüksek satış sayısıyla birlikte "
            "görülme eğilimindedir; iki formül aynı sayıyı verir. ρ ≈ 0,753 belirgin pozitif doğrusal birlikte "
            "hareket gösterir. Bunlar olasılık dağılımının (anakütlenin) özellikleridir; Konu 5'teki s_xy ve r_xy ise "
            "gözlenen bir veri setinden hesaplanan örneklem ölçüleriydi (§8.12)."
        ),
    ),
    LabStep(
        number=11,
        title="Bağımsızlık: ortak olasılık ve marjinallerin çarpımı",
        note=NoteRef("8.13", objects=("Şekil 8.13",)),
        explanation=(
            "$X$ ve $Y$ bağımsızsa her $(x, y)$ çifti için $P(X = x, Y = y) = P(X = x)P(Y = y)$ olmalıdır. "
            "$(1, 1)$ hücresinde ortak olasılık, marjinal olasılıkların çarpımıyla karşılaştırılır. Marjinal "
            "olasılıklar ilgili satırların ortak olasılıkları toplanarak bulunur."
        ),
        operations=(
            Event("teklif", "X1", "x", (1,), "X = 1"),
            Event("teklif", "Y1", "y", (1,), "Y = 1"),
            Derive("teklif", "X1_ve_Y1", E.mul(E.var("X1"), E.var("Y1")), "X = 1 ve Y = 1"),
            Statistic("teklif", "fxy", "sum", "P_X1", "P(X = 1): marjinal", where=("X1", 1), decimals=2),
            Statistic("teklif", "fxy", "sum", "P_Y1", "P(Y = 1): marjinal", where=("Y1", 1), decimals=2),
            Statistic("teklif", "fxy", "sum", "P_X1_Y1", "P(X = 1, Y = 1): ortak", where=("X1_ve_Y1", 1),
                      decimals=2),
            Scalar("carpim_11", E.mul(E.ref("P_X1"), E.ref("P_Y1")), "Bağımsızlık altında: P(X = 1)P(Y = 1)",
                   decimals=4),
        ),
        checks=(
            _scalar("P_X1_Y1", 0.25, "P(X = 1, Y = 1)", 2),
            _scalar("P_X1", 0.35, "P(X = 1)", 2),
            _scalar("P_Y1", 0.35, "P(Y = 1)", 2),
            _scalar("carpim_11", 0.1225, "P(X = 1)P(Y = 1) = (0,35)(0,35)", 4),
        ),
        takeaway=(
            "Ortak olasılık 0,25 iken bağımsızlık altında olması gereken çarpım 0,1225'tir; eşitlik sağlanmadığı "
            "için X ve Y bağımsız değildir. Bu, Adım 10'daki pozitif kovaryansla uyumludur: bağımsız iki rassal "
            "değişkenin kovaryansı sıfırdır. Tersi genel olarak doğru değildir; sıfır kovaryans bağımsızlığı garanti "
            "etmez (§8.13)."
        ),
    ),
    LabStep(
        number=12,
        title="Bütünleştirici uygulama: talep ve günlük kâr",
        note=NoteRef("8.14", objects=("Tablo 8.7",)),
        explanation=(
            "Yeni bir tamamlayıcı ürünün günlük talebi $X$, Tablo 8.1'deki dağılıma sahiptir. Her satılan birim "
            "300 TL katkı sağlar; ürünü satışta tutmanın günlük sabit maliyeti 250 TL'dir. Günlük kâr "
            "$\\Pi = 300X - 250$ olarak tanımlanır. Kâr, talebin her değerinde o değerin olasılığıyla gerçekleşir "
            "(Tablo 8.7)."
        ),
        operations=(
            Derive("ekurun", "kar", E.sub(E.mul(300, E.var("x")), 250), "π = 300x − 250 (TL)"),
            ShowFrame("ekurun", ("x", "f", "kar"), "Tablo 8.7: talepten günlük kâra"),
            Derive("ekurun", "kar_f", E.mul(E.var("kar"), E.var("f")), "π f(x): kâr × olasılık"),
            Statistic("ekurun", "kar_f", "sum", "E_Pi", "E(Π): kâr dağılımından, TL", decimals=0),
            Scalar("E_Pi_dogrusal", E.sub(E.mul(300, E.ref("E_X")), 250), "300E(X) − 250, TL", decimals=0),
            Derive("ekurun", "zarar", E.compare("lt", E.var("kar"), 0), "Π < 0: zarar göstergesi"),
            Statistic("ekurun", "f", "sum", "P_zarar", "P(Π < 0)", where=("zarar", 1), decimals=2),
        ),
        checks=(
            *_addon_cells("kar", (-250, 50, 350, 650, 950), "π = 300x − 250, x = {x}", 0),
            _scalar("E_Pi", 290, "E(Π)", 0),
            _scalar("E_Pi_dogrusal", 290, "300(1,80) − 250", 0),
            _scalar("P_zarar", 0.10, "P(Π < 0) = P(X = 0)", 2),
        ),
        takeaway=(
            "Beklenen günlük kâr 290 TL'dir; aynı sonuç E(aX + b) = aE(X) + b kuralıyla da bulunur. Yalnız X = 0 iken "
            "zarar oluşur: P(Π < 0) = 0,10. Pozitif beklenen kâr her gün kâr edileceği anlamına gelmez; karar "
            "verirken beklenen kâr, zarar olasılığı ve yayılım birlikte değerlendirilir (§8.14)."
        ),
    ),
)

KONU08_LAB = LabSpec(
    topic_key="konu08",
    title="Kesikli olasılık dağılımlarını, beklenen değeri, varyansı ve ortak dağılımı uygulamak",
    note_section="8",
    steps=STEPS,
    labels=(
        ("f", "f(x)"),
        ("en_az_iki", "X ≥ 2"),
        ("xf", "x f(x)"),
        ("sapma_kare", "(x − μ)²"),
        ("agirlikli_kare", "(x − μ)² f(x)"),
        ("kar", "Kâr"),
        ("kar_f", "Kâr × olasılık"),
        ("zarar", "Π < 0"),
        ("f_A", "f_A(x)"),
        ("f_B", "f_B(x)"),
        ("xf_A", "x f_A(x)"),
        ("xf_B", "x f_B(x)"),
        ("kare_A", "(x − μ_A)² f_A(x)"),
        ("kare_B", "(x − μ_B)² f_B(x)"),
        ("fxy", "f(x, y)"),
        ("x_f", "x f(x, y)"),
        ("y_f", "y f(x, y)"),
        ("xy_f", "xy f(x, y)"),
        ("capraz", "(x − μX)(y − μY) f(x, y)"),
        ("x_kare", "(x − μX)² f(x, y)"),
        ("y_kare", "(y − μY)² f(x, y)"),
        ("X1", "X = 1"),
        ("Y1", "Y = 1"),
        ("X1_ve_Y1", "X = 1, Y = 1"),
    ),
)
