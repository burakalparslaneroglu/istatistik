# Mimari

## İlke

Ders notları konu sırasını, terminolojiyi, notasyonu, matematik düzeyini ve pedagojik kapsamı belirler.
Uygulama notları tekrar etmez; notlardaki çözümlü örnekleri çalışır hâle getirir, kontrollü simülasyonlarla
sezgi kurar ve kavramları sınar.

## Katmanlar

- `app.py`: ortak kabuk, konu seçimi (`selected_topic`), kod dili seçimi (`code_language`), metin ölçeği.
- `core/`: Streamlit'ten bağımsız hesap, tanım ve metadata.
- `topics/`: Streamlit bileşenleri ve öğrenciye gösterilen metin.
- `tests/`: sözleşme, sayısal doğruluk, üretilen kod ve AppTest denetimleri.

## Yeni yapı (Konu 1–12)

| Dosya | Görev |
|---|---|
| `core/topic_registry.py`, `core/types.py` | 12 konunun başlığı (ders notlarındaki bölüm adı), kısa adı ve yönlendirici sorusu |
| `core/labs/spec.py` | Uygulama tanım şeması: işlemler, notlardaki sayılar (`Check`), tekrarlanabilirlik sınıfı |
| `core/labs/expr.py` | Türetilmiş değişken ve skalerler için küçük ifade dili; pandas'ta değerlendirilir, iki dile çevrilir |
| `core/labs/tables.py` | Frekans tablosu, çapraz tablo (sayı, satır ve sütun yüzdesi, ağırlıklı toplam), sayımdan gözlem verisi, çok aşamalı deneyin sonuçları, kombinasyon ve permütasyon listeleri, kategorik, kesikli ve sayım çekilişi, sınıf tablosu, gövde–yaprak, yüzdelik, kutu grafiği özeti, olasılık ağacının yerleşimi, olası değerler, dikdörtgen orta noktaları, yoğunluk eğrisi |
| `core/labs/runner.py` | Tanımı çalıştırır ve notlarla karşılaştırır |
| `core/labs/konuNN.py`, `core/labs/registry.py` | Konu uygulamaları |
| `core/labs/sezgi.py`, `core/labs/sezgi_konuNN.py` | Sezgi deneylerinin şeması ve konu deneyleri |
| `core/codegen/` | Python (`python_gen.py`) ve temel R (`r_gen.py`) üreticileri |
| `core/quiz/` | Soru türleri, notlandırma, güvenli formül okuma ve konu soru setleri |
| `core/charts.py` | Plotly grafikleri; `show_figure` tek `st.plotly_chart` çağrısıdır ve eksen adı ister |
| `topics/lab_ui.py`, `topics/sim_ui.py`, `topics/quiz_ui.py` | Üç sekmenin ortak arayüzü |
| `core/labs/ornek.py`, `core/labs/ornekler.py` | Uygulama sekmesinin ek veri kaynakları: örnek (`Case`), rol (`Role`), ayar (`Setting`), ayrı okunan sütun (`SeparateColumn`), kendi verini yükle tanımı (`CustomLab`), seçimlerden örneğe (`custom_case`), metinler için kesin ondalık sayılar (`kesin`, `ondalik`, `kesin_esit`) ve kayıt |
| `core/labs/ornek_konuNN.py` | Konunun genel uygulaması (notlardaki adımlar, verisi değiştirilebilir), kurgusal alternatif örnek ve kendi verini yükle rolleri |
| `core/labs/kendi_veri.py` | Yüklenen dosyayı okuma (Excel; CSV için ayırıcı, ondalık işareti ve kodlamanın algılanması), kodda kullanılacak sütun adları, Türkçe sıralama, temizleme ve doğrulama |
| `topics/kendi_veri_ui.py` | Kendi verini yükle paneli: dosya yükleme, örnek dosya, sütun ve kategori seçimi, tür tablosu, ayar kaydırıcıları |
| `topics/shared.py` | Konu başlığı ve yönlendirici soru |

Eski yapı (konuya özel `core/topicNN_logic.py` modülleri, `core/question_engine.py` ve
`core/ui_components.render_plotly`) Konu 11–12'nin taşınmasıyla kaldırıldı; `core/ui_components.py` yalnız stil
dosyasını yükler.

## Uygulama akışı

Bir konu uygulaması tek bir `LabSpec` tanımıdır ve dört çıktıyı birlikte besler:

1. `topics/lab_ui.py` adımları, tabloları, grafikleri ve kodu gösterir. Her adımda o adımın sonundaki durum
   gösterilir; sonraki adımların eklediği sütunlar görünmez. Satır içi veri, aynı adımda bütün sütunlarını
   gösteren bir `ShowFrame` ile sonuçlanıyorsa yalnız girdi sütunlarıyla gösterilir (tablo iki kez görünmez).
2. `core/labs/runner.py` hesabı yapar; her `Check` notlarda basılı bir sayıdır ve tolerans basılı basamak
   sayısıdır (0,5 × 10⁻ᵈ). Notlar dışındaki kaynaklarda beklenen değer uygulamanın hesabıdır; üretilen koddaki
   tolerans max(0,5 × 10⁻ᵈ, 10⁻¹² × |beklenen|) + 10⁻¹²'dir (çok büyük değerlerde toplamların son basamakları dilden
   dile değişebilir; yanlış bir kural, ör. yazılımın varsayılan yüzdeliği, yine yakalanır).
3. `core/codegen/` aynı işlemleri Python ve R'ye çevirir; tam betik sonunda sonuçları notlardaki sayılarla
   karşılaştırır.
4. `tests/test_all_labs.py` uygulamanın ve üretilen Python/R kodunun notlardaki sayıları ürettiğini doğrular.

