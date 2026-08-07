import pytest

from core.topic01_logic import (
    STUDENT_DATA,
    analytical_variable_count,
    classify_data_source,
    classify_inference,
    classify_time_structure,
    classify_variable,
    mean_exam_score,
    passing_rate,
)


def test_student_dataset_matches_course_notes():
    assert len(STUDENT_DATA) == 8
    assert analytical_variable_count() == 4
    assert mean_exam_score() == pytest.approx(64.0)
    assert passing_rate() == pytest.approx(5 / 8)


def test_variable_classifications():
    assert classify_variable("Bir öğrencinin bölümü") == ("Kategorik", "Nominal")
    assert classify_variable("Celsius cinsinden hava sıcaklığı") == ("Nicel – sürekli", "Aralık")
    assert classify_variable("Bir hanedeki otomobil sayısı") == ("Nicel – kesikli", "Oran")


def test_time_structure_classifications():
    assert classify_time_structure("2026 yılında 81 ilin işsizlik oranları") == "Yatay kesit"
    assert (
        classify_time_structure("Türkiye'nin 2010–2026 yılları arasındaki yıllık enflasyon oranı")
        == "Zaman serisi"
    )


def test_data_source_classifications():
    assert classify_data_source("Bir işletmenin geçen yılki satış kayıtlarını kullanmak") == "Mevcut kaynak"
    assert classify_data_source("200 müşteriye satın alma deneyimleri hakkında anket yapmak") == "Gözlemsel çalışma"


def test_inference_classifications():
    assert classify_inference("Ankete katılan 500 kişinin %54'ü ürünü beğendi.") == "Betimsel istatistik"
