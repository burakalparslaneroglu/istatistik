"""IKT 217 konu sırası. Başlıklar ders notlarındaki bölüm adlarıdır."""

from __future__ import annotations

from core.types import TopicMetadata

TOPICS: tuple[TopicMetadata, ...] = (
    TopicMetadata(
        "konu01", 1, "Veri ve İstatistiğe Giriş", "Veri ve İstatistiğe Giriş",
        "Bir veri tablosundaki sayılar neyi temsil eder ve hangi sorulara cevap verebilir?",
    ),
    TopicMetadata(
        "konu02", 2, "Kategorik Verilerin Tablo ve Grafiklerle Özetlenmesi", "Kategorik Verilerin Özetlenmesi",
        "Kategorik bir veri seti hangi tablo ve grafikle, hangi paydayla doğru özetlenir?",
    ),
    TopicMetadata("konu03", 3, "Nicel Verilerin Tablo ve Grafiklerle Özetlenmesi", "Nicel Verilerin Özetlenmesi"),
    TopicMetadata("konu04", 4, "Merkezi Eğilim ve Konum Ölçüleri", "Merkezi Eğilim ve Konum Ölçüleri"),
    TopicMetadata("konu05", 5, "Değişkenlik, Dağılım ve İlişki", "Değişkenlik, Dağılım ve İlişki"),
    TopicMetadata("konu06", 6, "Olasılığın Temelleri", "Olasılığın Temelleri"),
    TopicMetadata(
        "konu07", 7, "Koşullu Olasılık, Bağımsızlık ve Bayes Teoremi", "Koşullu Olasılık, Bağımsızlık ve Bayes",
    ),
    TopicMetadata(
        "konu08", 8, "Rassal Değişkenler ve Kesikli Olasılık Dağılımları",
        "Rassal Değişkenler ve Kesikli Dağılımlar",
    ),
    TopicMetadata("konu09", 9, "Binom, Poisson ve Hipergeometrik Dağılımlar", "Binom, Poisson ve Hipergeometrik"),
    TopicMetadata(
        "konu10", 10, "Sürekli Rassal Değişkenler, Tek-Düze ve Normal Dağılım",
        "Sürekli Rassal Değişkenler ve Normal Dağılım",
    ),
    TopicMetadata("konu11", 11, "Normal Olasılıklar ve Üstel Dağılım", "Normal Olasılıklar ve Üstel Dağılım"),
    TopicMetadata(
        "konu12", 12, "Örnekleme, Nokta Tahmini ve Örnekleme Dağılımları", "Örnekleme ve Örnekleme Dağılımları",
    ),
)

_BY_KEY = {topic.key: topic for topic in TOPICS}


def list_topics() -> tuple[TopicMetadata, ...]:
    return TOPICS


def get_topic(key: str) -> TopicMetadata:
    try:
        return _BY_KEY[key]
    except KeyError as error:
        raise KeyError(f"Tanımsız konu: {key}") from error
