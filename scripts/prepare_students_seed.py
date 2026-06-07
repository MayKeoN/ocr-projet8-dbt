import pandas as pd
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = ROOT / "data" / "DATASET_-_MAJ_-_P8_-_1040-_DA_-_DATA.csv"
SEED_FILE = ROOT / "seeds" / "students_raw.csv"

# ── Load ───────────────────────────────────────────────────────────────────
df = pd.read_csv(RAW_FILE, encoding="utf-8", sep=",")

# ── Normalise column names to match Snowflake source declaration ───────────
df.columns = [c.strip().upper() for c in df.columns]

# ── Basic sanity checks ────────────────────────────────────────────────────
expected = {"USER_ID", "PATH_CATEGORY_NAME", "AGE_GROUP", "GENDER", "REGION", "YEAR_PATH_STARTED"}
missing = expected - set(df.columns)
if missing:
    raise ValueError(f"Missing expected columns: {missing}")

print(f"Loaded {len(df)} rows, {df.columns.tolist()} columns")
print(f"GENDER nulls: {df['GENDER'].isna().sum()} ({df['GENDER'].isna().mean():.1%})")
print(f"Years present: {sorted(df['YEAR_PATH_STARTED'].dropna().unique().tolist())}")

# ── Write seed ─────────────────────────────────────────────────────────────
df.to_csv(SEED_FILE, index=False, encoding="utf-8")
print(f"Saved → {SEED_FILE}")