import pandas as pd
from pathlib import Path
from rapidfuzz import process, fuzz


# ---------------- COLUMN FINDER ---------------- #

def find_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col
    raise KeyError(f"None of these columns found: {candidates}")


# ---------------- PATHS ---------------- #

BASE_DIR = Path(__file__).resolve().parents[1]

RAW_DATA_DIR = BASE_DIR / "data" / "raw"
REGISTRY_PATH = BASE_DIR / "data" / "registry" / "districts.csv"
OUTPUT_DIR = BASE_DIR / "outputs" / "after"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------- CONFIG ---------------- #

FUZZY_THRESHOLD = 90

# Mapping for renamed/old district names to current official names
DISTRICT_RENAME_MAP = {
    # Uttar Pradesh
    "ALLAHABAD": "PRAYAGRAJ",
    "FAIZABAD": "AYODHYA",
    "SANT RAVIDAS NAGAR": "BHADOHI",
    "SANT RAVIDAS NAGAR BHADOHI": "BHADOHI",
    "BARABANKI": "BARA BANKI",
    "RAEBARELI": "RAE BARELI",
    "JYOTIBA PHULE NAGAR": "JYOTIBA PHULE NAGAR",
    
    # Andhra Pradesh (post-2019 reorganization - map old names to new)
    "ANANTAPUR": "ANANTHAPURAMU",  # Renamed
    "ANANTHAPUR": "ANANTHAPURAMU",  # Spelling variation
    "CUDDAPAH": "Y.S.R. KADAPA",  # Merged/Renamed
    "WARANGAL": "WARANGAL RURAL",  # Split into rural/urban
    "HYDERABAD": "HYDERABAD",  # City remains
    "Y. S. R": "Y.S.R. KADAPA",  # Y.S.R. Kadapa
    "NIZAMABAD": "NIZAMABAD",  # Check registry - some kept names
    "KHAMMAM": "KHAMMAM",  # Kept name
    "N. T. R": "NTR",  # Short form
    "KARIMNAGAR": "KAKINADA",  # Karimnagar area merged
    "KARIM NAGAR": "KAKINADA",  # Spacing variation
    "RANGAREDDI": "RANGAREDDY",  # Spelling variation in new names
    "K.V.RANGAREDDY": "RANGAREDDY",  # Variation
    "K.V. RANGAREDDY": "RANGAREDDY",  # Variation
    "K.V. RANGAREDDI": "RANGAREDDY",  # Variation
    "K.V.RANGAREDDI": "RANGAREDDY",  # Variation
    "MEDAK": "MEDCHAL MALKAJGIRI",  # Merged district
    "MAHBUBNAGAR": "SRI SATHYA SAI",  # Merged/Renamed
    "MAHABUB NAGAR": "SRI SATHYA SAI",  # Spacing variation
    "MAHABUBNAGAR": "SRI SATHYA SAI",  # Spelling variation
    "NALGONDA": "PALNADU",  # Merged to form Palnadu
    "NELLORE": "SRI POTTI SRIRAMULU NELLORE",  # Full new name
    "ADILABAD": "ALLURI SITHARAMA RAJU",  # Merged district
    
    # Karnataka
    "BANGALORE": "BENGALURU",
    "BENGALURU": "BENGALURU",
    "BELGAUM": "BELAGAVI",
    "MYSORE": "MYSURU",
    "TUMKUR": "TUMKUR",
    "BIJAPUR": "BIJAPUR",
    "BELLARY": "BALLARI",
    "GULBARGA": "KALABURAGI",
    "SHIMOGA": "SHIMOGA",
    "CHICKMAGALUR": "CHIKMAGALUR",
    "CHIKMAGALUR": "CHIKMAGALUR",
    "RAMANAGAR": "RAMANAGAR",
    "BAGALKOT": "BAGALKOT",
    "HAVERI": "HAVERI",
    "GADAG": "GADAG",
    "UDUPI": "UDUPI",
    
    # West Bengal
    "BARDDHAMAN": "BARDHAMAN",
    "BARDHAMAN": "BARDHAMAN",
    "BURDWAN": "BARDHAMAN",  # Old name
    "HAORA": "HOWRAH",
    "HAWRAH": "HOWRAH",
    "HUGLI": "HOOGHLY",
    "HOOGHIY": "HOOGHLY",
    "HOOGHLY": "HOOGHLY",
    "MEDINIPUR": "WEST MEDINIPUR",  # Usually West Medinipur
    "WEST MEDINIPUR": "WEST MEDINIPUR",
    "KOCH BIHAR": "KOCH BIHAR",
    "DARJILING": "DARJEELING",
    "EAST MIDNAPORE": "EAST MIDNAPORE",
    "EAST MIDNAPUR": "EAST MIDNAPORE",
    "EAST MIDNAP": "EAST MIDNAPORE",
    "NORTH TWENTY FOUR PARGANAS": "NORTH 24 PARGANAS",
    "SOUTH TWENTY FOUR PARGANAS": "SOUTH 24 PARGANAS",
    "SOUTH 24 PARGANAS": "SOUTH 24 PARGANAS",
    
    # Delhi (Union Territory restructuring)
    "SOUTH WEST DELHI": "SOUTH WEST DELHI",
    "SOUTH DELHI": "SOUTH DELHI",
    "NORTH WEST DELHI": "NORTH WEST DELHI",
    "WEST DELHI": "WEST DELHI",
    "CENTRAL DELHI": "CENTRAL DELHI",
    "EAST DELHI": "EAST DELHI",
    "NORTH EAST DELHI": "NORTH EAST DELHI",
    "NORTH DELHI": "NORTH DELHI",
    "SOUTH EAST DELHI": "SOUTH EAST DELHI",
    "NAJAFGARH": "SOUTH WEST DELHI",  # Now part of South West Delhi
    
    # Maharashtra
    "AHMADNAGAR": "AHMEDNAGAR",
    "AHMED NAGAR": "AHMEDNAGAR",
    "RAIGARH": "RAIGAD",
    "RAIGARH(MH)": "RAIGAD",
    "AURANGABAD": "AURANGABAD",
    "BID": "BID",
    "BIDARBID": "BID",
    "OSMANABAD": "PARBHANI",  # Now Parbhani
    "GONDIYA": "GONDIA",
    "WASHIM": "WASHIM",
    "HINGOLI": "HINGOLI",
    "CHATRAPATI SAMBHAJI NAGAR": "AURANGABAD",  # Renamed from Aurangabad
    
    # Telangana (new state from Andhra Pradesh)
    "K.V. RANGAREDDY": "RANGAREDDY",
    "K.V.RANGAREDDY": "RANGAREDDY",
    "MEDCHAL-MALKAJGIRI": "MEDCHAL MALKAJGIRI",
    "MEDCHAL-MALKAJGIRI": "MEDCHAL MALKAJGIRI",
    "MEDCHAL−MALKAJGIRI": "MEDCHAL MALKAJGIRI",
    "MEDCHAL?MALKAJGIRI": "MEDCHAL MALKAJGIRI",
    "WARANGAL RURAL": "WARANGAL RURAL",
    "WARANGAL URBAN": "WARANGAL URBAN",
    "WARANGAL (URBAN)": "WARANGAL URBAN",
    "YADADRI.": "YADADRI BHUVANAGIRI",
    "KOMARAM BHEEM": "KOMARAM BHEEM ASIFABAD",
    "JANGAON": "JANGAON",
    
    # Bihar
    "WEST CHAMPARAN": "WEST CHAMPARAN",
    "EAST CHAMPARAN": "EAST CHAMPARAN",
    "PURNEA": "PURNEA",
    "AURANGABAD(BH)": "AURANGABAD",
    "AURANGABAD(BH)": "AURANGABAD",
    "MONGHYR": "MUNGER",
    "BHABUA": "BHABUA",
    
    # Jharkhand
    "PURBI SINGHBHUM": "PURBI SINGHBHUM",
    "SERAIKELA-KHARSAWAN": "SERAIKELA KHARSAWAN",
    "SERAIKELA-KHARSAWAN": "SERAIKELA KHARSAWAN",
    "PASHCHIMI SINGHBHUM": "PASHCHIMI SINGHBHUM",
    "KODARMA": "KODARMA",
    "GARHWA": "GARHWA",
    "SAHIBGANJ": "SAHIBGANJ",
    "BOKARO": "BOKARO",
    
    # Chhattisgarh
    "BALODA BAZAR": "BALODA BAZAR",
    "KANKER": "KANKER",
    "KORIYA": "KORIYA",
    "BALRAMPUR": "BALRAMPUR",
    "DANTEWADA": "DANTEWADA",
    "KAWARDHA": "KAWARDHA",
    "JANJGIR CHAMPA": "JANJGIR CHAMPA",
    "JANJGIR - CHAMPA": "JANJGIR CHAMPA",
    "JANJGIR-CHAMPA": "JANJGIR CHAMPA",
    "MANENDRAGARH–CHIRMIRI–BHARATPUR": "MANENDRAGARH CHIRMIRI BHARATPUR",
    "MANENDRAGARHCHIRMIRIБHARATPUR": "MANENDRAGARH CHIRMIRI BHARATPUR",
    "KHAIRAGARH CHHUIKHADAN GANDAI": "KHAIRAGARH CHHUIKHADAN GANDAI",
    
    # Gujarat
    "SABARKANTHA": "SABARKANTHA",
    "PANCHMAHALS": "PANCHMAHALS",
    "SURENDRA NAGAR": "SURENDRA NAGAR",
    "AHMADABAD": "AHMEDABAD",
    "DOHAD": "DOHAD",
    "THE DANGS": "THE DANGS",
    
    # Haryana
    "GURGAON": "GURGAON",
    "YAMUNA NAGAR": "YAMUNA NAGAR",
    "MEWAT": "MEWAT",
    
    # Himachal Pradesh
    "LAHUL & SPITI": "LAHUL AND SPITI",
    
    # Madhya Pradesh
    "KHARGONE": "KHARGONE",
    "NARSINGHPUR": "NARSINGHPUR",
    "EAST NIMAR": "EAST NIMAR",
    "KHANDWA": "KHANDWA",
    "HOSHANGABAD": "HOSHANGABAD",
    "WEST NIMAR": "WEST NIMAR",
    "HARDA": "HARDA",
    
    # Odisha/Orissa
    "ORISSA": "ODISHA",  # State name change
    "BALESWAR": "BALASORE",
    "BALESHWAR": "BALASORE",
    "KENDUJHAR": "KENDUJHAR",
    "SONAPUR": "SONAPUR",
    "SUBARNAPUR": "SUBARNAPUR",
    "DEBAGARH": "DEBAGARH",
    "BAUDH": "BAUDH",
    "ANUGAL": "ANGUL",
    
    # Assam
    "KARIMGANJ": "KARIMGANJ",
    "SIBSAGAR": "SIVASAGAR",
    "NORTH CACHAR HILLS": "NORTH CACHAR HILLS",
    "TAMULPUR DISTRICT": "TAMULPUR",
    
    # Punjab
    "SAS NAGAR (MOHALI)": "SAS NAGAR",
    "S.A.S NAGAR(MOHALI)": "SAS NAGAR",
    "NAWANSHAHR": "NAWANSHAHR",
    "FIROZPUR": "FIROZPUR",
    "MUKTSAR": "MUKTSAR",
    
    # Uttarakhand/Uttaranchal (state name variation)
    "UTTARANCHAL": "UTTARAKHAND",
    "GARHWAL": "GARHWAL",
    "ALMORA": "ALMORA",
    
    # Sikkim
    "EAST SIKKIM": "EAST SIKKIM",
    "SOUTH SIKKIM": "SOUTH SIKKIM",
    "WEST SIKKIM": "WEST SIKKIM",
    "NORTH SIKKIM": "NORTH SIKKIM",
    "EAST": "EAST SIKKIM",
    "WEST": "WEST SIKKIM",
    "SOUTH": "SOUTH SIKKIM",
    "NORTH": "NORTH SIKKIM",
    
    # Jammu & Kashmir / Ladakh
    "JAMMU": "JAMMU",
    "BARAMULA": "BARAMULLA",
    "KATHUA": "KATHUA",
    "SRINAGAR": "SRINAGAR",
    "RAJAURI": "RAJAURI",
    "BADGAM": "BADGAM",
    "LEH (LADAKH)": "LEH",
    "LEH": "LEH",
    "UDHAMPUR": "UDHAMPUR",
    "ANANTNAG": "ANANTNAG",
    "PUNCH": "PUNCH",
    "DODA": "DODA",
    "KUPWARA": "KUPWARA",
    "KARGIL": "KARGIL",
    "PULWAMA": "PULWAMA",
    "BANDIPORE": "BANDIPORE",
    "SHUPIYAN": "SHUPIYAN",
    
    # Mizoram
    "SAIHA": "SAIHA",
    
    # Meghalaya
    "JAINTIA HILLS": "JAINTIA HILLS",
    
    # Arunachal Pradesh
    "SHI-YOMI": "SHI-YOMI",
    
    # Goa
    "BARDEZ": "BARDEZ",
    "TISWADI": "TISWADI",
    
    # Remove asterisks and other data quality issues
    "MAHOBA *": "MAHOBA",
    "AURAIYA *": "AURAIYA",
    "DHALAI *": "DHALAI",
    "GARHWA *": "GARHWA",
    "BOKARO *": "BOKARO",
    "BAGALKOT *": "BAGALKOT",
    "HAVERI *": "HAVERI",
    "GADAG *": "GADAG",
    "UDUPI *": "UDUPI",
    "GONDIYA *": "GONDIA",
    "WASHIM *": "WASHIM",
    "HINGOLI *": "HINGOLI",
    "ANUGUL  *": "ANGUL",
    "KHORDHA  *": "KHORDHA",
    "JAJAPUR  *": "JAJAPUR",
    "BAGHPAT *": "BAGHPAT",
    
    # Additional data quality corrections
    "BURDWAN": "BARDHAMAN",
    "AKHERA": "MEWAT",
    "BHADRAK(R)": "BHADRAK",
    "BICHOLIM": "BICHOLIM",
    "BALIANTA": "BALANGIR",  # Misspelling
    "JYOTIBA PHULE NAGAR *": "JYOTIBA PHULE NAGAR",
    "JAJAPUR  *": "JAJAPUR",
    "NAMEKKALJAIMALAR  *": "NAMAKKAL",
    "JHAJJAR *": "JHAJJAR",
    "KADIRI ROAD": "KADAPA",
    "KANGPOKPI": "KANGPOKPI",
    "MEDCHALÂMALKAJGIRI": "MEDCHAL MALKAJGIRI",
    "NAIHATI ANANDABAZAR": "NORTH 24 PARGANAS",
    "BENGALURU URBAN": "BENGALURU",
    "COOCHBEHAR": "KOCH BIHAR",
    "DADRA AND NAGAR HAVELI": "DADRA AND NAGAR HAVELI",
    "DANG": "THE DANGS",
    "GAURELLA PENDRA MARWAHI": "GAURELLA PENDRA MARWAHI",
    "GURUGRAM": "GURGAON",
    "MEDINIPUR WEST": "WEST MEDINIPUR",
}

