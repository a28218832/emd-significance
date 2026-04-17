# emd-significance

> The missing EMD significance-test toolkit — an educational, bilingual (EN / 繁中) GitHub repo.

[繁體中文版 README → README.zh-TW.md](./README.zh-TW.md)

`emd-significance` is a small teaching-focused repository that implements the
statistical significance test for Empirical Mode Decomposition (EMD) proposed
by **Wu & Huang (2004)**. The test uses the relationship between the natural
logarithm of IMF energy and period, **ln(E) vs ln(T)**, to decide whether an
intrinsic mode function (IMF) contains a real physical signal or is
statistically indistinguishable from noise.

The public Python ecosystem has mature EMD decomposition libraries (`EMD-signal`,
aka PyEMD) but no ready-made API for the significance test itself. This repo
fills that gap with a minimal module (`emdsig/`), a bilingual technical
reference under `docs/`, and runnable Jupyter notebooks under `notebooks/`.

---

## Why this exists

- **Decomposition is solved; interpretation is not.** PyEMD gives you IMFs
  but does not tell you which IMFs are signal and which are noise.
- **Closed-form vs Monte Carlo.** The production-grade chi-squared bounds
  are efficient and reproducible; Monte Carlo is easier to reason about and
  trivially extensible to colored-noise backgrounds. Both are implemented.
- **Documentation-first.** Every function has a doc chapter behind it, in
  English and Traditional Chinese.

## 30-second quickstart

```python
import numpy as np
from PyEMD import EMD
from emdsig import compute_et, chi2_confidence_bounds, calibrate_intercept, plot_significance

N = 2048
t = np.arange(N)
signal = np.sin(2 * np.pi * t / 64) + 0.5 * np.random.randn(N)

imfs = EMD().emd(signal)
E, T = compute_et(imfs)
ln_T, ln_E = np.log(T[~np.isnan(T)]), np.log(E[~np.isnan(T)])

c = calibrate_intercept(ln_T[0], ln_E[0])     # anchor on c_1
grid = np.linspace(ln_T.min() - 0.5, ln_T.max() + 0.5, 100)
lo, hi = chi2_confidence_bounds(grid, N=N, alpha=0.05, baseline_intercept=c)

plot_significance(ln_T, ln_E, bounds=(grid, lo, hi), baseline_intercept=c,
                  title="EMD significance test")
```

IMFs whose point lies **above** the upper band are statistically significant
(real signal); points within the band are indistinguishable from white noise.

## Repository map

| Path | Purpose |
|---|---|
| [`emdsig/`](./emdsig) | Core module: `metrics`, `confidence`, `montecarlo`, `colored_noise`, `plot`. |
| [`docs/en/`](./docs/en) / [`docs/zh-TW/`](./docs/zh-TW) | Five-chapter technical reference, bilingual. |
| [`notebooks/`](./notebooks) | Runnable tutorials (01 quickstart → 05 case study). |
| [`tests/`](./tests) | `pytest` smoke tests for the core API. |

### Reading order

1. [Principle](./docs/en/01-principle.md) — why ln(E) and ln(T)?
2. [Workflow](./docs/en/02-workflow.md) — six steps end-to-end.
3. [Confidence bounds](./docs/en/03-confidence.md) — closed-form vs Monte Carlo.
4. [Colored noise](./docs/en/04-colored-noise.md) — red noise / fGn extension.
5. [Pitfalls](./docs/en/05-pitfalls.md) — mode mixing, end effects, anchor failure.

## Installation

Recommended — with **conda** (the same setup used by this repo's tests):

```bash
git clone https://github.com/<your-handle>/emd-significance.git
cd emd-significance

conda create -n emdsig -c conda-forge python=3.10 numpy scipy matplotlib jupyter pytest -y
conda activate emdsig
pip install EMD-signal   # not on conda-forge; install inside the env
```

Or, if you prefer plain pip:

```bash
pip install -r requirements.txt
```

Python 3.9+ is recommended. The only non-standard dependency is
[`EMD-signal`](https://pyemd.readthedocs.io) (imported as `PyEMD`).

## Primary reference

```bibtex
@article{wu2004white,
  title   = {A study of the characteristics of white noise using the
             empirical mode decomposition method},
  author  = {Wu, Zhaohua and Huang, Norden E.},
  journal = {Proc. R. Soc. Lond. A},
  volume  = {460},
  number  = {2046},
  pages   = {1597--1611},
  year    = {2004},
}
```

See [`docs/en/01-principle.md`](./docs/en/01-principle.md) for the full
reading list including Flandrin's extension to fractional Gaussian noise.

## License

MIT — see [LICENSE](./LICENSE). Contributions welcome; please open an issue
before large changes.
