# Sunum–Streamlit bütünleştirmesi — güncel durum

Güncelleme: 17 Ekim 2026. Yerel kapsam tamamlandı.

## Amaç ve sabit sınırlar
- Bütün konuların Uygulama adımlarını sunumdan doğrudan açmak.
- Mevcut Sezgi içeriği/deneyleri ve bağlantılı çerçeveler korunacak; yalnız eksik bağlantı varsa eklenecek.
- Notlar, sayısal sonuçlar, notasyon, öğretim sırası, hesaplama ve Python/R üretimi korunur.
- Özgün kaynaklar/PDF'ler yerinde güncellenir; 30–40 gerçek sayfa sınırı, görünür ve tamamı tıklanabilir düğmeler sürer.
- Özel materyal public repoya eklenmez. Commit, push, canlı yayımlama yapılmaz.

## Başlangıç ve tamamlananlar
- Depo başlangıçta temizdi; önceki bütünleştirme 99ca2eb commit'inde.
- İlk envanter: 112 Uygulama adımı, 14 bağlı adım; 36 Sezgi deneyi ve 36 mevcut bağlantı.
- 98 yeni Uygulama düğmesi eklendi. Son kapsam: 112/112 Uygulama ve 36/36 Sezgi; her hedef bir kez, toplam 148 düğme.
- Sezgi'de eksik bağlantı yoktu; ekleme/değişiklik yapılmadı. Mevcut 50 bağlantılı kaynak çerçevesinin tamamı, Sezgi'deki 36 çerçeve dahil, aynen korundu.
- 13 deste / 491 gerçek PDF sayfası. Konu 10'da notlardaki Adım 6 için tek uygulama slaydı eklendi: N(70,10²), 60–80 → −1–1, aynı alan ≈0,683. Deste 36 → 37 sayfa. Diğer sayfa sayıları değişmedi.
- Konu 12a zaten tam kapsama sahipti; kaynağı değişmedi. Diğer 12 konu kaynağı güncellendi.
- Konu 3 Adım 2, aynı sayıları kullanan örneğe bağlandı (sayfa 7). İki yoğun çerçevede yalnız düşey boşluk düzeltildi.
- Uygulama/test/bağımlılık kodu bu turda değişmedi. Mevcut yönlendirme bütün adımları destekliyor.

## Dosyalar
- Özel ders kökü: E:/OneDrive - BAKIRÇAY ÜNİVERSİTESİ/Bakircay Dersler/Istatistik/2026-2027 IKT 217 İstatistik I.
- Kaynaklar: Sunumlar/sunumlar/konu*.tex; PDF'ler: Sunumlar/pdfs/main_konu*.pdf.
- Güncel rehber: Sunumlar/STREAMLIT_DERS_AKISI.md; README sayfa/düğme tablosu güncellendi.
- Güncel denetim: denetim/2026-10-17/STREAMLIT_DENETIM_RAPORU.md.
- Değiştirilmeyen başlangıç: denetim/2026-10-17/baseline.json. Registry, eşleştirme, kaynak/PDF denetimi, AppTest çıktıları ve görseller aynı özel dizinde.
- Önceki 10 Ekim başlangıç/denetim kayıtları tarihsel kanıt olarak korunur.

## Doğrulama
- 13 latexmk/pdfLaTeX derleme kontrolü başarılı; hata/Overfull/eksik referans yok. Önceden var olan Babel uyarısı 13 ve Underfull hbox 5 sürüyor; ilgili sayfalar incelendi. MiKTeX güncelleme durumu bildirimi var.
- Korunan dosya hash'leri, özgün çerçeve içerikleri ve 490 eski PDF sayfasının yeni karşılıkları: 0 denetim hatası. 20 ders notu kaynak dosyası değişmedi.
- 148 URL/etiket/tıklama alanı kontrol edildi; bütün bağlı sayfalar render edilip 25 temas sayfasında görüntülendi. Yoğun/ek sayfalar ayrıca incelendi.
- 148 son PDF URL'si gerçek AppTest'te geçti; görünür sekme, adım/deney, not kaynağı ve başlangıç değerleri doğru.
- Tek tam pytest çalışması: 932 geçti, 0 atlandı (372,28 saniye); R 4.6.1 ve readxl yolları dahil.
- compileall -q app.py core topics tests ve git diff --check başarılı.

## Açık durum
- Yerel düzenleme, derleme, test ve raporlama tamamlandı; bekleyen içerik kararı yok.
- Canlı site bu turda yeniden test edilmedi. 10 Ekim canlı gözlemi bugünkü dağıtımın durumu olarak kullanılmamalı.
- Commit, push veya canlı yayımlama yapılmadı; özel ders dosyaları repoya eklenmedi.
