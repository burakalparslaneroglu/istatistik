from __future__ import annotations

import pandas as pd


TRANSPORT_FREQUENCIES = pd.DataFrame(
    {
        "Ulaşım biçimi": ["Yürüme", "Otobüs", "Özel araç", "Bisiklet", "Raylı sistem"],
        "Frekans": [6, 16, 5, 3, 10],
    }
)

MATERIAL_CROSSTAB = pd.DataFrame(
    {
        "Basılı": [12, 10],
        "Dijital": [18, 8],
        "Her ikisi": [10, 2],
    },
    index=["İktisat", "İşletme"],
)

SIMPSON_DATA = pd.DataFrame(
    {
        "Müşteri grubu": ["Kolay", "Kolay", "Zor", "Zor"],
        "Tasarım": ["A", "B", "A", "B"],
        "Dönüşen": [90, 19, 1, 8],
        "Toplam": [100, 20, 10, 40],
    }
)

STUDY_RESOURCE_FREQUENCIES = pd.DataFrame(
    {
        "Kaynak": ["Ders notu", "Ders kitabı", "Video", "Soru çözümü", "Diğer"],
        "Frekans": [42, 18, 30, 24, 6],
    }
)


def frequency_summary(df: pd.DataFrame, category_col: str, frequency_col: str = "Frekans") -> pd.DataFrame:
    result = df[[category_col, frequency_col]].copy()
    total = int(result[frequency_col].sum())
    if total <= 0:
        raise ValueError("Toplam frekans pozitif olmalıdır.")
    result["Göreli frekans"] = result[frequency_col] / total
    result["Yüzde frekans"] = 100 * result["Göreli frekans"]
    return result


def row_percentages(table: pd.DataFrame) -> pd.DataFrame:
    denominators = table.sum(axis=1)
    if (denominators <= 0).any():
        raise ValueError("Satır toplamları pozitif olmalıdır.")
    return table.div(denominators, axis=0) * 100


def column_percentages(table: pd.DataFrame) -> pd.DataFrame:
    denominators = table.sum(axis=0)
    if (denominators <= 0).any():
        raise ValueError("Sütun toplamları pozitif olmalıdır.")
    return table.div(denominators, axis=1) * 100


def simpson_rates() -> pd.DataFrame:
    df = SIMPSON_DATA.copy()
    df["Dönüşüm oranı"] = 100 * df["Dönüşen"] / df["Toplam"]
    totals = (
        df.groupby("Tasarım", as_index=False)[["Dönüşen", "Toplam"]]
        .sum()
        .assign(**{"Müşteri grubu": "Tüm gruplar"})
    )
    totals["Dönüşüm oranı"] = 100 * totals["Dönüşen"] / totals["Toplam"]
    return pd.concat([df, totals[df.columns]], ignore_index=True)
