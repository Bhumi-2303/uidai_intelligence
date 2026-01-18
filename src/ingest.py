import pandas as pd
from pathlib import Path
from typing import Optional, Tuple, List, Dict


def _safe_parse_date(series: pd.Series) -> Tuple[pd.Series, List[str]]:
    issues = []
    try:
        parsed = pd.to_datetime(series, dayfirst=True, errors="coerce")
        bad = parsed.isna() & series.notna()
        if bad.any():
            issues.append(f"{bad.sum()} unparsable dates")
        return parsed, issues
    except Exception as e:
        return pd.Series(pd.NaT, index=series.index), [str(e)]


def _validate_df(df: pd.DataFrame, name: str) -> Tuple[pd.DataFrame, List[Dict]]:
    """Basic validation: required cols, date parsing, numeric age coercion.

    Returns cleaned df and a list of issue dicts.
    """
    issues = []
    df = df.copy()

    required = ["date", "state", "district"]
    for col in required:
        if col not in df.columns:
            issues.append({"file": name, "issue": f"missing_column:{col}", "rows": None})

    # parse date
    if "date" in df.columns:
        parsed, date_issues = _safe_parse_date(df["date"])
        df["date"] = parsed
        for it in date_issues:
            issues.append({"file": name, "issue": f"date_parse:{it}", "rows": None})

    # coerce age-like columns to numeric
    age_cols = [c for c in df.columns if "age" in c.lower()]
    for c in age_cols:
        before_nonnum = df[c].dtype == object and df[c].str.isnumeric().value_counts().get(False, 0)
        df[c] = pd.to_numeric(df[c], errors="coerce")
        nulls = df[c].isna().sum()
        if nulls:
            issues.append({"file": name, "issue": f"non_numeric_age:{c}", "rows": int(nulls)})

    # trim whitespace
    for c in ["state", "district"]:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()

    return df, issues


def load_uidai_data(state: Optional[str] = None,
                    start_date: Optional[str] = None,
                    end_date: Optional[str] = None,
                    paths: Optional[Dict[str, str]] = None) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load enrol, demo, bio datasets with validation and optional filtering.

    Args:
        state: optional state name to filter (case-insensitive)
        start_date/end_date: optional date strings (YYYY-MM-DD or dd-mm-YYYY)
        paths: optional dict with keys 'enrol','demo','bio' for custom file paths

    Returns (enrol, demo, bio)
    """
    if paths is None:
        paths = {
            "enrol": "data/raw/enrol.csv",
            "demo": "data/raw/demo_update.csv",
            "bio": "data/raw/bio_update.csv",
        }

    # If single-file paths don't exist, try to find CSVs in raw API folders
    from glob import glob
    base = Path("data/raw")
    if not Path(paths["enrol"]).exists():
        candidates = sorted(glob(str(base / "api_data_aadhar_enrolment" / "*.csv")))
        if candidates:
            paths["enrol"] = candidates
    if not Path(paths["demo"]).exists():
        candidates = sorted(glob(str(base / "api_data_aadhar_demographic" / "*.csv")))
        if candidates:
            paths["demo"] = candidates
    if not Path(paths["bio"]).exists():
        candidates = sorted(glob(str(base / "api_data_aadhar_biometric" / "*.csv")))
        if candidates:
            paths["bio"] = candidates
    out_issues = []
    dfs = {}
    for key in ["enrol", "demo", "bio"]:
        p = paths[key]
        # allow a list of files (concatenate) or single path
        if isinstance(p, list):
            frames = []
            for fp in p:
                fp = Path(fp)
                if not fp.exists():
                    continue
                try:
                    frames.append(pd.read_csv(fp))
                except Exception as e:
                    out_issues.append({"file": key, "issue": f"read_error:{fp}:{e}", "rows": None})
            if frames:
                df = pd.concat(frames, ignore_index=True)
            else:
                out_issues.append({"file": key, "issue": "missing_file", "rows": None})
                dfs[key] = pd.DataFrame()
                continue
        else:
            fp = Path(p)
            if not fp.exists():
                out_issues.append({"file": key, "issue": "missing_file", "rows": None})
                dfs[key] = pd.DataFrame()
                continue
            try:
                df = pd.read_csv(fp)
            except Exception as e:
                out_issues.append({"file": key, "issue": f"read_error:{e}", "rows": None})
                dfs[key] = pd.DataFrame()
                continue

        df, issues = _validate_df(df, key)
        out_issues.extend(issues)

        # optional filtering
        if state and "state" in df.columns:
            df = df[df["state"].str.upper() == state.upper()]

        if start_date:
            sd = pd.to_datetime(start_date, dayfirst=True, errors="coerce")
            if sd is not pd.NaT and "date" in df.columns:
                df = df[df["date"] >= sd]

        if end_date:
            ed = pd.to_datetime(end_date, dayfirst=True, errors="coerce")
            if ed is not pd.NaT and "date" in df.columns:
                df = df[df["date"] <= ed]

        dfs[key] = df

    # save issues
    out = Path("outputs/reports")
    out.mkdir(parents=True, exist_ok=True)
    if out_issues:
        issues_df = pd.DataFrame(out_issues)
        issues_df.to_csv(out / "ingest_issues.csv", index=False)

    return dfs.get("enrol", pd.DataFrame()), dfs.get("demo", pd.DataFrame()), dfs.get("bio", pd.DataFrame())

