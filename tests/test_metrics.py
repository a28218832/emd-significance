import numpy as np
import pytest

from emdsig import energy, period, compute_et


def test_energy_matches_variance_for_zero_mean():
    rng = np.random.default_rng(0)
    x = rng.standard_normal(4096)
    # trim_ratio=0 so energy is simply E[x^2]
    assert abs(energy(x, trim_ratio=0.0) - np.mean(x ** 2)) < 1e-12


def test_energy_trim_reduces_end_contamination():
    x = np.zeros(1000)
    x[:50] = 100        # fake spline overshoot at the head
    x[-50:] = 100       # and tail
    e_full = energy(x, trim_ratio=0.0)
    e_trim = energy(x, trim_ratio=0.1)
    assert e_trim < e_full / 2


def test_period_of_sine_is_known():
    N, p = 2048, 64
    t = np.arange(N)
    x = np.sin(2 * np.pi * t / p)
    # Wu & Huang convention: T = N / N_zc. A sine with period p has 2 zero
    # crossings per cycle, so the reported T is p/2.
    assert abs(period(x) - p / 2) < 1.0


def test_period_returns_nan_on_monotonic():
    x = np.linspace(0, 1, 500)
    assert np.isnan(period(x))


def test_compute_et_shapes():
    rng = np.random.default_rng(1)
    imfs = rng.standard_normal((5, 1024))
    E, T = compute_et(imfs)
    assert E.shape == (5,) and T.shape == (5,)


def test_trim_ratio_bounds_validated():
    with pytest.raises(ValueError):
        energy(np.zeros(100), trim_ratio=0.6)
