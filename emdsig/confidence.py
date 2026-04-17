"""Closed-form chi-squared confidence bounds for EMD significance test.

References
----------
Wu, Z. & Huang, N. E. (2004). A study of the characteristics of white noise
using the empirical mode decomposition method. Proc. R. Soc. Lond. A, 460,
1597-1611. See eqs. (2.13)-(2.17) for the spread function derivation.
"""

from __future__ import annotations

import numpy as np
from scipy.stats import chi2


def _dof(ln_T: np.ndarray, N: int) -> np.ndarray:
    """Effective degrees of freedom for each IMF.

    For white noise, DoF_m = N / T_m (independent samples per IMF).
    """
    T = np.exp(ln_T)
    return np.maximum(N / T, 1.0)


def chi2_confidence_bounds(
    ln_T: np.ndarray,
    N: int,
    alpha: float = 0.05,
    baseline_intercept: float = 0.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Return (lower, upper) ln(E) confidence bounds at significance alpha.

    Parameters
    ----------
    ln_T : 1-D array of natural-log periods for the points being tested.
    N : length of the original time series.
    alpha : two-sided significance level (default 0.05 = 95% CI).
    baseline_intercept : constant c in ln(E) = -ln(T) + c, calibrated from
        a reference IMF (typically c_1) or from theory.

    Returns
    -------
    (lower, upper) : arrays of ln(E) bounds, same shape as ln_T.

    Notes
    -----
    Derivation summary: for a white-noise IMF, N * E_m / sigma_m^2 follows
    a chi-squared distribution with DoF_m = N / T_m. Taking logs and
    rearranging gives the spread function below.
    """
    ln_T = np.asarray(ln_T, dtype=float)
    mean_ln_E = -ln_T + baseline_intercept
    k = _dof(ln_T, N)
    lo = np.log(chi2.ppf(alpha / 2, df=k) / k)
    hi = np.log(chi2.ppf(1 - alpha / 2, df=k) / k)
    return mean_ln_E + lo, mean_ln_E + hi


def calibrate_intercept(
    ln_T_ref: float, ln_E_ref: float
) -> float:
    """Solve c from ln(E) = -ln(T) + c given a reference IMF (default c_1)."""
    return ln_E_ref + ln_T_ref
