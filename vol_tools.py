"""Core analysis functions for volatility-managed portfolios.

All return series are in decimals (0.01 = 1%).
Monthly series are indexed by pandas monthly Periods; daily series by dates.

Reference: Moreira, A. and Muir, T. (2017), "Volatility-Managed Portfolios",
Journal of Finance 72(4), 1611-1644.
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm


# ---------------------------------------------------------------------------
# Building blocks
# ---------------------------------------------------------------------------

def to_monthly(daily_ret: pd.Series) -> pd.Series:
    """Compound daily returns into monthly returns: prod(1 + r_d) - 1."""
    return (1 + daily_ret).groupby(daily_ret.index.to_period("M")).prod() - 1


def realized_variance(daily_ret: pd.Series) -> pd.Series:
    """Monthly realized variance: sum over the month of (r_d - monthly mean)^2.

    This follows the definition in Moreira & Muir (2017).
    """
    month = daily_ret.index.to_period("M")
    return daily_ret.groupby(month).apply(lambda g: ((g - g.mean()) ** 2).sum())


def sharpe(r: pd.Series) -> float:
    """Annualized Sharpe ratio of a monthly (excess) return series."""
    return r.mean() / r.std() * np.sqrt(12)


# ---------------------------------------------------------------------------
# Volatility-managed portfolios
# ---------------------------------------------------------------------------

def vol_managed(f: pd.Series, rv: pd.Series):
    """Volatility-managed factor with a full-sample scaling constant (as in the paper).

        f_sigma_t = c / RV_{t-1} * f_t

    c is chosen so that f_sigma has the same full-sample standard deviation as f.
    Note: c uses the whole sample, so it is not known in real time. A constant c
    does not change Sharpe ratios or t-statistics, only the scale of returns.

    Returns (f_sigma, weight, c).
    """
    raw_w = 1 / rv.shift(1)                 # position uses LAST month's variance
    raw = (raw_w * f).dropna()
    c = f.loc[raw.index].std() / raw.std()
    f_sigma = c * raw
    weight = (c * raw_w).loc[f_sigma.index]
    return f_sigma, weight, c


def vol_managed_rt(f: pd.Series, rv: pd.Series, warmup: int = 120, cap=None):
    """Real-time volatility-managed factor.

    The scaling constant c_t is re-estimated each month using only data available
    up to month t-1 (expanding window), so the strategy has no look-ahead.

    warmup : number of months needed before c_t is first estimated
    cap    : optional upper bound on the position (e.g. 1 = no leverage)

    Returns (f_sigma, weight).
    """
    raw_w = 1 / rv.shift(1)
    raw = (raw_w * f).dropna()
    f_al = f.loc[raw.index]

    c_rt = (f_al.expanding(min_periods=warmup).std()
            / raw.expanding(min_periods=warmup).std()).shift(1)   # only past data
    weight = (c_rt * raw_w.loc[raw.index]).dropna()

    if cap is not None:
        weight = weight.clip(upper=cap)

    f_sigma = weight * f.loc[weight.index]
    return f_sigma, weight


def net_of_cost(f_sigma: pd.Series, weight: pd.Series, kappa: float) -> pd.Series:
    """Subtract the cost of rebalancing the position: kappa * |w_t - w_{t-1}|.

    Only the cost of changing overall exposure is included, not the cost of
    rebalancing the underlying factor portfolio.
    """
    turnover = weight.diff().abs()
    return (f_sigma - kappa * turnover).dropna()


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def spanning_regression(f_sigma: pd.Series, f: pd.Series) -> dict:
    """Regress the managed factor on the original factor: f_sigma = alpha + beta * f + e.

    Uses heteroskedasticity-robust (HC1) standard errors. As in Table 1 of the
    paper, alpha, its standard error and rmse are annualized in percent
    (monthly decimal x 1200). The appraisal ratio is alpha / rmse * sqrt(12).
    """
    x = f.loc[f_sigma.index]
    res = sm.OLS(f_sigma, sm.add_constant(x)).fit(cov_type="HC1")
    alpha = res.params.iloc[0]
    rmse = res.resid.std()
    return {
        "alpha": alpha * 1200,
        "alpha_se": res.bse.iloc[0] * 1200,
        "beta": res.params.iloc[1],
        "beta_se": res.bse.iloc[1],
        "N": int(res.nobs),
        "r2": res.rsquared,
        "rmse": rmse * 1200,
        "appraisal": alpha / rmse * np.sqrt(12),
    }


def vol_buckets(f: pd.Series, rv: pd.Series) -> pd.DataFrame:
    """Sort months into terciles by LAST month's realized variance.

    For each tercile, report the annualized mean, standard deviation and Sharpe
    ratio of this month's return. The paper's premise is that volatility rises
    across terciles while the mean return does not.
    """
    df = pd.DataFrame({"prev_var": rv.shift(1), "ret": f}).dropna()
    df["bucket"] = pd.qcut(df["prev_var"], 3, labels=["low", "mid", "high"])
    out = df.groupby("bucket", observed=True)["ret"].agg(["mean", "std"])
    out["mean"] = out["mean"] * 12
    out["std"] = out["std"] * np.sqrt(12)
    out["sharpe"] = out["mean"] / out["std"]
    return out
