"""Konu 4 uygulaması: bir veri setinin merkezini ve göreli konumları özetlemek.

Ders notlarının çözümlü örnekleri: §4.2 (satış verisinin ortalaması), §4.3 (uç değer), §4.4 (Tablo 4.1),
§4.5 (medyan), §4.6 (ortalama ve medyan), §4.7 (mod), §4.8 (60. yüzdelik), §4.9 (çeyrekler), §4.10
(geometrik ortalama) ve §4.12 (aynı merkez, farklı yayılım). Buradaki her ``Check`` notlarda basılı bir
sayıdır; değer notlardan kopyalanmıştır, hesaplanmamıştır.

Yüzdelikler notlardaki kuralla hesaplanır: L_p = (p/100)(n + 1), tam sayı değilse doğrusal ara değer.
numpy ve R'nin varsayılan kuralı farklıdır; kod bu nedenle kuralı açıkça yazar.
"""

from __future__ import annotations

from core.labs import expr as E
from core.labs.spec import (
    BarChart,
    CellTarget,
    Check,
    Derive,
    DotPlot,
    InlineData,
    LabSpec,
    LabStep,
    NoteRef,
    Percentile,
    Scalar,
    ScalarTable,
    ScalarTarget,
    Statistic,
)

SALES = (16, 18, 20, 22, 22, 22, 24, 26)
"""§4.1: sekiz günlük satış geliri (bin TL)."""
SALES_WITH_OUTLIER = (16, 18, 20, 22, 22, 22, 24, 56)
"""§4.3: en yüksek satış 26 yerine 56."""
COURSE_GRADE = (("Ara sınav", 70, 0.25), ("Proje", 80, 0.25), ("Final", 90, 0.50))
"""Tablo 4.1: bileşen, not ve ağırlık."""
ODD = (12, 14, 18, 20, 30)
EVEN = (12, 14, 18, 20, 30, 35)
"""§4.5: tek ve çift sayıda gözlem."""
ORDERED = (40, 42, 45, 47, 50, 52, 54, 55, 58, 60, 65, 70)
"""§4.8–4.9: 12 gözlemli sıralı veri."""
GROWTH = (("1. yıl", 1.10), ("2. yıl", 0.90))
"""§4.10: %10 artış, ardından %10 azalış (büyüme faktörleri)."""
SPREAD_A = (28, 29, 30, 31, 32)
SPREAD_B = (10, 20, 30, 40, 50)
"""§4.12: aynı merkez, farklı yayılım."""

SALES_AXIS = "Satış geliri (bin TL)"
SALES_RANGE = (12, 60)  # Şekil 4.3 ve 4.6: notlardaki yatay eksen
SPREAD_RANGE = (5, 55)  # Şekil 4.12: iki veri seti aynı eksende


def _scalar(name: str, expected: float, label: str, decimals: int) -> Check:
    return Check(label, ScalarTarget(name), expected, decimals)


def _column(frame: str, values, comment: str) -> InlineData:
    return InlineData(frame, ("x",), tuple((value,) for value in values), comment, layout=len(values))


def _sales(frame: str, values, comment: str) -> InlineData:
    return InlineData(frame, ("gelir",), tuple((value,) for value in values), comment, layout=len(values))


