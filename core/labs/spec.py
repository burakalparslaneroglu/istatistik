"""Ders notu uygulamalarının dilden bağımsız tanım şeması.

Bir uygulama tanımı dört şeyi birlikte besler:

1. Uygulama sekmesindeki adım adım anlatım,
2. Uygulamanın kendi hesabı (``core.labs.runner``),
3. Python ve R kodu (``core.codegen``),
4. Notlardaki sayılarla karşılaştıran testler.

Bir sayı veya işlem yalnız burada değişir; diğer dört çıktı kendiliğinden izler.

Adlandırma: ``frame`` gözlem düzeyindeki bir veri çerçevesidir (her satır bir gözlem);
``table`` ise bir sonuç tablosudur (satır adları kategoriler, sütunlar sayılar).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Union

from core.labs.expr import Expr


class ReproClass(str, Enum):
    """İki dilde (Python ve R) aynı sayının hangi anlamda beklenebileceği."""

    EXACT = "birebir"
    CONVENTION = "ayar"
    DISTRIBUTIONAL = "dagilim"


REPRO_DESCRIPTIONS = {
    ReproClass.EXACT: (
        "Birebir aynı",
        "Deterministik hesap. Python ve R aynı sayıyı ondalık düzeyinde verir.",
    ),
    ReproClass.CONVENTION: (
        "Ayar sabitlenince aynı",
        "Paketlerin varsayılan ayarları farklı. Kodda ayar açıkça sabitlendiği için sonuç aynıdır; "
        "varsayılan ayarla çalıştırırsanız farklı sayı görebilirsiniz.",
    ),
    ReproClass.DISTRIBUTIONAL: (
        "Yalnız dağılımda aynı",
        "Rastgele çekiliş içerir. Python ve R farklı rastgele sayı üreteci kullandığı için aynı tohum aynı "
        "çekilişi vermez; sonuçlar rastgele çekiliş farkı kadar değişir.",
    ),
}

STATISTICS = (
    "count", "sum", "mean", "median", "mode", "mode_freq", "prod", "min", "max", "var", "std", "nunique", "value",
)
"""``value``: koşulu sağlayan tek gözlemin değeri (ör. A mağazasının memnuniyeti). ``mode``: tek mod
(birden fazla değer en yüksek frekansa sahipse hata); ``mode_freq``: modun frekansı; ``prod``: çarpım;
``var`` ve ``std``: örneklem varyansı s² ve standart sapması s (payda n − 1); ``nunique``: farklı değer sayısı."""
PAIR_STATISTICS = ("cov", "corr")
"""İki değişkenli istatistikler: örneklem kovaryansı s_xy (payda n − 1) ve Pearson korelasyonu r."""
DISTRIBUTIONS = ("normal", "uniform", "beta", "gamma")
BOX_ROWS = (
    "en_kucuk", "q1", "medyan", "q3", "en_buyuk", "iqr", "alt_sinir", "ust_sinir", "alt_biyik", "ust_biyik",
    "aykiri_sayisi",
)
"""Kutu grafiği özetinin satırları: beş sayı özeti (çeyrekler ders kuralıyla), IQR, Q₁ − 1,5·IQR ve
Q₃ + 1,5·IQR sınırları, sınırların içindeki en uç gözlemler (bıyık uçları) ve aykırı değer sayısı."""
PERCENT_KINDS = (None, "satir", "sutun")
CLASS_COLUMNS = (
    "orta_nokta", "frekans", "goreli", "yuzde", "kumulatif_frekans", "kumulatif_goreli", "kumulatif_yuzde",
)
"""Sınıf tablosunun seçilebilir sütunları; ``alt`` ve ``ust`` her zaman vardır."""
TOTALLED_CLASS_COLUMNS = ("frekans", "goreli", "yuzde")
PERCENTILE_METHODS = ("ders", "yazilim")
"""``ders``: L_p = (p/100)(n + 1) ve doğrusal ara değer (Hyndman–Fan tip 6); ``yazilim``: numpy ve R'nin
varsayılanı (tip 7), 1 + (n − 1)p/100 konumu."""
TOTAL = "Toplam"
"""Frekans ve çapraz tablolarda toplam satırının/sütununun adı (iki dilde aynı)."""


# --- Veri ------------------------------------------------------------------

@dataclass(frozen=True)
class InlineData:
    """Ders notlarında basılı küçük veri seti; kodda satır içinde yazılır.

    ``rows`` her gözlem için bir demettir. ``layout`` verilirse (tek sütunlu veride)
    kod ve ekran değerleri notlardaki tablo gibi satır başına ``layout`` değer dizer.
    """

    frame: str
    columns: tuple[str, ...]
    rows: tuple[tuple[object, ...], ...]
    comment: str
    layout: int | None = None


@dataclass(frozen=True)
class FromCounts:
    """Sayım tablosundan gözlem düzeyinde veri: sayım tablosunun her satırı ``sayı`` kez tekrarlanır.

    ``rows`` her satır için (kategoriler..., sayı) demetidir.
    """

    frame: str
    columns: tuple[str, ...]
    rows: tuple[tuple[object, ...], ...]
    comment: str


@dataclass(frozen=True)
class VariableTypes:
    """Değişkenlerin notlardaki istatistiksel türü ve yazılımın onları saklama biçimi.

    ``rows``: (değişken, istatistiksel tür, ayrıntı). Yazılımın saklama türü veriden okunur.
    """

    frame: str
    rows: tuple[tuple[str, str, str], ...]
    result: str


@dataclass(frozen=True)
class Outcomes:
    """Çok aşamalı bir deneyin bütün sonuçları: aşamalardaki seçeneklerin bütün bileşimleri.

    ``stages``: (sütun adı, seçenekler). Satırlar ağaç diyagramındaki sırayla gelir: ilk aşama en yavaş,
    son aşama en hızlı değişir. Satır sayısı çarpım kuralıyla n₁·n₂·…·n_k'dir.
    """

    frame: str
    stages: tuple[tuple[str, tuple[object, ...]], ...]
    comment: str


@dataclass(frozen=True)
class Selections:
    """``items`` içinden ``k`` öğenin bütün seçimleri, sözlük sırasıyla.

    ``ordered=False``: sıra önemsiz, kombinasyonlar (C(N, k) satır); ``ordered=True``: sıra veya görev önemli,
    permütasyonlar (P(N, k) satır). ``columns`` k sütunun adlarıdır (ör. başkan, raportör).
    """

    frame: str
    items: tuple[str, ...]
    k: int
    ordered: bool
    columns: tuple[str, ...]
    comment: str


@dataclass(frozen=True)
class Event:
    """Olay: örnek uzayın bir alt kümesi. ``column`` değeri ``values`` içinde olan satırlarda 1, diğerlerinde 0.

    Satırlar örnek noktalar (ya da simülasyonda tek tek denemeler) olduğunda yeni sütun olayın gösterge
    değişkenidir; olayın olasılığı bu göstergeyle seçilen örnek noktaların olasılıkları toplanarak bulunur.
    """

    frame: str
    name: str
    column: str
    values: tuple[object, ...]
    comment: str


@dataclass(frozen=True)
class ShowFrame:
    """Bir veri çerçevesinin seçili sütunlarını gösterir (ör. örnek uzay ve olayların gösterge sütunları)."""

    frame: str
    columns: tuple[str, ...]
    comment: str


@dataclass(frozen=True)
class MapCodes:
    """Kategori etiketlerini sayı kodlarına çevirir (ör. Kaldı = 0, Geçti = 1)."""

    frame: str
    source: str
    name: str
    mapping: tuple[tuple[str, float], ...]
    comment: str


@dataclass(frozen=True)
class Groups:
    """Gözlemleri sırayla gruplara ayırır: ilk ``sizes[0]`` gözlem ``labels[0]`` grubunda, ..."""

    frame: str
    name: str
    labels: tuple[str, ...]
    sizes: tuple[int, ...]
    comment: str


@dataclass(frozen=True)
class Derive:
    """İfadeden yeni bir sayısal değişken türetir."""

    frame: str
    name: str
    expr: Expr
    comment: str


# --- Simülasyon ------------------------------------------------------------

@dataclass(frozen=True)
class NewSample:
    """Simülasyon için ``nobs`` satırlık boş örneklem.

    ``seed`` verilirse rastgele sayı üreteci bu tohumla (yeniden) başlatılır. ``seed=None`` yalnız Monte
    Carlo döngüsü içinde kullanılır: üreteç döngüden önce bir kez tohumlanır, her tekrar yeni çekiliş yapar.
    Deneyde tek bir üreteç vardır; bütün çekilişler işlem sırasıyla ondan yapılır.
    """

    frame: str
    nobs: int
    seed: int | None


@dataclass(frozen=True)
class Draw:
    """Sayısal rastgele değişken: normal(ortalama, std. sapma), uniform(alt, üst), beta(a, b) veya
    gamma(biçim, ölçek)."""

    frame: str
    name: str
    distribution: str
    first: float
    second: float
    comment: str


@dataclass(frozen=True)
class DrawCategory:
    """Kategorik rastgele değişken.

    Her gözlem için u ~ Tekdüze(0, 1) çekilir; kategori, birikimli olasılığı u'yu ilk aşan kategoridir
    (birikimli olasılıkların sonuncusu 1 kabul edilir). ``by`` verilirse olasılıklar o değişkenlerin
    kategorilerine göre değişir: ``probabilities`` (koşul etiketleri, olasılıklar) çiftleridir;
    ``by`` boşsa tek çift vardır ve etiketler boş demettir.
    """

    frame: str
    name: str
    categories: tuple[str, ...]
    probabilities: tuple[tuple[tuple[str, ...], tuple[float, ...]], ...]
    comment: str
    by: tuple[str, ...] = ()


# --- Sayma ve özet ---------------------------------------------------------

@dataclass(frozen=True)
class Shape:
    """Gözlem sayısı ``n`` ve değişken sayısı ``k``; ``exclude`` sütunları (kimlik) sayılmaz."""

    frame: str
    observations: str
    variables: str
    exclude: tuple[str, ...] = ()


@dataclass(frozen=True)
class Count:
    """``column == value`` koşulunu sağlayan gözlem sayısı."""

    frame: str
    name: str
    column: str
    value: object
    comment: str


@dataclass(frozen=True)
class Statistic:
    """Bir değişkenin tek istatistiği, skaler olarak (isteğe bağlı olarak bir alt grupta)."""

    frame: str
    variable: str
    stat: str
    name: str
    comment: str
    where: tuple[str, object] | None = None
    decimals: int = 4


@dataclass(frozen=True)
class PairStatistic:
    """İki sayısal değişkenin örneklem kovaryansı (``cov``: payda n − 1) ya da Pearson korelasyonu (``corr``)."""

    frame: str
    x: str
    y: str
    stat: str
    name: str
    comment: str
    decimals: int = 4


@dataclass(frozen=True)
class Scalar:
    """Skalerlerden (``E.ref``) ve sabitlerden hesaplanan tek sayı.

    ``percent``: değer yüzde biriminde; ekranda yüzde işaretiyle gösterilir.
    """

    name: str
    expr: Expr
    comment: str
    decimals: int = 4
    percent: bool = False


@dataclass(frozen=True)
class ScalarTable:
    """Birkaç skaleri tek tabloda toplar (satırlar etiketler, tek sütun ``deger``)."""

    rows: tuple[tuple[str, Expr], ...]
    result: str
    decimals: int = 2


@dataclass(frozen=True)
class GroupSummary:
    """Bir kategorik değişkenin gruplarına göre özet: (sütun adı, değişken, istatistik)."""

    frame: str
    by: str
    columns: tuple[tuple[str, str, str], ...]
    result: str
    order: tuple[object, ...]


@dataclass(frozen=True)
class FrequencyTable:
    """Kategorik değişkenin frekans dağılımı.

    Sütunlar: ``frekans`` (f), ``relative`` ise ``goreli`` (r = f/n) ve ``yuzde`` (p = 100 r).
    Kategoriler ``order`` sırasıyla; ``totals`` ise sonda ``Toplam`` satırı.
    """

    frame: str
    variable: str
    result: str
    order: tuple[str, ...]
    relative: bool = True
    totals: bool = False


@dataclass(frozen=True)
class CrossTab:
    """İki kategorik değişkenin çapraz tablosu.

    ``percent``: None sayılar; ``satir`` satır yüzdeleri (her satır 100'e toplanır); ``sutun`` sütun
    yüzdeleri. ``margins``: sayı tablosunda ``Toplam`` satırı ve sütunu; satır yüzdelerinde ``Toplam``
    sütunu, sütun yüzdelerinde ``Toplam`` satırı. ``where`` verilirse yalnız o alt gruptaki gözlemler.
    ``weights`` verilirse hücreler gözlem sayısı değil o sütunun toplamıdır (ör. ortak olasılık tablosu:
    her örnek noktanın olasılığı kendi hücresine yazılır); yalnız ``percent=None`` ile kullanılır.
    """

    frame: str
    row: str
    column: str
    result: str
    row_order: tuple[str, ...]
    column_order: tuple[str, ...]
    percent: str | None = None
    margins: bool = False
    where: tuple[str, object] | None = None
    decimals: int = 1
    weights: str | None = None


@dataclass(frozen=True)
class JoinColumns:
    """Aynı satır adlarına sahip tabloların sütunlarını tek tabloda yan yana toplar.

    ``columns``: (yeni sütun adı, tablo, sütun). Satırlar ilk tablonun sırasıyladır.
    """

    result: str
    columns: tuple[tuple[str, str, str], ...]
    decimals: int = 3
    percent: bool = False


@dataclass(frozen=True)
class BoxSummary:
    """Kutu grafiği özeti (``BOX_ROWS``): her seri için bir sütun.

    ``series``: (veri çerçevesi, değişken, etiket). Çeyrekler ders kuralıyla (L_p = (p/100)(n + 1)); bıyıklar
    Q₁ − 1,5·IQR ve Q₃ + 1,5·IQR sınırlarının içindeki en küçük ve en büyük gözleme kadar uzanır.
    """

    series: tuple[tuple[str, str, str], ...]
    result: str


@dataclass(frozen=True)
class ClassTable:
    """Nicel bir değişkenin eşit genişlikli sınıflarla frekans dağılımı.

    Sınıflar [a, a + h), [a + h, a + 2h), ...: alt sınır dahil, üst sınır hariç (notlardaki 10 ≤ x < 20
    yazımı). ``lower`` verilirse ``classes`` sınıf oradan başlar; verilmezse ilk sınıf en küçük değeri
    içeren h katından başlar ve sınıf sayısı en büyük değeri kapsayacak kadardır.

    Tabloda ``alt`` ve ``ust`` sütunları her zaman vardır; ``columns`` diğerlerini seçer (``CLASS_COLUMNS``):
    orta nokta m = (alt + üst)/2, frekans f, göreli frekans r = f/n, yüzde p = 100 r, kümülatif frekans
    F, F/n ve kümülatif yüzde. Satır adları "10 ≤ x < 20"; ``row_labels="ust"`` ise "x < 20" (kümülatif
    tablo). ``totals`` sonda ``Toplam`` satırı ekler (frekans, göreli ve yüzde sütunlarının toplamı).
    """

    frame: str
    variable: str
    result: str
    width: float
    columns: tuple[str, ...]
    lower: float | None = None
    classes: int | None = None
    totals: bool = False
    row_labels: str = "sinif"


@dataclass(frozen=True)
class StemLeaf:
    """Gövde–yaprak gösterimi: gövde onlar basamağı, yaprak birler basamağı (negatif olmayan tam sayılar).

    Sonuç tablosunun satırları gövdelerdir (en küçükten en büyüğe, boş gövdeler dahil); sütunlar
    ``yapraklar`` (küçükten büyüğe, boşlukla ayrılmış) ve ``yaprak_sayisi``.
    """

    frame: str
    variable: str
    result: str


@dataclass(frozen=True)
class Percentile:
    """p. yüzdelik ``name`` skalerine yazılır; ``location`` verilirse konum da skaler olur.

    ``method="ders"``: L_p = (p/100)(n + 1); L_p tam sayı değilse komşu iki gözlem arasında doğrusal ara
    değer; L_p ≤ 1 ise en küçük, L_p ≥ n ise en büyük gözlem (Hyndman–Fan tip 6). ``method="yazilim"``:
    numpy ve R'nin varsayılanı (tip 7), konum 1 + (n − 1)p/100.
    """

    frame: str
    variable: str
    p: float
    name: str
    comment: str
    location: str | None = None
    method: str = "ders"
    decimals: int = 2


# --- Grafikler -------------------------------------------------------------

@dataclass(frozen=True)
class BarChart:
    """Tek serili sütun grafiği.

    ``source`` bir sonuç tablosudur (kategoriler satır adları) ya da ``x`` verilirse bir veri
    çerçevesidir (kategoriler ``x`` sütunu). ``Toplam`` satırı çizilmez. ``sort="azalan"``
    sütunları yüksekten düşüğe dizer; ``y_range`` değer ekseninin sınırlarıdır (yanıltıcı
    eksen örneği için). ``percent``: değer etiketleri yüzde işaretiyle.
    """

    source: str
    y: str
    x_label: str
    y_label: str
    title: str
    x: str | None = None
    sort: str | None = None
    horizontal: bool = False
    y_range: tuple[float, float] | None = None
    percent: bool = False
    decimals: int = 0


@dataclass(frozen=True)
class GroupedBarChart:
    """Çapraz tablodan çok serili sütun grafiği: yan yana veya yığılmış (yüzde 100).

    ``series="satir"``: her tablo satırı bir seri, sütunlar yatay eksende; ``"sutun"``: tersi.
    ``Toplam`` satırı ve sütunu çizilmez. ``labels=False``: çok sayıda sütunda değer etiketleri yazılmaz (değerler
    tabloda gösterilir).
    """

    table: str
    x_label: str
    y_label: str
    title: str
    series: str = "satir"
    stacked: bool = False
    decimals: int = 0
    labels: bool = True


@dataclass(frozen=True)
class CompareBarChart:
    """Birkaç tablonun aynı sütununu yan yana karşılaştırır.

    ``tables``: (yatay eksendeki etiket, tablo adı); her tablonun satırları birer seridir.
    """

    tables: tuple[tuple[str, str], ...]
    column: str
    x_label: str
    y_label: str
    title: str
    decimals: int = 1


@dataclass(frozen=True)
class PieChart:
    """Dilim grafiği. Dilim açıları θ = 360°·r ``result`` tablosuna yazılır (sütun ``aci``).

    Dilimler ``order`` sırasıyla, 0°'den (saat 3 yönü) başlayarak saat yönünün tersine dizilir.
    """

    table: str
    column: str
    result: str
    title: str
    order: tuple[str, ...]


@dataclass(frozen=True)
class LineChart:
    """Bir veri çerçevesinde iki değişkenin çizgi grafiği (ör. zaman serisi).

    ``references``: (skaler adı, etiket) yatay çizgileri (ör. gerçek olasılık). ``markers``: noktalar
    işaretlenir; uzun serilerde (ör. birikimli oran) yalnız çizgi.
    """

    frame: str
    x: str
    y: str
    x_label: str
    y_label: str
    title: str
    references: tuple[tuple[str, str], ...] = ()
    markers: bool = True


@dataclass(frozen=True)
class ScatterPlot:
    """Serpilme diyagramı: her gözlem bir (x, y) noktası."""

    frame: str
    x: str
    y: str
    x_label: str
    y_label: str
    title: str


@dataclass(frozen=True)
class BoxPlot:
    """Yatay kutu grafiği; ``series`` ve kurallar ``BoxSummary`` ile aynıdır.

    Kutu Q₁'den Q₃'e, kutu içindeki çizgi medyandır; bıyıklar sınırların içindeki en uç gözlemlere uzanır,
    sınırların dışındaki gözlemler (aykırı değer adayları) ayrı noktalardır.
    """

    series: tuple[tuple[str, str, str], ...]
    x_label: str
    y_label: str
    title: str


@dataclass(frozen=True)
class Histogram:
    """Monte Carlo sonuç tablosundaki ya da bir veri çerçevesindeki sütunların histogramı; ``[lower, upper]``
    aralığında ``bins`` kutu.

    ``references``: (değer, etiket) dikey çizgileri (ör. gerçek anakütle değeri). Değer bir sayı ya da daha önce
    hesaplanmış bir skalerin adıdır (ör. örneklemden bulunan x̄ + 2s). ``y_label``: Monte Carlo tablosunda tekrar
    sayısı, veri çerçevesinde gözlem sayısı.
    """

    table: str
    columns: tuple[tuple[str, str], ...]
    bins: int
    lower: float
    upper: float
    title: str
    x_label: str
    references: tuple[tuple[float | str, str], ...] = ()
    y_label: str = "Tekrar sayısı"


@dataclass(frozen=True)
class ClassHistogram:
    """Sınıf tablosunun histogramı: sınıflar sayısal eksende bitişik dikdörtgenler.

    Dikdörtgenin genişliği sınıf genişliği, yüksekliği ``y`` sütunudur (frekans veya yüzde). ``Toplam``
    satırı çizilmez. ``labels``: değerler dikdörtgenlerin üstüne yazılır (``percent`` ise yüzde işaretiyle).
    """

    table: str
    y: str
    x_label: str
    y_label: str
    title: str
    labels: bool = False
    percent: bool = False
    decimals: int = 0


@dataclass(frozen=True)
class DotPlot:
    """Nokta grafiği: her gözlem bir nokta; aynı değerdeki gözlemler üst üste dizilir.

    ``references``: (skaler adı, etiket) dikey çizgileri (ör. ortalama, medyan). ``x_range``: yatay eksenin
    sınırları; iki veri setinin yayılımı karşılaştırılırken iki grafikte aynı eksen için (notlardaki gibi).
    """

    frame: str
    variable: str
    x_label: str
    title: str
    y_label: str = "Aynı değerdeki gözlem sayısı"
    references: tuple[tuple[str, str], ...] = ()
    x_range: tuple[float, float] | None = None


@dataclass(frozen=True)
class MonteCarlo:
    """``body`` işlemlerini ``reps`` kez tekrarlar; her tekrarda ``collect`` ifadelerini toplar.

    Rastgele sayı üreteci döngüden önce ``seed`` ile bir kez tohumlanır. Sonuç tablosunun her satırı
    bir tekrardır; sütunlar ``collect`` adlarıdır.
    """

    result: str
    reps: int
    seed: int
    body: tuple["Operation", ...]
    collect: tuple[tuple[str, Expr], ...]
    comment: str


Operation = Union[
    InlineData,
    FromCounts,
    Outcomes,
    Selections,
    VariableTypes,
    Event,
    ShowFrame,
    MapCodes,
    Groups,
    Derive,
    NewSample,
    Draw,
    DrawCategory,
    Shape,
    Count,
    Statistic,
    PairStatistic,
    Scalar,
    ScalarTable,
    GroupSummary,
    FrequencyTable,
    CrossTab,
    JoinColumns,
    BoxSummary,
    ClassTable,
    StemLeaf,
    Percentile,
    BarChart,
    GroupedBarChart,
    CompareBarChart,
    PieChart,
    LineChart,
    ScatterPlot,
    BoxPlot,
    Histogram,
    ClassHistogram,
    DotPlot,
    MonteCarlo,
]

CHARTS = (
    BarChart, GroupedBarChart, CompareBarChart, PieChart, LineChart, ScatterPlot, BoxPlot, Histogram, ClassHistogram,
    DotPlot,
)


# --- Notlarla karşılaştırma -------------------------------------------------

@dataclass(frozen=True)
class StatTarget:
    """Bir değişkenin (isteğe bağlı olarak bir alt gruptaki) istatistiği."""

    frame: str
    variable: str
    stat: str
    where: tuple[str, object] | None = None


@dataclass(frozen=True)
class ScalarTarget:
    name: str


@dataclass(frozen=True)
class TableTarget:
    """Bir sonuç tablosunun hücresi: satır adı ve sütun adı."""

    table: str
    row: str
    column: str


@dataclass(frozen=True)
class CellTarget:
    """Bir veri çerçevesinin ``row``'uncu gözleminin (1'den başlar) ``column`` değeri: xᵢ."""

    frame: str
    column: str
    row: int


Target = Union[StatTarget, ScalarTarget, TableTarget, CellTarget]


@dataclass(frozen=True)
class Check:
    """Notlarda basılı bir sayı ve onu üreten hesap. Tolerans, notlarda basılı basamak sayısıdır."""

    label: str
    target: Target
    expected: float
    decimals: int = 4

    @property
    def tolerance(self) -> float:
        if self.decimals <= 0:
            return 0.5
        return 0.5 * 10 ** (-self.decimals) + 1e-12


# --- Adım ve uygulama --------------------------------------------------------

@dataclass(frozen=True)
class NoteRef:
    section: str
    step: int = 0
    objects: tuple[str, ...] = ()

    def label(self) -> str:
        parts = [f"Notlar §{self.section}"]
        if self.step:
            parts.append(f"Adım {self.step}")
        parts.extend(self.objects)
        return " · ".join(parts)


@dataclass(frozen=True)
class LabStep:
    number: int
    title: str
    note: NoteRef
    explanation: str
    operations: tuple[Operation, ...] = ()
    checks: tuple[Check, ...] = ()
    reproducibility: ReproClass = ReproClass.EXACT
    takeaway: str = ""
    code_note: str = ""

    @property
    def key(self) -> str:
        return f"adim{self.number}"


@dataclass(frozen=True)
class LabSpec:
    """Bir konunun Uygulama sekmesi (``kind="uygulama"``) veya tek bir Sezgi deneyi (``kind="sezgi"``)."""

    topic_key: str
    title: str
    note_section: str
    steps: tuple[LabStep, ...]
    labels: tuple[tuple[str, str], ...] = field(default_factory=tuple)
    consistency_notes: tuple[str, ...] = field(default_factory=tuple)
    kind: str = "uygulama"

    def label(self, name: str) -> str:
        """Değişken, sütun veya tablo için öğrenciye gösterilecek Türkçe ad."""

        return dict(self.labels).get(name, name)

    def step(self, number: int) -> LabStep:
        for item in self.steps:
            if item.number == number:
                return item
        raise ValueError(f"Adım bulunamadı: {number}")

    def operations_through(self, number: int) -> tuple[Operation, ...]:
        """Bir adımı tek başına çalıştırmak için gereken bütün önceki işlemler."""

        collected: list[Operation] = []
        for item in self.steps:
            if item.number > number:
                break
            collected.extend(item.operations)
        return tuple(collected)
