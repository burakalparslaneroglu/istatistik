"""Betimsel tabloların ve kategorik çekilişlerin hesabı (Streamlit'ten bağımsız).

Buradaki her fonksiyon, üretilen Python kodundaki satırlarla aynı işlem sırasını izler:
uygulamanın sayısı ile öğrencinin çalıştıracağı kodun sayısı bit düzeyinde aynıdır.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd

from core.labs.spec import TOTAL


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
