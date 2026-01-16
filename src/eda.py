import matplotlib.pyplot as plt
from pathlib import Path


def before_after_district_count(before_df, after_df, state):
    """
    State-wise district count before vs after normalization
    """
    state = state.upper()

    b = before_df[before_df["state"].str.upper() == state]
    a = after_df[after_df["state"].str.upper() == state]

    before_count = b["district"].nunique()
    after_count  = a["district_clean"].nunique()

    import matplotlib.pyplot as plt
    from pathlib import Path

    plt.figure()
    plt.bar(["Before", "After"], [before_count, after_count])
    plt.ylabel("Number of Districts")
    plt.title(f"{state.title()} District Count: Before vs After")

    out = Path("outputs/reports")
    out.mkdir(parents=True, exist_ok=True)
    plt.savefig(out / f"{state.lower()}_district_count_before_after.png")
    plt.close()



def invalid_districts_chart(df):
    """
    Bar chart: most frequent invalid district names
    """
    invalid = df[~df["is_valid_district"]]
    counts = invalid["district"].value_counts().head(10)

    if counts.empty:
        return

    plt.figure(figsize=(8, 4))
    counts.plot(kind="bar")
    plt.title("Top Invalid District Names (Before Cleaning)")
    plt.ylabel("Frequency")
    plt.tight_layout()

    out = Path("outputs/reports")
    out.mkdir(parents=True, exist_ok=True)
    plt.savefig(out / "invalid_districts.png")
    plt.close()
