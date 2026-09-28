"""Konu 11 "Kendini sına" soru seti.

Her soru tek bir kavramı sınar ve notlardaki bir bölüme bağlıdır. Sorular notların Egzersiz 11.1–11.13 ve Mini Quiz
11.1–11.13 maddelerini tekrar etmez (ör. Φ(0,50), Φ(1,02), Φ(1,25), Φ(1,53) okumaları; Φ(0,80), Φ(1,40), Φ(1,90);
P(Z > 0,60) ve P(−0,40 ≤ Z ≤ 1,10); N(100, 15²); N(500, 20²) yüzdelikleri; dört alan türü ifadesi; dört binom
koşulu; P(X = 8), P(X ≤ 12), P(X ≥ 15), P(8 ≤ X ≤ 12), P(X > 20); Bin(100, 0,40) ile 35–45; μ = 10 dakikalık üstel
süre; saatte 6 çağrı; altı hikâye; §11.13'teki işletmenin beş sorusu); yeni sayılarla ve yeni bağlamlarla aynı
becerileri sınar. Φ değerleri notlardaki tablodandır: z iki, Φ(z) dört ondalık basamak.
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
        key="k01", concept="tablonun-verdigi-alan", note=_note("11.1", "Tablo 11.1"),
        prompt=(
            "Başka bir kitaptaki normal tabloda z = 1,00 satırında 0,3413 yazıyor. Bu tablo hangi alanı veriyor?"
        ),
        answer=MultipleChoice(
            (
                "0 ile z arasındaki alanı: P(0 ≤ Z ≤ z)",
                "Sol kümülatif alanı: Φ(z) = P(Z ≤ z)",
                "Sağ kuyruk alanını: P(Z > z)",
                "Eğrinin z noktasındaki yüksekliğini",
            ),
            correct=0,
        ),
        explanation=(
            "Notlardaki tablo sol kümülatif alanı verir: Φ(1,00) = 0,8413. 0,8413 − 0,5 = 0,3413 olduğundan bu tablo "
            "0 ile z arasındaki alanı veriyor. Sağ kuyruk 0,1587 olurdu. Bir tabloyu kullanmadan önce başlığının hangi "
            "alanı verdiği kontrol edilir (§11.1)."
        ),
    ),
    Question(
        key="k02", concept="ortalama-cevresinde-simetrik-aralik", note=_note("11.3", "(11.5)"),
        prompt="Tablo 11.1'e göre Φ(1,25) = 0,8944'tür. P(−1,25 ≤ Z ≤ 1,25) kaçtır?",
        answer=MultipleChoice(("0,8944", "0,1056", "0,7888", "0,3944"), correct=2),
        explanation=(
            "İki sol alanın farkı alınır, (11.5): Φ(1,25) − Φ(−1,25) = 0,8944 − (1 − 0,8944) = 0,8944 − 0,1056 = "
            "0,7888. 0,3944 yalnız 0 ile 1,25 arasındaki alandır; simetri nedeniyle aralığın alanı bunun iki katıdır "
            "(§11.3; yuvarlamasız değer 0,7887)."
        ),
    ),
    Question(
        key="k03", concept="esik-degerinden-yuzdelige", note=_note("11.5", "Tablo 11.2"),
        prompt="Sınav puanları N(70, 10²) dağılımına uyuyor. 63,26 puan hangi yüzdeliğe karşılık gelir?",
        answer=MultipleChoice(
            (
                "75. yüzdelik (üst çeyreğin sınırı)",
                "25. yüzdelik (alt çeyreğin sınırı)",
                "10. yüzdelik",
                "50. yüzdelik (medyan)",
            ),
            correct=1,
        ),
        explanation=(
            "z = (63,26 − 70)/10 = −0,674. Tablo 11.2'de P(Z ≤ −0,674) = 0,25: puanların %25'i bu değerin altındadır. "
            "Ters normal sorusu olasılık → z → x yönünde çözülür; burada yön tersine izlenir (§11.5)."
        ),
    ),
    Question(
        key="k04", concept="olumsuz-ifadeden-sag-alana", note=_note("11.6", "Şekil 11.6"),
        prompt=(
            "Bir ürünün ömrü normal dağılıyor ve z = (900 − μ)/σ. \"Ömrün 900 saatin altında kalmaması\" olasılığı "
            "hangi işlemle bulunur?"
        ),
        answer=MultipleChoice(("Φ(z)", "Φ(z) − 0,5", "Φ(z₂) − Φ(z₁)", "1 − Φ(z)"), correct=3),
        explanation=(
            "\"Altında kalmaması\", 900 veya daha fazla saat dayanması demektir: P(X ≥ 900), yani sağ alan 1 − Φ(z). "
            "Soru metnindeki olumsuzluk alan türünü tersine çevirir; önce istenen alan belirlenir (§11.6, "
            "Şekil 11.6)."
        ),
    ),
    Question(
        key="k05", concept="kosulu-saglayan-binom", note=_note("11.7", "(11.6)"),
        prompt="Aşağıdaki binom modellerinden hangisi normal yaklaşım koşulunu sağlar?",
        answer=MultipleChoice(
            ("n = 60, p = 0,05", "n = 30, p = 0,20", "n = 200, p = 0,98", "n = 12, p = 0,40"),
            correct=1,
        ),
        explanation=(
            "(11.6): np ≥ 5 ve n(1 − p) ≥ 5. n = 30, p = 0,20 için np = 6 ve n(1 − p) = 24. Diğerlerinde np = 3; "
            "n(1 − p) = 200 × 0,02 = 4; np = 4,8: en az biri 5'in altındadır. Büyük n tek başına yetmez (§11.7)."
        ),
    ),
    Question(
        key="k06", concept="kucuktur-olayinin-duzeltmesi", note=_note("11.8", "Tablo 11.3"),
        prompt=(
            "X ~ Bin(n, p) için P(X < 15) normal yaklaşımla hesaplanacak. Yaklaşım değişkeni Y ~ N(np, np(1 − p)) "
            "olmak üzere hangi olasılık kullanılır?"
        ),
        answer=MultipleChoice(("P(Y < 14,5)", "P(Y < 15,5)", "P(Y < 15)", "P(Y > 14,5)"), correct=0),
        explanation=(
            "X < 15 olayı 0, 1, …, 14 çubuklarıdır; son çubuğun dış kenarı 14,5'tir. Tablo 11.3: P(X < x) → "
            "P(Y < x − 0,5). 15,5 sınırı 15 çubuğunu da katardı (§11.8)."
        ),
    ),
    Question(
        key="k07", concept="sabit-denemede-sayim-binomdur", note=_note("11.12", "Tablo 11.4"),
        prompt=(
            "Bir çağrı merkezinde gün içinde gelen 100 bağımsız çağrının her biri 0,05 olasılıkla şikâyet içeriyor. "
            "Şikâyetli çağrı sayısı için en uygun model hangisidir?"
        ),
        answer=MultipleChoice(
            (
                "Poisson, çünkü bir olay sayısı sayılıyor",
                "Üstel, çünkü çağrılar zaman içinde gelir",
                "Binom, çünkü sabit sayıda bağımsız deneme ve sabit başarı olasılığı var",
                "Hipergeometrik, çünkü çağrı sayısı sonludur",
            ),
            correct=2,
        ),
        explanation=(
            "\"Kaç tane?\" sorusu tek başına yetmez; deney yapısına bakılır. n = 100 sabit, her çağrıda iki sonuç ve "
            "sabit p = 0,05 var: Bin(100, 0,05). Poisson sabit aralıktaki olay sayısı, üstel bir süre, "
            "hipergeometrik yerine koymadan seçimdir (§11.12, Tablo 11.4)."
        ),
    ),
    # --- Doğru–yanlış -------------------------------------------------------------
    Question(
        key="d01", concept="simetride-eksi-olasilik-yanilgisi", note=_note("11.2", "(11.3)"),
        prompt="Simetri nedeniyle Φ(−1,23) = −Φ(1,23) = −0,8907'dir.",
        answer=TrueFalse(False),
        explanation=(
            "Olasılık negatif olamaz. Simetri alanlar arasındadır: Φ(−z) = 1 − Φ(z), (11.3). Tablo 11.1'den "
            "Φ(1,23) = 0,8907, dolayısıyla Φ(−1,23) = 1 − 0,8907 = 0,1093: negatif bir z için sol alan 0,5'ten "
            "küçüktür (§11.2)."
        ),
    ),
    Question(
        key="d02", concept="ozgun-olcekte-sag-kuyruk", note=_note("11.4", "Şekil 11.4"),
        prompt="X ~ N(70, 10²) için P(X ≥ 82) = P(Z ≥ 1,2) = 1 − 0,8849 = 0,1151'dir.",
        answer=TrueFalse(True),
        explanation=(
            "z = (82 − 70)/10 = 1,2; sağ kuyruk tümleyenle bulunur, (11.4): 1 − Φ(1,20) = 1 − 0,8849 = 0,1151. Sürekli "
            "dağılımda ≥ ile > aynı olasılığı verir (§11.4, Şekil 11.4)."
        ),
    ),
    Question(
        key="d03", concept="tumleyen-olayda-duzeltme", note=_note("11.8", "Tablo 11.3"),
        prompt="Binom modelinde P(X ≠ 12) için normal yaklaşım 1 − P(11,5 < Y < 12,5) olarak yazılabilir.",
        answer=TrueFalse(True),
        explanation=(
            "X ≠ 12, X = 12 olayının tümleyenidir. 12 çubuğu normal ölçekte 11,5 ile 12,5 arasıdır (Tablo 11.3); "
            "geri kalan bütün çubuklar bu aralığın dışındaki alandır. §11.8.1'deki faturalar için 1 − 0,1052 = 0,8948 "
            "(§11.8)."
        ),
    ),
    Question(
        key="d04", concept="duzeltme-x-olceginde-yapilir", note=_note("11.9", "Şekil 11.9"),
        prompt=(
            "Normal yaklaştırmada süreklilik düzeltmesi, sınırlar z'ye dönüştürüldükten sonra z değerlerine ±0,5 "
            "eklenerek yapılır."
        ),
        answer=TrueFalse(False),
        explanation=(
            "Düzeltme binom sayılarının ölçeğinde yapılır: önce sınır 0,5 genişletilir (Şekil 11.9, adım 4), sonra "
            "z'ye dönüştürülür (adım 5). z ölçeğinde 0,5 eklemek x ölçeğinde 0,5σ kaydırmak demektir ve yanlış alan "
            "verir (§11.9)."
        ),
    ),
    Question(
        key="d05", concept="ustel-sag-kuyruk-formulu", note=_note("11.10", "(11.8)", "(11.9)"),
        prompt="Üstel dağılımda sağ kuyruk olasılığı P(X > x₀), 1 − e^(−x₀/μ) formülüyle bulunur.",
        answer=TrueFalse(False),
        explanation=(
            "1 − e^(−x₀/μ) sol alandır, P(X ≤ x₀), (11.8). Sağ kuyruk (11.9): P(X > x₀) = e^(−x₀/μ). μ = 15 için "
            "P(X > 18) = e^(−1,2) ≈ 0,3012 ve P(X ≤ 18) ≈ 0,6988; ikisinin toplamı 1'dir (§11.10)."
        ),
    ),
    Question(
        key="d06", concept="aralik-kisalinca-bekleme-degismez", note=_note("11.11", "(11.11)"),
        prompt=(
            "Bir olay sürecinde incelenen aralık 60 dakikadan 30 dakikaya indirilirse hem aralıktaki ortalama olay "
            "sayısı hem de ardışık olaylar arasındaki ortalama süre yarıya iner."
        ),
        answer=TrueFalse(False),
        explanation=(
            "Aralıktaki ortalama olay sayısı aralığın uzunluğuyla orantılıdır ve yarıya iner. Olaylar arasındaki "
            "ortalama süre ise sürecin hızına bağlıdır, aralığa değil: saatte 12 olay için 30 dakikada ortalama 6 "
            "olay, bekleme yine 60/12 = 5 dakika (§11.11, (11.11))."
        ),
    ),
    Question(
        key="d07", concept="hic-gelis-yok-ile-uzun-bekleme", note=_note("11.13"),
        prompt=(
            "§11.13'teki işletmede (saatte ortalama 8 müşteri) önümüzdeki bir saatte hiç müşteri gelmemesi olasılığı, "
            "bir sonraki müşteriye kadar 60 dakikadan fazla beklenmesi olasılığına eşittir."
        ),
        answer=TrueFalse(True),
        explanation=(
            "İkisi aynı olayın iki bakışıdır: gelecek 60 dakikada geliş yoksa ilk geliş 60 dakikadan sonradır. Poisson "
            "ile P(N = 0) = e⁻⁸; üstel ile P(T > 60) = e^(−60/7,5) = e⁻⁸ ≈ 0,0003 (§11.13, §11.11)."
        ),
    ),
    # --- Boşluk doldurma ----------------------------------------------------------
    Question(
        key="b01", concept="tablo-hucresi-okuma", note=_note("11.1", "Tablo 11.1"),
        prompt="Tablo 11.1'i kullanın: Φ(1,04) = **(1)** ve Φ(0,53) = **(2)** olur.",
        answer=FillBlanks((NumberBlank(0.8508, 0.00005, "0,8508"), NumberBlank(0.7019, 0.00005, "0,7019"))),
        explanation=(
            "z'nin tam kısmı ile ilk ondalığı satırı, ikinci ondalığı sütunu verir: 1,04 için satır 1,0 ve sütun "
            "0,04 → 0,8508; 0,53 için satır 0,5 ve sütun 0,03 → 0,7019 (§11.1, Tablo 11.1)."
        ),
    ),
    Question(
        key="b02", concept="sag-kuyruk-ve-iki-deger-arasi", note=_note("11.3", "(11.4)", "(11.5)"),
        prompt="Tablo 11.1'e göre P(Z > 1,50) = **(1)** ve P(0,50 ≤ Z ≤ 1,50) = **(2)** olur.",
        answer=FillBlanks((NumberBlank(0.0668, 0.00005, "0,0668"), NumberBlank(0.2417, 0.00005, "0,2417"))),
        explanation=(
            "Sağ kuyruk, (11.4): 1 − Φ(1,50) = 1 − 0,9332 = 0,0668. İki değer arası, (11.5): Φ(1,50) − Φ(0,50) = "
            "0,9332 − 0,6915 = 0,2417 (§11.3)."
        ),
    ),
    Question(
        key="b03", concept="ozgun-olcekte-sol-alan", note=_note("11.4", "Şekil 11.4"),
        prompt=(
            "Paketlerin ağırlığı X ~ N(250, 20²) gram. 271 gramın z-skoru **(1)** ve P(X ≤ 271) = **(2)** olur "
            "(Tablo 11.1)."
        ),
        answer=FillBlanks((NumberBlank(1.05, 0.005, "1,05"), NumberBlank(0.8531, 0.00005, "0,8531"))),
        explanation=(
            "z = (271 − 250)/20 = 1,05; sol alan doğrudan tablodan (satır 1,0, sütun 0,05): Φ(1,05) = 0,8531. z yalnız "
            "bir ara adımdır; soru olasılık istediği için alan hesabıyla biter (§11.4, Şekil 11.4)."
        ),
    ),
    Question(
        key="b04", concept="yaklasimin-parametreleri", note=_note("11.7"),
        prompt=(
            "X ~ Bin(150, 0,20) için normal yaklaşımın ortalaması μ = **(1)**, standart sapması σ = **(2)** olur "
            "(iki ondalık basamak)."
        ),
        answer=FillBlanks((NumberBlank(30, 0.005, "30"), NumberBlank(24 ** 0.5, 0.005, "4,90"))),
        explanation=(
            "μ = np = 150 × 0,20 = 30; σ = √(np(1 − p)) = √(150 × 0,20 × 0,80) = √24 ≈ 4,90. Koşul da sağlanır: "
            "np = 30 ve n(1 − p) = 120 (§11.7)."
        ),
    ),
    Question(
        key="b05", concept="ustel-sol-alan-ve-sag-kuyruk", note=_note("11.10", "(11.8)", "(11.9)"),
        prompt=(
            "Bir baskı işinin süresi, ortalaması μ = 12 dakika olan üstel dağılıma sahip. P(X ≤ 3) = **(1)** ve "
            "P(X > 24) = **(2)** olur (dört ondalık basamak)."
        ),
        answer=FillBlanks((NumberBlank(0.2212, 0.00005, "0,2212"), NumberBlank(0.1353, 0.00005, "0,1353"))),
        explanation=(
            "(11.8): P(X ≤ 3) = 1 − e^(−3/12) = 1 − e^(−0,25) ≈ 0,2212. (11.9): P(X > 24) = e^(−24/12) = e⁻² ≈ "
            "0,1353: ortalamanın iki katından uzun sürme olasılığı μ ne olursa olsun aynıdır (§11.10)."
        ),
    ),
    # --- Denklem yazma -----------------------------------------------------------
    Question(
        key="e01", concept="iki-kuyruk-toplami", note=_note("11.2", "(11.3)", "(11.4)"),
        prompt=(
            "z > 0 için P(|Z| > z), yani iki kuyruğun toplam alanını tablodaki Φ(z) değeri cinsinden yazın "
            "(Φ(z) için F kullanın)."
        ),
        answer=Equation(
            lhs="P(|Z| > z)",
            symbols=(Symbol("F", "\\Phi(z)", "tablodaki Φ(z) değeri", 0.5, 0.999),),
            answer="2*(1-F)",
            shown="2\\,[1-\\Phi(z)]",
        ),
        explanation=(
            "Sağ kuyruk 1 − Φ(z), (11.4); simetriden sol kuyruk P(Z < −z) = Φ(−z) = 1 − Φ(z), (11.3). Toplam "
            "2[1 − Φ(z)]. Tablo 11.2'deki 1,645 için 2(1 − 0,95) = 0,10 (§11.2, §11.3)."
        ),
    ),
    Question(
        key="e02", concept="ortadaki-yuzde-80-genisligi", note=_note("11.5", "Tablo 11.2"),
        prompt=(
            "X ~ N(μ, σ²) dağılımında ortadaki %80'lik bölgeyi, yani 10. ve 90. yüzdelikler arasını kapsayan aralığın "
            "genişliğini σ cinsinden yazın (Tablo 11.2'deki z değeriyle, 1,282 kullanın)."
        ),
        answer=Equation(
            lhs="\\text{genişlik}",
            symbols=(Symbol("s", "\\sigma", "standart sapma σ", 1, 30, aliases=("σ",)),),
            answer="2*1.282*s",
            shown="2(1{,}282)\\sigma = 2{,}564\\,\\sigma",
        ),
        explanation=(
            "Tablo 11.2: 10. yüzdelikte z = −1,282, 90. yüzdelikte z = 1,282. x = μ + zσ ile uçlar μ − 1,282σ ve "
            "μ + 1,282σ; genişlik 2,564σ. N(70, 10²) için aralık 57,18–82,82 (§11.5)."
        ),
    ),
    Question(
        key="e03", concept="buyuk-esit-olayinda-z", note=_note("11.9", "Şekil 11.9"),
        prompt=(
            "X ~ Bin(n, p) için P(X ≥ k) normal yaklaşımla hesaplanacak. Süreklilik düzeltmeli sınırın z değerini "
            "n, p ve k cinsinden yazın; karekök için sqrt() kullanın, çarpımları n*p biçiminde yazın."
        ),
        answer=Equation(
            lhs="z",
            symbols=(
                Symbol("n", "n", "deneme sayısı", 20, 200),
                Symbol("p", "p", "başarı olasılığı", 0.1, 0.9),
                Symbol("k", "k", "alt sınır (tam sayı)", 1, 50),
            ),
            answer="(k - 0.5 - n*p)/sqrt(n*p*(1-p))",
            shown="\\frac{k-0{,}5-np}{\\sqrt{np(1-p)}}",
        ),
        explanation=(
            "Şekil 11.9: μ = np, σ = √(np(1 − p)); P(X ≥ k) → P(Y ≥ k − 0,5) (Tablo 11.3); sonra z = (k − 0,5 − np)/σ "
            "ve olasılık ≈ 1 − Φ(z). n = 100, p = 0,10, k = 16 için z = (15,5 − 10)/3 ≈ 1,83 ve 1 − 0,9664 = 0,0336 "
            "(§11.9)."
        ),
    ),
    Question(
        key="e04", concept="ustel-medyan", note=_note("11.10", "(11.8)"),
        prompt=(
            "Ortalama süresi μ olan üstel dağılımın medyanını, yani P(X ≤ medyan) = 0,5 olan değeri yazın. Doğal "
            "logaritma için log() ya da ln() yazın."
        ),
        answer=Equation(
            lhs="\\text{medyan}",
            symbols=(Symbol("m", "\\mu", "ortalama süre μ", 1, 30, aliases=("μ",)),),
            answer="m*log(2)",
            shown="\\mu\\ln 2",
        ),
        explanation=(
            "(11.8): 1 − e^(−x/μ) = 0,5 ⇒ e^(−x/μ) = 0,5 ⇒ x = μ ln 2 ≈ 0,693μ. Medyan ortalamadan küçüktür; μ = 15 "
            "dakikalık yükleme süresinde işlerin yarısı yaklaşık 10,4 dakikadan kısa sürer (§11.10)."
        ),
    ),
    Question(
        key="e05", concept="saatlik-hizdan-bekleme-olasiligi", note=_note("11.11", "(11.9)", "(11.11)"),
        prompt=(
            "Bir süreçte saatte ortalama λ olay gerçekleşiyor. Bir sonraki olaya kadar t dakikadan uzun bekleme "
            "olasılığını yazın; e üzeri u için exp(u) yazın."
        ),
        answer=Equation(
            lhs="P(T > t)",
            symbols=(
                Symbol("L", "\\lambda", "saatteki ortalama olay sayısı λ", 1, 30, aliases=("λ",)),
                Symbol("t", "t", "bekleme eşiği (dakika)", 1, 60),
            ),
            answer="exp(-L*t/60)",
            shown="e^{-\\lambda t/60}",
        ),
        explanation=(
            "Ortalama bekleme süresi 1/λ saat, yani μ = 60/λ dakikadır (11.11). Üstel sağ kuyruk, (11.9): "
            "P(T > t) = e^(−t/μ) = e^(−λt/60). λ = 12, t = 10 için e⁻² ≈ 0,1353 (§11.11)."
        ),
    ),
)


KONU11_QUIZ = QuestionSet(
    topic_key="konu11",
    title="Konu 11: Kendini sına",
    questions=QUESTIONS,
    intro=(
        "Bu set haftanın temel kavramlarını sınar. Her soru tek bir kavrama odaklanır ve notlardaki bir "
        "bölüme bağlıdır; yanlış cevaplarınız için tekrar edilecek bölümler en üstte listelenir. Notlardaki "
        "egzersiz ve mini quiz maddelerini tekrar etmez, yeni sayılarla onları tamamlar."
    ),
    sections=tuple(f"11.{number}" for number in range(1, 14)),
)
