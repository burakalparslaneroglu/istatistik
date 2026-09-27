"""Konu 10 "Kendini sına" soru seti.

Her soru tek bir kavramı sınar ve notlardaki bir bölüme bağlıdır. Sorular notların Egzersiz 10.1–10.14 ve Mini Quiz
10.1–10.14 maddelerini tekrar etmez (ör. beş değişkenin sınıflandırılması, 10–20 uç noktaları, U(10, 18), U(0, 0,25),
N(50, 25)–N(70, 25), N(100, 4)–N(100, 25)–N(100, 100), N(500, 50²), N(0, 1)–N(1, 1)–N(0, 4), N(500, 20²), bölge
satış puanları, N(200, 15²) aralıkları, dört sürekli hikâye, 525 ml ve P(X = 500)); yeni sayılarla ve yeni
bağlamlarla aynı becerileri sınar. Normal eğri altındaki alanların hesabı Konu 11'in konusudur; bu sette yalnız
68–95–99,7 kuralı ve simetri kullanılır.
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
        key="k01", concept="kesiklide-toplam-surekli-alan", note=_note("10.1", "Şekil 10.2"),
        prompt=(
            "Kesikli bir X için P(2 ≤ X ≤ 4) = f(2) + f(3) + f(4) olarak bulunur. Sürekli bir Y için "
            "P(2 ≤ Y ≤ 4) nasıl bulunur?"
        ),
        answer=MultipleChoice(
            (
                "2 ile 4 arasında yoğunluk eğrisinin altında kalan alanla",
                "f(2) + f(3) + f(4) toplamıyla",
                "f(4) − f(2) farkıyla",
                "Eğrinin x = 3 noktasındaki yüksekliğiyle",
            ),
            correct=0,
        ),
        explanation=(
            "Sürekli bir değişkende 2 ile 4 arasında sonsuz sayıda değer vardır ve tek tek değerlerin olasılığı "
            "sıfırdır; olasılık yoğunluk eğrisinin o aralıktaki alanıdır. Yükseklikleri toplamak kesikli olasılık "
            "fonksiyonunun mantığıdır (§10.1, Şekil 10.2)."
        ),
    ),
    Question(
        key="k02", concept="tek-duze-varyansi-ve-aralik-uzunlugu", note=_note("10.3", "(10.6)"),
        prompt="Bir sürecin süresi U(0, 10) yerine U(0, 20) ile modellenirse varyans nasıl değişir?",
        answer=MultipleChoice(
            (
                "Değişmez, çünkü iki dağılımın alt sınırı aynıdır",
                "İki katına çıkar",
                "Dört katına çıkar",
                "Yarıya iner, çünkü yoğunluk yarıya iner",
            ),
            correct=2,
        ),
        explanation=(
            "σ² = (b − a)²/12: U(0, 10) için 100/12 ≈ 8,33, U(0, 20) için 400/12 ≈ 33,33. Aralık uzunluğu iki "
            "katına çıkınca varyans dört, standart sapma iki katına çıkar; yoğunluk ise 0,1'den 0,05'e iner "
            "(§10.3.1, (10.6))."
        ),
    ),
    Question(
        key="k03", concept="kuyruklar-eksene-degmez", note=_note("10.5"),
        prompt="Aşağıdaki ifadelerden hangisi normal dağılım için yanlıştır?",
        answer=MultipleChoice(
            (
                "Eğrinin tepe noktası x = μ'dadır",
                "μ + σ'nın sağındaki alan, μ − σ'nın solundaki alana eşittir",
                "Eğri, x = μ − d ve x = μ + d noktalarında aynı yüksekliktedir",
                "Eğri μ ± 3σ noktalarında yatay eksene değer; bu aralığın dışında değer yoktur",
            ),
            correct=3,
        ),
        explanation=(
            "Normal eğrinin kuyrukları iki yönde sonsuza uzanır ve yatay eksene teorik olarak değmez; μ ± 3σ "
            "dışında kalan alan küçüktür (yaklaşık 0,003) ama sıfır değildir. Diğer üç ifade eğrinin μ'da tepe "
            "yapmasının ve μ çevresindeki simetrisinin sonucudur (§10.5.1)."
        ),
    ),
    Question(
        key="k04", concept="ortalamayi-kaydirmak", note=_note("10.6", "Şekil 10.7"),
        prompt=(
            "Bir dolum makinesinde dolum miktarı yaklaşık normal dağılıyor. Makinenin ayarı standart sapmayı "
            "değiştirmeden ortalamayı 5 ml artırıyor. Dolum miktarının yoğunluk eğrisi için hangisi doğrudur?"
        ),
        answer=MultipleChoice(
            (
                "Eğri 5 ml sağa kayar ve genişler",
                "Eğri biçimi değişmeden 5 ml sağa kayar",
                "Eğri yerinde kalır, yalnız daha yüksek olur",
                "Eğri 5 ml sağa kayar ve tepe noktası yükselir",
            ),
            correct=1,
        ),
        explanation=(
            "μ konum parametresidir: σ sabitken μ değişince eğrinin genişliği ve yüksekliği aynı kalır, yalnız yatay "
            "konumu değişir. Şekil 10.7'deki üç eğri de bu nedenle aynı biçimdedir (§10.6)."
        ),
    ),
    Question(
        key="k05", concept="sigma-iki-katina-tepe-yariya", note=_note("10.7", "Şekil 10.8"),
        prompt="Aynı ortalamaya sahip N(μ, 4) ve N(μ, 16) eğrileri karşılaştırılıyor. Hangisi doğrudur?",
        answer=MultipleChoice(
            (
                "İkinci eğrinin tepe yüksekliği birincinin dört katıdır",
                "İki eğrinin tepe yükseklikleri eşittir; yalnız genişlikleri farklıdır",
                "İkinci eğrinin tepe yüksekliği birincinin yarısıdır",
                "İkinci eğrinin altındaki toplam alan birincinin dört katıdır",
            ),
            correct=2,
        ),
        explanation=(
            "N(μ, σ²) gösteriminde ikinci parametre varyanstır: σ₁ = 2, σ₂ = 4. Tepe yüksekliği f(μ) = "
            "1/(σ√(2π)), (10.7), σ ile ters orantılıdır; σ iki katına çıkınca tepe yarıya iner. Toplam alan iki "
            "eğride de 1'dir; genişleyen eğri basıklaşır (§10.7, Şekil 10.8)."
        ),
    ),
    Question(
        key="k06", concept="varyans-degil-standart-sapmayla-bolmek", note=_note("10.10", "(10.8)"),
        prompt="X ~ N(50, 16) ise X'i standart normal ölçeğe taşıyan dönüşüm hangisidir?",
        answer=MultipleChoice(("(X − 50)/4", "(X − 50)/16", "(X − 16)/50", "(X − 4)/50"), correct=0),
        explanation=(
            "N(μ, σ²) gösteriminde 16 varyanstır; standart sapma σ = √16 = 4'tür ve z = (x − 50)/4, (10.8). "
            "Varyansla bölmek z'yi yanlış ölçekler: x = 58 için doğru z = 2, yanlış hesap 0,5 verir (§10.10)."
        ),
    ),
    Question(
        key="k07", concept="tek-duze-hikayesini-tanimak", note=_note("10.13", "Tablo 10.1"),
        prompt="Aşağıdaki durumlardan hangisi için tek-düze dağılım en uygun modeldir?",
        answer=MultipleChoice(
            (
                "Bir sınıftaki öğrencilerin boy uzunlukları; değerler ortalama çevresinde yoğunlaşıyor",
                "Bir çağrı merkezine bir saatte gelen çağrı sayısı",
                "Bir hastanedeki bekleme süreleri; dağılım sağa çarpık",
                "Bir metro hattında trenler tam 8 dakikada bir geçiyor; rastgele bir anda perona gelen yolcunun "
                "bekleme süresi",
            ),
            correct=3,
        ),
        explanation=(
            "Yolcu rastgele bir anda geldiği için 0 ile 8 dakika arasındaki eşit uzunluktaki bekleme aralıkları eşit "
            "olasılıklıdır: U(0, 8). Boy uzunlukları çan biçimlidir (normal), çağrı sayısı kesiklidir (Konu 9), sağa "
            "çarpık bekleme süresi ise bu iki modelin hiçbirine uymaz (§10.13, Tablo 10.1)."
        ),
    ),
    # --- Doğru–yanlış -------------------------------------------------------------
    Question(
        key="d01", concept="yuksek-yogunluk-goreli-olasilik", note=_note("10.1"),
        prompt=(
            "Bir yoğunluk eğrisinin yüksek olduğu bölgedeki kısa bir aralık, eğrinin alçak olduğu bölgedeki aynı "
            "uzunlukta bir aralıktan daha büyük olasılık taşır."
        ),
        answer=TrueFalse(True),
        explanation=(
            "Kısa bir aralıkta alan yaklaşık olarak yükseklik × genişliktir; genişlikler eşitken yüksekliği fazla "
            "olan aralığın alanı, yani olasılığı daha büyüktür. Yükseklik kendisi olasılık değildir; o çevredeki "
            "yoğunluğu gösterir (§10.1)."
        ),
    ),
    Question(
        key="d02", concept="olcum-yuvarlama-araligi", note=_note("10.2", "(10.1)"),
        prompt=(
            "Uygulamada \"45 saniye\" olarak kaydedilen bir bekleme süresi çoğu zaman 44,5 ile 45,5 saniye "
            "arasındaki bir aralığı temsil eder; bu aralığın olasılığı pozitif olabilir."
        ),
        answer=TrueFalse(True),
        explanation=(
            "Sürekli modelde tam olarak 45,000… tek noktasının olasılığı sıfırdır, (10.1). Kaydedilen değer ise bir "
            "yuvarlama aralığıdır; pozitif genişlikteki bu aralığın eğri altındaki alanı pozitif olabilir (§10.2)."
        ),
    ),
    Question(
        key="d03", concept="tek-duzede-tekil-deger-yanilgisi", note=_note("10.3", "(10.3)"),
        prompt="X ~ U(a, b) ise X'in aralıktaki her tekil değeri alma olasılığı eşittir ve 1/(b − a)'dır.",
        answer=TrueFalse(False),
        explanation=(
            "1/(b − a) olasılık değil, yoğunluğun yüksekliğidir. Sürekli dağılımda her tekil değerin olasılığı "
            "sıfırdır; doğru ifade \"eşit uzunluktaki alt aralıkların olasılıkları eşittir\" biçimindedir "
            "(§10.3, (10.3))."
        ),
    ),
    Question(
        key="d04", concept="ampirik-kural-ve-chebyshev", note=_note("10.8"),
        prompt=(
            "Ampirik kural ile Chebyshev eşitsizliği birbirinin yerine kullanılabilir: ikisi de μ ± 2σ aralığı için "
            "yaklaşık %95,4 verir."
        ),
        answer=TrueFalse(False),
        explanation=(
            "%95,4 yalnız yaklaşık normal (çan biçimli) dağılımlar için geçerlidir. Chebyshev eşitsizliği her "
            "dağılım için geçerlidir ama daha zayıf bir alt sınır verir: μ ± 2σ içinde en az 1 − 1/2² = 0,75, yani "
            "%75. İki kural mekanik olarak birbirinin yerine kullanılmaz (§10.8)."
        ),
    ),
    Question(
        key="d05", concept="ortak-standart-olcek", note=_note("10.9", "Şekil 10.10"),
        prompt=(
            "Farklı ortalama ve standart sapmalara sahip bütün normal dağılımlar, z-dönüşümüyle tek bir ortak "
            "dağılıma, N(0, 1)'e taşınabilir."
        ),
        answer=TrueFalse(True),
        explanation=(
            "Her (μ, σ) çifti farklı bir normal eğri üretir; z = (x − μ)/σ dönüşümü ise hepsini ortalaması 0, "
            "standart sapması 1 olan standart normal dağılıma taşır. Farklı birimlerdeki normal değişkenler böylece "
            "aynı standart sapma ölçeğinde ifade edilir (§10.9, §10.10)."
        ),
    ),
    Question(
        key="d06", concept="z-skoru-yuzde-degildir", note=_note("10.11"),
        prompt=(
            "Bir sınavda z = 1,5 olan öğrencinin puanı, sınav ortalamasından %1,5 yüksektir."
        ),
        answer=TrueFalse(False),
        explanation=(
            "z-skoru yüzde değil, standart sapma birimidir: z = 1,5, puanın ortalamadan 1,5 standart sapma yukarıda "
            "olduğunu söyler. N(70, 10²) modelinde z = 1,5 olan puan 85'tir ve ortalamadan yaklaşık %21,4 yüksektir. "
            "z'nin normal eğri altındaki olasılık karşılığı Konu 11'de hesaplanacaktır (§10.11)."
        ),
    ),
    Question(
        key="d07", concept="asimetrik-araligi-standartlastirmak", note=_note("10.12", "(10.10)"),
        prompt="X ~ N(80, 5²) için P(70 ≤ X ≤ 85) = P(−2 ≤ Z ≤ 1)'dir.",
        answer=TrueFalse(True),
        explanation=(
            "Uçlar ayrı ayrı standartlaştırılır: z₁ = (70 − 80)/5 = −2, z₂ = (85 − 80)/5 = 1. Standartlaştırma yalnız "
            "yatay eksenin birimini değiştirir; aynı gözlemler aynı alanı kaplar (§10.12, (10.10))."
        ),
    ),
    # --- Boşluk doldurma ----------------------------------------------------------
    Question(
        key="b01", concept="tek-duze-ortalama-ve-standart-sapma", note=_note("10.3", "(10.5)", "(10.6)"),
        prompt=(
            "Bir paketin teslim süresi 24 ile 48 saat arasında tek-düze dağılıyor: X ~ U(24, 48). Ortalama "
            "μ = **(1)** saat, standart sapma σ = **(2)** saat olur (iki ondalık basamak)."
        ),
        answer=FillBlanks((NumberBlank(36, 0.005, "36"), NumberBlank(48 ** 0.5, 0.005, "6,93"))),
        explanation=(
            "μ = (a + b)/2 = (24 + 48)/2 = 36; σ² = (b − a)²/12 = 24²/12 = 48 ve σ = √48 ≈ 6,93 saat "
            "(§10.3.1, (10.5), (10.6))."
        ),
    ),
    Question(
        key="b02", concept="yogunluk-yuksekligi-ve-alan", note=_note("10.4", "Şekil 10.5"),
        prompt="X ~ U(3, 3,4) olsun. Yoğunluğun yüksekliği f(x) = **(1)** ve P(3,1 ≤ X ≤ 3,3) = **(2)** olur.",
        answer=FillBlanks((NumberBlank(2.5, 0.0005, "2,5"), NumberBlank(0.5, 0.0005, "0,5"))),
        explanation=(
            "f(x) = 1/(3,4 − 3) = 1/0,4 = 2,5: yükseklik 1'den büyüktür ama toplam alan 0,4 × 2,5 = 1'dir. "
            "P(3,1 ≤ X ≤ 3,3) = 0,2 × 2,5 = 0,5; olasılık kuralları yükseklik için değil alan için geçerlidir "
            "(§10.4, Şekil 10.5)."
        ),
    ),
    Question(
        key="b03", concept="ampirik-kural-araligi", note=_note("10.8", "Şekil 10.9"),
        prompt=(
            "Bir makinenin ürettiği parçaların uzunluğu yaklaşık N(120, 15²) mm dağılıyor. Ampirik kurala göre "
            "parçaların yaklaşık %99,7'si **(1)** mm ile **(2)** mm arasındadır."
        ),
        answer=FillBlanks((NumberBlank(75, 0.005, "75"), NumberBlank(165, 0.005, "165"))),
        explanation=(
            "μ ± 3σ = 120 ± 3(15): alt sınır 75, üst sınır 165 mm. Aynı mantıkla parçaların yaklaşık %68,3'ü "
            "105–135, %95,4'ü 90–150 mm aralığındadır (§10.8, Şekil 10.9)."
        ),
    ),
    Question(
        key="b04", concept="standart-olcekten-ozgun-olcege", note=_note("10.10", "(10.9)"),
        prompt=(
            "Bir sınavın puanları N(62, 8²) ile modelleniyor. z = 1,5 olan puan **(1)**, z = −0,75 olan puan "
            "**(2)** olur."
        ),
        answer=FillBlanks((NumberBlank(74, 0.005, "74"), NumberBlank(56, 0.005, "56"))),
        explanation=(
            "x = μ + zσ, (10.9): 62 + 1,5(8) = 74 ve 62 + (−0,75)(8) = 56. Pozitif z ortalamanın üstünü, negatif z "
            "altını gösterir (§10.10.1)."
        ),
    ),
    Question(
        key="b05", concept="butunlestirici-dolum", note=_note("10.14", "Şekil 10.15"),
        prompt=(
            "Bir kahve makinesinin dolum miktarı N(180, 6²) ml ile modelleniyor. 189 ml'nin z-skoru **(1)** ve "
            "P(X > 180) = **(2)** olur."
        ),
        answer=FillBlanks((NumberBlank(1.5, 0.0005, "1,5"), NumberBlank(0.5, 0.0005, "0,5"))),
        explanation=(
            "z = (189 − 180)/6 = 1,5: dolum ortalamanın 1,5 standart sapma üzerindedir. Normal eğri μ = 180 "
            "çevresinde simetrik olduğundan P(X > 180) = 0,50; tek noktanın olasılığı sıfır olduğu için "
            "P(X ≥ 180) de aynıdır (§10.14, §10.2)."
        ),
    ),
    # --- Denklem yazma -----------------------------------------------------------
    Question(
        key="e01", concept="tek-duze-ust-olasilik", note=_note("10.3", "(10.4)"),
        prompt="X ~ U($a$, $b$) ve $a$ ≤ $c$ ≤ $b$ ise P(X > $c$)'yi yazın.",
        answer=Equation(
            lhs="P(X > c)",
            symbols=(
                Symbol("a", "a", "alt sınır", 0, 10),
                Symbol("b", "b", "üst sınır", 20, 40),
                Symbol("c", "c", "eşik", 10, 20),
            ),
            answer="(b - c)/(b - a)",
            shown="\\frac{b-c}{b-a}",
        ),
        explanation=(
            "X > c olayı c ile b arasındaki dikdörtgendir: genişlik b − c, yükseklik 1/(b − a), alan "
            "(b − c)/(b − a). Şekil 10.4'teki U(120, 140) için P(X > 136) = 4/20 = 0,20 (§10.3, (10.4))."
        ),
    ),
    Question(
        key="e02", concept="yukseklik-ve-genislik-ters-orantili", note=_note("10.4", "Şekil 10.5"),
        prompt="X ~ U(0, $k$) dağılımının yoğunluk yüksekliği $h$'dir. $k$'yi $h$ cinsinden yazın.",
        answer=Equation(
            lhs="k",
            symbols=(Symbol("h", "h", "yoğunluk yüksekliği", 0.1, 5),),
            answer="1/h",
            shown="1/h",
        ),
        explanation=(
            "Toplam alan 1 olmalıdır: k × h = 1 ⇒ k = 1/h. Yükseklik 2 ise aralık 0,5 uzunluğundadır (Şekil 10.5); "
            "yükseklik büyüdükçe aralık daralır (§10.4)."
        ),
    ),
    Question(
        key="e03", concept="ortalama-degisince-z", note=_note("10.10", "(10.8)"),
        prompt=(
            "Bir x değerinin z-skoru $z$'dir. Standart sapma σ = $s$ aynı kalıp ortalama $c$ birim artarsa aynı x "
            "değerinin yeni z-skorunu yazın."
        ),
        answer=Equation(
            lhs="z_{\\text{yeni}}",
            symbols=(
                Symbol("z", "z", "eski z-skoru", -2, 2),
                Symbol("c", "c", "ortalamadaki artış", 0.5, 10),
                Symbol("s", "s", "standart sapma σ", 1, 10),
            ),
            answer="z - c/s",
            shown="z - c/s",
        ),
        explanation=(
            "Yeni z = (x − (μ + c))/σ = (x − μ)/σ − c/σ = z − c/s. z = 1,5 olan 85 puan, ortalama 70'ten 75'e "
            "çıkınca (σ = 10) z = 1 olur (§10.10, (10.8))."
        ),
    ),
    Question(
        key="e04", concept="esdeger-puan", note=_note("10.11", "(10.9)"),
        prompt=(
            "Bir öğrenci A sınavında $a$ puan aldı; A'da ortalama $m_1$, standart sapma $s_1$'dir. B sınavında "
            "ortalama $m_2$, standart sapma $s_2$ ise B'de aynı göreli konumu (aynı z) veren puanı yazın."
        ),
        answer=Equation(
            lhs="x_B",
            symbols=(
                Symbol("a", "a", "A sınavındaki puan", 60, 95),
                Symbol("m1", "m_1", "A sınavının ortalaması", 50, 75),
                Symbol("s1", "s_1", "A sınavının standart sapması", 2, 10),
                Symbol("m2", "m_2", "B sınavının ortalaması", 60, 85),
                Symbol("s2", "s_2", "B sınavının standart sapması", 3, 12),
            ),
            answer="m2 + s2*(a - m1)/s1",
            shown="m_2 + s_2\\,\\frac{a-m_1}{s_1}",
        ),
        explanation=(
            "A'daki z = (a − m₁)/s₁; B'de aynı z'yi veren puan x = m₂ + z s₂ = m₂ + s₂(a − m₁)/s₁. Notlardaki A "
            "sınavındaki 78 puan (z = 2), B sınavında 80 + 2(8) = 96 puana denktir (§10.11, (10.9))."
        ),
    ),
    Question(
        key="e05", concept="araliktan-standart-sapma", note=_note("10.8"),
        prompt=(
            "Yaklaşık normal bir değişkenin değerlerinin yaklaşık %68,3'ü [$a$, $b$] aralığındadır (μ ± σ). σ'yı "
            "$a$ ve $b$ cinsinden yazın."
        ),
        answer=Equation(
            lhs="\\sigma",
            symbols=(Symbol("a", "a", "aralığın alt ucu", 10, 50), Symbol("b", "b", "aralığın üst ucu", 60, 100)),
            answer="(b - a)/2",
            shown="\\frac{b-a}{2}",
        ),
        explanation=(
            "μ ± σ aralığının uzunluğu 2σ'dır: b − a = 2σ ⇒ σ = (b − a)/2; merkez μ = (a + b)/2. Notlardaki sınav "
            "örneğinde [60, 80] aralığı σ = 10 ve μ = 70 verir (§10.8)."
        ),
    ),
)


KONU10_QUIZ = QuestionSet(
    topic_key="konu10",
    title="Konu 10: Kendini sına",
    questions=QUESTIONS,
    intro=(
        "Bu set haftanın temel kavramlarını sınar. Her soru tek bir kavrama odaklanır ve notlardaki bir "
        "bölüme bağlıdır; yanlış cevaplarınız için tekrar edilecek bölümler en üstte listelenir. Notlardaki "
        "egzersiz ve mini quiz maddelerini tekrar etmez, yeni sayılarla onları tamamlar."
    ),
    sections=tuple(f"10.{number}" for number in range(1, 15)),
)