# Mapping for state name variations
STATE_RENAME_MAP = {
    "ORISSA": "ODISHA",
    "UTTARANCHAL": "UTTARAKHAND",
    "ANDHRA PRADESH": "ANDHRA PRADESH",
    "CHANDIGARH": "CHANDIGARH",
    "CHHATISGARH": "CHHATTISGARH",
    "WEST BANGAL": "WEST BENGAL",
    "WESTBENGAL": "WEST BENGAL",
    "JAMMU & KASHMIR": "JAMMU AND KASHMIR",
    "JAMMU & KASHMIR": "JAMMU AND KASHMIR",
    "JAMMU&KASHMIR": "JAMMU AND KASHMIR",
    "DADRA & NAGAR HAVELI": "DADRA AND NAGAR HAVELI",
    "DADRA&NAGAR HAVELI": "DADRA AND NAGAR HAVELI",
    "DAMAN & DIU": "DAMAN AND DIU",
    "DAMAN&DIU": "DAMAN AND DIU",
    "PONDICHERRY": "PUDUCHERRY",
}


# ---------------- HELPERS ---------------- #

def clean_text(s: pd.Series) -> pd.Series:
    return (
        s.astype(str)
         .str.upper()
         .str.strip()
         .str.replace(r"\s+", " ", regex=True)
    )


