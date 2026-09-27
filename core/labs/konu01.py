"""Konu 1 uygulaması: bir öğrenci veri setini okumak ve betimlemek.

Ders notlarının çözümlü örnekleri: §1.2 (Tablo 1.1), §1.3–1.4 (değişken türü ve ölçme düzeyi),
§1.5 (Şekil 1.4), §1.7 (geçme oranı ve ortalama puan), §1.11 (Tablo 1.3). Buradaki her ``Check``
notlarda basılı bir sayıdır; değer notlardan kopyalanmıştır, hesaplanmamıştır.
"""

from __future__ import annotations

from core.labs import expr as E
from core.labs.spec import (
    BarChart,
    CellTarget,
    Check,
    Count,
    InlineData,
    LabSpec,
    LabStep,
    LineChart,
    MapCodes,
    NoteRef,
    Scalar,
    ScalarTarget,
    Shape,
    Statistic,
    VariableTypes,
)

FRAME = "ogrenciler"

STUDENTS = (
    ("A", "İktisat", 4, 52, "Kaldı"),
    ("B", "İktisat", 7, 64, "Geçti"),
    ("C", "İşletme", 5, 58, "Kaldı"),
    ("D", "İktisat", 10, 76, "Geçti"),
    ("E", "İşletme", 8, 70, "Geçti"),
    ("F", "İşletme", 12, 84, "Geçti"),
    ("G", "İktisat", 6, 61, "Geçti"),
    ("H", "İşletme", 3, 47, "Kaldı"),
)
"""Tablo 1.1: öğrenci, bölüm, haftalık çalışma (saat), sınav puanı, ders durumu."""

PRICE_INDEX = ((1, 100), (2, 102), (3, 101), (4, 106), (5, 111), (6, 116), (7, 121), (8, 128))
"""Şekil 1.4 (sağ panel): aylık fiyat endeksi."""


def _cell(column: str, row: int, expected: float, label: str) -> Check:
    return Check(label, CellTarget(FRAME, column, row), expected, 0)


def _scalar(name: str, expected: float, label: str, decimals: int) -> Check:
    return Check(label, ScalarTarget(name), expected, decimals)


