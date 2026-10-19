# Konu 5 — CV, çarpıklık ve basıklık

## Son ekleme — §5.6 üç basıklık grafiği
- Mezokurtik, leptokurtik ve platikurtik durumlar notlara ve sunum sayfa 19'a eklendi.
  Aynı merkez/varyans, normal kesikli referans; b₂/g₂ sınıfları ve kısa yorum sınırları gösterilir.
- 40 sunum sayfası ve 16 bağlantı korundu; diğer 39 kaynak çerçevesi aynı. Notlar 301 sayfa.
- Streamlit kodu değişmedi: app/core/topics/tests kapsamındaki 118 Python dosyası aynı hash'e sahip.
- Yeniden doğrulama: 940 pytest geçti (355,01 s), compileall ve diff --check geçti; PDF'ler yeniden derlenip incelendi.
- Son denetim: denetim/2026-10-19-kurtosis-grafikleri/RAPOR.md. Aşağıdaki kayıt önceki içerik genişletmesidir.


Güncelleme: 19 Ekim 2026. Yerel içerik, kod ve PDF düzenlemeleri tamamlandı.

## Amaç ve kararlar
- Kullanıcının §5.5–5.6 genişletmesi önce LaTeX notlarına, sonra sunuma ve Streamlit'e uygulandı.
- CV = 100s/|x̄|; pozitif ortalamada klasik CV ile aynı, mutlak paydalı biçim RSD olarak da adlandırılır.
  Sıfır ortalamada tanımsız; sıfıra yakınken duyarlı. Anlamlı yorum oran ölçeği ve anlamlı mutlak sıfır gerektirir.
  Negatif/karışık işaretli veri tek başına hesaplamayı engellemez; uygunluk bağlamda değerlendirilir.
  y = ax (a ≠ 0) altında değişmez; ötelemede genellikle değişir.
- m_r = Σ(x−x̄)^r/n; g₁ = m₃/m₂^(3/2), b₂ = m₄/m₂², g₂ = b₂−3. Yanlılık düzeltmesi yok.
  m₂ > 0 gerekir. Sıfır çarpıklık simetriyi, normal referans değerleri normalliği kanıtlamaz.
  Basıklık yalnız tepe yüksekliği değildir; dördüncü kuvvetli uzaklık katkısıyla açıklanır.
- Yeni örnek veri yerine mevcut 4, 6, 8, 10, 12 yeniden kullanıldı: m₂=8, m₃=0, m₄=108,8;
  g₁=0, b₂=1,7, g₂=−1,3. Yeni Uygulama Adım 6, §5.6'ya bağlıdır; eski 6–12 artık 7–13.
- Mevcut Sezgi deneyleri/kodu ve bağlı kaynak çerçeveleri korundu. Bekleyen içerik kararı yok.

## Değişiklikler
- Özel ders kökü: E:/OneDrive - BAKIRÇAY ÜNİVERSİTESİ/Bakircay Dersler/Istatistik/2026-2027 IKT 217 İstatistik I.
- Notlar: bolumler/05_degiskenlik_dagilim_iliskiler.tex; ekler/kaynakca.tex; ekler/semboller_sozlugu.tex.
  Diğer not kaynakları ve bütün mevcut label adları korundu. Kaynakçaya iki NIST kaynağı eklendi.
- Sunum: sunumlar/konu05_degiskenlik_dagilim_iliskiler.tex; 39 → 40 gerçek sayfa.
  Öğrenme hedefi/CV/çarpıklık güncellendi; basıklık için bir çerçeve eklendi. 35 eski çerçeve (3 Sezgi dahil)
  içerik olarak aynen korundu; yalnız sonraki Uygulama düğmelerinin numaraları kaydırıldı.
- Repo: core/labs/konu05.py, ornek_konu05.py; ortak moment işlemleri core/labs/shape.py;
  core/quiz/konu05.py (24 soru korunarak yeni kavramlar), ilgili testler ve docs/ARCHITECTURE.md.
- Python/R aynı DSL işlemlerinden üretilir. Alternatif ve kendi verin kaynaklarında metinlerin işaret/tamlık
  kararları kesin kesirlerle verilir; büyük değerlerde gösterim/kontrol hassasiyeti sınırlandırılır.
- Konu 5 notes MD5 bilinçli güncellendi: 5c11318c38bca5c1e807526e0636f42b → d816fd9cff3129b0c453c5736d739f90.
  Diğer 11 konunun kod özetleri değişmedi.
- Akış rehberi/README güncellendi: 113 Uygulama + 36 Sezgi = 149 bağlantı, 13 deste / 492 sayfa.

## Doğrulama
- Tam pytest: 940 geçti, 0 atlandı (329,94 s); R 4.6.1/readxl ve Python/R betik çalıştırmaları dahil.
- Son metin/numara düzeltmeleri sonrası ilgili 75 test tekrar geçti (4,47 s).
- compileall -q app.py core topics tests ve git diff --check geçti.
- Notlar ve Konu 5 sunumu latexmk/pdfLaTeX ile başarıyla derlendi: 301 ve 40 sayfa.
  Overfull, eksik atıf/referans veya durduran TeX hatası yok. Babel/MiKTeX ortam bildirimleri;
  değişmeyen Konu 9 PDF yer imi uyarıları ve 7 Underfull satırı sürüyor.
  longtable paketinden gelen “ignored error: Infinite glue shrinkage…” bildirimi LaTeX projesinin #1907
  kaydında zararsız uyarı olarak tanımlanmış. Görünüm kontrol edildi; paketler değiştirilmedi.
- Değişen slaytlar, notların §5.5–5.6 sayfaları, sözlük ve kaynakça görsel olarak kontrol edildi.
- Son PDF'lerdeki 149 URL ve tıklama geometrisi doğrulandı. 149 hedef gerçek AppTest'te doğru konu, sekme,
  adım/deney, not kaynağı ve varsayılan parametrelerle açıldı.

## Kayıtlar ve kalan durum
- Güncel özel denetim: denetim/2026-10-19-konu05/RAPOR.md, baseline.json, preservation_verified.json,
  streamlit_verification.json, targets_verified.json, görseller ve verify_konu05.py.
- Önceki tüm-konular bağlantı çalışması: denetim/2026-10-17/STREAMLIT_DENETIM_RAPORU.md.
- Özel kaynak/PDF'ler public repoya eklenmedi. Commit, push ve canlı dağıtım yapılmadı.
  Tamamlananlar yerel dosyalardır; yayınlanmış sitenin bu değişiklikleri içerdiği iddia edilmez.
