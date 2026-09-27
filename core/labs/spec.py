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

STATISTICS = ("count", "sum", "mean", "min", "max", "value")
"""``value``: koşulu sağlayan tek gözlemin değeri (ör. A mağazasının memnuniyeti)."""
PERCENT_KINDS = (None, "satir", "sutun")
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
    """Sayısal rastgele değişken: normal(ortalama, std. sapma) veya uniform(alt, üst)."""

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
    ``Toplam`` satırı ve sütunu çizilmez.
    """

    table: str
    x_label: str
    y_label: str
    title: str
    series: str = "satir"
    stacked: bool = False
    decimals: int = 0


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
    """Bir veri çerçevesinde iki değişkenin çizgi grafiği (ör. zaman serisi)."""

    frame: str
    x: str
    y: str
    x_label: str
    y_label: str
    title: str


@dataclass(frozen=True)
class Histogram:
    """Monte Carlo sonuç tablosundaki sütunların histogramı; ``[lower, upper]`` aralığında ``bins`` kutu.

    ``references``: (değer, etiket) dikey çizgileri (ör. gerçek anakütle değeri).
    """

    table: str
    columns: tuple[tuple[str, str], ...]
    bins: int
    lower: float
    upper: float
    title: str
    x_label: str
    references: tuple[tuple[float, str], ...] = ()


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
    VariableTypes,
    MapCodes,
    Groups,
    Derive,
    NewSample,
    Draw,
    DrawCategory,
    Shape,
    Count,
    Statistic,
    Scalar,
    ScalarTable,
    GroupSummary,
    FrequencyTable,
    CrossTab,
    BarChart,
    GroupedBarChart,
    CompareBarChart,
    PieChart,
    LineChart,
    Histogram,
    MonteCarlo,
]

CHARTS = (BarChart, GroupedBarChart, CompareBarChart, PieChart, LineChart, Histogram)


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
