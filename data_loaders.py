"""Data loaders.

- US factors: Kenneth French Data Library (free, no registration).
- China A-share indices: AKShare (price indices, daily close).

All returns are returned in decimals (0.01 = 1%).
"""

import io
import re
import zipfile

import numpy as np
import pandas as pd
import requests

FRENCH_BASE = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"


# ---------------------------------------------------------------------------
# Kenneth French Data Library
# ---------------------------------------------------------------------------

def parse_french_csv(text: str) -> pd.DataFrame:
    """Parse the first data block of a Ken French CSV file.

    The files start with a few lines of description, and monthly files also
    append an annual block at the end; both are skipped.
    """
    lines = text.splitlines()
    header, rows = None, []
    for i, line in enumerate(lines):
        parts = [p.strip() for p in line.split(",")]
        if re.fullmatch(r"\d{6}|\d{8}", parts[0]):
            if header is None:
                header = [p.strip() for p in lines[i - 1].split(",")][1:]
            rows.append(parts)
        elif rows:                      # end of the first data block
            break

    df = pd.DataFrame([r[1:] for r in rows], columns=header).astype(float)
    df = df.replace([-99.99, -999.0], np.nan) / 100      # percent -> decimal
    dates = [r[0] for r in rows]
    if len(dates[0]) == 6:              # YYYYMM -> monthly Period
        df.index = pd.PeriodIndex(pd.to_datetime(dates, format="%Y%m"), freq="M")
    else:                               # YYYYMMDD -> date
        df.index = pd.to_datetime(dates, format="%Y%m%d")
    return df


def load_french(name: str) -> pd.DataFrame:
    """Download and parse one zipped CSV file from the French Data Library."""
    r = requests.get(FRENCH_BASE + name, timeout=60)
    r.raise_for_status()
    z = zipfile.ZipFile(io.BytesIO(r.content))
    return parse_french_csv(z.read(z.namelist()[0]).decode("latin-1"))


def load_us_factors():
    """Monthly and daily Fama-French 3 factors plus momentum.

    Returns (monthly, daily) DataFrames with columns Mkt-RF, SMB, HML, RF, Mom.
    """
    monthly = load_french("F-F_Research_Data_Factors_CSV.zip").join(
        load_french("F-F_Momentum_Factor_CSV.zip"))
    daily = load_french("F-F_Research_Data_Factors_daily_CSV.zip").join(
        load_french("F-F_Momentum_Factor_daily_CSV.zip"))
    return monthly, daily


# ---------------------------------------------------------------------------
# China A-share indices (AKShare)
# ---------------------------------------------------------------------------

def load_index(symbol: str) -> pd.Series:
    """Daily returns of a China A-share index from AKShare.

    Examples: "sh000001" (SSE Composite), "sh000300" (CSI 300).
    These are price indices (no dividends) and returns are not in excess of
    the risk-free rate.
    """
    import akshare as ak                # imported here so US notebooks don't need it

    raw = ak.stock_zh_index_daily(symbol=symbol)
    raw["date"] = pd.to_datetime(raw["date"])
    raw = raw.set_index("date")
    return raw["close"].pct_change().dropna()
