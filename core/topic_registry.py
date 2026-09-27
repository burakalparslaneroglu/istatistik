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
    TopicMetadata(
        "konu03", 3, "Nicel Verilerin Tablo ve Grafiklerle Özetlenmesi", "Nicel Verilerin Özetlenmesi",
        "Nicel bir değişkenin değerleri nerede yoğunlaşır ve bunu hangi sınıflarla, hangi grafikle göstermeliyiz?",
    ),
    TopicMetadata(
        "konu04", 4, "Merkezi Eğilim ve Konum Ölçüleri", "Merkezi Eğilim ve Konum Ölçüleri",
        "Bir veri setinin merkezini hangi ölçü en iyi özetler ve bir gözlemin göreli konumu nasıl belirlenir?",
    ),
    TopicMetadata(
        "konu05", 5, "Değişkenlik, Dağılımın Şekli ve İki Değişken Arasındaki İlişki", "Değişkenlik, Dağılım ve İlişki",
        "Aynı merkeze sahip veri setleri nasıl ayırt edilir ve iki nicel değişkenin birlikte hareketi nasıl ölçülür?",
    ),
    TopicMetadata(
        "konu06", 6, "Olasılığın Temelleri", "Olasılığın Temelleri",
        "Belirsiz bir sonucun ne ölçüde mümkün olduğunu nasıl sayısallaştırırız ve olayların olasılıkları nasıl "
        "birleşir?",
    ),
    TopicMetadata(
        "konu07", 7, "Koşullu Olasılık, Bağımsızlık ve Bayes Teoremi", "Koşullu Olasılık, Bağımsızlık ve Bayes",
        "Bir olayın gerçekleştiğini öğrendiğimizde diğer olayın olasılığı değişir mi ve gözlenen bir sonuçtan "
        "kaynağına nasıl geri akıl yürütürüz?",
    ),
    TopicMetadata(
        "konu08", 8, "Rassal Değişkenler ve Kesikli Olasılık Dağılımları",
        "Rassal Değişkenler ve Kesikli Dağılımlar",
        "Bir deneyin sayısal sonucunun olası değerlerine olasılıklar nasıl dağılır ve bu dağılımın merkezi, "
        "yayılımı ve iki değişkenin birlikte hareketi nasıl ölçülür?",
    ),
    TopicMetadata(
        "konu09", 9, "Binom, Poisson ve Hipergeometrik Dağılımlar", "Binom, Poisson ve Hipergeometrik",
        "Bir sayım hangi deney yapısından doğar, buna göre binom, Poisson ve hipergeometrik modellerden hangisi "
        "seçilir ve olasılıkları, beklenen değeri ve varyansı nasıl hesaplanır?",
    ),
    TopicMetadata(
        "konu10", 10, "Sürekli Rassal Değişkenler, Tek-Düze ve Normal Dağılım",
        "Sürekli Rassal Değişkenler ve Normal Dağılım",
        "Sürekli bir değişkende olasılık neden eğri altındaki alandır ve normal dağılımda z-dönüşümü farklı "
        "ölçekleri nasıl ortak bir dile çevirir?",
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
