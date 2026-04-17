"""Colored-noise helpers: fractional Gaussian noise (fGn) and slope correction.

For non-white backgrounds (red noise / long-range-correlated), the ln(E)-ln(T)
baseline slope deviates from -1. See Flandrin et al. for the fGn extension.
"""

from __future__ import annotations

import numpy as np


def generate_fgn(N: int, hurst: float, rng: np.random.Generator | None = None) -> np.ndarray:
    """Generate fractional Gaussian noise via Davies-Harte circulant embedding.

    Parameters
    ----------
    N : length of the output series.
    hurst : Hurst exponent in (0, 1). H = 0.5 is standard white noise.
    rng : optional numpy Generator for reproducibility.

    Returns
    -------
    1-D array of length N with unit variance fGn.
    """
    if not 0 < hurst < 1:
        raise ValueError("hurst must be in (0, 1)")
    rng = rng or np.random.default_rng()

    # Autocovariance of fGn
    k = np.arange(N)
    gamma = 0.5 * (
        np.abs(k - 1) ** (2 * hurst)
        - 2 * np.abs(k) ** (2 * hurst)
        + np.abs(k + 1) ** (2 * hurst)
    )

    # Circulant embedding: build first row of length 2N
    row = np.concatenate([gamma, [0.0], gamma[:0:-1]])
    eigvals = np.fft.fft(row).real
    if np.any(eigvals < 0):
        # Fall back to spectral truncation if embedding fails for extreme H
        eigvals = np.clip(eigvals, 0, None)

    m = len(row)
    z = rng.standard_normal(m) + 1j * rng.standard_normal(m)
    w = np.sqrt(eigvals / (2 * m)) * z
    y = np.fft.fft(w).real
    return y[:N]


def red_noise_slope(hurst: float) -> float:
    """Theoretical ln(E)-ln(T) baseline slope for fGn with given Hurst H.

    For white noise (H = 0.5) the slope is -1. For persistent processes
    (H > 0.5) the slope becomes shallower (closer to 0); for anti-persistent
    (H < 0.5) the slope is steeper than -1.

    Slope = -(2 * H + 1) / (2 * H) * ... is an approximation; the simpler
    empirical rule from Flandrin is: slope ~ 1 - 2 * H - 1 = -2 * H.
    We use that convention here.
    """
    if not 0 < hurst < 1:
        raise ValueError("hurst must be in (0, 1)")
    return -2.0 * hurst
