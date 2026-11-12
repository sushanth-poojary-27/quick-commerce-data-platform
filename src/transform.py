"""
Silver Layer Transformation Engine.
Reads Bronze Parquet files from data/raw/, applies data cleansing,
type enforcement, and schema conformance using DuckDB, and saves
the output to data/silver/.
"""

import os
import time
import duckdb

RAW_DIR = os.path.join("data", "raw")
SILVER_DIR = os.path.join("data", "silver")


def get_duckdb_con() -> duckdb.DuckDBPyConnection:
    """Creates an in-memory DuckDB connection for transformations."""
    return duckdb.connect(database=":memory:")


def test_bronze_connectivity(con: duckdb.DuckDBPyConnection) -> dict:
    """Verifies DuckDB can directly query all Bronze Parquet files."""
    tables = ["stores", "products", "customers", "orders", "order_items"]
    counts = {}

    for table in tables:
        path = os.path.join(RAW_DIR, f"{table}.parquet").replace("\\", "/")
        query = f"SELECT count(*) FROM '{path}'"
        counts[table] = con.execute(query).fetchone()[0]

    return counts


if __name__ == "__main__":
    os.makedirs(SILVER_DIR, exist_ok=True)
    con = get_duckdb_con()

    print("--- Verifying Bronze Layer for Silver Transformation ---")
    bronze_counts = test_bronze_connectivity(con)
    for table, count in bronze_counts.items():
        print(f"[✓] Bronze '{table}': {count} records accessible")
    print("---------------------------------------------------------")