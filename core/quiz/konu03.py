"""Konu 3 "Kendini sına" soru seti.

Her soru tek bir kavramı sınar ve notlardaki bir bölüme bağlıdır. Sorular notların Egzersiz 3.1–3.12 ve
Mini Quiz 3.1–3.12 maddelerini tekrar etmez (ör. yaklaşık sınıf genişliği formülünü sözle sormak, 4 | 7
gibi tek bir yaprağı okumak, ulaşım süresi tablosundan sayım yapmak); yeni sayılarla aynı becerileri sınar.
Sayısal cevaplar testlerde doğrudan hesaplanarak doğrulanır.
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
        key="k01", concept="gecerli-sinif-tanimi", note=_note("3.3"),
        prompt=(
            "Değerleri 3 ile 47 arasında olan tam sayılı bir veri için hangi sınıflandırma eşit genişlikli, "
            "birbirini dışlayan ve bütün gözlemleri kapsayan sınıflar tanımlar?"
        ),
        answer=MultipleChoice(
            (
                "0 ≤ x < 10, 10 ≤ x < 20, 20 ≤ x < 30, 30 ≤ x < 40, 40 ≤ x < 50",
                "0–10, 10–20, 20–30, 30–40, 40–50 (sınırdaki değerin nereye gireceği belirtilmemiş)",
                "5 ≤ x < 15, 15 ≤ x < 25, 25 ≤ x < 35, 35 ≤ x < 45",
                "0 ≤ x < 10, 10 ≤ x < 25, 25 ≤ x < 50",
            ),
            correct=0,
        ),
        explanation=(
            "Sınırları yalnız tire ile yazılan sınıflarda 10 veya 20 gibi bir değerin hangi sınıfa gireceği "
            "belirsizdir; 5'ten başlayan sınıflar 3 ile 45–47 arasındaki değerleri dışarıda bırakır; 10, 15 ve 25 "
            "genişlikli sınıflar eşit değildir. Alt sınır dahil, üst sınır hariç yazım her değeri tek bir sınıfa "
            "yerleştirir (§3.3)."
        ),
    ),
    Question(
        key="k02", concept="histogramin-gizledigi-bilgi", note=_note("3.7", "Şekil 3.6"),
        prompt="Bir histogramda aşağıdakilerden hangisi doğrudan okunamaz?",
        answer=MultipleChoice(
            (
                "En yüksek frekanslı sınıf",
                "Dağılımın genel biçimi",
                "Belirli bir değerin (ör. 35 dakikanın) kaç kez gözlendiği",
                "Bir sınıftaki gözlem sayısı",
            ),
            correct=2,
        ),
        explanation=(
            "Histogram değerleri sınıflara toplar: Şekil 3.6, 30 ≤ x < 40 sınıfında 11 gözlem olduğunu gösterir "
            "ama 35 dakikanın iki kez gözlendiğini göstermez. Tek tek değerler için nokta grafiği veya "
            "gövde–yaprak gösterimi kullanılır (§3.7)."
        ),
    ),
    Question(
        key="k03", concept="tablodan-carpiklik-yonu", note=_note("3.9"),
        prompt=(
            "Bir sınavın puan dağılımı: 0 ≤ x < 10: 1, 10 ≤ x < 20: 2, 20 ≤ x < 30: 4, 30 ≤ x < 40: 9, "
            "40 ≤ x < 50: 14 öğrenci. Bu dağılımın histogramı en iyi hangisiyle tanımlanır?"
        ),
        answer=MultipleChoice(
            (
                "Sağa çarpık",
                "Sola çarpık",
                "Yaklaşık simetrik",
                "Frekans tablosundan biçim okunamaz",
            ),
            correct=1,
        ),
        explanation=(
            "Gözlemler yüksek puanlarda yoğunlaşır; seyrekleşen uzun kuyruk düşük puanlara, yani sola uzanır. "
            "Çarpıklığın yönü kuyruğun uzandığı yöndür: dağılım sola çarpıktır (§3.9; Sezgi, Deney 2)."
        ),
    ),
    Question(
        key="k04", concept="kumulatiften-sinif-yuzdesi", note=_note("3.10", "Tablo 3.4"),
        prompt=(
            "Bir kümülatif yüzde tablosunda \"40 dakikadan az: %65\" ve \"50 dakikadan az: %82\" yazıyor. "
            "40 ≤ x < 50 sınıfının yüzde frekansı kaçtır?"
        ),
        answer=MultipleChoice(("%65", "%82", "%147", "%17"), correct=3),
        explanation=(
            "Kümülatif yüzde, üst sınıra kadar olan yüzde frekansların toplamıdır. Ardışık iki kümülatif "
            "yüzdenin farkı aradaki sınıfın yüzde frekansıdır: 82 − 65 = 17 (§3.10)."
        ),
    ),
    Question(
        key="k05", concept="genis-sinif-tepe-gizler", note=_note("3.8", "Şekil 3.8"),
        prompt=(
            "Aynı veriyle 10 dakikalık sınıflarla çizilen histogramda iki tepe, 30 dakikalık sınıflarla "
            "çizilende tek tepe görülüyor. En makul yorum hangisidir?"
        ),
        answer=MultipleChoice(
            (
                "Geniş sınıflar iki ayrı yoğunlaşmayı birleştirmiş olabilir; daha dar sınıflar da incelenmelidir.",
                "İki histogramdan biri yanlış çizilmiştir.",
                "Tek tepeli histogram her zaman doğrudur, çünkü daha az rastgelelik içerir.",
                "Veri iki çizim arasında değişmiştir.",
            ),
            correct=0,
        ),
        explanation=(
            "Histogramın görünümü sınıf genişliğine duyarlıdır. Geniş sınıflar komşu aralıkları birleştirir ve "
            "yerel tepeleri gizleyebilir; çok dar sınıflar ise rastgele dalgalanmayı tepe gibi gösterebilir "
            "(§3.8; Sezgi, Deney 1)."
        ),
    ),
    Question(
        key="k06", concept="govde-yaprak-ve-histogram", note=_note("3.11"),
        prompt=(
            "Gövdesi onlar basamağı olan bir gövde–yaprak gösterimi, gövdeler yatay eksende olacak biçimde "
            "90 derece döndürülürse neye benzer?"
        ),
        answer=MultipleChoice(
            (
                "Bir dilim grafiğine",
                "10 birim genişliğinde sınıflarla çizilmiş bir histograma",
                "Bir kümülatif yüzde eğrisine",
                "Bir çapraz tabloya",
            ),
            correct=1,
        ),
        explanation=(
            "Her gövde bir onluktur ve o satırdaki yaprak sayısı o onluktaki gözlem sayısıdır. Ulaşım süresi "
            "verisinde yaprak sayıları 6, 10, 11, 5, 4, 2 ve 2; bunlar Tablo 3.2'deki frekanslardır. Farkı, "
            "yaprakların ham değerleri de korumasıdır (§3.11)."
        ),
    ),
    Question(
        key="k07", concept="yuzde-histogramin-kullanimi", note=_note("3.12", "Şekil 3.12"),
        prompt="Yüzde frekans histogramı frekans histogramına göre en çok hangi durumda işe yarar?",
        answer=MultipleChoice(
            (
                "Tek tek gözlem değerlerini göstermek istediğimizde",
                "Sınıf genişliğini seçerken",
                "Farklı büyüklükteki iki örneklemin dağılımını karşılaştırırken",
                "Dağılımın biçimini değiştirmek istediğimizde",
            ),
            correct=2,
        ),
        explanation=(
            "Yüzde histogramı frekans histogramıyla aynı biçimdedir; değişen yalnız dikey eksendir. Bu yüzden "
            "40 ve 400 öğrencilik iki örneklemin dağılımı aynı ölçekte karşılaştırılabilir (§3.12, Şekil 3.12)."
        ),
    ),
    # --- Doğru–yanlış -------------------------------------------------------------
    Question(
        key="d01", concept="nicel-ozetin-amaci", note=_note("3.1", "Tablo 3.1"),
        prompt=(
            "Nicel veri için betimsel özetin temel amacı, değerlerin hangi bölgelerde yoğunlaştığını ve "
            "dağılımın genel biçimini görünür kılmaktır."
        ),
        answer=TrueFalse(True),
        explanation=(
            "Tablo 3.1'deki 40 değere tek tek bakarak yoğunlaşmayı görmek zordur. Frekans tablosu ve grafikler "
            "değerlerin nerede toplandığını ve dağılımın biçimini görünür kılar (§3.1)."
        ),
    ),
    Question(
        key="d02", concept="yuzde-frekansin-paydasi", note=_note("3.4"),
        prompt="İki örneklemde aynı sınıfın frekansı eşitse o sınıfın yüzde frekansları da eşittir.",
        answer=TrueFalse(False),
        explanation=(
            "Yüzde frekans 100 f/n'dir; payda örneklem büyüklüğüdür. Aynı 20 gözlem 40 kişilik örneklemde "
            "%50, 200 kişilik örneklemde %10 eder (§3.4)."
        ),
    ),
    Question(
        key="d03", concept="orta-noktalar-arasi-fark", note=_note("3.5"),
        prompt=(
            "Eşit genişlikli sınıflarda ardışık iki sınıfın orta noktaları arasındaki fark sınıf genişliğine "
            "eşittir."
        ),
        answer=TrueFalse(True),
        explanation=(
            "Orta nokta m = (L + U)/2'dir. Bir sonraki sınıfın iki sınırı da h kadar kaydığı için orta noktası "
            "da h kadar kayar: ulaşım süresinde 15, 25, 35, … (h = 10) (§3.5)."
        ),
    ),
    Question(
        key="d04", concept="nokta-grafiginin-eksenleri", note=_note("3.6", "Şekil 3.5"),
        prompt="Nokta grafiğinde yatay eksende gözlem numarası, dikey eksende gözlemin değeri gösterilir.",
        answer=TrueFalse(False),
        explanation=(
            "Nokta grafiğinde yatay eksen değişkenin değerleridir; her gözlem kendi değerinin üzerinde bir "
            "noktadır ve aynı değerdeki gözlemler üst üste dizilir (§3.6, Şekil 3.5)."
        ),
    ),
    Question(
        key="d05", concept="sinif-baslangic-noktasi", note=_note("3.8"),
        prompt=(
            "Sınıf genişliği aynı kalsa bile sınıfların başlangıç noktasını değiştirmek (ör. 10 yerine 15'ten "
            "başlamak) histogramın görünümünü değiştirebilir."
        ),
        answer=TrueFalse(True),
        explanation=(
            "Başlangıç noktası sınıf sınırlarını, dolayısıyla hangi gözlemin hangi sınıfa düştüğünü değiştirir. "
            "Genişlik gibi sınırlar da histogramı yorumlamadan önce kontrol edilmesi gereken bir tercihtir "
            "(§3.8, §3.3)."
        ),
    ),
    Question(
        key="d06", concept="ogive-artisi", note=_note("3.10", "Şekil 3.10"),
        prompt=(
            "Kümülatif yüzde eğrisinde ardışık iki nokta arasındaki yükseliş, aradaki sınıfın yüzde frekansına "
            "eşittir."
        ),
        answer=TrueFalse(True),
        explanation=(
            "Kümülatif yüzde bir üst sınırdan sonrakine geçerken o sınıfın yüzde frekansı kadar artar. Tablo "
            "3.4'te 40 dakikadan az %67,5, 50 dakikadan az %80: 40 ≤ x < 50 sınıfının payı 12,5 puandır (§3.10)."
        ),
    ),
    Question(
        key="d07", concept="donusumler-ayni", note=_note("3.13"),
        prompt=(
            "Nicel verilerde frekans, göreli frekans ve yüzde frekans, kategorik verilerdekinden farklı "
            "formüllerle hesaplanır."
        ),
        answer=TrueFalse(False),
        explanation=(
            "Dönüşümler aynıdır: r = f/n ve p = 100 r. Değişen yalnızca kategorilerin artık analistin seçtiği "
            "sayısal aralıklar olmasıdır (§3.13, §3.4)."
        ),
    ),
    # --- Boşluk doldurma ----------------------------------------------------------
    Question(
        key="b01", concept="yaklasik-genislik-hesabi", note=_note("3.2", "(3.1)"),
        prompt=(
            "En küçük değeri 150, en büyük değeri 390 olan bir veri setinde 6 sınıf için yaklaşık sınıf "
            "genişliği **(1)**, 8 sınıf için **(2)** olur."
        ),
        answer=FillBlanks((NumberBlank(40, 0.05, "40"), NumberBlank(30, 0.05, "30"))),
        explanation=(
            "Yaklaşık sınıf genişliği (en büyük − en küçük)/sınıf sayısıdır: 240/6 = 40 ve 240/8 = 30. Veri "
            "aralığı sabitken sınıf sayısı arttıkça genişlik azalır (§3.2, (3.1))."
        ),
    ),
    Question(
        key="b02", concept="kumulatif-frekans-hesabi", note=_note("3.10", "(3.6)"),
        prompt=(
            "60 çağrının bekleme süreleri (dakika): 0 ≤ x < 2: 21, 2 ≤ x < 4: 24, 4 ≤ x < 6: 9, 6 ≤ x < 8: 6 "
            "çağrı. 4 dakikadan kısa bekleyen çağrı sayısı **(1)**, bu çağrıların yüzdesi **(2)** olur."
        ),
        answer=FillBlanks((NumberBlank(45, 0.05, "45"), NumberBlank(75, 0.05, "75"))),
        explanation=(
            "Kümülatif frekans üst sınıra kadar olan frekansların toplamıdır: F = 21 + 24 = 45. Kümülatif yüzde "
            "100 × 45/60 = 75 (§3.10, (3.6))."
        ),
    ),
    Question(
        key="b03", concept="ondalikli-orta-nokta", note=_note("3.5", "(3.5)"),
        prompt=(
            "12,5 ≤ x < 17,5 sınıfının orta noktası **(1)**, 17,5 ≤ x < 22,5 sınıfının orta noktası **(2)** "
            "olur."
        ),
        answer=FillBlanks((NumberBlank(15, 0.005, "15"), NumberBlank(20, 0.005, "20"))),
        explanation=(
            "Orta nokta (L + U)/2'dir: (12,5 + 17,5)/2 = 15 ve (17,5 + 22,5)/2 = 20. Ardışık orta noktalar sınıf "
            "genişliği (5) kadar farklıdır (§3.5, (3.5))."
        ),
    ),
    Question(
        key="b04", concept="sinif-goreli-frekansi", note=_note("3.4", "(3.3)"),
        prompt=(
            "25 öğrencinin 7'si 80 ≤ x < 90 puan sınıfındadır. Bu sınıfın göreli frekansı **(1)**, yüzde "
            "frekansı **(2)** olur."
        ),
        answer=FillBlanks((NumberBlank(0.28, 0.005, "0,28"), NumberBlank(28, 0.05, "28"))),
        explanation="Göreli frekans r = f/n = 7/25 = 0,28; yüzde frekans p = 100 r = 28 (§3.4, (3.3)).",
    ),
    Question(
        key="b05", concept="govde-yaprak-satiri", note=_note("3.11"),
        prompt=(
            "Gövdesi onlar basamağı olan bir gösterimde \"6 | 1 4 4 9\" satırında **(1)** gözlem vardır; bu "
            "satırdaki en büyük değer **(2)** olur."
        ),
        answer=FillBlanks((NumberBlank(4, 0.005, "4"), NumberBlank(69, 0.005, "69"))),
        explanation=(
            "Her yaprak bir gözlemdir: 61, 64, 64 ve 69. Yapraklar küçükten büyüğe dizildiği için en büyük "
            "değer son yapraktır (§3.11)."
        ),
    ),
    # --- Denklem yazma -----------------------------------------------------------
    Question(
        key="e01", concept="yuzde-frekans-formulu", note=_note("3.4", "(3.4)"),
        prompt="Bir sınıfın frekansı $f$, gözlem sayısı $n$ ise sınıfın yüzde frekansını yazın.",
        answer=Equation(
            lhs="p",
            symbols=(Symbol("f", "f", "sınıfın frekansı", 1, 10), Symbol("n", "n", "gözlem sayısı", 11, 60)),
            answer="100*f/n",
            shown="100\\,f/n",
        ),
        explanation=(
            "Yüzde frekans göreli frekansın 100 katıdır: p = 100 f/n. Tablo 3.3'te 30 ≤ x < 40 sınıfı için "
            "100 × 11/40 = 27,5 (§3.4, (3.4))."
        ),
    ),
    Question(
        key="e02", concept="orta-nokta-formulu", note=_note("3.5", "(3.5)"),
        prompt="Alt sınırı $L$, üst sınırı $U$ olan bir sınıfın orta noktasını yazın.",
        answer=Equation(
            lhs="m",
            symbols=(
                Symbol("l", "L", "alt sınır", 0, 40, aliases=("L",)),
                Symbol("u", "U", "üst sınır", 41, 90, aliases=("U",)),
            ),
            answer="(l+u)/2",
            shown="(L+U)/2",
        ),
        explanation=(
            "Orta nokta alt ve üst sınırın ortalamasıdır: 20 ≤ x < 30 için (20 + 30)/2 = 25 dakika. Sınıftaki "
            "gözlemlerin bu değere eşit olduğu anlamına gelmez (§3.5, (3.5))."
        ),
    ),
    Question(
        key="e03", concept="kumulatif-frekans-yinelemesi", note=_note("3.10", "(3.6)"),
        prompt=(
            "Bir önceki sınıfa kadar kümülatif frekans $F$, bu sınıfın frekansı $f$ ise bu sınıfa kadar "
            "kümülatif frekansı yazın."
        ),
        answer=Equation(
            lhs="F_j",
            symbols=(
                Symbol("c", "F", "önceki sınıfa kadar kümülatif frekans", 1, 30, aliases=("F",)),
                Symbol("f", "f", "bu sınıfın frekansı", 1, 10),
            ),
            answer="c + f",
            shown="F + f",
        ),
        explanation=(
            "F_j = f_1 + ⋯ + f_j olduğundan her yeni sınıf bir öncekinin kümülatif frekansına kendi frekansını "
            "ekler: ulaşım süresinde 16 + 11 = 27 (§3.10, (3.6))."
        ),
    ),
    Question(
        key="e04", concept="genislikten-sinif-sayisi", note=_note("3.2", "(3.1)"),
        prompt=(
            "En küçük değer $a$, en büyük değer $b$ ve seçilen sınıf genişliği $h$ ise yaklaşık sınıf sayısını "
            "yazın."
        ),
        answer=Equation(
            lhs="k",
            symbols=(
                Symbol("a", "a", "en küçük değer", 0, 50),
                Symbol("b", "b", "en büyük değer", 60, 150),
                Symbol("h", "h", "sınıf genişliği", 1, 20),
            ),
            answer="(b-a)/h",
            shown="(b-a)/h",
        ),
        explanation=(
            "Yaklaşık sınıf genişliği h = (b − a)/k ise k = (b − a)/h'dir: ulaşım süresinde (76 − 12)/10 = 6,4, "
            "yani en az 7 sınıf gerekir (§3.2, (3.1))."
        ),
    ),
    Question(
        key="e05", concept="j-inci-sinifin-ust-siniri", note=_note("3.3"),
        prompt=(
            "İlk sınıfın alt sınırı $a$, sınıf genişliği $h$ ise $j$. sınıfın üst sınırını yazın (sınıflar "
            "a ≤ x < a + h, a + h ≤ x < a + 2h, …)."
        ),
        answer=Equation(
            lhs="U_j",
            symbols=(
                Symbol("a", "a", "ilk sınıfın alt sınırı", 0, 50),
                Symbol("h", "h", "sınıf genişliği", 1, 20),
                Symbol("j", "j", "sınıf numarası", 1, 10),
            ),
            answer="a + j*h",
            shown="a + j\\,h",
        ),
        explanation=(
            "Her sınıf bir öncekinin h kadar sağındadır; j. sınıfın üst sınırı a + j h olur. Ulaşım süresinde "
            "a = 10, h = 10: 3. sınıf 30 ≤ x < 40, üst sınırı 10 + 3 × 10 = 40 (§3.3)."
        ),
    ),
)


KONU03_QUIZ = QuestionSet(
    topic_key="konu03",
    title="Konu 3: Kendini sına",
    questions=QUESTIONS,
    intro=(
        "Bu set haftanın temel kavramlarını sınar. Her soru tek bir kavrama odaklanır ve notlardaki bir "
        "bölüme bağlıdır; yanlış cevaplarınız için tekrar edilecek bölümler en üstte listelenir. Notlardaki "
        "egzersiz ve mini quiz maddelerini tekrar etmez, yeni sayılarla onları tamamlar."
    ),
    sections=tuple(f"3.{number}" for number in range(1, 14)),
)
