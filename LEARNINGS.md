#### 1. OLTP Workload Protection (PostgreSQL)
- **Application Latency**: OLTP databases are optimized for low-latency, single-row reads and writes; heavy analytical queries monopolize CPU and memory, causing application connection timeouts and API degradation.
- **I/O Efficiency**: PostgreSQL uses row-oriented storage (`heap` files), reading entire rows from disk sequentially even when an analytical query requires only a single column aggregation.
- **Blast Radius Isolation**: Isolating analytical execution from the primary database ensures ad-hoc exploratory queries and large table scans cannot degrade or lock live customer-facing services.

#### 2. Intermediate Parquet Storage Layer
- **Decoupled Architecture**: Staging extracted data as immutable Parquet snapshots removes persistent connection load and long-lived transactions from the operational database.
- **Columnar Compression**: Column-oriented binary encoding reduces storage footprint by 70–90% using Snappy compression and allows downstream engines to read only requested columns from disk.
- **Vectorized Querying**: Provides an optimal storage substrate for analytical engines like DuckDB, enabling direct metadata inspection, predicate pushdown, and partition pruning without data ingestion.

#### 3. Environment Isolation (`.venv` and `.gitignore`)
- **Dependency Isolation (`.venv`)**: Scopes project packages locally to prevent version conflicts with system-level Python runtimes and ensure deterministic builds across environments.
- **Repository Hygiene (`.gitignore`)**: Prevents tracking transient development artifacts, including compiled virtual environments, large binary Parquet files (`data/`), and environment secrets (`.env`).

#### 4. Entity Granularity (`orders` vs. `order_items`)
- **Transaction Grain (`orders`)**: Represents a single checkout event executed by a customer at a specific point in time, storing header-level attributes such as payment total, fulfillment status, and order timestamps.
- **Line-Item Grain (`order_items`)**: Represents a specific product SKU and quantity associated with an order, linking individual catalog items to parent transactions for basket-level analysis.

#### 5. Relational Integrity and Deletion Policies
- **Audit Trail Preservation**: Master tables (`customers`, `products`) omit `ON DELETE CASCADE` to prevent the accidental deletion of a parent record from recursively destroying historical financial and operational logs.
- **Soft Delete Implementation**: Flags like `is_active = FALSE` or `deleted_at` timestamps deprecate entities within application logic while maintaining referential integrity for downstream financial reporting and lineage.

#### 6. Watermark Indexing for Incremental Extraction
- **Index Optimization**: A B-Tree index on the watermark column (`created_at`) enables log-time lookups for incremental extraction queries filtering on high-watermark ranges (`WHERE created_at >= :watermark`).
- **Sequential Scan Elimination**: Prevents the database engine from executing full-table disk scans across millions of static historical rows, keeping extraction query latency uniform as datasets grow.

#### 7. Concurrent Key Retrieval (`RETURNING` vs. `MAX()`)
- **Concurrency Safety**: Using `INSERT ... RETURNING order_id` guarantees retrieval of the exact primary key generated for the current session and transaction.
- **Race Condition Prevention**: Avoids secondary lookups like `SELECT MAX(order_id)`, which produce race conditions and incorrect foreign key mappings when concurrent transactions insert records simultaneously.

#### 8. Transaction Atomicity and Failure Recovery
- **Batch Atomicity**: Scoping `conn.commit()` outside data ingestion loops guarantees that complex multi-table inserts execute as an atomic, all-or-nothing unit of work.
- **State Recovery**: Catching exceptions and executing `conn.rollback()` purges uncommitted writes, preventing orphaned rows and corrupt partial data from persisting in the database.

#### 9. Source Data Financial Reconciliation
- **Mathematical Consistency**: Asserts that `orders.total_amount` equals the aggregated line-item calculation `SUM(quantity * unit_price)` directly at the source.
- **Error Detection**: Identifies floating-point drift, missing line items, or unhandled discounts before extracted data enters downstream transformation pipelines.

#### 10. Batch Extraction Engine Architecture (`src/extract.py`)
- **Table Registry Pattern**: Uses a centralized list (`TABLES_TO_EXTRACT`) to iterate through source entities programmatically, eliminating duplicate single-table extraction scripts.
- **Pipeline Observability**: Captures runtime duration, row counts, and compressed file sizes into a structured dictionary, providing operational telemetry for automated ingestion monitoring.

#### 11. Bronze Layer Automated Quality Gates (DuckDB)
- **Direct Parquet Execution**: Uses DuckDB to run cross-file validation queries directly on disk without standing up a database server or executing intermediate load steps.
- **Structural Integrity**: Asserts primary key uniqueness (`COUNT(*) - COUNT(DISTINCT order_id) = 0`) and referential integrity (confirming zero orphaned `customer_id` or `store_id` foreign keys).
- **Financial Integrity**: Confirms cross-file parity between `orders.parquet` and `order_items.parquet` to ensure zero data loss during file serialization.

#### 12. Incremental State Tracking (`src/state.py` & `_state.json`)
- **High-Watermark Pattern**: Storing the maximum `created_at` timestamp converts expensive full-table scans into targeted delta queries (`WHERE created_at > :watermark`).
- **Data Time vs. Execution Time**: `last_watermark` tracks the source transaction timestamp, while `last_run_at` logs the script's UTC execution time for observability and pipeline lag monitoring.
- **Per-Table State Isolation**: Scoping state by table key ensures independent watermarks, columns, and runtimes across multiple tables without state collisions.

#### 13. Hybrid Extraction Architecture (`src/extract.py`)
- **Hybrid Extraction Registry (`TABLE_CONFIGS`)**: Configured per-table extraction strategies—full snapshot refreshes (`watermark_col: None`) for dimension tables and incremental deltas (`watermark_col: "created_at"`) for append-heavy transaction tables.
- **Empty-Delta Guardrails**: Implemented an explicit guard clause on `len(df) == 0` to prevent scheduled pipeline runs from overwriting existing Parquet files with 0-byte/empty datasets during idle windows.
- **Delta Concatenation & Ingestion**: Implemented Parquet append logic (`pd.concat([existing_df, df])`) to merge incoming delta slices into Bronze Parquet storage while advancing the high watermark to `max(created_at)`.