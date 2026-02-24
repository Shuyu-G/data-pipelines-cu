# Binance Bitcoin Price Tracking Exercise

## Overview

This exercise demonstrates a real-world data pipeline that collects, aggregates, and stores cryptocurrency price data using Apache Airflow. The pipeline fetches Bitcoin (BTCUSDT) prices from the Binance API and performs multi-level time-based aggregations.

## Learning Objectives

By completing this exercise, you will learn:

1. **API Integration**: How to fetch data from external APIs in Airflow
2. **Multi-Level Aggregation**: Building hierarchical data processing pipelines
3. **Time-Based Scheduling**: Using different schedule intervals for different tasks
4. **Data Partitioning**: Organizing data by date for efficient storage and retrieval
5. **Error Handling**: Implementing retry logic for network operations
6. **CSV Data Storage**: Persisting data in CSV format for analysis

## Exercise Structure

This exercise consists of **three separate DAGs** that work together:

### 1. `12_binance_fetch_minute.py` - Data Collection

**Purpose**: Fetches Bitcoin price data from Binance API every minute

**Schedule**: Runs every 1 minute (`timedelta(minutes=1)`)

**What it does**:
- Calls Binance API: `https://api.binance.com/api/v3/avgPrice?symbol=BTCUSDT`
- Receives JSON response with price, timestamp, and metadata
- Saves raw data to CSV files with date partitioning
- Stores data in: `/data/binance/raw/{date}/daily_raw.csv`

**API Response Format**:
```json
{
    "mins": 5,
    "price": "68285.81006621",
    "closeTime": 1771317380403
}
```

**Output Structure**:
- Individual minute files: `/data/binance/raw/{date}/price_{hour}_{minute}.csv`
- Daily aggregated file: `/data/binance/raw/{date}/daily_raw.csv`

**Key Features**:
- Automatic retry on API failures (3 retries with 1-minute delay)
- Timestamp addition for tracking
- Date-partitioned storage
- Error handling for network issues

---

### 2. `13_binance_calculate_hourly.py` - Hourly Aggregation

**Purpose**: Calculates hourly average prices from minute-level data

**Schedule**: Runs every 1 hour (`timedelta(hours=1)`)

**What it does**:
- Reads minute-level data from the daily raw CSV file
- Groups data by hour
- Calculates statistics: average, min, max, first, last price
- Saves hourly aggregates to: `/data/binance/hourly/{date}/hourly_avg.csv`

**Input**: `/data/binance/raw/{date}/daily_raw.csv`

**Output**: `/data/binance/hourly/{date}/hourly_avg.csv`

**Calculated Metrics**:
- `avg_price`: Average price for the hour
- `min_price`: Minimum price in the hour
- `max_price`: Maximum price in the hour
- `first_price`: First price recorded in the hour
- `last_price`: Last price recorded in the hour
- `data_points`: Number of minute-level data points used

**Key Features**:
- Handles missing data gracefully
- Prevents duplicate hour entries
- Automatic date-based file organization

---

### 3. `14_binance_calculate_daily.py` - Daily Aggregation

**Purpose**: Calculates daily average prices from hourly data

**Schedule**: Runs every 24 hours (`timedelta(days=1)`)

**What it does**:
- Reads hourly average data
- Aggregates all hours in a day
- Calculates daily statistics including price change
- Saves to: `/data/binance/daily/daily_avg.csv`

**Input**: `/data/binance/hourly/{date}/hourly_avg.csv`

**Output**: `/data/binance/daily/daily_avg.csv`

**Calculated Metrics**:
- `avg_price`: Average price for the day
- `min_price`: Minimum price in the day
- `max_price`: Maximum price in the day
- `opening_price`: First price of the day
- `closing_price`: Last price of the day
- `price_change`: Absolute price change (closing - opening)
- `price_change_pct`: Percentage price change
- `total_data_points`: Total minute-level data points
- `hours_with_data`: Number of hours with data

