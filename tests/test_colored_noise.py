import numpy as np
import pytest

from emdsig import generate_fgn, red_noise_slope


def test_fgn_unit_variance_roughly():
    rng = np.random.default_rng(0)
    x = generate_fgn(4096, hurst=0.5, rng=rng)
    # Davies-Harte embedding produces approximately unit variance; tolerate 30%.
    assert 0.7 < np.std(x) < 1.3


def test_fgn_length_matches():
    assert len(generate_fgn(1000, hurst=0.7)) == 1000


@pytest.mark.parametrize("h", [0.1, 0.5, 0.9])
def test_red_noise_slope_formula(h):
    assert red_noise_slope(h) == pytest.approx(-2.0 * h)


def test_hurst_range_validated():
    with pytest.raises(ValueError):
        generate_fgn(256, hurst=1.5)
    with pytest.raises(ValueError):
        red_noise_slope(0.0)
