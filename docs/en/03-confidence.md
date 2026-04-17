# 03 · Confidence bounds: closed-form chi-squared vs Monte Carlo

The core of the significance test is deciding what counts as "plausible for
white noise" on the $\ln(T)$–$\ln(E)$ plane. This repo supplies two
methods: **closed-form chi-squared** (the default for production code) and
**Monte Carlo** (teaching-first, easy to extend).

## 1. Closed-form chi-squared (production default)

### Derivation in one breath

For a white-noise sequence of length $N$, Wu & Huang (2004) showed that
$N \cdot E_m / \sigma^2$ follows a chi-squared distribution with degrees
of freedom

$$k_m = \frac{N}{T_m}.$$

Intuition: the IMF has $N / T_m$ independent "cycles", each contributing
one degree of freedom. The confidence interval is

$$\ln(E_m) \in \big[\, -\ln T_m + c + \ln\tfrac{\chi^2_{\alpha/2, k_m}}{k_m},\;
-\ln T_m + c + \ln\tfrac{\chi^2_{1-\alpha/2, k_m}}{k_m} \,\big].$$

### API

```python
from emdsig import chi2_confidence_bounds

lo, hi = chi2_confidence_bounds(
    ln_T=grid,                  # ln(T) grid to evaluate
    N=len(signal),
    alpha=0.05,                 # two-sided alpha (95% CI)
    baseline_intercept=c,
)
```

### Pros and cons

- ✅ **Fast**: one `scipy.stats.chi2.ppf` call, $O(K)$.
- ✅ **Reproducible**: no randomness, test-friendly.
- ❌ **Assumes white noise**: for coloured backgrounds, switch to Monte
  Carlo or apply the slope correction from [Chapter 4](./04-colored-noise.md).

## 2. Monte Carlo (teaching-first)

### Flow

```
  ┌───────────────────┐
  │ for i in range(M) │
  └─────────┬─────────┘
            ▼
  ┌───────────────────┐   ┌───────────────────────┐
  │ draw noise w_i   │──▶│ swap noise model in    │
  │ (white/red/fGn)  │   │ one line for coloured  │
  └─────────┬─────────┘   └───────────────────────┘
            ▼
  ┌───────────────────┐
  │ EMD / CEEMDAN     │
  │ → IMFs            │
  └─────────┬─────────┘
            ▼
  ┌───────────────────┐
  │ compute (ln T, ln E) │
  └─────────┬─────────┘
            ▼
  aggregate M samples → np.nanpercentile → empirical bounds
```

### API

```python
from emdsig import monte_carlo_bounds

ln_T_grid, lo, hi = monte_carlo_bounds(
    N=2048,
    n_trials=100,
    alpha=0.05,
    noise="white",            # or "fgn"
    hurst=0.5,                # used when noise="fgn"
    emd_method="emd",         # or "ceemdan"
    seed=42,
)
```

### Pros and cons

- ✅ **Intuitive**: a single for-loop captures the statistical idea.
- ✅ **Extensible**: change noise model with one line — white → red →
  1/f → measured background.
- ❌ **Slow**: $M$ full EMDs, each at least $O(N \log N)$.
- ❌ **Sampling noise**: bounds wobble when $M$ is small; use $M \geq 100$.

## 3. Cross-validation

At $N = 1024$, $M = 100$, white noise, the 95% upper-bound gap between
Monte Carlo and closed-form should be $< 5\%$. If not, suspect one of:

1. Too few Monte Carlo trials.
2. Unstable decomposition (try CEEMDAN).
3. Series too short — end effects dominate (increase `trim_ratio`).

See [`notebooks/03_closed_form_chi2.ipynb`](../../notebooks/03_closed_form_chi2.ipynb).

## 4. Which to use

| Scenario | Pick |
|---|---|
| Production, automated pipelines | **Closed-form** |
| Red / fGn background | **Monte Carlo** (or closed-form with slope correction) |
| Teaching, paper figures | **Monte Carlo** (easier to explain) |
| Tiny data ($N < 256$) | **Monte Carlo** (chi-squared approx breaks down) |

## Next

Continue to [04 Colored noise](./04-colored-noise.md) for when the white-noise
assumption fails.
