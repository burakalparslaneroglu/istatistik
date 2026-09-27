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

## Yeni yapı (Konu 1–2)

| Dosya | Görev |
|---|---|
| `core/topic_registry.py`, `core/types.py` | 12 konunun başlığı (ders notlarındaki bölüm adı), kısa adı ve yönlendirici sorusu |
| `core/labs/spec.py` | Uygulama tanım şeması: işlemler, notlardaki sayılar (`Check`), tekrarlanabilirlik sınıfı |
| `core/labs/expr.py` | Türetilmiş değişken ve skalerler için küçük ifade dili; pandas'ta değerlendirilir, iki dile çevrilir |
| `core/labs/tables.py` | Frekans tablosu, çapraz tablo (sayı, satır ve sütun yüzdesi), sayımdan gözlem verisi, kategorik çekiliş |
| `core/labs/runner.py` | Tanımı çalıştırır ve notlarla karşılaştırır |
| `core/labs/konuNN.py`, `core/labs/registry.py` | Konu uygulamaları |
| `core/labs/sezgi.py`, `core/labs/sezgi_konuNN.py` | Sezgi deneylerinin şeması ve konu deneyleri |
| `core/codegen/` | Python (`python_gen.py`) ve temel R (`r_gen.py`) üreticileri |
| `core/quiz/` | Soru türleri, notlandırma, güvenli formül okuma ve konu soru setleri |
| `core/charts.py` | Plotly grafikleri; `show_figure` tek `st.plotly_chart` çağrısıdır ve eksen adı ister |
| `topics/lab_ui.py`, `topics/sim_ui.py`, `topics/quiz_ui.py` | Üç sekmenin ortak arayüzü |
| `topics/shared.py` | Konu başlığı ve yönlendirici soru |

Eski yapıdaki konular (3–12) kendi `core/topicNN_logic.py` modüllerini, `core/question_engine.py`'yi ve
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

## Sezgi deneyleri

Bir deney (`SimExperiment`), kaydırıcı değerlerinden işlem listesi üreten bir tanımdır. Deneyde tek bir
`np.random.default_rng(seed)` üreteci vardır; `Draw` (normal, tekdüze) ve `DrawCategory` çekilişleri işlem
sırasıyla ondan yapılır. Kategorik çekiliş, her gözlem için u ~ Tekdüze(0, 1) çekip birikimli olasılığı u'yu
ilk aşan kategoriyi seçer (Python `np.searchsorted(..., side="right")`, R `findInterval(u, esik) + 1`; son eşik
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
- `tests/test_konu01_02_content.py`: notlarla veri uyumu ve deneylerin istatistiksel doğruluğu.

Yeni bir konu kayda eklendiğinde ayrıca test yazmadan bu sözleşmelere tabidir.