STEPS = (
    LabStep(
        number=1,
        title="Veri tablosu: gözlem, değişken, hücre",
        note=NoteRef("1.2", objects=("Tablo 1.1",)),
        explanation=(
            "Tablo 1.1'deki sekiz öğrenci satır satır yazılır. Her **satır** bir gözlemdir (bir öğrenci), "
            "her **sütun** bir değişkendir, her **hücre** bir değişken değeridir. Öğrenci sütunu yalnızca "
            "kimlik etiketidir; analitik değişken sayılmaz.\n\n"
            "Çalışma saatini $x$ ile gösterirsek $x_i$, $i$ numaralı öğrencinin çalışma saatidir: "
            "$x_1 = 4$, $x_2 = 7$, $\\ldots$, $x_8 = 3$. Alt indis hangi gözlemden söz ettiğimizi belirtir."
        ),
        operations=(
            InlineData(
                FRAME,
                ("ogrenci", "bolum", "saat", "puan", "durum"),
                STUDENTS,
                "Tablo 1.1: sekiz öğrencinin bölümü, haftalık çalışma saati, sınav puanı ve ders durumu",
            ),
            Shape(FRAME, "n", "k", exclude=("ogrenci",)),
        ),
        checks=(
            _scalar("n", 8, "Gözlem sayısı n", 0),
            _scalar("k", 4, "Analitik değişken sayısı", 0),
            _cell("saat", 1, 4, "x₁: A öğrencisinin çalışma saati"),
            _cell("saat", 2, 7, "x₂: B öğrencisinin çalışma saati"),
            _cell("saat", 8, 3, "x₈: H öğrencisinin çalışma saati"),
            _cell("saat", 4, 10, "D öğrencisinin çalışma saati"),
            _cell("puan", 4, 76, "D öğrencisinin sınav puanı"),
        ),
        takeaway=(
            "D öğrencisinin gözlemi tablonun 4. satırıdır: İktisat, 10 saat, 76 puan ve Geçti. "
            "Bir gözlem, tek bir birim için kaydedilen bütün değişken değerlerinin bütünüdür."
        ),
    ),
    LabStep(
        number=2,
        title="Değişken türü ve ölçme düzeyi",
        note=NoteRef("1.3–1.4", objects=("Tablo 1.2",)),
        explanation=(
            "Her değişkene aynı işlemi uygulayamayız: sınav puanlarının ortalaması anlamlıdır, "
            "İktisat ve İşletme etiketlerinin ortalaması anlamsızdır. Ders durumu "
            "$\\text{Kaldı} = 0$, $\\text{Geçti} = 1$ biçiminde kodlanır; bu kodlar yalnızca iki kategoriyi "
            "temsil eden etiketlerdir.\n\n"
            "Yazılım kodlu sütunu sayı olarak saklar. İstatistiksel tür ise yazılımdan değil, değişkenin "
            "anlamından gelir: aşağıdaki tabloda iki bilgi yan yana durur."
        ),
        operations=(
            MapCodes(FRAME, "durum", "durum_kod", (("Kaldı", 0), ("Geçti", 1)), "Kaldı = 0, Geçti = 1 kodlaması"),
            VariableTypes(
                FRAME,
                (
                    ("ogrenci", "Kimlik etiketi", "Analitik değişken sayılmaz"),
                    ("bolum", "Kategorik", "Nominal: kategoriler arasında sıra yok"),
                    ("saat", "Nicel", "Sürekli; oran ölçeği (süre, gerçek sıfır)"),
                    ("puan", "Nicel", "Farklar anlamlı: 80 ile 60 puan arasında 20 puan"),
                    ("durum", "Kategorik", "İki kategori: Kaldı, Geçti"),
                    ("durum_kod", "Kategorik", "0 ve 1 yalnızca etiket; miktar değildir"),
                ),
                "turler",
            ),
        ),
        checks=(
            _cell("durum_kod", 1, 0, "A öğrencisinin kodu (Kaldı)"),
            _cell("durum_kod", 2, 1, "B öğrencisinin kodu (Geçti)"),
        ),
        takeaway=(
            "Sayıyla yazılan her değişken nicel değildir. Ders durumu kodu sayı olarak saklanır; "
            "fakat 1'in 0'dan \"bir birim fazla\" olduğu biçiminde nicel yorum yapılmaz."
        ),
    ),
    LabStep(
        number=3,
        title="Yatay kesit ve zaman serisi",
        note=NoteRef("1.5", objects=("Şekil 1.4",)),
        explanation=(
            "Şekil 1.4'ün iki paneli yeniden çizilir. Solda aynı sınavda farklı öğrencilerin puanları "
            "(**yatay kesit**), sağda aynı fiyat endeksinin sekiz aylık seyri (**zaman serisi**) vardır. "
            "Endeks değerleri şekildeki koordinatlardır."
        ),
        operations=(
            BarChart(
                FRAME,
                "puan",
                "Öğrenci",
                "Sınav puanı",
                "Yatay kesit: aynı sınav, farklı öğrenciler",
                x="ogrenci",
            ),
            InlineData(
                "endeks",
                ("ay", "fiyat_endeksi"),
                PRICE_INDEX,
                "Şekil 1.4 (sağ panel): sekiz ayın fiyat endeksi",
            ),
            LineChart(
                "endeks", "ay", "fiyat_endeksi", "Ay", "Fiyat endeksi", "Zaman serisi: aynı değişken, farklı aylar",
            ),
        ),
        takeaway=(
            "Zaman serisinde gözlemlerin sırası bilgidir: 6. ay 5. aydan sonra gelir. Yatay kesitte "
            "A ve B öğrencilerinin tablodaki sırasını değiştirmek çoğu zaman verinin anlamını değiştirmez."
        ),
    ),
    LabStep(
        number=4,
        title="Betimsel istatistik: geçme oranı ve ortalama puan",
        note=NoteRef("1.7"),
        explanation=(
            "Dersi geçen öğrenciler sayılır; geçme oranı $5/8$, geçme yüzdesi $100 \\times 5/8$'dir. "
            "Puanların toplamı $\\sum x_i$ ve ortalaması $\\bar{x} = \\sum x_i / n$ ile bulunur "
            "(ortalama Konu 4'te ayrıntılı işlenir). Burada amaç, betimsel istatistiğin veriyi daha "
            "okunabilir bir sayıya dönüştürdüğünü görmektir."
        ),
        operations=(
            Count(FRAME, "gecen", "durum", "Geçti", "Dersi geçen öğrenci sayısı"),
            Scalar("gecme_orani", E.div(E.ref("gecen"), E.ref("n")), "Geçme oranı", decimals=3),
            Scalar(
                "gecme_yuzdesi",
                E.mul(100, E.div(E.ref("gecen"), E.ref("n"))),
                "Geçme yüzdesi",
                decimals=1,
                percent=True,
            ),
            Statistic(FRAME, "puan", "sum", "toplam_puan", "Sınav puanlarının toplamı", decimals=0),
            Scalar("ortalama_puan", E.div(E.ref("toplam_puan"), E.ref("n")), "Ortalama puan", decimals=1),
        ),
        checks=(
            _scalar("gecen", 5, "Dersi geçen öğrenci sayısı", 0),
            _scalar("gecme_orani", 0.625, "Geçme oranı 5/8", 3),
            _scalar("gecme_yuzdesi", 62.5, "Geçme yüzdesi", 1),
            _scalar("toplam_puan", 512, "Sınav puanlarının toplamı", 0),
            _scalar("ortalama_puan", 64, "Ortalama puan 512/8", 0),
        ),
        takeaway=(
            "%62,5 ve 64 puan yalnızca bu sekiz öğrenciyi betimler. Daha geniş bir öğrenci grubu hakkında "
            "konuşmak çıkarımdır ve örneklemin nasıl seçildiğine bağlıdır (§1.8)."
        ),
    ),
    LabStep(
        number=5,
        title="Bütünleştirici uygulama: kavramları eşleştirmek",
        note=NoteRef("1.11", objects=("Tablo 1.3",)),
        explanation=(
            "Bir üniversite, ikinci sınıf öğrencilerinin kampüse ulaşım biçimini ve süresini 200 öğrenciye "
            "sorar: ana ulaşım aracı, tek yön ulaşım süresi (dakika) ve ulaşımın değerlendirmesi "
            "(zor, orta, kolay). Tablo 1.3'teki eşleştirme:\n\n"
            "| Kavram | Ulaşım araştırmasındaki karşılığı |\n"
            "|---|---|\n"
            "| Gözlem birimi | Ankete katılan her öğrenci |\n"
            "| Değişken | Ulaşım aracı, ulaşım süresi, ulaşım değerlendirmesi |\n"
            "| Kategorik değişken | Ulaşım aracı |\n"
            "| Ordinal değişken | Zor / orta / kolay değerlendirmesi |\n"
            "| Nicel değişken | Dakika cinsinden ulaşım süresi |\n"
            "| Örneklem | Ankete katılan 200 öğrenci |\n"
            "| Olası anakütle | Araştırma sorusuna bağlı olarak üniversitedeki ikinci sınıf öğrencileri |\n"
            "| Betimsel soru | 200 öğrencinin ortalama ulaşım süresi kaç dakikadır? |\n"
            "| Çıkarımsal soru | Bütün ikinci sınıf öğrencilerinin ortalama ulaşım süresi yaklaşık kaç dakikadır? |"
        ),
        takeaway=(
            "Aynı veriyle farklı sorular sorulur: en yaygın ulaşım aracı kategorik veriyi, ortalama süre "
            "nicel veriyi özetler; iki aracın süresini karşılaştırmak iki değişkeni birlikte incelemeye başlar."
        ),
    ),
)

KONU01_LAB = LabSpec(
    topic_key="konu01",
    title="Bir veri setini okumak ve betimlemek",
    note_section="1",
    steps=STEPS,
    labels=(
        ("ogrenci", "Öğrenci"),
        ("bolum", "Bölüm"),
        ("saat", "Haftalık çalışma (saat)"),
        ("puan", "Sınav puanı"),
        ("durum", "Ders durumu"),
        ("durum_kod", "Ders durumu kodu"),
        ("ay", "Ay"),
        ("fiyat_endeksi", "Fiyat endeksi"),
    ),
)
