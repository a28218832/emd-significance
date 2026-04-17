import numpy as np

from emdsig import chi2_confidence_bounds, calibrate_intercept


def test_bounds_bracket_the_baseline():
    grid = np.log(np.array([4.0, 8.0, 16.0, 32.0, 64.0]))
    lo, hi = chi2_confidence_bounds(grid, N=4096, alpha=0.05, baseline_intercept=0.0)
    baseline = -grid
    assert np.all(lo < baseline)
    assert np.all(hi > baseline)


def test_bounds_widen_for_low_dof():
    # Longer periods → fewer DoF → wider bands.
    grid = np.log(np.array([4.0, 512.0]))
    lo, hi = chi2_confidence_bounds(grid, N=4096, alpha=0.05)
    assert (hi[1] - lo[1]) > (hi[0] - lo[0])


def test_bounds_shift_with_alpha():
    grid = np.log(np.array([16.0]))
    _, hi_95 = chi2_confidence_bounds(grid, N=2048, alpha=0.05)
    _, hi_99 = chi2_confidence_bounds(grid, N=2048, alpha=0.01)
    assert hi_99[0] > hi_95[0]    # tighter alpha → wider upper bound


def test_calibrate_intercept_round_trips():
    c = calibrate_intercept(np.log(16.0), np.log(0.5))
    # ln(E) = -ln(T) + c  →  c = ln(E) + ln(T)
    assert abs(c - (np.log(0.5) + np.log(16.0))) < 1e-12
