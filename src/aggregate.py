def aggregate_monthly(df):
    df = df.copy()

    # create month ONLY if it does not exist
    if "month" not in df.columns:
        df["month"] = df["date"].astype(str).str[:7]

    group_cols = ["state", "district_clean", "month"]

    # aggregate only numeric columns
    agg_cols = df.select_dtypes("number").columns.tolist()

    return (
        df.groupby(group_cols, as_index=False)[agg_cols]
        .sum(min_count=1)
    )
