def _get_col(df, possible_names):
    """
    Returns the first column found from possible_names.
    """
    for col in possible_names:
        if col in df.columns:
            return df[col]
    return None


# ---------------- ENROLMENT ----------------

def standardize_enrol(df):
    df = df.copy()

    age_0_5 = _get_col(df, ["age_0_5", "age_0_4"])
    age_5_17 = _get_col(df, ["age_5_17", "age_5_17_years"])
    age_18 = _get_col(df, ["age_18_greater", "age_18_plus"])

    df["child_0_5"] = age_0_5
    df["child_5_17"] = age_5_17
    df["adult_18_plus"] = age_18

    df["enrol_total"] = (
        df["child_0_5"].fillna(0) +
        df["child_5_17"].fillna(0) +
        df["adult_18_plus"].fillna(0)
    )

    return df


# ---------------- DEMOGRAPHIC UPDATE ----------------

def standardize_demo(df):
    df = df.copy()

    age_5_17 = _get_col(df, ["age_5_17", "age_5_17_years", "age_5_17_update"])
    age_18 = _get_col(df, ["age_18_greater", "age_18_plus", "age_18_update"])

    df["child_0_5"] = None
    df["child_5_17"] = age_5_17
    df["adult_18_plus"] = age_18

    df["demo_updates"] = (
        df["child_5_17"].fillna(0) +
        df["adult_18_plus"].fillna(0)
    )

    return df


# ---------------- BIOMETRIC UPDATE ----------------

def standardize_bio(df):
    df = df.copy()

    age_5_17 = _get_col(df, ["age_5_17", "age_5_17_years", "age_5_17_bio"])
    age_18 = _get_col(df, ["age_18_greater", "age_18_plus", "age_18_bio"])

    df["child_0_5"] = None
    df["child_5_17"] = age_5_17
    df["adult_18_plus"] = age_18

    df["bio_updates"] = (
        df["child_5_17"].fillna(0) +
        df["adult_18_plus"].fillna(0)
    )

    return df
