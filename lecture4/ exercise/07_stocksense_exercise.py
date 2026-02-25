"""
Lecture 4 - Exercise: StockSense Wikipedia Pageviews ETL

Based on listing_4_20 from "Data Pipelines with Apache Airflow" (Chapter 4).

EXERCISE: Complete ETL pipeline that fetches Wikipedia pageviews for tracked
companies and saves to CSV. Uses Jinja templating for dynamic date handling.

Pipeline: get_data → extract_gz → fetch_pageviews → add_to_db

Data source: https://dumps.wikimedia.org/other/pageviews/
Format: domain_code page_title view_count response_size (space-separated)

Run for at least one successful execution, then include the output CSV in your PR.
"""

from pathlib import Path

import airflow.utils.dates
from airflow import DAG
import pendulum
try:
    from airflow.operators.bash import BashOperator
    from airflow.operators.python import PythonOperator
except ImportError:
    from airflow.providers.standard.operators.bash import BashOperator
    from airflow.providers.standard.operators.python import PythonOperator

PAGENAMES = {"Google", "Amazon", "Apple", "Microsoft", "Facebook"}
OUTPUT_DIR = "/Users/guishuyu/PycharmProjects/datapipeline/airflow_home/dags/data-pipelines-cu-main/lecture4/exercise/data/pageview_counts"
DB_PATH = "/Users/guishuyu/PycharmProjects/datapipeline/airflow_home/dags/data-pipelines-cu-main/lecture4/exercise/data/stocksense.db"

def _get_data(year, month, day, hour, output_path, **_):
    """Download Wikipedia pageviews for the given hour (templated op_kwargs)."""
    from urllib import request
    import ssl
    import certifi

    url = (
        f"https://dumps.wikimedia.org/other/pageviews/"
        f"{year}/{year}-{int(month):02d}/"
        f"pageviews-{year}{int(month):02d}{int(day):02d}-{int(hour):02d}0000.gz"
    )
    print(f"Downloading {url}")

    ctx = ssl.create_default_context(cafile=certifi.where())
    with request.urlopen(url, context=ctx) as resp, open(output_path, "wb") as f:
        f.write(resp.read())


def _fetch_pageviews(pagenames, logical_date, **context):
    result = dict.fromkeys(pagenames, 0)
    with open("/tmp/wikipageviews", "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 4:
                domain_code, page_title, view_count, _ = parts[0], parts[1], parts[2], parts[3]
                if domain_code == "en" and page_title in pagenames:
                    result[page_title] = int(view_count)

    output_path = context["templates_dict"]["output_path"]

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write("pagename,pageviewcount,datetime\n")
        for pagename, count in result.items():
            f.write(f'"{pagename}",{count},{logical_date}\n')

    print(f"Saved pageview counts to {output_path}")
    print(f"Counts: {result}")
    return result

def _add_to_db(**context):
    """Add pageview counts to database. Implement this task."""
    pass


dag = DAG(
    dag_id="lecture4_stocksense_exercise",
    start_date=pendulum.now("UTC").subtract(days=1),
    schedule="@hourly",
    catchup=False,
    max_active_runs=1,
    tags=["lecture4", "exercise", "stocksense", "etl"],
)

get_data = PythonOperator(
    task_id="get_data",
    python_callable=_get_data,
    op_kwargs={
        "year": "{{ logical_date.year }}",
        "month": "{{ logical_date.month }}",
        "day": "{{ logical_date.day }}",
        "hour": "{{ logical_date.hour }}",
        "output_path": "/tmp/wikipageviews.gz",
    },
    dag=dag,
)

extract_gz = BashOperator(
    task_id="extract_gz",
    bash_command="gunzip -f /tmp/wikipageviews.gz",
    dag=dag,
)

fetch_pageviews = PythonOperator(
    task_id="fetch_pageviews",
    python_callable=_fetch_pageviews,
    op_kwargs={"pagenames": PAGENAMES},
    templates_dict={"output_path": f"{OUTPUT_DIR}/{{{{ ds }}}}.csv"},
    dag=dag,
)

add_to_db = PythonOperator(
    task_id="add_to_db",
    python_callable=_add_to_db,
    templates_dict={"output_path": f"{OUTPUT_DIR}/{{{{ ds }}}}.csv"},
    dag=dag,
)

get_data >> extract_gz >> fetch_pageviews >> add_to_db