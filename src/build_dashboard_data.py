import pandas as pd
from pathlib import Path


# ---------------- PATHS ---------------- #

BASE_DIR = Path(__file__).resolve().parents[1]

REGISTRY_PATH = BASE_DIR / "data" / "registry" / "districts.csv"
AFTER_DIR = BASE_DIR / "outputs" / "after"
DASHBOARD_DIR = BASE_DIR / "outputs" / "dashboard"

DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)


# ---------------- LOAD REGISTRY ---------------- #

registry = pd.read_csv(REGISTRY_PATH)

registry["state_norm"] = (
    registry["state"]
    .astype(str)
    .str.upper()
    .str.strip()
)

registry["district_norm"] = (
    registry["district"]
    .astype(str)
    .str.upper()
    .str.strip()
)

official_pairs = set(
    zip(registry["state_norm"], registry["district_norm"])
)


# ---------------- HELPER ---------------- #

def load_and_prepare(path, value_columns):
    """
    Load a normalized dataset, keep only official districts,
    and aggregate for dashboard use.
    """
    df = pd.read_csv(path)

    df["state_norm"] = (
        df["state"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    df["district_norm"] = (
        df["district_final"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    # Keep only official (state, district)
    df = df[
        df.apply(
            lambda r: (r["state_norm"], r["district_norm"]) in official_pairs,
            axis=1
        )
    ]

    # Aggregate
    df_agg = (
        df.groupby(["state", "district_final"], as_index=False)[value_columns]
        .sum()
    )

    return df_agg.rename(columns={"district_final": "district"})


# ---------------- LOAD & PROCESS STREAMS ---------------- #

print("📊 Building dashboard dataset...")

bio_df = load_and_prepare(
    AFTER_DIR / "biometric_districts_normalized.csv",
    value_columns=["bio_age_5_17", "bio_age_17_"]
)

enrol_df = load_and_prepare(
    AFTER_DIR / "enrolment_districts_normalized.csv",
    value_columns=["age_0_5", "age_5_17", "age_18_greater"]
)

demo_df = load_and_prepare(
    AFTER_DIR / "demographic_districts_normalized.csv",
    value_columns=["demo_age_5_17", "demo_age_17_"]
)


# ---------------- MERGE ALL ---------------- #

dashboard_df = (
    enrol_df
    .merge(bio_df, on=["state", "district"], how="outer")
    .merge(demo_df, on=["state", "district"], how="outer")
)

dashboard_df = dashboard_df.fillna(0)

dashboard_df = dashboard_df.sort_values(
    ["state", "district"]
)


# ---------------- SAVE ---------------- #

out_file = DASHBOARD_DIR / "dashboard_data.csv"
dashboard_df.to_csv(out_file, index=False)

print("✅ Dashboard data created successfully")
print(f"📁 Output → {out_file}")
print(f"📊 Rows → {len(dashboard_df)}")
