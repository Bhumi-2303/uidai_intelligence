import pandas as pd


def aggregate_monthly(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate to district-month level and add simple feature engineering.

    Features added:
    - `total_count`: sum of numeric columns for the district-month
    - `<col>_share`: share of each numeric column over `total_count`
    - `total_count_mom_pct`: month-over-month percent change of `total_count`
    - `total_count_mom_diff`: month-over-month absolute difference
    - `total_count_3m_avg`: rolling 3-month average of `total_count`

    The function uses `district_clean` if present, otherwise `district`.
    """
    df = df.copy()

    # ensure date parsed
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")

    # create month in YYYY-MM
    if "month" not in df.columns:
        if "date" in df.columns:
            df["month"] = df["date"].dt.to_period("M").astype(str)
        else:
            df["month"] = df["month"].astype(str)

    # choose district key
    district_key = "district_clean" if "district_clean" in df.columns else "district"

    group_cols = ["state", district_key, "month"]

    # aggregate only numeric columns
    agg_cols = df.select_dtypes("number").columns.tolist()

    # if there are no numeric cols, return empty grouped frame
    if not agg_cols:
        return df.groupby(group_cols, as_index=False).size().to_frame(name="count")

    grouped = (
        df.groupby(group_cols, as_index=False)[agg_cols]
        .sum(min_count=1)
    )

    # feature: total_count (sum across numeric columns)
    grouped["total_count"] = grouped[agg_cols].sum(axis=1)

    # shares for numeric columns
    for c in agg_cols:
        share_col = f"{c}_share"
        grouped[share_col] = grouped[c] / grouped["total_count"].replace({0: pd.NA})

    # temporal features: month-over-month and rolling averages per state+district
    # convert month to datetime for sorting
    grouped = grouped.copy()
    grouped["_month_dt"] = pd.to_datetime(grouped["month"] + "-01", errors="coerce")

    grouped = grouped.sort_values(["state", district_key, "_month_dt"]) 

    def _compute_temps(g):
        g = g.sort_values("_month_dt")
        g["total_count_mom_diff"] = g["total_count"].diff().fillna(0)
        # pct change: where previous is zero -> inf/NaN, keep NaN
        g["total_count_mom_pct"] = g["total_count"].pct_change().fillna(0)
        g["total_count_3m_avg"] = g["total_count"].rolling(3, min_periods=1).mean()
        return g

    grouped = grouped.groupby(["state", district_key], group_keys=False).apply(_compute_temps)

    # cleanup helper column
    grouped = grouped.drop(columns=["_month_dt"]).reset_index(drop=True)

    return grouped
