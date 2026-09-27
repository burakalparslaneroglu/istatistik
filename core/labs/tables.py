"""Betimsel tabloların ve kategorik çekilişlerin hesabı (Streamlit'ten bağımsız).

Buradaki her fonksiyon, üretilen Python kodundaki satırlarla aynı işlem sırasını izler:
uygulamanın sayısı ile öğrencinin çalıştıracağı kodun sayısı bit düzeyinde aynıdır.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd

from core.labs.spec import CLASS_COLUMNS, TOTAL, TOTALLED_CLASS_COLUMNS


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


def frequency_table(values: pd.Series, order: Sequence[str], *, relative: bool = True,
                    totals: bool = False) -> pd.DataFrame:
    """Frekans dağılımı: f, r = f/n ve p = 100 r; kategoriler ``order`` sırasıyla."""

    unknown = sorted(set(values.dropna().astype(str)) - set(order))
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
             percent: str | None = None, margins: bool = False) -> pd.DataFrame:
    """Çapraz tablo: sayılar, satır yüzdeleri (payda satır toplamı) veya sütun yüzdeleri (payda sütun toplamı)."""

    counts = pd.crosstab(frame[row], frame[column]).reindex(
        index=list(row_order), columns=list(column_order), fill_value=0
    )
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


def class_edges(values: pd.Series, width: float, lower: float | None = None,
                classes: int | None = None) -> np.ndarray:
    """Eşit genişlikli sınıf sınırları: a, a + h, ..., a + k·h.

    ``lower`` verilmezse a, en küçük değeri içeren h katıdır (⌊min/h⌋·h) ve k en büyük değeri kapsayan
    en küçük sınıf sayısıdır (⌊(max − a)/h⌋ + 1); böylece her gözlem bir sınıfa düşer.
    """

    if width <= 0:
        raise ValueError("Sınıf genişliği pozitif olmalıdır.")
    if lower is None:
        x = values.to_numpy(dtype=float)
        lower = np.floor(x.min() / width) * width
        classes = int(np.floor((x.max() - lower) / width)) + 1
    elif classes is None or classes < 1:
        raise ValueError("Alt sınır verildiğinde sınıf sayısı da verilmelidir.")
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


def stem_leaf(values: pd.Series) -> pd.DataFrame:
    """Gövde (onlar basamağı) ve yapraklar (birler basamağı); boş gövdeler de satır olarak yer alır."""

    x = np.sort(values.to_numpy(dtype=float))
    if np.any(x < 0) or np.any(x != np.round(x)):
        raise ValueError("Gövde–yaprak gösterimi için negatif olmayan tam sayılar gerekir.")
    whole = x.astype(int)
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
    """u ~ Tekdüze(0, 1) değerlerinden kategoriler: birikimli olasılığı u'yu ilk aşan kategori."""

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
