"""Konu kaydı, konu modülleri ve yeni mimariye taşınan konuların sözleşmesi."""

from __future__ import annotations

import importlib
import inspect
from pathlib import Path

from app import TOPIC_RENDERERS
from core.labs.registry import LABS
from core.quiz.registry import QUIZZES
from core.topic_registry import get_topic, list_topics

TOPIC_MODULES = {
    "konu01": "topics.konu01_veri_istatistige_giris",
    "konu02": "topics.konu02_kategorik_verilerin_ozetlenmesi",
    "konu03": "topics.konu03_nicel_verilerin_ozetlenmesi",
    "konu04": "topics.konu04_merkezi_egilim_konum",
    "konu05": "topics.konu05_degiskenlik_dagilim_iliskiler",
    "konu06": "topics.konu06_olasiligin_temelleri",
    "konu07": "topics.konu07_kosullu_olasilik_bayes",
    "konu08": "topics.konu08_rassal_degiskenler_kesikli_dagilimlar",
    "konu09": "topics.konu09_binom_poisson_hipergeometrik",
    "konu10": "topics.konu10_surekli_rassal_degisken_normal",
    "konu11": "topics.konu11_normal_uygulamalar_diger_surekli",
    "konu12": "topics.konu12_ornekleme_ornekleme_dagilimlari",
}

# Uygulama + Sezgi + Kendini sına yapısına geçmiş konular: kod iki dilde, tek tanımdan üretilir.
MIGRATED_TOPICS = {"konu01", "konu02", "konu03", "konu04", "konu05", "konu06", "konu07", "konu08"}


def test_registry_has_exact_course_order() -> None:
    topics = list_topics()
    assert [topic.number for topic in topics] == list(range(1, 13))
    assert [topic.key for topic in topics] == list(TOPIC_MODULES)
    assert len({topic.title for topic in topics}) == 12
    assert all(topic.label.startswith(f"Konu {topic.number:02d} · ") for topic in topics)


def test_each_topic_module_exports_render() -> None:
    assert set(TOPIC_RENDERERS) == set(TOPIC_MODULES)
    for key, module_name in TOPIC_MODULES.items():
        module = importlib.import_module(module_name)
        assert callable(module.render), key
        assert TOPIC_RENDERERS[key] is module.render


def test_migrated_topics_use_three_tabs_and_single_source_definitions() -> None:
    for key in MIGRATED_TOPICS:
        module = importlib.import_module(TOPIC_MODULES[key])
        source = inspect.getsource(module)
        assert key in LABS and key in QUIZZES, key
        assert importlib.import_module(f"core.labs.sezgi_{key}"), key
        assert '("Uygulama", "Sezgi", "Kendini sına")' in source, key
        assert "render_lab(" in source and "render_experiments(" in source and "render_quiz(" in source, key
        assert "render_question_card(" not in source, key
        topic = get_topic(key)
        assert topic.guiding_question.endswith("?"), key
        assert source.splitlines()[0] == f'"""Konu {topic.number:02d}: {topic.title}.', key


def test_migrated_topics_have_no_legacy_logic_modules() -> None:
    for key in MIGRATED_TOPICS:
        number = key[-2:]
        assert not Path(f"core/topic{number}_logic.py").exists(), key
        assert not Path(f"tests/test_topic{number}_logic.py").exists(), key
