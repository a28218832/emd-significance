# 04 · Colored noise: red noise and the fGn extension

Wu & Huang (2004) built their theory on **pure white noise**. In practice,
backgrounds in many fields are **coloured**: meteorology, oceanography,
ECG, finance, low-frequency seismic segments, etc.

- **Red / Brownian noise**: low-frequency energy dominates, strong autocorrelation.
- **Fractional Gaussian noise (fGn)**: parametrised by Hurst exponent $H$.
  - $H = 0.5$: white noise.
  - $H > 0.5$: persistent (long-range positive correlation, e.g. climate).
  - $H < 0.5$: anti-persistent.

Applying the white-noise baseline to a coloured background **yields false
positives on low-frequency IMFs**.

## Why the slope deviates from −1

Flandrin et al. (2004, 2005) extended Wu & Huang's filter-bank analysis
and showed that for fGn

$$\ln(E_m) \approx (\text{slope}(H)) \cdot \ln(T_m) + c.$$

This repo uses Flandrin's empirical approximation:

$$\text{slope}(H) \approx -2H.$$

At $H = 0.5$ the slope returns to $-1$, matching Wu & Huang.

## Practical workflow

### Step 1. Estimate the background Hurst exponent

Standard tools:

- **R/S analysis** — classic, less stable on short data.
- **DFA (Detrended Fluctuation Analysis)** — recommended, robust to
  non-stationarity.
- **Wavelet variance**.

This repo does not ship a Hurst estimator (contributions welcome). Until
then, use [`hurst`](https://pypi.org/project/hurst/) or
[`nolds`](https://pypi.org/project/nolds/).

### Step 2. Correct the theoretical slope

```python
from emdsig import red_noise_slope

H = 0.7                              # from DFA
slope = red_noise_slope(H)           # = -1.4
# baseline: ln(E) = slope * ln(T) + c
```

### Step 3. Monte Carlo with fGn

The closed-form chi-squared derivation is tied to $H = 0.5$. For
coloured backgrounds, **switch to Monte Carlo**:

```python
from emdsig import monte_carlo_bounds

ln_T_grid, lo, hi = monte_carlo_bounds(
    N=len(signal),
    n_trials=200,
    alpha=0.05,
    noise="fgn",                     # key: fGn instead of white
    hurst=H,
    emd_method="ceemdan",
    seed=42,
)
```

Internally `monte_carlo_bounds` calls `emdsig.colored_noise.generate_fgn`
(Davies–Harte circulant embedding) to draw statistically correct fGn
samples efficiently.

### Step 4. Plot and classify (same as white-noise case)

```python
from emdsig import plot_significance
plot_significance(ln_T, ln_E,
                  bounds=(ln_T_grid, lo, hi),
                  title=f"EMD significance test (fGn, H={H})")
```

Full walkthrough in [`notebooks/04_red_noise_extension.ipynb`](../../notebooks/04_red_noise_extension.ipynb).

## When coloured noise matters

| Domain | Typical background | Expected Hurst |
|---|---|---|
| Climate / meteorology | Red noise | $H \in [0.6, 0.9]$ |
| ECG / EEG (low band) | 1/f noise | $H \approx 0.5$–$0.8$ |
| Financial returns | Near-white | $H \approx 0.5$ |
| Seismic (microseism) | Red noise | $H \in [0.6, 0.8]$ |
| Lab measurements, mechanical vibration | Often near-white | $H \approx 0.5$ |

> **Rule of thumb**: on new data, run a DFA first. If $H$ deviates from
> 0.5 significantly, do **not** use closed-form chi-squared blindly.

## Next

Continue to [05 Pitfalls](./05-pitfalls.md) for other real-world gotchas.
