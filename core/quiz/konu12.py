"""Konu 12 "Kendini sına" soru seti.

Her soru tek bir kavramı sınar ve notlardaki bir bölüme bağlıdır. Sorular notların Egzersiz 12.1–12.15 ve Mini Quiz
12.1–12.15 maddelerini tekrar etmez (ör. 120.000 hane ve 600 hane; 8.000 öğrenci ve kütüphane; yüzde 5 kuralının dört
durumu; dört parametre–istatistik sınıflaması; veri ve örnekleme dağılımı örnekleri; μ = 80, σ = 12; σ = 24 ile
n = 16, 64, 144; MLT'nin dört ifadesi; μ = 100, σ = 20, n = 25; p = 0,40, n = 100; N = 500, n = 100, σ = 15; A, B, C
tahmin edicileri; beş örnekleme hikâyesi; dört hata durumu; §12.15'teki işletmenin beş sorusu); yeni sayılarla ve
yeni bağlamlarla aynı becerileri sınar. Güven aralığı ve hipotez testi ikinci dönemin konusudur; bu sette yoktur.
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


SIGMA = Symbol("s", "\\sigma", "anakütle standart sapması σ", 5, 100, aliases=("σ",))

QUESTIONS = (
    # --- Çoktan seçmeli -----------------------------------------------------------
    Question(
        key="k01", concept="olcum-birimi-tuketiyorsa", note=_note("12.1"),
        prompt="Aşağıdaki durumlardan hangisinde anakütlenin tamamını gözlemek mantıklı değildir?",
        answer=MultipleChoice(
            (
                "Ampullerin ömrünü ölçmek için her ampulün yanıp bitmesi gerekiyorsa",
                "Anakütle 25 kişilik bir sınıfsa ve listesi hazırsa",
                "Ölçüm ucuz, hızlı ve birimlere zarar vermiyorsa",
                "Araştırma sorusu anakütle ortalamasıyla ilgiliyse",
            ),
            correct=0,
        ),
        explanation=(
            "Ölçüm birimi tüketiyorsa tam sayım bütün ürünü yok eder; ölçüm sürecinin niteliği örneklemeyi zorunlu "
            "kılar. Maliyet ve zaman da örnekleme gerekçesidir; küçük, listesi hazır bir anakütlede ise tam sayım "
            "mümkündür (§12.1)."
        ),
    ),
    Question(
        key="k02", concept="belirli-orneklemin-secilme-olasiligi", note=_note("12.2"),
        prompt=(
            "N = 5 birimlik {A, B, C, D, E} anakütlesinden n = 2 birimlik basit rassal örneklem seçiliyor. {A, C} "
            "örnekleminin seçilme olasılığı kaçtır?"
        ),
        answer=MultipleChoice(("1/5", "2/5", "1/10", "1/25"), correct=2),
        explanation=(
            "Basit rassal örneklemde olası her n birimli örneklemin seçilme olasılığı eşittir. 5 birimden "
            "$\\binom{5}{2} = 10$ farklı 2'li örneklem kurulur; her birinin olasılığı 1/10. 2/5, A'nın örneklemde yer "
            "alma olasılığıdır, belirli bir çiftin değil (§12.2)."
        ),
    ),
    Question(
        key="k03", concept="sigma-icin-istatistik", note=_note("12.4", "Tablo 12.1"),
        prompt="Anakütle standart sapması σ bilinmiyor. σ'nın nokta tahmini için örneklemden hangisi hesaplanır?",
        answer=MultipleChoice(("s²", "s", "x̄", "σ/√n"), correct=1),
        explanation=(
            "Tablo 12.1'de her parametrenin karşılığı bir istatistiktir: μ ↔ x̄, p ↔ p̂, σ² ↔ s², σ ↔ s. s² varyansın "
            "tahminidir; σ/√n ise ortalamanın standart hatasıdır, σ'nın tahmini değildir (§12.4)."
        ),
    ),
    Question(
        key="k04", concept="mlt-ile-ortalamanin-dagilimi", note=_note("12.8", "Şekil 12.8", "(12.3)"),
        prompt=(
            "Bir anakütle sağa çarpık; μ = 40, σ = 12. n = 64 gözlemlik rassal örneklemlerin ortalaması X̄'in dağılımı "
            "yaklaşık olarak hangisidir?"
        ),
        answer=MultipleChoice(
            (
                "Anakütle gibi sağa çarpık; ortalama 40, standart sapma 12",
                "Yaklaşık N(40, 12²)",
                "Yaklaşık N(40, 1,5²)",
                "Yaklaşık N(5, 1,5²)",
            ),
            correct=2,
        ),
        explanation=(
            "Merkezi Limit Teoremi: n büyüdükçe X̄'in dağılımı normale yaklaşır, anakütle çarpık olsa bile (§12.8). "
            "Merkez "
            "E(X̄) = μ = 40, yayılım σ/√n = 12/8 = 1,5, (12.2)–(12.3). Standart sapma 12 bireysel gözlemlere aittir."
        ),
    ),
    Question(
        key="k05", concept="yanli-tahmin-edici-tutarli-olmaz", note=_note("12.12"),
        prompt=(
            "Bir tahmin edicinin beklenen değeri n ne olursa olsun θ + 0,5'tir ve standart hatası n büyüdükçe sıfıra "
            "gider. Hangisi doğrudur?"
        ),
        answer=MultipleChoice(
            (
                "Yansız ve tutarlıdır",
                "Yanlıdır ve θ için tutarlı değildir: θ + 0,5 çevresinde yoğunlaşır",
                "Yanlıdır ama tutarlıdır, çünkü standart hatası sıfıra gider",
                "Yansızdır ama tutarlı değildir",
            ),
            correct=1,
        ),
        explanation=(
            "E(θ̂) ≠ θ olduğundan yanlıdır. n büyüdükçe dağılım daralır ama θ + 0,5 çevresinde: 0,5'ten küçük bir ε "
            "için P(|θ̂ − θ| > ε) sıfıra değil bire gider. Tutarlılık gerçek parametre çevresinde yoğunlaşmadır "
            "(§12.12)."
        ),
    ),
    Question(
        key="k06", concept="sistematik-orneklemede-baslangic", note=_note("12.13", "Tablo 12.4"),
        prompt=(
            "1.200 birimlik bir listeden 60 birimlik sistematik örneklem seçilecek. Hangi uygulama Tablo 12.4'teki "
            "tanıma uyar?"
        ),
        answer=MultipleChoice(
            (
                "Her 60. birim seçilir; başlangıç her zaman ilk birimdir",
                "Her 20. birim seçilir; başlangıç her zaman ilk birimdir",
                "Listenin ilk 60 birimi seçilir",
                "1 ile 20 arasından rassal bir başlangıç seçilir, sonra her 20. birim alınır",
            ),
            correct=3,
        ),
        explanation=(
            "Sistematik örneklemede rassal bir başlangıçtan sonra her k. birim seçilir (Tablo 12.4). 60 birim için "
            "k = 1.200/60 = 20; başlangıç ilk 20 birimden rassal seçilir. Sabit başlangıç ya da ilk 60 birim "
            "rassallığı ortadan kaldırır (§12.13)."
        ),
    ),
    Question(
        key="k07", concept="buyuk-n-kapsama-hatasini-gidermez", note=_note("12.14", "Şekil 12.15"),
        prompt=(
            "Bir anket şirketi örneklemi 1.000 kişiden 10.000 kişiye çıkarıyor, ama anketi yine yalnız sabit hatlı "
            "telefonu olanlara uyguluyor. Ne olur?"
        ),
        answer=MultipleChoice(
            (
                "Örnekleme hatası azalır; kapsama sorunu sürdüğü için örnekleme dışı hata azalmaz",
                "İki hata türü de ortadan kalkar",
                "Yalnız örnekleme dışı hata azalır",
                "Örnekleme hatası artar, çünkü daha çok kişi yanıt verir",
            ),
            correct=0,
        ),
        explanation=(
            "Büyük n rassal örneklem değişkenliğini, yani örnekleme hatasını azaltır. Sabit hattı olmayanların hiç "
            "seçilememesi kapsama hatasıdır; örnekleme dışı hata veri miktarıyla düzelmez (§12.14, Şekil 12.15)."
        ),
    ),
    # --- Doğru–yanlış -------------------------------------------------------------
    Question(
        key="d01", concept="sonsuz-anakutlede-duzeltme-yok", note=_note("12.3", "Şekil 12.3"),
        prompt=(
            "Bir üretim hattında gelecekte üretilecek ürünler gibi kavramsal olarak sonsuz bir anakütlede de standart "
            "hata, sonlu anakütle düzeltmesi √((N − n)/(N − 1)) ile çarpılarak hesaplanmalıdır."
        ),
        answer=TrueFalse(False),
        explanation=(
            "Süreç tipi, kavramsal olarak sonsuz bir anakütlede N yoktur; standart hata doğrudan σ/√n'dir "
            "(Şekil 12.3). Düzeltme yalnız sonlu anakütleden yerine koymadan ve n/N > 0,05 iken gerekir (§12.3)."
        ),
    ),
    Question(
        key="d02", concept="tekrar-sayisi-genisligi-daraltmaz", note=_note("12.5", "Şekil 12.5"),
        prompt=(
            "Aynı anakütleden 25'er gözlemlik örneklemler çekilip ortalamaların histogramı çiziliyor. Çekilen "
            "örneklemlerin sayısı 500'den 5.000'e çıkarılırsa (her biri yine 25 gözlem) histogramın genişliği belirgin "
            "biçimde daralmaz."
        ),
        answer=TrueFalse(True),
        explanation=(
            "Örnekleme dağılımının yayılımı her örneklemin büyüklüğüne bağlıdır: σ/√25 = σ/5. Çekilen örneklemlerin "
            "sayısını artırmak bu dağılımı daha ayrıntılı gösterir ama daraltmaz; daraltan n'yi büyütmektir "
            "(§12.5, §12.6)."
        ),
    ),
    Question(
        key="d03", concept="standart-hata-sigmadan-kucuk", note=_note("12.6", "(12.3)"),
        prompt="σ > 0 ve n ≥ 2 iken ortalamanın standart hatası σ/√n, anakütle standart sapması σ'dan küçüktür.",
        answer=TrueFalse(True),
        explanation=(
            "n ≥ 2 için √n > 1 olduğundan σ/√n < σ; n = 1'de ikisi eşittir. Ortalamalar tek tek gözlemlerden daha az "
            "değişkendir: Şekil 12.6'da σ = 15 iken n = 4 için 7,5, n = 25 için 3 (§12.6, (12.3))."
        ),
    ),
    Question(
        key="d04", concept="beklenen-deger-her-n-icin", note=_note("12.8", "(12.2)"),
        prompt="E(X̄) = μ eşitliği yalnız n ≥ 30 olduğunda, Merkezi Limit Teoremi sayesinde geçerlidir.",
        answer=TrueFalse(False),
        explanation=(
            "(12.2) her n için geçerlidir: X̄, μ için yansızdır. Merkezi Limit Teoremi X̄'in dağılımının biçimiyle "
            "ilgilidir; n ≥ 30 da yalnız bu biçim için pratik bir başlangıç kuralıdır, evrensel bir eşik değildir "
            "(§12.8, §12.6)."
        ),
    ),
    Question(
        key="d05", concept="oranin-en-buyuk-standart-hatasi", note=_note("12.10", "(12.8)"),
        prompt="Aynı n için örneklem oranının standart hatası √(p(1 − p)/n), p = 0,5 iken en büyük değerini alır.",
        answer=TrueFalse(True),
        explanation=(
            "p(1 − p) çarpımı p = 0,5'te en büyüktür (0,25) ve p 0'a ya da 1'e yaklaştıkça küçülür: p = 0,1 için 0,09. "
            "n = 100'de p = 0,5 için σ_p̂ = 0,05, p = 0,1 için σ_p̂ = 0,03 (§12.10, (12.8))."
        ),
    ),
    Question(
        key="d06", concept="ayni-orneklemde-xbar-daha-etkin", note=_note("12.12", "Tablo 12.3"),
        prompt=(
            "Aynı 25 gözlemlik örneklemden hesaplanan X̄ ile yalnız ilk gözlem X₁, μ için yansızdır; X̄, X₁'den daha "
            "etkindir."
        ),
        answer=TrueFalse(True),
        explanation=(
            "E(X̄) = μ ve E(X₁) = μ: ikisi de yansızdır. Standart hataları σ/5 ve σ'dır; aynı hedef için varyansı daha "
            "küçük olan yansız tahmin edici daha etkindir (Tablo 12.3). X₁ örneklemdeki diğer 24 gözlemin bilgisini "
            "kullanmaz (§12.12)."
        ),
    ),
    Question(
        key="d07", concept="kume-ile-tabakanin-farki", note=_note("12.13", "Tablo 12.4"),
        prompt=(
            "Bir okul müdürlüğü okuldaki 60 sınıftan 6'sını rassal seçip bu sınıflardaki bütün öğrencilere anket "
            "uyguluyor. Bu tasarım tabakalı örneklemedir."
        ),
        answer=TrueFalse(False),
        explanation=(
            "Sınıflar kümedir: bazı kümeler rassal seçilir ve veri seçilen kümelerden toplanır; bu küme örneklemesidir "
            "(Tablo 12.4). Tabakalı örneklemede her sınıftan (tabakadan) rassal öğrenci seçilirdi (§12.13)."
        ),
    ),
    # --- Boşluk doldurma ----------------------------------------------------------
    Question(
        key="b01", concept="ortalamanin-merkezi-ve-standart-hatasi", note=_note("12.6", "(12.2)", "(12.3)"),
        prompt=(
            "Bir anakütlede μ = 250 ve σ = 30. n = 36 gözlemlik örneklemler için E(X̄) = **(1)** ve "
            "σ_X̄ = **(2)** olur."
        ),
        answer=FillBlanks((NumberBlank(250, 0.005, "250"), NumberBlank(5, 0.005, "5"))),
        explanation="(12.2): E(X̄) = μ = 250. (12.3): σ_X̄ = σ/√n = 30/√36 = 30/6 = 5 (§12.6).",
    ),
    Question(
        key="b02", concept="ortalamayla-sag-kuyruk", note=_note("12.9", "(12.5)"),
        prompt=(
            "Bir kafede fiş tutarının ortalaması μ = 120 TL, standart sapması σ = 40 TL. 64 fişlik rassal örneklemde "
            "X̄ yaklaşık normaldir. σ_X̄ = **(1)** TL ve P(X̄ > 130) = **(2)** olur (Φ(2,00) = 0,9772; dört ondalık "
            "basamak)."
        ),
        answer=FillBlanks((NumberBlank(5, 0.005, "5"), NumberBlank(0.0228, 0.0001, "0,0228"))),
        explanation=(
            "σ_X̄ = 40/√64 = 5. (12.5): z = (130 − 120)/5 = 2 ve P(X̄ > 130) = 1 − 0,9772 = 0,0228. Paydada σ değil "
            "standart hata kullanılır; fiş tutarları normal dağılsaydı tek bir fişin 130 TL'yi aşma olasılığı "
            "1 − Φ(0,25) ≈ 0,40 olurdu (§12.9)."
        ),
    ),
    Question(
        key="b03", concept="oranin-merkezi-ve-standart-hatasi", note=_note("12.10", "(12.7)", "(12.8)"),
        prompt="p = 0,20 ve n = 400 için E(p̂) = **(1)** ve σ_p̂ = **(2)** olur.",
        answer=FillBlanks((NumberBlank(0.2, 0.0005, "0,20"), NumberBlank(0.02, 0.0005, "0,02"))),
        explanation=(
            "(12.7): E(p̂) = p = 0,20. (12.8): σ_p̂ = √(0,20 × 0,80/400) = √0,0004 = 0,02. np = 80 ve n(1 − p) = 320 "
            "olduğundan normal yaklaşım da uygundur (§12.10)."
        ),
    ),
    Question(
        key="b04", concept="sonlu-anakutle-duzeltmesi-sayisal", note=_note("12.11", "(12.4)"),
        prompt=(
            "N = 1.000, n = 250 ve σ = 50 olsun. Düzeltmesiz standart hata **(1)**, sonlu anakütle düzeltmeli standart "
            "hata **(2)** olur (iki ondalık basamak)."
        ),
        answer=FillBlanks((NumberBlank(50 / 250 ** 0.5, 0.005, "3,16"),
                           NumberBlank(50 / 250 ** 0.5 * (750 / 999) ** 0.5, 0.011, "2,74"))),
        explanation=(
            "n/N = 0,25 > 0,05 olduğundan düzeltme gerekir. 50/√250 ≈ 3,162; düzeltme √(750/999) ≈ 0,866 ve "
            "0,866 × 3,162 ≈ 2,74, (12.4). Örnekleme oranı büyüdükçe fark büyür (§12.11)."
        ),
    ),
    Question(
        key="b05", concept="butunlestirici-yeni-orneklem", note=_note("12.15"),
        prompt=(
            "§12.15'teki işletme (μ = 600 TL, σ = 120 TL, p = 0,64) örneklemi n = 225 müşteriye çıkarıyor. "
            "σ_X̄ = **(1)** TL ve σ_p̂ = **(2)** olur (üç ondalık basamak)."
        ),
        answer=FillBlanks((NumberBlank(8, 0.005, "8"), NumberBlank(0.032, 0.0005, "0,032"))),
        explanation=(
            "σ_X̄ = 120/√225 = 120/15 = 8. σ_p̂ = √(0,64 × 0,36/225) = 0,48/15 = 0,032. n = 100'e göre ikisi de "
            "10/15 = 2/3 katına iner; iki standart hata da 1/√n ile ölçeklenir (§12.15, §12.6, §12.10)."
        ),
    ),
    # --- Denklem yazma -----------------------------------------------------------
    Question(
        key="e01", concept="duzeltmesiz-en-buyuk-orneklem", note=_note("12.3", "(12.1)"),
        prompt=(
            "N birimlik bir anakütlede sonlu anakütle düzeltmesini ihmal edebilmek için seçilebilecek en büyük "
            "örneklem büyüklüğünü yazın."
        ),
        answer=Equation(
            lhs="n_{\\max}",
            symbols=(Symbol("N", "N", "anakütle büyüklüğü", 100, 100000),),
            answer="0.05*N",
            shown="0{,}05\\,N",
        ),
        explanation=(
            "(12.1): n/N ≤ 0,05 ⇒ n ≤ 0,05N. N = 2.400 için en çok 120 birim; daha büyük örneklemlerde (12.4)'teki "
            "düzeltme kullanılır (§12.3)."
        ),
    ),
    Question(
        key="e02", concept="xbar-varyansi", note=_note("12.6", "(12.3)"),
        prompt="Sonsuz anakütleden n gözlemlik rassal örneklemde X̄'in varyansını σ ve n cinsinden yazın.",
        answer=Equation(
            lhs="\\sigma^2_{\\bar X}",
            symbols=(SIGMA, Symbol("n", "n", "örneklem büyüklüğü", 2, 400)),
            answer="s^2/n",
            shown="\\frac{\\sigma^2}{n}",
        ),
        explanation=(
            "Standart hata σ/√n'dir, (12.3); varyans bunun karesidir: σ²/n. Varyans n ile ters orantılı, standart "
            "hata √n ile ters orantılı küçülür: n dört katına çıkınca varyans dörtte bire, standart hata yarıya iner "
            "(§12.6)."
        ),
    ),
    Question(
        key="e03", concept="hedef-standart-hata-icin-n", note=_note("12.7", "Tablo 12.2"),
        prompt="Ortalamanın standart hatasının h olması için gereken örneklem büyüklüğünü σ ve h cinsinden yazın.",
        answer=Equation(
            lhs="n",
            symbols=(SIGMA, Symbol("h", "h", "hedef standart hata", 0.5, 5)),
            answer="(s/h)^2",
            shown="\\left(\\frac{\\sigma}{h}\\right)^2",
        ),
        explanation=(
            "σ/√n = h ⇒ √n = σ/h ⇒ n = (σ/h)². Tablo 12.2'de σ = 20 için h = 2 → n = 100, h = 1 → n = 400: standart "
            "hatayı yarıya indirmek n'yi dört katına çıkarır (§12.7)."
        ),
    ),
    Question(
        key="e04", concept="ortalamanin-sapma-siniri-icin-z", note=_note("12.9", "(12.5)"),
        prompt=(
            "X̄'in μ'den en fazla d kadar uzak olması olayı −z ≤ Z ≤ z biçiminde yazılır. z'yi d, n ve σ cinsinden "
            "yazın; karekök için sqrt() kullanın."
        ),
        answer=Equation(
            lhs="z",
            symbols=(Symbol("d", "d", "izin verilen uzaklık", 1, 20), Symbol("n", "n", "örneklem büyüklüğü", 4, 400),
                     SIGMA),
            answer="d*sqrt(n)/s",
            shown="\\frac{d\\sqrt{n}}{\\sigma}",
        ),
        explanation=(
            "(12.5): z = d/(σ/√n) = d√n/σ. Dolum örneğinde d = 10, n = 36, σ = 60 için z = 1 ve olasılık 0,6826. "
            "Aynı d için n büyüdükçe z büyür ve olasılık artar (§12.9)."
        ),
    ),
    Question(
        key="e05", concept="oran-kosulu-icin-en-kucuk-n", note=_note("12.10", "(12.10)"),
        prompt=(
            "p < 0,5 olsun. Örneklem oranı için normal yaklaşım koşulunu sağlayan en küçük örneklem büyüklüğünü p "
            "cinsinden yazın."
        ),
        answer=Equation(
            lhs="n_{\\min}",
            symbols=(Symbol("p", "p", "anakütle oranı (0,5'ten küçük)", 0.05, 0.45),),
            answer="5/p",
            shown="\\frac{5}{p}",
        ),
        explanation=(
            "(12.10): np ≥ 5 ve n(1 − p) ≥ 5. p < 0,5 iken np < n(1 − p) olduğundan bağlayıcı koşul np ≥ 5'tir: "
            "n ≥ 5/p. p = 0,04 için en az 125 gözlem (§12.10)."
        ),
    ),
)


KONU12_QUIZ = QuestionSet(
    topic_key="konu12",
    title="Konu 12: Kendini sına",
    questions=QUESTIONS,
    intro=(
        "Bu set haftanın temel kavramlarını sınar. Her soru tek bir kavrama odaklanır ve notlardaki bir "
        "bölüme bağlıdır; yanlış cevaplarınız için tekrar edilecek bölümler en üstte listelenir. Notlardaki "
        "egzersiz ve mini quiz maddelerini tekrar etmez, yeni sayılarla onları tamamlar."
    ),
    sections=tuple(f"12.{number}" for number in range(1, 16)),
)