**Key Features**:
- Maintains historical daily averages in single file
- Sorts data chronologically
- Calculates price change metrics

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  Binance API                                                │
│  https://api.binance.com/api/v3/avgPrice?symbol=BTCUSDT   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ Every 1 minute
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  12_binance_fetch_minute.py                                 │
│  - Fetches price data                                       │
│  - Adds timestamp                                           │
│  - Saves to CSV                                             │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ Writes
                       ▼
        /data/binance/raw/{date}/daily_raw.csv
                       │
                       │ Every 1 hour
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  13_binance_calculate_hourly.py                             │
│  - Reads minute data                                        │
│  - Groups by hour                                           │
│  - Calculates hourly stats                                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ Writes
                       ▼
        /data/binance/hourly/{date}/hourly_avg.csv
                       │
                       │ Every 24 hours
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  14_binance_calculate_daily.py                              │
│  - Reads hourly data                                        │
│  - Aggregates by day                                        │
│  - Calculates daily stats                                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ Writes
                       ▼
            /data/binance/daily/daily_avg.csv
```

---

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `requests` - For API calls
- `pandas` - For data processing
- `apache-airflow` - For orchestration

### 2. Configure Airflow

1. **Place DAG files** in your Airflow DAGs folder:
   ```
   /path/to/airflow/dags/
   ├── 12_binance_fetch_minute.py
   ├── 13_binance_calculate_hourly.py
   └── 14_binance_calculate_daily.py
   ```

2. **Create data directory** (or let Airflow create it):
   ```bash
   mkdir -p /data/binance/{raw,hourly,daily}
   ```

3. **Ensure write permissions** for Airflow user

### 3. Enable DAGs in Airflow UI

1. Open Airflow web UI (typically `http://localhost:8080`)
2. Find the three Binance DAGs:
   - `binance_fetch_minute`
   - `binance_calculate_hourly`
   - `binance_calculate_daily`
3. Toggle them ON (enable)

### 4. Monitor Execution

- **Minute DAG**: Should run every minute (check after 1-2 minutes)
- **Hourly DAG**: Should run every hour (check after 1 hour)
- **Daily DAG**: Should run once per day (check after 24 hours)

---

## Running the Exercise

### Initial Setup

1. **Start Airflow** (if not already running):
   ```bash
   airflow webserver
   airflow scheduler
   ```

2. **Enable all three DAGs** in the Airflow UI

3. **Wait for data collection**:
   - Minute-level data starts immediately
   - Hourly aggregation begins after first hour
   - Daily aggregation begins after first 24 hours

### Recommended Run Duration

**Minimum**: 24 hours to see complete daily aggregation

**Recommended**: 3-7 days to see:
- Multiple daily averages
- Price trends over time
- Data quality and consistency

### Verifying Data Collection

Check the output directories:

```bash
# Raw minute data
ls -la /data/binance/raw/$(date +%Y-%m-%d)/

# Hourly averages
ls -la /data/binance/hourly/$(date +%Y-%m-%d)/

# Daily averages
ls -la /data/binance/daily/
```

---

## Output File Formats

### 1. Raw Minute Data (`daily_raw.csv`)

**Location**: `/data/binance/raw/{date}/daily_raw.csv`

**Columns**:
- `mins`: Time window in minutes (usually 5)
- `price`: Price as string
- `closeTime`: Unix timestamp in milliseconds
- `timestamp`: ISO format timestamp
- `fetch_time`: Human-readable timestamp
- `price_float`: Price as float for calculations

**Example**:
```csv
mins,price,closeTime,timestamp,fetch_time,price_float
5,68200.50,1705312200000,2024-01-15T10:00:00,2024-01-15 10:00:00,68200.50
5,68210.25,1705312260000,2024-01-15T10:01:00,2024-01-15 10:01:00,68210.25
```

### 2. Hourly Averages (`hourly_avg.csv`)

**Location**: `/data/binance/hourly/{date}/hourly_avg.csv`

**Columns**:
- `date`: Date (YYYY-MM-DD)
- `hour`: Hour (00-23)
- `avg_price`: Average price for the hour
- `min_price`: Minimum price in the hour
- `max_price`: Maximum price in the hour
- `first_price`: First price in the hour
- `last_price`: Last price in the hour
- `data_points`: Number of minute data points
- `calculated_at`: When the calculation was performed

