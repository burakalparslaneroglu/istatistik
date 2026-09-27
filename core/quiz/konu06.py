"""Konu 6 "Kendini sına" soru seti.

Her soru tek bir kavramı sınar ve notlardaki bir bölüme bağlıdır. Sorular notların Egzersiz 6.1–6.11 ve
Mini Quiz 6.1–6.11 maddelerini tekrar etmez (ör. kredi sözleşmesinde 3 × 2 × 2 bileşim, 6 projeden 2 seçim,
8 üründen 3 seçim, faturada hata olasılığı 0,07, %45–%30–%18 haber anketi, 4! kaçtır); yeni sayılarla ve yeni
bağlamlarla aynı becerileri sınar. Koşullu olasılık, bağımsızlık ve çarpma kuralı bir sonraki konunun
konusudur; bu sette kullanılmaz.
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
        key="k01", concept="yuzde-ve-olasilik", note=_note("6.1", "(6.1)"),
        prompt="Bir ürünün iade edilme olasılığı %4 olarak verilmiştir. Hangisi aynı bilgiyi ifade eder?",
        answer=MultipleChoice(("P(iade) = 4", "P(iade) = 0,4", "P(iade) = 0,04", "P(iade) = 0,96"), correct=2),
        explanation=(
            "Olasılık 0 ile 1 arasındadır; yüzde 100 ile çarpılmış yazımdır: %4 = 4/100 = 0,04. 0,96 iade "
            "edilmeme olasılığıdır (§6.1, (6.1))."
        ),
    ),
    Question(
        key="k02", concept="tekrarli-secimde-carpim-kurali", note=_note("6.3", "(6.3)"),
        prompt=(
            "Bir müşteri kodu 29 harfli alfabeden 2 harf ve ardından 3 rakamdan oluşur; harf ve rakamlar tekrar "
            "edebilir. Kaç farklı kod oluşturulabilir?"
        ),
        answer=MultipleChoice(("841.000", "584.640", "290", "39"), correct=0),
        explanation=(
            "Beş aşama vardır: 29, 29, 10, 10 ve 10 seçenek. Çarpım kuralıyla 29 × 29 × 10 × 10 × 10 = 841.000. "
            "584.640 tekrar yasak olsaydı bulunurdu: 29 × 28 × 10 × 9 × 8 (§6.3, (6.3))."
        ),
    ),
    Question(
        key="k03", concept="kombinasyon-simetrisi", note=_note("6.4", "(6.5)"),
        prompt="10 kişiden 3 kişilik bir komisyon seçmenin yol sayısı C(10, 3) hangisine eşittir?",
        answer=MultipleChoice(("P(10, 3)", "C(10, 7)", "10 × 3", "3!"), correct=1),
        explanation=(
            "3 kişiyi seçmek, dışarıda kalacak 7 kişiyi seçmekle aynıdır: C(10, 3) = 10!/(3! 7!) = C(10, 7) = 120. "
            "P(10, 3) = 720 görev sırasını da sayar (§6.4, (6.5))."
        ),
    ),
    Question(
        key="k04", concept="goreli-frekansin-istikrari", note=_note("6.5", "Şekil 6.6"),
        prompt="Göreli frekans yöntemiyle bulunan bir olasılık tahmini için hangisi doğrudur?",
        answer=MultipleChoice(
            (
                "İlk 10 gözlemdeki oran uzun dönem oranına her zaman eşittir.",
                "Gözlem sayısı arttıkça oran gerçek olasılıktan uzaklaşır.",
                "Göreli frekans yalnız eşit olasılıklı sonuçlar için kullanılabilir.",
                "Az gözlemde oran belirgin biçimde oynar; gözlem arttıkça daha istikrarlı bir düzeye yaklaşır.",
            ),
            correct=3,
        ),
        explanation=(
            "Şekil 6.6'da oran ilk dokuz işlemde 0, 20–30 işlem arasında 0,20 civarında, 100 işlemde 0,16'dır; "
            "gerçek olasılık 0,15. Göreli frekans geçmiş tekrarlardan gelen bir tahmindir (§6.5, Şekil 6.6)."
        ),
    ),
    Question(
        key="k05", concept="yalniz-biri-olayi", note=_note("6.8"),
        prompt=(
            "Adil bir zar atılıyor. A = {2, 4, 6} ve B = {4, 5, 6} olsun. \"A veya B gerçekleşir ama ikisi birden "
            "gerçekleşmez\" olayı hangisidir?"
        ),
        answer=MultipleChoice(("{2, 4, 5, 6}", "{4, 6}", "{2, 5}", "{1, 3}"), correct=2),
        explanation=(
            "A ∪ B = {2, 4, 5, 6}, A ∩ B = {4, 6}. \"Yalnız biri\" birleşimden kesişimin çıkarılmasıdır: {2, 5}. "
            "Olasılıkta \"veya\" kapsayıcıdır; \"yalnız biri\" ayrıca belirtilmelidir (§6.8)."
        ),
    ),
    Question(
        key="k06", concept="ayrik-olaylarda-toplama", note=_note("6.9", "(6.14)"),
        prompt=(
            "Bir siparişin ödemesi kart, nakit veya havaleyle yapılır ve tek bir yöntem seçilir. P(kart) = 0,55 ve "
            "P(nakit) = 0,30 ise P(kart veya nakit) kaçtır?"
        ),
        answer=MultipleChoice(("0,85", "0,165", "0,25", "0,70"), correct=0),
        explanation=(
            "Tek bir siparişte kart ve nakit aynı anda seçilemez: olaylar ayrıktır ve P(kart ∩ nakit) = 0. Toplama "
            "kuralı sadeleşir: 0,55 + 0,30 = 0,85 (§6.9, (6.14))."
        ),
    ),
    Question(
        key="k07", concept="sistematik-cozumde-ilk-adim", note=_note("6.11", "Şekil 6.13"),
        prompt="Bir olasılık problemini çözerken önerilen ilk adım hangisidir?",
        answer=MultipleChoice(
            (
                "Rassal deneyi tanımlamak",
                "Toplama kuralını uygulamak",
                "Kombinasyon formülünü seçmek",
                "Sonucu yüzdeye çevirmek",
            ),
            correct=0,
        ),
        explanation=(
            "Önerilen sıra: deneyi tanımla → örnek uzayı belirle → olayları küme olarak yaz → kuralı seç → sonucu "
            "yorumla. İlk işin formül seçmek olması hesap hatalarının sık kaynağıdır (§6.11, Şekil 6.13)."
        ),
    ),
    # --- Doğru–yanlış -------------------------------------------------------------
    Question(
        key="d01", concept="yari-olasilik", note=_note("6.1", "Şekil 6.1"),
        prompt="P(A) = 0,50 ise A'nın gerçekleşmesi ile gerçekleşmemesi aynı olasılık düzeyindedir.",
        answer=TrueFalse(True),
        explanation=(
            "P(A) = 0,50 ise P(A'nın gerçekleşmemesi) = 1 − 0,50 = 0,50'dir; olasılık ölçeğinin tam ortasıdır. "
            "Bu, tek bir denemede sonucun ne olacağını söylemez (§6.1)."
        ),
    ),
    Question(
        key="d02", concept="olasi-deger-esit-olasilikli-degil", note=_note("6.2"),
        prompt="İki zar atıldığında 11 farklı toplam mümkün olduğu için her toplamın olasılığı 1/11'dir.",
        answer=TrueFalse(False),
        explanation=(
            "Toplamlar eşit sayıda temel sonuçla oluşmaz: 2 yalnız (1, 1) ile, 7 altı zar çiftiyle oluşur. Eşit "
            "olasılıklı olan 36 zar çiftidir; P(toplam 7) = 6/36 (§6.2)."
        ),
    ),
    Question(
        key="d03", concept="carpim-kurali-toplama-degil", note=_note("6.3", "(6.3)"),
        prompt="Üç aşamalı bir deneyde aşamaların seçenek sayıları 2, 3 ve 4 ise olası sonuç sayısı 2 + 3 + 4 = 9'dur.",
        answer=TrueFalse(False),
        explanation=(
            "Her aşamanın her seçeneği sonraki aşamanın her seçeneğiyle birleşir: sonuç sayısı 2 × 3 × 4 = 24. "
            "Ağaç diyagramında her tam dal bir sonuçtur (§6.3, (6.3))."
        ),
    ),
    Question(
        key="d04", concept="permutasyon-kombinasyon-iliskisi", note=_note("6.4", "(6.5)", "(6.6)"),
        prompt="Aynı N ve n için P(N, n) = n! × C(N, n) eşitliği geçerlidir.",
        answer=TrueFalse(True),
        explanation=(
            "Her n kişilik grup n! farklı sırayla dizilebilir. P(N, n) = N!/(N − n)! = n! × N!/(n!(N − n)!). "
            "Notlardaki örnekte P(5, 2) = 20 = 2! × 10 (§6.4)."
        ),
    ),
    Question(
        key="d05", concept="sayma-orani-esit-olasilik-ister", note=_note("6.6", "(6.10)"),
        prompt=(
            "Örnek noktaları eşit olasılıklı olmayan bir deneyde de P(A), A'daki örnek nokta sayısının toplam örnek "
            "nokta sayısına bölümüyle bulunur."
        ),
        answer=TrueFalse(False),
        explanation=(
            "Sayma oranı yalnız eşit olasılıklı örnek noktalarda geçerlidir. Genel kural olaydaki örnek noktaların "
            "olasılıklarını toplamaktır: Tablo 6.2'de P(Z) = 0,70 + 0,08 = 0,78, 2/4 değil (§6.6)."
        ),
    ),
    Question(
        key="d06", concept="tumleyen-karsilastirmasi", note=_note("6.7", "(6.12)"),
        prompt="P(Aᶜ) değeri P(A)'dan büyükse P(A) < 0,50'dir.",
        answer=TrueFalse(True),
        explanation=(
            "P(Aᶜ) = 1 − P(A) olduğundan 1 − P(A) > P(A) eşitsizliği P(A) < 0,50 demektir. Tümleyen kuralı iki "
            "olasılığı birbirine bağlar (§6.7, (6.12))."
        ),
    ),
    Question(
        key="d07", concept="ortak-tablonun-satir-toplami", note=_note("6.10", "Tablo 6.2"),
        prompt=(
            "Ortak olasılık tablosunda bir satırın toplamı, o satırın gösterdiği olayın (ör. \"zamanında\") "
            "olasılığıdır."
        ),
        answer=TrueFalse(True),
        explanation=(
            "Satırdaki hücreler o olayın örnek noktalarıdır; olasılıkları toplanınca olayın olasılığı bulunur. "
            "Tablo 6.2'de zamanında satırı 0,70 + 0,08 = 0,78 (§6.10)."
        ),
    ),
    # --- Boşluk doldurma ----------------------------------------------------------
    Question(
        key="b01", concept="kombinasyon-ve-permutasyon-hesabi", note=_note("6.4", "(6.5)", "(6.6)"),
        prompt=(
            "7 kişiden 3 kişilik bir çalışma grubu **(1)** farklı biçimde seçilebilir; aynı 7 kişiden başkan, "
            "yardımcı ve sekreter **(2)** farklı biçimde seçilebilir."
        ),
        answer=FillBlanks((NumberBlank(35, 0.005, "35"), NumberBlank(210, 0.005, "210"))),
        explanation=(
            "Grup için sıra önemsiz: C(7, 3) = 7!/(3! 4!) = 35. Görevler farklı olduğu için sıra önemli: "
            "P(7, 3) = 7 × 6 × 5 = 210 = 3! × 35 (§6.4)."
        ),
    ),
    Question(
        key="b02", concept="iki-zarda-olay-olasiligi", note=_note("6.6", "(6.10)"),
        prompt=(
            "İki adil zar atılıyor. \"Toplam 9\" olayında **(1)** örnek nokta vardır; olayın olasılığı üç "
            "ondalıkla **(2)** olur."
        ),
        answer=FillBlanks((NumberBlank(4, 0.005, "4"), NumberBlank(4 / 36, 0.0015, "0,111"))),
        explanation=(
            "Toplamı 9 olan zar çiftleri (3, 6), (4, 5), (5, 4), (6, 3). 36 zar çifti eşit olasılıklı olduğundan "
            "P = 4/36 ≈ 0,111 (§6.6, §6.2)."
        ),
    ),
    Question(
        key="b03", concept="gecmis-veriden-olasilik", note=_note("6.5"),
        prompt=(
            "Geçmiş 400 siparişin 36'sı iade edilmiştir. Göreli frekans yöntemiyle P(iade) ≈ **(1)**; iade edilmeme "
            "olasılığı ≈ **(2)** olur."
        ),
        answer=FillBlanks((NumberBlank(0.09, 0.0005, "0,09"), NumberBlank(0.91, 0.0005, "0,91"))),
        explanation=(
            "Göreli frekans 36/400 = 0,09; tümleyen kuralıyla 1 − 0,09 = 0,91. Tahmin geçmiş tekrarlar aynı "
            "süreçten geldiği ölçüde anlamlıdır (§6.5, §6.7)."
        ),
    ),
    Question(
        key="b04", concept="toplama-kuralindan-kesisim", note=_note("6.9", "(6.13)"),
        prompt=(
            "P(A) = 0,50, P(B) = 0,40 ve P(A ∪ B) = 0,70'tir. P(A ∩ B) = **(1)**; yalnız A'nın gerçekleşme "
            "olasılığı **(2)** olur."
        ),
        answer=FillBlanks((NumberBlank(0.20, 0.0005, "0,20"), NumberBlank(0.30, 0.0005, "0,30"))),
        explanation=(
            "Toplama kuralından P(A ∩ B) = P(A) + P(B) − P(A ∪ B) = 0,50 + 0,40 − 0,70 = 0,20. Yalnız A: "
            "P(A) − P(A ∩ B) = 0,30. Kesişim sıfır olmadığı için A ve B ayrık değildir (§6.9, (6.13))."
        ),
    ),
    Question(
        key="b05", concept="ortak-tablodan-birlesim", note=_note("6.10", "Tablo 6.2"),
        prompt=(
            "Bir tedarikçide ortak olasılıklar: zamanında–hatasız 0,60, zamanında–hatalı 0,10, geç–hatasız 0,25, "
            "geç–hatalı 0,05. P(hatalı) = **(1)**, P(geç veya hatalı) = **(2)** olur."
        ),
        answer=FillBlanks((NumberBlank(0.15, 0.0005, "0,15"), NumberBlank(0.40, 0.0005, "0,40"))),
        explanation=(
            "P(hatalı) = 0,10 + 0,05 = 0,15; P(geç) = 0,25 + 0,05 = 0,30. Toplama kuralıyla 0,30 + 0,15 − 0,05 = "
            "0,40; tümleyen kontrolü: 1 − P(zamanında ve hatasız) = 1 − 0,60 = 0,40 (§6.10)."
        ),
    ),
    # --- Denklem yazma -----------------------------------------------------------
    Question(
        key="e01", concept="uc-asamali-sonuc-sayisi", note=_note("6.3", "(6.3)"),
        prompt="Üç aşamalı bir deneyde aşamaların seçenek sayıları $a$, $b$ ve $c$ ise olası sonuç sayısını yazın.",
        answer=Equation(
            lhs="N_{\\text{sonuç}}",
            symbols=(
                Symbol("a", "a", "birinci aşamanın seçenek sayısı", 1, 6),
                Symbol("b", "b", "ikinci aşamanın seçenek sayısı", 1, 6),
                Symbol("c", "c", "üçüncü aşamanın seçenek sayısı", 1, 6),
            ),
            answer="a*b*c",
            shown="a\\,b\\,c",
        ),
        explanation=(
            "Çarpım kuralı: N = n₁ n₂ ⋯ n_k. Ürün örneğinde 4 renk × 3 kapasite × 2 garanti = 24 bileşim "
            "(§6.3, (6.3))."
        ),
    ),
    Question(
        key="e02", concept="n-kisiden-ikili-grup", note=_note("6.4", "(6.5)"),
        prompt="$N$ kişiden sıra önemsiz olarak 2 kişi seçmenin yol sayısını $N$ cinsinden yazın.",
        answer=Equation(
            lhs="\\binom{N}{2}",
            symbols=(Symbol("N", "N", "kişi sayısı", 3, 30),),
            answer="N*(N-1)/2",
            shown="N\\,(N-1)/2",
        ),
        explanation=(
            "C(N, 2) = N!/(2!(N − 2)!) = N(N − 1)/2: birinci kişi N, ikinci N − 1 yoldan seçilir; her grup iki "
            "sırayla sayıldığı için 2'ye bölünür. N = 5 için 10 (§6.4, (6.5))."
        ),
    ),
    Question(
        key="e03", concept="toplama-kurali-formulu", note=_note("6.9", "(6.13)"),
        prompt="P(A) = $a$, P(B) = $b$ ve P(A ∩ B) = $c$ ise P(A ∪ B)'yi yazın.",
        answer=Equation(
            lhs="P(A \\cup B)",
            symbols=(
                Symbol("a", "a", "P(A)", 0.3, 0.5),
                Symbol("b", "b", "P(B)", 0.3, 0.5),
                Symbol("c", "c", "P(A ∩ B)", 0.0, 0.2),
            ),
            answer="a + b - c",
            shown="a + b - c",
        ),
        explanation=(
            "Ortak kısım P(A) ve P(B)'de iki kez sayılır; bir kez çıkarılır. Excel–Python örneğinde "
            "0,40 + 0,35 − 0,15 = 0,60 (§6.9, (6.13))."
        ),
    ),
    Question(
        key="e04", concept="tumleyen-ile-fark", note=_note("6.7", "(6.12)"),
        prompt="P(A) = $p$ ise P(Aᶜ) − P(A) farkını $p$ cinsinden yazın.",
        answer=Equation(
            lhs="P(A^c) - P(A)",
            symbols=(Symbol("p", "p", "P(A)", 0.05, 0.95),),
            answer="1 - 2*p",
            shown="1 - 2p",
        ),
        explanation=(
            "P(Aᶜ) = 1 − p olduğundan fark (1 − p) − p = 1 − 2p. p = 0,12 (gecikme) için zamanında gelme "
            "olasılığı gecikmeninkinden 0,76 fazladır (§6.7, (6.12))."
        ),
    ),
    Question(
        key="e05", concept="yalniz-a-olasiligi", note=_note("6.8"),
        prompt="P(A) = $a$ ve P(A ∩ B) = $c$ ise \"A gerçekleşir ama B gerçekleşmez\" olayının olasılığını yazın.",
        answer=Equation(
            lhs="P(\\text{yalnız } A)",
            symbols=(Symbol("a", "a", "P(A)", 0.3, 0.6), Symbol("c", "c", "P(A ∩ B)", 0.0, 0.25)),
            answer="a - c",
            shown="a - c",
        ),
        explanation=(
            "A'nın örnek noktaları iki gruba ayrılır: B'de olanlar (A ∩ B) ve olmayanlar. Olasılıklar toplandığı "
            "için P(yalnız A) = P(A) − P(A ∩ B). Excel–Python örneğinde 0,40 − 0,15 = 0,25 (§6.8, §6.6)."
        ),
    ),
)


KONU06_QUIZ = QuestionSet(
    topic_key="konu06",
    title="Konu 6: Kendini sına",
    questions=QUESTIONS,
    intro=(
        "Bu set haftanın temel kavramlarını sınar. Her soru tek bir kavrama odaklanır ve notlardaki bir "
        "bölüme bağlıdır; yanlış cevaplarınız için tekrar edilecek bölümler en üstte listelenir. Notlardaki "
        "egzersiz ve mini quiz maddelerini tekrar etmez, yeni sayılarla onları tamamlar."
    ),
    sections=tuple(f"6.{number}" for number in range(1, 12)),
)
