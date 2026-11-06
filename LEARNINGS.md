### 1. Why Not Run Heavy Analytics on OLTP (PostgreSQL)?
* **Protects App Performance:** OLTP is optimized for millisecond-level customer writes and reads; heavy analytics consume CPU and memory, causing API timeouts or app crashes.
* **Avoids Row-Storage Inefficiency:** PostgreSQL reads entire rows from disk just to calculate a single column's average, resulting in massive disk I/O waste.
* **Limits Blast Radius:** Analytical experimentation, ad-hoc queries, and large exports stay completely isolated from live production transactions.

### 2. Role of Parquet Between PostgreSQL and DuckDB
* **Decoupled Staging Layer:** Stores raw extracted snapshots as files on disk instead of holding long-lived live connections to PostgreSQL.
* **Columnar & Compressed:** Shrinks storage size by 70–90% compared to raw database dumps and loads only queried columns into memory.
* **DuckDB's Native Format:** Allows DuckDB to execute fast vectorized queries and metadata-based filtering (predicate pushdown) directly on the files.

### 3. Purpose of `.venv` and `.gitignore`
* **`.venv` (Isolation):** Prevents dependency version conflicts between different projects and protects your operating system's base Python environment.
* **`.gitignore` (Security & Cleanliness):** Prevents tracking gigabytes of virtual environment binaries, temporary data files (`*.parquet`), and secret credentials (`.env`).

### The grain difference between orders (checkout transaction) and order_items (basket line item).
In `orders`, one row represents a single checkout transaction placed by a customer at a specific point in time; in `order_items`, one row represents a single product line item (and its purchased quantity) belonging to that order.

### Why master records should not use ON DELETE CASCADE, and why production systems prefer soft deletes (is_active = FALSE).
 Master tables (e.g., `customers`, `products`) must avoid `ON DELETE CASCADE` because permanently deleting a parent record would trigger a chain reaction that erases historical sales receipts and audit trails; using a soft delete (`is_active = FALSE` or `deleted_at`) hides the entity from the customer-facing app while keeping historical transaction integrity and financial reports completely intact.

### Why an index on the watermark column (created_at) is mandatory for high-volume incremental extraction.
Incremental pipelines extract only newly created or updated records using queries like `WHERE created_at >= :watermark`; adding a B-Tree index on `created_at` prevents the database engine from executing a full-table disk scan on millions of past rows, enabling high-speed range lookups that fetch only the delta.


- **`RETURNING order_id` vs `MAX()`**: Avoids race conditions in concurrent pipelines by returning the exact auto-generated identity for that statement, rather than relying on another lookup.
- **Transaction Atomicity**: Keeping `conn.commit()` outside the loop ensures the entire batch is all-or-nothing; if one record fails, `conn.rollback()` prevents dirty, partial data from polluting the database.
- **Financial Reconciliation Checks**: Verifying that `orders.total_amount` equals `SUM(quantity * unit_price)` in SQL guarantees source data consistency before building analytical models.


- **Batch Extraction Engine (`src/extract.py`)**: Implemented a generalized Table Registry pattern (`TABLES_TO_EXTRACT`) that dynamically queries PostgreSQL tables, writes compressed Parquet files, and logs extraction metrics (row counts, file sizes, runtimes).
- **Bronze Layer Quality Gate**: Used DuckDB to run cross-file SQL assertions directly against raw Parquet files on disk, validating:
  1. Financial reconciliation (`orders.total_amount` matches `order_items` line-item sums).
  2. Primary key uniqueness (`COUNT(*) == COUNT(DISTINCT order_id)`).
  3. Referential integrity (zero orphan foreign keys for `customer_id` and `store_id`).