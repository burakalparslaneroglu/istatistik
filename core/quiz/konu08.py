"""Konu 8 "Kendini sına" soru seti.

Her soru tek bir kavramı sınar ve notlardaki bir bölüme bağlıdır. Sorular notların Egzersiz 8.1–8.15 ve Mini Quiz
8.1–8.15 maddelerini tekrar etmez (ör. P(X = 3), P(X ≥ 2) ve P(1 ≤ X ≤ 3), 0,25–0,30–a–0,15 tablosu, 100 çağrı
aralığı, acil servis maliyeti, 0,25–0,50–0,25 varyans örneği, −5–5–15 ve 0–5–10 getirileri, 0,30–0,20–0,10–0,40
ortak tablosu, 0,60–0,40–0,24 bağımsızlık hücresi, Π = 400X − 500, destek talebi dağılımı); yeni sayılarla ve yeni
bağlamlarla aynı becerileri sınar. Binom, Poisson ve hipergeometrik dağılımlar bir sonraki konunun konusudur; bu
sette kullanılmaz.
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


JOINT_2X2 = (
    "İki rassal değişkenin ortak olasılıkları: P(X = 0, Y = 0) = 0,20, P(X = 0, Y = 1) = 0,10, "
    "P(X = 1, Y = 0) = 0,30, P(X = 1, Y = 1) = 0,40."
)

QUESTIONS = (
    # --- Çoktan seçmeli -----------------------------------------------------------
    Question(
        key="k01", concept="surekli-rassal-degisken-secimi", note=_note("8.2", "Şekil 8.2"),
        prompt="Aşağıdakilerden hangisi sürekli bir rassal değişkendir?",
        answer=MultipleChoice(
            (
                "Bir kasada bir saatte işlem gören müşteri sayısı",
                "Bir öğrencinin 20 soruluk testte yaptığı hata sayısı",
                "Bir teslimatın dakika cinsinden süresi",
                "Bir ailedeki çocuk sayısı",
            ),
            correct=2,
        ),
        explanation=(
            "Süre bir aralıktaki her değeri alabilir (ör. 12,7 dakika): süreklidir. Müşteri, hata ve çocuk sayıları "
            "\"kaç tane?\" sorusuna cevap veren sayımlardır ve kesiklidir (§8.2, Şekil 8.2)."
        ),
    ),
    Question(
        key="k02", concept="olasilik-fonksiyonunu-okumak", note=_note("8.3", "(8.1)"),
        prompt=(
            "Bir kargo firmasında bir paketin teslimi için gereken deneme sayısı X'in dağılımı f(1) = 0,70, "
            "f(2) = 0,20, f(3) = 0,10'dur. Hangisi doğrudur?"
        ),
        answer=MultipleChoice(
            (
                "En olası değer 1'dir: paketlerin %70'i ilk denemede teslim edilir.",
                "En olası değer 3'tür, çünkü en büyük değerdir.",
                "f(2) = 0,20, ikinci denemenin %20 daha uzun sürdüğünü gösterir.",
                "Olasılıklar ondalıklı olduğu için X kesikli olamaz.",
            ),
            correct=0,
        ),
        explanation=(
            "f(x) = P(X = x): f(1) = 0,70 en büyük olasılıktır, en yüksek sütun x = 1'dedir. Kesikliliği "
            "olasılıkların biçimi değil, olası değerlerin (1, 2, 3) ayrı noktalar olması belirler (§8.3, (8.1))."
        ),
    ),
    Question(
        key="k03", concept="iki-yonlu-esitsizlik-olayi", note=_note("8.5", "(8.4)"),
        prompt=(
            "Ek ürün dağılımı f(0) = 0,10, f(1) = 0,30, f(2) = 0,35, f(3) = 0,20, f(4) = 0,05 için "
            "P(1 < X ≤ 3) kaçtır?"
        ),
        answer=MultipleChoice(("0,65", "0,55", "0,90", "0,20"), correct=1),
        explanation=(
            "1 < X ≤ 3 olayı {2, 3} değerlerini içerir: soldaki 1 dahil değildir, sağdaki 3 dahildir. "
            "P = f(2) + f(3) = 0,35 + 0,20 = 0,55. 0,65 = f(1) + f(2) eşitsizlik işaretlerinin yanlış "
            "okunmasıdır (§8.5, (8.4))."
        ),
    ),
    Question(
        key="k04", concept="beklenen-degerin-hesabi", note=_note("8.7", "(8.5)"),
        prompt=(
            "Bir restoranda bir masanın tatlı siparişi sayısı X'in dağılımı f(0) = 0,40, f(1) = 0,35, f(2) = 0,20, "
            "f(3) = 0,05'tir. E(X) kaçtır?"
        ),
        answer=MultipleChoice(("1,50", "1", "0,25", "0,90"), correct=3),
        explanation=(
            "E(X) = Σ x f(x) = 0(0,40) + 1(0,35) + 2(0,20) + 3(0,05) = 0,90. 1,50 değerlerin olasılıklar hesaba "
            "katılmadan alınan basit ortalamasıdır; 0,25 olasılıkların ortalamasıdır (§8.7, (8.5))."
        ),
    ),
    Question(
        key="k05", concept="ayni-beklenen-deger-farkli-risk", note=_note("8.10", "Tablo 8.5"),
        prompt=(
            "İki yatırımın yıllık getirisi (%) şöyledir: A kesin olarak %4 getirir; B eşit olasılıkla %−6 ya da %14 "
            "getirir. Hangisi doğrudur?"
        ),
        answer=MultipleChoice(
            (
                "E(B) = 10'dur.",
                "Beklenen değerler eşit olduğu için iki yatırımın riski de eşittir.",
                "E(A) = E(B) = 4; B'nin varyansı 100, A'nınki 0'dır.",
                "Var(B) = 10'dur.",
            ),
            correct=2,
        ),
        explanation=(
            "E(B) = 0,5(−6) + 0,5(14) = 4 = E(A). Var(B) = 0,5(−10)² + 0,5(10)² = 100, σ_B = 10; kesin getirinin "
            "varyansı 0'dır. Aynı beklenen değer farklı belirsizlik taşıyabilir (§8.10, (8.6))."
        ),
    ),
    Question(
        key="k06", concept="korelasyonun-hesabi", note=_note("8.12", "(8.10)"),
        prompt="Cov(X, Y) = 0,12, σ_X = 0,4 ve σ_Y = 0,5 ise ρ_XY kaçtır?",
        answer=MultipleChoice(("0,048", "0,12", "0,24", "0,60"), correct=3),
        explanation=(
            "ρ = Cov(X, Y)/(σ_X σ_Y) = 0,12/(0,4 × 0,5) = 0,60. Kovaryans ölçü birimlerine bağlıdır; standart "
            "sapmalara bölünen korelasyon birimsizdir ve −1 ile 1 arasında kalır (§8.12, (8.10))."
        ),
    ),
    Question(
        key="k07", concept="sistematik-cozumde-gecerlilik-adimi", note=_note("8.15", "Şekil 8.15"),
        prompt=(
            "Şekil 8.15'teki çözüm sırasına göre, E(X) ya da Var(X) hesaplanmadan hemen önce hangi adım gelir?"
        ),
        answer=MultipleChoice(
            (
                "Sonucu bağlam ve ölçü birimiyle yorumlamak",
                "Rassal değişkeni tanımlamak",
                "Geçerlilik koşullarını kontrol etmek",
                "Olasılıkları 100 ile çarpmak",
            ),
            correct=2,
        ),
        explanation=(
            "Sıra: rassal değişkeni tanımla → olası değerleri belirle → f(x)'i yaz → geçerlilik koşullarını "
            "(f(x) ≥ 0, Σ f(x) = 1) kontrol et → E(X), Var(X) ya da ortak dağılım özetini hesapla → yorumla. "
            "Geçersiz bir tabloyla hesaplanan beklenen değer anlamsızdır (§8.15, Şekil 8.15)."
        ),
    ),
    # --- Doğru–yanlış -------------------------------------------------------------
    Question(
        key="d01", concept="kodlanmis-degerlerin-anlami", note=_note("8.1"),
        prompt=(
            "Kredi başvurusu onaylanınca X = 1, reddedilince X = 0 yazılırsa, 1 değeri 0'dan bir birim daha büyük "
            "bir ekonomik sonucu gösterir."
        ),
        answer=TrueFalse(False),
        explanation=(
            "0 ve 1 burada iki sonucu kodlar: rassal değişken deney sonucunu sayısal dile çevirir, ama bu sayılar "
            "arasındaki fark bir ekonomik büyüklük değildir. X'in neyi ölçtüğü açıkça tanımlanmalıdır (§8.1)."
        ),
    ),
    Question(
        key="d02", concept="toplam-bir-tek-basina-yetmez", note=_note("8.4", "Şekil 8.4"),
        prompt=(
            "f(0) = 0,5, f(1) = 0,7 ve f(2) = −0,2 değerleri geçerli bir olasılık fonksiyonu oluşturur, çünkü "
            "toplamları 1'dir."
        ),
        answer=TrueFalse(False),
        explanation=(
            "Geçerlilik iki koşulu birlikte ister: her f(x) ≥ 0 ve Σ f(x) = 1. Toplam 1 olsa da f(2) < 0 olduğu "
            "için tablo geçersizdir; Şekil 8.4'teki sağdaki örnek de böyledir (§8.4, (8.2), (8.3))."
        ),
    ),
    Question(
        key="d03", concept="orneklem-ortalamasi-beklenen-deger-degildir", note=_note("8.8", "Şekil 8.8"),
        prompt=(
            "Şekil 8.8'deki 100 çekilişin ortalaması 1,77 olduğuna göre Tablo 8.1'deki dağılımın beklenen değeri "
            "1,77'dir."
        ),
        answer=TrueFalse(False),
        explanation=(
            "Beklenen değer dağılımdan hesaplanır: E(X) = Σ x f(x) = 1,80. 1,77 tek bir 100 çekilişlik simülasyonun "
            "ortalamasıdır; başka tekrarlar farklı yollar izler ve ortalama uzun dönemde 1,80 çevresinde istikrar "
            "kazanır (§8.8, Şekil 8.8)."
        ),
    ),
    Question(
        key="d04", concept="tek-degerli-dagilimin-varyansi", note=_note("8.9", "(8.6)"),
        prompt="Bir rassal değişken olasılık 1 ile tek bir değer alıyorsa (ör. P(X = 5) = 1) varyansı 0'dır.",
        answer=TrueFalse(True),
        explanation=(
            "Var(X) = Σ (x − μ)² f(x): tek değer 5 ise μ = 5 ve tek sapma 0'dır. Varyans olası değerlerin merkezden "
            "uzaklığını ölçer; yayılım yoksa sıfırdır (§8.9, (8.6))."
        ),
    ),
    Question(
        key="d05", concept="mantiksal-kisittan-gelen-sifir-hucre", note=_note("8.11", "Tablo 8.6"),
        prompt=(
            "Tablo 8.6'da P(X = 0, Y = 1) = 0 olması, bu (x, y) çiftinin mantıksal olarak imkânsız olmasından "
            "kaynaklanır."
        ),
        answer=TrueFalse(True),
        explanation=(
            "Y, teklif taleplerinden satışa dönüşenlerin sayısıdır ve X'i aşamaz: Y > X olan (0, 1), (0, 2) ve "
            "(1, 2) hücreleri mantıksal kısıt nedeniyle 0'dır. Hiç teklif talebi yokken satış gerçekleşemez "
            "(§8.11, Tablo 8.6)."
        ),
    ),
    Question(
        key="d06", concept="bagimsizlik-hucre-kontrolu", note=_note("8.13", "(8.11)"),
        prompt=(
            "P(X = 0) = 0,3, P(Y = 0) = 0,5 ve P(X = 0, Y = 0) = 0,25 ise bu hücre bağımsızlık koşulunu sağlar."
        ),
        answer=TrueFalse(False),
        explanation=(
            "Bağımsızlıkta her hücrede P(X = x, Y = y) = P(X = x)P(Y = y) olmalıdır: 0,3 × 0,5 = 0,15 ≠ 0,25. Tek "
            "bir hücrede eşitliğin bozulması X ile Y'nin bağımsız olmadığını gösterir (§8.13, (8.11))."
        ),
    ),
    Question(
        key="d07", concept="donusumde-olasiliklar-tasinir", note=_note("8.14", "Tablo 8.7"),
        prompt=(
            "Π = 300X − 250 dönüşümünde, Π'nin her olası değerinin olasılığı X'in karşılık gelen değerinin "
            "olasılığına eşittir."
        ),
        answer=TrueFalse(True),
        explanation=(
            "Her x değeri tek bir kâr değerine karşılık gelir: X = 2 ise Π = 350 olur, bu nedenle "
            "P(Π = 350) = P(X = 2) = 0,35. Kâr dağılımı talep dağılımının olasılıklarını taşır (§8.14, Tablo 8.7)."
        ),
    ),
    # --- Boşluk doldurma ----------------------------------------------------------
    Question(
        key="b01", concept="gunlerden-ampirik-dagilim", note=_note("8.6", "Tablo 8.2"),
        prompt=(
            "Bir dükkânda 250 günün 45'inde hiç iade gelmemiş, 110'unda 1, 70'inde 2 ve 25'inde 3 iade gelmiştir. "
            "X = \"günlük iade sayısı\" için ampirik dağılımda f(1) = **(1)** ve P(X ≥ 2) = **(2)** olur."
        ),
        answer=FillBlanks((NumberBlank(0.44, 0.0005, "0,44"), NumberBlank(0.38, 0.0005, "0,38"))),
        explanation=(
            "Göreli frekans = gün sayısı/250: f(1) = 110/250 = 0,44. X ≥ 2 olayı 2 ve 3 değerlerini içerir: "
            "(70 + 25)/250 = 0,38. Olasılıkların toplamı 250/250 = 1'dir (§8.6, Tablo 8.2)."
        ),
    ),
    Question(
        key="b02", concept="beklenen-deger-ve-varyans-hesabi", note=_note("8.9", "Tablo 8.4"),
        prompt=(
            "X; 1, 3 ve 5 değerlerini 0,2, 0,5 ve 0,3 olasılıklarıyla alıyor. E(X) = **(1)**, Var(X) = **(2)** "
            "olur."
        ),
        answer=FillBlanks((NumberBlank(3.2, 0.0005, "3,2"), NumberBlank(1.96, 0.0005, "1,96"))),
        explanation=(
            "E(X) = 1(0,2) + 3(0,5) + 5(0,3) = 3,2. Var(X) = (1 − 3,2)²(0,2) + (3 − 3,2)²(0,5) + (5 − 3,2)²(0,3) "
            "= 0,968 + 0,020 + 0,972 = 1,96; σ = 1,4 (§8.9, (8.6))."
        ),
    ),
    Question(
        key="b03", concept="ortak-tablodan-marjinaller", note=_note("8.11", "Tablo 8.6"),
        prompt=f"{JOINT_2X2} P(X = 1) = **(1)** ve P(Y = 1) = **(2)** olur.",
        answer=FillBlanks((NumberBlank(0.70, 0.0005, "0,70"), NumberBlank(0.50, 0.0005, "0,50"))),
        explanation=(
            "Marjinal olasılık ilgili satır ya da sütundaki ortak olasılıkların toplamıdır: "
            "P(X = 1) = 0,30 + 0,40 = 0,70; P(Y = 1) = 0,10 + 0,40 = 0,50 (§8.11, Tablo 8.6)."
        ),
    ),
    Question(
        key="b04", concept="ortak-dagilimdan-beklenen-degerler", note=_note("8.12", "(8.9)"),
        prompt=f"{JOINT_2X2} E(X) = **(1)** ve E(XY) = **(2)** olur.",
        answer=FillBlanks((NumberBlank(0.70, 0.0005, "0,70"), NumberBlank(0.40, 0.0005, "0,40"))),
        explanation=(
            "E(X) = 0 × P(X = 0) + 1 × P(X = 1) = 0,70. XY yalnız X = 1, Y = 1 hücresinde sıfırdan farklıdır: "
            "E(XY) = 1 × 1 × 0,40 = 0,40. Bu iki değer kovaryansın kısa yol formülünde kullanılır (§8.12, (8.9))."
        ),
    ),
    Question(
        key="b05", concept="kar-donusumunde-beklenen-deger", note=_note("8.14", "Tablo 8.7"),
        prompt=(
            "Günlük talep X'in beklenen değeri E(X) = 2,5 birimdir. Birim katkı 200 TL, günlük sabit maliyet 300 TL "
            "olduğundan Π = 200X − 300'dür. E(Π) = **(1)** TL olur; X = 1 olan bir günde kâr **(2)** TL'dir."
        ),
        answer=FillBlanks((NumberBlank(200, 0.005, "200"), NumberBlank(-100, 0.005, "−100"))),
        explanation=(
            "E(aX + b) = aE(X) + b: 200(2,5) − 300 = 200 TL. X = 1 için π = 200 − 300 = −100 TL: beklenen kâr "
            "pozitif olsa da düşük talepli günlerde zarar edilir (§8.14)."
        ),
    ),
    # --- Denklem yazma -----------------------------------------------------------
    Question(
        key="e01", concept="eksik-olasiligi-bulmak", note=_note("8.4", "(8.3)"),
        prompt="X yalnız 0, 1 ve 2 değerlerini alıyor; f(0) = $a$ ve f(1) = $b$ ise f(2)'yi yazın.",
        answer=Equation(
            lhs="f(2)",
            symbols=(Symbol("a", "a", "f(0)", 0.10, 0.40), Symbol("b", "b", "f(1)", 0.10, 0.40)),
            answer="1 - a - b",
            shown="1 - a - b",
        ),
        explanation=(
            "Olasılıkların toplamı 1 olmalıdır: f(0) + f(1) + f(2) = 1 ⇒ f(2) = 1 − a − b. Notlardaki örnekte "
            "P(X = 3) = 1 − (0,20 + 0,35 + 0,30) = 0,15 (§8.4, (8.3))."
        ),
    ),
    Question(
        key="e02", concept="iki-degerli-degiskenin-beklenen-degeri", note=_note("8.7", "(8.5)"),
        prompt="X yalnız $a$ ve $b$ değerlerini sırasıyla $p$ ve 1 − $p$ olasılıklarıyla alıyor. E(X)'i yazın.",
        answer=Equation(
            lhs="E(X)",
            symbols=(
                Symbol("a", "a", "birinci değer", -5, 5),
                Symbol("b", "b", "ikinci değer", 6, 20),
                Symbol("p", "p", "birinci değerin olasılığı", 0.05, 0.95),
            ),
            answer="a*p + b*(1-p)",
            shown="a\\,p + b\\,(1-p)",
        ),
        explanation=(
            "E(X) = Σ x f(x) = ap + b(1 − p): değerler olasılıklarıyla ağırlıklandırılır. p = 0,5 ise basit "
            "ortalamaya (a + b)/2 eşittir; p büyüdükçe beklenen değer a'ya yaklaşır (§8.7, (8.5))."
        ),
    ),
    Question(
        key="e03", concept="simetrik-iki-degerli-varyans", note=_note("8.10", "(8.6)"),
        prompt="X, $m$ − $d$ ve $m$ + $d$ değerlerini 0,5 olasılıkla alıyor. Var(X)'i yazın.",
        answer=Equation(
            lhs="\\operatorname{Var}(X)",
            symbols=(Symbol("m", "m", "merkez", 0, 10), Symbol("d", "d", "merkezden uzaklık", 0.5, 3)),
            answer="d*d",
            shown="d^2",
        ),
        explanation=(
            "E(X) = 0,5(m − d) + 0,5(m + d) = m. İki değer de merkezden d uzaktadır: Var = 0,5d² + 0,5d² = d². "
            "Varyans merkezden bağımsızdır; yayılımı yalnız d belirler (§8.10, (8.6))."
        ),
    ),
    Question(
        key="e04", concept="kovaryansin-kisa-yol-formulu", note=_note("8.12", "(8.9)"),
        prompt="E(XY) = $m$, E(X) = $u$ ve E(Y) = $v$ ise Cov(X, Y)'yi yazın.",
        answer=Equation(
            lhs="\\operatorname{Cov}(X, Y)",
            symbols=(
                Symbol("m", "m", "E(XY)", 0.5, 3),
                Symbol("u", "u", "E(X)", 0.5, 2),
                Symbol("v", "v", "E(Y)", 0.5, 2),
            ),
            answer="m - u*v",
            shown="m - u\\,v",
        ),
        explanation=(
            "Kısa yol formülü: Cov(X, Y) = E(XY) − E(X)E(Y) = m − uv. Tablo 8.6'da 1,45 − (1,15)(0,85) = 0,4725 "
            "(§8.12, (8.9))."
        ),
    ),
    Question(
        key="e05", concept="bagimsizlikta-ortak-olasilik", note=_note("8.13", "(8.11)"),
        prompt="X ile Y bağımsız, P(X = 1) = $a$ ve P(Y = 1) = $b$ ise P(X = 1, Y = 1)'i yazın.",
        answer=Equation(
            lhs="P(X = 1, Y = 1)",
            symbols=(Symbol("a", "a", "P(X = 1)", 0.10, 0.90), Symbol("b", "b", "P(Y = 1)", 0.10, 0.90)),
            answer="a*b",
            shown="a\\,b",
        ),
        explanation=(
            "Bağımsızlıkta ortak olasılık marjinal olasılıkların çarpımıdır: P(X = 1, Y = 1) = ab. Tablo 8.6'da bu "
            "çarpım (0,35)(0,35) = 0,1225 olurdu; ortak olasılık 0,25 olduğu için X ile Y bağımsız değildir "
            "(§8.13, (8.11))."
        ),
    ),
)


KONU08_QUIZ = QuestionSet(
    topic_key="konu08",
    title="Konu 8: Kendini sına",
    questions=QUESTIONS,
    intro=(
        "Bu set haftanın temel kavramlarını sınar. Her soru tek bir kavrama odaklanır ve notlardaki bir "
        "bölüme bağlıdır; yanlış cevaplarınız için tekrar edilecek bölümler en üstte listelenir. Notlardaki "
        "egzersiz ve mini quiz maddelerini tekrar etmez, yeni sayılarla onları tamamlar."
    ),
    sections=tuple(f"8.{number}" for number in range(1, 16)),
)
