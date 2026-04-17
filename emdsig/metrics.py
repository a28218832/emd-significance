"""Energy and period metrics for IMFs, following Wu & Huang (2004)."""

from __future__ import annotations

import numpy as np


def _trim(imf: np.ndarray, trim_ratio: float) -> np.ndarray:
    if trim_ratio <= 0:
        return imf
    if not 0 <= trim_ratio < 0.5:
        raise ValueError("trim_ratio must be in [0, 0.5)")
    n = len(imf)
    k = int(n * trim_ratio)
    return imf[k : n - k] if k > 0 else imf


def energy(imf: np.ndarray, trim_ratio: float = 0.05) -> float:
    """Mean-square energy density E_m = (1/N) * sum(c_m^2).

    `trim_ratio` drops both ends before computing variance to suppress
    spline-overshoot end effects (see Wu & Huang 2004; end-effect caveat).
    """
    segment = _trim(np.asarray(imf, dtype=float), trim_ratio)
    return float(np.mean(segment ** 2))


def period(imf: np.ndarray) -> float:
    """Mean period T_m = N / N_zero_crossings.

    Returns NaN when the IMF has no zero crossings (typical for the residual).
    """
    arr = np.asarray(imf, dtype=float)
    n = len(arr)
    signs = np.sign(arr)
    signs[signs == 0] = 1  # treat exact zeros as positive to avoid double-counts
    n_zc = int(np.sum(np.diff(signs) != 0))
    if n_zc == 0:
        return float("nan")
    return float(n / n_zc)


def compute_et(
    imfs: np.ndarray, trim_ratio: float = 0.05
) -> tuple[np.ndarray, np.ndarray]:
    """Compute (E, T) arrays for a stack of IMFs with shape (n_imfs, N)."""
    imfs = np.asarray(imfs, dtype=float)
    if imfs.ndim != 2:
        raise ValueError("imfs must be 2-D with shape (n_imfs, N)")
    energies = np.array([energy(row, trim_ratio) for row in imfs])
    periods = np.array([period(row) for row in imfs])
    return energies, periods
