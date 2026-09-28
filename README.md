# IKT 217 İstatistik I — Etkileşimli Ders Uygulaması

İzmir Bakırçay Üniversitesi İktisat Bölümü ikinci sınıf öğrencileri için Streamlit tabanlı, Türkçe
etkileşimli ders uygulaması. Ders notları konu sırası, terminoloji, notasyon ve pedagojik kapsam
açısından bağlayıcı kaynaktır.

## Konular ve kapsam

Konular ders notlarının bölümleridir. Her konuda üç sekme vardır:

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
| 05 | Değişkenlik, Dağılımın Şekli ve İki Değişken Arasındaki İlişki | Yeni yapı | 12 | 40 | 3 | 24 |
| 06 | Olasılığın Temelleri | Yeni yapı | 9 | 35 | 3 | 24 |
| 07 | Koşullu Olasılık, Bağımsızlık ve Bayes Teoremi | Yeni yapı | 10 | 61 | 3 | 24 |
| 08 | Rassal Değişkenler ve Kesikli Olasılık Dağılımları | Yeni yapı | 12 | 65 | 3 | 24 |
| 09 | Binom, Poisson ve Hipergeometrik Dağılımlar | Yeni yapı | 8 | 39 | 3 | 24 |
| 10 | Sürekli Rassal Değişkenler, Tek-Düze ve Normal Dağılım | Yeni yapı | 7 | 30 | 3 | 24 |
| 11 | Normal Olasılıklar ve Üstel Dağılım | Yeni yapı | 10 | 46 | 3 | 24 |
| 12 | Örnekleme, Nokta Tahmini ve Örnekleme Dağılımları | Yeni yapı | 6 | 19 | 3 | 24 |

Konu 12'nin Sezgi Deney 1'i notlardaki Şekil 12.13'ü üretir (tohum 217); varsayılan ayarlarda Python kodu şekildeki
yolun aynısını verir.

## İki dilde kod

Python ve R kodu uygulamanın hesabıyla aynı tanımdan üretilir (`core/codegen/`). Her adımda iki dilde
sonucun hangi anlamda aynı olduğu yazılır:

- **Birebir aynı:** deterministik hesap; Python ve R aynı sayıyı ondalık düzeyinde verir (Uygulama sekmesi).
- **Yalnız dağılımda aynı:** rastgele çekiliş içerir. Python sürümü uygulamadaki sayıların aynısını verir;
  R'nin rastgele sayı üreteci farklı olduğu için aynı tohum aynı çekilişi vermez (Sezgi sekmesi).

İndirilen Uygulama dosyaları bütün adımları çalıştırır ve sonunda sonuçları ders notlarındaki basılı
sayılarla karşılaştırır (`OK` / `HATA`). Gerekli paketler:

- Python 3.12: `pandas`, `numpy`, `matplotlib`. Olasılık dağılımı fonksiyonu (binom, Poisson, hipergeometrik,
  normal, tek-düze, üstel, gamma) kullanan kod ayrıca `scipy` ister (Konu 3 Deney 3, Konu 4 Deney 2 ve Konu 9–12).
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

Yayın sonrasında en az iki konu için canlı duman testi yapılmalıdır: Uygulama adımları, Sezgi kaydırıcıları,
Kendini sına kontrolü, kod dili seçimi ve metin ölçeği.

## Kullanım ve lisans notu

Bu depo IKT 217 İstatistik I dersi için eğitim materyali olarak hazırlanmıştır. Depoya ayrıca açık kaynak
lisansı eklenmediği sürece standart telif hakları geçerlidir; yeniden kullanım ve dağıtım için hak sahibinin
belirlediği koşullar esas alınmalıdır.
