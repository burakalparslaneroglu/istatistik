# IKT 217 İstatistik I — Etkileşimli Ders Uygulaması

İzmir Bakırçay Üniversitesi İktisat Bölümü ikinci sınıf öğrencileri için Streamlit tabanlı, Türkçe
etkileşimli ders uygulaması. Ders notları konu sırası, terminoloji, notasyon ve pedagojik kapsam
açısından bağlayıcı kaynaktır.

## Konular ve kapsam

Konular ders notlarının bölümleridir. Yeni yapıya taşınan konularda üç sekme vardır:

- **Uygulama:** ders notlarındaki çözümlü örnekler, bölüm sırasıyla. Tablolar notlardaki sayıların
  aynısını verir; her adımın Python ve R kodu gösterilir, bütün uygulama tek dosya olarak indirilir.
- **Sezgi:** veri üretim süreci (DGP) bilinen kontrollü simülasyonlar. Kaydırıcılarla parametre
  değiştirilir; kod şu anki kaydırıcı değerleriyle üretilir.
- **Kendini sına:** dört soru türünden 24 soru (çoktan seçmeli, doğru–yanlış, boşluk doldurma, denklem).

| Konu | Başlık | Durum | Uygulama adımı | Notlarla karşılaştırılan sayı | Sezgi deneyi | Soru |
|---|---|---|---:|---:|---:|---:|
| 01 | Veri ve İstatistiğe Giriş | Yeni yapı | 5 | 14 | 3 | 24 |
| 02 | Kategorik Verilerin Tablo ve Grafiklerle Özetlenmesi | Yeni yapı | 12 | 56 | 3 | 24 |
| 03 | Nicel Verilerin Tablo ve Grafiklerle Özetlenmesi | Yeni yapı | 11 | 85 | 3 | 24 |
| 04 | Merkezi Eğilim ve Konum Ölçüleri | Yeni yapı | 10 | 32 | 3 | 24 |
| 05 | Değişkenlik, Dağılım ve İlişki | Eski yapı | — | — | — | — |
| 06 | Olasılığın Temelleri | Eski yapı | — | — | — | — |
| 07 | Koşullu Olasılık, Bağımsızlık ve Bayes Teoremi | Eski yapı | — | — | — | — |
| 08 | Rassal Değişkenler ve Kesikli Olasılık Dağılımları | Eski yapı | — | — | — | — |
| 09 | Binom, Poisson ve Hipergeometrik Dağılımlar | Eski yapı | — | — | — | — |
| 10 | Sürekli Rassal Değişkenler, Tek-Düze ve Normal Dağılım | Eski yapı | — | — | — | — |
| 11 | Normal Olasılıklar ve Üstel Dağılım | Eski yapı | — | — | — | — |
| 12 | Örnekleme, Nokta Tahmini ve Örnekleme Dağılımları | Eski yapı | — | — | — | — |

Eski yapıdaki konular sırayla yeni yapıya taşınır.

## İki dilde kod

Python ve R kodu uygulamanın hesabıyla aynı tanımdan üretilir (`core/codegen/`). Her adımda iki dilde
sonucun hangi anlamda aynı olduğu yazılır:

- **Birebir aynı:** deterministik hesap; Python ve R aynı sayıyı ondalık düzeyinde verir (Uygulama sekmesi).
- **Yalnız dağılımda aynı:** rastgele çekiliş içerir. Python sürümü uygulamadaki sayıların aynısını verir;
  R'nin rastgele sayı üreteci farklı olduğu için aynı tohum aynı çekilişi vermez (Sezgi sekmesi).

İndirilen Uygulama dosyaları bütün adımları çalıştırır ve sonunda sonuçları ders notlarındaki basılı
sayılarla karşılaştırır (`OK` / `HATA`). Gerekli paketler:

- Python 3.12: `pandas`, `numpy`, `matplotlib`. Normal dağılım fonksiyonu kullanan Sezgi deneylerinin kodu
  ayrıca `scipy` ister (Konu 3 Deney 3, Konu 4 Deney 2).
- R 4.2 veya üstü: yalnız temel R; ek paket gerekmez. Betik Rscript ile çalıştırılırsa grafikler
  çalışma klasörüne değil R'nin geçici klasörüne yazılır; RStudio'da Plots panelinde görünür.

## Tasarım ilkeleri

- Hesaplama `core/`, sunum `topics/` altındadır; `app.py` yalnız kabuk ve konu yönlendirmesidir.
- Grafiklerde yatay ve dikey eksen adları zorunludur ve test edilir.
- Sayılar Türkçe biçimde gösterilir: ondalık virgül, yüzde işareti sayıdan önce (%62,5).
- Simülasyonlar sabit tohumla yeniden üretilebilir; tohum üretilen kodda görünür.
- Sonraki konuların yöntemleri önceki konularda uygulama olarak açılmaz.

Ayrıntılar: `docs/ARCHITECTURE.md` ve `AGENTS.md`.

## Kurulum

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

## Çalıştırma

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## Test

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m compileall app.py core topics tests
git diff --check
```

Testler üretilen Python kodunu çalıştırır ve notlardaki sayıları üretip üretmediğini denetler. `Rscript`
kuruluysa R kodu da aynı biçimde denetlenir; kurulu değilse R testleri atlanır.

## Veri ve hesaplama kaynakları

Uygulamadaki veri setleri ders notlarındaki örneklerden (tabloların içinde yazılı küçük veri setleri) veya
öğretim amacıyla açıkça tanımlanmış simülasyonlardan oluşur. Çalışma zamanında dış veri kaynağı, LLM veya
dış API çağrısı yapılmaz. Simülasyonlarda yeniden üretilebilirlik için sabit tohumlu
`np.random.default_rng(seed)` kullanılır.

## İstatistiksel yorumlama ilkeleri

- Betimsel sonuçlar gözlenen veri bağlamında yorumlanır; anakütleye genelleme ancak çıkarım mantığıyla ve
  örneklemin nasıl seçildiği bilinerek yapılır.
- Korelasyon veya birlikte hareket tek başına nedensellik kanıtı olarak yorumlanmaz.
- Olasılık, dağılım ve yüzde sonuçlarında payda, birim ve koşul açık tutulur.
- Grafiklerde eksen başlıkları zorunludur; bilgi yalnız renkle kodlanmaz.
- Ders notlarında henüz tanıtılmamış yöntemler önceki konularda varsayılmaz.

## Streamlit Community Cloud ile yayınlama

Kararlı `main` dalı Streamlit Community Cloud üzerinden yayımlanabilir:

1. GitHub deposunu seçin.
2. Branch olarak `main` kullanın.
3. Main file path olarak `app.py` seçin.
4. Python sürümünü `3.12` olarak ayarlayın.
5. Bağımlılıkların `requirements.txt` üzerinden kurulmasını sağlayın.

Uygulama secret veya dış API kullanmadığından ek bir secret yapılandırması gerektirmez.

Yayın sonrasında en az yeni yapıdaki iki konu ve eski yapıdaki bir konu için canlı duman testi yapılmalıdır:
Uygulama adımları, Sezgi kaydırıcıları, Kendini sına kontrolü, kod dili seçimi ve metin ölçeği.

## Kullanım ve lisans notu

Bu depo IKT 217 İstatistik I dersi için eğitim materyali olarak hazırlanmıştır. Depoya ayrıca açık kaynak
lisansı eklenmediği sürece standart telif hakları geçerlidir; yeniden kullanım ve dağıtım için hak sahibinin
belirlediği koşullar esas alınmalıdır.
