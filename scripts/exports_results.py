import snowflake.connector
import pandas as pd
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "exports"
OUTPUT_DIR.mkdir(exist_ok=True)

# ── Connection ─────────────────────────────────────────────────────────────
conn = snowflake.connector.connect(
    account="ARLHWOC-BM40687",
    user="YUKEL",
    password="OCRdbtYukel2026",
    database="PROJET8OCR",
    warehouse="COMPUTE_WH",
    role="ACCOUNTADMIN"
)

# ── Export ─────────────────────────────────────────────────────────────────
queries = {
    "mart_student_detail":        "SELECT * FROM PROJET8OCR.DBT_YUKEL_ANALYTICS.MART_STUDENT_DETAIL",
    "mart_demographic_evolution": "SELECT * FROM PROJET8OCR.DBT_YUKEL_ANALYTICS.MART_DEMOGRAPHIC_EVOLUTION",
    "mart_insee_context":         "SELECT * FROM PROJET8OCR.DBT_YUKEL_ANALYTICS.MART_INSEE_CONTEXT",
}

for name, sql in queries.items():
    df = pd.read_sql(sql, conn)
    out = OUTPUT_DIR / f"{name}.csv"
    df.to_csv(out, index=False, encoding="utf-8")
    print(f"Exported {len(df)} rows → {out}")

conn.close()
print("Done.")