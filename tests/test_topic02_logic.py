import pytest

from core.topic02_logic import (
    MATERIAL_CROSSTAB,
    TRANSPORT_FREQUENCIES,
    column_percentages,
    frequency_summary,
    row_percentages,
    simpson_rates,
)


def test_transport_frequency_summary_matches_notes():
    result = frequency_summary(TRANSPORT_FREQUENCIES, "Ulaşım biçimi")
    assert result["Frekans"].sum() == 40
    bus = result[result["Ulaşım biçimi"] == "Otobüs"].iloc[0]
    assert bus["Göreli frekans"] == pytest.approx(0.4)
    assert bus["Yüzde frekans"] == pytest.approx(40.0)


def test_row_percentages_match_notes():
    result = row_percentages(MATERIAL_CROSSTAB)
    assert result.loc["İktisat", "Dijital"] == pytest.approx(45.0)
    assert result.loc["İşletme", "Basılı"] == pytest.approx(50.0)
    assert result.sum(axis=1).tolist() == pytest.approx([100.0, 100.0])


def test_column_percentages_use_column_denominator():
    result = column_percentages(MATERIAL_CROSSTAB)
    assert result.loc["İktisat", "Dijital"] == pytest.approx(100 * 18 / 26)
    assert result.loc["İşletme", "Dijital"] == pytest.approx(100 * 8 / 26)


def test_simpson_example_matches_notes():
    rates = simpson_rates()
    easy_b = rates[(rates["Müşteri grubu"] == "Kolay") & (rates["Tasarım"] == "B")].iloc[0]
    hard_b = rates[(rates["Müşteri grubu"] == "Zor") & (rates["Tasarım"] == "B")].iloc[0]
    overall_a = rates[(rates["Müşteri grubu"] == "Tüm gruplar") & (rates["Tasarım"] == "A")].iloc[0]
    overall_b = rates[(rates["Müşteri grubu"] == "Tüm gruplar") & (rates["Tasarım"] == "B")].iloc[0]
    assert easy_b["Dönüşüm oranı"] == pytest.approx(95.0)
    assert hard_b["Dönüşüm oranı"] == pytest.approx(20.0)
    assert overall_a["Dönüşüm oranı"] == pytest.approx(100 * 91 / 110)
    assert overall_b["Dönüşüm oranı"] == pytest.approx(45.0)
