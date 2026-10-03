"""Betimsel tabloların ve kategorik çekilişlerin hesabı (Streamlit'ten bağımsız).

Buradaki her fonksiyon, üretilen Python kodundaki satırlarla aynı işlem sırasını izler:
uygulamanın sayısı ile öğrencinin çalıştıracağı kodun sayısı bit düzeyinde aynıdır.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from decimal import Decimal
from itertools import combinations, permutations, product

import numpy as np
import pandas as pd
from scipy import stats

from core.labs.spec import BOX_ROWS, CLASS_COLUMNS, COUNT_DISTRIBUTIONS, DENSITIES, TOTAL, TOTALLED_CLASS_COLUMNS


def inline_frame(columns: Sequence[str], rows: Sequence[Sequence[object]]) -> pd.DataFrame:
    """Satır demetlerinden veri çerçevesi; her sütun kendi türünde (metin veya sayı)."""

    widths = {len(row) for row in rows}
    if widths != {len(columns)}:
        raise ValueError("Her satırda sütun sayısı kadar değer olmalıdır.")
    return pd.DataFrame({name: [row[position] for row in rows] for position, name in enumerate(columns)})


def from_counts(columns: Sequence[str], rows: Sequence[Sequence[object]]) -> pd.DataFrame:
    """Sayım tablosunun her satırını ``sayi`` kez tekrarlayarak gözlem düzeyinde veri kurar."""

    counts = pd.DataFrame([tuple(row) for row in rows], columns=[*columns, "sayi"])
    if (counts["sayi"] < 0).any():
        raise ValueError("Sayılar negatif olamaz.")
    return counts.loc[counts.index.repeat(counts["sayi"]), list(columns)].reset_index(drop=True)


def outcomes(stages: Sequence[tuple[str, Sequence[object]]]) -> pd.DataFrame:
    """Aşamaların seçeneklerinin bütün bileşimleri; ilk aşama en yavaş değişir (``itertools.product``)."""

    names = [name for name, _ in stages]
    return pd.DataFrame(list(product(*[list(values) for _, values in stages])), columns=names)


def selections(items: Sequence[str], k: int, ordered: bool, columns: Sequence[str]) -> pd.DataFrame:
    """``items`` içinden ``k`` öğenin kombinasyonları (sıra önemsiz) ya da permütasyonları, sözlük sırasıyla."""

    if len(columns) != k:
        raise ValueError("Her seçim sırası için bir sütun adı gerekir.")
    chosen = permutations(items, k) if ordered else combinations(items, k)
    return pd.DataFrame(list(chosen), columns=list(columns))


def frequency_table(values: pd.Series, order: Sequence[object], *, relative: bool = True,
                    totals: bool = False) -> pd.DataFrame:
    """Frekans dağılımı: f, r = f/n ve p = 100 r; kategoriler ``order`` sırasıyla.

    ``order`` sayılardan oluşuyorsa (ör. iki zarın toplamı 2, 3, …, 12) değerler sayı olarak eşleştirilir.
    """

    numeric = all(isinstance(item, (int, float)) and not isinstance(item, bool) for item in order)
    present = set(values.dropna()) if numeric else set(values.dropna().astype(str))
    unknown = sorted(str(value) for value in present - set(order))
    if unknown:
        raise ValueError("Sırada olmayan kategori: " + ", ".join(unknown))
    table = values.value_counts().reindex(list(order), fill_value=0).to_frame("frekans")
    table.index.name = values.name
    if relative:
        table["goreli"] = table["frekans"] / table["frekans"].sum()
        table["yuzde"] = 100 * table["goreli"]
    if totals:
        table.loc[TOTAL] = table.sum()
    return table


def crosstab(frame: pd.DataFrame, row: str, column: str, row_order: Sequence[str], column_order: Sequence[str], *,
             percent: str | None = None, margins: bool = False, weights: str | None = None) -> pd.DataFrame:
    """Çapraz tablo: sayılar, satır yüzdeleri (payda satır toplamı) veya sütun yüzdeleri (payda sütun toplamı).

    ``weights`` verilirse hücreler o sütunun toplamıdır (ör. örnek noktaların olasılıkları).
    """

    if weights is None:
        counts = pd.crosstab(frame[row], frame[column])
    else:
        if percent is not None:
            raise ValueError("Ağırlıklı çapraz tablo yalnız toplamları verir (percent=None).")
        counts = pd.crosstab(frame[row], frame[column], values=frame[weights], aggfunc="sum").fillna(0)
    counts = counts.reindex(index=list(row_order), columns=list(column_order), fill_value=0)
    if percent is None:
        table = counts
        if margins:
            table.loc[TOTAL] = table.sum()
            table[TOTAL] = table.sum(axis=1)
    elif percent == "satir":
        table = counts.div(counts.sum(axis=1), axis=0) * 100
        if margins:
            table[TOTAL] = table.sum(axis=1)
    elif percent == "sutun":
        table = counts.div(counts.sum(axis=0), axis=1) * 100
        if margins:
            table.loc[TOTAL] = table.sum()
    else:
        raise ValueError(f"Desteklenmeyen yüzde türü: {percent}")
    table.index.name = row
    table.columns.name = column
    return table


def boundary_label(value: float) -> str:
    """Sınıf sınırının yazımı: en çok 10 anlamlı basamak, ondalık virgül. R'de ``trimws(formatC(v, format = "fg",
    digits = 10, decimal.mark = ","))`` aynı metni verir."""

    return f"{value:.10g}".replace(".", ",")


def _short_places(value: float) -> int | None:
    """Kısa bir değerin ondalık basamağı, uzun değerde ``None``. Kısa değer şu yazımlardan biriyle az basamaklıdır:
    12 anlamlı basamağa yuvarlanınca en çok 10 basamak (son basamaklarında kayan nokta gürültüsü olan değer:
    243,35999999999999 → 243,36); en kısa yazımı (repr) 15'ten az anlamlı basamak (yüklenen veri, 0,03125 gibi tam
    sonuçlar); 15 anlamlı basamağa yuvarlanınca en çok 13 basamak (13 basamaklı bir sonuç ve gürültüsü:
    −2,1541280961449997 → −2,154128096145). Bölmeyle bulunan değerler (17/21 = 0,8095…, 15 basamakta tek sıfırla biter)
    uzundur."""

    for text, limit in ((f"{value:.12g}", 10), (repr(value), 14), (f"{value:.15g}", 13)):
        digits = Decimal(text).normalize().as_tuple()
        if len(digits.digits) <= limit:
            return max(0, -digits.exponent)
    return None


def frame_decimals(values) -> int:
    """Notlar dışındaki kaynaklarda kesirli bir veri çerçevesi sütununun ekrandaki basamağı (en az 2, en çok 15).

    Sütunun en büyük değerinin 10⁻¹²'sinden küçük değerler kayan nokta artığıdır (x = μ iken 1e-30) ve sıfır sayılır.
    Bütün değerler kısaysa (``_short_places``: veri ya da tam sonuçlar) sütun tam yazılır. Aksi hâlde uzun bir sütundur
    (bölmeyle bulunan değerler): en az 4 basamak ve en küçük değerin 3 anlamlı basamağı, en çok 13 anlamlı basamak (en
    büyük değere göre). Uzun bir sütundaki tek tek kısa görünen değerler basamağı uzatmaz: hesaplanan bir değerin kısa
    görünmesi rastlantı olabilir. Genel uygulamalar metnin andığı ya da tam görünmesi gereken sütunların basamağını
    kesin değerlerden kurar (``ShowFrame.decimals``)."""

    finite = [float(value) for value in values if np.isfinite(value)]
    largest = max((abs(value) for value in finite), default=0.0)
    nonzero = [value for value in finite if abs(value) > 1e-12 * largest]
    if not nonzero:
        return 2
    places = [_short_places(value) for value in nonzero]
    if all(place is not None for place in places):
        return min(15, max(2, *places))
    cap = max(0, 12 - math.floor(math.log10(largest)))
    smallest = min(abs(value) for value in nonzero)
    return min(15, cap, max(4, 2 - math.floor(math.log10(smallest))))


def decimal_places(value: float, limit: int = 10) -> int:
    """Bir sayıyı tam gösteren en az ondalık basamak (0,25 → 2; 10 → 0; 520000000,75 → 2); en çok ``limit``.

    Sayının en kısa ondalık yazımından (``repr``) okunur; büyük sayılarda da kesirli kısım kaybolmaz.
    """

    value = float(value)
    if not math.isfinite(value) or value == 0:
        return 0
    exponent = Decimal(repr(value)).normalize().as_tuple().exponent
    return min(limit, max(0, -int(exponent)))


def class_edges(values: pd.Series, width: float, lower: float | None = None,
                classes: int | None = None) -> np.ndarray:
    """Eşit genişlikli sınıf sınırları: a, a + h, ..., a + k·h.

    ``lower`` verilmezse a, en küçük değeri içeren h katıdır (⌊min/h⌋·h) ve k en büyük değeri kapsayan
    en küçük sınıf sayısıdır (⌊(max − a)/h⌋ + 1); böylece her gözlem bir sınıfa düşer.

    ``lower`` verildiğinde ve genişlik ondalıklıysa sınırlar genişliğin ondalık basamağına yuvarlanır: 0,2 + 0,1
    kayan noktada 0,30000000000000004 olur; sınır tam 0,3 olmalıdır ki 0,3 değerindeki gözlem kendi sınıfına düşsün.
    Kod bu sınırları değişmez olarak yazar; iki dil aynı ondalık sayıyı okur.
    """

    if width <= 0:
        raise ValueError("Sınıf genişliği pozitif olmalıdır.")
    if lower is None:
        x = values.to_numpy(dtype=float)
        lower = np.floor(x.min() / width) * width
        classes = int(np.floor((x.max() - lower) / width)) + 1
    elif classes is None or classes < 1:
        raise ValueError("Alt sınır verildiğinde sınıf sayısı da verilmelidir.")
    else:
        digits = max(decimal_places(width), decimal_places(lower))
        if digits:
            return np.round(lower + width * np.arange(classes + 1), digits)
    return lower + width * np.arange(classes + 1)


def class_table(values: pd.Series, edges: np.ndarray, columns: Sequence[str], *, totals: bool = False,
                row_labels: str = "sinif") -> pd.DataFrame:
    """Sınıflara göre frekans dağılımı; sınıflar [alt, üst): alt sınır dahil, üst sınır hariç.

    Göreli frekans ve yüzde, sınıflara düşen gözlem sayısına (n) bölünür. Hesap sırası üretilen Python
    koduyla aynıdır (``pd.cut(..., right=False)``).
    """

    unknown = sorted(set(columns) - set(CLASS_COLUMNS))
    if unknown:
        raise ValueError("Tanınmayan sınıf tablosu sütunu: " + ", ".join(unknown))
    edges = np.asarray(edges, dtype=float)
    lower, upper = edges[:-1], edges[1:]
    counts = pd.cut(values, bins=edges, right=False).value_counts(sort=False).to_numpy()
    if row_labels == "sinif":
        labels = [f"{boundary_label(a)} ≤ x < {boundary_label(b)}" for a, b in zip(lower, upper)]
    elif row_labels == "ust":
        labels = [f"x < {boundary_label(b)}" for b in upper]
    else:
        raise ValueError(f"Desteklenmeyen satır adı türü: {row_labels}")
    table = pd.DataFrame({"alt": lower, "ust": upper}, index=pd.Index(labels, name="sinif"))
    n = counts.sum()
    computed = {"frekans": counts}
    computed["orta_nokta"] = (lower + upper) / 2
    computed["goreli"] = counts / n
    computed["yuzde"] = 100 * computed["goreli"]
    computed["kumulatif_frekans"] = np.cumsum(counts)
    computed["kumulatif_goreli"] = computed["kumulatif_frekans"] / n
    computed["kumulatif_yuzde"] = 100 * computed["kumulatif_goreli"]
    for column in CLASS_COLUMNS:
        if column in columns:
            table[column] = computed[column]
    if totals:
        summed = [column for column in TOTALLED_CLASS_COLUMNS if column in table.columns]
        table.loc[TOTAL] = table[summed].sum()
    return table


_PLACES = ("birler", "onlar", "yüzler", "binler", "on binler", "yüz binler", "milyonlar", "on milyonlar",
           "yüz milyonlar", "milyarlar", "on milyarlar", "yüz milyarlar", "trilyonlar", "on trilyonlar",
           "yüz trilyonlar")


def stem_unit_text(unit: int) -> str:
    """Yaprak biriminin Türkçe yazımı: 10^unit (1, 10, 100, 0,1, 0,01, …)."""

    return str(10 ** unit) if unit >= 0 else "0," + "0" * (-unit - 1) + "1"


def stem_leaf_place(unit: int) -> str:
    """Yaprağın hangi basamak olduğu (yaprak birimi 10^unit): "onlar basamağı", "2. ondalık basamak"."""

    if unit >= 0:
        return f"{_PLACES[unit]} basamağı" if unit < len(_PLACES) else f"10^{unit} basamağı"
    return f"{-unit}. ondalık basamak"


def stem_unit_note(unit: int) -> str:
    """Üretilen koddaki açıklama: yaprak hangi basamak, gövde ne, hangi basamaklar atılır."""

    return f"yaprak {stem_leaf_place(unit)}, gövde ondan önceki basamaklar; daha küçük basamaklar kesilir"


def stem_leaf_units(values, decimals: int = 0, unit: int = 0) -> np.ndarray:
    """Sıralı değerlerin yaprak birimi cinsinden tam sayı karşılığı (gövde × 10 + yaprak).

    Notlardaki gösterimde (``decimals = unit = 0``) değerler negatif olmayan tam sayılardır. Diğer durumlarda değer
    10^decimals ile çarpılıp tam sayıya yuvarlanır (tam sayıya en yakın; yarımlar çifte) ve 10^(decimals + unit)
    ile tam bölünür: yaprak biriminden küçük basamaklar kesilir (yaprak birimi 10 iken 1565 → 156).
    """

    x = np.sort(np.asarray(values, dtype=float))
    if np.any(x < 0):
        raise ValueError("Gövde–yaprak gösterimi için negatif olmayan değerler gerekir.")
    if decimals == 0 and unit == 0:
        if np.any(x != np.round(x)):
            raise ValueError("Gövde–yaprak gösterimi için negatif olmayan tam sayılar gerekir.")
        return x.astype(np.int64)
    if decimals < 0 or unit < -decimals:
        raise ValueError("Yaprak birimi verinin ondalık hassasiyetinden ince olamaz.")
    scaled = np.round(x * 10.0 ** decimals) if decimals else x
    if np.any(scaled != np.round(scaled)) or np.any(scaled >= 2.0 ** 53):
        raise ValueError("Değerler bu ondalık basamakla tam sayıya çevrilemiyor.")
    divisor = 10.0 ** (decimals + unit)
    return (scaled // divisor).astype(np.int64) if divisor != 1 else scaled.astype(np.int64)


def stem_leaf(values: pd.Series, decimals: int = 0, unit: int = 0) -> pd.DataFrame:
    """Gövde ve yapraklar; boş gövdeler de satır olarak yer alır. Notlarda gövde onlar, yaprak birler basamağıdır;
    ``unit`` ve ``decimals`` için ``stem_leaf_units``."""

    whole = stem_leaf_units(values, decimals, unit)
    stems, leaves = whole // 10, whole % 10
    rows = range(int(stems.min()), int(stems.max()) + 1)
    return pd.DataFrame(
        {
            "yapraklar": [" ".join(str(leaf) for leaf in leaves[stems == stem]) for stem in rows],
            "yaprak_sayisi": [int((stems == stem).sum()) for stem in rows],
        },
        index=pd.Index([str(stem) for stem in rows], name="govde"),
    )


def percentile_location(n: int, p: float, method: str = "ders") -> float:
    """Yüzdelik konumu: ders kuralı L_p = (p/100)(n + 1); yazılım varsayılanı 1 + (p/100)(n − 1)."""

    if method == "ders":
        return p / 100 * (n + 1)
    if method == "yazilim":
        return 1 + p / 100 * (n - 1)
    raise ValueError(f"Desteklenmeyen yüzdelik yöntemi: {method}")


def percentile(values, p: float, method: str = "ders") -> float:
    """p. yüzdelik. ``ders``: L_p konumunda doğrusal ara değer, uçlarda en küçük/en büyük gözlem
    (Hyndman–Fan tip 6). ``yazilim``: ``np.percentile`` varsayılanı (tip 7)."""

    x = np.sort(np.asarray(values, dtype=float))
    n = len(x)
    if n == 0:
        raise ValueError("Veri seti boş olamaz.")
    if method == "yazilim":
        return float(np.percentile(x, p))
    location = percentile_location(n, p, method)
    if location <= 1:
        return float(x[0])
    if location >= n:
        return float(x[-1])
    k = int(np.floor(location))
    return float(x[k - 1] + (location - k) * (x[k] - x[k - 1]))


def box_summary(values, fence_decimals: int | None = None) -> pd.Series:
    """Kutu grafiği özeti (``BOX_ROWS``): beş sayı özeti ders kuralıyla, IQR, 1,5·IQR sınırları, bıyık uçları.

    Bıyıklar sınırların içindeki en küçük ve en büyük gözleme uzanır; sınırların dışındaki gözlemler aykırı
    değer adaylarıdır. Üretilen koddaki ``kutu_ozeti`` fonksiyonuyla aynı işlem sırası. ``fence_decimals``: sınırlar
    sınıflamadan önce bu basamağa yuvarlanır (``BoxSummary.fence_decimals``).
    """

    x = np.sort(np.asarray(values, dtype=float))
    q1, medyan, q3 = percentile(x, 25), percentile(x, 50), percentile(x, 75)
    iqr = q3 - q1
    alt, ust = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    if fence_decimals is not None:
        alt, ust = np.round(alt, fence_decimals), np.round(ust, fence_decimals)
    icerde = x[(x >= alt) & (x <= ust)]
    values_by_row = {
        "en_kucuk": x[0], "q1": q1, "medyan": medyan, "q3": q3, "en_buyuk": x[-1], "iqr": iqr,
        "alt_sinir": alt, "ust_sinir": ust, "alt_biyik": icerde.min(), "ust_biyik": icerde.max(),
        "aykiri_sayisi": float(((x < alt) | (x > ust)).sum()),
    }
    return pd.Series([float(values_by_row[row]) for row in BOX_ROWS], index=list(BOX_ROWS))


def outliers(values, summary: pd.Series) -> np.ndarray:
    """Q₁ − 1,5·IQR ve Q₃ + 1,5·IQR sınırlarının dışındaki gözlemler (veri sırasıyla)."""

    x = np.asarray(values, dtype=float)
    return x[(x < summary["alt_sinir"]) | (x > summary["ust_sinir"])]


def map_codes(values: pd.Series, mapping: Sequence[tuple[str, float]]) -> pd.Series:
    codes = values.map(dict(mapping))
    if codes.isna().any():
        missing = sorted(set(values[codes.isna()].astype(str)))
        raise ValueError("Kodu tanımlanmamış kategori: " + ", ".join(missing))
    return codes.astype(float)


def thresholds(probabilities: Sequence[float]) -> np.ndarray:
    """Birikimli olasılıklar; sonuncusu yuvarlama hatasına karşı tam 1 yapılır."""

    values = np.asarray(probabilities, dtype=float)
    if np.any(values < 0) or not np.isclose(values.sum(), 1.0):
        raise ValueError("Olasılıklar negatif olmamalı ve toplamı 1 olmalıdır.")
    edges = np.cumsum(values)
    edges[-1] = 1.0
    return edges


def draw_categories(frame: pd.DataFrame, u: np.ndarray, categories: Sequence[str],
                    probabilities, by: Sequence[str]) -> np.ndarray:
    """u ~ Tek-düze(0, 1) değerlerinden kategoriler: birikimli olasılığı u'yu ilk aşan kategori."""

    labels = np.asarray(categories, dtype=object)
    result = np.full(len(frame), None, dtype=object)
    for condition, probs in probabilities:
        if len(probs) != len(categories):
            raise ValueError("Her kategori için bir olasılık gerekir.")
        selected = np.ones(len(frame), dtype=bool)
        for column, value in zip(by, condition):
            selected &= (frame[column] == value).to_numpy()
        result[selected] = labels[np.searchsorted(thresholds(probs), u[selected], side="right")]
    if any(value is None for value in result):
        raise ValueError("Bazı gözlemler için olasılık tanımlanmamış.")
    return result


