import os
import time
import pandas as pd
from src.db import get_db_connection
from src.state import get_last_watermark, update_watermark

# Registry of tables to extract from PostgreSQL into Bronze Parquet files
# Registry of tables and extraction strategies
TABLE_CONFIGS = [
    {"table": "stores", "watermark_col": None, "pk": "store_id"},
    {"table": "products", "watermark_col": None, "pk": "product_id"},
    {"table": "customers", "watermark_col": None, "pk": "customer_id"},
    {"table": "orders", "watermark_col": "created_at", "pk": "order_id"},
    {"table": "order_items", "watermark_col": None, "pk": "order_item_id"},
]


def build_extract_query(
    table_name: str,
    watermark_col: str | None = None,
    watermark_val: str | None = None,
) -> str:
    """Constructs either an incremental delta query or a full snapshot query."""
    if watermark_col and watermark_val:
        return (
            f"SELECT * FROM {table_name} "
            f"WHERE {watermark_col} > '{watermark_val}' "
            f"ORDER BY {watermark_col} ASC;"
        )
    return f"SELECT * FROM {table_name};"


def extract_table_to_parquet(
    table_name: str,
    output_dir: str,
    conn,
    watermark_col: str | None = None,
    primary_key: str | None = None,
) -> dict:
    """Extracts a table (full or incremental) and saves it as a Parquet file."""
    start_time = time.time()
    output_path = os.path.join(output_dir, f"{table_name}.parquet")

    # 1. Fetch watermark if column is configured
    watermark_val = get_last_watermark(table_name) if watermark_col else None

    # 2. Build and execute query
    query = build_extract_query(table_name, watermark_col, watermark_val)
    df = pd.read_sql_query(query, conn)
    duration = round(time.time() - start_time, 2)

    # 3. Guard against overwriting existing Parquet file with an empty delta
    if len(df) == 0:
        file_size_kb = (
            round(os.path.getsize(output_path) / 1024, 2)
            if os.path.exists(output_path)
            else 0.0
        )
        return {
            "table": table_name,
            "rows": 0,
            "size_kb": file_size_kb,
            "duration_sec": duration,
            "path": output_path,
        }

    if os.path.exists(output_path) and watermark_val:
        existing_df = pd.read_parquet(output_path)
        combined_df = pd.concat([existing_df, df], ignore_index=True)
        if primary_key and primary_key in combined_df.columns:
            combined_df = combined_df.drop_duplicates(subset=[primary_key], keep="last")
        combined_df.to_parquet(output_path, engine="pyarrow", index=False)
    else:
        df.to_parquet(output_path, engine="pyarrow", index=False)
    # 5. Advance watermark in state file
    if watermark_col:
        new_watermark = str(df[watermark_col].max())
        update_watermark(table_name, watermark_col, new_watermark)

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
        for cfg in TABLE_CONFIGS:
            result = extract_table_to_parquet(
                table_name=cfg["table"],
                output_dir=output_dir,
                conn=conn,
                watermark_col=cfg["watermark_col"],
                primary_key=cfg["pk"],
            )
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