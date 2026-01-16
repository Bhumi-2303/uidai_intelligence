import pandas as pd


def load_district_registry(path="data/registry/districts.csv"):
    """
    Loads district registry and returns a dict:
    {
        "GUJARAT": set([...]),
        "MAHARASHTRA": set([...]),
        "RAJASTHAN": set([...])
    }
    """
    reg = pd.read_csv(path)

    # normalize text
    reg["state"] = reg["state"].str.upper().str.strip()
    reg["district"] = reg["district"].str.upper().str.strip()

    registry = (
        reg.groupby("state")["district"]
        .apply(set)
        .to_dict()
    )

    return registry


def apply_district_normalization(df, registry):
    """
    Adds:
    - district_clean
    - is_valid_district
    State-aware normalization (NO cross-state leakage)
    """
    df = df.copy()

    # normalize incoming text
    df["state"] = df["state"].str.upper().str.strip()
    df["district"] = df["district"].str.upper().str.strip()

    clean = []
    valid = []

    for _, row in df.iterrows():
        state = row["state"]
        dist = row["district"]

        if state in registry and dist in registry[state]:
            clean.append(dist)
            valid.append(True)
        else:
            clean.append(dist)
            valid.append(False)

    df["district_clean"] = clean
    df["is_valid_district"] = valid

    return df
