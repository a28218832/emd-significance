# 05 · Pitfalls: the four most common real-world traps

Here are the four traps people hit when applying the EMD significance test
to real data, each paired with how this repo handles it.

---

## 1. White-noise assumption fails (red / fGn background)

**Symptom**: low-frequency IMFs sit far above the baseline and look
"significant", but you suspect they are just a coloured-noise pile-up.

**Detection**:

- DFA the background segment for Hurst $H$. If $|H - 0.5| > 0.1$, white-noise
  fails.
- Fit a line through the first few IMFs and check how far the slope deviates
  from $-1$.

**Handling**: see [04 Colored noise](./04-colored-noise.md):

```python
from emdsig import monte_carlo_bounds, red_noise_slope
slope = red_noise_slope(H)
grid, lo, hi = monte_carlo_bounds(N, noise="fgn", hurst=H, ...)
```

---

## 2. $c_1$ anchoring failure

**Symptom**: in vibration sensing, radar, etc., the highest frequency is
**the signal itself**. Anchoring on $c_1$ drags the whole baseline up, and
all downstream IMFs vanish into the confidence band (false negatives).

**Detection**:

- Check whether $E_1$ is "abnormally high" (orders of magnitude above $E_2$).
- Fit the baseline on a quieter mid-range IMF or residual instead.

**Handling**: `calibrate_intercept` accepts any IMF you trust:

```python
from emdsig import calibrate_intercept
# anchor on c_3 instead of c_1
c = calibrate_intercept(ln_T[2], ln_E[2])
```

Alternatively, run a long measurement of a quiet period through EMD to get
a real-noise $c$, then reuse it.

---

## 3. Mode mixing

**Symptom**: a single IMF mixes scales (e.g. intermittent high-frequency
spikes chop up a low-frequency oscillation). $E_m$ and $T_m$ lose physical
meaning and the test cannot be trusted.

**Detection**:

- By eye: the IMF envelope amplitude varies wildly across segments.
- Quantitatively: sliding-window $T_m$ with stddev > 20% of the mean.

**Handling**: **switch to CEEMDAN** (or EEMD).

```python
from PyEMD import CEEMDAN
imfs = CEEMDAN().ceemdan(signal)     # replaces EMD().emd(signal)
```

All examples in this repo default to CEEMDAN.

---

## 4. End effects

**Symptom**: EMD's envelope spline diverges at the two ends (overshoot),
contaminating 5–10% of the series on each side. If $N$ is small the
contamination dominates $E_m$.

**Detection**:

- Plot the IMF; look for large spikes near the boundaries.
- Compare $E_m$ under `trim_ratio=0` vs `trim_ratio=0.1`. A > 20% gap means
  serious end effects.

**Handling**: `emdsig.metrics.energy` defaults to `trim_ratio=0.05` (drop
5% from each end). Bump to 0.1 for noisy cases:

```python
from emdsig import energy
E = energy(imf, trim_ratio=0.1)     # drop 10% each end
```

> **Best fix**: use longer data when possible ($N \geq 2^{10}$ recommended).
> When the series is short, annotate every result with an end-effect caveat.

---

## 5. Other things to watch

- **Period estimator**: this repo uses zero-crossings (fast, robust). For
  very short high-frequency IMFs, local-extrema counting may work better.
  Differences are typically < 10%.
- **IMF count**: PyEMD's default `max_imf` sometimes over-decomposes and
  the last "IMF" is essentially a residual. Plot IMF index vs $\ln T$;
  drop the trailing points if they fall off the line.
- **Statistically significant ≠ physically meaningful**. Passing the test
  is necessary but not sufficient; corroborate with time-frequency analysis
  and domain knowledge.

## Table of contents

- [01 Principle](./01-principle.md) · [02 Workflow](./02-workflow.md) · [03 Confidence](./03-confidence.md) · [04 Colored noise](./04-colored-noise.md) · 05 Pitfalls (this chapter)