def draw_discrete(u: np.ndarray, values: Sequence[float], probabilities: Sequence[float]) -> np.ndarray:
    """Ters dağılım fonksiyonu: X, birikimli olasılığı F(x) u'yu ilk aşan değerdir (``np.searchsorted``, sağ)."""

    if len(values) != len(probabilities):
        raise ValueError("Her değer için bir olasılık gerekir.")
    return np.asarray(values, dtype=float)[np.searchsorted(thresholds(probabilities), u, side="right")]


def tree_layout(frame: pd.DataFrame, first: str, second: str, first_p: str, second_p: str) -> pd.DataFrame:
    """İki aşamalı olasılık ağacının yolları ve çizim konumları (soldan sağa: kök 0, ilk aşama 1, yollar 2).

    Her satır bir tam yoldur; ilk yol en üstte (``y_yol = n − 1, …, 0``). İlk aşamadaki bir dal, kendi yollarının
    ortasında durur (``y_ilk``). ``ortak`` yolun ortak olasılığıdır: ilk dalın olasılığı × ikinci dalın koşullu
    olasılığı. Üretilen koddaki ağaç çizimiyle aynı kural.
    """

    paths = pd.DataFrame({
        "ilk": frame[first].astype(str).to_numpy(),
        "ikinci": frame[second].astype(str).to_numpy(),
        "p_ilk": frame[first_p].to_numpy(dtype=float),
        "p_ikinci": frame[second_p].to_numpy(dtype=float),
    })
    for name, group in paths.groupby("ilk", sort=False):
        if group["p_ilk"].nunique() != 1:
            raise ValueError(f"'{name}' dalının olasılığı her yolda aynı olmalıdır.")
    paths["ortak"] = paths["p_ilk"] * paths["p_ikinci"]
    paths["y_yol"] = np.arange(len(paths))[::-1].astype(float)
    paths["y_ilk"] = paths.groupby("ilk", sort=False)["y_yol"].transform("mean")
    return paths


