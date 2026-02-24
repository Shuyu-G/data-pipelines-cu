# Lecture 3 Exercise – Binance Data Pipeline

## Overview

This exercise implements a complete data pipeline using Apache Airflow to collect and aggregate Bitcoin (BTCUSDT) price data from the Binance public API.

The pipeline consists of three DAGs:

1. **12_binance_fetch_minute.py**
   - Fetches BTCUSDT average price from Binance API every minute
   - Stores minute-level raw data as CSV files
   - Appends data to a `daily_raw.csv` file for further aggregation

2. **13_binance_calculate_hourly.py**
   - Reads minute-level raw data
   - Calculates hourly statistics:
     - Average price
     - Minimum price
     - Maximum price
     - First price of the hour
     - Last price of the hour
     - Number of data points
   - Stores results in `hourly_avg.csv`

3. **14_binance_calculate_daily.py**
   - Reads hourly aggregated data
   - Calculates daily statistics:
     - Daily average price
     - Minimum and maximum price
     - Opening price
     - Closing price
     - Price change
     - Percentage change
     - Total number of data points
   - Stores results in `daily_avg.csv`

---

## Data Source

The data is collected from the Binance public API:

https://api.binance.com/api/v3/avgPrice?symbol=BTCUSDT

The API provides the current average BTCUSDT price.

---

## Data Storage Structure

All generated output data is stored inside:
lecture3/exercise/binance/
## Data Storage Structure

All generated data is stored in the following structure:

```text
binance/
├── raw/
│   └── YYYY-MM-DD/
│       ├── price_HH_MM.csv
│       └── daily_raw.csv
├── hourly/
│   └── YYYY-MM-DD/
│       └── hourly_avg.csv
└── daily/
    └── daily_avg.csv
```

## Scheduling

- Minute DAG → runs every 1 minute  
- Hourly DAG → runs every 1 hour  
- Daily DAG → runs every 24 hours  

---

## What Was Implemented

- A complete ETL pipeline using Apache Airflow
- Minute-level data ingestion from a real-world API
- Partitioned file storage by date
- Multi-level aggregation (minute → hourly → daily)
- File-based processing using Pandas
- Automated scheduling and task orchestration

---

## Result

The pipeline successfully collected and aggregated Binance price data for the exercise period.

All generated output files are included in this folder.
