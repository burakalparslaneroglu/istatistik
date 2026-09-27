"""Konu 9 "Kendini sına" soru seti.

Her soru tek bir kavramı sınar ve notlardaki bir bölüme bağlıdır. Sorular notların Egzersiz 9.1–9.13 ve Mini Quiz
9.1–9.13 maddelerini tekrar etmez (ör. 12 müşteri ve 0,20, 10 dakikada 4 müşteri, 30 faturanın 6'sı, 0,30 olasılıklı
10 kullanıcı, saatte 8 acil talep, 25 parçanın 5'i, 0,04 ile 100 ürünlük parti, on iki kısa hikâye, minimal çiftler
tablosu, öğrenci ifadeleri, Bin(20, 0,15)–Pois(4)–Hiper(30, 6, 5) hesapları, 12 müşteri–6 duruş–18 dosya); yeni
sayılarla ve yeni bağlamlarla aynı becerileri sınar. Sürekli dağılımlar bir sonraki konunun konusudur; bu sette
kullanılmaz.
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
        key="k01", concept="sayimin-olusumu-dagilimi-belirler", note=_note("9.1", "Şekil 9.1"),
        prompt=(
            "Bir üniversite kütüphanesinde üç sayım yapılıyor: (A) bir saatte ödünç verilen kitap sayısı; (B) iade "
            "edilen 36 kitabın 9'u hasarlıdır, bu 36 kitaptan yerine koymadan seçilen 4 kitaptaki hasarlı sayısı; "
            "(C) bugün kitap alan 14 okuyucudan kitabı geç iade edenlerin sayısı, her okuyucu birbirinden bağımsız "
            "olarak 0,15 olasılıkla geç iade ediyor. Hangi eşleştirme doğrudur?"
        ),
        answer=MultipleChoice(
            (
                "A: binom, B: hipergeometrik, C: Poisson",
                "A: Poisson, B: binom, C: hipergeometrik",
                "A: Poisson, B: hipergeometrik, C: binom",
                "A: hipergeometrik, B: Poisson, C: binom",
            ),
            correct=2,
        ),
        explanation=(
            "A sabit bir zaman aralığındaki olay sayısıdır (Poisson); B sonlu bir anakütleden yerine koymadan "
            "seçimdir (hipergeometrik); C sabit n = 14 bağımsız denemedeki başarı sayısıdır (binom). Üçü de "
            "\"kaç tane?\" sorusuna cevap verir; dağılımı sayımın nasıl oluştuğu belirler (§9.1, Şekil 9.1)."
        ),
    ),
    Question(
        key="k02", concept="kosullar-saglanmazsa-otomatik-model-yok", note=_note("9.2", "Şekil 9.2"),
        prompt=(
            "Şekil 9.2'deki karar ağacında bir problem şu cevapları alıyor: sabit bir aralıkta olay sayısı "
            "sayılmıyor; sabit sayıda (n = 10) deneme var; seçim sonlu bir anakütleden yerine koymadan yapılmıyor; "
            "ama denemelerin başarı olasılığı denemeden denemeye değişiyor. Karar ağacının sonucu nedir?"
        ),
        answer=MultipleChoice(
            (
                "Binom, çünkü deneme sayısı sabittir",
                "Poisson, çünkü bir sayım yapılmaktadır",
                "Hipergeometrik, çünkü başarı olasılığı değişmektedir",
                "Bu üç dağılımdan biri otomatik olarak seçilmez",
            ),
            correct=3,
        ),
        explanation=(
            "Binom için sabit n, iki sonuç, sabit p ve bağımsızlık birlikte gerekir; p değiştiği için son soru "
            "\"hayır\" cevabı alır. Hipergeometrikteki değişim yerine koymadan seçimden gelir; burada öyle bir seçim "
            "yoktur. Koşullar sağlanmıyorsa üç dağılımdan biri otomatik olarak seçilmez (§9.2, Şekil 9.2)."
        ),
    ),
    Question(
        key="k03", concept="binom-katsayisinin-rolu", note=_note("9.3", "Şekil 9.5"),
        prompt="P(X = x) = C(n, x) pˣ (1 − p)ⁿ⁻ˣ formülünde C(n, x) çarpanı neyi sayar?",
        answer=MultipleChoice(
            (
                "x başarının n deneme içinde yerleşebileceği farklı konumların sayısını",
                "x başarının olasılık katkısını",
                "n − x başarısızlığın olasılık katkısını",
                "Deneyin bütün olası sonuç dizilerinin sayısını",
            ),
            correct=0,
        ),
        explanation=(
            "pˣ(1 − p)ⁿ⁻ˣ belirli bir başarı–başarısızlık dizisinin olasılığıdır; C(n, x), x başarı içeren farklı "
            "dizilerin sayısıdır. 8 denemede 2 başarı C(8, 2) = 28 farklı dizide gerçekleşir ve her dizinin "
            "olasılığı aynıdır. Bütün dizilerin sayısı ise 2ⁿ'dir (§9.3.3, Şekil 9.5)."
        ),
    ),
    Question(
        key="k04", concept="hipergeometrik-hikayeyi-tanimak", note=_note("9.9"),
        prompt="Aşağıdaki hikâyelerden hangisinin uygun modeli hipergeometrik dağılımdır?",
        answer=MultipleChoice(
            (
                "Bir fotokopi makinesinde bir günde oluşan kâğıt sıkışması sayısı",
                "35 kişilik bir sınıfta 8 öğrenci burslu; kurayla ve yerine koymadan seçilen 6 kişilik temsilci "
                "grubundaki burslu sayısı",
                "25 kredi kartı işleminden şüpheli işaretlenenlerin sayısı; her işlem birbirinden bağımsız olarak "
                "0,03 olasılıkla işaretleniyor",
                "Bir yazılımın 1000 satırlık kodunda bulunan hata sayısı",
            ),
            correct=1,
        ),
        explanation=(
            "Sonlu anakütle (N = 35), anakütledeki başarı sayısı (r = 8) ve yerine koymadan seçim (n = 6) "
            "hipergeometrik modelin işaretleridir. Günlük sıkışma ve kod satırlarındaki hata sabit bir aralıktaki "
            "olay sayısıdır (Poisson); 25 bağımsız işlem binomdur (§9.9; özet için §9.8, Tablo 9.3)."
        ),
    ),
    Question(
        key="k05", concept="hipergeometrik-degerler-kumesi", note=_note("9.8", "Tablo 9.3"),
        prompt=(
            "20 ürünlük bir partide 3 ürün kusurludur ve partiden yerine koymadan 5 ürün seçiliyor. Seçilen kusurlu "
            "sayısı X hangi değerleri alabilir?"
        ),
        answer=MultipleChoice(("0, 1, 2, 3", "0, 1, 2, 3, 4, 5", "1, 2, 3", "0, 1, …, 20"), correct=0),
        explanation=(
            "Seçilen kusurlu sayısı ne seçilen ürün sayısını (n = 5) ne de partideki kusurlu sayısını (r = 3) "
            "aşabilir; hiç kusurlu seçilmemesi de mümkündür. Bu yüzden X ∈ {0, 1, 2, 3}: hipergeometrik dağılımın "
            "değerleri anakütle kısıtlarına bağlıdır (§9.8, Tablo 9.3; model §9.5)."
        ),
    ),
    Question(
        key="k06", concept="tam-model-ve-binom-yaklasimi", note=_note("9.6", "(9.13)"),
        prompt=(
            "5000 ürünlük bir partide 500 kusurlu ürün vardır ve partiden yerine koymadan 10 ürün seçiliyor. "
            "Hangisi doğrudur?"
        ),
        answer=MultipleChoice(
            (
                "Tam model binomdur, çünkü anakütle büyüktür",
                "Tam model Poisson'dur, çünkü kusurlu oranı küçüktür",
                "Tam model hipergeometriktir; (5000 − 10)/(5000 − 1) ≈ 0,998 olduğundan Bin(10, 0,10) iyi bir "
                "yaklaşımdır",
                "Seçimler bağımsız olduğundan iki model tamamen aynı olasılıkları verir",
            ),
            correct=2,
        ),
        explanation=(
            "Seçim sonlu bir partiden yerine koymadan yapıldığı için tam model Hiper(N = 5000, r = 500, n = 10) "
            "modelidir. Örneklem oranı küçük olduğundan kusurlu oranı seçimler arasında çok az değişir ve düzeltme "
            "çarpanı ≈ 0,998'dir; binom yalnız bir yaklaşımdır. Derste önce tam model belirlenir (§9.6, (9.13))."
        ),
    ),
    Question(
        key="k07", concept="cozum-sirasi", note=_note("9.13", "Şekil 9.11"),
        prompt="Şekil 9.11'deki çözüm sırasında \"Dağılımı seç\" adımından hemen önce hangi adım gelir?",
        answer=MultipleChoice(
            (
                "Parametreleri belirle",
                "Deney yapısını tanı",
                "\"Tam / en az / en çok\" ifadesini matematiksel olaya çevir",
                "Olasılığı hesapla ve bağlam içinde yorumla",
            ),
            correct=1,
        ),
        explanation=(
            "Sıra: rassal değişkeni tanımla → deney yapısını tanı → dağılımı seç → parametreleri belirle → "
            "\"tam / en az / en çok\" ifadesini olaya çevir → hesapla ve yorumla. Parametreler ve formül ancak model "
            "seçildikten sonra devreye girer (§9.13, Şekil 9.11)."
        ),
    ),
    # --- Doğru–yanlış -------------------------------------------------------------
    Question(
        key="d01", concept="bernoulli-varyansinin-en-buyugu", note=_note("9.3"),
        prompt=(
            "Bernoulli değişkeni Y'nin varyansı p(1 − p)'dir; bu varyans p = 0,5 iken en büyüktür ve 0,25'e "
            "eşittir."
        ),
        answer=TrueFalse(True),
        explanation=(
            "Var(Y) = p(1 − p) = 0,25 − (p − 0,5)² olduğundan en büyük değer p = 0,5'te 0,25'tir. p, 0'a ya da 1'e "
            "yaklaştıkça sonuç neredeyse kesinleşir ve varyans küçülür; p = 0,25 için 0,1875 (§9.3.1)."
        ),
    ),
    Question(
        key="d02", concept="varyanslarin-toplanmasi-bagimsizlik-ister", note=_note("9.3", "(9.1)"),
        prompt=(
            "Bernoulli denemeleri birbirine bağımlı olsa da X = Y₁ + ⋯ + Yₙ toplamının varyansı her zaman "
            "np(1 − p)'dir."
        ),
        answer=TrueFalse(False),
        explanation=(
            "E(X) = np için bağımsızlık gerekmez; beklenen değerler her durumda toplanır. Varyansların toplanması "
            "ise denemelerin bağımsızlığına dayanır: Var(X) = Σ Var(Yᵢ) = np(1 − p) bağımsızlık varsayımıyla elde "
            "edilir (§9.3.2). Yerine koymadan seçimde varyansın düzeltme çarpanıyla küçülmesi bunun örneğidir, "
            "(9.13)."
        ),
    ),
    Question(
        key="d03", concept="en-cok-olayinin-tumleyeni", note=_note("9.3", "(9.3)"),
        prompt="X ~ Bin(6, 0,3) için P(X ≤ 2) = 1 − P(X ≥ 2)'dir.",
        answer=TrueFalse(False),
        explanation=(
            "X ≤ 2 olayının tümleyeni X ≥ 3'tür: P(X ≤ 2) = 1 − P(X ≥ 3). X = 2 değeri hem X ≤ 2 hem de X ≥ 2 "
            "olayındadır; bu yüzden 1 − P(X ≥ 2) = P(X ≤ 1) olur. \"Tam\", \"en az\" ve \"en çok\" farklı olaylardır "
            "(§9.3.4)."
        ),
    ),
    Question(
        key="d04", concept="ayrik-araliklarda-bagimsizlik", note=_note("9.4"),
        prompt=(
            "Poisson modelinde, birbiriyle çakışmayan iki zaman aralığındaki olay sayıları birbirinden bağımsız "
            "kabul edilir."
        ),
        answer=TrueFalse(True),
        explanation=(
            "Poisson deneyinin iki temel özelliği vardır: eşit uzunluktaki aralıklarda olay oluşum davranışı "
            "aynıdır ve ayrık aralıklardaki oluşumlar bağımsızdır. 09.00–09.15 aralığında çok çağrı gelmesi "
            "09.15–09.30 aralığındaki çağrı sayısını değiştirmez (§9.4)."
        ),
    ),
    Question(
        key="d05", concept="sabit-deneme-sayisi-binomu-gosterir", note=_note("9.7", "Tablo 9.2"),
        prompt=(
            "\"Bugün mağazaya giren 40 müşteriden kaçı alışveriş yapar?\" sorusu (her müşterinin alışveriş "
            "olasılığı aynı, kararlar bağımsız) bir günlük aralıktan söz ettiği için Poisson modeliyle çözülür."
        ),
        answer=TrueFalse(False),
        explanation=(
            "Soru sabit bir aralıktaki olay sayısını değil, önceden belli n = 40 müşteri içindeki başarı sayısını "
            "sorar: sabit n, iki sonuç, sabit p ve bağımsızlık binom modelidir. X en fazla 40 olabilir; Poisson'da "
            "ise teorik üst sınır yoktur (§9.7, Tablo 9.2)."
        ),
    ),
    Question(
        key="d06", concept="ayni-nesne-farkli-deney-yapisi", note=_note("9.10", "Tablo 9.4"),
        prompt=(
            "\"Bir yazılım testinde bir saatte bulunan hata sayısı\" ile \"test edilen 30 bağımsız modülden hatalı "
            "olanların sayısı (her modülün hatalı olma olasılığı 0,1)\" ikisi de hata saydığı için ikisi de Poisson "
            "dağılımıyla modellenir."
        ),
        answer=TrueFalse(False),
        explanation=(
            "Birincisi sabit bir zaman aralığındaki olay sayısıdır (Poisson); ikincisi sabit n = 30 bağımsız "
            "denemedeki başarı sayısıdır, Bin(30, 0,1). Model seçimini bağlamdaki nesne değil, deney yapısı "
            "belirler (§9.10, Tablo 9.4)."
        ),
    ),
    Question(
        key="d07", concept="en-az-ifadesi-olayi-belirler", note=_note("9.11", "Tablo 9.5"),
        prompt=(
            "\"Bir vardiyada en az bir iş kazası olma olasılığı\" sorusunda \"en az bir\" ifadesi dağılımı değil, "
            "hesaplanacak olayı belirler."
        ),
        answer=TrueFalse(True),
        explanation=(
            "Model, vardiyadaki kaza sayısının nasıl oluştuğuna göre seçilir (ör. sabit aralıkta olay sayısı ise "
            "Poisson). \"En az bir\" ise X ≥ 1 olayını tanımlar; olasılığı tümleyenle P(X ≥ 1) = 1 − P(X = 0) "
            "olarak hesaplanır. Önce model seçilir, sonra olay hesaplanır (§9.11, Tablo 9.5)."
        ),
    ),
    # --- Boşluk doldurma ----------------------------------------------------------
    Question(
        key="b01", concept="binom-tam-bir-ve-hic", note=_note("9.3", "(9.2)"),
        prompt=(
            "Bir kargo firmasında her gönderi birbirinden bağımsız olarak 0,10 olasılıkla hasarlı ulaşıyor. 6 "
            "gönderiden tam 1'inin hasarlı ulaşma olasılığı **(1)**, hiçbirinin hasarlı ulaşmama olasılığı **(2)** "
            "olur (dört ondalık basamak)."
        ),
        answer=FillBlanks((NumberBlank(0.354294, 0.0005, "0,3543"), NumberBlank(0.531441, 0.0005, "0,5314"))),
        explanation=(
            "X ~ Bin(6, 0,10): P(X = 1) = C(6, 1)(0,10)(0,90)⁵ = 6 × 0,10 × 0,59049 = 0,3543; P(X = 0) = (0,90)⁶ "
            "= 0,5314. En az bir hasarlı gönderi olasılığı tümleyenle 1 − 0,5314 = 0,4686'dır (§9.3.3, (9.2))."
        ),
    ),
    Question(
        key="b02", concept="poisson-olasilik-hesabi", note=_note("9.4", "(9.7)"),
        prompt=(
            "Bir web sitesine dakikada ortalama 2,5 sipariş geliyor ve Poisson koşulları sağlanıyor. Bir dakikada "
            "tam 3 sipariş gelme olasılığı **(1)**, hiç sipariş gelmeme olasılığı **(2)** olur (dört ondalık "
            "basamak)."
        ),
        answer=FillBlanks((NumberBlank(0.213763, 0.0005, "0,2138"), NumberBlank(0.082085, 0.0005, "0,0821"))),
        explanation=(
            "λ = 2,5: P(X = 3) = 2,5³e⁻²·⁵/3! = 15,625(0,0821)/6 = 0,2138; P(X = 0) = e⁻²·⁵ = 0,0821. λ bir "
            "dakikadaki beklenen sipariş sayısıdır; tek bir dakikada 3 sipariş gelmesi bu uzun dönem ortalamasıyla "
            "çelişmez (§9.4, (9.7))."
        ),
    ),
    Question(
        key="b03", concept="hipergeometrik-olasilik-hesabi", note=_note("9.5", "(9.11)"),
        prompt=(
            "12 kişilik bir proje ekibinde 4 kişi yöneticidir. Kurayla ve yerine koymadan 3 kişi seçiliyor. "
            "Seçilenlerden tam 1'inin yönetici olma olasılığı **(1)**, hiçbirinin yönetici olmama olasılığı **(2)** "
            "olur (dört ondalık basamak)."
        ),
        answer=FillBlanks((NumberBlank(112 / 220, 0.0005, "0,5091"), NumberBlank(56 / 220, 0.0005, "0,2545"))),
        explanation=(
            "N = 12, r = 4, n = 3: P(X = 1) = C(4, 1)C(8, 2)/C(12, 3) = 4 × 28/220 = 0,5091; P(X = 0) = "
            "C(8, 3)/C(12, 3) = 56/220 = 0,2545. Payda, 12 kişiden 3 kişi seçmenin bütün yollarıdır (§9.5, (9.11))."
        ),
    ),
    Question(
        key="b04", concept="ayni-ortalama-farkli-varyans", note=_note("9.8", "Tablo 9.3"),
        prompt=(
            "Bin(20, 0,25), Pois(5) ve Hiper(N = 40, r = 10, n = 20) dağılımlarının üçünün de beklenen değeri 5'tir. "
            "Varyansları binom için **(1)**, Poisson için **(2)** ve hipergeometrik için **(3)** olur "
            "(hipergeometriği dört ondalık basamakla yazın)."
        ),
        answer=FillBlanks(
            (
                NumberBlank(3.75, 0.0005, "3,75"),
                NumberBlank(5, 0.0005, "5"),
                NumberBlank(3.75 * 20 / 39, 0.0005, "1,9231"),
            )
        ),
        explanation=(
            "Binom: np(1 − p) = 20(0,25)(0,75) = 3,75. Poisson: Var(X) = λ = 5. Hipergeometrik: "
            "n(r/N)(1 − r/N)(N − n)/(N − 1) = 3,75 × 20/39 = 1,9231; yerine koymadan seçim varyansı küçültür. Aynı "
            "ortalama farklı belirsizlik düzeyleri taşıyabilir (§9.8, Tablo 9.3)."
        ),
    ),
    Question(
        key="b05", concept="ayni-isletmede-farkli-modeller", note=_note("9.12", "Tablo 9.6"),
        prompt=(
            "Bir kafede iki soru soruluyor. (i) Birbirinden bağımsız 18 müşterinin her biri 0,10 olasılıkla tatlı "
            "sipariş ediyor; en az bir tatlı siparişi olasılığı **(1)** olur. (ii) Kafeye 5 dakikada ortalama 1,2 "
            "müşteri geliyor (Poisson); 5 dakikada hiç müşteri gelmeme olasılığı **(2)** olur (dört ondalık "
            "basamak)."
        ),
        answer=FillBlanks((NumberBlank(0.849905, 0.0005, "0,8499"), NumberBlank(0.301194, 0.0005, "0,3012"))),
        explanation=(
            "(i) Bin(18, 0,10): P(X ≥ 1) = 1 − (0,90)¹⁸ = 1 − 0,1501 = 0,8499. (ii) Pois(1,2): P(Y = 0) = e⁻¹·² = "
            "0,3012. Aynı işletmede iki farklı belirsizlik mekanizması iki farklı dağılım gerektirir (§9.12, "
            "Tablo 9.6)."
        ),
    ),
    # --- Denklem yazma -----------------------------------------------------------
    Question(
        key="e01", concept="en-az-iki-tumleyenle", note=_note("9.3", "(9.2)"),
        prompt="X ~ Bin($n$, $p$) için P(X ≥ 2)'yi tümleyen olayla yazın.",
        answer=Equation(
            lhs="P(X \\geq 2)",
            symbols=(Symbol("n", "n", "deneme sayısı", 2, 20), Symbol("p", "p", "başarı olasılığı", 0.05, 0.95)),
            answer="1 - (1-p)^n - n*p*(1-p)^(n-1)",
            shown="1 - (1-p)^n - n\\,p\\,(1-p)^{n-1}",
        ),
        explanation=(
            "X ≥ 2 olayının tümleyeni X ≤ 1, yani {X = 0} ∪ {X = 1}: P(X ≥ 2) = 1 − (1 − p)ⁿ − np(1 − p)ⁿ⁻¹. "
            "Bin(8, 0,25) için 1 − 0,1001 − 0,2670 = 0,6329 (§9.3.4, (9.2), (9.3))."
        ),
    ),
    Question(
        key="e02", concept="ortalamadan-varyansa", note=_note("9.3", "(9.5)"),
        prompt="X ~ Bin(n, p) değişkeninin beklenen değeri E(X) = $m$'dir. Var(X)'i $m$ ve $p$ cinsinden yazın.",
        answer=Equation(
            lhs="\\operatorname{Var}(X)",
            symbols=(Symbol("m", "m", "E(X) = np", 0.5, 20), Symbol("p", "p", "başarı olasılığı", 0.05, 0.95)),
            answer="m*(1-p)",
            shown="m\\,(1-p)",
        ),
        explanation=(
            "E(X) = np = m olduğundan Var(X) = np(1 − p) = m(1 − p). Bin(8, 0,25)'te m = 2 ve Var(X) = 2(0,75) = "
            "1,5 (§9.3.5, (9.4), (9.5))."
        ),
    ),
    Question(
        key="e03", concept="lambdayi-araliga-donusturmek", note=_note("9.4", "Şekil 9.7"),
        prompt=(
            "Bir süreçte saatte ortalama $r$ olay gerçekleşiyor ve Poisson koşulları sağlanıyor. $t$ dakikalık "
            "aralık için λ'yı yazın."
        ),
        answer=Equation(
            lhs="\\lambda",
            symbols=(Symbol("r", "r", "saatlik ortalama olay sayısı", 1, 30),
                     Symbol("t", "t", "aralığın uzunluğu (dakika)", 1, 120)),
            answer="r*t/60",
            shown="r\\,t/60",
        ),
        explanation=(
            "λ, incelenen aralıktaki beklenen olay sayısıdır ve aralığın uzunluğuyla orantılıdır: λ = r × t/60. "
            "Saatte 12 çağrı için 15 dakikada λ = 12 × 15/60 = 3 (§9.4.1, Şekil 9.7)."
        ),
    ),
    Question(
        key="e04", concept="sonlu-anakutle-duzeltme-carpani", note=_note("9.5", "(9.13)"),
        prompt=(
            "Hipergeometrik varyans, binom biçimli n(r/N)(1 − r/N) ifadesinin bir düzeltme çarpanıyla çarpımıdır. "
            "Bu çarpanı $N$ ve $n$ cinsinden yazın."
        ),
        answer=Equation(
            lhs="\\text{düzeltme çarpanı}",
            symbols=(Symbol("N", "N", "anakütle büyüklüğü", 20, 200), Symbol("n", "n", "seçilen birim sayısı", 1, 15)),
            answer="(N-n)/(N-1)",
            shown="\\frac{N-n}{N-1}",
        ),
        explanation=(
            "(N − n)/(N − 1), yerine koymadan seçimin varyansı küçülten etkisidir: N = 20, n = 4 için 16/19 = 0,8421 "
            "ve Var(X) = 4(0,25)(0,75)(0,8421) = 0,6316. N büyüdükçe çarpan 1'e yaklaşır (§9.5, (9.13))."
        ),
    ),
    Question(
        key="e05", concept="poisson-en-cok-bir", note=_note("9.4", "(9.7)"),
        prompt="X ~ Pois(λ) için P(X ≤ 1)'i yazın. e üzeri u için exp(u) yazın (ör. exp(-L)).",
        answer=Equation(
            lhs="P(X \\leq 1)",
            symbols=(Symbol("L", "\\lambda", "beklenen olay sayısı λ", 0.5, 8, aliases=("λ",)),),
            answer="exp(-L)*(1+L)",
            shown="e^{-\\lambda}(1+\\lambda)",
        ),
        explanation=(
            "X ≤ 1 olayı {X = 0} ∪ {X = 1}'dir: P(X ≤ 1) = e^(−λ) + λe^(−λ) = e^(−λ)(1 + λ). λ = 3 için "
            "e⁻³ × 4 = 0,1991 (§9.4, (9.7))."
        ),
    ),
)


KONU09_QUIZ = QuestionSet(
    topic_key="konu09",
    title="Konu 9: Kendini sına",
    questions=QUESTIONS,
    intro=(
        "Bu set haftanın temel kavramlarını sınar. Her soru tek bir kavrama odaklanır ve notlardaki bir "
        "bölüme bağlıdır; yanlış cevaplarınız için tekrar edilecek bölümler en üstte listelenir. Notlardaki "
        "egzersiz ve mini quiz maddelerini tekrar etmez, yeni sayılarla onları tamamlar."
    ),
    sections=tuple(f"9.{number}" for number in range(1, 14)),
)
