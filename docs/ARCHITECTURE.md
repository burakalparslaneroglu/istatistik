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

## Yeni yapı (Konu 1–6)

| Dosya | Görev |
|---|---|
| `core/topic_registry.py`, `core/types.py` | 12 konunun başlığı (ders notlarındaki bölüm adı), kısa adı ve yönlendirici sorusu |
| `core/labs/spec.py` | Uygulama tanım şeması: işlemler, notlardaki sayılar (`Check`), tekrarlanabilirlik sınıfı |
| `core/labs/expr.py` | Türetilmiş değişken ve skalerler için küçük ifade dili; pandas'ta değerlendirilir, iki dile çevrilir |
| `core/labs/tables.py` | Frekans tablosu, çapraz tablo (sayı, satır ve sütun yüzdesi, ağırlıklı toplam), sayımdan gözlem verisi, çok aşamalı deneyin sonuçları, kombinasyon ve permütasyon listeleri, kategorik çekiliş, sınıf tablosu, gövde–yaprak, yüzdelik, kutu grafiği özeti |
| `core/labs/runner.py` | Tanımı çalıştırır ve notlarla karşılaştırır |
| `core/labs/konuNN.py`, `core/labs/registry.py` | Konu uygulamaları |
| `core/labs/sezgi.py`, `core/labs/sezgi_konuNN.py` | Sezgi deneylerinin şeması ve konu deneyleri |
| `core/codegen/` | Python (`python_gen.py`) ve temel R (`r_gen.py`) üreticileri |
| `core/quiz/` | Soru türleri, notlandırma, güvenli formül okuma ve konu soru setleri |
| `core/charts.py` | Plotly grafikleri; `show_figure` tek `st.plotly_chart` çağrısıdır ve eksen adı ister |
| `topics/lab_ui.py`, `topics/sim_ui.py`, `topics/quiz_ui.py` | Üç sekmenin ortak arayüzü |
| `topics/shared.py` | Konu başlığı ve yönlendirici soru |

Eski yapıdaki konular (7–12) kendi `core/topicNN_logic.py` modüllerini, `core/question_engine.py`'yi ve
`core/ui_components.render_plotly`'yi kullanır. Bir konu yeni yapıya taşındığında eski modülü ve testleri
aynı blokta kaldırılır.

## Uygulama akışı

Bir konu uygulaması tek bir `LabSpec` tanımıdır ve dört çıktıyı birlikte besler:

1. `topics/lab_ui.py` adımları, tabloları, grafikleri ve kodu gösterir. Her adımda o adımın sonundaki durum
   gösterilir; sonraki adımların eklediği sütunlar görünmez.
2. `core/labs/runner.py` hesabı yapar; her `Check` notlarda basılı bir sayıdır ve tolerans basılı basamak
   sayısıdır (0,5 × 10⁻ᵈ).
3. `core/codegen/` aynı işlemleri Python ve R'ye çevirir; tam betik sonunda sonuçları notlardaki sayılarla
   karşılaştırır.
4. `tests/test_all_labs.py` uygulamanın ve üretilen Python/R kodunun notlardaki sayıları ürettiğini doğrular.

Adımlar notların bölüm sırasını izler (`NoteRef("2.8")`); işlemsiz (yalnız metin) adım yalnız son adım
olabilir. Veriler notlardaki küçük veri setleridir: `InlineData` tabloyu satır satır yazar, `FromCounts`
sayım tablosunun her satırını sayısı kadar tekrarlayarak gözlem düzeyinde veri kurar. Tablolar ve çapraz
tablolar bu veriden yeniden sayılır; yani notlardaki sayılar girdi değil, hesabın sonucudur.

Çapraz tabloda yüzde türü paydayı belirler: `percent="satir"` her satırı, `percent="sutun"` her sütunu 100'e
tamamlar. `Toplam` satırı ve sütunu iki dilde aynı adla eklenir; grafiklerde çizilmez.

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
- `StemLeaf`: gövde onlar, yaprak birler basamağıdır; boş gövdeler satır olarak kalır.
- `Percentile`: ders kuralı L_p = (p/100)(n + 1), iki komşu gözlem arasında doğrusal ara değer; L_p ≤ 1 ise en
  küçük, L_p ≥ n ise en büyük gözlem. Bu Hyndman–Fan (1996) tip 6'dır: numpy `method="weibull"`, R
  `quantile(type = 6)`. Üretilen kod kuralı açıkça yazar (`yuzdelik`); `method="yazilim"` numpy ve R'nin
  varsayılanını (tip 7, konum 1 + (p/100)(n − 1)) gösterir. İki kural medyanda aynıdır; konum farkı 2p/100 − 1'dir.
- `Statistic`: `median`, `mode` (tek mod; birden fazla mod hata verir), `mode_freq` ve `prod` (geometrik ortalama
  için çarpım) eklendi.

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

## Sezgi deneyleri

Bir deney (`SimExperiment`), kaydırıcı değerlerinden işlem listesi üreten bir tanımdır. Deneyde tek bir
`np.random.default_rng(seed)` üreteci vardır; `Draw` (normal, tekdüze, beta, gamma) ve `DrawCategory` çekilişleri
işlem sırasıyla ondan yapılır. Kategorik çekiliş, her gözlem için u ~ Tekdüze(0, 1) çekip birikimli olasılığı
u'yu ilk aşan kategoriyi seçer (Python `np.searchsorted(..., side="right")`, R `findInterval(u, esik) + 1`; son eşik
yuvarlama hatasına karşı tam 1'dir). Üretilen Python kodu aynı sırayla çektiği için uygulamadaki sayıların
aynısını verir. R aynı dağılımdan farklı çekiliş yapar.

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
- `tests/test_konu01_02_content.py`, `tests/test_konu03_04_content.py`, `tests/test_konu05_06_content.py`:
  notlarla veri uyumu, yüzdelik kuralının Hyndman–Fan tip 6 ile özdeşliği, Konu 6 Deney 1'in notlardaki
  Şekil 6.6'yı birebir üretmesi ve deneylerin istatistiksel doğruluğu.

Yeni bir konu kayda eklendiğinde ayrıca test yazmadan bu sözleşmelere tabidir.
