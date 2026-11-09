"""Load the generated CSVs into PostgreSQL (schema 'raw') exactly as they are: all text.

Re-running is safe: tables are truncated and refilled, never dropped, so dbt
views built on top of them keep working.
"""
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
load_dotenv(ROOT / ".env")

url = "postgresql+psycopg2://{u}:{p}@{h}:{port}/{db}".format(
    u=os.environ["POSTGRES_USER"], p=os.environ["POSTGRES_PASSWORD"],
    h=os.environ["POSTGRES_HOST"], port=os.environ["POSTGRES_PORT"], db=os.environ["POSTGRES_DB"],
)
engine = create_engine(url)

TABLES = ["customers", "materials", "installed_base", "change_requests", "ground_truth_defects"]


def main():
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw"))

    for table in TABLES:
        # only an empty cell is NULL; text like 'N/A' must stay as text (it is a defect we injected)
        df = pd.read_csv(DATA_DIR / f"{table}.csv", dtype=str, keep_default_na=False, na_values=[""])
        df["_loaded_at"] = pd.Timestamp.now(tz="UTC")
        df.head(0).to_sql(table, engine, schema="raw", if_exists="append", index=False)  # creates it if missing
        with engine.begin() as conn:
            conn.execute(text(f"TRUNCATE TABLE raw.{table}"))
        df.to_sql(table, engine, schema="raw", if_exists="append", index=False,
                  chunksize=2000, method="multi")
        print(f"Loaded raw.{table}")

    print("\nRow counts:")
    with engine.connect() as conn:
        for table in TABLES:
            n = conn.execute(text(f"SELECT count(*) FROM raw.{table}")).scalar()
            print(f"  raw.{table}: {n:,}")


if __name__ == "__main__":
    main()