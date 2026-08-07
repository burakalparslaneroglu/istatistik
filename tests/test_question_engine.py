import pytest

from core.question_engine import Question


def test_question_is_immutable():
    question = Question("Soru?", "Cevap")
    with pytest.raises(Exception):
        question.prompt = "Başka soru"
