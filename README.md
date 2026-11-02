# Volatility-Managed Portfolios: Replication, Real-Time Tests, and Evidence from China's A-Share Market

This project replicates the main result of Moreira & Muir (2017), *"Volatility-Managed Portfolios"* (Journal of Finance), using free data, and then asks how much of the result survives under realistic constraints:

1. **Real-time implementation**: the scaling constant is estimated only from past data, with caps on leverage
2. **Post-publication sample**: 2016 onward, data the paper never saw
3. **Trading costs** from rebalancing the position
4. **A different market**: China's A-share indices (SSE Composite, CSI 300)

All code runs on free data (Kenneth French Data Library and AKShare), so every number below can be reproduced.

## Method

The volatility-managed version of a factor $f$ scales next month's position by the inverse of this month's realized variance:

$$f^{\sigma}_{t} = \frac{c}{RV^2_{t-1}} \, f_t$$

- **Paper version**: $c$ is a constant chosen so that $f^\sigma$ and $f$ have the same full-sample volatility.
- **Real-time version**: $c_t$ is re-estimated each month from data up to month $t-1$ (expanding window, 120-month warm-up for the US, 60 months for A-shares). Positions can be capped (cap = 1 means no leverage).

Performance is evaluated with the spanning regression $f^{\sigma}_t = \alpha + \beta f_t + \varepsilon_t$ (HC1 standard errors) and with Sharpe ratios. Because alpha scales with the average position size, versions with different leverage are compared using Sharpe ratios and t-statistics.

## Key findings

1. **Replication succeeds.** Alphas for the market (4.88% vs. 4.86% in the paper) and momentum (12.80% vs. 12.51%) match Table 1 closely.
2. **Real time, the market result disappears but momentum survives.** Excluding the 1926–1936 warm-up period (which contains the Great Depression), the market factor's alpha is not significant even with the paper's full-sample constant (t = 1.93), and real-time versions have t ≈ 1.3–1.5. Momentum remains strongly significant (t ≈ 4.3–5.1).
3. **Momentum survives rebalancing costs.** The break-even cost is about 1% per unit of position traded, far above the cost of adjusting exposure with futures or ETFs.
4. **After publication (2016 onward), there is no significant evidence either way.** Momentum itself performed poorly in this period (Sharpe 0.10), and ten years is too short to distinguish failure from noise.
5. **In A-shares, volatility timing helps after 2010 but not before.** After 2010, high-volatility months had average returns near zero, and timing raised Sharpe ratios, though not significantly. From 1996 to 2009, high-volatility months had higher average returns, and the real-time constant, estimated on extreme early-1990s data, kept positions around 10%.

## Results

### 1. Replication of Table 1, Panel A (1926–2015)

| | Paper α | Replication α | α s.e. | β | R² | α t-stat | Appraisal ratio |
|---|---|---|---|---|---|---|---|
| Mkt | 4.86 | 4.88 | 1.56 | 0.60 | 0.36 | 3.13 | 0.33 |
| Mom | 12.51 | 12.80 | 1.72 | 0.45 | 0.20 | 7.46 | 0.87 |

Sharpe ratio: Mkt 0.42 → 0.51, Mom 0.49 → 1.00.

### 2. Full-sample vs. real-time scaling (after the 120-month warm-up, through 2015)

| | Original | Full-sample c | Real-time, no cap | Real-time, cap 2 | Real-time, cap 1.5 |
|---|---|---|---|---|---|
| **Mkt** Sharpe | 0.48 | 0.49 | 0.45 | 0.48 | 0.50 |
| Mkt α t-stat | – | 1.93 | 1.45 | 1.31 | 1.37 |
| **Mom** Sharpe | 0.56 | 1.02 | 0.76 | 0.92 | 0.87 |
| Mom α t-stat | – | 7.03 | 4.35 | 5.07 | 4.27 |

Without a cap, the real-time market position reaches 19x, and exceeds 2x in 27% of months.

### 3. Post-publication sample (real-time, cap 2)

| | Period | Months | Sharpe original → managed | α t-stat |
|---|---|---|---|---|
| Mkt | before 2016 | 953 | 0.48 → 0.48 | 1.31 |
| Mkt | 2016 onward | 129 | 0.83 → 0.70 | 0.51 |
| Mom | before 2016 | 948 | 0.56 → 0.92 | 5.07 |
| Mom | 2016 onward | 129 | 0.10 → 0.19 | 0.55 |

### 4. Rebalancing costs (real-time, cap 2, full sample)