**Example**:
```csv
date,hour,avg_price,min_price,max_price,first_price,last_price,data_points,calculated_at
2024-01-15,10,68250.25,68100.00,68400.00,68200.00,68300.00,60,2024-01-15 10:59:59
```

### 3. Daily Averages (`daily_avg.csv`)

**Location**: `/data/binance/daily/daily_avg.csv`

**Columns**:
- `date`: Date (YYYY-MM-DD)
- `avg_price`: Average price for the day
- `min_price`: Minimum price in the day
- `max_price`: Maximum price in the day
- `opening_price`: First price of the day
- `closing_price`: Last price of the day
- `price_change`: Absolute price change
- `price_change_pct`: Percentage price change
- `total_data_points`: Total minute data points
- `hours_with_data`: Number of hours with data
- `calculated_at`: When the calculation was performed

**Example**:
```csv
date,avg_price,min_price,max_price,opening_price,closing_price,price_change,price_change_pct,total_data_points,hours_with_data,calculated_at
2024-01-15,68250.25,67500.00,69000.00,68000.00,68500.00,500.00,0.74,1440,24,2024-01-16 00:00:00
```

---

## Task-by-Task Explanation

### Task 1: `fetch_binance_price` (12_binance_fetch_minute.py)

#### What It Does
Fetches the current Bitcoin average price from Binance API and saves it to a CSV file.

#### How It Works

**In Airflow**:
```python
fetch_price = PythonOperator(
    task_id="fetch_binance_price",
    python_callable=_fetch_binance_price,
    dag=dag,
)
```

The function:
1. Makes HTTP GET request to Binance API
2. Parses JSON response
3. Adds timestamp and converts price to float
4. Saves to date-partitioned CSV file
5. Handles errors with retry logic

#### Why Airflow is Better

| Feature | Airflow | Regular Script |
|---------|---------|----------------|
| **Scheduling** | Automatic every minute | Manual or cron (harder to monitor) |
| **Retries** | Built-in retry (3 attempts) | Must implement yourself |
| **Monitoring** | Web UI shows all runs | No visibility |
| **Error Handling** | Automatic failure tracking | Manual error checking |
| **Continuous Operation** | Runs 24/7 automatically | Requires process management |

**Without Airflow**, you would need to:
- Set up a cron job or systemd timer
- Implement your own retry logic
- Build monitoring and alerting
- Handle process crashes manually
- Track execution history yourself

---

### Task 2: `calculate_hourly_average` (13_binance_calculate_hourly.py)

#### What It Does
Reads minute-level price data and calculates hourly statistics (average, min, max, etc.).

#### How It Works

**In Airflow**:
```python
calculate_hourly = PythonOperator(
    task_id="calculate_hourly_average",
    python_callable=_calculate_hourly_average,
    dag=dag,
)
```

The function:
1. Reads the daily raw CSV file
2. Filters data for the current hour
3. Calculates statistics (mean, min, max, first, last)
4. Saves hourly aggregate to CSV
5. Prevents duplicate entries

#### Why Airflow is Better

| Feature | Airflow | Regular Script |
|---------|---------|----------------|
| **Dependency Management** | Waits for minute data to exist | Must check file existence manually |
| **Scheduling** | Runs exactly every hour | Cron timing issues |
| **Data Partitioning** | Automatic date-based organization | Manual file management |
| **Idempotency** | Can rerun safely without duplicates | Risk of duplicate calculations |
| **Monitoring** | See which hours were processed | No visibility |

**Without Airflow**, you would need to:
- Manually check if minute data exists
- Implement duplicate prevention logic
- Handle timezone and scheduling edge cases
- Build your own execution tracking

---

### Task 3: `calculate_daily_average` (14_binance_calculate_daily.py)

#### What It Does
Reads hourly average data and calculates daily statistics including price change metrics.

#### How It Works

**In Airflow**:
```python
calculate_daily = PythonOperator(
    task_id="calculate_daily_average",
    python_callable=_calculate_daily_average,
    dag=dag,
)
```

