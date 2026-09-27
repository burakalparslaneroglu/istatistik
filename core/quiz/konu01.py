"""Konu 1 "Kendini sına" soru seti.

Her soru tek bir kavramı sınar ve notlardaki bir bölüme bağlıdır. Sorular notların egzersiz ve
mini quiz maddelerini tekrar etmez; onları tamamlar. Sayısal cevaplar Tablo 1.1'den hesaplanır ve
testlerde doğrulanır.

Bu sette denklem sorusu üçtür (8 çoktan seçmeli, 7 doğru–yanlış, 6 boşluk, 3 denklem): Konu 1'de
formül olarak yalnız oran, yüzde ve ortalama geçer. Ayrım ders yürütücüsünün kararıdır ve
``tests/test_all_quizzes.py`` içinde belgelenmiştir.
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
    TextBlank,
    TrueFalse,
)

PASSED = Symbol("g", "g", "dersi geçen öğrenci sayısı", 1, 10)
STUDENTS = Symbol("n", "n", "öğrenci sayısı", 11, 40)
TOTAL = Symbol("t", "T", "puanların toplamı", 100, 900, aliases=("T",))


def _note(section: str, *objects: str) -> NoteRef:
    return NoteRef(section, 0, tuple(objects))


QUESTIONS = (
    # --- Çoktan seçmeli -----------------------------------------------------------
    Question(
        key="k01", concept="surecin-geri-beslemesi", note=_note("1.1", "Şekil 1.1"),
        prompt=(
            "Şekil 1.1'deki istatistiksel düşünme akışında son adımdan ilk adıma kesikli bir ok döner. "
            "Bu ok neyi anlatır?"
        ),
        answer=MultipleChoice(
            (
                "Veriyi veya grafiği gördükten sonra araştırma sorusu yeniden düzenlenebilir.",
                "Her analiz aynı soruyla başlayıp aynı soruyla bitmelidir.",
                "Özetleme adımı atlanıp doğrudan çıkarıma geçilebilir.",
                "Yorum yapıldıktan sonra veri silinmelidir.",
            ),
            correct=0,
        ),
        explanation=(
            "Akış doğrusal bir reçete değildir: veriyi gördükten sonra ilk soru değişebilir ya da hazırlanan "
            "bir grafik yeni bir soru doğurabilir. Önemli olan, hesaplamanın araştırma sorusundan "
            "kopmamasıdır (§1.1, Şekil 1.1)."
        ),
    ),
    Question(
        key="k02", concept="alt-indis-okuma", note=_note("1.2", "Tablo 1.1"),
        prompt="Tablo 1.1'de haftalık çalışma saati $x$ ile gösterilirse $x_7$ kaçtır?",
        answer=MultipleChoice(("61", "7", "6", "3"), correct=2),
        explanation=(
            "Alt indis gözlemin sırasını gösterir: $x_7$, tablonun 7. satırındaki G öğrencisinin çalışma "
            "saatidir, yani 6. 61 aynı öğrencinin sınav puanıdır; 7 ise alt indisin kendisidir (§1.2)."
        ),
    ),
    Question(
        key="k03", concept="surekli-degisken", note=_note("1.3"),
        prompt="Aşağıdakilerden hangisi **sürekli** bir nicel değişkendir?",
        answer=MultipleChoice(
            (
                "Bir sınıftaki öğrenci sayısı",
                "Bir hanedeki oda sayısı",
                "Bir yolculuğun dakika cinsinden süresi",
                "Bir öğrencinin doğduğu şehir",
            ),
            correct=2,
        ),
        explanation=(
            "Sürekli değişken bir aralıkta ölçüm sonucu elde edilir; süre bunun tipik örneğidir. Süre 18,4 "
            "dakika gibi sınırlı basamakla kaydedilse de kavramsal olarak süreklidir. Öğrenci ve oda sayısı "
            "sayma sonucu olduğu için kesiklidir; doğum yeri kategoriktir (§1.3)."
        ),
    ),
    Question(
        key="k04", concept="aralik-olceginde-oran-yorumu", note=_note("1.4", "Tablo 1.2"),
        prompt=(
            "Bugün hava 20 °C, dün 10 °C idi. \"Bugün hava dünden iki kat sıcak\" ifadesi için hangisi "
            "doğrudur?"
        ),
        answer=MultipleChoice(
            (
                "Doğrudur; sıcaklık oran ölçeğindedir.",
                "Yanlıştır; Celsius aralık ölçeğindedir ve 0 °C sıcaklığın yokluğu değildir.",
                "Yanlıştır; sıcaklık kategorik bir değişkendir.",
                "Doğrudur; iki değer arasındaki fark anlamlıdır.",
            ),
            correct=1,
        ),
        explanation=(
            "Celsius sıcaklığında farklar anlamlıdır (10 derece fark), fakat 0 °C sıcaklığın yok olduğu "
            "anlamına gelmez. Gerçek sıfır olmadığı için \"iki katı\" gibi oran karşılaştırmaları anlamlı "
            "değildir; bunlar oran ölçeğine özgüdür (§1.4, Tablo 1.2)."
        ),
    ),
    Question(
        key="k05", concept="birim-ve-zaman-boyutu", note=_note("1.5"),
        prompt=(
            "81 ilin 2010–2026 yıllarına ait yıllık işsizlik oranlarını içeren bir veri seti için hangisi "
            "doğrudur?"
        ),
        answer=MultipleChoice(
            (
                "Yalnızca yatay kesit verisidir.",
                "Yalnızca zaman serisi verisidir.",
                "Kategorik bir veri setidir.",
                "Hem birimler (iller) hem zaman (yıllar) boyutu içerir.",
            ),
            correct=3,
        ),
        explanation=(
            "Aynı birimleri birkaç dönem boyunca gözlemek iki boyut içerir: her yıl için 81 ilin yatay "
            "kesiti, her il için bir zaman serisi vardır. Notlar bu yapıya yalnızca değinir; dersin ilk "
            "döneminde temel ayrım yatay kesit ile zaman serisidir (§1.5)."
        ),
    ),
    Question(
        key="k06", concept="rastgele-atamanin-yarari", note=_note("1.6"),
        prompt=(
            "Bir araştırmacı ek çalışma programının etkisini ölçmek için öğrencileri programa yazı-turayla "
            "atıyor. Bu tasarımın, öğrencilerin programı kendilerinin seçtiği gözlemsel çalışmaya göre temel "
            "üstünlüğü nedir?"
        ),
        answer=MultipleChoice(
            (
                "Katılan ve katılmayan gruplar motivasyon gibi diğer özellikler bakımından benzer olur; puan "
                "farkı programa bağlanabilir.",
                "Örneklem büyüklüğü kendiliğinden artar.",
                "Veri toplama hataları ortadan kalkar.",
                "Sonuç bütün öğrenciler için kesinleşir.",
            ),
            correct=0,
        ),
        explanation=(
            "Deneyde araştırmacı koşulu kendisi değiştirir. Katılımı yazı-tura belirlediğinde katılım, puanı "
            "etkileyen diğer özelliklerden bağımsızdır; gözlemsel çalışmada ise daha motive öğrenciler "
            "programı daha sık seçebilir (§1.6; Sezgi, Deney 2)."
        ),
    ),
    Question(
        key="k07", concept="buyuk-yanli-orneklem", note=_note("1.8"),
        prompt=(
            "Öğrencilerin ortalama ulaşım süresini tahmin etmek için anket yalnızca kampüs otoparkında "
            "5.000 öğrenciye uygulanıyor. En önemli sorun hangisidir?"
        ),
        answer=MultipleChoice(
            (
                "Örneklem çok küçüktür.",
                "Örneklem özel araçla gelenleri fazla temsil eder; büyüklük bu sorunu gidermez.",
                "Bu bir tam sayımdır; çıkarım gerekmez.",
                "Ulaşım süresi kategorik bir değişkendir.",
            ),
            correct=1,
        ),
        explanation=(
            "Otoparkta yapılan anket özel araçla gelenlerden oluşur; bu öğrencilerin süreleri anakütleden "
            "sistematik biçimde farklıdır. Sistematik olarak yanlı büyük bir örneklem, iyi seçilmiş küçük bir "
            "örneklemden daha kötü olabilir (§1.8; Sezgi, Deney 3)."
        ),
    ),
    Question(
        key="k08", concept="yazilimin-rolu", note=_note("1.9"),
        prompt="İstatistiksel yazılımın analizdeki rolüyle ilgili hangisi notlardaki görüşle uyumludur?",
        answer=MultipleChoice(
            (
                "Yazılımın ürettiği sonuç doğru yorumlanmış demektir.",
                "Büyük veri setlerinde temel istatistik bilgisine gerek kalmaz.",
                "Yazılım hangi değişkenin ne anlama geldiğine kendisi karar verir.",
                "Yazılım aritmetiği yapar; araştırma sorusunu, veri kalitesini ve yorumu değerlendirmek "
                "kullanıcıya aittir.",
            ),
            correct=3,
        ),
        explanation=(
            "Yazılım hesaplamayı hızlandırır, büyük tabloları özetler ve grafik üretir; fakat \"bilgisayar "
            "hesapladı\" ifadesi yorumun doğru olduğunu garanti etmez. Temel istatistik bilgisi analitik ve "
            "büyük veri alanlarının ön koşuludur (§1.9)."
        ),
    ),
    # --- Doğru–yanlış -------------------------------------------------------------
    Question(
        key="d01", concept="ortalama-betimseldir", note=_note("1.7"),
        prompt=(
            "Tablo 1.1'deki sekiz öğrencinin ortalama puanının 64 olduğunu söylemek bir istatistiksel "
            "çıkarımdır."
        ),
        answer=TrueFalse(False),
        explanation=(
            "Bu ifade yalnızca elimizdeki sekiz öğrenciyi özetler; bu yüzden betimsel istatistiktir. Çıkarım, "
            "gözlemediğimiz daha geniş bir grup hakkında örneklemden hareketle konuşmaktır (§1.7)."
        ),
    ),
    Question(
        key="d02", concept="sayisal-kod-kategorik", note=_note("1.3"),
        prompt="Posta kodu sayılarla yazıldığı için nicel bir değişkendir.",
        answer=TrueFalse(False),
        explanation=(
            "Posta kodu sayısal görünür ama bölgeleri tanımlayan bir etikettir; iki posta kodunun farkı veya "
            "ortalaması anlamlı değildir. Bir değişkenin sayılarla yazılması onu otomatik olarak nicel "
            "yapmaz (§1.3)."
        ),
    ),
    Question(
        key="d03", concept="ordinalde-esit-aralik-yok", note=_note("1.4"),
        prompt="Ordinal ölçekte ardışık kategoriler arasındaki farkların eşit olduğu varsayılır.",
        answer=TrueFalse(False),
        explanation=(
            "Ordinal düzeyde yalnızca sıra anlamlıdır: düşük < orta < yüksek. Yüksek ile orta arasındaki "
            "farkın, orta ile düşük arasındaki farka eşit olduğunu söylemek zorunda değiliz; kodların "
            "ortalaması bu yüzden keyfî aralıklara bağlıdır (§1.4; Sezgi, Deney 1)."
        ),
    ),
    Question(
        key="d04", concept="tutarsiz-gozlem-kontrolu", note=_note("1.6"),
        prompt=(
            "20 yaşındaki bir öğrencinin 18 yıllık tam zamanlı iş deneyimi kayıtlıysa bu gözlem hemen veri "
            "setinden silinmelidir."
        ),
        answer=TrueFalse(False),
        explanation=(
            "Böyle bir kayıt tutarlılık açısından kontrol edilmelidir; fakat otomatik olarak silinmemelidir. "
            "Önce veri girişi, soru veya ölçüm hatası olup olmadığı araştırılır; gerekçesiz gözlem çıkarmak "
            "etik bir sorundur (§1.6, §1.10)."
        ),
    ),
    Question(
        key="d05", concept="anakutle-soruya-bagli", note=_note("1.11", "Tablo 1.3"),
        prompt="Aynı öğrenci anketinde anakütle, araştırma sorusuna bağlı olarak farklı tanımlanabilir.",
        answer=TrueFalse(True),
        explanation=(
            "Tablo 1.3'te olası anakütle \"araştırma sorusuna bağlı olarak üniversitedeki ikinci sınıf "
            "öğrencileri\" diye verilir. Hangi grup hakkında konuşmak istediğimiz anakütleyi belirler; "
            "örneklem de o anakütleyi temsil edecek biçimde seçilmelidir (§1.11)."
        ),
    ),
    Question(
        key="d06", concept="secici-raporlama", note=_note("1.10"),
        prompt=(
            "Her analiz doğru hesaplanmış olsa bile yalnızca istenen sonucu veren analizleri raporlamak "
            "istatistiksel bilgiye duyulan güveni bozar."
        ),
        answer=TrueFalse(True),
        explanation=(
            "Etik sorunlar yalnızca hesap hatasından doğmaz. Uygunsuz örnekleme, yanıltıcı grafik ve seçici "
            "raporlama da sonucu verinin izin verdiğinden farklı gösterir (§1.10)."
        ),
    ),
    Question(
        key="d07", concept="yatay-kesitte-sira", note=_note("1.5", "Şekil 1.4"),
        prompt=(
            "Yatay kesit verisinde gözlemlerin tablodaki sırasını değiştirmek çoğu zaman verinin anlamını "
            "değiştirmez."
        ),
        answer=TrueFalse(True),
        explanation=(
            "Yatay kesitte gözlemler aynı zaman noktasına aittir; A ve B öğrencilerinin satır sırası bir bilgi "
            "taşımaz. Zaman serisinde ise sıra bilgidir: 6. ay 5. aydan sonra gelir (§1.5, Şekil 1.4)."
        ),
    ),
    # --- Boşluk doldurma ----------------------------------------------------------
    Question(
        key="b01", concept="gozlem-ve-degisken-sayisi", note=_note("1.2"),
        prompt=(
            "Bir ankette 150 öğrenciye bölüm, yaş ve haftalık çalışma süresi sorulmuştur. Her öğrenciye "
            "ayrıca yalnızca kimlik olarak kullanılan bir anket numarası verilmiştir. Gözlem sayısı "
            "$n$ = **(1)**, analitik değişken sayısı = **(2)**."
        ),
        answer=FillBlanks((NumberBlank(150, 0, "150"), NumberBlank(3, 0, "3"))),
        explanation=(
            "Her öğrenci bir gözlemdir: $n = 150$. Bölüm, yaş ve çalışma süresi analitik değişkenlerdir; "
            "anket numarası yalnızca kimlik etiketi olduğu için sayılmaz (§1.2)."
        ),
    ),
    Question(
        key="b02", concept="alt-grupta-oran", note=_note("1.7", "Tablo 1.1"),
        prompt=(
            "Tablo 1.1'e göre İşletme bölümünde **(1)** öğrenci vardır ve bunların yüzde **(2)**'si dersi "
            "geçmiştir."
        ),
        answer=FillBlanks((NumberBlank(4, 0, "4"), NumberBlank(50, 0.05, "50"))),
        explanation=(
            "İşletme öğrencileri C, E, F ve H'dir; bunlardan E ve F geçmiştir. Geçme yüzdesi "
            "100 × 2/4 = %50'dir. Bütün sınıfta bu yüzde %62,5'tir; alt grubun yüzdesinde payda alt grubun "
            "büyüklüğüdür (§1.7)."
        ),
    ),
    Question(
        key="b03", concept="veri-yapisi-adlari", note=_note("1.5"),
        prompt=(
            "Aynı zaman noktasında çok sayıda birimden toplanan veriye **(1)** verisi, bir değişkenin ardışık "
            "dönemlerde gözlenmesiyle oluşan veriye **(2)** verisi denir."
        ),
        answer=FillBlanks(
            (
                TextBlank(("yatay kesit", "kesit", "yatay-kesit", "cross-sectional", "cross sectional"),
                          "yatay kesit"),
                TextBlank(("zaman serisi", "zaman serileri", "time series"), "zaman serisi"),
            )
        ),
        explanation=(
            "Yatay kesit, aynı veya yaklaşık aynı zamanda farklı birimlerden toplanır (ör. aynı sınavda farklı "
            "öğrenciler). Zaman serisi aynı değişkeni ardışık dönemlerde izler (ör. aylık fiyat endeksi) "
            "(§1.5, Şekil 1.4)."
        ),
    ),
    Question(
        key="b04", concept="anakutle-ve-orneklem-adlari", note=_note("1.8"),
        prompt=(
            "Hakkında bilgi edinmek istediğimiz bütün birimlerin kümesine **(1)**, veri topladığımız alt "
            "kümeye **(2)** denir."
        ),
        answer=FillBlanks(
            (
                TextBlank(("anakütle", "ana kütle", "anakutle", "evren", "population"), "anakütle"),
                TextBlank(("örneklem", "orneklem", "örnek", "sample"), "örneklem"),
            )
        ),
        explanation=(
            "Anakütle (population) çalışmanın hedeflediği bütün birimlerdir; örneklem (sample) bunlardan "
            "gözlediğimiz alt kümedir. Anakütledeki bütün birimlerden veri toplamak tam sayımdır (§1.8)."
        ),
    ),
    Question(
        key="b05", concept="olcme-duzeyi-adlari", note=_note("1.4", "Tablo 1.2"),
        prompt=(
            "Kategori ve anlamlı sıra bilgisi taşıyan ölçme düzeyine **(1)**, eşit farkları anlamlı olan ama "
            "gerçek sıfırı olmayan ölçme düzeyine **(2)** denir."
        ),
        answer=FillBlanks(
            (
                TextBlank(("ordinal", "sıralı", "ordinal ölçek", "sıralı ölçek", "sirali"), "ordinal (sıralı)"),
                TextBlank(("aralık", "aralık ölçeği", "aralik", "interval"), "aralık"),
            )
        ),
        explanation=(
            "Ordinal düzeyde kategoriler sıralanır (düşük < orta < yüksek) ama farklar eşit kabul edilmez. "
            "Aralık ölçeğinde farklar anlamlıdır; Celsius sıcaklığında olduğu gibi sıfır noktası mutlak yokluk "
            "değildir (§1.4, Tablo 1.2)."
        ),
    ),
    Question(
        key="b06", concept="istatistigin-islevleri", note=_note("1.1"),
        prompt=(
            "İstatistik, verileri kullanarak bir olguyu **(1)**, değişkenler arasındaki düzeni görmemize ve "
            "uygun koşullarda örneklemden daha geniş bir grup hakkında **(2)** yapmamıza yardımcı olan "
            "yöntemler bütünüdür."
        ),
        answer=FillBlanks(
            (
                TextBlank(("betimlememize", "betimleme", "betimlemek", "betimlemeye"), "betimlememize"),
                TextBlank(("çıkarım", "istatistiksel çıkarım", "cikarim", "çıkarsama"), "çıkarım"),
            )
        ),
        explanation=(
            "Notlardaki tanım istatistiğin üç işini sayar: betimleme, düzeni görme ve çıkarım. Hesaplama bu "
            "işlerin aracıdır; hangi sayının hangi soruya cevap verdiğini bilmek istatistiğin kendisidir (§1.1)."
        ),
    ),
    # --- Denklem yazma -----------------------------------------------------------
    Question(
        key="e01", concept="oran-formulu", note=_note("1.7"),
        prompt="$n$ öğrenciden $g$'si dersi geçmiştir. Geçme **oranını** yazın.",
        answer=Equation(lhs=r"\text{oran}", symbols=(PASSED, STUDENTS), answer="g/n", shown=r"g/n"),
        explanation=(
            "Oran, ilgilenilen gözlem sayısının toplam gözlem sayısına bölümüdür: Tablo 1.1'de "
            "5/8 = 0,625. Oran 0 ile 1 arasındadır (§1.7)."
        ),
    ),
    Question(
        key="e02", concept="yuzde-formulu", note=_note("1.7"),
        prompt="Aynı sınıf için geçme **yüzdesini** $g$ ve $n$ cinsinden yazın.",
        answer=Equation(lhs=r"\%", symbols=(PASSED, STUDENTS), answer="100*g/n", shown=r"100\,g/n"),
        explanation=(
            "Yüzde, oranın 100 ile çarpımıdır: 100 × 5/8 = %62,5. Türkçe yazımda yüzde işareti sayıdan önce "
            "gelir (§1.7)."
        ),
    ),
    Question(
        key="e03", concept="ortalama-formulu", note=_note("1.7"),
        prompt="$n$ öğrencinin sınav puanlarının toplamı $T$ ise ortalama puanı yazın.",
        answer=Equation(lhs=r"\bar{x}", symbols=(TOTAL, STUDENTS), answer="t/n", shown=r"T/n"),
        explanation=(
            "Ortalama, değerlerin toplamının gözlem sayısına bölümüdür: Tablo 1.1'de 512/8 = 64. Ortalama "
            "kavramı Konu 4'te ayrıntılı işlenir (§1.7)."
        ),
    ),
)


KONU01_QUIZ = QuestionSet(
    topic_key="konu01",
    title="Konu 1: Kendini sına",
    questions=QUESTIONS,
    intro=(
        "Bu set haftanın temel kavramlarını sınar. Her soru tek bir kavrama odaklanır ve notlardaki bir "
        "bölüme bağlıdır; yanlış cevaplarınız için tekrar edilecek bölümler en üstte listelenir. Notlardaki "
        "egzersiz ve mini quiz maddelerini tekrar etmez, onları tamamlar."
    ),
    sections=("1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8", "1.9", "1.10", "1.11"),
)
