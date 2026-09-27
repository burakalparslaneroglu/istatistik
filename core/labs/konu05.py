"""Konu 5 uygulaması: değişkenlik, dağılımın şekli ve iki değişken arasındaki ilişki.

Ders notlarının çözümlü örnekleri: §5.1 (iki tedarikçi), §5.2 (değişim aralığı), §5.3 (Tablo 5.1: sapmalar
ve varyans), §5.4 (standart sapma), §5.5 (değişim katsayısı), §5.7 (z-skoru), §5.8 (Chebyshev), §5.9 (IQR ile
aykırı değer), §5.10 (beş sayı özeti ve kutu grafiği), §5.11 (Tablo 5.2: kovaryans), §5.12 (korelasyon) ve
§5.13 (istatistiksel profil). Buradaki her ``Check`` notlarda basılı bir sayıdır; değer notlardan
kopyalanmıştır, hesaplanmamıştır. §5.6 (çarpıklık) sayısal örnek içermez; Sezgi sekmesindeki deneyler bu
bölümü simülasyonla işler.

Çeyrekler Konu 4'teki ders kuralıyla hesaplanır: L_p = (p/100)(n + 1), tam sayı değilse doğrusal ara değer.
Varyans, standart sapma ve kovaryansın paydası n − 1'dir (pandas ve R'nin varsayılanı).
"""

from __future__ import annotations

from core.labs import expr as E
from core.labs.spec import (
    BoxPlot,
    BoxSummary,
    CellTarget,
    Check,
    Derive,
    DotPlot,
    InlineData,
    LabSpec,
    LabStep,
    NoteRef,
    PairStatistic,
    Percentile,
    Scalar,
    ScalarTable,
    ScalarTarget,
    ScatterPlot,
    Statistic,
    TableTarget,
)

SUPPLIER_A = (9, 10, 10, 10, 11)
SUPPLIER_B = (7, 8, 10, 12, 13)
"""§5.1: iki tedarikçinin son beş teslim süresi (gün)."""
DEVIATIONS = (4, 6, 8, 10, 12)
"""§5.3, Tablo 5.1: sapmalar ve varyans için küçük örneklem."""
INCOME = (20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 65)
"""§5.9–5.10: sıralanmış gelir verisi (11 gözlem)."""
ADVERTISING = ((1, 1, 20), (2, 2, 22), (3, 3, 25), (4, 4, 27), (5, 5, 31))
"""Tablo 5.2: hafta, reklam sayısı x ve satış y (bin TL)."""

DAYS_AXIS = "Teslim süresi (gün)"
DAYS_RANGE = (6, 14)  # Şekil 5.1: notlardaki yatay eksen, iki tedarikçi aynı eksende
INCOME_RANGE = (10, 70)  # Şekil 5.10: notlardaki yatay eksen


def _scalar(name: str, expected: float, label: str, decimals: int) -> Check:
    return Check(label, ScalarTarget(name), expected, decimals)


def _box(row: str, expected: float, label: str) -> Check:
    return Check(label, TableTarget("kutu", row, "Gelir"), expected, 0)


def _column(frame: str, variable: str, values, comment: str) -> InlineData:
    return InlineData(frame, (variable,), tuple((value,) for value in values), comment, layout=len(values))


