"""Konu 6 uygulaması: örnek uzay, sayma kuralları, olasılık atama, olaylar ve toplama kuralı.

Ders notlarının çözümlü örnekleri: §6.2 (zar ve iki zar), §6.3 (sipariş ağacı ve çarpım kuralı), §6.4 (faktöriyel,
kombinasyon, permütasyon), §6.5 (klasik ve göreli frekans yöntemi), §6.6 (olay), §6.7 (tümleyen), §6.8 (birleşim
ve kesişim), §6.9 (toplama kuralı) ve §6.10 (Tablo 6.2: tedarik performansı). Buradaki her ``Check`` notlarda
basılı bir sayıdır; değer notlardan kopyalanmıştır, hesaplanmamıştır. §6.1 ve §6.11 hesap içermez; Şekil 6.6'daki
birikimli gecikme oranı Sezgi sekmesindeki Deney 1'in varsayılan ayarlarıyla birebir üretilir.

Olaylar örnek uzayın alt kümeleridir: her örnek nokta bir satırdır, olayın gösterge sütunu olaydaki satırlarda 1,
diğerlerinde 0'dır. Bir olayın olasılığı, olaydaki örnek noktaların olasılıklarının toplamıdır.
"""

from __future__ import annotations

from core.labs import expr as E
from core.labs.spec import (
    BarChart,
    CellTarget,
    Check,
    CrossTab,
    Derive,
    Event,
    FrequencyTable,
    FromCounts,
    InlineData,
    LabSpec,
    LabStep,
    NoteRef,
    Outcomes,
    Scalar,
    ScalarTarget,
    Selections,
    ShowFrame,
    Statistic,
    TableTarget,
)

DIE = (1, 2, 3, 4, 5, 6)
SUMS = tuple(range(2, 13))
TEAM = ("A", "B", "C", "D", "E")
"""§6.4: beş kişilik ekip; A Ayşe, B Berk."""
DELIVERIES = (("Gecikti", 30), ("Zamanında", 170))
"""§6.5: geçmiş 200 teslimatın 30'u gecikmiş."""
SKILLS = (("Evet", "Evet", 15), ("Evet", "Hayır", 25), ("Hayır", "Evet", 20), ("Hayır", "Hayır", 40))
"""§6.9: 100 çalışan; 40'ı ileri Excel, 35'i Python, 15'i ikisini de kullanabiliyor (hücreler bu sayılardan)."""
SHIPMENTS = (
    ("E1", "Zamanında", "Hatasız", 0.70),
    ("E2", "Zamanında", "Hatalı", 0.08),
    ("E3", "Geç", "Hatasız", 0.17),
    ("E4", "Geç", "Hatalı", 0.05),
)
"""Tablo 6.2: sevkiyat sonuçlarının ortak örnek noktaları ve olasılıkları."""


def _scalar(name: str, expected: float, label: str, decimals: int) -> Check:
    return Check(label, ScalarTarget(name), expected, decimals)