def support(lower: int, upper: int) -> np.ndarray:
    """Kesikli değişkenin olası değerleri lower, …, upper (``np.arange(lower, upper + 1)``)."""

    if int(lower) != lower or int(upper) != upper or upper < lower:
        raise ValueError("Olası değerler lower ≤ upper olan tam sayılardır.")
    return np.arange(int(lower), int(upper) + 1)


def rectangle_midpoints(lower: float, width: float, count: int) -> np.ndarray:
    """Dikdörtgenlerin orta noktaları lower + width·(i − 0,5), i = 1, …, count (üretilen kodla aynı işlem sırası)."""

    return lower + width * (np.arange(1, count + 1) - 0.5)


def density(distribution: str, first: float, second: float, x) -> np.ndarray:
    """Yoğunluk f(x): normal (μ = first, σ = second), tek-düze U(a = first, b = second), üstel (ortalama süre
    μ = first, σ = second = μ) ya da gamma (biçim k = first, oran r = second)."""

    if distribution not in DENSITIES:
        raise ValueError(f"Desteklenmeyen yoğunluk: {distribution}")
    if distribution == "normal":
        if second <= 0:
            raise ValueError("Standart sapma pozitif olmalıdır.")
        return stats.norm.pdf(x, first, second)
    if distribution == "exponential":
        if first <= 0 or second != first:
            raise ValueError("Üstel dağılımda ortalama süre μ pozitiftir ve σ = μ'dür.")
        return stats.expon.pdf(x, scale=first)
    if distribution == "gamma":
        if first <= 0 or second <= 0:
            raise ValueError("Gamma dağılımında biçim ve oran pozitif olmalıdır.")
        return stats.gamma.pdf(x, first, scale=1 / second)
    if second <= first:
        raise ValueError("Tek-düze dağılımda b > a olmalıdır.")
    return stats.uniform.pdf(x, first, second - first)


