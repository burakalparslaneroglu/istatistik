"""Konu 4 "Kendini sına" soru seti.

Her soru tek bir kavramı sınar ve notlardaki bir bölüme bağlıdır. Sorular notların Egzersiz 4.1–4.12 ve
Mini Quiz 4.1–4.12 maddelerini tekrar etmez (ör. %10 artış–%10 azalışın başlangıca dönüp dönmediği,
Q₁'in hangi yüzdelik olduğu, en sık tercih edilen marka için ölçü seçimi); yeni sayılarla ve yeni
bağlamlarla aynı becerileri sınar. Yüzdelikler notlardaki L_p = (p/100)(n + 1) kuralıyla hesaplanır.
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
        key="k01", concept="ortalamaya-sabit-eklemek", note=_note("4.2", "(4.1)"),
        prompt="Bir veri setindeki her gözleme 5 eklenirse aritmetik ortalama nasıl değişir?",
        answer=MultipleChoice(("5 artar", "Değişmez", "5 katına çıkar", "n/5 kadar artar"), correct=0),
        explanation=(
            "Her gözleme 5 eklenince toplam 5n artar: (Σxᵢ + 5n)/n = x̄ + 5. Satış verisinde her gün 5 bin TL "
            "fazla satış olsaydı ortalama 21,25'ten 26,25'e çıkardı (§4.2, (4.1))."
        ),
    ),
    Question(
        key="k02", concept="yuzdeligin-yorumu", note=_note("4.8"),
        prompt="Bir çalışanın maaşı, şirketteki maaşların 85. yüzdeliğine eşittir. Hangisi doğrudur?",
        answer=MultipleChoice(
            (
                "Çalışanın maaşı 85 bin TL'dir.",
                "Çalışanların yaklaşık %15'i ondan az kazanır.",
                "Çalışanların yaklaşık %85'i ondan az kazanır.",
                "Çalışanın maaşı ortalama maaşın %85'idir.",
            ),
            correct=2,
        ),
        explanation=(
            "Yüzdelik göreli konumu anlatır: 85. yüzdelikte gözlemlerin yaklaşık %85'i altta, %15'i üstte kalır. "
            "Değerin kendisi hakkında bilgi vermez (§4.8)."
        ),
    ),
    Question(
        key="k03", concept="grup-ortalamalarini-birlestirmek", note=_note("4.4", "(4.3)"),
        prompt=(
            "A şubesinde 30 öğrencinin not ortalaması 70, B şubesinde 10 öğrencinin not ortalaması 90'dır. "
            "Bütün 40 öğrencinin not ortalaması kaçtır?"
        ),
        answer=MultipleChoice(("80", "75", "85", "72,5"), correct=1),
        explanation=(
            "Şube ortalamaları öğrenci sayılarıyla ağırlıklandırılır: (30 × 70 + 10 × 90)/40 = 3.000/40 = 75. "
            "Basit ortalama (70 + 90)/2 = 80, şubelerin büyüklük farkını yok sayar (§4.4, (4.3))."
        ),
    ),
    Question(
        key="k04", concept="ortalama-medyandan-buyuk", note=_note("4.6", "Tablo 4.2"),
        prompt=(
            "Bir şirkette ortalama aylık maaş 45 bin TL, medyan maaş 32 bin TL'dir. En makul yorum "
            "hangisidir?"
        ),
        answer=MultipleChoice(
            (
                "Çalışanların yarısı 45 bin TL'den fazla kazanır.",
                "Dağılım sola çarpıktır.",
                "Hesaplardan biri yanlıştır; ortalama ile medyan yakın olmalıdır.",
                "Az sayıda çok yüksek maaş ortalamayı yukarı çekmektedir; dağılım sağa çarpıktır.",
            ),
            correct=3,
        ),
        explanation=(
            "Ortalamanın medyandan belirgin biçimde büyük olması, sağdaki büyük değerlerin ortalamayı çektiğine "
            "işaret eder. Çalışanların yarısı medyanın, yani 32 bin TL'nin altında kazanır (§4.6)."
        ),
    ),
    Question(
        key="k05", concept="surekli-veride-mod", note=_note("4.7"),
        prompt=(
            "0,01 kg duyarlıkla ölçülen 200 paketin ağırlıklarında mod neden çoğu zaman bilgilendirici "
            "değildir?"
        ),
        answer=MultipleChoice(
            (
                "Mod yalnız kategorik veride hesaplanabilir.",
                "Değerlerin çoğu bir kez gözlenir; en sık görülen değer rastlantısal olabilir.",
                "Mod her zaman ortalamaya eşittir.",
                "Mod uç değerlere çok duyarlıdır.",
            ),
            correct=1,
        ),
        explanation=(
            "Sürekli ölçümlerde değerler nadiren tekrar eder; bir değerin iki kez gözlenmesi tesadüf olabilir. "
            "Mod, tekrar eden değerlerin anlamlı olduğu durumlarda ve kategorik veride yararlıdır (§4.7)."
        ),
    ),
    Question(
        key="k06", concept="ceyrekler-arasi-pay", note=_note("4.9", "Şekil 4.9"),
        prompt=(
            "Bir sınavda Q₁ = 55 ve Q₃ = 80'dir. Öğrencilerin yaklaşık yüzde kaçı 55 ile 80 arasında puan "
            "almıştır?"
        ),
        answer=MultipleChoice(("%25", "%75", "%80", "%50"), correct=3),
        explanation=(
            "Q₁'in altında gözlemlerin yaklaşık %25'i, Q₃'ün altında %75'i vardır; ikisinin arasında yaklaşık "
            "75 − 25 = 50, yani öğrencilerin yarısı kalır (§4.9)."
        ),
    ),
    Question(
        key="k07", concept="esik-icin-yuzdelik", note=_note("4.11", "Tablo 4.3"),
        prompt=(
            "Bir kargo şirketi \"siparişlerin %90'ı en geç X günde teslim edilir\" demek istiyor. X için hangi "
            "ölçü uygundur?"
        ),
        answer=MultipleChoice(("90. yüzdelik", "Aritmetik ortalama", "Mod", "Medyan"), correct=0),
        explanation=(
            "Soru bir eşik konumu istiyor: teslim sürelerinin %90'ının altında kaldığı değer 90. yüzdeliktir. "
            "Ortalama ve medyan merkezi, mod en sık görülen değeri gösterir (§4.11, Tablo 4.3)."
        ),
    ),
    # --- Doğru–yanlış -------------------------------------------------------------
    Question(
        key="d01", concept="konum-yayilimi-gostermez", note=_note("4.1"),
        prompt=(
            "Konum ölçüleri değerlerin sayısal eksendeki tipik konumunu özetler; gözlemlerin merkez çevresinde "
            "ne kadar yayıldığını göstermez."
        ),
        answer=TrueFalse(True),
        explanation=(
            "Konum ölçüsü \"merkez nerede?\" sorusunu cevaplar. Aynı ortalama ve medyana sahip iki veri seti çok "
            "farklı yayılabilir; bu fark değişkenlik ölçüleriyle ölçülür (§4.1, §4.12)."
        ),
    ),
    Question(
        key="d02", concept="istatistik-ve-parametre", note=_note("4.2", "(4.2)"),
        prompt="Örneklem ortalaması $\\bar{x}$ bir parametre, anakütle ortalaması $\\mu$ bir istatistiktir.",
        answer=TrueFalse(False),
        explanation=(
            "Tersi doğrudur: örneklemden hesaplanan x̄ bir istatistik, bütün anakütlenin ortalaması μ bir "
            "parametredir. Hesaplama mantığı aynıdır; notasyon elimizde neyin bulunduğunu gösterir (§4.2)."
        ),
    ),
    Question(
        key="d03", concept="medyan-toplam-gerektirmez", note=_note("4.5"),
        prompt="Medyanı bulmak için gözlemlerin toplamını bilmek gerekir.",
        answer=TrueFalse(False),
        explanation=(
            "Medyan yalnız sıralamaya dayanır: sıralanmış verinin ortasındaki gözlem (n tek) ya da ortadaki iki "
            "gözlemin ortalaması (n çift). Toplam, aritmetik ortalama için gerekir (§4.5)."
        ),
    ),
    Question(
        key="d04", concept="tek-n-de-medyan-konumu", note=_note("4.8", "(4.4)"),
        prompt=(
            "Tek sayıda gözlemi olan bir veri setinde medyanın konumu $L_{50} = (n + 1)/2$ her zaman bir tam "
            "sayıdır."
        ),
        answer=TrueFalse(True),
        explanation=(
            "n tekse n + 1 çifttir ve (n + 1)/2 tam sayıdır; medyan tam ortadaki gözlemdir. n çiftse L₅₀ buçuklu "
            "bir sayıdır ve ortadaki iki gözlemin ortalaması alınır (§4.8, §4.5)."
        ),
    ),
    Question(
        key="d05", concept="geometrik-ortalama-faktorlerle", note=_note("4.10", "(4.5)"),
        prompt="Geometrik ortalama yüzde değişimlerin (ör. 10 ve −10) çarpımından hesaplanır.",
        answer=TrueFalse(False),
        explanation=(
            "Geometrik ortalama büyüme faktörlerinden (1,10 ve 0,90) hesaplanır: G = √(1,10 × 0,90) ≈ 0,995. "
            "Yüzde değişimlerin çarpımı negatif olabilir ve anlamlı değildir; ortalama büyüme (G − 1) × 100 ile "
            "bulunur (§4.10, (4.5))."
        ),
    ),
    Question(
        key="d06", concept="ayni-merkez-farkli-ceyrek", note=_note("4.12", "Şekil 4.12"),
        prompt="Ortalaması ve medyanı aynı olan iki veri setinin çeyrekleri de aynı olmak zorundadır.",
        answer=TrueFalse(False),
        explanation=(
            "§4.12'deki A = 28, …, 32 ve B = 10, …, 50 veri setlerinde ortalama ve medyan 30; fakat A'da "
            "Q₁ = 28,5, B'de Q₁ = 15. Çeyrekler yayılım hakkında bilgi taşır (§4.12, §4.9)."
        ),
    ),
    Question(
        key="d07", concept="sola-carpiklikta-ortalama", note=_note("4.13"),
        prompt="Birkaç çok küçük değerin bulunduğu, sola çarpık bir dağılımda ortalama genellikle medyandan küçüktür.",
        answer=TrueFalse(True),
        explanation=(
            "Ortalama bütün büyüklükleri kullanır; soldaki çok küçük değerler ortalamayı aşağı çeker, medyan ise "
            "sıradaki konuma dayandığı için az etkilenir. Sağa çarpık dağılımda durum tersidir (§4.13, §4.6)."
        ),
    ),
    # --- Boşluk doldurma ----------------------------------------------------------
    Question(
        key="b01", concept="ortalamadan-toplam", note=_note("4.2", "(4.1)"),
        prompt=(
            "Beş gözlemin ortalaması 12'dir. Gözlemlerin toplamı **(1)** olur; altıncı gözlem olarak 18 "
            "eklenirse yeni ortalama **(2)** olur."
        ),
        answer=FillBlanks((NumberBlank(60, 0.05, "60"), NumberBlank(13, 0.05, "13"))),
        explanation=(
            "Ortalama toplam/n olduğundan toplam n × x̄ = 5 × 12 = 60. 18 eklenince toplam 78, gözlem sayısı 6 "
            "olur: 78/6 = 13 (§4.2, (4.1))."
        ),
    ),
    Question(
        key="b02", concept="iki-bilesenli-agirlikli-not", note=_note("4.4", "Tablo 4.1"),
        prompt=(
            "Ara sınav notu 60 (ağırlık %40), final notu 85'tir (ağırlık %60). Ağırlıklı ortalama **(1)**, "
            "basit ortalama **(2)** olur."
        ),
        answer=FillBlanks((NumberBlank(75, 0.05, "75"), NumberBlank(72.5, 0.05, "72,5"))),
        explanation=(
            "Ağırlıklı ortalama 0,40 × 60 + 0,60 × 85 = 24 + 51 = 75; basit ortalama (60 + 85)/2 = 72,5. "
            "Ağırlığı yüksek final notu sonucu yukarı çeker (§4.4, Tablo 4.1)."
        ),
    ),
    Question(
        key="b03", concept="siralayip-medyan", note=_note("4.5"),
        prompt="7, 3, 9, 1, 5 verisinin medyanı **(1)** olur; bu veriye 11 eklenirse medyan **(2)** olur.",
        answer=FillBlanks((NumberBlank(5, 0.005, "5"), NumberBlank(6, 0.005, "6"))),
        explanation=(
            "Önce sıralanır: 1, 3, 5, 7, 9; ortadaki değer 5. 11 eklenince n = 6 olur ve ortadaki iki değerin "
            "ortalaması alınır: (5 + 7)/2 = 6 (§4.5)."
        ),
    ),
    Question(
        key="b04", concept="ara-degerli-yuzdelik", note=_note("4.8", "(4.4)"),
        prompt=(
            "Sıralı veri: 2, 4, 7, 8, 10, 13, 15, 18, 20, 25 (n = 10). 70. yüzdeliğin konumu L₇₀ = **(1)**, "
            "değeri P₇₀ = **(2)** olur."
        ),
        answer=FillBlanks((NumberBlank(7.7, 0.005, "7,7"), NumberBlank(17.1, 0.005, "17,1"))),
        explanation=(
            "L₇₀ = 0,70 × (10 + 1) = 7,7. 7. değer 15, 8. değer 18 olduğundan P₇₀ = 15 + 0,7 × (18 − 15) = 17,1 "
            "(§4.8, (4.4))."
        ),
    ),
    Question(
        key="b05", concept="artis-azalis-sifir-bilesik", note=_note("4.10", "(4.5)"),
        prompt=(
            "Bir endeks önce %25 artmış, ardından %20 azalmıştır. Başlangıç değeri 100 ise son değer **(1)** "
            "olur; iki yıllık ortalama bileşik büyüme yüzde **(2)** olur."
        ),
        answer=FillBlanks((NumberBlank(100, 0.05, "100"), NumberBlank(0, 0.05, "0"))),
        explanation=(
            "Büyüme faktörleri 1,25 ve 0,80; çarpımları 1 olduğu için son değer yine 100 ve G = √1 = 1: ortalama "
            "bileşik büyüme sıfır. Yüzde değişimlerin aritmetik ortalaması ise (25 − 20)/2 = 2,5 olurdu "
            "(§4.10, (4.5))."
        ),
    ),
    # --- Denklem yazma -----------------------------------------------------------
    Question(
        key="e01", concept="tek-gozlem-degisince-ortalama", note=_note("4.3"),
        prompt=(
            "$n$ gözlemin ortalaması $m$'dir. Gözlemlerden biri $a$ yerine $b$ olarak değiştirilirse yeni "
            "ortalamayı yazın."
        ),
        answer=Equation(
            lhs="\\bar{x}_{\\text{yeni}}",
            symbols=(
                Symbol("m", "m", "eski ortalama", 10, 50),
                Symbol("a", "a", "değiştirilen gözlem", 1, 20),
                Symbol("b", "b", "yeni gözlem", 21, 100),
                Symbol("n", "n", "gözlem sayısı", 5, 30),
            ),
            answer="m + (b-a)/n",
            shown="m + (b-a)/n",
        ),
        explanation=(
            "Toplam b − a kadar değişir; ortalama bu farkın n'de biri kadar değişir. Satış verisinde "
            "21,25 + (56 − 26)/8 = 25 (§4.3)."
        ),
    ),
    Question(
        key="e02", concept="agirlikli-ortalama-formulu", note=_note("4.4", "(4.3)"),
        prompt=(
            "İki notun değerleri $a$ ve $b$, ağırlıkları $p$ ve $q$ ise ağırlıklı ortalamayı yazın (ağırlıkların "
            "toplamı 1 olmak zorunda değildir)."
        ),
        answer=Equation(
            lhs="\\bar{x}_w",
            symbols=(
                Symbol("a", "a", "birinci not", 40, 100),
                Symbol("b", "b", "ikinci not", 40, 100),
                Symbol("p", "p", "birinci notun ağırlığı", 1, 5),
                Symbol("q", "q", "ikinci notun ağırlığı", 1, 5),
            ),
            answer="(p*a + q*b)/(p + q)",
            shown="(p\\,a + q\\,b)/(p + q)",
        ),
        explanation=(
            "Ağırlıklı ortalama Σwᵢxᵢ/Σwᵢ'dir. Ağırlıkların toplamı 1 ise payda 1 olur; ağırlıklar yüzde olarak "
            "yazılmışsa payda 100 olur (§4.4, (4.3))."
        ),
    ),
    Question(
        key="e03", concept="yuzdelik-konum-formulu", note=_note("4.8", "(4.4)"),
        prompt="$n$ gözlemli sıralı bir veri setinde $p$. yüzdeliğin konumunu yazın.",
        answer=Equation(
            lhs="L_p",
            symbols=(Symbol("p", "p", "yüzdelik", 1, 99), Symbol("n", "n", "gözlem sayısı", 5, 100)),
            answer="p*(n+1)/100",
            shown="p\\,(n+1)/100",
        ),
        explanation=(
            "Bu derste yüzdelik konumu Lₚ = (p/100)(n + 1) ile bulunur: n = 12 ve p = 60 için 7,8. numpy ve "
            "R'nin varsayılanı başka bir konum kullanır (§4.8, (4.4); Sezgi, Deney 2)."
        ),
    ),
    Question(
        key="e04", concept="ucuncu-ceyrek-ara-degeri", note=_note("4.9"),
        prompt=(
            "$L_{75} = 9{,}75$ olduğuna göre üçüncü çeyreği 9. gözlem $a$ ve 10. gözlem $b$ cinsinden yazın."
        ),
        answer=Equation(
            lhs="Q_3",
            symbols=(Symbol("a", "a", "9. gözlem", 40, 60), Symbol("b", "b", "10. gözlem", 61, 80)),
            answer="a + 0.75*(b-a)",
            shown="a + 0{,}75\\,(b-a)",
        ),
        explanation=(
            "Konumun tam kısmı 9, ondalık kısmı 0,75: 9. gözlemden 10. gözleme doğru yolun %75'i kadar ilerlenir. "
            "Notlarda 58 + 0,75 × (60 − 58) = 59,5 (§4.9)."
        ),
    ),
    Question(
        key="e05", concept="iki-yillik-bilesik-buyume", note=_note("4.10", "(4.5)"),
        prompt="İki yılın büyüme faktörleri $g$ ve $h$ ise ortalama bileşik büyüme oranını yüzde olarak yazın.",
        answer=Equation(
            lhs="\\text{ortalama büyüme (\\%)}",
            symbols=(
                Symbol("g", "g", "birinci yılın faktörü", 0.5, 1.5),
                Symbol("h", "h", "ikinci yılın faktörü", 0.5, 1.5),
            ),
            answer="100*(sqrt(g*h) - 1)",
            shown="100\\,(\\sqrt{g\\,h} - 1)",
        ),
        explanation=(
            "Geometrik ortalama G = √(g h), ortalama dönemsel büyüme (G − 1) × 100. Faktörler 1,10 ve 0,90 ise "
            "√0,99 ≈ 0,995, yani yaklaşık %−0,5 (§4.10, (4.5))."
        ),
    ),
)


KONU04_QUIZ = QuestionSet(
    topic_key="konu04",
    title="Konu 4: Kendini sına",
    questions=QUESTIONS,
    intro=(
        "Bu set haftanın temel kavramlarını sınar. Her soru tek bir kavrama odaklanır ve notlardaki bir "
        "bölüme bağlıdır; yanlış cevaplarınız için tekrar edilecek bölümler en üstte listelenir. Notlardaki "
        "egzersiz ve mini quiz maddelerini tekrar etmez, yeni sayılarla onları tamamlar."
    ),
    sections=tuple(f"4.{number}" for number in range(1, 14)),
)
