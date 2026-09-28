from pathlib import Path


def test_binding_course_note_titles_are_used_on_topic_pages():
    expected = {
        "topics/konu01_veri_istatistige_giris.py": "Veri ve İstatistiğe Giriş",
        "topics/konu02_kategorik_verilerin_ozetlenmesi.py": "Kategorik Verilerin Tablo ve Grafiklerle Özetlenmesi",
        "topics/konu03_nicel_verilerin_ozetlenmesi.py": "Nicel Verilerin Tablo ve Grafiklerle Özetlenmesi",
        "topics/konu04_merkezi_egilim_konum.py": "Merkezi Eğilim ve Konum Ölçüleri",
        "topics/konu05_degiskenlik_dagilim_iliskiler.py": (
            "Değişkenlik, Dağılımın Şekli ve İki Değişken Arasındaki İlişki"
        ),
        "topics/konu06_olasiligin_temelleri.py": "Olasılığın Temelleri",
        "topics/konu07_kosullu_olasilik_bayes.py": "Koşullu Olasılık, Bağımsızlık ve Bayes Teoremi",
        "topics/konu08_rassal_degiskenler_kesikli_dagilimlar.py": "Rassal Değişkenler ve Kesikli Olasılık Dağılımları",
        "topics/konu09_binom_poisson_hipergeometrik.py": "Binom, Poisson ve Hipergeometrik Dağılımlar",
        "topics/konu10_surekli_rassal_degisken_normal.py": "Sürekli Rassal Değişkenler, Tek-Düze ve Normal Dağılım",
        "topics/konu11_normal_uygulamalar_diger_surekli.py": "Normal Olasılıklar ve Üstel Dağılım",
        "topics/konu12_ornekleme_ornekleme_dagilimlari.py": "Örnekleme, Nokta Tahmini ve Örnekleme Dağılımları",
    }
    for path, title in expected.items():
        assert title in Path(path).read_text(encoding="utf-8")


def test_readme_contains_release_sections():
    readme = Path("README.md").read_text(encoding="utf-8")
    for heading in (
        "## Veri ve hesaplama kaynakları",
        "## İstatistiksel yorumlama ilkeleri",
        "## Streamlit Community Cloud ile yayınlama",
        "## Kullanım ve lisans notu",
    ):
        assert heading in readme