STEPS = (
    LabStep(
        number=1,
        title="Aritmetik ortalama",
        note=NoteRef("4.2"),
        explanation=(
            "Sekiz günlük satış gelirinin ortalaması $\\bar{x} = \\sum x_i / n$ ile bulunur: "
            "$(16 + 18 + 20 + 22 + 22 + 22 + 24 + 26)/8 = 170/8$. Nokta grafiğinde ortalama, bütün noktaları "
            "dengede tutan destek noktası gibi düşünülebilir."
        ),
        operations=(
            _sales("satis", SALES, "Sekiz günlük satış geliri (bin TL)"),
            Statistic("satis", "gelir", "sum", "toplam", "Satışların toplamı (bin TL)", decimals=0),
            Statistic("satis", "gelir", "count", "n", "Gün sayısı n", decimals=0),
            Scalar("ortalama", E.div(E.ref("toplam"), E.ref("n")), "Ortalama x̄ (bin TL)", decimals=2),
            DotPlot("satis", "gelir", SALES_AXIS, "Ortalama bir denge noktasıdır",
                    references=(("ortalama", "Ortalama"),)),
        ),
        checks=(
            _scalar("toplam", 170, "Satışların toplamı", 0),
            _scalar("ortalama", 21.25, "Ortalama 170/8", 2),
        ),
        takeaway=(
            "Ortalama 21,25 bin TL'dir; bu değer gözlemler arasında yoktur. Ortalama gözlemlerin toplamını korur, "
            "\"en sık görülen\" veya \"ortadaki gözlem\" anlamına gelmez (§4.2)."
        ),
    ),
    LabStep(
        number=2,
        title="Uç değerin ortalamaya etkisi",
        note=NoteRef("4.3", objects=("Şekil 4.3",)),
        explanation=(
            "En yüksek günlük satış 26 yerine 56 olsun. Toplam 200'e çıkar ve ortalama $200/8 = 25$ olur: tek bir "
            "gözlemin değişmesi ortalamayı 21,25'ten 25'e taşır."
        ),
        operations=(
            _sales("satis_uc", SALES_WITH_OUTLIER, "Son gün 56 bin TL"),
            Statistic("satis_uc", "gelir", "sum", "toplam_uc", "Satışların toplamı (bin TL)", decimals=0),
            Scalar("ortalama_uc", E.div(E.ref("toplam_uc"), E.ref("n")), "Yeni ortalama x̄ (bin TL)", decimals=2),
            DotPlot("satis_uc", "gelir", SALES_AXIS, "Tek bir büyük değer ortalamayı sağa çeker",
                    references=(("ortalama_uc", "Yeni ortalama"), ("ortalama", "İlk ortalama")), x_range=SALES_RANGE),
        ),
        checks=(
            _scalar("toplam_uc", 200, "Uç değerli toplam", 0),
            _scalar("ortalama_uc", 25, "Uç değerli ortalama 200/8", 0),
        ),
        takeaway=(
            "Ortalama uç değerlere duyarlıdır. Bu, ortalamanın yanlış olduğu anlamına gelmez; amaç tipik bir "
            "günü betimlemekse medyana da bakılmalıdır (§4.3)."
        ),
    ),
    LabStep(
        number=3,
        title="Ağırlıklı ortalama",
        note=NoteRef("4.4", objects=("Tablo 4.1",)),
        explanation=(
            "Her bileşenin katkısı $w_i x_i$'dir ve ağırlıklı ortalama $\\bar{x}_w = \\sum w_i x_i / \\sum w_i$ ile "
            "bulunur. Ağırlıkların toplamı 1 olduğundan payda 1'dir."
        ),
        operations=(
            InlineData("basari", ("bilesen", "puan", "agirlik"), COURSE_GRADE, "Tablo 4.1: bileşen, not ve ağırlık"),
            Derive("basari", "katki", E.mul(E.var("agirlik"), E.var("puan")), "Katkı wᵢxᵢ"),
            Statistic("basari", "katki", "sum", "toplam_katki", "Katkıların toplamı Σwᵢxᵢ", decimals=2),
            Statistic("basari", "agirlik", "sum", "toplam_agirlik", "Ağırlıkların toplamı Σwᵢ", decimals=2),
            Scalar("agirlikli_ortalama", E.div(E.ref("toplam_katki"), E.ref("toplam_agirlik")),
                   "Ağırlıklı ortalama x̄_w", decimals=1),
            Statistic("basari", "puan", "mean", "basit_ortalama", "Basit ortalama", decimals=1),
            Derive("basari", "agirlik_yuzde", E.mul(100, E.var("agirlik")), "Ağırlık yüzde olarak"),
            BarChart("basari", "agirlik_yuzde", "Bileşen", "Ağırlık (%)", "Her bileşenin ağırlığı", x="bilesen",
                     percent=True),
        ),
        checks=(
            Check("Ara sınav katkısı 0,25 × 70", CellTarget("basari", "katki", 1), 17.50, 2),
            Check("Proje katkısı 0,25 × 80", CellTarget("basari", "katki", 2), 20.00, 2),
            Check("Final katkısı 0,50 × 90", CellTarget("basari", "katki", 3), 45.00, 2),
            _scalar("toplam_agirlik", 1.00, "Ağırlıkların toplamı", 2),
            _scalar("toplam_katki", 82.50, "Katkıların toplamı", 2),
            _scalar("agirlikli_ortalama", 82.5, "Ağırlıklı ortalama", 1),
            _scalar("basit_ortalama", 80, "Basit ortalama (70 + 80 + 90)/3", 0),
        ),
        takeaway=(
            "Final sınavı daha yüksek ağırlığa sahip olduğu için ağırlıklı ortalama (82,5) 90'a, basit "
            "ortalamadan (80) daha yakındır. Ağırlıklar 0,25 biçiminde kullanılıyorsa bir kez daha 100'e "
            "bölünmez (§4.4)."
        ),
    ),
    LabStep(
        number=4,
        title="Medyan",
        note=NoteRef("4.5", objects=("Şekil 4.5",)),
        explanation=(
            "Medyan sıralanmış verinin ortasındaki konumdur: $n$ tek ise tam ortadaki gözlem, $n$ çift ise "
            "ortadaki iki gözlemin ortalaması. Medyandan önce veri mutlaka sıralanır."
        ),
        operations=(
            _column("tek", ODD, "Beş gözlem (tek sayı)"),
            _column("cift", EVEN, "Altı gözlem (çift sayı)"),
            Statistic("tek", "x", "median", "medyan_tek", "Medyan, n = 5", decimals=0),
            Statistic("cift", "x", "median", "medyan_cift", "Medyan, n = 6", decimals=0),
        ),
        checks=(
            _scalar("medyan_tek", 18, "Medyan: üçüncü değer", 0),
            _scalar("medyan_cift", 19, "Medyan: (18 + 20)/2", 0),
        ),
        takeaway=(
            "Çift sayıda gözlemde medyan (19) veri setinde gözlenmiş bir değer olmak zorunda değildir. Medyan "
            "büyüklükten çok sıralamadaki konuma dayanır (§4.5)."
        ),
    ),
    LabStep(
        number=5,
        title="Ortalama ve medyanın karşılaştırılması",
        note=NoteRef("4.6", objects=("Şekil 4.6",)),
        explanation=(
            "Satış verisinin medyanı dördüncü ve beşinci değerlerin ortalamasıdır: $(22 + 22)/2 = 22$. En büyük "
            "gözlem 56 olduğunda ortalama 25'e çıkar; medyan yine 22'dir."
        ),
        operations=(
            Statistic("satis", "gelir", "median", "medyan", "Medyan (bin TL)", decimals=0),
            Statistic("satis_uc", "gelir", "median", "medyan_uc", "Uç değerli medyan (bin TL)", decimals=0),
            ScalarTable(
                (
                    ("İlk veri: ortalama", E.ref("ortalama")),
                    ("İlk veri: medyan", E.ref("medyan")),
                    ("56 ile: ortalama", E.ref("ortalama_uc")),
                    ("56 ile: medyan", E.ref("medyan_uc")),
                ),
                "karsilastirma",
            ),
            DotPlot("satis_uc", "gelir", SALES_AXIS, "Uç değer karşısında medyan ve ortalama",
                    references=(("medyan_uc", "Medyan"), ("ortalama_uc", "Ortalama")), x_range=SALES_RANGE),
        ),
        checks=(
            _scalar("medyan", 22, "Medyan (22 + 22)/2", 0),
            _scalar("medyan_uc", 22, "Uç değerli medyan", 0),
        ),
        takeaway=(
            "Ortalama bütün büyüklükleri kullandığı için sağa kayar; medyan sıradaki konuma dayandığı için "
            "değişmez. Sağa çarpık gelir, servet veya konut fiyatında ikisini birlikte raporlamak daha "
            "bilgilendiricidir (§4.6)."
        ),
    ),
    LabStep(
        number=6,
        title="Mod",
        note=NoteRef("4.7"),
        explanation=(
            "Mod en yüksek frekansla gözlenen değerdir. Satış verisinde 22 üç kez, diğer değerler birer kez "
            "gözlenir. Adım 1'deki nokta grafiğinde mod en yüksek yığındır."
        ),
        operations=(
            Statistic("satis", "gelir", "mode", "mod", "Mod (bin TL)", decimals=0),
            Statistic("satis", "gelir", "mode_freq", "mod_frekansi", "Modun frekansı", decimals=0),
        ),
        checks=(
            _scalar("mod", 22, "Mod", 0),
            _scalar("mod_frekansi", 3, "Modun frekansı", 0),
        ),
        takeaway=(
            "Bir veri setinde bir mod, birden fazla mod veya hiç ayırt edici mod bulunmayabilir. Mod, en sık "
            "tercih edilen ödeme yöntemi gibi nominal kategorik veride de anlamlıdır (§4.7)."
        ),
    ),
    LabStep(
        number=7,
        title="Yüzdelikler: göreli konum",
        note=NoteRef("4.8", objects=("Şekil 4.8",)),
        explanation=(
            "Bu derste yüzdelik konumu $L_p = \\frac{p}{100}(n + 1)$ ile bulunur; $L_p$ tam sayı değilse komşu iki "
            "gözlem arasında doğrusal ara değer alınır. $n = 12$ için $L_{60} = 0{,}60 \\times 13 = 7{,}8$: 7. değer "
            "54, 8. değer 55 olduğundan $P_{60} = 54 + 0{,}8\\,(55 - 54)$."
        ),
        operations=(
            _column("sirali", ORDERED, "12 gözlemli sıralı veri"),
            Percentile("sirali", "x", 60, "P60", "60. yüzdelik P₆₀", location="L60", decimals=1),
        ),
        checks=(
            _scalar("L60", 7.8, "Konum L₆₀", 1),
            _scalar("P60", 54.8, "60. yüzdelik P₆₀", 1),
        ),
        code_note=(
            "numpy'nin np.percentile ve R'nin quantile fonksiyonları varsayılan olarak başka bir kural kullanır "
            "(bu veride 54,6). Notlardaki kural numpy'de method=\"weibull\", R'de type = 6 ile aynıdır; kod "
            "karışıklık olmasın diye kuralı açıkça yazar."
        ),
        takeaway=(
            "Bir sonucun 80. yüzdelikte olması notun 80 olduğu anlamına gelmez; gözlemlerin yaklaşık %80'inin "
            "altında kaldığı konumu anlatır. P₆₀ = 54,8 değerinin altında gözlemlerin yaklaşık %60'ı vardır (§4.8)."
        ),
    ),
    LabStep(
        number=8,
        title="Çeyrekler",
        note=NoteRef("4.9", objects=("Şekil 4.9",)),
        explanation=(
            "Çeyrekler özel yüzdeliklerdir: $Q_1 = P_{25}$, $Q_2 = P_{50}$ (medyan), $Q_3 = P_{75}$. Aynı 12 "
            "gözlem için $L_{25} = 3{,}25$ ve $L_{75} = 9{,}75$'tir; $Q_2$, 6. ve 7. değerlerin ortalamasıdır."
        ),
        operations=(
            Percentile("sirali", "x", 25, "Q1", "Birinci çeyrek Q₁", location="L25", decimals=1),
            Percentile("sirali", "x", 50, "Q2", "İkinci çeyrek Q₂ (medyan)", location="L50", decimals=1),
            Percentile("sirali", "x", 75, "Q3", "Üçüncü çeyrek Q₃", location="L75", decimals=1),
            DotPlot("sirali", "x", "Değer", "Çeyrekler gözlemleri dört gruba ayırır",
                    references=(("Q1", "Q₁"), ("Q2", "Q₂"), ("Q3", "Q₃"))),
        ),
        checks=(
            _scalar("L25", 3.25, "Konum L₂₅", 2),
            _scalar("Q1", 45.5, "Q₁ = 45 + 0,25 × (47 − 45)", 1),
            _scalar("Q2", 53, "Q₂ = (52 + 54)/2", 0),
            _scalar("L75", 9.75, "Konum L₇₅", 2),
            _scalar("Q3", 59.5, "Q₃ = 58 + 0,75 × (60 − 58)", 1),
        ),
        takeaway=(
            "Çeyrekler sayısal ekseni eşit uzunluklara değil, gözlemleri yaklaşık eşit sayıda dört gruba böler: "
            "Q₁ ile Q₂ arası 7,5, Q₂ ile Q₃ arası 6,5 birimdir (§4.9)."
        ),
    ),
    LabStep(
        number=9,
        title="Geometrik ortalama ve bileşik büyüme",
        note=NoteRef("4.10", objects=("Şekil 4.10",)),
        explanation=(
            "Bir yatırım ilk yıl %10 artar, ikinci yıl %10 azalır. Büyüme faktörleri 1,10 ve 0,90'dır; 100 TL "
            "önce 110, sonra 99 TL olur. Geometrik ortalama $G = (g_1 g_2)^{1/2}$ ve ortalama bileşik büyüme "
            "oranı $(G - 1) \\times 100$'dür."
        ),
        operations=(
            InlineData("buyume", ("yil", "faktor"), GROWTH, "İki yılın büyüme faktörleri"),
            Derive("buyume", "degisim", E.mul(100, E.sub(E.var("faktor"), 1)), "Yüzde değişim"),
            Statistic("buyume", "degisim", "mean", "aritmetik_degisim", "Aritmetik ortalama değişim",
                      decimals=0),
            Statistic("buyume", "faktor", "prod", "carpim", "Faktörlerin çarpımı", decimals=2),
            Statistic("buyume", "faktor", "count", "yil_sayisi", "Yıl sayısı", decimals=0),
            Scalar("son_deger", E.mul(100, E.ref("carpim")), "100 TL'nin iki yıl sonraki değeri", decimals=0),
            Scalar("G", E.power(E.ref("carpim"), E.div(1, E.ref("yil_sayisi"))), "Geometrik ortalama G",
                   decimals=3),
            Scalar("bilesik_buyume", E.mul(100, E.sub(E.ref("G"), 1)), "Ortalama bileşik büyüme",
                   decimals=1, percent=True),
        ),
        checks=(
            _scalar("aritmetik_degisim", 0, "Yüzde değişimlerin aritmetik ortalaması", 0),
            _scalar("son_deger", 99, "İki yıl sonraki değer", 0),
            _scalar("G", 0.995, "Geometrik ortalama √0,99", 3),
            _scalar("bilesik_buyume", -0.5, "Ortalama bileşik büyüme (%)", 1),
        ),
        takeaway=(
            "Yüzde değişimlerin aritmetik ortalaması 0'dır, ama yatırım başlangıç değerine dönmez: ardışık "
            "büyüme oranları çarpımsal işler. Ortalama bileşik büyüme geometrik ortalamayla bulunur (§4.10)."
        ),
    ),
    LabStep(
        number=10,
        title="Aynı merkez, farklı dağılım",
        note=NoteRef("4.12", objects=("Şekil 4.12",)),
        explanation=(
            "İki veri setinin aritmetik ortalaması da medyanı da 30'dur: A = 28, 29, 30, 31, 32 ve "
            "B = 10, 20, 30, 40, 50. Konum ölçüleri yayılımdaki farkı göstermez."
        ),
        operations=(
            _column("veri_a", SPREAD_A, "Veri A"),
            _column("veri_b", SPREAD_B, "Veri B"),
            Statistic("veri_a", "x", "mean", "ortalama_a", "Veri A: ortalama", decimals=0),
            Statistic("veri_a", "x", "median", "medyan_a", "Veri A: medyan", decimals=0),
            Statistic("veri_b", "x", "mean", "ortalama_b", "Veri B: ortalama", decimals=0),
            Statistic("veri_b", "x", "median", "medyan_b", "Veri B: medyan", decimals=0),
            DotPlot("veri_a", "x", "Değer", "Veri A: 30 çevresinde sık", references=(("ortalama_a", "Ortalama"),),
                    x_range=SPREAD_RANGE),
            DotPlot("veri_b", "x", "Değer", "Veri B: aynı merkez, geniş yayılım",
                    references=(("ortalama_b", "Ortalama"),), x_range=SPREAD_RANGE),
        ),
        checks=(
            _scalar("ortalama_a", 30, "Veri A: ortalama", 0),
            _scalar("medyan_a", 30, "Veri A: medyan", 0),
            _scalar("ortalama_b", 30, "Veri B: ortalama", 0),
            _scalar("medyan_b", 30, "Veri B: medyan", 0),
        ),
        takeaway=(
            "Tek bir konum ölçüsü dağılımın bütün özelliklerini göstermez. Bir sonraki konuda bu farkı "
            "değişkenlik ve yayılım ölçüleriyle sayısallaştıracağız (§4.12)."
        ),
    ),
)

KONU04_LAB = LabSpec(
    topic_key="konu04",
    title="Merkezi eğilim ve konum ölçülerini hesaplamak",
    note_section="4",
    steps=STEPS,
    labels=(
        ("gelir", SALES_AXIS),
        ("bilesen", "Bileşen"),
        ("puan", "Not xᵢ"),
        ("agirlik", "Ağırlık wᵢ"),
        ("katki", "Katkı wᵢxᵢ"),
        ("agirlik_yuzde", "Ağırlık (%)"),
        ("x", "Değer"),
        ("yil", "Yıl"),
        ("faktor", "Büyüme faktörü"),
        ("degisim", "Yüzde değişim"),
    ),
)
