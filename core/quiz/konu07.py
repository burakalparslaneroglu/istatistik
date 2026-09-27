"""Konu 7 "Kendini sına" soru seti.

Her soru tek bir kavramı sınar ve notlardaki bir bölüme bağlıdır. Sorular notların Egzersiz 7.1–7.13 ve Mini Quiz
7.1–7.13 maddelerini tekrar etmez (ör. 500 çalışan ve sertifika, mobil bankacılık ve fatura talimatı, iktisat
öğrencileri ve istatistik seçmelisi, %70 ilk temsilci ve %85 çözüm, A–B fabrikaları %3–%5, üç dağıtım merkezi,
%5 kusurlu ve %10 yanlış işaret, üyeler ve kampanya); yeni sayılarla ve yeni bağlamlarla aynı becerileri sınar.
Rassal değişken ve beklenen değer bir sonraki konunun konusudur; bu sette kullanılmaz.
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
        key="k01", concept="kosulun-ilgili-grubu-daraltmasi", note=_note("7.1", "Şekil 7.1"),
        prompt=(
            "Bir kütüphanenin 800 üyesinin 300'ü öğrencidir. Öğrenci üyelerin 120'si, bütün üyelerin 200'ü bu ay "
            "kitap ödünç almıştır. Üyenin öğrenci olduğu biliniyorsa bu ay kitap ödünç almış olma olasılığı "
            "kaçtır?"
        ),
        answer=MultipleChoice(("120/800 = 0,15", "200/800 = 0,25", "120/300 = 0,40", "120/200 = 0,60"), correct=2),
        explanation=(
            "\"Öğrenci\" bilgisi ilgili grubu 300 öğrenci üyeye daraltır; bu grubun 120'si ödünç almıştır: "
            "120/300 = 0,40. 120/200 = 0,60 ters yöndeki koşuldur (ödünç alanlar içinde öğrenci payı), 200/800 ise "
            "koşulsuz olasılıktır (§7.1, Şekil 7.1)."
        ),
    ),
    Question(
        key="k02", concept="kosul-yonunun-sozel-okunusu", note=_note("7.4", "Şekil 7.4"),
        prompt=(
            "Bir sigorta şirketinde H = \"hasar bildirdi\" ve G = \"genç sürücü\" olmak üzere P(H | G) = 0,08 "
            "verilmiştir. Hangi cümle bu olasılığı doğru okur?"
        ),
        answer=MultipleChoice(
            (
                "Hasar bildirenlerin %8'i genç sürücüdür.",
                "Genç sürücülerin %8'i hasar bildirmiştir.",
                "Sürücülerin %8'i hem genç hem hasar bildirmiştir.",
                "Sürücülerin %8'i genç sürücüdür.",
            ),
            correct=1,
        ),
        explanation=(
            "Dikey çizginin sağındaki olay (G) karşılaştırma grubudur: genç sürücüler içinde hasar bildirenlerin "
            "oranı. İlk seçenek P(G | H), üçüncüsü P(G ∩ H), dördüncüsü P(G)'yi okur (§7.4, Şekil 7.4)."
        ),
    ),
    Question(
        key="k03", concept="ayrik-olayda-kosullu-olasilik", note=_note("7.6", "Tablo 7.3"),
        prompt=(
            "Bir derste her öğrenci tek bir harf notu alır; P(AA) = 0,15 ve P(BA) = 0,25'tir. Bir öğrencinin AA "
            "aldığı biliniyorsa BA almış olma olasılığı P(BA | AA) kaçtır?"
        ),
        answer=MultipleChoice(("0,25", "0,0375", "0", "0,40"), correct=2),
        explanation=(
            "AA ve BA ayrık olaylardır: aynı öğrenci ikisini birden alamaz, P(AA ∩ BA) = 0. Dolayısıyla "
            "P(BA | AA) = 0/0,15 = 0. Bu, P(BA) = 0,25'ten farklı olduğu için olaylar bağımlıdır; 0,0375 bağımsızlık "
            "varsayılarak bulunan çarpımdır (§7.6, Tablo 7.3)."
        ),
    ),
    Question(
        key="k04", concept="agacta-yolun-ortak-olasiligi", note=_note("7.8", "Şekil 7.8"),
        prompt=(
            "Bir e-ticaret sitesinde siparişlerin %40'ı kampanyalıdır. Kampanyalı siparişlerin %15'i, kampanyasız "
            "siparişlerin %5'i iade edilir. Rastgele bir siparişin hem kampanyalı hem iade edilmiş olma olasılığı "
            "kaçtır?"
        ),
        answer=MultipleChoice(("0,06", "0,15", "0,09", "0,55"), correct=0),
        explanation=(
            "Aynı yol üzerindeki dal olasılıkları çarpılır: 0,40 × 0,15 = 0,06. 0,15 yalnız ikinci dalın koşullu "
            "olasılığıdır; 0,09 = 0,06 + 0,60 × 0,05 ise iadeye ulaşan iki yolun toplamı, yani toplam iade "
            "olasılığıdır (§7.8, Şekil 7.8)."
        ),
    ),
    Question(
        key="k05", concept="iki-kaynakli-bayes-hesabi", note=_note("7.10", "(7.7)"),
        prompt=(
            "Bir fabrikada ürünlerin %80'i A hattında, %20'si B hattında üretilir; hatalı ürün oranları A'da %1, "
            "B'de %4'tür. Hatalı olduğu görülen bir ürünün B hattından gelmiş olma olasılığı kaçtır?"
        ),
        answer=MultipleChoice(("0,04", "0,20", "0,008", "0,50"), correct=3),
        explanation=(
            "Ortak olasılıklar 0,80 × 0,01 = 0,008 ve 0,20 × 0,04 = 0,008; toplamları P(H) = 0,016. "
            "P(B | H) = 0,008/0,016 = 0,50: B hattı üretimin yalnız %20'sini yapar, ama hata oranı dört kat olduğu "
            "için hatalı ürünlerin yarısı ondan gelir (§7.10, (7.7))."
        ),
    ),
    Question(
        key="k06", concept="bayes-tablosunda-en-buyuk-sonsal", note=_note("7.11", "Tablo 7.4"),
        prompt=(
            "Bir bilginin üç olası kaynağının önsel olasılıkları 0,60, 0,25 ve 0,15; bilginin bu kaynaklardan "
            "gelme koşullu olasılıkları sırasıyla 0,05, 0,12 ve 0,30'dur. Bilgi gözlendikten sonra sonsal olasılığı "
            "en büyük olan kaynak hangisidir?"
        ),
        answer=MultipleChoice(
            (
                "1. kaynak: önseli en büyük olan",
                "2. kaynak",
                "3. kaynak: ortak olasılığı en büyük olan",
                "1. ve 2. kaynak eşit ve en büyük",
            ),
            correct=2,
        ),
        explanation=(
            "Ortak = önsel × koşullu: 0,60 × 0,05 = 0,030; 0,25 × 0,12 = 0,030; 0,15 × 0,30 = 0,045. Toplam 0,105. "
            "Sonsal olasılıklar ortak olasılıklarla orantılıdır: yaklaşık 0,286, 0,286 ve 0,429. En büyük sonsal, "
            "önseli en küçük olan 3. kaynaktadır (§7.11, Tablo 7.4)."
        ),
    ),
    Question(
        key="k07", concept="soru-turune-gore-arac-secimi", note=_note("7.13", "Tablo 7.6"),
        prompt=(
            "\"Bir müşteri şikâyette bulunduğuna göre hangi şubeden alışveriş yapmış olması en olasıdır?\" sorusu "
            "için temel araç hangisidir?"
        ),
        answer=MultipleChoice(
            ("Toplama kuralı", "Bağımsızlık kontrolü", "Yalnız çarpma kuralı", "Bayes teoremi / Bayes tablosu"),
            correct=3,
        ),
        explanation=(
            "Yeni bilgi (şikâyet) geldikten sonra kaynağın (şube) olasılığı soruluyor; Tablo 7.6'da bu soru türünün "
            "aracı Bayes teoremi ve Bayes tablosudur. Çarpma kuralı yalnız ortak olasılıkları verir; sonra bunlar "
            "kendi toplamları içinde yeniden oranlanır (§7.13, Tablo 7.6)."
        ),
    ),
    # --- Doğru–yanlış -------------------------------------------------------------
    Question(
        key="d01", concept="satirdaki-ortak-olasiliklarin-toplami", note=_note("7.2", "Tablo 7.2"),
        prompt=(
            "Bir 2 × 2 ortak olasılık tablosunun ilk satırındaki hücreler 0,12 ve 0,28; ikinci satırındaki hücreler "
            "0,18 ve 0,42'dir. İlk satırın marjinal olasılığı 0,12'dir."
        ),
        answer=TrueFalse(False),
        explanation=(
            "Marjinal olasılık satırdaki ortak olasılıkların toplamıdır: 0,12 + 0,28 = 0,40. 0,12 tek bir hücrenin "
            "ortak olasılığıdır; dört hücrenin toplamı 1,00'dır (§7.2, Tablo 7.2)."
        ),
    ),
    Question(
        key="d02", concept="kosullu-olasilik-ortak-olasiliktan-kucuk-olamaz", note=_note("7.3", "(7.1)"),
        prompt="P(B) > 0 olduğunda P(A | B) hiçbir zaman P(A ∩ B)'den küçük olamaz.",
        answer=TrueFalse(True),
        explanation=(
            "P(A | B) = P(A ∩ B)/P(B) ve 0 < P(B) ≤ 1 olduğundan bölüm paydan küçük olamaz; P(B) = 1 ise ikisi "
            "eşittir. Mağaza örneğinde 0,18/0,60 = 0,30 > 0,18 (§7.3, (7.1))."
        ),
    ),
    Question(
        key="d03", concept="bagimsizlikta-kosullu-olasilik", note=_note("7.5", "(7.3)"),
        prompt="A ile B bağımsız, P(A) = 0,40 ve P(B) = 0,50 ise P(B | A) = 0,40'tır.",
        answer=TrueFalse(False),
        explanation=(
            "Bağımsızlıkta A bilgisi B'nin olasılığını değiştirmez: P(B | A) = P(B) = 0,50. Koşullu olasılık, koşul "
            "olayının değil sorulan olayın olasılığına eşit kalır; 0,40 = P(A)'dır (§7.5, (7.3))."
        ),
    ),
    Question(
        key="d04", concept="bagimsiz-olaylarda-birlikte-gerceklesme", note=_note("7.7", "(7.6)"),
        prompt="P(A) = 0,5 ve P(B) = 0,4 olan iki bağımsız olayın birlikte gerçekleşme olasılığı 0,9'dur.",
        answer=TrueFalse(False),
        explanation=(
            "Birlikte gerçekleşme kesişimdir; bağımsızlıkta çarpma kuralı P(A ∩ B) = P(A)P(B) = 0,5 × 0,4 = 0,20 "
            "verir. 0,9 olasılıkların toplamıdır ve birleşim için bile doğru değildir: "
            "P(A ∪ B) = 0,5 + 0,4 − 0,20 = 0,70 (§7.7, (7.6))."
        ),
    ),
    Question(
        key="d05", concept="dugumden-cikan-dallarin-toplami", note=_note("7.8", "Şekil 7.8"),
        prompt=(
            "İki aşamalı bir olasılık ağacında, ilk aşamadaki bir düğümden çıkan ikinci aşama dallarının "
            "olasılıklarının toplamı 1'dir."
        ),
        answer=TrueFalse(True),
        explanation=(
            "İkinci aşama dalları, ilk aşamadaki sonuç verildiğinde koşullu olasılıklardır ve o düğümde mümkün bütün "
            "sonuçları kapsar: Şekil 7.8'de standart düğümünden 0,80 + 0,20 = 1, öncelikli düğümünden "
            "0,95 + 0,05 = 1 (§7.8, Şekil 7.8)."
        ),
    ),
    Question(
        key="d06", concept="sonsal-onselden-buyuk-olabilir", note=_note("7.9", "Şekil 7.9"),
        prompt="Bayes hesabında bir kaynağın sonsal olasılığı hiçbir zaman önsel olasılığından büyük olamaz.",
        answer=TrueFalse(False),
        explanation=(
            "Yeni bilgi bir kaynakla daha uyumluysa o kaynağın olasılığı artar: iki tedarikçi örneğinde "
            "P(T₂) = 0,30 iken P(T₂ | K) = 0,5625. Bayes hesabı olasılığı bilgiye göre yukarı ya da aşağı "
            "günceller (§7.9, §7.10)."
        ),
    ),
    Question(
        key="d07", concept="temel-oran-artinca-sonsal", note=_note("7.12", "Şekil 7.12"),
        prompt=(
            "Alarm sisteminin P(A | F) ve P(A | Fᶜ) değerleri aynı kalırken temel oran P(F) artarsa, alarm "
            "verildiğinde işlemin gerçekten sahte olma olasılığı P(F | A) da artar."
        ),
        answer=TrueFalse(True),
        explanation=(
            "P(F | A) = P(F)P(A | F)/[P(F)P(A | F) + P(Fᶜ)P(A | Fᶜ)]: P(F) büyüdükçe gerçek alarm terimi büyür, "
            "yanlış alarm terimi küçülür. Notlardaki sistemde P(F) = 0,02 için 0,269; P(F) = 0,10 için "
            "0,090/(0,090 + 0,045) ≈ 0,667 (§7.12)."
        ),
    ),
    # --- Boşluk doldurma ----------------------------------------------------------
    Question(
        key="b01", concept="sayimdan-ortak-ve-marjinal-olasilik", note=_note("7.2", "Tablo 7.1", "Tablo 7.2"),
        prompt=(
            "Bir otelin 400 misafirinin 240'ı iş seyahatindedir. İş seyahatindeki misafirlerin 60'ı, diğer "
            "misafirlerin 20'si oda servisi kullanmıştır. \"İş seyahatinde ve oda servisi kullandı\" olayının ortak "
            "olasılığı **(1)**, oda servisi kullanmanın marjinal olasılığı **(2)** olur."
        ),
        answer=FillBlanks((NumberBlank(0.15, 0.0005, "0,15"), NumberBlank(0.20, 0.0005, "0,20"))),
        explanation=(
            "Her hücre toplam 400'e bölünür: ortak olasılık 60/400 = 0,15. Marjinal olasılık ilgili sütunun "
            "toplamıdır: (60 + 20)/400 = 0,20 (§7.2, Tablo 7.2)."
        ),
    ),
    Question(
        key="b02", concept="iki-yonde-kosullu-olasilik", note=_note("7.4", "(7.1)", "(7.2)"),
        prompt=(
            "Bir otelin 400 misafirinin 240'ı iş seyahatindedir; iş seyahatindeki 60 misafir ve diğer 20 misafir oda "
            "servisi kullanmıştır. P(oda servisi | iş seyahati) = **(1)**, P(iş seyahati | oda servisi) = **(2)** "
            "olur."
        ),
        answer=FillBlanks((NumberBlank(0.25, 0.0005, "0,25"), NumberBlank(0.75, 0.0005, "0,75"))),
        explanation=(
            "Pay iki yönde de aynı hücredir (60 misafir); payda koşul olayıdır: iş seyahatindeki 240 misafir için "
            "60/240 = 0,25, oda servisi kullanan 80 misafir için 60/80 = 0,75 (§7.4, (7.1), (7.2))."
        ),
    ),
    Question(
        key="b03", concept="carpma-kurali-hesabi", note=_note("7.7", "(7.5)"),
        prompt=(
            "Bir bankada kredi başvurularının %30'u ön onay alır; ön onay alanların %60'ı krediyi kullanır. Rastgele "
            "bir başvurunun ön onay alıp krediyi kullanma olasılığı **(1)**, ön onay alıp krediyi kullanmama "
            "olasılığı **(2)** olur."
        ),
        answer=FillBlanks((NumberBlank(0.18, 0.0005, "0,18"), NumberBlank(0.12, 0.0005, "0,12"))),
        explanation=(
            "Çarpma kuralı: P(O ∩ K) = P(O)P(K | O) = 0,30 × 0,60 = 0,18. Ön onay alanlar içinde kullanmama "
            "olasılığı 1 − 0,60 = 0,40; ortak olasılık 0,30 × 0,40 = 0,12. İki yolun toplamı P(O) = 0,30'dur "
            "(§7.7, (7.5))."
        ),
    ),
    Question(
        key="b04", concept="agacta-toplam-olasilik", note=_note("7.8", "Şekil 7.8"),
        prompt=(
            "Bir fabrikada makinelerin %25'i yeni, %75'i eskidir. Yeni makinelerin %2'si, eski makinelerin %8'i ay "
            "içinde arıza verir. Rastgele bir makinenin arıza verme olasılığı **(1)**, \"eski ve arızasız\" yolunun "
            "ortak olasılığı **(2)** olur."
        ),
        answer=FillBlanks((NumberBlank(0.065, 0.0005, "0,065"), NumberBlank(0.69, 0.0005, "0,69"))),
        explanation=(
            "Arızaya iki yol ulaşır: 0,25 × 0,02 = 0,005 ve 0,75 × 0,08 = 0,060; toplam 0,065. Eski ve arızasız "
            "yol: 0,75 × 0,92 = 0,690. Dört yolun ortak olasılıklarının toplamı 1'dir (§7.8, Şekil 7.8)."
        ),
    ),
    Question(
        key="b05", concept="dogal-frekansla-bayes", note=_note("7.12", "Tablo 7.5"),
        prompt=(
            "Bir taramada kişilerin %1'i hastadır. Test hastaların %95'inde, hasta olmayanların %4'ünde pozitif "
            "sonuç verir. 10.000 kişide beklenen pozitif sonuç sayısı **(1)** olur; pozitif sonuç alan birinin "
            "gerçekten hasta olma olasılığı (üç ondalıkla) **(2)** olur."
        ),
        answer=FillBlanks((NumberBlank(491, 0.005, "491"), NumberBlank(95 / 491, 0.0015, "0,193"))),
        explanation=(
            "Doğal frekanslar: 100 hastanın 95'i, 9900 hasta olmayanın 396'sı pozitif; toplam 491. "
            "P(hasta | pozitif) = 95/491 ≈ 0,193: temel oran düşük olduğu için pozitif sonuçların çoğu yanlış "
            "pozitiftir (§7.12, Tablo 7.5)."
        ),
    ),
    # --- Denklem yazma -----------------------------------------------------------
    Question(
        key="e01", concept="kosullu-olasilik-formulu", note=_note("7.3", "(7.1)"),
        prompt="P(A ∩ B) = $c$ ve P(B) = $b$ ise P(A | B)'yi yazın.",
        answer=Equation(
            lhs="P(A \\mid B)",
            symbols=(
                Symbol("c", "c", "P(A ∩ B)", 0.05, 0.20),
                Symbol("b", "b", "P(B)", 0.30, 0.90),
            ),
            answer="c/b",
            shown="c/b",
        ),
        explanation=(
            "Koşullu olasılık ortak olasılığın koşul olayının olasılığına bölümüdür: P(A | B) = P(A ∩ B)/P(B), "
            "P(B) > 0. Mağaza örneğinde 0,18/0,60 = 0,30 (§7.3, (7.1))."
        ),
    ),
    Question(
        key="e02", concept="yonu-cevirerek-kosullu-olasilik", note=_note("7.4", "(7.1)", "(7.2)"),
        prompt="P(A) = $a$, P(B) = $b$ ve P(A | B) = $p$ ise P(B | A)'yı yazın.",
        answer=Equation(
            lhs="P(B \\mid A)",
            symbols=(
                Symbol("a", "a", "P(A)", 0.30, 0.80),
                Symbol("b", "b", "P(B)", 0.20, 0.60),
                Symbol("p", "p", "P(A | B)", 0.10, 0.50),
            ),
            answer="b*p/a",
            shown="b\\,p/a",
        ),
        explanation=(
            "Pay iki yönde de aynı ortak olasılıktır: P(A ∩ B) = P(B)P(A | B) = bp. Payda artık koşul olayı A'dır: "
            "P(B | A) = bp/a. Mağaza örneğinde P(M | S) = 0,60 × 0,30/0,26 ≈ 0,692 (§7.4, (7.1), (7.2))."
        ),
    ),
    Question(
        key="e03", concept="bagimsizlikta-yalniz-a", note=_note("7.5", "(7.3)", "(7.6)"),
        prompt="A ile B bağımsız, P(A) = $a$ ve P(B) = $b$ ise P(A ∩ Bᶜ)'yi yazın.",
        answer=Equation(
            lhs="P(A \\cap B^c)",
            symbols=(Symbol("a", "a", "P(A)", 0.10, 0.90), Symbol("b", "b", "P(B)", 0.10, 0.90)),
            answer="a*(1-b)",
            shown="a\\,(1-b)",
        ),
        explanation=(
            "A'nın olasılığı B'de olan ve olmayan iki parçaya ayrılır: P(A ∩ Bᶜ) = P(A) − P(A ∩ B). Bağımsızlıkta "
            "P(A ∩ B) = ab olduğundan sonuç a − ab = a(1 − b); yani P(A | Bᶜ) = a ve B bilgisi yine olasılığı "
            "değiştirmez (§7.5, §7.7)."
        ),
    ),
    Question(
        key="e04", concept="iki-kaynakli-bayes-formulu", note=_note("7.10", "(7.7)"),
        prompt="P(A) = $a$, P(B | A) = $p$ ve P(B | Aᶜ) = $q$ ise P(A | B)'yi yazın.",
        answer=Equation(
            lhs="P(A \\mid B)",
            symbols=(
                Symbol("a", "a", "önsel P(A)", 0.10, 0.90),
                Symbol("p", "p", "P(B | A)", 0.05, 0.95),
                Symbol("q", "q", "P(B | Aᶜ)", 0.05, 0.95),
            ),
            answer="a*p/(a*p + (1-a)*q)",
            shown="\\dfrac{a\\,p}{a\\,p + (1-a)\\,q}",
        ),
        explanation=(
            "Pay A'dan B'ye giden yolun ortak olasılığı ap; payda B'ye ulaşan iki yolun toplamı ap + (1 − a)q. "
            "Tedarikçi örneğinde a = 0,30, p = 0,06, q = 0,02 için 0,018/0,032 = 0,5625 (§7.10, (7.7))."
        ),
    ),
    Question(
        key="e05", concept="dogal-frekansta-gercek-alarm-sayisi", note=_note("7.12", "Tablo 7.5"),
        prompt=(
            "$n$ işlemin P(F) = $f$ oranı sahtedir ve alarm sahte işlemlerin P(A | F) = $p$ oranında çalışır. "
            "Beklenen gerçek alarm (sahte ve alarm) sayısını yazın."
        ),
        answer=Equation(
            lhs="\\text{gerçek alarm}",
            symbols=(
                Symbol("n", "n", "işlem sayısı", 1000, 20000),
                Symbol("f", "f", "temel oran P(F)", 0.005, 0.20),
                Symbol("p", "p", "P(A | F)", 0.50, 0.99),
            ),
            answer="n*f*p",
            shown="n\\,f\\,p",
        ),
        explanation=(
            "Önce beklenen sahte işlem sayısı nf, sonra bunların p oranı alarm alır: nfp = n·P(F ∩ A). Notlarda "
            "10.000 × 0,02 × 0,90 = 180 (§7.12, Tablo 7.5)."
        ),
    ),
)


KONU07_QUIZ = QuestionSet(
    topic_key="konu07",
    title="Konu 7: Kendini sına",
    questions=QUESTIONS,
    intro=(
        "Bu set haftanın temel kavramlarını sınar. Her soru tek bir kavrama odaklanır ve notlardaki bir "
        "bölüme bağlıdır; yanlış cevaplarınız için tekrar edilecek bölümler en üstte listelenir. Notlardaki "
        "egzersiz ve mini quiz maddelerini tekrar etmez, yeni sayılarla onları tamamlar."
    ),
    sections=tuple(f"7.{number}" for number in range(1, 14)),
)
