"""Konu 2 uygulaması: kategorik verileri tablo ve grafiklerle özetlemek.

Ders notlarının çözümlü örnekleri §2.1–§2.12 sırasıyla izlenir: ulaşım biçimi verisi (Tablo 2.1–2.3,
Şekil 2.3–2.6), bölüm × materyal çapraz tablosu (Tablo 2.4–2.5, Şekil 2.8–2.9), kesilmiş eksen
(Şekil 2.10), Simpson paradoksu (Tablo 2.6) ve bütünleştirici anket (Tablo 2.7, Şekil 2.11).
Buradaki her ``Check`` notlarda basılı bir sayıdır; değer notlardan kopyalanmıştır, hesaplanmamıştır.
"""

from __future__ import annotations

from core.labs import expr as E
from core.labs.spec import (
    TOTAL,
    BarChart,
    Check,
    CompareBarChart,
    CrossTab,
    FrequencyTable,
    FromCounts,
    GroupedBarChart,
    InlineData,
    LabSpec,
    LabStep,
    NoteRef,
    PieChart,
    Scalar,
    ScalarTarget,
    Shape,
    Statistic,
    TableTarget,
)

RAW_TRANSPORT = (
    "Otobüs", "Raylı sistem", "Yürüme", "Otobüs", "Özel araç",
    "Bisiklet", "Otobüs", "Raylı sistem", "Otobüs", "Yürüme",
    "Otobüs", "Otobüs", "Raylı sistem", "Özel araç", "Otobüs",
    "Yürüme", "Raylı sistem", "Otobüs", "Bisiklet", "Otobüs",
    "Özel araç", "Otobüs", "Raylı sistem", "Yürüme", "Otobüs",
    "Raylı sistem", "Otobüs", "Bisiklet", "Özel araç", "Otobüs",
    "Yürüme", "Raylı sistem", "Otobüs", "Raylı sistem", "Özel araç",
    "Otobüs", "Yürüme", "Otobüs", "Raylı sistem", "Raylı sistem",
)
"""Tablo 2.1, satır satır okunmuş 40 kayıt."""

TRANSPORT_ORDER = ("Yürüme", "Otobüs", "Özel araç", "Bisiklet", "Raylı sistem")
"""Tablo 2.2–2.3 ve Şekil 2.3'teki kategori sırası."""
PIE_ORDER = ("Otobüs", "Raylı sistem", "Yürüme", "Özel araç", "Bisiklet")
"""Şekil 2.5'teki dilim sırası (0°'den başlayarak saat yönünün tersine)."""

DEPARTMENTS = ("İktisat", "İşletme")
MATERIALS = ("Basılı", "Dijital", "Her ikisi")
MATERIAL_COUNTS = (
    ("İktisat", "Basılı", 12), ("İktisat", "Dijital", 18), ("İktisat", "Her ikisi", 10),
    ("İşletme", "Basılı", 10), ("İşletme", "Dijital", 8), ("İşletme", "Her ikisi", 2),
)
"""Tablo 2.4'ün hücreleri."""

OUTCOMES = ("Dönüştü", "Dönüşmedi")
AD_COUNTS = (
    ("Kolay", "A", "Dönüştü", 90), ("Kolay", "A", "Dönüşmedi", 10),
    ("Kolay", "B", "Dönüştü", 19), ("Kolay", "B", "Dönüşmedi", 1),
    ("Zor", "A", "Dönüştü", 1), ("Zor", "A", "Dönüşmedi", 9),
    ("Zor", "B", "Dönüştü", 8), ("Zor", "B", "Dönüşmedi", 32),
)
"""Tablo 2.6: dönüşen ve toplam sayılardan dönüşmeyenler (toplam − dönüşen)."""

SOURCES = ("Ders notu", "Ders kitabı", "Video", "Soru çözümü", "Diğer")
SOURCE_COUNTS = (("Ders notu", 42), ("Ders kitabı", 18), ("Video", 30), ("Soru çözümü", 24), ("Diğer", 6))
"""Tablo 2.7."""


