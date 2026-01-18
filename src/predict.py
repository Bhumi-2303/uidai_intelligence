def simple_forecast(df):
    df = df.copy()
    df["next_month_enrol_prediction"] = df["enrol_total"]
    return df
