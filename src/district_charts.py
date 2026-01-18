import pandas as pd
import matplotlib.pyplot as plt
import shutil
from pathlib import Path


# ---------------- PATHS ---------------- #

CHART_OUTPUT_DIR = Path("outputs/after/charts")
DATASETS = ["biometric", "demographic", "enrolment"]


# Clean up old charts
if CHART_OUTPUT_DIR.exists():
    shutil.rmtree(CHART_OUTPUT_DIR)
    print(f"🗑️  Removed old charts from {CHART_OUTPUT_DIR}")

CHART_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# Function to generate all charts for a dataset
def generate_charts_for_dataset(source_name: str):
    """Generate all visualization charts for a given dataset"""
    
    print(f"\n{'='*80}")
    print(f"Generating charts for: {source_name}")
    print(f"{'='*80}")
    
    # Load normalized data
    data_file = Path(f"outputs/after/{source_name}_districts_normalized.csv")
    if not data_file.exists():
        print(f"⚠️  Data file not found: {data_file}")
        return
    
    df = pd.read_csv(data_file)
    
    # Create subdirectory for this dataset
    dataset_charts_dir = CHART_OUTPUT_DIR / source_name
    dataset_charts_dir.mkdir(parents=True, exist_ok=True)
    
    # Chart 1: Unique districts before vs after
    before_count = df["district"].nunique()
    after_count = df["district_final"].nunique()

    plt.figure(figsize=(10, 6))
    plt.bar(
        ["Before Normalization", "After Normalization"],
        [before_count, after_count],
        color=['#FF6B6B', '#4ECDC4'],
        alpha=0.8
    )
    plt.title(f"{source_name.title()}: Unique Districts Before vs After Normalization", fontsize=14, fontweight='bold')
    plt.ylabel("Count", fontsize=12)
    plt.ylim(0, max(before_count, after_count) * 1.1)
    for i, v in enumerate([before_count, after_count]):
        plt.text(i, v + 2, str(v), ha='center', fontweight='bold')
    plt.tight_layout()
    plt.savefig(dataset_charts_dir / "01_district_count_before_after.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Chart 1: District count before/after - {before_count} → {after_count}")

    # Chart 2: Match type distribution
    match_counts = df["match_type"].value_counts()

    plt.figure(figsize=(10, 6))
    colors = ['#2ECC71', '#3498DB', '#F39C12', '#E74C3C']
    bars = plt.bar(match_counts.index, match_counts.values, color=colors[:len(match_counts)], alpha=0.8)
    plt.title(f"{source_name.title()}: District Match Type Distribution", fontsize=14, fontweight='bold')
    plt.ylabel("Number of Records", fontsize=12)
    plt.xlabel("Match Type", fontsize=12)
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontweight='bold')
    plt.tight_layout()
    plt.savefig(dataset_charts_dir / "02_match_type_distribution.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Chart 2: Match type distribution")

    # Chart 3: Top unmatched districts
    unmatched = (
        df[df["match_type"] == "unmatched"]["district"]
        .value_counts()
        .head(10)
    )

    if not unmatched.empty:
        plt.figure(figsize=(12, 8))
        plt.barh(unmatched.index[::-1], unmatched.values[::-1], color='#E74C3C', alpha=0.8)
        plt.title(f"{source_name.title()}: Top 10 Unmatched District Names", fontsize=14, fontweight='bold')
        plt.xlabel("Frequency", fontsize=12)
        plt.tight_layout()
        plt.savefig(dataset_charts_dir / "03_top_unmatched_districts.png", dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✅ Chart 3: Top 10 unmatched districts")

    # Chart 4: State-wise unmatched count
    state_unmatched = (
        df[df["match_type"] == "unmatched"]
        .groupby("state")
        .size()
        .sort_values(ascending=False)
        .head(10)
    )

    if not state_unmatched.empty:
        plt.figure(figsize=(12, 8))
        plt.barh(state_unmatched.index[::-1], state_unmatched.values[::-1], color='#F39C12', alpha=0.8)
        plt.title(f"{source_name.title()}: Top States by Unmatched Districts", fontsize=14, fontweight='bold')
        plt.xlabel("Unmatched Count", fontsize=12)
        plt.tight_layout()
        plt.savefig(dataset_charts_dir / "04_state_unmatched.png", dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✅ Chart 4: Top states with unmatched districts")

    # Chart 5: State-wise before vs after district normalization
    state_before_after = df.groupby("state").apply(
        lambda x: pd.Series({
            "before": x["district"].nunique(),
            "after": x["district_final"].nunique()
        }),
        include_groups=False
    ).reset_index()

    state_before_after = state_before_after.sort_values("before", ascending=False).head(15)

    fig, ax = plt.subplots(figsize=(14, 8))
    x = range(len(state_before_after))
    width = 0.35

    ax.bar([i - width/2 for i in x], state_before_after["before"], width, label="Before Normalization", alpha=0.8, color='#FF6B6B')
    ax.bar([i + width/2 for i in x], state_before_after["after"], width, label="After Normalization", alpha=0.8, color='#4ECDC4')

    ax.set_xlabel("State", fontsize=12, fontweight='bold')
    ax.set_ylabel("Unique Districts Count", fontsize=12, fontweight='bold')
    ax.set_title(f"{source_name.title()}: State-wise Unique Districts - Before vs After Normalization", fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(state_before_after["state"], rotation=45, ha="right")
    ax.legend(fontsize=11)
    plt.tight_layout()
    plt.savefig(dataset_charts_dir / "05_state_before_after_normalization.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Chart 5: State-wise before/after normalization")

    # Save state data as CSV
    state_before_after.to_csv(dataset_charts_dir / "state_before_after_normalization.csv", index=False)
    print(f"✅ Data CSV: State-wise normalization data")
    
    # Summary statistics
    print(f"\n📊 Summary for {source_name}:")
    print(f"   Total Records: {len(df):,}")
    print(f"   Exact Matches: {(df['match_type']=='exact').sum():,}")
    print(f"   Renamed: {(df['match_type']=='renamed').sum():,}")
    print(f"   Fuzzy Matches: {(df['match_type']=='fuzzy').sum():,}")
    print(f"   Unmatched: {(df['match_type']=='unmatched').sum():,}")
    print(f"   Match Success Rate: {((len(df) - (df['match_type']=='unmatched').sum()) / len(df) * 100):.1f}%")


# Generate charts for all datasets
for dataset in DATASETS:
    generate_charts_for_dataset(dataset)

print(f"\n{'='*80}")
print("📊 All visualizations generated successfully!")
print(f"📁 Charts saved in → {CHART_OUTPUT_DIR}")
print(f"{'='*80}")
