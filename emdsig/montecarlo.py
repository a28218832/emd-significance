"""Monte Carlo confidence bounds (teaching-oriented alternative to chi-squared).

Slower than the closed-form solution but trivially adaptable to any background
noise model: just replace the noise-generating call. Use this in notebooks
and exploratory work; use `confidence.chi2_confidence_bounds` in production.
"""

from __future__ import annotations

from typing import Literal

import numpy as np

from .colored_noise import generate_fgn
from .metrics import compute_et


def _generate_noise(
    N: int,
    kind: Literal["white", "fgn"],
    hurst: float,
    rng: np.random.Generator,
) -> np.ndarray:
    if kind == "white":
        return rng.standard_normal(N)
    if kind == "fgn":
        return generate_fgn(N, hurst=hurst, rng=rng)
    raise ValueError(f"unknown noise kind: {kind!r}")


def monte_carlo_bounds(
    N: int,
    n_trials: int = 100,
    alpha: float = 0.05,
    noise: Literal["white", "fgn"] = "white",
    hurst: float = 0.5,
    trim_ratio: float = 0.05,
    seed: int | None = None,
    emd_method: Literal["emd", "ceemdan"] = "emd",
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Simulate `n_trials` noise realisations, return empirical ln(E) bounds.

    Returns
    -------
    (ln_T_grid, lower, upper)
        Aligned 1-D arrays. The grid is built from the union of all IMF
        periods observed across trials, then bounds are computed per IMF
        index via percentile across trials. For non-uniform IMF counts the
        shorter trials are padded with NaN and ignored by np.nanpercentile.
    """
    # Lazy import so the package can be inspected without PyEMD installed.
    if emd_method == "emd":
        from PyEMD import EMD
        decomposer = EMD()
        decompose = decomposer.emd
    else:
        from PyEMD import CEEMDAN
        decomposer = CEEMDAN()
        decompose = decomposer.ceemdan

    rng = np.random.default_rng(seed)
    all_ln_T: list[np.ndarray] = []
    all_ln_E: list[np.ndarray] = []

    for _ in range(n_trials):
        sample = _generate_noise(N, kind=noise, hurst=hurst, rng=rng)
        imfs = decompose(sample)
        E, T = compute_et(imfs, trim_ratio=trim_ratio)
        valid = ~np.isnan(T)
        all_ln_T.append(np.log(T[valid]))
        all_ln_E.append(np.log(E[valid]))

    max_len = max(len(a) for a in all_ln_T)
    grid = np.full((n_trials, max_len), np.nan)
    ln_E_mat = np.full((n_trials, max_len), np.nan)
    for i, (t, e) in enumerate(zip(all_ln_T, all_ln_E)):
        grid[i, : len(t)] = t
        ln_E_mat[i, : len(e)] = e

    ln_T_grid = np.nanmean(grid, axis=0)
    lower = np.nanpercentile(ln_E_mat, 100 * (alpha / 2), axis=0)
    upper = np.nanpercentile(ln_E_mat, 100 * (1 - alpha / 2), axis=0)
    return ln_T_grid, lower, upper
