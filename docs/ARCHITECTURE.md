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

Yeni bir konu kayda eklendiğinde ayrıca test yazmadan bu sözleşmelere tabidir.
