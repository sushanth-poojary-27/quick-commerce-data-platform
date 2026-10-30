# Quick-Commerce Data Platform

An end-to-end data platform simulating a 10-minute grocery delivery service (Blinkit/Zepto style).

## Architecture
- **OLTP Database:** PostgreSQL (orders, inventory, deliveries, customers)
- **Ingestion:** Python & Faker (synthetic transaction generator)
- **Data Lake / Storage:** Local Parquet files (partitioned & idempotent)
- **Transformation & Warehouse:** dbt + DuckDB (Star Schema)
- **Orchestration:** Apache Airflow in Docker
- **BI / Analytics:** Streamlit / Metabase Dashboard