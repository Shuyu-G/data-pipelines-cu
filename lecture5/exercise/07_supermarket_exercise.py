"""
Lecture 5 - Exercise: Supermarket Promotions ETL with FileSensor

Based on Chapter 6 "Triggering Workflows" – supermarket data ingestion pattern.

EXERCISE: Complete pipeline that waits for supermarket data (FileSensor),
processes it, and loads to a database. The add_to_db task is left empty.

Pipeline: wait_for_supermarket_1 → process_supermarket → add_to_db
"""

import airflow.utils.dates
from airflow import DAG
from datetime import datetime, timedelta
try:
    from airflow.sensors.filesystem import FileSensor
except ImportError:
    from airflow.providers.filesystem.sensors.filesystem import FileSensor

try:
    from airflow.operators.bash import BashOperator
    from airflow.operators.python import PythonOperator
except ImportError:
    from airflow.operators.bash import BashOperator
    from airflow.operators.python import PythonOperator

DATA_DIR = "/Users/guishuyu/data/supermarket1"


def _process_supermarket(**context):
    """
    Read raw data from supermarket, aggregate promotions, save to CSV.
    execution_date (ds) comes from Airflow context.
    """
    import csv
    from pathlib import Path

    ds = context["ds"]
    output_path = Path(f"{DATA_DIR}/processed/promotions_{ds}.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Read all data-*.csv files and aggregate
    raw_dir = Path(DATA_DIR)
    data_files = list(raw_dir.glob("data-*.csv"))
    if not data_files:
        raise FileNotFoundError(f"No data-*.csv files in {raw_dir}")

    promotions = {}
    for f in data_files:
        with open(f, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                prod = row.get("product_id", row.get("product", "unknown"))
                promotions[prod] = promotions.get(prod, 0) + 1

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["product_id", "promotion_count", "date"])
        for prod, count in promotions.items():
            writer.writerow([prod, count, context["ds"]])

    print(f"Saved to {output_path}: {len(promotions)} products")
    return str(output_path)


def _add_to_db(**context):
    """
    Load processed promotions CSV into a local SQLite DB.
    Creates table if missing, then UPSERTs rows for the execution date.
    """
    import csv
    import os
    import sqlite3
    from pathlib import Path

    # 1) Get processed file path from XCom
    processed_csv = context["ti"].xcom_pull(task_ids="process_supermarket")
    if not processed_csv:
        raise ValueError("No XCom value from process_supermarket (expected processed CSV path).")

    processed_csv = str(processed_csv)
    if not os.path.exists(processed_csv):
        raise FileNotFoundError(f"Processed CSV not found: {processed_csv}")

    # 2) Choose a DB location (inside AIRFLOW_HOME)
    airflow_home = os.environ.get("AIRFLOW_HOME", str(Path.home() / "airflow"))
    db_path = os.path.join(airflow_home, "supermarket_promotions.db")

    # 3) Read CSV
    rows = []
    with open(processed_csv, newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(
                (r["product_id"], int(r["promotion_count"]), r["date"])
            )

    if not rows:
        raise ValueError(f"No rows found in processed CSV: {processed_csv}")

    # 4) Write into SQLite (create table + upsert)
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS promotions (
                product_id TEXT NOT NULL,
                date TEXT NOT NULL,
                promotion_count INTEGER NOT NULL,
                PRIMARY KEY (product_id, date)
            )
            """
        )

        # Upsert: replace if exists (SQLite)
        cur.executemany(
            """
            INSERT INTO promotions (product_id, date, promotion_count)
            VALUES (?, ?, ?)
            ON CONFLICT(product_id, date)
            DO UPDATE SET promotion_count=excluded.promotion_count
            """,
            rows,
        )

        conn.commit()

        print(f"✅ Loaded {len(rows)} rows into SQLite DB: {db_path}")
        return db_path
    finally:
        conn.close()


dag = DAG(
    dag_id="lecture5_supermarket_exercise",
    start_date=datetime.now() - timedelta(days=3),
    schedule="0 16 * * *",
    catchup=False,
    tags=["lecture5", "exercise", "supermarket", "filesensor"],
)

# Wait for supermarket data (FileSensor checks for _SUCCESS marker)
wait_for_supermarket_1 = FileSensor(
    task_id="wait_for_supermarket_1",
    filepath=f"{DATA_DIR}/_SUCCESS",
    poke_interval=60,
    timeout=60 * 60 * 24,
    mode="reschedule",
    dag=dag,
)

process_supermarket = PythonOperator(
    task_id="process_supermarket",
    python_callable=_process_supermarket,
    dag=dag,
)

add_to_db = PythonOperator(
    task_id="add_to_db",
    python_callable=_add_to_db,
    dag=dag,
)

wait_for_supermarket_1 >> process_supermarket >> add_to_db