STEPS = (
    LabStep(
        number=1,
        title="Aynı merkez, farklı yayılım",
        note=NoteRef("5.1", objects=("Şekil 5.1",)),
        explanation=(
            "İki tedarikçinin son beş teslim süresi: A = 9, 10, 10, 10, 11 ve B = 7, 8, 10, 12, 13 gün. İki "
            "tedarikçinin ortalaması da 10 gündür. Nokta grafiklerinde yatay eksen aynıdır; fark gözlemlerin "
            "merkez çevresinde nasıl dağıldığındadır."
        ),
        operations=(
            _column("tedarikci_a", "sure", SUPPLIER_A, "Tedarikçi A: teslim süreleri (gün)"),
            _column("tedarikci_b", "sure", SUPPLIER_B, "Tedarikçi B: teslim süreleri (gün)"),
            Statistic("tedarikci_a", "sure", "mean", "ortalama_a", "Tedarikçi A: ortalama (gün)", decimals=0),
            Statistic("tedarikci_b", "sure", "mean", "ortalama_b", "Tedarikçi B: ortalama (gün)", decimals=0),
            DotPlot("tedarikci_a", "sure", DAYS_AXIS, "Tedarikçi A: 9–11 gün arasında",
                    references=(("ortalama_a", "Ortalama"),), x_range=DAYS_RANGE),
            DotPlot("tedarikci_b", "sure", DAYS_AXIS, "Tedarikçi B: 7–13 gün arasında",
                    references=(("ortalama_b", "Ortalama"),), x_range=DAYS_RANGE),
        ),
        checks=(
            _scalar("ortalama_a", 10, "Tedarikçi A: ortalama", 0),
            _scalar("ortalama_b", 10, "Tedarikçi B: ortalama", 0),
        ),
        takeaway=(
            "\"Ortalama teslim süresi 10 gün\" bilgisi iki tedarikçiyi ayırmaz. Bir veri setini özetlerken merkez "
            "ve yayılım birlikte raporlanır (§5.1)."
        ),
    ),
    LabStep(
        number=2,
        title="Değişim aralığı",
        note=NoteRef("5.2", objects=("Şekil 5.2",)),
        explanation=(
            "Değişim aralığı en büyük ve en küçük gözlem arasındaki farktır: $R = x_{\\max} - x_{\\min}$. Yalnız "
            "iki gözlemi kullanır."
        ),
        operations=(
            Statistic("tedarikci_a", "sure", "max", "en_buyuk_a", "Tedarikçi A: en büyük", decimals=0),
            Statistic("tedarikci_a", "sure", "min", "en_kucuk_a", "Tedarikçi A: en küçük", decimals=0),
            Scalar("aralik_a", E.sub(E.ref("en_buyuk_a"), E.ref("en_kucuk_a")), "Değişim aralığı R_A (gün)",
                   decimals=0),
            Statistic("tedarikci_b", "sure", "max", "en_buyuk_b", "Tedarikçi B: en büyük", decimals=0),
            Statistic("tedarikci_b", "sure", "min", "en_kucuk_b", "Tedarikçi B: en küçük", decimals=0),
            Scalar("aralik_b", E.sub(E.ref("en_buyuk_b"), E.ref("en_kucuk_b")), "Değişim aralığı R_B (gün)",
                   decimals=0),
        ),
        checks=(
            _scalar("aralik_a", 2, "R_A = 11 − 9", 0),
            _scalar("aralik_b", 6, "R_B = 13 − 7", 0),
        ),
        takeaway=(
            "B'nin teslim süreleri daha geniş bir aralığa yayılır. Ancak değişim aralığı yalnız iki uç gözleme "
            "dayanır; tek bir çok büyük değer onu belirgin biçimde büyütebilir (§5.2). Adım 8'deki gelir "
            "verisinde bunu göreceğiz."
        ),
    ),
    LabStep(
        number=3,
        title="Ortalamadan sapmalar ve varyans",
        note=NoteRef("5.3", objects=("Tablo 5.1",)),
        explanation=(
            "4, 6, 8, 10, 12 örnekleminde $\\bar{x} = 8$'dir. Her gözlemin sapması $x_i - \\bar{x}$, kareli "
            "sapması $(x_i - \\bar{x})^2$'dir. Örneklem varyansı kareli sapmalar toplamının $n - 1$'e bölümüdür: "
            "$s^2 = \\sum (x_i - \\bar{x})^2 / (n - 1)$."
        ),
        operations=(
            _column("orneklem", "x", DEVIATIONS, "Tablo 5.1: beş gözlem"),
            Statistic("orneklem", "x", "mean", "ortalama", "Ortalama x̄", decimals=0),
            Derive("orneklem", "sapma", E.sub(E.var("x"), E.ref("ortalama")), "Sapma xᵢ − x̄"),
            Derive("orneklem", "sapma_kare", E.power(E.var("sapma"), 2), "Kareli sapma (xᵢ − x̄)²"),
            Statistic("orneklem", "sapma", "sum", "sapma_toplami", "Sapmaların toplamı", decimals=0),
            Statistic("orneklem", "sapma_kare", "sum", "kare_toplami", "Kareli sapmalar toplamı", decimals=0),
            Statistic("orneklem", "x", "count", "n", "Gözlem sayısı n", decimals=0),
            Scalar("varyans", E.div(E.ref("kare_toplami"), E.sub(E.ref("n"), 1)), "Varyans s² = 40/(5 − 1)",
                   decimals=0),
            Statistic("orneklem", "x", "var", "varyans_yazilim", "Yazılımın varyans fonksiyonu", decimals=0),
        ),
        checks=(
            _scalar("ortalama", 8, "Ortalama x̄", 0),
            Check("İlk gözlemin sapması 4 − 8", CellTarget("orneklem", "sapma", 1), -4, 0),
            Check("İlk gözlemin kareli sapması", CellTarget("orneklem", "sapma_kare", 1), 16, 0),
            _scalar("sapma_toplami", 0, "Sapmaların toplamı", 0),
            _scalar("kare_toplami", 40, "Kareli sapmalar toplamı", 0),
            _scalar("varyans", 10, "Örneklem varyansı s²", 0),
            _scalar("varyans_yazilim", 10, "Yazılımla varyans", 0),
        ),
        code_note=(
            "pandas'ın var() ve R'nin var() fonksiyonları örneklem varyansını verir (payda n − 1). numpy'nin "
            "np.var fonksiyonu ise varsayılan olarak n'ye böler (bu veride 8); örneklem varyansı için ddof=1 "
            "yazılmalıdır."
        ),
        takeaway=(
            "Sapmaların toplamı her veri setinde sıfırdır; pozitif ve negatif sapmalar birbirini götürür. Varyans bu "
            "yüzden kareli sapmaları kullanır. Birimi özgün birimin karesidir (§5.3)."
        ),
    ),
    LabStep(
        number=4,
        title="Standart sapma",
        note=NoteRef("5.4"),
        explanation=(
            "Standart sapma varyansın pozitif kareköküdür: $s = \\sqrt{s^2}$. Önceki adımda $s^2 = 10$ olduğundan "
            "$s = \\sqrt{10}$. Standart sapma özgün ölçü birimindedir; tedarikçileri gün cinsinden karşılaştırır."
        ),
        operations=(
            Scalar("std_sapma", E.sqrt(E.ref("varyans")), "Standart sapma s = √10", decimals=2),
            Statistic("tedarikci_a", "sure", "std", "std_a", "Tedarikçi A: s (gün)", decimals=2),
            Statistic("tedarikci_b", "sure", "std", "std_b", "Tedarikçi B: s (gün)", decimals=2),
        ),
        checks=(
            _scalar("std_sapma", 3.16, "s = √10", 2),
            _scalar("std_a", 0.71, "Tedarikçi A: s", 2),
            _scalar("std_b", 2.55, "Tedarikçi B: s", 2),
        ),
        takeaway=(
            "Ortalamalar eşitken B'nin standart sapması (2,55 gün) A'nınkinin (0,71 gün) üç katından fazladır: B'nin "
            "teslim süresi daha değişkendir (§5.4)."
        ),
    ),
    LabStep(
        number=5,
        title="Değişim katsayısı",
        note=NoteRef("5.5", objects=("Şekil 5.6",)),
        explanation=(
            "Ortalamaları çok farklı iki değişkenin yayılımı standart sapmayla değil, ortalamaya göre "
            "karşılaştırılır: $CV = (s/\\bar{x}) \\times 100$. A değişkeninde $\\bar{x} = 80$, $s = 8$; B "
            "değişkeninde $\\bar{x} = 10$, $s = 2$."
        ),
        operations=(
            Scalar("ortalama_1", E.const(80), "A değişkeni: ortalama", decimals=0),
            Scalar("std_1", E.const(8), "A değişkeni: standart sapma", decimals=0),
            Scalar("cv_1", E.mul(E.div(E.ref("std_1"), E.ref("ortalama_1")), 100), "A değişkeni: CV", decimals=0,
                   percent=True),
            Scalar("ortalama_2", E.const(10), "B değişkeni: ortalama", decimals=0),
            Scalar("std_2", E.const(2), "B değişkeni: standart sapma", decimals=0),
            Scalar("cv_2", E.mul(E.div(E.ref("std_2"), E.ref("ortalama_2")), 100), "B değişkeni: CV", decimals=0,
                   percent=True),
        ),
        checks=(
            _scalar("cv_1", 10, "CV = 8/80 × 100 (%)", 0),
            _scalar("cv_2", 20, "CV = 2/10 × 100 (%)", 0),
        ),
        takeaway=(
            "Mutlak standart sapma A'da büyüktür (8 > 2), ama kendi ortalamasına göre B daha değişkendir (%20 > %10). "
            "CV, sıfırın anlamlı olduğu oran ölçekli değişkenlerde kullanılır; ortalama sıfıra yakınsa yanıltır "
            "(§5.5)."
        ),
    ),
    LabStep(
        number=6,
        title="z-skoru ve göreli konum",
        note=NoteRef("5.7", objects=("Şekil 5.8",)),
        explanation=(
            "$z = (x - \\bar{x})/s$, bir gözlemin ortalamadan kaç standart sapma uzakta olduğunu gösterir. Birinci "
            "sınavda $\\bar{x} = 70$, $s = 10$ ve not 85; ikinci sınavda $\\bar{x} = 30$, $s = 10$ ve not 45'tir."
        ),
        operations=(
            Scalar("z_1", E.div(E.sub(85, 70), 10), "Birinci sınav: z = (85 − 70)/10", decimals=1),
            Scalar("z_2", E.div(E.sub(45, 30), 10), "İkinci sınav: z = (45 − 30)/10", decimals=1),
        ),
        checks=(
            _scalar("z_1", 1.5, "Birinci sınav: z", 1),
            _scalar("z_2", 1.5, "İkinci sınav: z", 1),
        ),
        takeaway=(
            "Ham notlar (85 ve 45) çok farklıdır, ama iki öğrenci de kendi sınavının ortalamasının 1,5 standart "
            "sapma üzerindedir: göreli konumları aynıdır (§5.7)."
        ),
    ),
    LabStep(
        number=7,
        title="Chebyshev eşitsizliği",
        note=NoteRef("5.8", objects=("Şekil 5.9",)),
        explanation=(
            "Dağılımın biçimi ne olursa olsun, $k > 1$ için gözlemlerin en az $1 - 1/k^2$ kadarı $\\bar{x} \\pm ks$ "
            "aralığındadır. Yaklaşık çan biçimli dağılımlarda ampirik kural daha güçlü bir yaklaşık bilgi verir: "
            "%68, %95 ve %99,7."
        ),
        operations=(
            Scalar("chebyshev_2", E.sub(1, E.div(1, E.power(2, 2))), "k = 2: en az 1 − 1/2²", decimals=2),
            Scalar("chebyshev_3", E.sub(1, E.div(1, E.power(3, 2))), "k = 3: en az 1 − 1/3²", decimals=3),
            ScalarTable(
                (
                    ("k = 2: Chebyshev (en az)", E.ref("chebyshev_2")),
                    ("k = 2: ampirik kural (yaklaşık)", E.const(0.95)),
                    ("k = 3: Chebyshev (en az)", E.ref("chebyshev_3")),
                    ("k = 3: ampirik kural (yaklaşık)", E.const(0.997)),
                ),
                "kurallar",
                decimals=3,
            ),
        ),
        checks=(
            _scalar("chebyshev_2", 0.75, "k = 2 için en az", 2),
            _scalar("chebyshev_3", 0.889, "k = 3 için en az 8/9", 3),
        ),
        takeaway=(
            "Chebyshev her dağılım için geçerli bir alt sınırdır (\"en az\"); ampirik kural yalnız yaklaşık çan "
            "biçimli dağılımlar için yaklaşık bir orandır. İkisinin kapsamı aynı değildir (§5.8). Sezgi sekmesindeki "
            "Deney 2 iki kuralı çarpık ve simetrik verilerde karşılaştırır."
        ),
    ),
    LabStep(
        number=8,
        title="IQR ile aykırı değer",
        note=NoteRef("5.9", objects=("Şekil 5.10",)),
        explanation=(
            "Sıralanmış gelir verisi 20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 65 ($n = 11$). Çeyrekler Konu 4'teki "
            "kuralla bulunur: $L_{25} = 0{,}25 \\times 12 = 3$ ve $L_{75} = 9$. Sınırlar $Q_1 - 1{,}5\\,IQR$ ve "
            "$Q_3 + 1{,}5\\,IQR$'dir; bunların dışındaki gözlemler aykırı değer adayıdır."
        ),
        operations=(
            _column("veri", "gelir", INCOME, "Sıralanmış gelir verisi"),
            Percentile("veri", "gelir", 25, "Q1", "Birinci çeyrek Q₁", location="L25", decimals=0),
            Percentile("veri", "gelir", 75, "Q3", "Üçüncü çeyrek Q₃", location="L75", decimals=0),
            Scalar("iqr", E.sub(E.ref("Q3"), E.ref("Q1")), "IQR = Q₃ − Q₁", decimals=0),
            Scalar("alt_sinir", E.sub(E.ref("Q1"), E.mul(1.5, E.ref("iqr"))), "Alt sınır Q₁ − 1,5·IQR", decimals=0),
            Scalar("ust_sinir", E.add(E.ref("Q3"), E.mul(1.5, E.ref("iqr"))), "Üst sınır Q₃ + 1,5·IQR", decimals=0),
            Derive(
                "veri", "aykiri",
                E.add(E.compare("lt", E.var("gelir"), E.ref("alt_sinir")),
                      E.compare("gt", E.var("gelir"), E.ref("ust_sinir"))),
                "Sınırların dışında mı? (1: evet, 0: hayır)",
            ),
            Statistic("veri", "aykiri", "sum", "aykiri_sayisi", "Aykırı değer adayı sayısı", decimals=0),
            DotPlot("veri", "gelir", "Gelir", "Aykırı değer sınırları",
                    references=(("alt_sinir", "Alt sınır"), ("ust_sinir", "Üst sınır")), x_range=INCOME_RANGE),
        ),
        checks=(
            _scalar("Q1", 23, "Q₁", 0),
            _scalar("Q3", 29, "Q₃", 0),
            _scalar("iqr", 6, "IQR = 29 − 23", 0),
            _scalar("alt_sinir", 14, "Alt sınır 23 − 1,5 × 6", 0),
            _scalar("ust_sinir", 38, "Üst sınır 29 + 1,5 × 6", 0),
            _scalar("aykiri_sayisi", 1, "Aykırı değer adayı sayısı (65)", 0),
        ),
        takeaway=(
            "65 üst sınırın (38) üzerindedir ve aykırı değer adayıdır. Bu bir silme emri değildir: gözlem doğruysa ve "
            "incelenen anakütleye aitse analizde kalır; önce nedeni araştırılır (§5.9)."
        ),
    ),
    LabStep(
        number=9,
        title="Beş sayı özeti ve kutu grafiği",
        note=NoteRef("5.10", objects=("Şekil 5.11",)),
        explanation=(
            "Beş sayı özeti: en küçük değer, $Q_1$, medyan, $Q_3$ ve en büyük değer. Kutu $Q_1$'den $Q_3$'e çizilir, "
            "içindeki çizgi medyandır. Bıyıklar sınırların içindeki en uç gözlemlere uzanır; sınırların dışındaki "
            "gözlemler ayrı noktalardır."
        ),
        operations=(
            BoxSummary((("veri", "gelir", "Gelir"),), "kutu"),
            BoxPlot((("veri", "gelir", "Gelir"),), "Gelir", "Veri seti", "Gelir verisinin kutu grafiği"),
        ),
        checks=(
            _box("en_kucuk", 20, "En küçük değer"),
            _box("q1", 23, "Q₁"),
            _box("medyan", 26, "Medyan"),
            _box("q3", 29, "Q₃"),
            _box("en_buyuk", 65, "En büyük değer"),
            _box("ust_biyik", 30, "Sağ bıyık ucu: aykırı olmayan en büyük değer"),
        ),
        code_note=(
            "matplotlib'in boxplot ve R'nin boxplot fonksiyonları çeyrekleri kendi kurallarıyla hesaplar ve bu "
            "kural ders kuralından farklı olabilir. Kod, kutuyu ders kuralıyla bulunan özetten çizer."
        ),
        takeaway=(
            "Beş sayı özeti 20, 23, 26, 29, 65'tir; ama üst bıyık 65'e değil aykırı olmayan en büyük değer olan 30'a "
            "uzanır ve 65 ayrı bir nokta olarak gösterilir. Uzun sağ taraf ve tek uç nokta sağa çarpıklığın işaretidir "
            "(§5.10)."
        ),
    ),
    LabStep(
        number=10,
        title="Kovaryans",
        note=NoteRef("5.11", objects=("Tablo 5.2", "Şekil 5.13")),
        explanation=(
            "Beş haftada reklam sayısı $x$ ve satış $y$ (bin TL). Her hafta için sapmaların çarpımı "
            "$(x_i - \\bar{x})(y_i - \\bar{y})$ hesaplanır; örneklem kovaryansı bu çarpımların toplamının "
            "$n - 1$'e bölümüdür: $s_{xy} = \\sum (x_i - \\bar{x})(y_i - \\bar{y}) / (n - 1)$."
        ),
        operations=(
            InlineData("haftalar", ("hafta", "reklam", "satis"), ADVERTISING, "Tablo 5.2: reklam sayısı ve satış"),
            Statistic("haftalar", "reklam", "mean", "ortalama_x", "Ortalama x̄", decimals=0),
            Statistic("haftalar", "satis", "mean", "ortalama_y", "Ortalama ȳ (bin TL)", decimals=0),
            Derive("haftalar", "carpim",
                   E.mul(E.sub(E.var("reklam"), E.ref("ortalama_x")), E.sub(E.var("satis"), E.ref("ortalama_y"))),
                   "Sapmaların çarpımı (xᵢ − x̄)(yᵢ − ȳ)"),
            Statistic("haftalar", "carpim", "sum", "carpim_toplami", "Çarpımların toplamı", decimals=0),
            Statistic("haftalar", "reklam", "count", "n_hafta", "Hafta sayısı n", decimals=0),
            Scalar("kovaryans", E.div(E.ref("carpim_toplami"), E.sub(E.ref("n_hafta"), 1)),
                   "Kovaryans s_xy = toplam/(n − 1)", decimals=2),
            PairStatistic("haftalar", "reklam", "satis", "cov", "kovaryans_yazilim", "Yazılımın kovaryans fonksiyonu",
                          decimals=2),
            ScatterPlot("haftalar", "reklam", "satis", "Reklam sayısı", "Satış (bin TL)",
                        "Reklam sayısı ve satış: serpilme diyagramı"),
        ),
        checks=(
            _scalar("ortalama_x", 3, "Ortalama x̄", 0),
            _scalar("ortalama_y", 25, "Ortalama ȳ", 0),
            _scalar("kovaryans", 6.75, "Kovaryans s_xy", 2),
            _scalar("kovaryans_yazilim", 6.75, "Yazılımla kovaryans", 2),
        ),
        takeaway=(
            "Beş haftanın hiçbirinde çarpım negatif değildir: reklamın ortalamanın üstünde olduğu haftalarda satış da "
            "ortalamanın üstündedir. Kovaryansın işareti yönü gösterir; büyüklüğü ise ölçü birimine bağlıdır (§5.11)."
        ),
    ),
    LabStep(
        number=11,
        title="Korelasyon katsayısı",
        note=NoteRef("5.12", objects=("Şekil 5.15",)),
        explanation=(
            "Kovaryans iki standart sapmaya bölünerek ölçekten bağımsız hâle gelir: $r_{xy} = s_{xy}/(s_x s_y)$. "
            "Değer her zaman $-1$ ile $1$ arasındadır."
        ),
        operations=(
            Statistic("haftalar", "reklam", "std", "std_x", "Reklam: s_x", decimals=2),
            Statistic("haftalar", "satis", "std", "std_y", "Satış: s_y (bin TL)", decimals=2),
            Scalar("korelasyon", E.div(E.ref("kovaryans"), E.mul(E.ref("std_x"), E.ref("std_y"))),
                   "Korelasyon r = s_xy/(s_x s_y)", decimals=2),
            PairStatistic("haftalar", "reklam", "satis", "corr", "korelasyon_yazilim",
                          "Yazılımın korelasyon fonksiyonu", decimals=2),
        ),
        checks=(
            _scalar("std_x", 1.58, "s_x", 2),
            _scalar("std_y", 4.30, "s_y", 2),
            _scalar("korelasyon", 0.99, "Korelasyon r", 2),
            _scalar("korelasyon_yazilim", 0.99, "Yazılımla korelasyon", 2),
        ),
        takeaway=(
            "r ≈ 0,99: örneklemde çok güçlü pozitif doğrusal ilişki. Bu, reklamın satışa neden olduğunu tek başına "
            "göstermez; korelasyon betimsel bir doğrusal ilişki ölçüsüdür. Eğrisel bir ilişkide r sıfıra yakın "
            "olabilir (§5.12; Sezgi sekmesi, Deney 3)."
        ),
    ),
    LabStep(
        number=12,
        title="Tek sayı yerine istatistiksel profil",
        note=NoteRef("5.13", objects=("Şekil 5.18", "Tablo 5.3")),
        explanation=(
            "Raporlama ilkesi: ortalamanın yanında standart sapma veya IQR, dağılımın biçimini gösteren bir grafik ve "
            "aykırı değer bilgisi verilir. Gelir verisinin profilini bu bölümün ölçüleriyle birlikte çıkaralım. "
            "Buradaki sayılar notlarda basılı değildir; önceki adımların sonuçlarından hesaplanır."
        ),
        operations=(
            Statistic("veri", "gelir", "mean", "gelir_ortalama", "Ortalama", decimals=2),
            Statistic("veri", "gelir", "median", "gelir_medyan", "Medyan", decimals=0),
            Statistic("veri", "gelir", "std", "gelir_std", "Standart sapma s", decimals=2),
            Statistic("veri", "gelir", "max", "gelir_max", "En büyük değer", decimals=0),
            Statistic("veri", "gelir", "min", "gelir_min", "En küçük değer", decimals=0),
            ScalarTable(
                (
                    ("Ortalama", E.ref("gelir_ortalama")),
                    ("Medyan", E.ref("gelir_medyan")),
                    ("Standart sapma s", E.ref("gelir_std")),
                    ("IQR", E.ref("iqr")),
                    ("Değişim aralığı", E.sub(E.ref("gelir_max"), E.ref("gelir_min"))),
                ),
                "profil",
                decimals=2,
            ),
        ),
        takeaway=(
            "Tek bir uç gözlem (65) ortalamayı medyanın üzerine çeker, standart sapmayı ve değişim aralığını büyütür; "
            "IQR ise orta %50'ye dayandığı için etkilenmez. Bu yüzden bu veri için medyan ve IQR, kutu grafiği ve "
            "aykırı değer notuyla birlikte raporlanır (§5.13)."
        ),
    ),
)

KONU05_LAB = LabSpec(
    topic_key="konu05",
    title="Değişkenlik, dağılım ve ilişki ölçülerini hesaplamak",
    note_section="5",
    steps=STEPS,
    labels=(
        ("sure", DAYS_AXIS),
        ("x", "Gözlem xᵢ"),
        ("sapma", "Sapma xᵢ − x̄"),
        ("sapma_kare", "Kareli sapma (xᵢ − x̄)²"),
        ("gelir", "Gelir"),
        ("aykiri", "Aykırı değer adayı (1: evet)"),
        ("hafta", "Hafta"),
        ("reklam", "Reklam sayısı x"),
        ("satis", "Satış y (bin TL)"),
        ("carpim", "(xᵢ − x̄)(yᵢ − ȳ)"),
    ),
)
