import os
import pandas as pd
from src.db import get_db_connection


def extract_orders_to_parquet():
    output_dir = os.path.join("data", "raw")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "orders.parquet")

    query = """
        SELECT 
            order_id,
            customer_id,
            store_id,
            total_amount,
            order_status,
            created_at,
            delivered_at
        FROM orders
        ORDER BY order_id;
    """

    conn = None
    try:
        conn = get_db_connection()
        print("Extracting orders from PostgreSQL...")

        # 1. Read query results into a pandas DataFrame
        df = pd.read_sql_query(query, conn)

        # 2. Write DataFrame to a compressed Parquet file using pyarrow
        df.to_parquet(output_path, engine="pyarrow", index=False)

        file_size_kb = os.path.getsize(output_path) / 1024
        print(f"Successfully extracted {len(df)} orders to {output_path}")
        print(f"File size: {file_size_kb:.2f} KB")

    except Exception as e:
        print(f"Error extracting orders: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    extract_orders_to_parquet()



