"""
03_run_sql.py: loads the prepared tables into SQLite and runs every query in sql/.
Results are saved to outputs/sql_results/<query_name>.csv
Run:  python src/03_run_sql.py   (after 01_prepare_data.py)
"""
from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "sql_results"
OUT.mkdir(parents=True, exist_ok=True)

con = sqlite3.connect(":memory:")
for name in ("orders_enriched", "items_enriched"):
    pd.read_csv(ROOT / "data" / "processed" / f"{name}.csv").to_sql(name, con, index=False)

for f in sorted((ROOT / "sql").glob("*.sql")):
    df = pd.read_sql_query(f.read_text(), con)
    df.to_csv(OUT / f"{f.stem}.csv", index=False)
    print(f"\n== {f.name}  ({len(df)} rows)")
    print(df.head(6).to_string(index=False))
con.close()
