import pytest

from core.topic03_logic import TRAVEL_TIMES, approximate_class_width, grouped_frequency, stem_leaf


def test_travel_time_dataset_matches_notes():
    assert len(TRAVEL_TIMES) == 40
    assert TRAVEL_TIMES.min() == 12
    assert TRAVEL_TIMES.max() == 76


def test_approximate_width_for_seven_classes():
    assert approximate_class_width(TRAVEL_TIMES, 7) == pytest.approx(64 / 7)


def test_ten_minute_frequency_distribution_matches_notes():
    grouped = grouped_frequency(TRAVEL_TIMES, 10)
    assert grouped["Frekans"].tolist() == [6, 10, 11, 5, 4, 2, 2]
    assert grouped["Frekans"].sum() == 40
    assert grouped.iloc[2]["Yüzde frekans"] == pytest.approx(27.5)


def test_cumulative_distribution_matches_notes():
    grouped = grouped_frequency(TRAVEL_TIMES, 10)
    assert grouped["Kümülatif frekans"].tolist() == [6, 16, 27, 32, 36, 38, 40]
    assert grouped.iloc[3]["Kümülatif yüzde"] == pytest.approx(80.0)
    assert grouped.iloc[-1]["Kümülatif yüzde"] == pytest.approx(100.0)


def test_stem_leaf_preserves_example_structure():
    result = dict(stem_leaf(TRAVEL_TIMES))
    assert result[1] == "2 3 5 7 8 8"
    assert result[3] == "0 1 2 3 4 5 5 6 7 8 9"
