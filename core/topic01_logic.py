from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


STUDENT_DATA = pd.DataFrame(
    {
        "Öğrenci": list("ABCDEFGH"),
        "Bölüm": ["İktisat", "İktisat", "İşletme", "İktisat", "İşletme", "İşletme", "İktisat", "İşletme"],
        "Haftalık çalışma (saat)": [4, 7, 5, 10, 8, 12, 6, 3],
        "Sınav puanı": [52, 64, 58, 76, 70, 84, 61, 47],
        "Ders durumu": ["Kaldı", "Geçti", "Kaldı", "Geçti", "Geçti", "Geçti", "Geçti", "Kaldı"],
    }
)


VARIABLE_EXAMPLES = {
    "Bir öğrencinin bölümü": ("Kategorik", "Nominal"),
    "Bir hanedeki otomobil sayısı": ("Nicel – kesikli", "Oran"),
    "Bir ürünün kilogram cinsinden ağırlığı": ("Nicel – sürekli", "Oran"),
    "Müşteri memnuniyeti: düşük / orta / yüksek": ("Kategorik", "Ordinal"),
    "Bir firmanın çalışan sayısı": ("Nicel – kesikli", "Oran"),
    "Bir öğrencinin okul numarası": ("Kategorik", "Nominal"),
    "Celsius cinsinden hava sıcaklığı": ("Nicel – sürekli", "Aralık"),
}


TIME_STRUCTURE_EXAMPLES = {
    "2026 yılında 81 ilin işsizlik oranları": "Yatay kesit",
    "Türkiye'nin 2010–2026 yılları arasındaki yıllık enflasyon oranı": "Zaman serisi",
    "Aynı gün 50 mağazanın günlük satış tutarı": "Yatay kesit",
    "Bir mağazanın son 24 aya ait aylık satışları": "Zaman serisi",
}


DATA_SOURCE_EXAMPLES = {
    "Bir işletmenin geçen yılki satış kayıtlarını kullanmak": "Mevcut kaynak",
    "200 müşteriye satın alma deneyimleri hakkında anket yapmak": "Gözlemsel çalışma",
    "Aynı reklamın iki tasarımını rastgele seçilmiş gruplara göstermek": "Deney",
    "Resmî kurumun yayımladığı nüfus verilerini kullanmak": "Mevcut kaynak",
}


INFERENCE_EXAMPLES = {
    "Ankete katılan 500 kişinin %54'ü ürünü beğendi.": "Betimsel istatistik",
    "Örneklem sonucuna göre şehirdeki seçmenlerin yaklaşık yarısının öneriyi desteklediği tahmin edilmektedir.": "İstatistiksel çıkarım",
    "İncelenen 20 firmanın ortalama çalışan sayısı 74'tür.": "Betimsel istatistik",
    "Örneklem verisinden hareketle sektördeki ortalama satışın 2 milyon TL civarında olduğu tahmin edilmektedir.": "İstatistiksel çıkarım",
}


@dataclass(frozen=True)
class SampleScenario:
    name: str
    description: str
    representativeness: str


SAMPLE_SCENARIOS = (
    SampleScenario(
        "Dengeli seçim",
        "Öğrenciler farklı bölüm ve ulaşım biçimlerinden dengeli biçimde seçiliyor.",
        "Temsil gücü görece yüksektir; yine de seçimin nasıl yapıldığı açıkça raporlanmalıdır.",
    ),
    SampleScenario(
        "Tek noktadan seçim",
        "Anket yalnızca kampüs otoparkının çıkışında uygulanıyor.",
        "Özel araç kullanan öğrenciler aşırı temsil edilebilir; büyük örneklem bu yanlılığı kendiliğinden gidermez.",
    ),
    SampleScenario(
        "Gönüllü çevrim içi anket",
        "Bağlantı tüm öğrencilere gönderiliyor ancak yalnızca isteyenler cevaplıyor.",
        "Yanıt verenlerle vermeyenler sistematik biçimde farklıysa gönüllü katılım yanlılığı oluşabilir.",
    ),
)


def analytical_variable_count() -> int:
    """Exclude the student ID/name column from the analytical variable count."""
    return STUDENT_DATA.shape[1] - 1


def passing_rate() -> float:
    return float((STUDENT_DATA["Ders durumu"] == "Geçti").mean())


def mean_exam_score() -> float:
    return float(STUDENT_DATA["Sınav puanı"].mean())


def classify_variable(example: str) -> tuple[str, str]:
    return VARIABLE_EXAMPLES[example]


def classify_time_structure(example: str) -> str:
    return TIME_STRUCTURE_EXAMPLES[example]


def classify_data_source(example: str) -> str:
    return DATA_SOURCE_EXAMPLES[example]


def classify_inference(example: str) -> str:
    return INFERENCE_EXAMPLES[example]
