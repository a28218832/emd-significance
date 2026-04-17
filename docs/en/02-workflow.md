# 02 · Workflow: the six-step pipeline

This chapter turns the theory from [Chapter 1](./01-principle.md) into six
runnable steps. Each step maps to a function in `emdsig/`.

## Step 1. Decompose with EMD or CEEMDAN

Split the time series $x(t)$ into $n$ IMFs $c_m(t)$ plus a residual $r(t)$.

```python
import numpy as np
from PyEMD import CEEMDAN            # CEEMDAN recommended to avoid mode mixing

x = np.loadtxt("examples/sample_signal.csv")
imfs = CEEMDAN().ceemdan(x)          # shape: (n_imfs, N)
```

> **Why CEEMDAN?** Vanilla EMD is prone to mode mixing, which destroys the
> physical meaning of $E_m$ and $T_m$. See
> [05 Pitfalls §3](./05-pitfalls.md).

## Step 2. Energy density $E_m$ per IMF

$$E_m = \frac{1}{N} \sum_{i=1}^{N} \big[c_m(t_i)\big]^2,$$

which is just the variance. `emdsig.metrics.energy` trims 5% off each end
by default to suppress end effects.

```python
from emdsig import energy, compute_et
E = energy(imfs[0], trim_ratio=0.05)
E_all, T_all = compute_et(imfs, trim_ratio=0.05)
```

## Step 3. Mean period $T_m$ per IMF

Using zero crossings (fast and robust):

$$T_m = \frac{N}{N_z}, \quad N_z = \#\{i : \text{sign}\,c_m(t_i) \neq \text{sign}\,c_m(t_{i+1})\}.$$

```python
from emdsig import period
T = period(imfs[0])
```

The residual has no zero crossings; the function returns `NaN`, filtered
upstream with `~np.isnan(T)`.

## Step 4. Anchor the baseline

The constant $c$ in $\ln(E) = -\ln(T) + c$ is calibrated from a trusted
noise-like IMF. Convention: use $c_1$ (highest frequency, usually noise):

```python
from emdsig import calibrate_intercept
ln_T = np.log(T_all[~np.isnan(T_all)])
ln_E = np.log(E_all[~np.isnan(T_all)])
c = calibrate_intercept(ln_T[0], ln_E[0])
```

If the highest frequency is the signal itself (e.g. high-frequency vibration
sensing), this anchoring fails. See [05 Pitfalls §2](./05-pitfalls.md).

## Step 5. Scatter + confidence bounds

```python
from emdsig import chi2_confidence_bounds, plot_significance

N = len(x)
grid = np.linspace(ln_T.min() - 0.5, ln_T.max() + 0.5, 100)
lo, hi = chi2_confidence_bounds(grid, N=N, alpha=0.05, baseline_intercept=c)

plot_significance(ln_T, ln_E,
                  bounds=(grid, lo, hi),
                  baseline_intercept=c,
                  title="EMD significance test")
```

## Step 6. Classify and filter

| Position | Verdict | Action |
|---|---|---|
| Above upper bound | Statistically significant | **Keep** for feature extraction / reconstruction. |
| Inside the band | Indistinguishable from noise | **Drop**, or treat as background. |
| Below lower bound | Anomalously low energy | Investigate: over-smoothing or data artefact. |

Reconstruct the filtered signal:

```python
significant = ln_E > hi_at_their_ln_T     # boolean mask
filtered_signal = imfs[significant].sum(axis=0)
```

## One-shot example

See [`notebooks/01_quickstart.ipynb`](../../notebooks/01_quickstart.ipynb)
for the full runnable pipeline.

## Next

Continue to [03 Confidence bounds](./03-confidence.md) for the closed-form
vs Monte Carlo discussion.
