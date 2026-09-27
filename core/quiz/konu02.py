"""Konu 2 "Kendini sına" soru seti.

Her soru tek bir kavramı sınar ve notlardaki bir bölüme bağlıdır. Sorular notların egzersiz ve
mini quiz maddelerini tekrar etmez; yeni sayılarla aynı becerileri sınar. Sayısal cevaplar testlerde
doğrudan hesaplanarak doğrulanır.
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
        key="k01", concept="frekans-toplami-kontrolu", note=_note("2.2", "(2.1)"),
        prompt=(
            "Kırk öğrencinin katıldığı bir ankette frekans tablosundaki frekansların toplamı 42 çıkıyor. "
            "En olası açıklama hangisidir?"
        ),
        answer=MultipleChoice(
            (
                "Frekansların toplamı n'yi her zaman aşabilir; sorun yoktur.",
                "Bazı öğrenciler birden fazla kategoriye yazılmış ya da sayımda hata yapılmıştır.",
                "Göreli frekanslar henüz hesaplanmamıştır.",
                "Kategori sayısı gözlem sayısından fazladır.",
            ),
            correct=1,
        ),
        explanation=(
            "Kategoriler birbirini dışlıyorsa her öğrenci tek bir kategoriye düşer ve $\\sum f_j = n$ olur. "
            "Toplam n'yi aşıyorsa kategoriler çakışıyordur (ör. hem \"toplu taşıma\" hem \"otobüs\") ya da "
            "sayımda veya veri girişinde hata vardır (§2.2, (2.1))."
        ),
    ),
    Question(
        key="k02", concept="farkli-buyuklukte-gruplar", note=_note("2.3"),
        prompt=(
            "Merkez kampüste 2.000 öğrencinin 250'si, yeni kampüste 300 öğrencinin 135'i özel araçla geliyor. "
            "Hangi ifade doğrudur?"
        ),
        answer=MultipleChoice(
            (
                "Özel araç payı yeni kampüste daha yüksektir: %45'e karşı %12,5.",
                "Özel araç merkez kampüste daha yaygındır, çünkü 250 > 135.",
                "Kampüslerin büyüklüğü farklı olduğu için karşılaştırma yapılamaz.",
                "Frekanslar ve yüzdeler her zaman aynı sonucu verir.",
            ),
            correct=0,
        ),
        explanation=(
            "Frekans \"kaç öğrenci?\" sorusunu, yüzde \"toplamın ne kadarı?\" sorusunu cevaplar. Büyüklükleri "
            "farklı grupları karşılaştırırken yüzde kullanılır: 135/300 = %45, 250/2.000 = %12,5 "
            "(§2.3; Sezgi, Deney 1)."
        ),
    ),
    Question(
        key="k03", concept="sutun-grafiginin-ustunlugu", note=_note("2.6", "Şekil 2.6"),
        prompt=(
            "Birbirine yakın yüzdeleri karşılaştırmak için sütun grafiği neden dilim grafiğinden genellikle "
            "daha etkilidir?"
        ),
        answer=MultipleChoice(
            (
                "Sütun grafiği daha çok renk kullanır.",
                "Dilim grafiği yüzdeleri gösteremez.",
                "Sütunlar ortak bir tabandan başlar ve göz uzunlukları açı ve alanlardan daha hassas karşılaştırır.",
                "Sütun grafiğinde kategorilerin toplamı her zaman 100'dür.",
            ),
            correct=2,
        ),
        explanation=(
            "Dilim grafiği bütünün parçalarını gösterir ama açı ve alan karşılaştırması zordur. Şekil 2.6'da "
            "%15 ile %12,5 arasındaki fark, sütunlar ortak tabandan başladığı için sütun grafiğinde daha "
            "kolay görülür (§2.6)."
        ),
    ),
    Question(
        key="k04", concept="marjinal-toplamlarin-toplami", note=_note("2.7", "Tablo 2.4"),
        prompt=(
            "Bir çapraz tabloda satır toplamlarının toplamı ile sütun toplamlarının toplamı arasındaki ilişki "
            "nedir?"
        ),
        answer=MultipleChoice(
            (
                "Satır toplamlarının toplamı her zaman daha büyüktür.",
                "Aralarında sabit bir ilişki yoktur.",
                "Sütun sayısına göre değişir.",
                "İkisi de genel toplam n'ye eşittir.",
            ),
            correct=3,
        ),
        explanation=(
            "Her gözlem tek bir satıra ve tek bir sütuna düşer. Bu yüzden satır toplamları da sütun toplamları "
            "da bütün gözlemleri bir kez sayar: Tablo 2.4'te 40 + 20 = 22 + 26 + 12 = 60 (§2.7)."
        ),
    ),
    Question(
        key="k05", concept="sutun-yuzdesinin-paydasi", note=_note("2.8", "Tablo 2.4"),
        prompt=(
            "Tablo 2.4'e göre \"Dijital materyali tercih edenlerin yüzde kaçı İşletme öğrencisidir?\" "
            "sorusunda payda hangisidir?"
        ),
        answer=MultipleChoice(
            (
                "26: Dijital sütununun toplamı",
                "20: İşletme satırının toplamı",
                "60: genel toplam",
                "8: İşletme ∩ Dijital hücresi",
            ),
            correct=0,
        ),
        explanation=(
            "Soru \"dijital tercih edenlerin\" içinde bir pay istiyor; payda dijital sütununun toplamıdır: "
            "8/26 × 100 ≈ %30,8. \"İşletme öğrencilerinin yüzde kaçı dijital tercih ediyor?\" sorusunun "
            "paydası ise 20'dir (§2.8)."
        ),
    ),
    Question(
        key="k06", concept="yigilmis-grafikte-zor-karsilastirma", note=_note("2.9", "Şekil 2.9"),
        prompt="Yüzde 100 yığılmış sütun grafiğinde hangi karşılaştırma en zordur?",
        answer=MultipleChoice(
            (
                "Her grubun toplamının %100 olduğunu görmek",
                "İki grubun ortadaki parçalarını (ör. \"Dijital\") karşılaştırmak",
                "Her grubun iç bileşimini tek sütunda görmek",
                "En alttaki parçaları karşılaştırmak",
            ),
            correct=1,
        ),
        explanation=(
            "En alttaki parçalar ortak tabandan (0) başlar; ortadaki parçaların ise ortak bir başlangıç çizgisi "
            "yoktur. Bu yüzden yığılmış grafik iç bileşimi özetler ama orta kategorilerde küçük farkları "
            "karşılaştırmayı zorlaştırır (§2.9, Şekil 2.9)."
        ),
    ),
    Question(
        key="k07", concept="paradoksun-kosulu", note=_note("2.11", "Tablo 2.6"),
        prompt=(
            "B tasarımı hem kolay hem zor müşteri grubunda A'dan daha yüksek dönüşüm oranına sahiptir. "
            "Aşağıdaki durumların hangisinde gruplar birleştirildiğinde A'nın daha yüksek görünmesi "
            "**mümkün değildir**?"
        ),
        answer=MultipleChoice(
            (
                "Kolay grup zor gruptan büyük olduğunda",
                "Dönüşüm oranları %50'nin üzerinde olduğunda",
                "İki tasarım da kolay ve zor gruplara aynı oranda gösterildiğinde",
                "Her tasarım 1.000'den fazla müşteriye gösterildiğinde",
            ),
            correct=2,
        ),
        explanation=(
            "Genel oran, alt grup oranlarının o tasarımı görenler içindeki grup paylarıyla birleşimidir. Paylar "
            "iki tasarımda aynıysa B'nin her gruptaki üstünlüğü toplama da taşınır. Tablo 2.6'da A'yı "
            "görenlerin %91'i, B'yi görenlerin yalnız %33'ü kolay gruptadır (§2.11; Sezgi, Deney 3)."
        ),
    ),
    # --- Doğru–yanlış -------------------------------------------------------------
    Question(
        key="d01", concept="kayit-sirasi-frekansi-degistirmez", note=_note("2.1", "Tablo 2.1"),
        prompt="Tablo 2.1'deki 40 kaydın sırası değiştirilse de frekans dağılımı aynı kalır.",
        answer=TrueFalse(True),
        explanation=(
            "Frekans dağılımı her kategoride kaç gözlem olduğunu sayar; kayıtların hangi sırayla yazıldığı "
            "sayımı etkilemez. Özet bilgiyi yoğunlaştırır: kayıtların sırası özetin parçası değildir (§2.1)."
        ),
    ),
    Question(
        key="d02", concept="siralama-frekansi-degistirmez", note=_note("2.5", "Şekil 2.4"),
        prompt="Nominal bir değişkenin sütunlarını frekansa göre sıralamak frekans değerlerini değiştirir.",
        answer=TrueFalse(False),
        explanation=(
            "Sıralama yalnızca sunumu değiştirir; her kategorinin frekansı aynı kalır. Şekil 2.3 ile Şekil 2.4 "
            "aynı sayıları gösterir; sıralı grafik yalnızca karşılaştırmayı kolaylaştırır (§2.5)."
        ),
    ),
    Question(
        key="d03", concept="frekans-ve-yuzde-grafigi", note=_note("2.4", "Şekil 2.3"),
        prompt=(
            "Aynı veri için frekans sütun grafiği ile yüzde sütun grafiği kategorilerin sıralamasını "
            "değiştirmez; yalnızca dikey eksenin ölçeği değişir."
        ),
        answer=TrueFalse(True),
        explanation=(
            "Yüzde, her frekansın aynı $n$'ye bölünüp 100 ile çarpılmasıdır. Bütün sütunlar aynı oranda "
            "ölçeklendiği için sütunların birbirine göre durumu değişmez (§2.4)."
        ),
    ),
    Question(
        key="d04", concept="satir-yuzdesi-grup-buyuklugunden-bagimsiz", note=_note("2.8", "Tablo 2.5"),
        prompt=(
            "Bölümlerin büyüklüğü değişse de satır yüzdeleri her bölümün kendi içindeki tercih dağılımını "
            "yansıtır."
        ),
        answer=TrueFalse(True),
        explanation=(
            "Satır yüzdesinin paydası satır toplamıdır; her bölüm kendi içinde %100'e tamamlanır. Sütun "
            "yüzdeleri ise bölüm büyüklüklerine bağlıdır: kalabalık bölüm her sütunda daha büyük pay alır "
            "(§2.8; Sezgi, Deney 2)."
        ),
    ),
    Question(
        key="d05", concept="kesik-eksenin-yonu", note=_note("2.10", "Şekil 2.10"),
        prompt=(
            "Sütun grafiğinde dikey ekseni %70'ten başlatmak, %72 ile %78 arasındaki farkı olduğundan küçük "
            "gösterir."
        ),
        answer=TrueFalse(False),
        explanation=(
            "Kesilmiş eksende sütun boyları farkı abartır: Şekil 2.10'un solunda 6 yüzde puanlık fark çok büyük "
            "görünür. Sütun uzunluğu büyüklüğü temsil ettiği için değer ekseni genel olarak sıfırdan "
            "başlamalıdır (§2.10)."
        ),
    ),
    Question(
        key="d06", concept="yatay-sutun-grafigi", note=_note("2.12", "Şekil 2.11"),
        prompt="Yatay sütun grafiği yalnızca kategoriler ordinal olduğunda kullanılabilir.",
        answer=TrueFalse(False),
        explanation=(
            "Yatay sütun grafiği özellikle kategori adları uzunsa etiketleri okunur kılar. Şekil 2.11'deki ana "
            "çalışma kaynağı nominal bir değişkendir ve yatay grafikle gösterilmiştir (§2.12)."
        ),
    ),
    Question(
        key="d07", concept="marjinal-toplam-tek-degisken", note=_note("2.7", "Tablo 2.4"),
        prompt=(
            "Çapraz tablonun son satırı ve son sütunu (marjinal toplamlar) tek bir değişkenin frekans "
            "dağılımını verir."
        ),
        answer=TrueFalse(True),
        explanation=(
            "Son sütun bölümlerin frekanslarını (40, 20), son satır materyal tercihlerinin frekanslarını "
            "(22, 26, 12) verir. Hücreler ise iki kategorinin birleşimidir (§2.7, Tablo 2.4)."
        ),
    ),
    # --- Boşluk doldurma ----------------------------------------------------------
    Question(
        key="b01", concept="goreli-ve-yuzde-hesabi", note=_note("2.3"),
        prompt=(
            "Bir kafede 50 müşteriden 18'i çay, 22'si kahve, 10'u meyve suyu tercih etmiştir. Kahvenin göreli "
            "frekansı **(1)**, çayın yüzde frekansı **(2)**'dir."
        ),
        answer=FillBlanks((NumberBlank(0.44, 0.005, "0,44"), NumberBlank(36, 0.05, "36"))),
        explanation=(
            "Göreli frekans $r = f/n$: kahve için 22/50 = 0,44. Yüzde frekans $p = 100\\,r$: çay için "
            "100 × 18/50 = %36. Kontrol: 0,36 + 0,44 + 0,20 = 1 (§2.3)."
        ),
    ),
    Question(
        key="b02", concept="aci-ve-yuzde-donusumu", note=_note("2.6", "(2.4)"),
        prompt=(
            "Yüzde frekansı %15 olan bir kategorinin dilim açısı **(1)** derecedir; dilim açısı 45° olan bir "
            "kategorinin göreli frekansı **(2)**'dir."
        ),
        answer=FillBlanks((NumberBlank(54, 0.05, "54"), NumberBlank(0.125, 0.0005, "0,125"))),
        explanation=(
            "Dilim açısı θ = 360° × r'dir: 360 × 0,15 = 54°. Ters yönde r = θ/360: 45/360 = 0,125. Şekil 2.5'te "
            "yürüme (%15) 54°, özel araç (%12,5) 45° kaplar (§2.6, (2.4))."
        ),
    ),
    Question(
        key="b03", concept="payda-secimi-yeni-veri", note=_note("2.8"),
        prompt=(
            "Bir firmada 40 kadın ve 60 erkek çalışan vardır; uzaktan çalışanlar 10 kadın ve 20 erkektir. "
            "Kadın çalışanların yüzde **(1)**'i uzaktan çalışır; uzaktan çalışanların yüzde **(2)**'si "
            "kadındır (bir ondalık)."
        ),
        answer=FillBlanks((NumberBlank(25, 0.05, "25"), NumberBlank(33.33, 0.05, "33,3"))),
        explanation=(
            "İlk soruda payda kadın çalışanların sayısıdır (satır toplamı): 10/40 = %25. İkinci soruda payda "
            "uzaktan çalışanların sayısıdır (sütun toplamı): 10/30 ≈ %33,3. Aynı hücre (10) iki farklı "
            "paydaya bölünür (§2.8)."
        ),
    ),
    Question(
        key="b04", concept="simpson-hesabi", note=_note("2.11"),
        prompt=(
            "Kolay grupta A tasarımını 50 müşteri görmüş, 45'i dönüşmüş; B'yi 20 müşteri görmüş, 19'u "
            "dönüşmüştür. Zor grupta A'yı 10 müşteri görmüş, 2'si dönüşmüş; B'yi 40 müşteri görmüş, 12'si "
            "dönüşmüştür. Gruplar birleştirildiğinde A'nın dönüşüm oranı yüzde **(1)**, B'ninki yüzde **(2)**'dir "
            "(bir ondalık)."
        ),
        answer=FillBlanks((NumberBlank(78.33, 0.05, "78,3"), NumberBlank(51.67, 0.05, "51,7"))),
        explanation=(
            "Her iki grupta B daha yüksektir (%95 > %90 ve %30 > %20); fakat birleşik oranlar A için "
            "47/60 ≈ %78,3, B için 31/60 ≈ %51,7'dir. A'nın gözlemlerinin çoğu kolay gruptadır: Simpson "
            "paradoksu (§2.11)."
        ),
    ),
    Question(
        key="b05", concept="yuzde-puan-ve-goreli-artis", note=_note("2.10"),
        prompt=(
            "İşsizlik oranı %10'dan %12'ye çıkmıştır. Artış **(1)** yüzde puandır; göreli artış ise yüzde "
            "**(2)**'dir."
        ),
        answer=FillBlanks((NumberBlank(2, 0.005, "2"), NumberBlank(20, 0.05, "20"))),
        explanation=(
            "Yüzde puan iki yüzdenin farkıdır: 12 − 10 = 2. Göreli artış farkın başlangıç değerine oranıdır: "
            "(12 − 10)/10 × 100 = %20. \"Yüzde\" ile \"yüzde puan\" aynı kavram değildir (§2.10)."
        ),
    ),
    # --- Denklem yazma -----------------------------------------------------------
    Question(
        key="e01", concept="goreli-frekans-formulu", note=_note("2.3", "(2.2)"),
        prompt="Bir kategorinin frekansı $f$, toplam gözlem sayısı $n$ ise göreli frekansını yazın.",
        answer=Equation(
            lhs="r",
            symbols=(Symbol("f", "f", "kategorinin frekansı", 1, 10), Symbol("n", "n", "gözlem sayısı", 11, 50)),
            answer="f/n",
            shown="f/n",
        ),
        explanation=(
            "Göreli frekans, frekansın toplam gözlem sayısına bölümüdür: otobüs için 16/40 = 0,40. Bütün "
            "kategorilerin göreli frekansları 1'e toplanır (§2.3, (2.2))."
        ),
    ),
    Question(
        key="e02", concept="yuzdeden-aciya", note=_note("2.6", "(2.4)"),
        prompt="Yüzde frekansı $p$ olan bir kategorinin dilim açısını (derece) $p$ cinsinden yazın.",
        answer=Equation(
            lhs=r"\theta",
            symbols=(Symbol("p", "p", "yüzde frekans", 1, 100),),
            answer="360*p/100",
            shown=r"360\,p/100 = 3{,}6\,p",
        ),
        explanation=(
            "Dilim açısı θ = 360° × r ve r = p/100'dür; bu yüzden θ = 3,6 p. Otobüs için p = 40 ise "
            "θ = 144° (§2.6, (2.4))."
        ),
    ),
    Question(
        key="e03", concept="goreli-artis-formulu", note=_note("2.10"),
        prompt="Bir oran %$a$'dan %$b$'ye çıkmıştır. Göreli artışı yüzde olarak $a$ ve $b$ cinsinden yazın.",
        answer=Equation(
            lhs=r"\%\Delta",
            symbols=(Symbol("a", "a", "başlangıç yüzdesi", 5, 50), Symbol("b", "b", "yeni yüzde", 51, 95)),
            answer="100*(b-a)/a",
            shown=r"100\,(b-a)/a",
        ),
        explanation=(
            "Göreli artış farkın başlangıç değerine oranıdır: (78 − 72)/72 × 100 ≈ %8,3. Farkın kendisi "
            "(b − a) ise yüzde puan cinsindendir (§2.10)."
        ),
    ),
    Question(
        key="e04", concept="satir-yuzdesi-formulu", note=_note("2.8", "Tablo 2.5"),
        prompt=(
            "Bir çapraz tabloda bir hücrenin frekansı $h$, o hücrenin satır toplamı $S$ ise satır yüzdesini "
            "yazın."
        ),
        answer=Equation(
            lhs=r"\text{satır yüzdesi}",
            symbols=(
                Symbol("h", "h", "hücre frekansı", 1, 10),
                Symbol("s", "S", "satır toplamı", 11, 60, aliases=("S",)),
            ),
            answer="100*h/s",
            shown=r"100\,h/S",
        ),
        explanation=(
            "Satır yüzdesinin paydası satır toplamıdır: İktisat ∩ Dijital için 100 × 18/40 = %45. Sütun "
            "yüzdesinde payda sütun toplamı olurdu (§2.8, Tablo 2.5)."
        ),
    ),
    Question(
        key="e05", concept="genel-oran-bilesimi", note=_note("2.11", "Tablo 2.6"),
        prompt=(
            "A tasarımını gören müşterilerin $a$ payı kolay gruptadır. Kolay gruptaki dönüşüm oranı $k$, zor "
            "gruptaki $z$ ise A'nın bütün müşterilerdeki dönüşüm oranını yazın."
        ),
        answer=Equation(
            lhs=r"\text{genel oran}",
            symbols=(
                Symbol("a", "a", "kolay grubun payı", 0.05, 0.95),
                Symbol("k", "k", "kolay gruptaki dönüşüm oranı", 0.5, 1.0),
                Symbol("z", "z", "zor gruptaki dönüşüm oranı", 0.0, 0.5),
            ),
            answer="a*k + (1-a)*z",
            shown=r"a\,k + (1-a)\,z",
        ),
        explanation=(
            "A'yı gören N müşterinin aN'si kolay gruptadır ve bunların k payı dönüşür; (1 − a)N'si zor "
            "gruptadır ve z payı dönüşür. Dönüşenlerin toplamı N'ye bölünür: a k + (1 − a) z. Tablo 2.6'da "
            "0,909 × 0,90 + 0,091 × 0,10 ≈ 0,827 (§2.11)."
        ),
    ),
)


KONU02_QUIZ = QuestionSet(
    topic_key="konu02",
    title="Konu 2: Kendini sına",
    questions=QUESTIONS,
    intro=(
        "Bu set haftanın temel kavramlarını sınar. Her soru tek bir kavrama odaklanır ve notlardaki bir "
        "bölüme bağlıdır; yanlış cevaplarınız için tekrar edilecek bölümler en üstte listelenir. Notlardaki "
        "egzersiz ve mini quiz maddelerini tekrar etmez, yeni sayılarla onları tamamlar."
    ),
    sections=("2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "2.8", "2.9", "2.10", "2.11", "2.12"),
)