def density_grid(distribution: str, first: float, second: float, x_range: tuple[float, float],
                 points: int = 401) -> pd.DataFrame:
    """Yoğunluk grafiğinin eğrisi: yatay eksende eşit aralıklı ``points`` nokta ve f(x)."""

    low, high = x_range
    if not low < high:
        raise ValueError("Yatay eksenin alt sınırı üst sınırından küçük olmalıdır.")
    x = np.linspace(low, high, points)
    return pd.DataFrame({"x": x, "f": density(distribution, first, second, x)})


def draw_count(rng: np.random.Generator, distribution: str, parameters: Sequence[float], size: int) -> np.ndarray:
    """Sayım çekilişi, üretilen Python koduyla aynı çağrı: ``rng.binomial``, ``rng.poisson`` ya da
    ``rng.hypergeometric``."""

    if COUNT_DISTRIBUTIONS.get(distribution) != len(parameters):
        raise ValueError(f"{distribution}: parametre sayısı uygun değil.")
    if distribution == "binomial":
        n, p = parameters
        return rng.binomial(int(n), p, size=size).astype(float)
    if distribution == "poisson":
        return rng.poisson(parameters[0], size=size).astype(float)
    population, successes, draws = (int(value) for value in parameters)
    if not 0 <= successes <= population or not 0 <= draws <= population:
        raise ValueError("Hipergeometrik: 0 ≤ r ≤ N ve 0 ≤ n ≤ N olmalıdır.")
    return rng.hypergeometric(successes, population - successes, draws, size=size).astype(float)
