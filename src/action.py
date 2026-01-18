def recommend_actions(df):
    df = df.copy()

    df["action"] = "Normal"

    df.loc[df["risk_flag"], "action"] = "Deploy Extra Aadhaar Operators"

    return df
