## 1. OLTP vs. OLAP (PostgreSQL Protection)
- Running heavy analytics directly on PostgreSQL consumes CPU and memory, risking timeouts on live application traffic.
- Row-based storage requires reading entire rows from disk even when a query only needs a single column aggregation.

## 2. Intermediate Parquet Layer
- Staging data in Parquet files decouples analytical workloads from live database connections.
- Columnar storage and Snappy compression cut storage footprint and allow engines to read only queried columns.
- Enables query engines like DuckDB to run fast scans and predicate filtering directly on disk files.

## 3. Environment Isolation (`.venv` and `.gitignore`)
- A dedicated `.venv` isolates dependencies locally to avoid version conflicts with the host system.
- The `.gitignore` file keeps heavy binary Parquet extracts (`data/`), virtual environments, and secrets (`.env`) out of version control.

## 4. Entity Granularity (`orders` vs. `order_items`)
- `orders`: One row per customer checkout event (stores total amount, status, timestamps).
- `order_items`: One row per product line item within an order (stores SKU, quantity, unit price).

## 5. Relational Integrity & Deletion Policies
- Master tables (`customers`, `products`) avoid `ON DELETE CASCADE` to prevent accidental loss of historical transaction records.
- Soft deletes (`is_active = FALSE` or `deleted_at`) deactivate records in the application while keeping reporting data intact.

## 6. Watermark Indexing
- Incremental extraction relies on querying delta ranges (`WHERE created_at >= :watermark`).
- A B-Tree index on `created_at` replaces full table scans with fast range lookups as data volume grows.

## 7. Concurrent Key Retrieval (`RETURNING` vs. `MAX()`)
- `INSERT ... RETURNING order_id` returns the exact generated key for that specific transaction.
- `SELECT MAX(order_id)` introduces race conditions in concurrent pipelines where multiple inserts happen at once.

## 8. Transaction Atomicity
- Scoping `conn.commit()` after the entire batch ensures all-or-nothing execution.
- Catching exceptions with `conn.rollback()` purges partial writes so the database stays clean if an error occurs.

## 9. Source Financial Reconciliation
- Verifying `orders.total_amount = SUM(quantity * unit_price)` confirms that header totals match line-item totals before downstream processing.
- Catches calculation drift, missing items, or unhandled discounts at ingestion time.

## 10. Batch Extraction Engine (`src/extract.py`)
- Uses a table registry (`TABLES_TO_EXTRACT`) to handle multiple tables cleanly without duplicating extraction logic.
- Collects execution metrics (row count, file size, duration) to monitor ingestion health.

## 11. Bronze Quality Gates (DuckDB)
- Executes validation queries directly against Parquet files without spinning up a database server.
- Verifies primary key uniqueness (`COUNT(*) = COUNT(DISTINCT order_id)`).
- Verifies referential integrity (zero orphan `customer_id` or `store_id` references).
- Confirms revenue parity between `orders.parquet` and `order_items.parquet`.