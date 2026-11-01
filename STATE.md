### STATE BLOCK
- Phase / Day / Step: Phase 0 | Day 2 | Gate Completed (Ready for Phase 1, Day 3)
- Tool versions in use: Python 3.14.7, Git, VS Code, local PostgreSQL + DBeaver
- Repo structure:
  quick-commerce-data-platform/
  ├── .gitignore
  ├── .gitattributes
  ├── README.md
  ├── LEARNINGS.md
  ├── data/ (.gitkeep)
  ├── sql/ (.gitkeep)
  └── src/ (__init__.py)
- Decisions made and why:
  - PostgreSQL selected for OLTP (fast, ACID row transactions for order placement).
  - Parquet selected for intermediate lake storage (compressed, columnar format).
  - DuckDB + dbt selected for OLAP transformation (fast analytical aggregations without loading the OLTP DB).
  - Apache Airflow selected to orchestrate the pipeline runs.
  - Streamlit selected for the user-facing KPI dashboard.
- Open problems: Install Docker Desktop on Windows 11 with WSL2 backend before running containerized PostgreSQL in Phase 1.

### STATE BLOCK
- Phase / Day / Step: Phase 1 | Day 6 | Gate Completed (Ready for Phase 2, Day 7, Step 1)
- Tool versions in use: Python 3.14.7, Docker Desktop (WSL 2 backend), PostgreSQL 16 (port 5433), DBeaver, Git
- Repo structure:
  quick-commerce-data-platform/
  ├── .gitignore
  ├── .gitattributes
  ├── README.md
  ├── LEARNINGS.md
  ├── data/ (.gitkeep)
  ├── sql/
  │   ├── 01_create_tables.sql
  │   └── 02_create_indexes.sql
  └── src/ (__init__.py)
- Table schemas decided so far:
  - customers (customer_id PK, first_name, last_name, email UNIQUE, phone_number UNIQUE, address, created_at)
  - stores (store_id PK, store_name, address, city, zip_code, is_active, created_at)
  - products (product_id PK, product_name, description, price, category, stock_quantity, created_at)
  - orders (order_id PK, customer_id FK, store_id FK, total_amount, order_status, created_at, delivered_at)
  - order_items (order_item_id PK, order_id FK ON DELETE CASCADE, product_id FK, quantity, unit_price)
- Decisions made and why:
  - Containerized PostgreSQL 16 mapped to host port 5433 to avoid collision with Windows PostgreSQL on 5432.
  - Persistent volume `qc_postgres_data` attached so data survives container stops.
  - Master entities omit `ON DELETE CASCADE` to protect historical transactional and revenue data.
  - Custom B-Tree indexes added on all FKs and `orders(created_at)` to eliminate sequential scans during incremental pipeline extraction.
- Open problems: None. Phase 1 schema, indexes, and constraints verified in PostgreSQL.