The function:
1. Reads hourly average CSV for the day
2. Aggregates all hours
3. Calculates daily statistics
4. Computes price change (opening vs closing)
5. Maintains historical daily file

#### Why Airflow is Better

| Feature | Airflow | Regular Script |
|---------|---------|----------------|
| **Historical Tracking** | Maintains single file with all days | Must manually merge files |
| **Data Consistency** | Ensures all hours processed | Risk of missing hours |
| **Scheduling** | Runs once per day reliably | Cron timing issues |
| **Data Quality** | Can validate data completeness | Manual validation needed |
| **Reprocessing** | Can rerun for specific dates | Complex manual process |

**Without Airflow**, you would need to:
- Manually run script once per day
- Handle file merging and deduplication
- Validate data completeness
- Build your own historical tracking

---

## Common Issues and Troubleshooting

### Issue 1: API Rate Limiting

**Symptom**: API calls fail with 429 (Too Many Requests)

**Solution**: 
- Binance API has rate limits
- The current implementation (1 request/minute) is well within limits
- If issues occur, increase retry delay in `default_args`

### Issue 2: Missing Data Files

**Symptom**: Hourly/Daily DAGs fail with "file not found"

**Solution**:
- Ensure minute DAG has been running long enough
- Check file paths and permissions
- Verify data directory exists: `/data/binance/`

### Issue 3: Duplicate Entries

**Symptom**: CSV files have duplicate rows

**Solution**:
- The DAGs include deduplication logic
- If duplicates appear, check the filtering logic
- Ensure DAGs are not running with `catchup=True` unnecessarily

### Issue 4: Timezone Issues

**Symptom**: Data appears in wrong hours/days

**Solution**:
- All timestamps use system timezone
- Ensure Airflow server timezone matches your expectations
- Check `datetime.now()` usage in functions

---

## Extending the Exercise

### Ideas for Enhancement

1. **Add More Cryptocurrencies**:
   - Fetch prices for ETH, BNB, etc.
   - Modify symbol parameter in API call

2. **Add Alerting**:
   - Send email/Slack when price changes > 5%
   - Alert on API failures

3. **Add Database Storage**:
   - Store data in PostgreSQL/MySQL
   - Enable SQL queries for analysis

4. **Add Visualization**:
   - Generate charts using matplotlib
   - Create price trend reports

5. **Add Data Validation**:
   - Check for missing data points
   - Validate price ranges (detect anomalies)

---

## Key Concepts Demonstrated

### 1. Multi-Level Aggregation
- Raw data → Hourly aggregates → Daily aggregates
- Each level provides different insights
- Demonstrates hierarchical data processing

### 2. Time-Based Scheduling
- Different schedules for different tasks
- Minute, hourly, and daily intervals
- Shows flexibility of Airflow scheduling

### 3. Data Partitioning
- Files organized by date
- Easy to locate specific time periods
- Efficient for large datasets

### 4. Error Handling
- Retry logic for transient failures
- Graceful handling of missing data
- Logging for debugging

### 5. Idempotency
- Tasks can be rerun safely
- Prevents duplicate data
- Essential for data pipelines

---

## Sample Output Files

Sample CSV files are included in this directory:

- `sample_output_raw_data.csv` - Example minute-level data
- `sample_output_hourly_avg.csv` - Example hourly averages
- `sample_output_daily_avg.csv` - Example daily averages

These demonstrate the expected output format after running the pipeline.

---

## Summary

This exercise demonstrates a **production-ready data pipeline** that:

✅ Fetches data from external APIs  
✅ Performs time-based aggregations  
✅ Stores data in organized, partitioned files  
✅ Handles errors gracefully  
✅ Runs continuously without manual intervention  
✅ Provides monitoring and observability  

**Key Takeaway**: Airflow transforms what would be complex, error-prone scripts into reliable, monitored, production-grade data pipelines.

---

## Next Steps

1. **Run the exercise** for at least 24 hours
2. **Analyze the output** CSV files
3. **Experiment** with different schedule intervals
4. **Extend** the pipeline with additional features
5. **Compare** with how you would implement this without Airflow

Happy learning! 🚀

