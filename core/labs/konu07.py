"""Konu 7 uygulaması: koşullu olasılık, bağımsızlık, çarpma kuralı, olasılık ağacı ve Bayes teoremi.

Ders notlarının çözümlü örnekleri: §7.1–7.4 (mağaza: cihaz ve satın alma; Tablo 7.1–7.2, Şekil 7.1–7.2), §7.5
(bağımsızlık kontrolü), §7.7 (çarpma kuralı), §7.8 (sipariş ağacı, Şekil 7.8), §7.10 (iki tedarikçi, Şekil 7.10),
§7.11 (Bayes tablosu, Tablo 7.4) ve §7.12 (sahtecilik alarmı ve temel oran; Tablo 7.5, Şekil 7.12). Buradaki her
``Check`` notlarda basılı bir sayıdır; değer notlardan kopyalanmıştır, hesaplanmamıştır. §7.6, §7.9 ve §7.13 hesap
içermez.

Koşullu olasılık, koşul olayındaki gözlemler (ya da örnek noktalar) içinde hesaplanan orandır: payda yeni bilgiye
göre daralır. Ağaçta ve Bayes tablosunda her satır bir yoldur; yolun ortak olasılığı dal olasılıklarının çarpımıdır.
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
    FromCounts,
    InlineData,
    LabSpec,
    LabStep,
    MosaicChart,
    NoteRef,
    Scalar,
    ScalarTable,
    ScalarTarget,
    ShowFrame,
    Statistic,
    TableTarget,
    TreeDiagram,
)

DEVICES = ("Mobil", "Masaüstü")
OUTCOMES = ("Satın aldı", "Satın almadı")
VISITS = (
    ("Mobil", "Satın aldı", 180),
    ("Mobil", "Satın almadı", 420),
    ("Masaüstü", "Satın aldı", 80),
    ("Masaüstü", "Satın almadı", 320),
)
"""§7.1–7.2 (Tablo 7.1): 1000 ziyaretçi; 600 mobil (180'i satın aldı), 400 masaüstü (80'i satın aldı)."""
ORDER_TREE = (
    ("Standart", "Aynı gün", 0.70, 0.80),
    ("Standart", "Daha geç", 0.70, 0.20),
    ("Öncelikli", "Aynı gün", 0.30, 0.95),
    ("Öncelikli", "Daha geç", 0.30, 0.05),
)
"""§7.8 (Şekil 7.8): sipariş türü ve kargo; her satır ağaçta bir yol (tür olasılığı, türe göre kargo olasılığı)."""
SUPPLIER_TREE = (
    ("T₁", "Kusurlu", 0.70, 0.02),
    ("T₁", "Sağlam", 0.70, 0.98),
    ("T₂", "Kusurlu", 0.30, 0.06),
    ("T₂", "Sağlam", 0.30, 0.94),
)
"""§7.10 (Şekil 7.10): önsel P(Tᵢ) ve koşullu P(durum | Tᵢ)."""
BAYES_TABLE = (("T₁", 0.70, 0.02), ("T₂", 0.30, 0.06))
"""§7.11 (Tablo 7.4): kaynak, önsel P(Tᵢ), koşullu P(K | Tᵢ)."""
ALARM_PATHS = (
    ("Sahte", "Alarm", 0.02, 0.90),
    ("Sahte", "Alarm yok", 0.02, 0.10),
    ("Sahte değil", "Alarm", 0.98, 0.05),
    ("Sahte değil", "Alarm yok", 0.98, 0.95),
)
"""§7.12: P(F) = 0,02; P(A | F) = 0,90; P(A | Fᶜ) = 0,05."""
NATURAL_TOTAL = 10000
"""§7.12 (Tablo 7.5): doğal frekanslar için düşünülen işlem sayısı."""


def _scalar(name: str, expected: float, label: str, decimals: int) -> Check:
    return Check(label, ScalarTarget(name), expected, decimals)


def _cell(table: str, row: object, column: object, expected: float, label: str, decimals: int) -> Check:
    return Check(label, TableTarget(table, row, column), expected, decimals)


STEPS = (
    LabStep(
        number=1,
        title="Yeni bilgi paydayı değiştirir",
        note=NoteRef("7.1", objects=("Şekil 7.1",)),
        explanation=(
            "Bir çevrim içi mağazanın 1000 ziyaretçisinin 600'ü mobil cihazdan, 400'ü masaüstü bilgisayardan "
            "girmiştir; mobil ziyaretçilerin 180'i, masaüstü ziyaretçilerin 80'i satın alma yapmıştır. $S$ = satın "
            "aldı, $M$ = mobil. $P(S)$ bütün ziyaretçiler içinde, $P(S \\mid M)$ ise yalnız mobil ziyaretçiler içinde "
            "satın alanların oranıdır: ziyaretçinin mobil olduğunu öğrenince ilgili grup 600 kişiye daralır."
        ),
        operations=(
            FromCounts("ziyaret", ("cihaz", "satin"), VISITS, "1000 ziyaretçi: cihaz türü ve satın alma"),
            Event("ziyaret", "S", "satin", ("Satın aldı",), "S: satın aldı"),
            Event("ziyaret", "M", "cihaz", ("Mobil",), "M: mobil cihaz"),
            Statistic("ziyaret", "S", "count", "n_ziyaret", "Ziyaretçi sayısı", decimals=0),
            Statistic("ziyaret", "S", "sum", "satin_sayisi", "Satın alan", decimals=0),
            Statistic("ziyaret", "M", "sum", "mobil_sayisi", "Mobil ziyaretçi", decimals=0),
            Statistic("ziyaret", "S", "sum", "mobil_satin", "Mobil ve satın alan", where=("M", 1), decimals=0),
            Scalar("mobil_almayan", E.sub(E.ref("mobil_sayisi"), E.ref("mobil_satin")), "Mobil ve satın almayan",
                   decimals=0),
            Statistic("ziyaret", "S", "mean", "P_S", "P(S): bütün ziyaretçiler içinde", decimals=2),
            Statistic("ziyaret", "S", "mean", "P_S_M", "P(S | M): mobiller içinde", where=("M", 1), decimals=2),
        ),
        checks=(
            _scalar("satin_sayisi", 260, "Satın alan ziyaretçi sayısı", 0),
            _scalar("mobil_sayisi", 600, "Mobil ziyaretçi sayısı", 0),
            _scalar("mobil_satin", 180, "Mobil ve satın alan", 0),
            _scalar("mobil_almayan", 420, "Mobil ve satın almayan", 0),
            _scalar("P_S", 0.26, "P(S) = 260/1000", 2),
            _scalar("P_S_M", 0.30, "P(S | M) = 180/600", 2),
        ),
        takeaway=(
            "Pay aynı 180 kişi olabilir; değişen paydadır. P(S) bütün 1000 ziyaretçiyi, P(S | M) yalnız 600 mobil "
            "ziyaretçiyi kullanır. Bu yüzden 0,26 ile 0,30 aynı sorunun cevabı değildir (§7.1)."
        ),
    ),
    LabStep(
        number=2,
        title="Çapraz tablo: ortak ve marjinal olasılıklar",
        note=NoteRef("7.2", objects=("Tablo 7.1", "Tablo 7.2", "Şekil 7.2")),
        explanation=(
            "Sayılar çapraz tabloya yazılır (Tablo 7.1). Her hücre toplam 1000'e bölününce iç hücreler **ortak "
            "olasılıklar** ($P(M \\cap S) = 0{,}18$), satır ve sütun toplamları **marjinal olasılıklar** "
            "($P(M) = 0{,}60$, $P(S) = 0{,}26$) olur (Tablo 7.2). Mozaik grafiğinde sütun genişliği marjinal "
            "olasılık, sütun içindeki yükseklik o sütundaki paydır; her parçanın alanı ortak olasılığa eşittir."
        ),
        operations=(
            CrossTab("ziyaret", "cihaz", "satin", "sayilar", DEVICES, OUTCOMES, margins=True),
            Derive("ziyaret", "pay", E.div(1, E.ref("n_ziyaret")), "Her ziyaretçinin payı 1/n"),
            CrossTab("ziyaret", "cihaz", "satin", "ortak", DEVICES, OUTCOMES, margins=True, decimals=2,
                     weights="pay"),
            MosaicChart("ortak", "Cihaz türü (sütun genişliği: marjinal olasılık)",
                        "Sütun içindeki pay", "Ortak ve marjinal olasılıklar: mozaik"),
        ),
        checks=(
            _cell("sayilar", "Masaüstü", "Satın almadı", 320, "Tablo 7.1: masaüstü ve satın almadı", 0),
            _cell("sayilar", "Mobil", "Toplam", 600, "Tablo 7.1: mobil toplamı", 0),
            _cell("sayilar", "Masaüstü", "Toplam", 400, "Tablo 7.1: masaüstü toplamı", 0),
            _cell("sayilar", "Toplam", "Satın aldı", 260, "Tablo 7.1: satın alanlar", 0),
            _cell("sayilar", "Toplam", "Satın almadı", 740, "Tablo 7.1: satın almayanlar", 0),
            _cell("sayilar", "Toplam", "Toplam", 1000, "Tablo 7.1: ziyaretçi sayısı", 0),
            _cell("ortak", "Mobil", "Satın aldı", 0.18, "P(M ∩ S)", 2),
            _cell("ortak", "Mobil", "Satın almadı", 0.42, "P(M ∩ Sᶜ)", 2),
            _cell("ortak", "Masaüstü", "Satın aldı", 0.08, "P(D ∩ S)", 2),
            _cell("ortak", "Masaüstü", "Satın almadı", 0.32, "P(D ∩ Sᶜ)", 2),
            _cell("ortak", "Mobil", "Toplam", 0.60, "P(M)", 2),
            _cell("ortak", "Masaüstü", "Toplam", 0.40, "P(D)", 2),
            _cell("ortak", "Toplam", "Satın aldı", 0.26, "P(S)", 2),
            _cell("ortak", "Toplam", "Satın almadı", 0.74, "P(Sᶜ)", 2),
            _cell("ortak", "Toplam", "Toplam", 1.00, "Ortak olasılıkların toplamı", 2),
        ),
        takeaway=(
            "İç hücreler iki olayın birlikte gerçekleşmesini, kenarlar tek bir değişkeni gösterir. Mozaikte "
            "mobil-satın almayan parçanın alanı (0,42) mobil-satın alan parçanınkinden (0,18) büyüktür; mobil "
            "sütununun içinde satın alanların payı 0,30, masaüstünde 0,20'dir (§7.2)."
        ),
    ),
    LabStep(
        number=3,
        title="Koşullu olasılık formülü",
        note=NoteRef("7.3"),
        explanation=(
            "Koşullu olasılık ortak olasılığın koşul olayının olasılığına bölümüdür: "
            "$P(A \\mid B) = P(A \\cap B)/P(B)$, $P(B) > 0$. Pay $A$ ile $B$'nin birlikte gerçekleştiği bölge, "
            "payda artık içinde çalıştığımız koşul olayıdır. Satır yüzdeleri tablosunun her satırı, o satır "
            "verildiğinde koşullu olasılıkları (yüzde olarak) verir."
        ),
        operations=(
            Derive("ziyaret", "M_ve_S", E.mul(E.var("M"), E.var("S")), "M ∩ S: mobil ve satın aldı"),
            Statistic("ziyaret", "M_ve_S", "mean", "P_MS", "P(M ∩ S)", decimals=2),
            Statistic("ziyaret", "M", "mean", "P_M", "P(M)", decimals=2),
            Scalar("P_S_M_formul", E.div(E.ref("P_MS"), E.ref("P_M")), "P(S | M) = P(M ∩ S)/P(M)", decimals=2),
            Statistic("ziyaret", "S", "mean", "P_S_D", "P(S | D): masaüstü içinde", where=("M", 0), decimals=2),
            CrossTab("ziyaret", "cihaz", "satin", "kosullu", DEVICES, OUTCOMES, percent="satir", margins=True,
                     decimals=1),
        ),
        checks=(
            _scalar("P_MS", 0.18, "P(M ∩ S) = 180/1000", 2),
            _scalar("P_M", 0.60, "P(M) = 600/1000", 2),
            _scalar("P_S_M_formul", 0.30, "P(S | M) = 0,18/0,60", 2),
            _scalar("P_S_D", 0.20, "Masaüstü sütunundaki pay: 0,08/0,40", 2),
            _cell("kosullu", "Mobil", "Satın aldı", 30.0, "Mobillerin yüzde kaçı satın aldı", 1),
        ),
        takeaway=(
            "Sayılarla (180/600) ve olasılıklarla (0,18/0,60) aynı sonuç çıkar: 0,30. En yaygın hata paydada bütün "
            "örnek uzayı kullanmaya devam etmektir; P(A | B) sorulduğunda payda P(B)'dir (§7.3)."
        ),
    ),
    LabStep(
        number=4,
        title="Koşulun yönü: P(S | M) ile P(M | S)",
        note=NoteRef("7.4", objects=("Şekil 7.4",)),
        explanation=(
            "Aynı iki olayda $P(S \\mid M)$ ile $P(M \\mid S)$ genellikle farklıdır. $P(S \\mid M)$ mobil kullanıcılar "
            "içinde satın alanların, $P(M \\mid S)$ satın alanlar içinde mobil kullanıcıların oranıdır. Sütun "
            "yüzdeleri tablosu satın alma durumu verildiğinde cihaz türünün koşullu olasılıklarını verir."
        ),
        operations=(
            Statistic("ziyaret", "M", "mean", "P_M_S", "P(M | S): satın alanlar içinde", where=("S", 1), decimals=3),
            Scalar("yuzde_M_S", E.mul(100, E.ref("P_M_S")), "Satın alanların mobil yüzdesi", decimals=1,
                   percent=True),
            CrossTab("ziyaret", "cihaz", "satin", "sutun_yuzde", DEVICES, OUTCOMES, percent="sutun", margins=True,
                     decimals=1),
        ),
        checks=(
            _scalar("P_M_S", 0.692, "P(M | S) = 180/260", 3),
            _scalar("yuzde_M_S", 69.2, "Satın alanların yüzde kaçı mobil", 1),
            _cell("sutun_yuzde", "Mobil", "Satın aldı", 69.2, "Sütun yüzdesi: satın alanlar içinde mobil", 1),
        ),
        takeaway=(
            "Pay aynı ortak hücredir (180), ama koşul değişince payda değişir: 600 yerine 260. Mobil kullanıcıların "
            "%30'u satın alır; satın alanların ise yaklaşık %69,2'si mobildir. Dikey çizginin sağındaki olay "
            "karşılaştırma grubunu belirler (§7.4)."
        ),
    ),
    LabStep(
        number=5,
        title="Bağımsızlık kontrolü",
        note=NoteRef("7.5", objects=("Şekil 7.5",)),
        explanation=(
            "$A$ ile $B$ bağımsızsa $B$'nin gerçekleştiğini öğrenmek $A$'nın olasılığını değiştirmez: "
            "$P(A \\mid B) = P(A)$. Notlardaki örnekte siparişlerin %40'ı ekspres teslimattır ve kartla ödeyenler "
            "içinde de oran %40'tır: $P(E \\mid K) = P(E) = 0{,}40$. Mağaza verisinde aynı kontrol "
            "$P(S \\mid M)$ ile $P(S)$ karşılaştırılarak yapılır."
        ),
        operations=(
            Scalar("P_E", E.const(0.40), "Ekspres: P(E)", decimals=2),
            Scalar("P_E_K", E.const(0.40), "Kartla ödeyenler içinde: P(E | K)", decimals=2),
            Scalar("fark_E", E.sub(E.ref("P_E_K"), E.ref("P_E")), "P(E | K) − P(E)", decimals=2),
            ScalarTable(
                (
                    ("Ekspres teslimat: P(E)", E.ref("P_E")),
                    ("Kartla ödeyenlerde: P(E | K)", E.ref("P_E_K")),
                    ("Mağaza: P(S)", E.ref("P_S")),
                    ("Mağaza, mobillerde: P(S | M)", E.ref("P_S_M")),
                    ("Mağaza, masaüstünde: P(S | D)", E.ref("P_S_D")),
                ),
                "bagimsizlik",
            ),
        ),
        checks=(
            _scalar("P_E_K", 0.40, "P(E | K)", 2),
            _scalar("fark_E", 0.00, "P(E | K) = P(E): fark sıfır", 2),
        ),
        takeaway=(
            "Ekspres örneğinde kart bilgisi oranı değiştirmez: E ve K bağımsızdır. Mağazada ise P(S | M) = 0,30 ile "
            "P(S) = 0,26 farklıdır; cihaz bilgisi satın alma olasılığını değiştirdiği için S ile M bağımlıdır. "
            "Bağımsız olaylar birlikte gerçekleşebilir; bağımsızlık ayrıklık demek değildir (§7.5, §7.6)."
        ),
    ),
    LabStep(
        number=6,
        title="Çarpma kuralı",
        note=NoteRef("7.7", objects=("Şekil 7.7",)),
        explanation=(
            "Koşullu olasılık formülü yeniden düzenlenince $P(A \\cap B) = P(A)P(B \\mid A)$ elde edilir. Siparişlerin "
            "%80'inin ödemesi aynı gün tamamlanır ($O$), bunların %90'ı aynı gün kargoya verilir ($K$). Bağımsız "
            "olaylarda kural $P(A \\cap B) = P(A)P(B)$'ye sadeleşir; bu eşitlik bağımsızlığı denetlemek için de "
            "kullanılabilir."
        ),
        operations=(
            Scalar("P_O", E.const(0.80), "P(O): ödeme aynı gün", decimals=2),
            Scalar("P_K_O", E.const(0.90), "P(K | O): aynı gün kargo", decimals=2),
            Scalar("P_OK", E.mul(E.ref("P_O"), E.ref("P_K_O")), "P(O ∩ K) = P(O)P(K | O)", decimals=2),
            Scalar("carpim_MS", E.mul(E.ref("P_M"), E.ref("P_S")), "Mağaza: P(M)P(S)", decimals=3),
        ),
        checks=(
            _scalar("P_OK", 0.72, "P(O ∩ K) = 0,80 × 0,90", 2),
        ),
        takeaway=(
            "Siparişlerin %72'si hem aynı gün ödenmiş hem aynı gün kargoya verilmiştir. Mağazada P(M)P(S) = 0,156 "
            "iken P(M ∩ S) = 0,18'dir; çarpım eşitliği sağlanmadığı için S ile M bağımsız değildir (§7.7)."
        ),
    ),
    LabStep(
        number=7,
        title="Olasılık ağacı",
        note=NoteRef("7.8", objects=("Şekil 7.8",)),
        explanation=(
            "Siparişlerin %70'i standart ($S$), %30'u öncelikli ($O$); standartların %80'i, önceliklilerin %95'i aynı "
            "gün kargolanır ($A$), diğerleri daha geç ($G$). Ağaçta her tam yol bir ortak sonuçtur: aynı yol "
            "üzerindeki olasılıklar çarpılır, aynı sonuca ulaşan farklı yolların ortak olasılıkları toplanır."
        ),
        operations=(
            InlineData("siparis", ("sinif", "kargo", "p_sinif", "p_kargo"), ORDER_TREE,
                       "Ağacın yolları: sipariş türü ve kargo"),
            Derive("siparis", "ortak", E.mul(E.var("p_sinif"), E.var("p_kargo")),
                   "Yolun ortak olasılığı: dal olasılıkları çarpılır"),
            TreeDiagram("siparis", "sinif", "kargo", "p_sinif", "p_kargo", "Sipariş",
                        "Sipariş türü ve kargo: iki aşamalı olasılık ağacı"),
            ShowFrame("siparis", ("sinif", "kargo", "ortak"), "Dört yolun ortak olasılıkları"),
            Statistic("siparis", "ortak", "sum", "yol_toplami", "Dört ortak olasılığın toplamı", decimals=0),
            Event("siparis", "A", "kargo", ("Aynı gün",), "A: aynı gün kargolandı"),
            Statistic("siparis", "ortak", "sum", "P_A", "P(A): aynı gün yollarının toplamı", where=("A", 1),
                      decimals=3),
        ),
        checks=(
            Check("P(S ∩ A) = 0,70(0,80)", CellTarget("siparis", "ortak", 1), 0.56, 2),
            Check("P(S ∩ G) = 0,70(0,20)", CellTarget("siparis", "ortak", 2), 0.14, 2),
            Check("P(O ∩ A) = 0,30(0,95)", CellTarget("siparis", "ortak", 3), 0.285, 3),
            Check("P(O ∩ G) = 0,30(0,05)", CellTarget("siparis", "ortak", 4), 0.015, 3),
            _scalar("yol_toplami", 1, "Dört ortak olasılığın toplamı", 0),
            _scalar("P_A", 0.845, "P(A) = 0,56 + 0,285", 3),
        ),
        takeaway=(
            "Aynı gün kargolanma iki yoldan gelir: standart ve aynı gün (0,56) ile öncelikli ve aynı gün (0,285). "
            "Yollar birbirini dışladığı için olasılıklar toplanır: P(A) = 0,845. Bu iki işlem, çarpma ve toplama, "
            "Bayes teoreminde yeniden kullanılır (§7.8)."
        ),
    ),
    LabStep(
        number=8,
        title="Bayes teoremi: iki tedarikçi",
        note=NoteRef("7.10", objects=("Şekil 7.10",)),
        explanation=(
            "Parçaların %70'i Tedarikçi 1'den ($T_1$), %30'u Tedarikçi 2'den ($T_2$) gelir; kusur oranları %2 ve "
            "%6'dır. Kusurlu bir parça gözlendiğinde $P(T_2 \\mid K)$ aranır. Önce kusurlu sonuca ulaşan iki yolun "
            "ortak olasılıkları bulunur, sonra ilgilenilen yol bu iki yolun toplamı içinde yeniden oranlanır: "
            "$P(T_2 \\mid K) = P(T_2 \\cap K)/P(K)$."
        ),
        operations=(
            InlineData("parca", ("tedarikci", "durum", "onsel", "kosullu"), SUPPLIER_TREE,
                       "Ağacın yolları: tedarikçi ve parça durumu"),
            Derive("parca", "ortak", E.mul(E.var("onsel"), E.var("kosullu")), "Yolun ortak olasılığı"),
            TreeDiagram("parca", "tedarikci", "durum", "onsel", "kosullu", "Parça",
                        "İki tedarikçili Bayes probleminde olasılık ağacı"),
            Event("parca", "K", "durum", ("Kusurlu",), "K: kusurlu parça"),
            Event("parca", "T2", "tedarikci", ("T₂",), "T₂: ikinci tedarikçi"),
            Derive("parca", "T2_ve_K", E.mul(E.var("T2"), E.var("K")), "T₂ ∩ K: ikinci tedarikçi ve kusurlu"),
            Statistic("parca", "ortak", "sum", "P_K", "P(K): kusurlu yolların toplamı", where=("K", 1), decimals=3),
            Statistic("parca", "ortak", "sum", "P_T2_K", "P(T₂ ∩ K)", where=("T2_ve_K", 1), decimals=3),
            Scalar("P_T2_bilinen_K", E.div(E.ref("P_T2_K"), E.ref("P_K")), "P(T₂ | K) = P(T₂ ∩ K)/P(K)",
                   decimals=4),
        ),
        checks=(
            Check("P(T₁ ∩ K) = 0,70(0,02)", CellTarget("parca", "ortak", 1), 0.014, 3),
            Check("P(T₂ ∩ K) = 0,30(0,06)", CellTarget("parca", "ortak", 3), 0.018, 3),
            _scalar("P_K", 0.032, "P(K) = 0,014 + 0,018", 3),
            _scalar("P_T2_bilinen_K", 0.5625, "P(T₂ | K) = 0,018/0,032", 4),
        ),
        takeaway=(
            "Parçaların yalnız %30'u T₂'den gelir, ama kusurlu olduğu bilinen parçalar içinde T₂'nin payı %56,25'tir: "
            "T₂'nin kusur oranı daha yüksektir. Bayes hesabı kusurlu sonuca ulaşan iki dalı (0,014 ve 0,018) "
            "toplamları 0,032 içinde yeniden oranlar (§7.10)."
        ),
    ),
    LabStep(
        number=9,
        title="Bayes hesabı tabloyla",
        note=NoteRef("7.11", objects=("Tablo 7.4",)),
        explanation=(
            "Kategori sayısı arttıkça tablo daha düzenlidir: (1) kaynakları ve önsel olasılıkları yazın, (2) her "
            "kaynak için yeni bilginin koşullu olasılığını yazın, (3) ikisini çarparak ortak olasılıkları bulun, "
            "(4) ortak olasılıkları kendi toplamlarına bölerek sonsal olasılıkları elde edin."
        ),
        operations=(
            InlineData("bayes", ("kaynak", "onsel", "kosullu"), BAYES_TABLE,
                       "Kaynaklar, önsel ve koşullu olasılıklar"),
            Derive("bayes", "ortak", E.mul(E.var("onsel"), E.var("kosullu")), "Ortak = önsel × koşullu"),
            Statistic("bayes", "ortak", "sum", "P_K_tablo", "P(K): ortak olasılıkların toplamı", decimals=3),
            Derive("bayes", "sonsal", E.div(E.var("ortak"), E.ref("P_K_tablo")), "Sonsal = ortak / P(K)"),
            ShowFrame("bayes", ("kaynak", "onsel", "kosullu", "ortak", "sonsal"), "Bayes tablosu (Tablo 7.4)"),
            Statistic("bayes", "onsel", "sum", "onsel_toplami", "Önsel olasılıkların toplamı", decimals=2),
            Statistic("bayes", "sonsal", "sum", "sonsal_toplami", "Sonsal olasılıkların toplamı", decimals=4),
        ),
        checks=(
            Check("Sonsal P(T₁ | K) = 0,014/0,032", CellTarget("bayes", "sonsal", 1), 0.4375, 4),
            Check("Sonsal P(T₂ | K) = 0,018/0,032", CellTarget("bayes", "sonsal", 2), 0.5625, 4),
            _scalar("P_K_tablo", 0.032, "P(K)", 3),
            _scalar("onsel_toplami", 1.00, "Önsel toplamı", 2),
            _scalar("sonsal_toplami", 1.0000, "Sonsal toplamı", 4),
        ),
        takeaway=(
            "Tablo, ağaçtaki iki işlemi sütunlara çevirir: ortak sütunu yol çarpımlarıdır, toplamı P(K)'dir; sonsal "
            "sütunu ortak olasılıkların P(K) içindeki payıdır ve toplamı 1'dir (§7.11)."
        ),
    ),
    LabStep(
        number=10,
        title="Bütünleştirici uygulama: alarm ve temel oran",
        note=NoteRef("7.12", objects=("Tablo 7.5", "Şekil 7.12")),
        explanation=(
            "İşlemlerin yalnız %2'si sahtedir ($F$); alarm sistemi sahte işlemlerin %90'ında, sahte olmayanların "
            "%5'inde alarm üretir ($A$). Alarm verildiğinde işlemin gerçekten sahte olma olasılığı "
            "$P(F \\mid A) = P(F \\cap A)/P(A)$'dır. Doğal frekans tablosu aynı hesabı 10.000 işlem üzerinden "
            "sayılarla gösterir."
        ),
        operations=(
            InlineData("alarm", ("durum", "sinyal", "onsel", "kosullu"), ALARM_PATHS,
                       "Yollar: gerçek durum ve alarm"),
            Derive("alarm", "ortak", E.mul(E.var("onsel"), E.var("kosullu")), "Yolun ortak olasılığı"),
            Event("alarm", "F", "durum", ("Sahte",), "F: işlem sahte"),
            Event("alarm", "A", "sinyal", ("Alarm",), "A: alarm verildi"),
            Derive("alarm", "F_ve_A", E.mul(E.var("F"), E.var("A")), "F ∩ A: sahte ve alarm"),
            Derive("alarm", "Fc_ve_A", E.mul(E.sub(1, E.var("F")), E.var("A")), "Fᶜ ∩ A: sahte değil ve alarm"),
            Statistic("alarm", "ortak", "sum", "P_FA", "P(F ∩ A)", where=("F_ve_A", 1), decimals=3),
            Statistic("alarm", "ortak", "sum", "P_FcA", "P(Fᶜ ∩ A)", where=("Fc_ve_A", 1), decimals=3),
            Statistic("alarm", "ortak", "sum", "P_A_alarm", "P(A): toplam alarm olasılığı", where=("A", 1),
                      decimals=3),
            Scalar("P_F_bilinen_A", E.div(E.ref("P_FA"), E.ref("P_A_alarm")), "P(F | A) = P(F ∩ A)/P(A)",
                   decimals=3),
            Derive("alarm", "islem", E.mul(NATURAL_TOTAL, E.var("ortak")), "10.000 işlemde beklenen sayı"),
            CrossTab("alarm", "durum", "sinyal", "dogal", ("Sahte", "Sahte değil"), ("Alarm", "Alarm yok"),
                     margins=True, decimals=0, weights="islem"),
            BarChart("dogal", "Alarm", "Gerçek durum", "Alarm alan işlem sayısı",
                     "Alarm alan 670 işlem: gerçek sahte ve yanlış alarm"),
            Statistic("alarm", "islem", "sum", "dogru_alarm", "Alarm alan sahte işlem", where=("F_ve_A", 1),
                      decimals=0),
            Statistic("alarm", "islem", "sum", "toplam_alarm", "Alarm alan işlem", where=("A", 1), decimals=0),
            Scalar("dogal_oran", E.div(E.ref("dogru_alarm"), E.ref("toplam_alarm")), "180/670", decimals=3),
        ),
        checks=(
            _scalar("P_FA", 0.018, "P(F ∩ A) = 0,02(0,90)", 3),
            _scalar("P_FcA", 0.049, "P(Fᶜ ∩ A) = 0,98(0,05)", 3),
            _scalar("P_A_alarm", 0.067, "P(A) = 0,018 + 0,049", 3),
            _scalar("P_F_bilinen_A", 0.269, "P(F | A) = 0,018/0,067", 3),
            _cell("dogal", "Sahte", "Alarm", 180, "Tablo 7.5: sahte ve alarm", 0),
            _cell("dogal", "Sahte", "Alarm yok", 20, "Tablo 7.5: sahte ve alarm yok", 0),
            _cell("dogal", "Sahte", "Toplam", 200, "Tablo 7.5: sahte işlem", 0),
            _cell("dogal", "Sahte değil", "Alarm", 490, "Tablo 7.5: yanlış alarm", 0),
            _cell("dogal", "Sahte değil", "Alarm yok", 9310, "Tablo 7.5: sahte değil ve alarm yok", 0),
            _cell("dogal", "Sahte değil", "Toplam", 9800, "Tablo 7.5: sahte olmayan işlem", 0),
            _cell("dogal", "Toplam", "Alarm", 670, "Tablo 7.5: alarm alan işlem", 0),
            _cell("dogal", "Toplam", "Alarm yok", 9330, "Tablo 7.5: alarm almayan işlem", 0),
            _cell("dogal", "Toplam", "Toplam", 10000, "Tablo 7.5: işlem sayısı", 0),
            _scalar("dogal_oran", 0.269, "180/670", 3),
        ),
        takeaway=(
            "Alarm verilse bile işlemin gerçekten sahte olma olasılığı yaklaşık %26,9'dur. Sahtecilik başlangıçta "
            "nadirdir (temel oran %2); büyük \"sahte değil\" grubunun yalnız %5'i yanlış alarm üretse de 490 işlem "
            "eder ve 180 gerçek alarmı sayıca geçer. Bayes teoremi hem alarmın doğruluğunu hem temel oranı birlikte "
            "hesaba katar (§7.12)."
        ),
    ),
)

KONU07_LAB = LabSpec(
    topic_key="konu07",
    title="Koşullu olasılık, bağımsızlık ve Bayes teoremini uygulamak",
    note_section="7",
    steps=STEPS,
    labels=(
        ("cihaz", "Cihaz türü"),
        ("satin", "Satın alma durumu"),
        ("pay", "Ziyaretçinin payı (1/n)"),
        ("M_ve_S", "M ∩ S"),
        ("sinif", "Sipariş türü"),
        ("kargo", "Kargo"),
        ("p_sinif", "P(tür)"),
        ("p_kargo", "P(kargo | tür)"),
        ("ortak", "Ortak olasılık"),
        ("tedarikci", "Tedarikçi"),
        ("durum", "Durum"),
        ("onsel", "Önsel olasılık"),
        ("kosullu", "Koşullu olasılık"),
        ("sonsal", "Sonsal olasılık"),
        ("kaynak", "Kaynak"),
        ("T2_ve_K", "T₂ ∩ K"),
        ("sinyal", "Alarm durumu"),
        ("F_ve_A", "F ∩ A"),
        ("Fc_ve_A", "Fᶜ ∩ A"),
        ("islem", "10.000 işlemde sayı"),
    ),
)