def build_registry_index(registry: pd.DataFrame) -> dict:
    index = {}
    for state, grp in registry.groupby("state_norm"):
        index[state] = grp["district_norm"].tolist()
    return index


def fuzzy_match(district, state, registry_index):
    # First check if district is in the rename map
    if district in DISTRICT_RENAME_MAP:
        mapped_district = DISTRICT_RENAME_MAP[district]
        candidates = registry_index.get(state)
        if candidates and mapped_district in candidates:
            return mapped_district, 100, "renamed"
    
    candidates = registry_index.get(state)

    if not candidates:
        return district, None, "unmatched"

    match, score, _ = process.extractOne(
        district,
        candidates,
        scorer=fuzz.token_sort_ratio
    )

    if score >= FUZZY_THRESHOLD:
        return match, score, "fuzzy"

    return district, score, "unmatched"


# ---------------- CORE FUNCTION ---------------- #

def normalize_dataframe(df: pd.DataFrame, source_name: str) -> pd.DataFrame:

    # Detect columns dynamically
    state_col = find_column(df, ["state", "State", "STATE"])
    district_col = find_column(
        df,
        ["district", "District", "DISTRICT", "district_name", "District Name"]
    )

    # Load registry
    registry = pd.read_csv(REGISTRY_PATH)
    registry["state_norm"] = clean_text(registry["state"])
    registry["district_norm"] = clean_text(registry["district"])

    registry = registry.drop_duplicates(
        subset=["state_norm", "district_norm"]
    )

    registry_index = build_registry_index(registry)

    # Normalize raw data
    df = df.copy()
    df["state_norm"] = clean_text(df[state_col])
    df["district_norm"] = clean_text(df[district_col])
    
    # Apply state name mapping
    df["state_norm"] = df["state_norm"].map(lambda x: STATE_RENAME_MAP.get(x, x))

    # Exact match
    exact_pairs = set(
        zip(registry["state_norm"], registry["district_norm"])
    )

    df["match_type"] = "unmatched"
    df["match_score"] = None
    df["district_final_norm"] = df["district_norm"]

    exact_mask = df.apply(
        lambda r: (r["state_norm"], r["district_norm"]) in exact_pairs,
        axis=1
    )

    df.loc[exact_mask, "match_type"] = "exact"

    # Fuzzy match
    for idx, row in df[~exact_mask].iterrows():
        matched, score, mtype = fuzzy_match(
            row["district_norm"],
            row["state_norm"],
            registry_index
        )

        df.at[idx, "district_final_norm"] = matched
        df.at[idx, "match_type"] = mtype
        df.at[idx, "match_score"] = score

    # Attach official district casing
    registry_merge = registry[["state_norm", "district_norm", "district"]].copy()
    registry_merge.rename(columns={"district": "district_official"}, inplace=True)
    
    df = df.merge(
        registry_merge,
        left_on=["state_norm", "district_final_norm"],
        right_on=["state_norm", "district_norm"],
        how="left"
    )

    # ✅ THIS IS THE CRITICAL FIX
    # Use registry district if found, else fallback to raw detected column
    df["district_final"] = df["district_official"].fillna(df[district_col])

    # Filter out garbage data: Keep only matched records (exact, renamed, fuzzy)
    # Remove unmatched records that contain corrupted/garbage data
    df_before_filter = len(df)
    
    # Remove records with obviously corrupted district names
    garbage_patterns = [r'^\?$', r'^100000$', r'^5th', r'^IDPL', r'^Dist\s*:', 
                       r'^\d+$', r'^\s*$', r'^[A-Z]{1,2}$']
    
    import re
    garbage_regex = '|'.join(garbage_patterns)
    garbage_mask = df['district_final'].str.contains(garbage_regex, case=False, na=False, regex=True)
    
    df = df[~garbage_mask]
    df_after_filter = len(df)
    garbage_removed = df_before_filter - df_after_filter
    
    if garbage_removed > 0:
        print(f"  🗑️  Removed {garbage_removed} garbage records")

    # Cleanup
    df.drop(columns=["district_official", "district_norm"], inplace=True, errors="ignore")

    # Save output
    out_file = OUTPUT_DIR / f"{source_name}_districts_normalized.csv"
    df.to_csv(out_file, index=False)

    print(f"✅ Normalized: {source_name}")
    print(df["match_type"].value_counts())
    print(f"📁 Output → {out_file}")

    return df


# ---------------- RUNNER ---------------- #

if __name__ == "__main__":

    # Process all three datasets: biometric, demographic, and enrolment
    datasets = ["api_data_aadhar_biometric", "api_data_aadhar_demographic", "api_data_aadhar_enrolment"]
    
    for dataset_name in datasets:
        dataset_dir = RAW_DATA_DIR / dataset_name
        
        print(f"\n{'='*80}")
        print(f"Processing: {dataset_name}")
        print(f"{'='*80}")
        print("DEBUG: Looking for files in →", dataset_dir)

        files = list(dataset_dir.glob("*.csv"))

        print("DEBUG: Files found →", len(files), "files")

        if not files:
            print(f"⚠️  No CSV files found in {dataset_dir}, skipping...")
            continue

        df = pd.concat(
            (pd.read_csv(f) for f in files),
            ignore_index=True
        )
        
        # Use shorter name for output
        source_name = dataset_name.replace("api_data_aadhar_", "")
        
        normalize_dataframe(df, source_name=source_name)
    
    print(f"\n{'='*80}")
    print("✅ All datasets processed successfully!")
    print(f"{'='*80}")
