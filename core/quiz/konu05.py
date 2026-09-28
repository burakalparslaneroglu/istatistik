"""Konu 5 "Kendini sına" soru seti.

Her soru tek bir kavramı sınar ve notlardaki bir bölüme bağlıdır. Sorular notların Egzersiz 5.1–5.13 ve
Mini Quiz 5.1–5.13 maddelerini tekrar etmez (ör. 68–72 ve 50–90 notlu iki sınıf, 2, 4, 6 verisinin varyansı,
s² = 16 ve 49, Q₁ = 40 ve Q₃ = 56 ile aykırı değer, 12, 18, 25, 31, 40 beş sayı özeti, kovaryansın işareti,
r = 0,85 ve −0,90 ifadeleri); yeni sayılarla ve yeni bağlamlarla aynı becerileri sınar. Çeyrekler notlardaki
L_p = (p/100)(n + 1) kuralıyla hesaplanır; varyans ve kovaryansın paydası n − 1'dir.
"""

from __future__ import annotations

from core.labs.spec import NoteRef
from core.quiz.expression import Symbol
from core.quiz.model import (
    Equation,
    FillBlanks,
    MultipleChoice,
    NumberBlank,
    Question,
    QuestionSet,
    TrueFalse,
)


def _note(section: str, *objects: str) -> NoteRef:
    return NoteRef(section, 0, tuple(objects))


