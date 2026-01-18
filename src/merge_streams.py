def merge_streams(enrol, demo, bio):
    df = enrol.merge(
        demo, on=["state", "district_clean", "month"], how="outer"
    )
    df = df.merge(
        bio, on=["state", "district_clean", "month"], how="outer"
    )
    return df
