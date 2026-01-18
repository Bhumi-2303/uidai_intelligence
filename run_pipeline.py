from src.ingest import load_uidai_data
from src.standardize import (
    standardize_enrol,
    standardize_demo,
    standardize_bio
)
from src.normalize_districts import (
    load_district_registry,
    apply_district_normalization
)
from src.aggregate import aggregate_monthly
from src.merge_streams import merge_streams
from src.risk import compute_risk
from src.predict import simple_forecast
from src.action import recommend_actions
from src.eda import (
    before_after_district_count,
    invalid_districts_chart
)
from src.analysis import generate_state_analysis

# =====================================================
# 1️⃣ LOAD RAW UIDAI DATA
# =====================================================
enrol, demo, bio = load_uidai_data()

# =====================================================
# 2️⃣ STANDARDIZE AGE SCHEMAS
# =====================================================
enrol = standardize_enrol(enrol)
demo  = standardize_demo(demo)
bio   = standardize_bio(bio)

# =====================================================
# 3️⃣ SAVE SNAPSHOT (BEFORE DISTRICT NORMALIZATION)
# =====================================================
# This is CRITICAL for before vs after comparison
enrol_before_norm = enrol.copy()

# =====================================================
# 4️⃣ NORMALIZE DISTRICTS USING OFFICIAL REGISTRY
# =====================================================
registry = load_district_registry()

enrol = apply_district_normalization(enrol, registry)
demo  = apply_district_normalization(demo, registry)
bio   = apply_district_normalization(bio, registry)

# =====================================================
# 5️⃣ AGGREGATE MONTHLY (DISTRICT + MONTH)
# =====================================================
enrol_m = aggregate_monthly(enrol)
demo_m  = aggregate_monthly(demo)
bio_m   = aggregate_monthly(bio)

# =====================================================
# 6️⃣ MERGE ENROL + DEMO + BIO STREAMS
# =====================================================
final = merge_streams(enrol_m, demo_m, bio_m)

# =====================================================
# 7️⃣ RISK ANALYSIS, PREDICTION & ACTIONS
# =====================================================
final = compute_risk(final)
final = simple_forecast(final)
final = recommend_actions(final)

# =====================================================
# 8️⃣ SAVE FINAL MASTER TABLE
# =====================================================
final.to_csv("outputs/final_master_table.csv", index=False)

print("✅ Pipeline executed successfully")

# =====================================================
# 9️⃣ BEFORE vs AFTER DATA QUALITY CHARTS
# =====================================================
before_df = enrol_before_norm   # before normalization
after_df  = enrol               # after normalization

before_after_district_count(
    before_df,
    after_df,
    state="Gujarat"
)
invalid_districts_chart(after_df)

print("📊 Before vs After charts generated")

# Generate per-state analysis for all states present in the registry or data
# Use states present in the final dataframe to cover all available states
states = sorted(final["state"].dropna().unique())

for st in states:
    try:
        print(f"🔎 Generating analysis for {st}")
        generate_state_analysis(enrol_before_norm, demo, bio, st)
        # before vs after chart per state
        before_after_district_count(before_df, after_df, state=st)
    except Exception as e:
        print(f"Error generating analysis for {st}: {e}")