QUESTIONS = (
    # --- Çoktan seçmeli -----------------------------------------------------------
    Question(
        key="k01", concept="iqr-den-ucuncu-ceyrek", note=_note("5.2", "(5.2)"),
        prompt="Bir veri setinde Q₁ = 40 ve IQR = 18'dir. Üçüncü çeyrek Q₃ kaçtır?",
        answer=MultipleChoice(("22", "49", "58", "76"), correct=2),
        explanation=(
            "IQR = Q₃ − Q₁ olduğundan Q₃ = Q₁ + IQR = 40 + 18 = 58. 49, 40 ile 58'in ortası; 22 ise 40 − 18'dir. "
            "IQR orta %50'nin genişliğidir (§5.2, (5.2))."
        ),
    ),
    Question(
        key="k02", concept="varyans-kaydirmaya-duyarsiz", note=_note("5.3", "(5.3)"),
        prompt="Bir veri setindeki her gözleme 10 eklenirse örneklem varyansı nasıl değişir?",
        answer=MultipleChoice(("10 artar", "Değişmez", "100 artar", "10 katına çıkar"), correct=1),
        explanation=(
            "Her gözlem 10 artınca ortalama da 10 artar; sapmalar xᵢ − x̄ aynı kalır. Varyans sapmalardan "
            "hesaplandığı için değişmez. Yayılım, verinin eksende kaydırılmasından etkilenmez (§5.3, (5.3))."
        ),
    ),
    Question(
        key="k03", concept="kuyruga-gore-adlandirma", note=_note("5.6", "Şekil 5.7"),
        prompt=(
            "Bir hastanede bekleme sürelerinin çoğu 5–15 dakikadır; az sayıda hasta 60–90 dakika beklemiştir. "
            "Bekleme sürelerinin dağılımı en iyi nasıl adlandırılır?"
        ),
        answer=MultipleChoice(("Sağa çarpık", "Sola çarpık", "Simetrik", "Tek-düze"), correct=0),
        explanation=(
            "Uzun kuyruk büyük değerlere doğru uzanır; çarpıklık kuyruğun yönüyle adlandırıldığı için dağılım "
            "sağa çarpıktır. Değerlerin çoğunun solda toplanması adlandırmayı belirlemez (§5.6, Şekil 5.7)."
        ),
    ),
    Question(
        key="k04", concept="aykiri-deger-kaynagi", note=_note("5.9"),
        prompt=(
            "Hanelerin aylık gelirini içeren bir veri setine yanlışlıkla bir şirketin aylık cirosu girilmiştir. "
            "Bu gözlem hangi aykırı değer kaynağına örnektir?"
        ),
        answer=MultipleChoice(
            (
                "Gerçekten sıra dışı ama doğru bir gözlem",
                "Dağılımın sola çarpık olması",
                "Örneklemin çok büyük olması",
                "İncelenen anakütleye ait olmayan birimin veri setine girmesi",
            ),
            correct=3,
        ),
        explanation=(
            "Şirket bir hane değildir; gözlem incelenen anakütlenin birimi olmadığı için veri setine ait değildir. "
            "Aykırı değer veri giriş hatası, yanlış birim ya da doğru ama sıra dışı bir gözlem olabilir; karar "
            "nedeni incelendikten sonra verilir (§5.9)."
        ),
    ),
    Question(
        key="k05", concept="birim-degisiminde-kovaryans-ve-r", note=_note("5.12", "(5.12)"),
        prompt=(
            "Reklam sayısı ile satış arasındaki ilişkide satışlar bin TL yerine TL ile ölçülürse (her değer 1.000 "
            "ile çarpılırsa) kovaryans ve korelasyon nasıl değişir?"
        ),
        answer=MultipleChoice(
            (
                "İkisi de 1.000 katına çıkar.",
                "Kovaryans 1.000 katına çıkar; korelasyon değişmez.",
                "İkisi de değişmez.",
                "Kovaryans değişmez; korelasyon 1.000 katına çıkar.",
            ),
            correct=1,
        ),
        explanation=(
            "yᵢ − ȳ sapmaları 1.000 katına çıktığı için s_xy de 1.000 katına çıkar. s_y de 1.000 katına çıktığından "
            "r = s_xy/(s_x s_y) değişmez: korelasyon ölçekten bağımsızdır (§5.12, §5.11)."
        ),
    ),
    Question(
        key="k06", concept="korelasyonla-serpilme-diyagrami", note=_note("5.13", "Tablo 5.3"),
        prompt="İki nicel değişken arasındaki korelasyon raporlanırken yanında mutlaka ne sunulmalıdır?",
        answer=MultipleChoice(
            (
                "İki değişkenin modları",
                "Değişkenlerin değişim aralıkları",
                "Kovaryansın mutlak değeri",
                "Serpilme diyagramı",
            ),
            correct=3,
        ),
        explanation=(
            "Korelasyon yalnız doğrusal ilişkiyi özetler; eğrisel bir ilişki veya birkaç uç nokta tek bir r değerinde "
            "görünmez. Raporlama ilkesi korelasyonun serpilme diyagramıyla birlikte değerlendirilmesidir (§5.13)."
        ),
    ),
    Question(
        key="k07", concept="farkli-derslerde-goreli-konum", note=_note("5.7", "(5.7)"),
        prompt=(
            "Bir öğrenci matematikte 72 (sınıf ortalaması 60, standart sapma 8), fizikte 80 (ortalama 70, standart "
            "sapma 5) almıştır. Öğrenci hangi derste sınıfına göre daha iyi bir konumdadır?"
        ),
        answer=MultipleChoice(
            (
                "Fizikte: z = 2,0",
                "Matematikte: ortalamanın 12 puan üzerinde",
                "İkisi aynı: iki derste de ortalamanın üzerinde",
                "Karşılaştırılamaz: ölçekler farklı",
            ),
            correct=0,
        ),
        explanation=(
            "z_mat = (72 − 60)/8 = 1,5 ve z_fiz = (80 − 70)/5 = 2,0. Ham fark matematikte büyük olsa da fizikte "
            "yayılım küçük olduğu için öğrenci ortalamadan standart sapma cinsinden daha uzaktadır (§5.7, (5.7))."
        ),
    ),
    # --- Doğru–yanlış -------------------------------------------------------------
    Question(
        key="d01", concept="ayni-ortalama-ayni-tutarlilik-degil", note=_note("5.1", "Şekil 5.1"),
        prompt=(
            "İki makinenin doldurduğu şişelerin ortalama hacmi 500 ml'dir; A makinesinde hacimler 498–502 ml, "
            "B makinesinde 490–510 ml arasındadır. Ortalamalar eşit olduğu için iki makine eşit derecede tutarlıdır."
        ),
        answer=TrueFalse(False),
        explanation=(
            "Ortalama yalnız merkezi söyler. B'nin hacimleri daha geniş bir aralığa yayılır; B daha az tutarlıdır. "
            "Bir veri seti merkez ve yayılımla birlikte özetlenir (§5.1)."
        ),
    ),
    Question(
        key="d02", concept="sifir-varyans-sabit-veri", note=_note("5.3", "(5.3)"),
        prompt="Bir veri setinin örneklem varyansı 0 ise bütün gözlemler birbirine eşittir.",
        answer=TrueFalse(True),
        explanation=(
            "Varyans kareli sapmalardan hesaplanır ve kareler negatif olamaz. Toplamın 0 olması için her sapmanın "
            "0 olması, yani her gözlemin ortalamaya eşit olması gerekir (§5.3, (5.3))."
        ),
    ),
    Question(
        key="d03", concept="cv-oran-olcegi-ister", note=_note("5.5"),
        prompt=(
            "Celsius cinsinden ölçülen günlük sıcaklıklar için değişim katsayısı anlamlı bir göreli değişkenlik "
            "ölçüsüdür."
        ),
        answer=TrueFalse(False),
        explanation=(
            "CV, sıfırın anlamlı bir başlangıç olduğu oran ölçekli değişkenlerde yorumlanır. Celsius'ta 0 °C "
            "\"sıcaklık yok\" demek değildir; ortalama sıfıra yakınsa veya negatifse CV yanıltıcı olur (§5.5)."
        ),
    ),
    Question(
        key="d04", concept="esit-ortalama-medyan-simetri-kaniti-degil", note=_note("5.6"),
        prompt="Ortalama ile medyanın eşit olması, dağılımın simetrik olduğunu kesin olarak gösterir.",
        answer=TrueFalse(False),
        explanation=(
            "Ortalama–medyan karşılaştırması bir yorum yardımcısıdır, kesin bir kural değildir. Dağılımın biçimi "
            "histogram veya kutu grafiğiyle birlikte değerlendirilir (§5.6)."
        ),
    ),
    Question(
        key="d05", concept="chebyshev-k1-bilgi-vermez", note=_note("5.8", "(5.8)"),
        prompt=(
            "k = 1 için Chebyshev'in alt sınırı 1 − 1/1² = 0'dır; eşitsizlik ortalamanın bir standart sapma "
            "çevresindeki gözlemler hakkında bilgi vermez."
        ),
        answer=TrueFalse(True),
        explanation=(
            "Alt sınır 1 − 1/k² ancak k > 1 için pozitiftir: k = 2'de 0,75, k = 3'te yaklaşık 0,889. Bu yüzden "
            "eşitsizlik k > 1 için ifade edilir (§5.8, (5.8))."
        ),
    ),
    Question(
        key="d06", concept="biyik-aykiri-degere-uzanmaz", note=_note("5.10", "Şekil 5.11"),
        prompt="Standart kutu grafiğinde bıyıklar her zaman veri setinin en küçük ve en büyük gözlemine kadar uzanır.",
        answer=TrueFalse(False),
        explanation=(
            "Bıyıklar Q₁ − 1,5·IQR ve Q₃ + 1,5·IQR sınırlarının içindeki en uç gözlemlere uzanır. Gelir verisinde "
            "en büyük değer 65'tir ama üst bıyık 30'da biter; 65 ayrı bir nokta olarak çizilir (§5.10)."
        ),
    ),
    Question(
        key="d07", concept="r-eksi-bir-tam-dogrusal", note=_note("5.12", "Şekil 5.15"),
        prompt="r = −1 ise serpilme diyagramındaki bütün noktalar negatif eğimli tek bir doğru üzerindedir.",
        answer=TrueFalse(True),
        explanation=(
            "|r| = 1 tam doğrusal ilişki demektir; işaret eğimin yönünü verir. |r| küçüldükçe noktalar doğru "
            "çevresinde daha geniş dağılır (§5.12)."
        ),
    ),
    # --- Boşluk doldurma ----------------------------------------------------------
    Question(
        key="b01", concept="ham-veriden-aralik-ve-iqr", note=_note("5.2", "(5.1)", "(5.2)"),
        prompt=(
            "Sıralı veri: 3, 5, 6, 8, 9, 11, 14 (n = 7). Değişim aralığı **(1)**, IQR **(2)** olur (çeyrekler "
            "L_p = (p/100)(n + 1) kuralıyla)."
        ),
        answer=FillBlanks((NumberBlank(11, 0.005, "11"), NumberBlank(6, 0.005, "6"))),
        explanation=(
            "R = 14 − 3 = 11. L₂₅ = 0,25 × 8 = 2 ve L₇₅ = 6 tam sayıdır: Q₁ = 5 (2. değer), Q₃ = 11 (6. değer); "
            "IQR = 11 − 5 = 6 (§5.2)."
        ),
    ),
    Question(
        key="b02", concept="kareli-sapmalardan-s", note=_note("5.4", "(5.3)", "(5.5)"),
        prompt=(
            "Beş gözlemli bir örneklemde kareli sapmalar toplamı 64'tür. Örneklem varyansı **(1)**, standart "
            "sapma **(2)** olur."
        ),
        answer=FillBlanks((NumberBlank(16, 0.005, "16"), NumberBlank(4, 0.005, "4"))),
        explanation=(
            "s² = 64/(5 − 1) = 16 ve s = √16 = 4. Payda n değil n − 1'dir; standart sapma varyansın pozitif "
            "kareköküdür ve özgün birimdedir (§5.3, §5.4)."
        ),
    ),
    Question(
        key="b03", concept="z-den-ham-degere", note=_note("5.7", "(5.7)"),
        prompt=(
            "Ortalaması 50, standart sapması 6 olan bir sınavda z = −1,5 olan öğrencinin notu **(1)**, z = 2 olan "
            "öğrencinin notu **(2)** olur."
        ),
        answer=FillBlanks((NumberBlank(41, 0.005, "41"), NumberBlank(62, 0.005, "62"))),
        explanation=(
            "z = (x − x̄)/s eşitliğinden x = x̄ + z s: 50 − 1,5 × 6 = 41 ve 50 + 2 × 6 = 62. Negatif z ortalamanın "
            "altında kalan bir gözlemi gösterir (§5.7)."
        ),
    ),
    Question(
        key="b04", concept="sinirlardan-iqr-ve-q1", note=_note("5.9", "(5.9)", "(5.10)"),
        prompt=(
            "Bir veri setinde IQR yöntemiyle alt sınır 10, üst sınır 50 bulunmuştur. IQR **(1)**, Q₁ **(2)** "
            "olur."
        ),
        answer=FillBlanks((NumberBlank(10, 0.005, "10"), NumberBlank(25, 0.005, "25"))),
        explanation=(
            "Üst sınır − alt sınır = (Q₃ + 1,5 IQR) − (Q₁ − 1,5 IQR) = IQR + 3 IQR = 4 IQR = 40, yani IQR = 10. "
            "Q₁ = alt sınır + 1,5 × 10 = 25 (ve Q₃ = 35) (§5.9)."
        ),
    ),
    Question(
        key="b05", concept="kucuk-veride-kovaryans", note=_note("5.11", "(5.11)"),
        prompt=(
            "x: 1, 2, 3 ve y: 2, 4, 9 için x̄ = 2, ȳ = 5'tir. Sapma çarpımlarının toplamı "
            "Σ(xᵢ − x̄)(yᵢ − ȳ) = **(1)**, örneklem kovaryansı **(2)** olur."
        ),
        answer=FillBlanks((NumberBlank(7, 0.005, "7"), NumberBlank(3.5, 0.005, "3,5"))),
        explanation=(
            "Sapmalar x için −1, 0, 1; y için −3, −1, 4. Çarpımlar 3, 0, 4; toplam 7. s_xy = 7/(3 − 1) = 3,5. "
            "Pozitif değer iki değişkenin aynı yönde hareket ettiğini gösterir (§5.11, (5.11))."
        ),
    ),
    # --- Denklem yazma -----------------------------------------------------------
    Question(
        key="e01", concept="cv-formulu", note=_note("5.5", "(5.6)"),
        prompt="Ortalaması $m$, standart sapması $s$ olan bir değişkenin değişim katsayısını yüzde olarak yazın.",
        answer=Equation(
            lhs="CV",
            symbols=(Symbol("s", "s", "standart sapma", 1, 10), Symbol("m", "m", "ortalama", 20, 100)),
            answer="100*s/m",
            shown="100\\,s/m",
        ),
        explanation=(
            "CV = (s/x̄) × 100: standart sapma ortalamaya göre ölçeklenir. m = 80, s = 8 için %10; m = 10, s = 2 "
            "için %20 (§5.5, (5.6))."
        ),
    ),
    Question(
        key="e02", concept="chebyshev-alt-siniri", note=_note("5.8", "(5.8)"),
        prompt=(
            "Chebyshev eşitsizliğine göre ortalamanın $k$ standart sapma çevresinde bulunan gözlemlerin en az "
            "oranını yazın."
        ),
        answer=Equation(
            lhs="\\text{en az oran}",
            symbols=(Symbol("k", "k", "standart sapma sayısı", 1.5, 5),),
            answer="1 - 1/k^2",
            shown="1 - 1/k^2",
        ),
        explanation=(
            "Alt sınır 1 − 1/k²'dir ve dağılımın biçiminden bağımsızdır: k = 2 için 0,75, k = 3 için yaklaşık "
            "0,889 (§5.8, (5.8))."
        ),
    ),
    Question(
        key="e03", concept="ust-aykiri-deger-siniri", note=_note("5.9", "(5.10)"),
        prompt="Birinci çeyrek $a$, üçüncü çeyrek $b$ ise üst aykırı değer sınırını yazın.",
        answer=Equation(
            lhs="\\text{üst sınır}",
            symbols=(Symbol("a", "a", "birinci çeyrek", 10, 40), Symbol("b", "b", "üçüncü çeyrek", 41, 80)),
            answer="b + 1.5*(b - a)",
            shown="b + 1{,}5\\,(b - a)",
        ),
        explanation=(
            "IQR = b − a ve üst sınır Q₃ + 1,5·IQR. Gelir verisinde 29 + 1,5 × (29 − 23) = 38; 65 bu sınırın "
            "üzerindedir (§5.9)."
        ),
    ),
    Question(
        key="e04", concept="korelasyon-formulu", note=_note("5.12", "(5.12)"),
        prompt="İki değişkenin kovaryansı $c$, standart sapmaları $p$ ve $q$ ise korelasyon katsayısını yazın.",
        answer=Equation(
            lhs="r_{xy}",
            symbols=(
                Symbol("c", "c", "kovaryans", -5, 5),
                Symbol("p", "p", "birinci değişkenin standart sapması", 1, 4),
                Symbol("q", "q", "ikinci değişkenin standart sapması", 1, 4),
            ),
            answer="c/(p*q)",
            shown="c/(p\\,q)",
        ),
        explanation=(
            "r = s_xy/(s_x s_y): kovaryans iki standart sapmaya bölünerek ölçekten bağımsız hâle gelir. Reklam–satış "
            "örneğinde 6,75/(1,58 × 4,30) ≈ 0,99 (§5.12)."
        ),
    ),
    Question(
        key="e05", concept="iki-gozlemin-varyansi", note=_note("5.3", "(5.3)"),
        prompt="İki gözlem $a$ ve $b$ olan bir örneklemin örneklem varyansını $a$ ve $b$ cinsinden yazın.",
        answer=Equation(
            lhs="s^2",
            symbols=(Symbol("a", "a", "birinci gözlem", 0, 10), Symbol("b", "b", "ikinci gözlem", 11, 20)),
            answer="(a - b)^2/2",
            shown="(a - b)^2/2",
        ),
        explanation=(
            "x̄ = (a + b)/2; sapmalar ±(a − b)/2, kareleri toplamı (a − b)²/2. Payda n − 1 = 1 olduğu için "
            "s² = (a − b)²/2 (§5.3, (5.3))."
        ),
    ),
)


KONU05_QUIZ = QuestionSet(
    topic_key="konu05",
    title="Konu 5: Kendini sına",
    questions=QUESTIONS,
    intro=(
        "Bu set haftanın temel kavramlarını sınar. Her soru tek bir kavrama odaklanır ve notlardaki bir "
        "bölüme bağlıdır; yanlış cevaplarınız için tekrar edilecek bölümler en üstte listelenir. Notlardaki "
        "egzersiz ve mini quiz maddelerini tekrar etmez, yeni sayılarla onları tamamlar."
    ),
    sections=tuple(f"5.{number}" for number in range(1, 14)),
)
