def compute_risk(df):
    df = df.copy()

    df["update_pressure"] = (
        df.get("demo_updates", 0).fillna(0) +
        df.get("bio_updates", 0).fillna(0)
    ) / df["enrol_total"]

    df["risk_flag"] = df["update_pressure"] > 0.5

    return df