STEPS = (
    LabStep(
        number=1,
        title="Örnek uzay: bir zar ve iki zar",
        note=NoteRef("6.2", objects=("Şekil 6.2",)),
        explanation=(
            "Bir zar atıldığında örnek uzay $S = \\{1, 2, 3, 4, 5, 6\\}$'dır. İki zar atıldığında temel örnek "
            "noktalar $(1, 1), (1, 2), \\ldots, (6, 6)$ biçimindeki zar çiftleridir. Toplam 2 ile 12 arasında bir "
            "değer alır; ama her toplam aynı sayıda temel sonuçla oluşmaz."
        ),
        operations=(
            Outcomes("zar", (("sonuc", DIE),), "Bir zar atılır: örnek uzay S"),
            Statistic("zar", "sonuc", "count", "m", "Örnek nokta sayısı", decimals=0),
            Outcomes("iki_zar", (("birinci", DIE), ("ikinci", DIE)), "İki zar atılır: temel örnek noktalar"),
            Derive("iki_zar", "toplam", E.add(E.var("birinci"), E.var("ikinci")), "İki zarın toplamı"),
            Statistic("iki_zar", "toplam", "nunique", "farkli_toplam", "Farklı toplam sayısı", decimals=0),
            FrequencyTable("iki_zar", "toplam", "toplamlar", SUMS, relative=False),
            BarChart("toplamlar", "frekans", "İki zarın toplamı", "Temel örnek nokta sayısı",
                     "Her toplam kaç temel sonuçla oluşur?"),
        ),
        checks=(
            _scalar("m", 6, "Bir zarda örnek nokta sayısı", 0),
            _scalar("farkli_toplam", 11, "Farklı toplam sayısı (2, …, 12)", 0),
            Check("Toplam 2: yalnız (1, 1)", TableTarget("toplamlar", 2, "frekans"), 1, 0),
            Check("Toplam 7: altı zar çifti", TableTarget("toplamlar", 7, "frekans"), 6, 0),
        ),
        takeaway=(
            "11 toplamın her biri mümkündür ama eşit olasılıklı değildir: toplam 2 yalnız bir, toplam 7 altı temel "
            "sonuçla oluşur. Olasılıkları kurmak için örnek noktalar zar çiftleri olarak yazılır (§6.2)."
        ),
    ),
    LabStep(
        number=2,
        title="Çok aşamalı deney ve çarpım kuralı",
        note=NoteRef("6.3", objects=("Şekil 6.3",)),
        explanation=(
            "Siparişte önce teslimat türü (Standart, Hızlı), sonra ödeme türü (Kart, Havale, Kapıda) seçilir. Ağaç "
            "diyagramındaki her tam dal bir örnek noktadır. $k$ aşamada $n_1, n_2, \\ldots, n_k$ seçenek varsa "
            "sonuç sayısı $n_1 n_2 \\cdots n_k$'dır."
        ),
        operations=(
            Outcomes("siparis", (("teslimat", ("Standart", "Hızlı")), ("odeme", ("Kart", "Havale", "Kapıda"))),
                     "Sipariş: teslimat türü, sonra ödeme türü"),
            Statistic("siparis", "teslimat", "count", "siparis_sayisi", "Listelenen sonuç sayısı", decimals=0),
            Scalar("iki_asama", E.mul(2, 3), "Çarpım kuralı: 2 × 3", decimals=0),
            Scalar("uc_asama", E.mul(E.mul(4, 3), 2), "4 renk × 3 kapasite × 2 garanti", decimals=0),
        ),
        checks=(
            _scalar("siparis_sayisi", 6, "Listelenen sipariş sonucu", 0),
            _scalar("iki_asama", 6, "2 × 3", 0),
            _scalar("uc_asama", 24, "4 × 3 × 2", 0),
        ),
        takeaway=(
            "Sonuçlar ağaçtaki sırayla listelenir: ilk aşama en yavaş, son aşama en hızlı değişir. Çarpım kuralı "
            "listeyi yazmadan sonuç sayısını verir; aşama sayısı arttıkça listelemek pratik olmaktan çıkar (§6.3)."
        ),
    ),
    LabStep(
        number=3,
        title="Faktöriyel, kombinasyon ve permütasyon",
        note=NoteRef("6.4", objects=("Şekil 6.4",)),
        explanation=(
            "Beş kişilik ekibi A (Ayşe), B (Berk), C, D ve E ile gösterelim. Eğitime iki kişi gönderilecekse sıra "
            "önemsizdir: $\\binom{5}{2} = 5!/(2!\\,3!)$. Bir başkan ve bir raportör seçilecekse görevler farklıdır: "
            "$P(5, 2) = 5!/3!$."
        ),
        operations=(
            Scalar("faktoriyel", E.factorial(5), "5!", decimals=0),
            Scalar("kombinasyon", E.comb(5, 2), "Kombinasyon C(5, 2)", decimals=0),
            Scalar("permutasyon", E.perm(5, 2), "Permütasyon P(5, 2)", decimals=0),
            Selections("egitim", TEAM, 2, False, ("birinci", "ikinci"), "Eğitime gidecek iki kişi"),
            Statistic("egitim", "birinci", "count", "grup_sayisi", "Listelenen iki kişilik grup", decimals=0),
            Selections("gorev", TEAM, 2, True, ("baskan", "raportor"), "Başkan ve raportör"),
            Statistic("gorev", "baskan", "count", "gorev_sayisi", "Listelenen başkan–raportör çifti", decimals=0),
        ),
        checks=(
            _scalar("faktoriyel", 120, "5! = 5 · 4 · 3 · 2 · 1", 0),
            _scalar("kombinasyon", 10, "C(5, 2) = 5!/(2! 3!)", 0),
            _scalar("permutasyon", 20, "P(5, 2) = 5!/3!", 0),
            _scalar("grup_sayisi", 10, "Listelenen grup sayısı", 0),
            _scalar("gorev_sayisi", 20, "Listelenen görev çifti sayısı", 0),
        ),
        takeaway=(
            "Permütasyon listesinde her grup iki kez görünür: (A, B) ve (B, A). Bu yüzden P(5, 2) = 2! × C(5, 2). "
            "Formülden önce \"sıra veya görev önemli mi?\" sorusu cevaplanır (§6.4)."
        ),
    ),
    LabStep(
        number=4,
        title="Olasılık atama: klasik ve göreli frekans",
        note=NoteRef("6.5"),
        explanation=(
            "Klasik yöntem: $m$ eşit olasılıklı sonuç varsa her örnek noktaya $1/m$ atanır; adil zarda "
            "$P(1) = \\cdots = P(6) = 1/6$. Göreli frekans yöntemi: geçmiş 200 teslimatın 30'u gecikmişse "
            "$P(\\text{gecikme}) \\approx 30/200$. İki durumda da $0 \\le P(E_i) \\le 1$ ve $\\sum P(E_i) = 1$'dir."
        ),
        operations=(
            Derive("zar", "olasilik", E.div(1, E.ref("m")), "Klasik yöntem: her örnek noktaya 1/m"),
            ShowFrame("zar", ("sonuc", "olasilik"), "Adil zarın örnek noktaları ve olasılıkları"),
            Statistic("zar", "olasilik", "sum", "olasilik_toplami", "Olasılıkların toplamı", decimals=0),
            FromCounts("teslimat", ("durum",), DELIVERIES, "Geçmiş teslimatlar"),
            FrequencyTable("teslimat", "durum", "teslimat_tablo", ("Gecikti", "Zamanında"), totals=True),
        ),
        checks=(
            Check("Klasik yöntem: P(1) = 1/6", CellTarget("zar", "olasilik", 1), 1 / 6, 4),
            _scalar("olasilik_toplami", 1, "Olasılıkların toplamı", 0),
            Check("Teslimat sayısı", TableTarget("teslimat_tablo", "Toplam", "frekans"), 200, 0),
            Check("Göreli frekans: P(gecikme) ≈ 30/200", TableTarget("teslimat_tablo", "Gecikti", "goreli"), 0.15, 2),
        ),
        takeaway=(
            "Göreli frekans, aynı sürecin çok sayıda tekrarından gelen bir tahmindir. Az gözlemde oran belirgin "
            "biçimde oynar; gözlem arttıkça daha istikrarlı bir düzeye yaklaşır. Şekil 6.6'yı Sezgi sekmesindeki "
            "Deney 1 üretir (§6.5)."
        ),
    ),
    LabStep(
        number=5,
        title="Olay ve olayın olasılığı",
        note=NoteRef("6.6", objects=("Şekil 6.7",)),
        explanation=(
            "Olay örnek uzayın bir alt kümesidir: $A$ = \"çift sayı\" $= \\{2, 4, 6\\}$, $B$ = \"en az 5\" "
            "$= \\{5, 6\\}$. Olayın olasılığı olaydaki örnek noktaların olasılıklarının toplamıdır: "
            "$P(A) = \\sum_{E_i \\in A} P(E_i)$. Sonuçlar eşit olasılıklıysa bu, olaydaki nokta sayısının $m$'ye "
            "bölümüne eşittir."
        ),
        operations=(
            Event("zar", "A", "sonuc", (2, 4, 6), "A: çift sayı gelmesi"),
            Event("zar", "B", "sonuc", (5, 6), "B: en az 5 gelmesi"),
            ShowFrame("zar", ("sonuc", "olasilik", "A", "B"), "Örnek noktalar ve olaylar (1: olayda, 0: değil)"),
            Statistic("zar", "olasilik", "sum", "P_A", "P(A): A'daki noktaların olasılıkları toplamı", where=("A", 1),
                      decimals=2),
            Statistic("zar", "A", "sum", "A_sayisi", "A'daki örnek nokta sayısı", decimals=0),
            Scalar("P_A_klasik", E.div(E.ref("A_sayisi"), E.ref("m")), "P(A) = A'daki nokta sayısı / m", decimals=2),
        ),
        checks=(
            _scalar("A_sayisi", 3, "A'daki örnek nokta sayısı", 0),
            _scalar("P_A", 0.50, "P(A) = 1/6 + 1/6 + 1/6", 2),
            _scalar("P_A_klasik", 0.50, "P(A) = 3/6", 2),
        ),
        takeaway=(
            "İki yol aynı sonucu verir: 1/6 + 1/6 + 1/6 = 3/6 = 0,50. Sayma oranı yalnız örnek noktalar eşit "
            "olasılıklıysa kullanılır; genel kural olasılıkları toplamaktır (§6.6)."
        ),
    ),
    LabStep(
        number=6,
        title="Tümleyen olay",
        note=NoteRef("6.7", objects=("Şekil 6.8",)),
        explanation=(
            "$A^c$, örnek uzayda olup $A$'da olmayan noktalardır. Bir deneyde ya $A$ ya $A^c$ gerçekleşir: "
            "$P(A) + P(A^c) = 1$, dolayısıyla $P(A) = 1 - P(A^c)$. Bir sevkiyatın gecikme olasılığı 0,12 ise "
            "zamanında gelme olasılığı tümleyen kuralıyla bulunur."
        ),
        operations=(
            Derive("zar", "A_degil", E.sub(1, E.var("A")), "Aᶜ: çift olmayan sayı (A'da 0 olan noktalar)"),
            Statistic("zar", "olasilik", "sum", "P_A_degil", "P(Aᶜ)", where=("A_degil", 1), decimals=2),
            Scalar("toplam_A", E.add(E.ref("P_A"), E.ref("P_A_degil")), "P(A) + P(Aᶜ)", decimals=0),
            Scalar("P_gecikme", E.const(0.12), "P(gecikme)", decimals=2),
            Scalar("P_zamaninda", E.sub(1, E.ref("P_gecikme")), "P(zamanında) = 1 − P(gecikme)", decimals=2),
        ),
        checks=(
            _scalar("toplam_A", 1, "P(A) + P(Aᶜ)", 0),
            _scalar("P_zamaninda", 0.88, "P(zamanında) = 1 − 0,12", 2),
        ),
        takeaway=(
            "A ile Aᶜ aynı anda gerçekleşemez ve birlikte bütün örnek uzayı kapsar. \"En az bir\", \"hiçbiri\" gibi "
            "ifadelerde tümleyen çoğu zaman en kısa yoldur (§6.7)."
        ),
    ),
    LabStep(
        number=7,
        title="Birleşim ve kesişim",
        note=NoteRef("6.8", objects=("Şekil 6.9",)),
        explanation=(
            "$A \\cup B$: $A$ veya $B$ veya ikisi (göstergelerden en az biri 1). $A \\cap B$: hem $A$ hem $B$ "
            "(iki gösterge de 1). $A = \\{2, 4, 6\\}$ ve $B = \\{5, 6\\}$ için $A \\cup B = \\{2, 4, 5, 6\\}$ ve "
            "$A \\cap B = \\{6\\}$."
        ),
        operations=(
            Derive("zar", "A_veya_B", E.maximum(E.var("A"), E.var("B")), "A ∪ B: iki göstergenin büyüğü"),
            Derive("zar", "A_ve_B", E.mul(E.var("A"), E.var("B")), "A ∩ B: iki göstergenin çarpımı"),
            ShowFrame("zar", ("sonuc", "A", "B", "A_veya_B", "A_ve_B"), "Birleşim ve kesişim"),
            Statistic("zar", "olasilik", "sum", "P_A_veya_B", "P(A ∪ B)", where=("A_veya_B", 1), decimals=4),
            Statistic("zar", "olasilik", "sum", "P_A_ve_B", "P(A ∩ B)", where=("A_ve_B", 1), decimals=4),
        ),
        checks=(
            _scalar("P_A_veya_B", 4 / 6, "P(A ∪ B) = 4/6", 4),
            _scalar("P_A_ve_B", 1 / 6, "P(A ∩ B) = 1/6", 4),
        ),
        takeaway=(
            "Olasılıkta \"veya\" kapsayıcıdır: 6 hem A'da hem B'dedir ve A ∪ B'de bir kez yer alır. \"Yalnız biri\" "
            "ayrı bir olay olarak açıkça belirtilmelidir (§6.8)."
        ),
    ),
    LabStep(
        number=8,
        title="Toplama kuralı",
        note=NoteRef("6.9", objects=("Şekil 6.10",)),
        explanation=(
            "100 çalışanın 40'ı ileri Excel, 35'i Python kullanabiliyor, 15'i ikisini de. Rastgele seçilen bir "
            "çalışan için olasılıklar oranlardır. Toplama kuralı: $P(E \\cup P) = P(E) + P(P) - P(E \\cap P)$; ortak "
            "kısım $P(E)$ ve $P(P)$'de iki kez sayıldığı için bir kez çıkarılır."
        ),
        operations=(
            FromCounts("calisan", ("excel", "python"), SKILLS, "100 çalışan: ileri Excel ve Python"),
            CrossTab("calisan", "excel", "python", "beceri", ("Evet", "Hayır"), ("Evet", "Hayır"), margins=True),
            Event("calisan", "E", "excel", ("Evet",), "E: ileri Excel kullanabilir"),
            Event("calisan", "P", "python", ("Evet",), "P: Python kullanabilir"),
            Derive("calisan", "E_ve_P", E.mul(E.var("E"), E.var("P")), "E ∩ P: ikisini de kullanabilir"),
            Statistic("calisan", "E", "mean", "P_E", "P(E)", decimals=2),
            Statistic("calisan", "P", "mean", "P_P", "P(P)", decimals=2),
            Statistic("calisan", "E_ve_P", "mean", "P_E_ve_P", "P(E ∩ P)", decimals=2),
            Scalar("P_E_veya_P", E.sub(E.add(E.ref("P_E"), E.ref("P_P")), E.ref("P_E_ve_P")),
                   "P(E ∪ P): toplama kuralı", decimals=2),
            Derive("calisan", "E_veya_P", E.maximum(E.var("E"), E.var("P")), "E ∪ P: en az birini kullanabilir"),
            Statistic("calisan", "E_veya_P", "mean", "P_E_veya_P_sayim", "P(E ∪ P): doğrudan sayım", decimals=2),
        ),
        checks=(
            _scalar("P_E", 0.40, "P(E)", 2),
            _scalar("P_P", 0.35, "P(P)", 2),
            _scalar("P_E_ve_P", 0.15, "P(E ∩ P)", 2),
            _scalar("P_E_veya_P", 0.60, "P(E ∪ P) = 0,40 + 0,35 − 0,15", 2),
            _scalar("P_E_veya_P_sayim", 0.60, "P(E ∪ P): en az birini kullananların oranı", 2),
        ),
        takeaway=(
            "0,40 + 0,35 = 0,75 ortak %15'i iki kez sayar; çıkarınca 0,60 bulunur ve bu, en az birini kullananların "
            "doğrudan sayılan oranıyla aynıdır. Ayrık olaylarda P(A ∩ B) = 0 olduğu için kural P(A) + P(B)'ye "
            "sadeleşir; ayrıklık bağımsızlıkla aynı kavram değildir (§6.9)."
        ),
    ),
    LabStep(
        number=9,
        title="Bütünleştirici uygulama: tedarik performansı",
        note=NoteRef("6.10", objects=("Tablo 6.2", "Şekil 6.12")),
        explanation=(
            "Sevkiyatlar zamanında/geç ve hatasız/hatalı olarak sınıflandırılır; dört örnek noktanın olasılıkları "
            "Tablo 6.2'dedir. $Z$ = zamanında, $H$ = hatalı, $G = Z^c$ = geç. Ortak olasılık tablosunda her hücre bir "
            "örnek noktanın olasılığıdır; satır ve sütun toplamları olayların olasılıklarını verir."
        ),
        operations=(
            InlineData("sevkiyat", ("nokta", "zaman", "kalite", "olasilik"), SHIPMENTS,
                       "Tablo 6.2: örnek noktalar ve olasılıkları"),
            Statistic("sevkiyat", "olasilik", "sum", "toplam_olasilik", "Olasılıkların toplamı", decimals=2),
            CrossTab("sevkiyat", "zaman", "kalite", "ortak", ("Zamanında", "Geç"), ("Hatasız", "Hatalı"),
                     margins=True, decimals=2, weights="olasilik"),
            Event("sevkiyat", "Z", "zaman", ("Zamanında",), "Z: zamanında"),
            Event("sevkiyat", "H", "kalite", ("Hatalı",), "H: hatalı"),
            Derive("sevkiyat", "G", E.sub(1, E.var("Z")), "G = Zᶜ: geç"),
            Derive("sevkiyat", "G_ve_H", E.mul(E.var("G"), E.var("H")), "G ∩ H: geç ve hatalı"),
            Statistic("sevkiyat", "olasilik", "sum", "P_Z", "P(Z)", where=("Z", 1), decimals=2),
            Statistic("sevkiyat", "olasilik", "sum", "P_H", "P(H)", where=("H", 1), decimals=2),
            Statistic("sevkiyat", "olasilik", "sum", "P_G", "P(G)", where=("G", 1), decimals=2),
            Statistic("sevkiyat", "olasilik", "sum", "P_G_ve_H", "P(G ∩ H)", where=("G_ve_H", 1), decimals=2),
            Scalar("P_G_veya_H", E.sub(E.add(E.ref("P_G"), E.ref("P_H")), E.ref("P_G_ve_H")),
                   "P(G ∪ H) = P(G) + P(H) − P(G ∩ H)", decimals=2),
            Scalar("sorunsuz", E.sub(1, E.ref("P_G_veya_H")), "Zamanında ve hatasız: 1 − P(G ∪ H)", decimals=2),
        ),
        checks=(
            _scalar("toplam_olasilik", 1.00, "Örnek nokta olasılıklarının toplamı", 2),
            _scalar("P_Z", 0.78, "P(Z) = 0,70 + 0,08", 2),
            _scalar("P_H", 0.13, "P(H) = 0,08 + 0,05", 2),
            _scalar("P_G", 0.22, "P(G)", 2),
            _scalar("P_G_ve_H", 0.05, "P(G ∩ H)", 2),
            _scalar("P_G_veya_H", 0.30, "P(G ∪ H) = 0,22 + 0,13 − 0,05", 2),
            _scalar("sorunsuz", 0.70, "1 − 0,30 = P(E₁)", 2),
        ),
        takeaway=(
            "Sevkiyatların %30'unda en az bir performans problemi (gecikme veya hata) vardır. Bunun tümleyeni "
            "\"zamanında ve hatasız\" sonuçtur ve doğrudan P(E₁) = 0,70 ile aynıdır: aynı soruya iki yoldan gelmek "
            "hesabı denetlemenin iyi bir yoludur (§6.10)."
        ),
    ),
)

KONU06_LAB = LabSpec(
    topic_key="konu06",
    title="Örnek uzay, sayma ve temel olasılık kurallarını uygulamak",
    note_section="6",
    steps=STEPS,
    labels=(
        ("sonuc", "Sonuç"),
        ("birinci", "Birinci"),
        ("ikinci", "İkinci"),
        ("toplam", "İki zarın toplamı"),
        ("olasilik", "Olasılık P(Eᵢ)"),
        ("teslimat", "Teslimat"),
        ("odeme", "Ödeme"),
        ("baskan", "Başkan"),
        ("raportor", "Raportör"),
        ("durum", "Teslimat durumu"),
        ("A_veya_B", "A ∪ B"),
        ("A_ve_B", "A ∩ B"),
        ("A_degil", "Aᶜ"),
        ("excel", "İleri Excel"),
        ("python", "Python"),
        ("nokta", "Örnek nokta"),
        ("zaman", "Zaman durumu"),
        ("kalite", "Kalite durumu"),
        ("G_ve_H", "G ∩ H"),
    ),
)
