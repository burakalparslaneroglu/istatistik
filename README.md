# İKT 207 İstatistik — Etkileşimli Ders Uygulaması

İkinci sınıf İktisat öğrencileri için Streamlit tabanlı, Türkçe etkileşimli ders uygulaması. Ders notları konu sırası, terminoloji, notasyon ve pedagojik kapsam açısından bağlayıcı kaynaktır.

## Mevcut modüller

- Konu 01 — Veri ve İstatistiğe Giriş
- Konu 02 — Kategorik Verilerin Özetlenmesi
- Konu 03 — Nicel Verilerin Özetlenmesi
- Konu 04 — Merkezi Eğilim ve Konum Ölçüleri
- Konu 05 — Değişkenlik, Dağılımın Şekli ve İki Değişken Arasındaki İlişki
- Konu 06 — Olasılığın Temelleri
- Konu 07 — Koşullu Olasılık, Bağımsızlık ve Bayes Teoremi
- Konu 08 — Rassal Değişkenler ve Kesikli Olasılık Dağılımları
- Konu 09 — Binom, Poisson ve Hipergeometrik Dağılımlar
- Konu 10 — Sürekli Rassal Değişkenler, Tek-Düze ve Normal Dağılım
- Konu 11 — Normal Dağılım Uygulamaları ve Diğer Sürekli Dağılımlar
- Konu 12 — Örnekleme ve Örnekleme Dağılımları

## Tasarım ilkeleri

- Hesaplama mantığı `core/`, sunum `topics/` altında ayrılır.
- Her X–Y grafiği ortak `render_plotly` bileşeninden geçer.
- Bütün veri grafiklerinde açık X ve Y eksen başlıkları zorunludur ve test edilir.
- Simülasyon ve hesaplamalar deterministik/test edilebilir tasarlanır.
- İleri konular önceki konularda varsayılmaz.

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

## Veri ve hesaplama kaynakları

Uygulamadaki örnek veri setleri ve sayısal senaryolar ders notlarındaki örneklerden veya öğretim amacıyla açıkça tanımlanmış yapay verilerden oluşturulur. Çalışma zamanında dış veri kaynağı, LLM veya dış API çağrısı yapılmaz. Simülasyonlarda yeniden üretilebilirlik için sabit veya açıkça yönetilen rassal sayı üreticileri kullanılır.

## İstatistiksel yorumlama ilkeleri

- Betimsel sonuçlar gözlenen veri bağlamında yorumlanır; anakütleye genelleme ancak çıkarım mantığıyla yapılır.
- Korelasyon tek başına nedensellik kanıtı olarak yorumlanmaz.
- Olasılık, dağılım ve örnekleme sonuçlarında payda, birim ve koşul açık tutulur.
- Grafiklerde X ve Y eksen başlıkları zorunludur; bilgi yalnız renkle kodlanmaz.
- Ders notlarında henüz tanıtılmamış yöntemler önceki konularda varsayılmaz.

## Streamlit Community Cloud ile yayınlama

Kararlı `main` dalı Streamlit Community Cloud üzerinden yayımlanabilir:

1. GitHub deposunu seçin.
2. Branch olarak `main` kullanın.
3. Main file path olarak `app.py` seçin.
4. Python sürümünü `3.12` olarak ayarlayın.
5. Bağımlılıkların `requirements.txt` üzerinden kurulmasını sağlayın.

Uygulama secret veya dış API kullanmadığından ek bir secret yapılandırması gerektirmez.

Yayın sonrasında en az Konu 01, orta bir konu ve Konu 12 için canlı smoke test yapılmalıdır. Grafikler, widget'lar, soru düğmeleri ve metin ölçeği canlı ortamda yeniden kontrol edilmelidir.

## Kullanım ve lisans notu

Bu depo İKT 207 İstatistik dersi için eğitim materyali olarak hazırlanmıştır. Depoya ayrıca açık kaynak lisansı eklenmediği sürece standart telif hakları geçerlidir; yeniden kullanım ve dağıtım için hak sahibinin belirlediği koşullar esas alınmalıdır.
