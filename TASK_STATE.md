# Sunum–Streamlit bütünleştirmesi

## Amaç ve sabit kararlar
- İKT 217 sunumlarından doğru konu, sekme, Sezgi deneyi veya Uygulama adımına görünür düğmelerle geçiş.
- Yayımlanmış temel adres: https://istatistik.streamlit.app/.
- Ders notları, sayısal sonuçlar, Python/R üretim tanımları ve öğretim sırası korunacak.
- Yerel sunumlar özgün klasörlerinde güncellenecek; özel materyaller depoya eklenmeyecek.
- Commit, push ve yayımlama yapılmayacak.

## İncelenenler ve bulgular
- Referans talimat, AGENTS.md, app.py, ortak konu/laboratuvar/deney arayüzleri, test sözleşmeleri.
- Yerel materyal: `E:/OneDrive - BAKIRÇAY ÜNİVERSİTESİ/Bakircay Dersler/Istatistik/2026-2027 IKT 217 İstatistik I`.
- 12 konu, 13 Beamer destesi (12a ve 12b ayrı). Mevcut README sayımlarında 26–48 PDF sayfası.
- Streamlit 1.60.0 kurulu; st.tabs key/on_change/default destekliyor. Sürüm artırımı gerekmiyor.
- MiKTeX latexmk/pdfLaTeX mevcut. PDF inceleme için paketli Python/PyMuPDF kullanılabilir.

## Tamamlanan yerel çalışma
- 13 deste özgün `Sunumlar/` kaynaklarında ve `Sunumlar/pdfs/main_konu*.pdf` dosyalarında güncellendi: 490 gerçek sayfa, 50 görünür bağlantı; bütün desteler 30–40 sayfa.
- Handout derleme ile aşamalı gösterimler birleştirildi; kaynakta pause korundu. Konu 08'de bir soru/cevap, Konu 12a'da altı yoğun çerçeve bölündü. Notlar, matematik, hesaplama/kod üretim tanımları ve veri/görsel varlıkları değişmedi.
- `core/navigation.py`, `topics/navigation_ui.py`, `app.py`, 12 konu modülü, `topics/lab_ui.py`: doğrulanan URL ve bir kez uygulanan başlangıç durumu. Kaydırıcı/sekme seçimleri korunur; dosya bekleyen hedef görünür.
- `tests/test_navigation.py`: 46 kontrol. Dört mevcut test dosyasında R alt süreçlerinin Windows UTF-8 yerel ayarı düzeltildi; uyarı kontrolleri korunur.
- `docs/SUNUM_BAGLANTILARI.md`, `docs/ARCHITECTURE.md` güncellendi. Özel rehber `Sunumlar/STREAMLIT_DERS_AKISI.md`; denetim `denetim/STREAMLIT_DENETIM_RAPORU.md`. Özel materyal public repoya eklenmedi.

## Doğrulanan kanıtlar
- 13 latexmk/pdfLaTeX derlemesi başarılı; hata/Overfull/eksik referans yok. Babel eski yapı uyarısı 13; Underfull hbox 5 (görüntüleri incelendi); MiKTeX güncelleme durumu bildirimi var.
- Değiştirilmemiş başlangıç kaydıyla kaynak/PDF karşılaştırması ve korunmuş dosya hash'leri: 0 denetim hatası. PDF metin kontrolü harf/rakam çoklukları ve overlay eşleştirmesi; matematik kaynak/görüntü ile denetlendi.
- 50 son PDF bağlantısı/etiketi/tıklama alanı doğrulandı; bütün bağlantılı sayfalar render edilip incelendi.
- 50 gerçek AppTest hedef kontrolü başarılı. Yerel tarayıcıda Konu 07/Sezgi 3 ayar koruması ve Konu 04/Uygulama/Adım 7 doğrulandı.
- Genel test R PATH'te yokken 864 geçti, 68 atlandı. Kurulu R 4.6.1 + readxl ile ayrı 68 R kontrolü geçti. R etkin tam çalışma: 923 geçti, 9 Windows yerel ayarı hatası. Düzeltmeden sonra ilgili iki test dosyası tamamen yeniden çalıştı: 121 geçti, önceki dokuz kontrol dahil. 932 testlik kapsamda açık hata/atlanmış R yolu yok; bu sonuç birden fazla çalışmanın birlikte doğruladığı kapsamdır.
- Son `compileall -q app.py core topics tests` ve `git diff --check` başarılı. Ham kayıtlar özel `denetim/` ve ignored `references_private/` içinde. Yerel denetim sunucusu kapatıldı.

## Kalan işler
- Yerel kapsam tamamlandı; kaynaklar, PDF'ler, ders akışı rehberi ve denetim raporu hazır.
- Canlı uygulama henüz yeni yönlendirmeyi içermiyor: denetlenen hedef Konu 01/Uygulama ile açıldı. Kullanıcı commit/push/yayımlama yaptıktan sonra canlı hedef kontrolü gerekir; bu oturumda yayımlama yapılmayacak.

## Tamamlanma ölçütleri
- Her deste 30–40 gerçek PDF sayfası; özgün içerik korunmuş.
- Tüm düğmeler görünür, tıklama alanlarıyla örtüşür ve doğrulanan hedefe gider.
- Doğrudan bağlantı doğru sekme ve deney/adımı açar; sonraki kullanıcı seçimleri korunur.
- Yerel doğrulama ile canlı dağıtımın durumu ayrı raporlanır.
