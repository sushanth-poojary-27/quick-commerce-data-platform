import os
import time
import pandas as pd
from src.db import get_db_connection

# Registry of tables to extract from PostgreSQL into Bronze Parquet files
TABLES_TO_EXTRACT = [
    "stores",
    "products",
    "customers",
    "orders",
    "order_items",
]


def extract_table_to_parquet(table_name: str, output_dir: str, conn) -> dict:
    """Extracts a single table from PostgreSQL and saves it as a Parquet file."""
    start_time = time.time()
    output_path = os.path.join(output_dir, f"{table_name}.parquet")
    query = f"SELECT * FROM {table_name};"

    df = pd.read_sql_query(query, conn)
    df.to_parquet(output_path, engine="pyarrow", index=False)

    duration = round(time.time() - start_time, 2)
    file_size_kb = round(os.path.getsize(output_path) / 1024, 2)

    return {
        "table": table_name,
        "rows": len(df),
        "size_kb": file_size_kb,
        "duration_sec": duration,
        "path": output_path,
    }


def run_batch_extraction():
    """Iterates through all registered tables and runs the full extract pipeline."""
    output_dir = os.path.join("data", "raw")
    os.makedirs(output_dir, exist_ok=True)

    print("--- Starting Raw Layer Extraction (PostgreSQL -> Parquet) ---")

    conn = None
    try:
        conn = get_db_connection()
        print("Connected to PostgreSQL database.")

        summary = []
        for table in TABLES_TO_EXTRACT:
            result = extract_table_to_parquet(table, output_dir, conn)
            summary.append(result)
            print(
                f"[✓] Extracted '{result['table']}': "
                f"{result['rows']} rows | {result['size_kb']} KB | {result['duration_sec']}s"
            )

        print("\n--- Extraction Summary Table ---")
        summary_df = pd.DataFrame(summary)[["table", "rows", "size_kb", "duration_sec"]]
        print(summary_df.to_string(index=False))

    except Exception as e:
        print(f"[!] Extraction pipeline failed: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")


if __name__ == "__main__":
    run_batch_extraction()