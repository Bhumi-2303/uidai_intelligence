import os
from pathlib import Path
from typing import Optional, List

import pandas as pd
import matplotlib.pyplot as plt

try:
    import seaborn as sns
    _HAS_SEABORN = True
except Exception:
    _HAS_SEABORN = False


def _ensure_outdir(outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)


def _numeric_columns(df: pd.DataFrame) -> List[str]:
    return [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]


def univariate_analysis(df: pd.DataFrame, outdir: str, prefix: str = "univariate") -> None:
    """Generate summary stats and histograms for numeric columns.

    Saves CSV summaries and PNG histograms to `outdir`.
    """
    out = Path(outdir)
    _ensure_outdir(out)

    num_cols = _numeric_columns(df)
    if not num_cols:
        return

    # summary
    summary = df[num_cols].describe(percentiles=[0.25, 0.5, 0.75]).T
    summary.to_csv(out / f"{prefix}_summary.csv")

    # overall histograms
    for c in num_cols:
        plt.figure()
        df[c].dropna().hist(bins=40)
        plt.title(f"{prefix} - {c}")
        plt.xlabel(c)
        plt.ylabel("count")
        plt.tight_layout()
        plt.savefig(out / f"{prefix}_{c}_hist.png")
        plt.close()


def bivariate_analysis(dfs: List[pd.DataFrame], outdir: str, prefix: str = "bivariate") -> None:
    """Compute correlation heatmap across merged numeric features from provided dataframes.

    The function groups each df by `district` (if exists) and sums numeric columns, then merges
    on `district` to produce a single wide table for correlation.
    """
    out = Path(outdir)
    _ensure_outdir(out)

    agg_tables = []
    for i, df in enumerate(dfs):
        if df.empty:
            continue
        if "district" in df.columns:
            g = df.groupby("district").sum(numeric_only=True).add_prefix(f"d{i}_")
            # keep district as column
            g = g.reset_index().rename(columns={"district": "district"})
            agg_tables.append(g)
        else:
            g = df.sum(numeric_only=True).to_frame().T.add_prefix(f"d{i}_")
            g["district"] = "__all__"
            agg_tables.append(g)

    if not agg_tables:
        return

    # merge on district
    merged = agg_tables[0]
    for t in agg_tables[1:]:
        merged = merged.merge(t, on="district", how="outer")

    merged = merged.fillna(0)

    num_cols = _numeric_columns(merged.drop(columns=["district"]))
    if not num_cols:
        return

    corr = merged[num_cols].corr()
    corr.to_csv(out / f"{prefix}_corr.csv")

    plt.figure(figsize=(8, 6))
    if _HAS_SEABORN:
        sns.heatmap(corr, annot=True, fmt=".2f", cmap="vlag")
    else:
        plt.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
        plt.colorbar()
        plt.xticks(range(len(corr)), corr.columns, rotation=90)
        plt.yticks(range(len(corr)), corr.index)
    plt.title("Correlation Heatmap")
    plt.tight_layout()
    plt.savefig(out / f"{prefix}_heatmap.png")
    plt.close()


def trivariate_analysis(df: pd.DataFrame, x: str, y: str, hue: Optional[str], outdir: str, prefix: str = "trivariate") -> None:
    """Create a scatter plot of x vs y colored by hue (categorical) if provided.

    Saves PNG to `outdir`.
    """
    out = Path(outdir)
    _ensure_outdir(out)

    if x not in df.columns or y not in df.columns:
        return

    plt.figure(figsize=(6, 5))
    if hue and hue in df.columns and _HAS_SEABORN:
        sns.scatterplot(data=df, x=x, y=y, hue=hue, alpha=0.7)
    else:
        plt.scatter(df[x], df[y], alpha=0.6)
    plt.xlabel(x)
    plt.ylabel(y)
    plt.title(f"{prefix}: {x} vs {y}")
    plt.tight_layout()
    plt.savefig(out / f"{prefix}_{x}_vs_{y}.png")
    plt.close()


def generate_state_analysis(enrol: pd.DataFrame, demo: pd.DataFrame, bio: pd.DataFrame, state: str, outdir_root: str = "outputs/reports") -> None:
    """Top-level function to generate uni/bi/trivariate analyses for a given state.

    - Filters datasets to the state
    - Produces univariate summaries for each stream
    - Produces a bivariate correlation heatmap across aggregated district-level features
    - Produces example trivariate plots for top numeric features
    """
    state_upper = state.upper()
    out_root = Path(outdir_root) / state_lower(state)
    _ensure_outdir(out_root)

    e = enrol[enrol["state"].str.upper() == state_upper] if not enrol.empty else pd.DataFrame()
    d = demo[demo["state"].str.upper() == state_upper] if not demo.empty else pd.DataFrame()
    b = bio[bio["state"].str.upper() == state_upper] if not bio.empty else pd.DataFrame()

    # univariate per-stream
    univariate_analysis(e, str(out_root / "enrol_univariate"), prefix="enrol")
    univariate_analysis(d, str(out_root / "demo_univariate"), prefix="demo")
    univariate_analysis(b, str(out_root / "bio_univariate"), prefix="bio")

    # bivariate across merged district aggregates
    bivariate_analysis([e, d, b], str(out_root / "bivariate"), prefix="state_features")

    # trivariate examples: pick top numeric cols from merged aggregated table
    # Build merged aggregated table similar to bivariate_analysis
    agg_tables = []
    for i, df in enumerate([e, d, b]):
        if df.empty:
            continue
        if "district" in df.columns:
            g = df.groupby("district").sum(numeric_only=True).add_prefix(f"s{i}_")
            g = g.reset_index().rename(columns={"district": "district"})
            agg_tables.append(g)

    if agg_tables:
        merged = agg_tables[0]
        for t in agg_tables[1:]:
            merged = merged.merge(t, on="district", how="outer")
        merged = merged.fillna(0)
        num_cols = _numeric_columns(merged.drop(columns=["district"]))
        if len(num_cols) >= 2:
            x, y = num_cols[0], num_cols[1]
            hue = None
            if len(num_cols) >= 3:
                hue = num_cols[2]
            trivariate_analysis(merged, x, y, hue, str(out_root / "trivariate"), prefix="district_interaction")


def state_lower(s: str) -> str:
    return s.strip().lower().replace(" ", "_")