Adımlar notların bölüm sırasını izler (`NoteRef("2.8")`); işlemsiz (yalnız metin) adım yalnız son adım
olabilir. Veriler notlardaki küçük veri setleridir: `InlineData` tabloyu satır satır yazar, `FromCounts`
sayım tablosunun her satırını sayısı kadar tekrarlayarak gözlem düzeyinde veri kurar. Tablolar ve çapraz
tablolar bu veriden yeniden sayılır; yani notlardaki sayılar girdi değil, hesabın sonucudur.

Çapraz tabloda yüzde türü paydayı belirler: `percent="satir"` her satırı, `percent="sutun"` her sütunu 100'e
tamamlar. `Toplam` satırı ve sütunu iki dilde aynı adla eklenir; grafiklerde çizilmez.

## Veri kaynağı: notlardaki örnek, alternatif örnek, kendi verini yükle

Kayıtta (`core/labs/ornekler.py`) ek kaynağı olan konularda Uygulama sekmesinin en üstünde üç seçenek vardır.
Notlardaki örnek varsayılandır; onun tanımı (`core/labs/konuNN.py`), üretilen kodu ve kontrolleri değişmez.

- **Genel uygulama** (`core/labs/ornek_konuNN.build`): notlardaki adımlar aynı numaralar ve aynı bölüm bağlarıyla,
  fakat veri bir `Case`'ten gelir. `Case` veriyi kuran işlemleri, temizlenmiş veriyi, rolleri (rol → sütun),
  ekranda görünen adları, kategori sıralarını ve seçilen kategorileri taşır. Metinler veriden kurulur: sayı ve
  kategori adları metne eklenir, fakat değişken bir sayıya ya da kategori adına Türkçe ek getirilmez ("Şube =
  Merkez", "{sayı} gözlem" gibi kalıplar).
- **Alternatif örnek:** genel uygulamanın kurgusal bir veriyle kurulmuş hâlidir (satır içi veri). Veri,
  notlardaki öğretim noktasını gösterecek biçimde seçilir (ör. Konu 2'de Simpson paradoksu, Konu 1'de 25 bin
  TL hedefi).
- **Kendi verini yükle:** öğrenci Excel (.xlsx) ya da CSV dosyası yükler, her rol için bir sütun seçer. Gereken rol
  seçilmemişse adım işlem içermez ve hangi sütunun gerektiğini söyler. Konu 1'de öğrenci her sütunun
  istatistiksel türünü de seçer; kimlik sütununun türü sabittir, sayısal rol nicel, iki kategorili rol kategorik
  olmalıdır. Öneriler reddedilecek sütunları (tarih, gözlem numarası gibi) atlar.
- **Ayarlar (`Setting`):** konuya özgü tam sayı ayarları (Konu 3'te sınıf sayısı k, 5–20) veri panelinde
  kaydırıcıdır; başlangıç değeri veriden önerilir (Konu 3: ⌈1 + log₂ n⌉, Sturges kuralı). Kaydırıcının anahtarı
  dosyaya, Excel sayfasına ve rol seçimine bağlıdır; bunlar değişince öneri yeniden hesaplanır. Ayardan bağımsız
  denetimler (`CustomLab.validate`) kaydırıcıdan önce çalışır; ayara bağlı bir hata (ör. sınıf sınırları iki dilde
  aynı yazılamıyor) kaydırıcının altında gösterilir.
- **Ayrı okunan sütun (`Role.separate`):** diğer sütunlardan kısa olabilen bir sütun (Konu 4'te dönemlik yüzde
  değişimler) ana veriden ayrı, kendi `ReadFile` işlemiyle ve yalnız dolu hücreleriyle, dosyadaki sırayla okunur
  (`SeparateColumn`, `Case.extra["separate"]`). Ana verinin satır çıkarma kuralı ve boş hücre notları ona
  uygulanmaz; sütunda hiç dolu hücre yoksa ileti verilir.
- **Kontroller:** notlar dışındaki kaynaklarda beklenen değerler uygulamanın kendi hesabıdır (`with_app_values`);
  indirilen kod bu değerleri yeniden üretmelidir. Kontrol satırına beklenen değer gösterilen basamaktan iki basamak
  fazlasıyla yazılır (`codegen.base.expected_text`; notlarda basılı değer olduğu gibi): yuvarlanmış değer iki
  gösterimin ortasına yakınsa iki dilin son basamaktaki küçük farkı toleransı (0,5·10⁻ᵈ) aşmaz. Alternatif
  örneklerin değerleri testlerde motordan bağımsız bir hesapla doğrulanır. Notların üretilen kodu (betik, adım
  kodları, Sezgi betikleri; iki dil) konu başına md5 özetiyle kilitlidir (`test_notes_outputs_are_unchanged`).
- **Adım kodu:** notlar dışındaki kaynaklarda önceki bir adımın skalerini kullanan adımın kodu "Önceki adımlar
  çalıştırılmış olmalıdır" notunu taşır (`Generator.depends_on_earlier`); notların adım kodları değişmez.
- **Alt çerçeve (`Subset`):** bir sütunun bir değerine eşit satırlar yeni bir çerçeve olur (Konu 5'te iki grup;
  Python `df[df[s] == v]`, R `%in%`: boş hücreli satır hiçbir gruba girmez).
- **Dosya okuma (`ReadFile`):** kod dosyayı okur (Python `pd.read_excel`/`pd.read_csv`, R `readxl::read_excel`/
  `read.csv`; boş hücre ve `NA` eksik değer), seçilen sütunları ASCII adlarla yeniden adlandırır ve metin
  hücrelerini iki dilde aynı kuralla temizler: bölünmez boşluk boşluğa çevrilir, baştaki ve sondaki boşluklar
  silinir, boş kalan hücre ve `NA` eksik değerdir. Sütun türü dönüştürülür: kategorik metin, tam sayı kodlu
  kategori ("1", "2"; R'de `sprintf("%.0f")`, 32 bit sınırı yok), sayı ya da metin olarak saklanmış sayı. R, CSV
  dosyasının bütün sütunlarını metin olarak okur ve sayıları açıkça dönüştürür. Uygulama aynı kuralları
  `core/labs/kendi_veri` ile uygular (`clean_text`, `code_text`); tanım temizlenmiş değerleri taşır. CSV'de
  ayırıcı, ondalık işareti ve kodlama (dosyanın tamamı UTF-8 ya da Windows-1254 olarak çözülür) algılanır ve kodda
  açıkça yazılır. R'nin metinden sayı okuması altı ve daha çok ondalık basamakta son ikili basamakta pandas'tan
  ayrılabildiği için böyle bir CSV sütunu R'de `round(as.numeric(…), d)` ile okunur (d: sütunun basamağı; daha az
  basamakta kod değişmez).
- **Boş hücreler:** satırlar yalnız zorunlu rolün (ör. ana değişken) boş hücreleri yüzünden çıkarılır. İsteğe
  bağlı bir rolü kullanan adım kendi tam gözlemlerini seçer (`CompleteCases`: Konu 2'de çapraz tablo ve Simpson
  adımları, Konu 4'te ağırlıklı ortalama) ve kaç gözlemle çalıştığını söyler; yalnız tabloda gösterilen sütunlardaki boşluklar yerinde kalır.
  Konu 1'de kimlik, iki kategorili ve zaman sütunu seçilirse boş hücre içeremez.
- **Reddedilen dosya ve sütunlar:** iki dilin aynı sonucu vereceği güvence altına alınamıyorsa açık bir ileti
  verilir. Dosya düzeyinde: ilk satırı boş sayfa, aynı adı taşıyan sütunlar (adlar temizlendikten sonra), başlıkta
  veri satırlarından az alan, hücre ortasında tırnak işareti, yalnız boşluk içeren satır, UTF-16 kodlama. Sütun
  düzeyinde (seçeneklere alınmaz, not düşülür): adı sayı ya da tarih olan, adsız, adı "NA" olan ya da adında
  tırnak, ters bölü veya denetim karakteri bulunan sütunlar. Seçimde: tarih, DOĞRU/YANLIŞ, sonsuz değer, metinle
  karışık ondalık ya da çok büyük sayı, binlik ayırıcılı, ondalık işareti karışık ya da belirsiz (ayırıcıdan sonra
  hep üç basamak) metin sayılar; CSV'de 15'ten fazla anlamlı basamaklı sayılar (ör. 0,30000000000000004: pandas
  ile R son basamakta farklı okuyabilir; Excel dosyasında sayılar ikili değerle okunduğu için sorun yoktur).
  Konuya özgü: bütün değerleri aynı sayısal sütun (Konu 3–5); Konu 5'te x ile y için aynı sütun, x'in ya da bir
  grubun değerleri büyüklüklerine göre çok yakın (en büyük − en küçük < 10⁻⁷ × büyüklük), iki gözlemden az olan grup;
  Konu 6'da iki olay için aynı sütun ve ekip büyüklüğünü aşan seçim (kaydırıcının altında); Konu 4'te değerleri
  büyüklüklerine göre birbirine çok yakın sütun (en büyük − en küçük < 10⁻⁹ × büyüklük; grafik eksenleri farkı
  gösteremez); Konu 3'te |x| ≥ 10¹⁰ olan değerler ve hiçbir sınıf sayısının (5–20) sınırlarını iki dilde aynı
  yazamadığı veri (çok küçük ya da çok basamaklı değerler; ileti çarpma ya da ortak sayı çıkarma önerir). Yalnız
  seçilen sınıf sayısı işe yaramıyorsa hata kaydırıcının altında görünür ve çalışan sınıf sayılarını listeler.
- **Metinlere giren adlar:** öğrencinin sütun ve kategori adları Markdown işaretleri kaçırılarak (`ornek.md`)
  yazılır ve hiçbir zaman matematik ifadesine girmez. "=" ile "≈" gösterilen değerin tam olup olmamasına göre
  seçilir (`ornek.esit`, göreli 10⁻¹²).
- **Kesin değerler (Konu 4; Konu 3'te Adım 2 ve 5):** metindeki sayılar ve eşitlik yargıları verinin kısa ondalık
  yazımından kurulan kesin değerlerle verilir (`ornek.kesin`, `ondalik`, `kesin_esit`): ortalamanın veride gözlenip
  gözlenmediği, medyanın ortalamaya eşitliği, iki yüzdelik kuralının aynı sonucu verip vermediği tam olarak
  karşılaştırılır. Verinin ondalık basamağı d, her değerin 15 anlamlı basamaklı yazımından okunur (0,1000001 → 7;
  kayan nokta gürültüsü 0,30000000000000004 → 1) ve en büyük değerde 15 anlamlı basamağı aşmaz
  (`data_decimals`). Gösterim basamağı: veriden doğrudan gelen değerler d, medyan ve yüzdelikler kesin değerleri
  (en çok d + 2), ortalamalar en az 2, d + 1 ve 3 anlamlı basamak; en çok 15 anlamlı basamak. İki gösterimin tam
  ortasındaki bir değer (49,475) bir basamak daha yazılır (`yarim_basamak`); böylece metin ile tablo aynı sayıyı
  gösterir. Düzyazıda yuvarlanmış sayının ya da yüzdenin başında "yaklaşık" vardır. Konu 1–2 ve Konu 3'ün diğer
  adımları kayan noktalı değerle `ornek.esit` kullanır.
- **Ekran biçimi (notlar dışındaki kaynaklar):** veri tablolarında kısa değerler (15'ten az anlamlı basamak, ör.
  0,345678 ya da 0,000056) tam yazılır; bölmeyle bulunan uzun değerler en az 4 basamak ve en küçük değerin 3
  anlamlı basamağıyla; tam sayı denetimi toleranssızdır (1e-11 gibi değerler 0 görünmez). Notlardaki örneğin
  ekranı değişmez (`lab_ui._decimals(small=False)`). Üretilen kod sınıf tablosunu üstel gösterim olmadan yazdırır
  (Python `to_string(float_format=…)`, R `format(…, digits = 15, scientific = FALSE)`); notlardaki kod aynıdır.
  Yine yalnız notlar dışında: işaretli sıfır ("−0,00", kayan nokta gürültüsü) işaretsiz yazılır (metrik, tablo,
  skaler tablosu, grafik açıklaması); kutu özeti değerleri kısa ondalık yazımlarıyla tam (11,625) ve sütunları
  serilerin etiketleriyle gösterilir; nokta grafiğindeki başvuru çizgisinin değeri metrikle aynı basamakla yazılır
  (`DotPlot.reference_decimals`, `with_app_values` doldurur).
- **Kategori sırası:** alfabetik (Türkçe sıra, sayılar değerleriyle), dosyadaki ilk görülme sırası ya da
  frekans. Sıra kodda açık bir liste olarak yazılır; dil ve yerel ayar farkı sonucu değiştirmez.
- **Gizlilik:** yüklenen dosya ve ondan kurulan uygulama yalnız `st.session_state` içinde tutulur; ortak
  önbelleğe yazılmaz. Dosya en çok 5 MB ve 10.000 satırdır. Veri kaynağı değişince Streamlit panelin widget
  durumunu siler; dosya ve seçimler bu yüzden widget dışı anahtarlarda da saklanır (`_kalici_…`).
- **Üretilen kod:** başlık kaynağı söyler; dosya adları `ikt217_konuNN_uygulama`, `_alternatif` ve
  `_kendi_verim` biçimindedir.

### Nicel veri: sınıflar, gövde–yaprak, yüzdelik

- `ClassTable`: eşit genişlikli sınıflar [alt, üst); alt sınır dahil, üst sınır hariç (Python
  `pd.cut(..., right=False)`, R `cut(..., right = FALSE)`). Sınırlar ya notlardaki gibi verilir (`lower`,
  `classes`) ya da veriden kurulur: alt sınır ⌊min/h⌋·h, sınıf sayısı en büyük değeri kapsayan en küçük sayı.
  Seçilebilir sütunlar orta nokta, frekans, göreli frekans, yüzde ve üç kümülatif sütundur. Satır adı
  "10 ≤ x < 20" ya da kümülatif tabloda "x < 20" biçimindedir; sınır metni Python'da `f"{v:.10g}"`, R'de
  `trimws(formatC(v, format = "fg", digits = 10))` ile, ondalık virgülle aynı yazılır.
- `ClassHistogram`: sınıf tablosundan bitişik dikdörtgenler (genişlik = sınıf genişliği). `DotPlot`: aynı
  değerdeki gözlemler üst üste nokta olarak; isteğe bağlı dikey referans çizgileri (ortalama, medyan, çeyrekler)
  ve karşılaştırılan grafiklerde ortak yatay eksen (`x_range`, notlardaki şekillerin ekseni).
- `StemLeaf`: notlarda gövde onlar, yaprak birler basamağıdır; boş gövdeler satır olarak kalır. Genel uygulamada
  (Konu 3) değerler önce 10^d ile tam sayıya çevrilir (`decimals` = d, yarımlar çift basamağa), sonra yaprak
  biriminden küçük basamaklar atılır (`unit` = e, yaprak birimi 10^e; kesilir, yuvarlanmaz). Yaprak birimi en çok
  20 gövde veren en küçük birimdir; negatif veride ya da 300'den fazla gözlemde adım açıklamayla atlanır.
- Konu 3 genel uygulamasında sınıf genişliği h, yaklaşık genişliğin (en büyük − en küçük)/k kolay bir değere
  (1; 2; 2,5 ya da 5 × 10^m) yukarı yuvarlanmasıdır ve verinin biriminden (10^−d) küçük olamaz; sınırlar ondalık
  aritmetikle tam yazılır. Sınır etiketleri iki dilde aynı yazılabilmeli (0 ya da [10⁻⁴, 10¹⁰) aralığında, en çok
  10 anlamlı basamak). Üretilen kod sınıf tablosunu en az 3, genişliğin basamağından bir fazla basamakla yazdırır.
- `Percentile`: ders kuralı L_p = (p/100)(n + 1), iki komşu gözlem arasında doğrusal ara değer; L_p ≤ 1 ise en
  küçük, L_p ≥ n ise en büyük gözlem. Bu Hyndman–Fan (1996) tip 6'dır: numpy `method="weibull"`, R
  `quantile(type = 6)`. Üretilen kod kuralı açıkça yazar (`yuzdelik`); `method="yazilim"` numpy ve R'nin
  varsayılanını (tip 7, konum 1 + (p/100)(n − 1)) gösterir. İki kural medyanda aynıdır; konum farkı 2p/100 − 1'dir.
- `Statistic`: `median`, `mode` (tek mod; birden fazla mod hata verir), `mode_freq` ve `prod` (geometrik ortalama
  için çarpım) eklendi.
- `ReplaceMax`: bir çerçevenin kopyasında en büyük gözlem (ilk görülen; Python `idxmax`, R `which.max`) verilen
  değerle değiştirilir (Konu 4, uç değerin ortalamaya etkisi). `GroupSummary(as_frame=True)`: özet aynı adla bir
  veri çerçevesi de olur (her satır bir grup); ardından `Derive` ve `Statistic` gruplar üzerinde çalışır (grup
  paylarıyla ağırlıklı ortalama). `Histogram.hover_unit`: üzerine gelince kutudaki sayının birimi (varsayılan
  "tekrar"; veri setinin histogramında "gözlem").

### Yayılım, kutu grafiği ve iki değişken (Konu 5)

- `Statistic`: `var` ve `std` örneklem ölçüleridir (payda n − 1; pandas `var()`/`std()`, R `var()`/`sd()`);
  `nunique` farklı değer sayısıdır. `PairStatistic`: örneklem kovaryansı (`cov`) ve Pearson korelasyonu (`corr`).
- `BoxSummary` ve `BoxPlot`: çeyrekler ders kuralıyla (`yuzdelik`); bıyıklar Q₁ − 1,5·IQR ve Q₃ + 1,5·IQR
  sınırlarının içindeki en uç gözlemlere uzanır, dışındaki gözlemler ayrı noktadır. matplotlib `boxplot` ve R
  `boxplot()` çeyrekleri kendi kurallarıyla hesapladığı için kullanılmaz: Python kutuyu `kutu_ozeti`nden
  dikdörtgen ve çizgilerle, R `bxp()` ile hazır özetten, uygulama Plotly `go.Box` ile hazır çeyreklerden çizer.
- `ScatterPlot`: serpilme diyagramı. `LineChart`: `references` yatay başvuru çizgileri (ör. gerçek olasılık),
  `markers=False` uzun seriler için yalnız çizgi.
- `JoinColumns`: aynı satır adlı tabloların sütunlarını yan yana toplar (ör. gözlenen oran, Chebyshev alt sınırı,
  ampirik kural). `Histogram` bir veri çerçevesini de çizebilir; başvuru çizgisi sayı ya da skaler adıdır.
- Genel uygulama (`ornek_konu05`): yayılım ölçüleri tek sayısal sütunda; tam iki kategorili grup sütunu (Adım 1,
  2, 4, 6, 9) ve ikinci sayısal sütun (Adım 5, 10, 11) isteğe bağlıdır. Metindeki ortalama, kareler toplamı,
  varyans, kovaryans ve korelasyon kesin ondalık aritmetikle n·Σx² − (Σx)² özdeşliğinden kurulur (sonlu sonuç tam
  kalır; tam doğrusal ilişkide r = ±1, orantılı sütunlarda CV'ler eşit). Gösterim basamağı kayan noktalı hesabın
  olası farkıyla sınırlanır (`_safe_digits`: 10⁻ᵈ ≥ 5·fark; `_noise`, `_std_bounds`); fark basamak sıfırda bile
  toleransı aşabiliyorsa o kontrol atlanır (`_checkable`; çok büyük değerlerde ör. ilk gözlemin kareli sapması) ve
  kod notu bunu söyler. x̄ ± ks sınırı göreli payla karşılaştırılır (`_slack`; en az 10⁻⁹, veride kayan nokta farkı
  büyükse daha büyük on kuvveti); tam sınırdaki gözlem iki dilde içeride sayılır.
- `BoxSummary.fence_decimals` / `BoxPlot.fence_decimals` (yalnız notlar dışında): 1,5·IQR sınırları sınıflamadan
  önce d + 3 basamağa yuvarlanır (çeyrekler komşu gözlemlerin 0,25'lik adımlarla ara değeridir); tam sınırdaki gözlem
  aykırı değer sayılmaz. Uygulama (`tables.box_summary`), Python (`np.round`) ve R (`round`) aynı ikili sayıyı verir;
  üretilen kod `kutu_ozeti(x, ondalik)` sürümünü kullanır. Kayan nokta farkı bu basamağın yarısına yaklaşıyorsa
  (çok büyük değerler) yuvarlama yapılmaz ve tam sınırdaki gözlemin sınıflaması kesin hesaptan ayrılırsa metin bunu
  söyler. `DotPlot.range_note`: sabit yatay eksenin koddaki açıklaması.

### Sayma ve olaylar (Konu 6)

- `Outcomes`: çok aşamalı deneyin bütün sonuçları, ağaç diyagramındaki sırayla (ilk aşama en yavaş değişir;
  Python `itertools.product`, R `expand.grid` aşamalar ters sırayla verilip sütunlar yeniden dizilerek).
- `Selections`: kombinasyonlar (Python `itertools.combinations`, R `combn`) ve permütasyonlar (Python
  `itertools.permutations`, R'de `sirali_secimler` yardımcısı) sözlük sırasıyla.
- `Event`: olay, örnek uzayın alt kümesidir; olaydaki satırlarda 1, diğerlerinde 0 olan gösterge sütunu (Python
  `isin`, R `%in%`). Birleşim göstergelerin büyüğü (`maximum`), kesişim çarpımıdır. Olasılık, olaydaki örnek
  noktaların olasılıklarının toplamıdır (`Statistic(..., "sum", where=(olay, 1))`).
- `CrossTab(weights=...)`: hücreler gözlem sayısı değil bir sütunun toplamıdır (ortak olasılık tablosu; Python
  `pd.crosstab(values=..., aggfunc="sum")`, R `xtabs(w ~ satır + sütun)`).
- `ShowFrame`: bir veri çerçevesinin seçili sütunlarını gösterir (ör. örnek noktalar ve olay göstergeleri).
- İfade dilinde `cummean` (birikimli ortalama), `seq` (1, …, n), `factorial`, `comb`, `perm` vardır; R'de
  `choose` ve `factorial` ile yazılır.
- Genel uygulama (`ornek_konu06`): E ve F olayları iki kategorik sütunun seçilen kategorileridir (Adım 2, 4, 6, 8,
  9); zarın yüz sayısı m (4–20), ekip büyüklüğü N (2–10) ve seçilen kişi sayısı n (1–10, n ≤ N) kaydırıcıdır.
  Kombinasyon ve permütasyonlar 720 satıra kadar listelenir. Olasılıklar kesirle (`Fraction`) hesaplanır; en çok dört
  basamakla tam yazılabiliyorsa "=", değilse "≈" (zincirde yerine konan terim yuvarlanmışsa da "≈"). Kümeler altı
  öğeye kadar tek tek, daha uzunsa düzenli baş kısım üç noktayla ve düzeni bozan son öğeler açıkça yazılır
  ({2, 4, …, 18, 19, 20}).

### Koşullu olasılık, rassal değişken ve ortak dağılım (Konu 7–8)

- `MosaicChart`: çapraz tablonun (sayılar ya da ortak olasılıklar) her satırı bir sütundur; sütun genişliği
  satırın marjinal payı, sütun içindeki yükseklik satır verildiğinde koşullu pay, parça alanı ortak olasılıktır.
  İlk sütun kategorisi en üstte çizilir (notlardaki Şekil 7.2 gibi).
- `TreeDiagram`: iki aşamalı olasılık ağacı, soldan sağa. Veri çerçevesinin her satırı bir tam yoldur (ilk aşama,
  ikinci aşama, ilk dalın olasılığı, ikinci dalın koşullu olasılığı); ilk yol en üstte, ilk aşamadaki dal kendi
  yollarının ortasında durur ve yol sonunda ortak olasılık yazılır (`tables.tree_layout`; aynı dalın olasılığı
  her yolda aynı olmalıdır). Ağaçta eksen yoktur (`AXISLESS_CHARTS`).
- `HeatMap`: tablonun her hücresi bir kare; ilk satır üstte, sütun adları üstte (notlardaki ortak dağılım
  tablosu gibi). Renk sıfırda ana rengin açık tonundan (`HEAT_LOW`) başlar; sıfır hücreler de zeminden ayrılır.
- `DrawDiscrete`: kesikli rassal değişken; ters dağılım fonksiyonu yöntemi (u ~ Tek-düze(0, 1), X birikimli
  olasılığı u'yu ilk aşan değer), `DrawCategory` ile aynı kural, sonuç sayıdır.
- Sütun grafiğinde sayısal kategoriler (ör. x = 0, 1, 2) Python kodunda metne çevrilir (`astype(str)`):
  matplotlib sayısal konumlara ara eksen işaretleri koyardı. R'de satır içi veride negatif değer varsa etiket
  sütunun altına yazılır. Python'da değer etiketleri için üstte boşluk bırakılır (`ax.margins`); R'de çizgi
  grafiği açıklaması serinin üstündeki boş bantta durur.
- Konu 8 Deney 1'in varsayılan ayarları notlardaki Şekil 8.8'in veri üretim sürecidir (Tablo 8.1'in dağılımı,
  n = 100, tohum 217); şekildeki birikimli ortalama yolu Python'da birebir üretilir.

### Özel kesikli dağılımlar ve sürekli dağılımlar (Konu 9–10)

- İfade dilinde dağılım fonksiyonları: `dbinom`, `pbinom` (x, n, p), `dpois`, `ppois` (x, λ), `dhyper`, `phyper`
  (x, N, r, n) ve `dnorm` (x, μ, σ). Python'da `scipy.stats` (`binom.pmf`, `poisson.cdf`, `hypergeom.pmf(x, N, r, n)`,
  `norm.pdf`), R'de temel `dbinom`, `ppois`, `dnorm`; R'nin hipergeometrik sırası farklı olduğu için
  `dhyper(x, r, N − r, n)` yazılır. Fonksiyonların argüman sayısı `expr.ARITY` ile denetlenir.
- Tek terimli eksi `neg`: e^(−λ) için `exp(neg(λ))`; işlem içinde parantezle yazılır (70 + (−2) * 10). Önceki
  konuların ürettiği kod bu eklemeden etkilenmez (bayt düzeyinde aynıdır).
- `Support`: kesikli değişkenin olası değerleri lower, …, upper; olasılıklar ardından `Derive` ile eklenir.
  `RowSum`: satır toplamı (ör. Bernoulli dizisindeki başarı sayısı X = Y₁ + ⋯ + Yₙ). `GroupSummary` grupları sayı
  da olabilir; R'de `tapply` sonucu konumla değil adla (`"0"`, `"1"`, …) seçilir.
- `Rectangles`: [a, b] aralığını genişliği w olan dikdörtgenlere böler (orta noktalar a + w(i − 0,5)); eğri
  altındaki alan yükseklik × genişliklerin toplamıdır. Konu 10'da 68–95–99,7 alanları Φ tablosu kullanılmadan
  böyle doğrulanır; tablo hesabı Konu 11'e bırakılır.
- `DrawCount`: sayım çekilişi, binom (n, p), Poisson (λ) ve hipergeometrik (N, r, n); Python'da uygulamayla aynı
  çağrı (`rng.binomial`, `rng.poisson`, `rng.hypergeometric(ngood=r, nbad=N − r, nsample=n)`), R'de `rbinom`,
  `rpois`, `rhyper(m = r, n = N − r, k = n)`.
- `DensityPlot`: normal ya da tek-düze yoğunluk eğrisi; boyalı aralıklar olasılık alanıdır, dikey başvuru
  çizgileri eklenebilir. Yatay eksen sabittir (`x_range`); `y_max` verilirse dikey eksen de sabittir ve σ
  büyüyünce eğrinin basıklaştığı görülür. Tek-düzede scipy'nin konum–ölçek biçimi `uniform.pdf(x, a, b − a)`,
  R'de `dunif(x, a, b)`.
- Deneylerin varsayılan ayarları notların örnekleridir (Şekil 9.6'nın p = 0,20 paneli, §9.4'te λ = 3, Tablo
  9.1'deki N = 40, r = 4, n = 8; N(70, 10²), U(120, 140)). Poisson deneyinde gösterilen değerler
  0, …, ⌈2λ + 4√λ + 6⌉ aralığıdır; bu sınırı aşma olasılığı kaydırıcının her değerinde 10⁻¹⁰'dan küçüktür.

### Normal olasılıklar, üstel dağılım ve örnekleme dağılımları (Konu 11–12)

- `roundto(a, d)`: notlardaki tablo kuralı; z iki, Φ(z) dört ondalık basamağa yuvarlanır (Python `np.round`,
  R `round`). Tablo kuralıyla bulunan sonuç ve yuvarlamasız sonuç birlikte gösterilir (ör. 0,5859 ve 0,5858).
- Yoğunluklar (`DENSITIES`): normal (μ, σ), tek-düze (a, b), üstel (μ, σ = μ; scipy `expon.pdf(x, scale=μ)`,
  R `dexp(x, rate = 1 / μ)`) ve gamma (biçim k, oran r; scipy `gamma.pdf(x, k, scale=1 / r)`, R
  `dgamma(x, shape = k, rate = r)`). Grafik parametreleri sayı ya da önceden hesaplanmış bir skalerin adıdır.
- `Draw` üstel: Python `rng.exponential(μ, size=…)`, R `rexp(n, rate = 1 / μ)`; σ = μ denetlenir.
- `DensityCompare`: aynı eksende birden çok yoğunluk (ör. bireysel X ile farklı n'lerde X̄). `PmfWithDensity`:
  kesikli olasılık fonksiyonunun çubukları ve sürekli yaklaşım eğrisi; boyalı aralık süreklilik düzeltmesidir
  (X = 12 → 11,5–12,5).
- `Histogram(curves=…)`: beklenen sayı eğrisi, gözlem sayısı × kutu genişliği × f(x); histogramla aynı ölçektedir.
  `LineChart(bands=…)`: aynı çerçeveden kesikli çizilen ek seriler (ör. μ ± 2σ/√n bandının iki kenarı); boş
  etiketli seri açıklamada gösterilmez.
- Konu 12 Deney 1'in varsayılan ayarları notlardaki Şekil 12.13'ün veri üretim sürecidir (N(50, 20²), n = 100,
  tohum 217); şekildeki yol Python'da birebir üretilir. Deney 2'nin anakütlesi Şekil 12.8'deki üstel dağılımdır
  ve X̄'in tam dağılımı gamma(n, n) eğrisiyle gösterilir. Deney 3'te histogramın her kutusu p̂'nin tek bir
  değerini içerir (sınırlar (k ± 0,5)/n).
- Önceki konuların ürettiği kod bu eklemelerden etkilenmez. Yalnız "Tekdüze" yazımı notlardaki "tek-düze"
  yazımına çevrildi; Konu 1–8 Sezgi kodunun açıklama satırları bu kelimede değişir.

## Sezgi deneyleri

Bir deney (`SimExperiment`), kaydırıcı değerlerinden işlem listesi üreten bir tanımdır. Deneyde tek bir
`np.random.default_rng(seed)` üreteci vardır; `Draw` (normal, tek-düze, beta, gamma, üstel), `DrawCount` (binom,
Poisson, hipergeometrik) ve `DrawCategory` çekilişleri işlem sırasıyla ondan yapılır. Kategorik çekiliş, her gözlem
için u ~ Tek-düze(0, 1) çekip birikimli olasılığı u'yu ilk aşan kategoriyi seçer (Python
`np.searchsorted(..., side="right")`, R `findInterval(u, esik) + 1`; son eşik yuvarlama hatasına karşı tam 1'dir).
Üretilen Python kodu aynı sırayla çektiği için uygulamadaki sayıların aynısını verir. R aynı dağılımdan farklı
çekiliş yapar.

`MonteCarlo` bir işlem bloğunu yeni çekilişlerle tekrarlar; üreteç döngüden önce bir kez tohumlanır.
`Histogram` sonuç tablosunun sütunlarını aynı kutularla iki dilde ve uygulamada çizer.

## Grafikler ve sayı biçimi

Uygulamada Plotly, üretilen kodda Python'da matplotlib, R'de temel grafik kullanılır. Renk sırası
(`core/codegen/base.PALETTE`) üçünde aynıdır. Dilim grafiği notlardaki gibi 0°'den (saat 3 yönü) başlar ve
saat yönünün tersine döner: matplotlib `startangle=0, counterclock=True`, R `init.angle = 0, clockwise =
FALSE`, Plotly'de ilk dilimi o açıda bitirdiği için `rotation = 90° − 360°·r₁`.

Arayüzde sayılar Türkçe biçimdedir (ondalık virgül, yüzde işareti önde); grafik etiketleri Python'da
`sayi_metni`, R'de `formatC(decimal.mark = ",")` ile aynı biçimde yazılır.

## Kendini sına

Her soru tek bir kavramı sınar (`concept`); aynı sette iki soru aynı kavramı sınayamaz ve bölümün her
numaralı alt bölümü en az bir soruyla kapsanır. Sorular notlardaki egzersiz ve mini quiz maddelerini tekrar
etmez. Denklem sorularında öğrenci girdisi Python sözdizimi ağacına çevrilir; yalnız sayılar, tanımlı
semboller, `+ - * / ^` ve `exp/log/sqrt` kabul edilir (`eval` yoktur). Eşdeğerlik, sembollerin rastgele
değerlerinde sayısal karşılaştırmayla sınanır; `100g/n` ile `g/n*100` aynı kabul edilir.

## Ortak testler

- `tests/test_all_labs.py`: adım numaralandırması; iki dilde kod üretimi; notlardaki sayıların uygulamada,
  Python'da (Türkçe Windows kod sayfası `PYTHONIOENCODING=cp1254` altında) ve R'de üretilmesi; üretilen
  kodun çalışma klasöründe dosya bırakmaması; Sezgi deneylerinde Python kodunun uygulamanın sayılarını
  birebir vermesi.
- `tests/test_all_quizzes.py`: soru sayısı ve türleri, kavram tekilliği, bölüm kapsamı, cevap anahtarı dengesi.
- `tests/test_topic_contracts.py`: konu sırası, render fonksiyonları, yeni yapıya taşınan konuların sözleşmesi.
- `tests/test_app_smoke.py`: AppTest ile kabuk, adımlar, deneyler, soru kontrolü, konu ve kod dili geçişi.
- `tests/test_konu01_02_content.py`, `tests/test_konu03_04_content.py`, `tests/test_konu05_06_content.py`,
  `tests/test_konu07_08_content.py`, `tests/test_konu09_10_content.py`, `tests/test_konu11_12_content.py`:
  notlarla veri uyumu, yüzdelik kuralının Hyndman–Fan tip 6 ile özdeşliği, Konu 6 Deney 1'in Şekil 6.6'yı,
  Konu 8 Deney 1'in Şekil 8.8'i ve Konu 12 Deney 1'in Şekil 12.13'ü birebir üretmesi, mozaik ve ağaç kuralları,
  kesikli çekilişin ters dağılım fonksiyonu, Şekil 9.6, 9.8 ve 11.7'nin basılı değerleri, Tablo 11.1'in bütün
  hücreleri, dikdörtgen toplamlarının normal alanları vermesi ve deneylerin istatistiksel doğruluğu.
- `tests/test_lab_engine.py`: tablo hesapları, ifade dili (dağılım fonksiyonları, tek terimli eksi, tablo
  kuralı), yeni işlemler (`Support`, `RowSum`, `Rectangles`, `DrawCount`, `DensityPlot`, üstel çekiliş,
  `DensityCompare`, `PmfWithDensity`, histogram eğrisi, çizgi grafiğinde bant) ve kod üreticisi yardımcıları.

- `tests/test_lab_variants.py`: ek kaynağı olan her konuda alternatif örneğin adım ve bölüm uyumu, uygulama,
  Python ve R'nin aynı sayıları vermesi; örnek dosyanın yüklenmesinin alternatif örneğin sayılarını vermesi;
  Excel ve dört CSV biçiminde okuma ve temizlemenin (bölünmez boşluk, " NA ", başlık adları) iki dilde aynı
  olması; boş hücrelerin yalnız ilgili adımı etkilemesi; reddedilen dosya, başlık ve sayı biçimleri; kodda
  kullanılan adlar ve Türkçe sıralama; Konu 3–4'te zor veri setlerinin (ondalıklı sınırlar, yaprak birimi 10,
  negatif değerler, çok dar sınıflar, boş grup hücreleri, ayrı okunan yüzde değişim sütunu, çok büyük ve çok küçük
  değerler, 300'den fazla gözlem) CSV'den iki dilde aynı sayılarla üretilmesi. R'nin Excel testleri `readxl`
  kurulu değilse atlanır.
- `tests/test_konu01_02_ornekler.py`: Konu 1–2 alternatif örneklerinin değerlerinin doğrudan sayımla
  doğrulanması; kesilmiş eksen, Simpson metinleri (eşitlikler ve karışık yönler dahil), en yaygın kategoride
  eşitlik, varsayılan olumlu kategori; Konu 1'de kimlik, zaman ve tür kuralları, türetilen ad çakışmaları;
  metinlerde değişken sayılara ek getirilmemesi ve kullanıcı adlarının Markdown/KaTeX'i bozmaması.
- `tests/test_konu03_04_ornekler.py`: Konu 3–4 alternatif örneklerinin bağımsız hesapla doğrulanması; sınıf
  kuralının (kolay genişlik, birim alt sınırı, ondalıklı sınırlar) ve gövde–yaprak biriminin bağımsız yazımla
  karşılaştırılması; kendi verinde rastgele veri setleriyle bağımsız sayım ve yüzdelik hesabı; mod durumları, grup
  ağırlıkları, ayrı okunan büyüme sütunu, türetilen ad çakışmaları; çok büyük, çok küçük ve uzun ondalıklı
  değerlerde kesin eşitlikler, "yaklaşık" işareti ve basamak sayısı; metin kuralları ve kullanıcı adları.
- `tests/test_app_smoke.py`: "Kendi verini yükle" seçeneğinde örnek dosyayla bütün adımlar; veri kaynağı değişince
  dosyanın ve seçimlerin korunması, dosyanın kaldırılması ve yeni adın koda yansıması; Konu 3'te sınıf sayısı
  kaydırıcısının sınıfları değiştirmesi, ayara bağlı hatanın kaydırıcının altında görünmesi ve Excel sayfası
  değişince önerinin yeniden hesaplanması.

Yeni bir konu kayda eklendiğinde ayrıca test yazmadan bu sözleşmelere tabidir.
