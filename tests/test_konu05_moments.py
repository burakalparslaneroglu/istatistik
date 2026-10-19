"""5.5–5.6: bağımsız referanslar, işaret/ölçek dönüşümleri ve tanım sınırları."""
import math

import numpy as np
import pandas as pd
import pytest

from core.labs import kendi_veri as K
from core.labs import ornek_konu05 as O5
from core.labs.ornek import CustomChoices, custom_case
from core.labs.registry import get_lab
from core.labs.runner import run_lab


def _run(values):
    table = K.UploadedTable("veri.csv", "csv", pd.DataFrame({"x": values}))
    case, _ = custom_case(O5.CUSTOM, table, CustomChoices(roles={"sayisal": "x"}))
    spec = O5.build(case)
    run = run_lab(spec)
    assert run.all_passed
    return spec, run.state.scalars


def test_notes_shape_reuses_the_variance_example_with_n_divisor():
    spec = get_lab("konu05")
    result = run_lab(spec)
    assert result.all_passed
    s = result.state.scalars
    assert s["bicim_m2"] == 8
    assert s["bicim_m3"] == 0
    assert s["bicim_m4"] == pytest.approx(108.8)
    assert s["bicim_g1"] == 0
    assert s["bicim_b2"] == pytest.approx(1.7)
    assert s["bicim_g2"] == pytest.approx(-1.3)
    assert [step.number for step in spec.steps] == list(range(1, 14))
    assert spec.step(6).note.section == "5.6" and spec.step(7).note.section == "5.7"


def test_shape_matches_two_point_distribution_and_affine_transformations():
    # P(X=2)=1/5, P(X=0)=4/5: standardized Bernoulli moments.
    x = np.array([0., 0., 0., 0., 2.])
    _, ref = _run(x)
    assert ref["bicim_g1"] == pytest.approx(1.5)
    assert ref["bicim_b2"] == pytest.approx(3.25)
    assert ref["bicim_g2"] == pytest.approx(0.25)
    for a, b in ((3, 7), (-4, 19), (1, 1e6)):
        _, got = _run(a*x+b)
        assert got["bicim_g1"] == pytest.approx(math.copysign(1, a) * 1.5, abs=1e-8)
        assert got["bicim_b2"] == pytest.approx(3.25, abs=1e-8)
        assert got["bicim_g2"] == pytest.approx(0.25, abs=1e-8)


@pytest.mark.parametrize("a", [-100, -1, 0.01, 7])
def test_cv_absolute_mean_is_scale_invariant(a):
    x = np.array([2., 3., 5., 7., 8.])
    _, base = _run(x)
    spec, got = _run(a*x)
    assert got["cv_x"] == pytest.approx(100*np.std(x, ddof=1)/x.mean())
    assert got["cv_x"] == pytest.approx(base["cv_x"])
    assert "mutlak sıfır" in spec.step(5).takeaway
    _, shifted = _run(x+20)
    assert shifted["cv_x"] != pytest.approx(base["cv_x"])


def test_cv_zero_mean_is_undefined_and_near_zero_has_no_arbitrary_cutoff():
    spec, values = _run([-2, -1, 0, 1, 2])
    assert not spec.step(5).operations and "cv_x" not in values
    assert "ortalama sıfır" in spec.step(5).explanation
    spec, values = _run([-2, -1, 0, 1, 2.00001])
    assert values["cv_x"] > 1e6
    assert "evrensel bir sayısal eşik yoktur" in spec.step(5).takeaway


def test_custom_constant_data_is_rejected_before_standardized_moments():
    with pytest.raises(K.UploadError, match="bütün değerler aynı"):
        _run([8, 8, 8, 8, 8])
