# emd-significance

> 把 EMD 統計顯著性檢定（Wu & Huang 2004 的 ln(E) vs ln(T) 方法）做成中英雙語的教學型 GitHub repo。

[English README → README.md](./README.md)

`emd-significance` 是一個小型的教學導向專案，專門實作 **Wu & Huang (2004)**
提出的 EMD 統計顯著性檢定。這套方法用 IMF 的**能量對數 ln(E)** 與
**週期對數 ln(T)** 的關係，判斷一個本質模態函數（IMF）到底是真實的物理訊號，
還是在統計意義上與雜訊無法區分。

目前 Python 生態系有成熟的 EMD 分解套件（`EMD-signal`，也就是 PyEMD），
但**沒有**現成、開箱即用的顯著性檢定 API。這個 repo 就是來補這一塊空缺，
提供：

- 一個極簡的 Python 模組 `emdsig/`
- 中英文雙語的技術文檔（`docs/en/`、`docs/zh-TW/`）
- 可直接執行的 Jupyter 教學 Notebook（`notebooks/`）

---

## 為什麼需要這個 repo

- **分解已經是成熟問題，判讀還不是。** PyEMD 可以給你 IMF，但沒告訴你
  哪個 IMF 是訊號、哪個是雜訊。
- **閉式解 vs 蒙地卡羅。** 卡方閉式解效能好、可重現，適合正式 code；
  Monte Carlo 則直觀、容易擴展到各種有色雜訊。兩者都提供。
- **文件優先。** 每個函式背後都有對應的文檔章節，中英文同步。

## 30 秒快速開始

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

c = calibrate_intercept(ln_T[0], ln_E[0])     # 以 c_1 定錨
grid = np.linspace(ln_T.min() - 0.5, ln_T.max() + 0.5, 100)
lo, hi = chi2_confidence_bounds(grid, N=N, alpha=0.05, baseline_intercept=c)

plot_significance(ln_T, ln_E, bounds=(grid, lo, hi), baseline_intercept=c,
                  title="EMD 顯著性檢定")
```

落在**上限之上**的 IMF 具有統計顯著性（真實訊號）；落在信賴帶之內的
IMF 與白雜訊沒有可區分的差異，應視為背景雜訊。

## 專案目錄

| 路徑 | 用途 |
|---|---|
| [`emdsig/`](./emdsig) | 核心模組：`metrics`、`confidence`、`montecarlo`、`colored_noise`、`plot`。 |
| [`docs/en/`](./docs/en) / [`docs/zh-TW/`](./docs/zh-TW) | 雙語五章技術文檔。 |
| [`notebooks/`](./notebooks) | 可直接執行的教學 Notebook（01 quickstart → 05 案例研究）。 |
| [`tests/`](./tests) | `pytest` 基本測試。 |

### 建議閱讀順序

1. [原理](./docs/zh-TW/01-原理.md) — 為什麼是 ln(E) 與 ln(T)？
2. [分析流程](./docs/zh-TW/02-分析流程.md) — 完整六步驟。
3. [信賴邊界](./docs/zh-TW/03-信賴邊界.md) — 閉式解 vs Monte Carlo。
4. [有色雜訊](./docs/zh-TW/04-有色雜訊.md) — 紅雜訊／fGn 擴展。
5. [避坑指南](./docs/zh-TW/05-避坑指南.md) — 模態混疊、邊界效應、定錨失真。

## 安裝

推薦使用 **conda**（本 repo 的測試環境即是如此）：

```bash
git clone https://github.com/<your-handle>/emd-significance.git
cd emd-significance

conda create -n emdsig -c conda-forge python=3.10 numpy scipy matplotlib jupyter pytest -y
conda activate emdsig
pip install EMD-signal   # conda-forge 沒有，在已啟用的 env 內用 pip 安裝
```

或使用純 pip：

```bash
pip install -r requirements.txt
```

建議 Python 3.9 以上。唯一非標準依賴是
[`EMD-signal`](https://pyemd.readthedocs.io)（在程式裡以 `PyEMD` 匯入）。

## 主要參考文獻

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

完整文獻清單（含 Flandrin 對分數高斯雜訊的延伸）請見
[`docs/zh-TW/01-原理.md`](./docs/zh-TW/01-原理.md)。

## 授權

MIT — 詳見 [LICENSE](./LICENSE)。歡迎貢獻，大幅修改前請先開 issue 討論。
