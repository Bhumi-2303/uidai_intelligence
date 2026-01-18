from fastapi import APIRouter, HTTPException
import pandas as pd
from pathlib import Path

router = APIRouter()

# Data Loading Cache
# In a production app, we might use a proper database or a more robust caching mechanism.
DATA_CACHE = {}

def get_data(filename: str):
    if filename not in DATA_CACHE:
        # Assuming run from root of repo
        base_path = Path.cwd()
        # Fallback logic if running from inside backend
        if not (base_path / "outputs").exists():
             base_path = base_path.parent
        
        file_path = base_path / "outputs" / "dashboard" / filename
        if not file_path.exists():
             # Try other path structure from app.py vs dashboards/app.py
             file_path = base_path / "outputs" / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"Data file {filename} not found at {file_path}")
            
        DATA_CACHE[filename] = pd.read_csv(file_path)
    return DATA_CACHE[filename]

@router.get("/dashboard-data")
def get_dashboard_data():
    """Returns the main dashboard data."""
    try:
        df = get_data("dashboard_data.csv")
        # Convert NaN to None for JSON compatibility
        return df.where(pd.notnull(df), None).to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/states")
def get_states():
    """Returns list of available states."""
    try:
        df = get_data("dashboard_data.csv")
        states = sorted(df["state"].unique().tolist())
        return ["All"] + states
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/districts/{state}")
def get_districts(state: str):
    """Returns data filtered by state."""
    try:
        df = get_data("dashboard_data.csv")
        if state != "All":
            df = df[df["state"] == state]
        return df.where(pd.notnull(df), None).to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
