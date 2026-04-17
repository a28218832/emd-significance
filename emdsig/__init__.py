"""emdsig — EMD significance test toolkit.

A small, educational Python library implementing the ln(E)-vs-ln(T)
significance test for Empirical Mode Decomposition, following
Wu & Huang (2004).
"""

from .colored_noise import generate_fgn, red_noise_slope
from .confidence import calibrate_intercept, chi2_confidence_bounds
from .metrics import compute_et, energy, period
from .montecarlo import monte_carlo_bounds
from .plot import plot_significance

__all__ = [
    "energy",
    "period",
    "compute_et",
    "chi2_confidence_bounds",
    "calibrate_intercept",
    "monte_carlo_bounds",
    "generate_fgn",
    "red_noise_slope",
    "plot_significance",
]

__version__ = "0.1.0"
