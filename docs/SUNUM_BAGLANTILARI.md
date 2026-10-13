# Sunumdan uygulamaya doğrudan geçiş

Yayımlanmış temel adres: https://istatistik.streamlit.app/.
Yerel değişiklikler kullanıcı tarafından yayımlanınca bu sözleşme canlı uygulamada da geçerlidir.

```text
https://istatistik.streamlit.app/?konu=07&sekme=sezgi&deney=3
https://istatistik.streamlit.app/?konu=04&sekme=uygulama&adim=7
```

## Alanlar

| Alan | Kabul edilen değer | Başlangıç |
|---|---|---|
| `konu` | `01`–`12`; iki basamak | Doğrudan bağlantıda gerekli |
| `sekme` | `uygulama`, `sezgi`, `kendini_sina` | `uygulama` |
| `adim` | Konunun `LabSpec.steps` numaralarından biri | Uygulama: ilk adım |
| `deney` | Konunun `SimExperiment.number` numaralarından biri | Sezgi: ilk deney |
| `kaynak` | `notlar`, `alternatif`, `kendi`; yalnız Uygulama | `notlar` |
| `p_<anahtar>` | Hedef deneyin parametresi; yalnız Sezgi | Deneyin tanımlı varsayılanı |

Örneğin `?konu=01&sekme=sezgi&deney=1&p_c=3&p_n=500`, kategori kodu deneyi için
izin verilen iki başlangıç değerini belirtir. Ondalık değerler URL'de noktayla yazılır.
Aralık, tam sayı gereksinimi ve kaydırıcı adımına uyum `Decimal` ile doğrulanır.
Sunum bağlantıları deneylerin tanımlı varsayılanlarını kullanır; tohum deney tanımındadır.

## Oturum davranışı

- Yeni/değişen bağlantı konu, görünür sekme ve hedefi bileşenler kurulmadan önce seçer.
- Aynı URL, kaydırıcı ya da sekme etkileşimi sırasında tekrar uygulanmaz.
- Sezgi bağlantısı hedef deneyin bütün parametrelerini varsayılanlarına veya URL değerlerine getirir.
- Uygulama bağlantısı aksi belirtilmedikçe notlardaki örneği seçer; önceki alternatif veri seçimini sıfırlar.
- `kaynak=kendi`, Konu 1–8'de dosya yükleme; Konu 9–12'de değer giriş panelini açar.
  Dosya yükleme başlamadan hedef adım başlığı görünür ve hedef, dosya/girdi hazırlanırken korunur.
  Bağlantı dosya yüklemez, temizlemez veya paylaşmaz.
- Geçersiz veya tekrarlanan seçimlerde açık hata gösterilir; bağlantının hiçbir seçimi uygulanmaz.
  Kullanıcı kenar çubuğuyla normal gezinmeye devam edebilir.
- Uygulamayı bağlantısız açma davranışı ve üç sekmenin sırası korunur.

## Uygulama ve doğrulama

- `core/navigation.py`: Streamlit'ten bağımsız hedef doğrulaması ve bir kez uygulanan başlangıç durumu.
- `topics/navigation_ui.py`: query parametrelerini oturum durumuna aktarır; hatayı gösterir.
- Konu modüllerindeki `st.tabs(..., key=..., on_change="rerun")`: görünür sekme durumunu izler.
- `topics/lab_ui.py`: dosya bekleyen bağlantının hedef adımını korur.
- `tests/test_navigation.py`: tüm kayıtlı adım/deney hedefleri, geçersiz URL'ler, gerçek AppTest
  oturumları, veri kaynağı ve etkileşim sonrası durum koruması.

Kurulu ve sabitlenen Streamlit sürümü **1.60.0**; `key`, `on_change` ve programatik sekme durumu
yerel kurulu API'de doğrulandı. Bağımlılık sürümü değiştirilmedi.

Sunum kaynakları, PDF'ler, slayt sayfaları ve ders akışı özel ders klasöründe tutulur;
bu public depoya kopyalanmaz. Matematiksel hesaplar ve Python/R üretim tanımları değiştirilmedi.
