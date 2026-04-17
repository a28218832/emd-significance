"""Plot helpers for the ln(E)-ln(T) significance diagram."""

from __future__ import annotations

from typing import Optional

import numpy as np


def plot_significance(
    ln_T: np.ndarray,
    ln_E: np.ndarray,
    bounds: Optional[tuple[np.ndarray, np.ndarray, np.ndarray]] = None,
    baseline_intercept: Optional[float] = None,
    title: str | None = None,
    ax=None,
):
    """Render the ln(E) vs ln(T) scatter with optional bounds and baseline.

    Parameters
    ----------
    ln_T, ln_E : IMF coordinates.
    bounds : optional (ln_T_grid, lower, upper) from Monte Carlo or chi2.
    baseline_intercept : if given, draws ln(E) = -ln(T) + c.
    """
    import matplotlib.pyplot as plt

    if ax is None:
        _, ax = plt.subplots(figsize=(8, 6))

    ax.scatter(ln_T, ln_E, color="crimson", zorder=5, label="IMFs")

    if baseline_intercept is not None:
        x = np.linspace(np.min(ln_T) - 0.5, np.max(ln_T) + 0.5, 100)
        ax.plot(x, -x + baseline_intercept, "b--", label="Baseline (slope -1)")

    if bounds is not None:
        grid, lo, hi = bounds
        order = np.argsort(grid)
        ax.fill_between(
            grid[order], lo[order], hi[order],
            color="steelblue", alpha=0.2, label="Confidence band",
        )

    ax.set_xlabel("ln(T)  —  log mean period")
    ax.set_ylabel("ln(E)  —  log mean energy")
    if title:
        ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    return ax
