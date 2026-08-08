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