def _cell(table: str, row: str, column: str, expected: float, label: str, decimals: int = 0) -> Check:
    return Check(label, TableTarget(table, row, column), expected, decimals)


STEPS = (
    LabStep(
        number=1,
        title="Ham kategorik veri",
        note=NoteRef("2.1", objects=("Tablo 2.1",)),
        explanation=(
            "Kırk öğrenciye kampüse en sık hangi ulaşım biçimiyle geldikleri sorulmuştur. Tablo 2.1 satır "
            "satır okunarak her öğrenci bir gözlem olur; tek değişken ulaşım biçimidir. Kırk etiketi tek tek "
            "saymak yavaş ve hataya açıktır: betimsel istatistiğin ilk görevi bu ham veriyi okunabilir bir "
            "özete dönüştürmektir."
        ),
        operations=(
            InlineData(
                "ulasim",
                ("arac",),
                tuple((label,) for label in RAW_TRANSPORT),
                "Tablo 2.1: 40 öğrencinin kampüse ulaşım biçimi, satır satır",
                layout=5,
            ),
            Shape("ulasim", "n", "k"),
        ),
        checks=(Check("Gözlem sayısı n", ScalarTarget("n"), 40, 0),),
        takeaway=(
            "Özette bilgi kaybolmaz, yoğunlaşır: hangi öğrencinin hangi aracı seçtiğini artık görmeyiz; "
            "buna karşılık hangi kategorinin ne kadar yaygın olduğunu hemen görürüz."
        ),
    ),
    LabStep(
        number=2,
        title="Frekans dağılımı",
        note=NoteRef("2.2", objects=("Tablo 2.2", "(2.1)")),
        explanation=(
            "Her kategorideki gözlem sayısı o kategorinin frekansıdır ($f_j$). Kategoriler notlardaki "
            "sırayla dizilir ve sona toplam satırı eklenir. Frekansların toplamı gözlem sayısına eşit "
            "olmalıdır: $\\sum_{j=1}^{k} f_j = n$. Bu eşitlik yeni bir hesap değil, tablonun kontrol kuralıdır."
        ),
        operations=(
            FrequencyTable("ulasim", "arac", "frekans_tablosu", TRANSPORT_ORDER, relative=False, totals=True),
        ),
        checks=(
            _cell("frekans_tablosu", "Yürüme", "frekans", 6, "Yürüme frekansı"),
            _cell("frekans_tablosu", "Otobüs", "frekans", 16, "Otobüs frekansı"),
            _cell("frekans_tablosu", "Özel araç", "frekans", 5, "Özel araç frekansı"),
            _cell("frekans_tablosu", "Bisiklet", "frekans", 3, "Bisiklet frekansı"),
            _cell("frekans_tablosu", "Raylı sistem", "frekans", 10, "Raylı sistem frekansı"),
            _cell("frekans_tablosu", TOTAL, "frekans", 40, "Frekansların toplamı = n"),
        ),
        takeaway=(
            "Örneklemde en sık gözlenen ulaşım biçimi otobüstür (40 öğrencinin 16'sı), en az gözlenen "
            "bisiklettir (3 öğrenci). Bu ifadeler yalnızca gözlenen 40 öğrenciyi betimler."
        ),
    ),
    LabStep(
        number=3,
        title="Göreli frekans ve yüzde frekans",
        note=NoteRef("2.3", objects=("Tablo 2.3", "(2.2)", "(2.3)")),
        explanation=(
            "Göreli frekans $r_j = f_j / n$, yüzde frekans $p_j = 100 \\times r_j$'dir. Örneğin otobüs için "
            "$r = 16/40 = 0{,}40$ ve $p = 100 \\times 0{,}40 = \\%40$. Üç sütun aynı dağılımı üç ölçekte "
            "anlatır: $\\sum f_j = n$, $\\sum r_j = 1$, $\\sum p_j = 100$."
        ),
        operations=(FrequencyTable("ulasim", "arac", "tam_tablo", TRANSPORT_ORDER, relative=True, totals=True),),
        checks=(
            _cell("tam_tablo", "Yürüme", "goreli", 0.150, "Yürüme göreli frekansı", 3),
            _cell("tam_tablo", "Otobüs", "goreli", 0.400, "Otobüs göreli frekansı 16/40", 3),
            _cell("tam_tablo", "Özel araç", "goreli", 0.125, "Özel araç göreli frekansı", 3),
            _cell("tam_tablo", "Bisiklet", "goreli", 0.075, "Bisiklet göreli frekansı", 3),
            _cell("tam_tablo", "Raylı sistem", "goreli", 0.250, "Raylı sistem göreli frekansı", 3),
            _cell("tam_tablo", TOTAL, "goreli", 1.000, "Göreli frekansların toplamı", 3),
            _cell("tam_tablo", "Yürüme", "yuzde", 15.0, "Yürüme yüzde frekansı", 1),
            _cell("tam_tablo", "Otobüs", "yuzde", 40.0, "Otobüs yüzde frekansı", 1),
            _cell("tam_tablo", "Özel araç", "yuzde", 12.5, "Özel araç yüzde frekansı", 1),
            _cell("tam_tablo", "Bisiklet", "yuzde", 7.5, "Bisiklet yüzde frekansı", 1),
            _cell("tam_tablo", "Raylı sistem", "yuzde", 25.0, "Raylı sistem yüzde frekansı", 1),
            _cell("tam_tablo", TOTAL, "yuzde", 100.0, "Yüzde frekansların toplamı", 1),
        ),
        takeaway=(
            "Frekans \"kaç kişi?\", göreli ve yüzde frekans \"toplamın ne kadarı?\" sorusunu cevaplar. "
            "Farklı büyüklükteki veri setleri yüzdelerle karşılaştırılır."
        ),
    ),
    LabStep(
        number=4,
        title="Sütun grafiği",
        note=NoteRef("2.4", objects=("Şekil 2.3",)),
        explanation=(
            "Kategoriler yatay eksende, frekanslar dikey eksende gösterilir; her kategori ayrı bir sütundur. "
            "Sütunun uzunluğu büyüklüğü temsil ettiği için dikey eksen sıfırdan başlar."
        ),
        operations=(
            BarChart(
                "frekans_tablosu",
                "frekans",
                "Ulaşım biçimi",
                "Öğrenci sayısı",
                "Kampüse ulaşım biçimi için sütun grafiği",
            ),
        ),
        takeaway=(
            "Sütunlar arasındaki boşluk, kategorilerin birbirinden ayrı olduğunu gösterir. Bu özellik "
            "sütun grafiğini Konu 3'teki histogramdan ayırır."
        ),
    ),
    LabStep(
        number=5,
        title="Kategori sırası: sıralanmış sütun grafiği",
        note=NoteRef("2.5", objects=("Şekil 2.4",)),
        explanation=(
            "Ulaşım biçimi nominal bir değişkendir; kategorilerin doğal bir sırası yoktur. Sütunları "
            "yüksekten düşüğe sıralamak karşılaştırmayı kolaylaştırır."
        ),
        operations=(
            BarChart(
                "frekans_tablosu",
                "frekans",
                "Ulaşım biçimi",
                "Öğrenci sayısı",
                "Frekansa göre sıralanmış sütun grafiği",
                sort="azalan",
            ),
        ),
        takeaway=(
            "Nominal veride frekansa göre sıralama yapılabilir. Ordinal veride ise öncelik kategorilerin "
            "doğal sırasını korumaktır (ör. Çok düşük < Düşük < Orta < Yüksek < Çok yüksek)."
        ),
    ),
    LabStep(
        number=6,
        title="Dilim grafiği ve dilim açısı",
        note=NoteRef("2.6", objects=("(2.4)", "Şekil 2.5", "Şekil 2.6")),
        explanation=(
            "Daire bütün veri setini, her dilim bir kategorinin payını temsil eder. Bir daire $360^\\circ$ "
            "olduğundan dilim açısı $\\theta_j = 360^\\circ \\times r_j$'dir; otobüs için "
            "$\\theta = 360^\\circ \\times 0{,}40 = 144^\\circ$. Dilimler notlardaki gibi $0^\\circ$'den başlar "
            "ve saat yönünün tersine dizilir. Aynı yüzdeler karşılaştırma için bir de sütun grafiğiyle çizilir."
        ),
        operations=(
            PieChart("tam_tablo", "goreli", "dilim_acilari", "Kampüse ulaşım biçimi için dilim grafiği", PIE_ORDER),
            BarChart(
                "tam_tablo",
                "yuzde",
                "Ulaşım biçimi",
                "Yüzde",
                "Aynı yüzdelerin sütun grafiği",
                sort="azalan",
                percent=True,
                decimals=1,
            ),
        ),
        checks=(_cell("dilim_acilari", "Otobüs", "aci", 144, "Otobüs dilim açısı (derece)"),),
        takeaway=(
            "%15 ile %12,5 arasındaki fark, sütunlar ortak bir tabandan başladığı için sütun grafiğinde "
            "daha kolay görülür. Grafik seçimi veriyi değiştirmez; hangi özelliğin kolay görüleceğini değiştirir."
        ),
    ),
    LabStep(
        number=7,
        title="İki kategorik değişken: çapraz tablo",
        note=NoteRef("2.7", objects=("Tablo 2.4", "Şekil 2.7")),
        explanation=(
            "Altmış öğrencinin bölümü ve tercih ettiği ders materyali birlikte özetlenir. Sayım tablosunun "
            "her satırı, o bölüm–materyal birleşimindeki öğrenci sayısı kadar tekrarlanarak gözlem düzeyinde "
            "veri kurulur; çapraz tablo bu veriden sayılır. Son satır ve son sütun marjinal toplamlardır."
        ),
        operations=(
            FromCounts(
                "tercihler",
                ("bolum", "materyal"),
                MATERIAL_COUNTS,
                "Tablo 2.4'ün hücre sayıları: her satır bir bölüm–materyal birleşimi",
            ),
            CrossTab("tercihler", "bolum", "materyal", "capraz", DEPARTMENTS, MATERIALS, margins=True),
        ),
        checks=(
            _cell("capraz", "İktisat", "Dijital", 18, "İktisat ∩ Dijital"),
            _cell("capraz", "İktisat", TOTAL, 40, "İktisat satır toplamı"),
            _cell("capraz", "İşletme", TOTAL, 20, "İşletme satır toplamı"),
            _cell("capraz", TOTAL, "Basılı", 22, "Basılı sütun toplamı"),
            _cell("capraz", TOTAL, "Dijital", 26, "Dijital sütun toplamı"),
            _cell("capraz", TOTAL, "Her ikisi", 12, "Her ikisi sütun toplamı"),
            _cell("capraz", TOTAL, TOTAL, 60, "Genel toplam"),
        ),
        takeaway=(
            "Bir hücre iki koşulu birlikte söyler: \"18 öğrenci dijital materyal kullanıyor\" eksiktir; "
            "doğrusu \"18 İktisat öğrencisi dijital materyali tercih ediyor\"."
        ),
    ),
    LabStep(
        number=8,
        title="Satır ve sütun yüzdeleri: doğru payda",
        note=NoteRef("2.8", objects=("Tablo 2.5",)),
        explanation=(
            "\"Her bölümün kendi içinde tercihleri nasıl dağılıyor?\" sorusunun paydası **satır toplamıdır**: "
            "İktisat'ta dijital tercih $18/40 \\times 100 = \\%45$. \"Dijital tercih edenlerin bölüm dağılımı "
            "nedir?\" sorusunun paydası ise **sütun toplamıdır**: $18/26 \\times 100 \\approx \\%69{,}2$."
        ),
        operations=(
            CrossTab(
                "tercihler", "bolum", "materyal", "satir_yuzde", DEPARTMENTS, MATERIALS,
                percent="satir", margins=True,
            ),
            CrossTab(
                "tercihler", "bolum", "materyal", "sutun_yuzde", DEPARTMENTS, MATERIALS,
                percent="sutun", margins=True,
            ),
        ),
        checks=(
            _cell("satir_yuzde", "İktisat", "Basılı", 30, "İktisat: basılı (satır %)"),
            _cell("satir_yuzde", "İktisat", "Dijital", 45, "İktisat: dijital (satır %)"),
            _cell("satir_yuzde", "İktisat", "Her ikisi", 25, "İktisat: her ikisi (satır %)"),
            _cell("satir_yuzde", "İktisat", TOTAL, 100, "İktisat satır toplamı (%)"),
            _cell("satir_yuzde", "İşletme", "Basılı", 50, "İşletme: basılı (satır %)"),
            _cell("satir_yuzde", "İşletme", "Dijital", 40, "İşletme: dijital (satır %)"),
            _cell("satir_yuzde", "İşletme", "Her ikisi", 10, "İşletme: her ikisi (satır %)"),
            _cell("satir_yuzde", "İşletme", TOTAL, 100, "İşletme satır toplamı (%)"),
            _cell("sutun_yuzde", "İktisat", "Dijital", 69.2, "Dijital tercih edenlerde İktisat (sütun %)", 1),
            _cell("sutun_yuzde", "İşletme", "Dijital", 30.8, "Dijital tercih edenlerde İşletme (sütun %)", 1),
        ),
        takeaway=(
            "Aynı 18 hücresi farklı sorularda farklı paydaya bölünür. Yüzde hesabında en önemli adım "
            "çoğu zaman bölme değil, doğru paydayı seçmektir."
        ),
    ),
    LabStep(
        number=9,
        title="Yan yana ve yüzde 100 yığılmış sütun grafikleri",
        note=NoteRef("2.9", objects=("Şekil 2.8", "Şekil 2.9")),
        explanation=(
            "Satır yüzdeleri iki biçimde çizilir. Yan yana grafikte her materyal kategorisinde iki bölüm "
            "doğrudan karşılaştırılır. Yüzde 100 yığılmış grafikte her bölüm tek bir sütundur ve sütun "
            "%100'e tamamlanır; böylece bölüm büyüklükleri farklı olsa da iç bileşim karşılaştırılır."
        ),
        operations=(
            GroupedBarChart(
                "satir_yuzde",
                "Materyal tercihi",
                "Bölüm içindeki yüzde",
                "Bölümlere göre materyal tercihi: yan yana sütun grafiği",
                series="satir",
            ),
            GroupedBarChart(
                "satir_yuzde",
                "Bölüm",
                "Bölüm içindeki yüzde",
                "Bölüm içindeki dağılım: yüzde 100 yığılmış sütun grafiği",
                series="sutun",
                stacked=True,
            ),
        ),
        takeaway=(
            "Yan yana grafik tek bir kategoride grupları karşılaştırmayı kolaylaştırır; yığılmış grafik her "
            "grubun iç bileşimini özetler. Yığılmış grafikte orta parçaların ortak tabanı olmadığı için küçük "
            "farkları karşılaştırmak zorlaşır."
        ),
    ),
    LabStep(
        number=10,
        title="Kesilmiş eksen: yüzde ve yüzde puan",
        note=NoteRef("2.10", objects=("Şekil 2.10",)),
        explanation=(
            "İki mağazanın müşteri memnuniyeti %72 ve %78'dir. Aynı iki sayı önce %70–%80 aralığına kesilmiş, "
            "sonra sıfırdan başlayan bir eksenle çizilir. Fark 6 **yüzde puandır**; göreli artış ise "
            "$(78 - 72)/72 \\times 100 \\approx \\%8{,}3$'tür."
        ),
        operations=(
            InlineData(
                "magazalar",
                ("magaza", "memnuniyet"),
                (("A", 72), ("B", 78)),
                "Şekil 2.10: iki mağazanın müşteri memnuniyeti (%)",
            ),
            BarChart("magazalar", "memnuniyet", "Mağaza", "Memnuniyet (%)", "Kesilmiş eksen", x="magaza",
                     y_range=(70, 80)),
            BarChart("magazalar", "memnuniyet", "Mağaza", "Memnuniyet (%)", "Sıfır tabanlı eksen", x="magaza",
                     y_range=(0, 100)),
            Statistic("magazalar", "memnuniyet", "value", "memnuniyet_a", "A mağazasının memnuniyeti (%)",
                      where=("magaza", "A"), decimals=0),
            Statistic("magazalar", "memnuniyet", "value", "memnuniyet_b", "B mağazasının memnuniyeti (%)",
                      where=("magaza", "B"), decimals=0),
            Scalar("fark_puan", E.sub(E.ref("memnuniyet_b"), E.ref("memnuniyet_a")), "Fark (yüzde puan)",
                   decimals=0),
            Scalar(
                "goreli_artis",
                E.mul(100, E.div(E.sub(E.ref("memnuniyet_b"), E.ref("memnuniyet_a")), E.ref("memnuniyet_a"))),
                "Göreli artış",
                decimals=1,
                percent=True,
            ),
        ),
        checks=(
            Check("B − A farkı (yüzde puan)", ScalarTarget("fark_puan"), 6, 0),
            Check("Göreli artış (78 − 72)/72", ScalarTarget("goreli_artis"), 8.3, 1),
        ),
        takeaway=(
            "Kesilmiş eksende 6 yüzde puanlık fark çok büyük görünür. Sütun grafiğinde değer ekseni genel "
            "olarak sıfırdan başlamalıdır; \"yüzde\" ile \"yüzde puan\" aynı kavram değildir."
        ),
    ),
    LabStep(
        number=11,
        title="Toplulaştırma yanılsaması: Simpson paradoksu",
        note=NoteRef("2.11", objects=("Tablo 2.6",)),
        explanation=(
            "İki reklam tasarımının dönüşüm oranları kolay ve zor müşteri gruplarında ayrı ayrı, sonra "
            "birlikte hesaplanır. Dönüşmeyen sayısı toplam eksi dönüşendir. Her iki grupta B daha yüksektir "
            "(%95 > %90, %20 > %10); gruplar birleştirilince A daha yüksek görünür (%82,7 > %45)."
        ),
        operations=(
            FromCounts(
                "reklam",
                ("grup", "tasarim", "sonuc"),
                AD_COUNTS,
                "Tablo 2.6: müşteri grubu, tasarım ve sonuç birleşimlerinin sayıları",
            ),
            CrossTab("reklam", "tasarim", "sonuc", "kolay_oran", ("A", "B"), OUTCOMES, percent="satir",
                     where=("grup", "Kolay")),
            CrossTab("reklam", "tasarim", "sonuc", "zor_oran", ("A", "B"), OUTCOMES, percent="satir",
                     where=("grup", "Zor")),
            CrossTab("reklam", "tasarim", "sonuc", "genel_sayi", ("A", "B"), OUTCOMES, margins=True),
            CrossTab("reklam", "tasarim", "sonuc", "genel_oran", ("A", "B"), OUTCOMES, percent="satir"),
            CompareBarChart(
                (("Kolay grup", "kolay_oran"), ("Zor grup", "zor_oran"), ("Tüm gruplar", "genel_oran")),
                "Dönüştü",
                "Müşteri grubu",
                "Dönüşüm oranı (%)",
                "Tasarıma göre dönüşüm oranı: alt gruplar ve toplam",
            ),
        ),
        checks=(
            _cell("kolay_oran", "A", "Dönüştü", 90, "Kolay grupta A (%)"),
            _cell("kolay_oran", "B", "Dönüştü", 95, "Kolay grupta B (%)"),
            _cell("zor_oran", "A", "Dönüştü", 10, "Zor grupta A (%)"),
            _cell("zor_oran", "B", "Dönüştü", 20, "Zor grupta B (%)"),
            _cell("genel_sayi", "A", "Dönüştü", 91, "Tüm gruplarda A: dönüşen"),
            _cell("genel_sayi", "A", TOTAL, 110, "Tüm gruplarda A: toplam"),
            _cell("genel_sayi", "B", "Dönüştü", 27, "Tüm gruplarda B: dönüşen"),
            _cell("genel_sayi", "B", TOTAL, 60, "Tüm gruplarda B: toplam"),
            _cell("genel_oran", "A", "Dönüştü", 82.7, "Tüm gruplarda A (%)", 1),
            _cell("genel_oran", "B", "Dönüştü", 45.0, "Tüm gruplarda B (%)", 1),
        ),
        takeaway=(
            "Tasarımlar gruplara eşit oranlarda uygulanmamıştır: A'nın gözlemlerinin çoğu dönüşümün zaten "
            "yüksek olduğu kolay gruptadır, B'ninkilerin çoğu zor gruptadır. Toplam oran alt grupların "
            "bileşiminden etkilenir."
        ),
    ),
    LabStep(
        number=12,
        title="Bütünleştirici uygulama: bir anketi raporlamak",
        note=NoteRef("2.12", objects=("Tablo 2.7", "Şekil 2.11")),
        explanation=(
            "Yüz yirmi öğrencinin ders çalışırken en çok kullandığı kaynak özetlenir. Frekanslardan yüzdeler "
            "hesaplanır; toplamlar kontrol edilir; uzun kategori adları için yatay sütun grafiği çizilir. "
            "Grafikte frekans yerine yüzde kullanılır: soru \"120 kişiden kaçı?\" değil, \"öğrencilerin ne "
            "kadarı?\"dır."
        ),
        operations=(
            FromCounts("anket", ("kaynak",), SOURCE_COUNTS, "Tablo 2.7: ana çalışma kaynağına göre öğrenci sayıları"),
            FrequencyTable("anket", "kaynak", "kaynak_tablosu", SOURCES, relative=True, totals=True),
            BarChart(
                "kaynak_tablosu",
                "yuzde",
                "Ana çalışma kaynağı",
                "Öğrencilerin yüzdesi",
                "Ana çalışma kaynağı için yatay sütun grafiği",
                sort="azalan",
                horizontal=True,
                percent=True,
            ),
        ),
        checks=(
            _cell("kaynak_tablosu", TOTAL, "frekans", 120, "Frekansların toplamı"),
            _cell("kaynak_tablosu", "Ders notu", "yuzde", 35, "Ders notu (%)"),
            _cell("kaynak_tablosu", "Ders kitabı", "yuzde", 15, "Ders kitabı (%)"),
            _cell("kaynak_tablosu", "Video", "yuzde", 25, "Video (%)"),
            _cell("kaynak_tablosu", "Soru çözümü", "yuzde", 20, "Soru çözümü (%)"),
            _cell("kaynak_tablosu", "Diğer", "yuzde", 5, "Diğer (%)"),
            _cell("kaynak_tablosu", TOTAL, "yuzde", 100, "Yüzdelerin toplamı"),
        ),
        takeaway=(
            "Rapor sırası: değişkeni tanımla (nominal), özeti kontrol et (120 ve %100), örüntüyü belirt "
            "(en yaygın ders notu, %35), uygun grafiği seç ve sınırı yaz: sonuçlar yanıtlayan 120 öğrenciyi betimler."
        ),
    ),
)

KONU02_LAB = LabSpec(
    topic_key="konu02",
    title="Kategorik verileri tablo ve grafiklerle özetlemek",
    note_section="2",
    steps=STEPS,
    labels=(
        ("arac", "Ulaşım biçimi"),
        ("frekans", "Frekans"),
        ("goreli", "Göreli frekans"),
        ("yuzde", "Yüzde frekans"),
        ("aci", "Dilim açısı (°)"),
        ("bolum", "Bölüm"),
        ("materyal", "Materyal"),
        ("magaza", "Mağaza"),
        ("memnuniyet", "Memnuniyet (%)"),
        ("grup", "Müşteri grubu"),
        ("tasarim", "Tasarım"),
        ("sonuc", "Sonuç"),
        ("kaynak", "Ana çalışma kaynağı"),
    ),
)
