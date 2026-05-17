"""Export mart tables to deliverables/1_csv_final (requires snowflake-connector-python, pyyaml)."""
from __future__ import annotations

import csv
from pathlib import Path

import yaml

try:
    import snowflake.connector
except ImportError as exc:
    raise SystemExit("pip install snowflake-connector-python pyyaml") from exc

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "deliverables" / "1_csv_final"
PROFILES = Path.home() / ".dbt" / "profiles.yml"


def load_profile() -> dict:
    with PROFILES.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["projet8_ocr"]["outputs"]["dev"]


def export_table(conn, fq_table: str, outfile: Path) -> int:
    cur = conn.cursor()
    cur.execute(f"select * from {fq_table}")
    rows = cur.fetchall()
    cols = [c[0] for c in cur.description]
    outfile.parent.mkdir(parents=True, exist_ok=True)
    with outfile.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        w.writerows(rows)
    return len(rows)


def main() -> None:
    p = load_profile()
    conn = snowflake.connector.connect(
        account=p["account"],
        user=p["user"],
        password=p["password"],
        database=p["database"],
        warehouse=p["warehouse"],
        schema=p["schema"],
        role=p.get("role"),
    )
    db = p["database"]
    n1 = export_table(
        conn,
        f"{db}.analytics_prod_analytics.mart_student_detail",
        OUT_DIR / "mart_student_detail.csv",
    )
    n2 = export_table(
        conn,
        f"{db}.analytics_prod_analytics.mart_demographic_evolution",
        OUT_DIR / "mart_demographic_evolution.csv",
    )
    print(f"Exported {n1} rows -> mart_student_detail.csv")
    print(f"Exported {n2} rows -> mart_demographic_evolution.csv")


if __name__ == "__main__":
    main()