Net return $= w_t f_t - \kappa\,|w_t - w_{t-1}|$.

| Cost κ | Mkt Sharpe (original 0.52) | Mom Sharpe (original 0.51) |
|---|---|---|
| 0% | 0.50 | 0.86 |
| 0.1% | 0.47 | 0.83 |
| 0.5% | 0.35 | 0.69 |
| 1.0% | 0.21 | 0.52 |

Average monthly turnover: Mkt 0.40, Mom 0.35.

### 5. China A-share indices (real-time, 60-month warm-up)

| Index (results start) | Cap | Sharpe original → managed | Net of 0.1% cost | α t-stat | Appraisal |
|---|---|---|---|---|---|
| SSE Composite (1996) | 1 | 0.37 → 0.37 | 0.35 | 0.97 | 0.17 |
| SSE Composite (1996) | 2 | 0.37 → 0.36 | 0.34 | 0.91 | 0.16 |
| CSI 300 (2010) | 1 | 0.23 → 0.32 | 0.31 | 1.13 | 0.25 |
| CSI 300 (2010) | 2 | 0.23 → 0.37 | 0.35 | 1.37 | 0.30 |

Over the same months (2010 onward, cap 1), the SSE Composite also improves (0.18 → 0.38), so the difference between the two indices comes from the time period, not the index.

### 6. The paper's premise: volatility is predictable, returns are not

Months sorted into terciles by last month's realized variance (annualized; low → mid → high):

| | Mean return | Volatility | Sharpe |
|---|---|---|---|
| US Mkt | 8.6% / 6.8% / 9.5% | 11% / 15% / 26% | 0.77 / 0.46 / 0.37 |
| US Mom | 10.7% / 8.9% / 2.7% | 7% / 12% / 24% | 1.44 / 0.74 / 0.11 |
| SSE, 1996–2009 | 15.3% / 13.1% / 23.5% | 24% / 27% / 39% | 0.65 / 0.49 / 0.60 |
| SSE, 2010 onward | 7.6% / −0.2% / −0.2% | 17% / 19% / 23% | 0.46 / −0.01 / −0.01 |
| CSI 300 | 10.4% / 15.1% / −0.9% | 18% / 26% / 32% | 0.57 / 0.57 / −0.03 |

In the US, volatility more than doubles across terciles while mean returns stay flat (market) or fall (momentum), which is exactly why scaling by inverse variance works. In A-shares from 1996 to 2009, high-volatility months had *higher* average returns, though the means are noisy and the difference is not statistically significant.

## Caveats

- French data are revised over time, so replicated numbers differ slightly from the paper.
- A-share series are price indices (no dividends) and are not in excess of the risk-free rate.
- Costs include only changes in overall exposure, not the turnover of the underlying factor portfolio, which is the main cost of momentum strategies.
- Short samples (post-2016, A-shares) have large estimation error: a 10-year Sharpe ratio has a standard error of about 0.3.

## Repository structure

| File | Content |
|---|---|
| `vol_tools.py` | Realized variance, volatility-managed portfolios (paper and real-time), costs, regressions |
| `data_loaders.py` | Downloads Kenneth French factors and A-share indices |
| `01_us_replication.ipynb` | Replication of Table 1 |
| `02_us_realtime_and_costs.ipynb` | Real-time scaling, post-publication sample, costs, volatility terciles |
| `03_a_share_index.ipynb` | SSE Composite and CSI 300 |

## How to run

```
pip install -r requirements.txt
```

Then open the notebooks in order. Data are downloaded automatically (about one minute).

## References

- Moreira, A., and Muir, T. (2017). Volatility-Managed Portfolios. *Journal of Finance*, 72(4), 1611–1644.
- Cederburg, S., O'Doherty, M. S., Wang, F., and Yan, X. (2020). On the performance of volatility-managed portfolios. *Journal of Financial Economics*.
- DeMiguel, V., Martín-Utrera, A., and Uppal, R. (2024). A Multifactor Perspective on Volatility-Managed Portfolios. *Journal of Finance*.
- Barroso, P., and Santa-Clara, P. (2015). Momentum has its moments. *Journal of Financial Economics*.
- Daniel, K., and Moskowitz, T. J. (2016). Momentum crashes. *Journal of Financial Economics*.
- McLean, R. D., and Pontiff, J. (2016). Does Academic Research Destroy Stock Return Predictability? *Journal of Finance*.

## Author

Huacheng Chen, Mathematics of Computation, UCLA
