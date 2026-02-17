# Anatomy of an Airflow DAG

This document explains the structure and components of an Apache Airflow DAG (Directed Acyclic Graph), based on the "Anatomy of an Airflow DAG" chapter from "Data Pipelines with Apache Airflow" by Bas P. Harenslak and Julian Rutger de Ruiter.

## Table of Contents

1. [Overview](#overview)
2. [DAG Structure](#dag-structure)
3. [Components Explained](#components-explained)
4. [Complete Example](#complete-example)
5. [Rocket Launcher Example](#rocket-launcher-example)
6. [Best Practices](#best-practices)

---

## Overview

An Airflow DAG is a Python script that defines a workflow as a collection of tasks with dependencies. The DAG itself doesn't perform any computation; it describes **what** should run, **when** it should run, and **how** tasks depend on each other.

### Key Concepts

- **DAG**: A collection of tasks with dependencies, representing a workflow
- **Task**: A single unit of work (e.g., running a Python function, executing a SQL query)
- **Operator**: A template for a task that defines what work to perform
- **Dependencies**: Relationships between tasks that determine execution order

---

## DAG Structure

A typical Airflow DAG consists of the following sections:

```python
# 1. IMPORTS
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

# 2. DEFAULT ARGUMENTS
default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'email': ['admin@example.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# 3. DAG DEFINITION
dag = DAG(
    'example_dag',
    default_args=default_args,
    description='A simple example DAG',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['example', 'tutorial'],
)

# 4. TASK DEFINITIONS
def extract_data():
    """Extract data from source."""
    print("Extracting data...")
    return "extracted_data"

extract_task = PythonOperator(
    task_id='extract',
    python_callable=extract_data,
    dag=dag,
)

def transform_data():
    """Transform the extracted data."""
    print("Transforming data...")
    return "transformed_data"

transform_task = PythonOperator(
    task_id='transform',
    python_callable=transform_data,
    dag=dag,
)

def load_data():
    """Load transformed data to destination."""
    print("Loading data...")
    return "loaded_data"

load_task = PythonOperator(
    task_id='load',
    python_callable=load_data,
    dag=dag,
)

# 5. TASK DEPENDENCIES
extract_task >> transform_task >> load_task
```

---

## Components Explained

### 1. Imports

**Purpose**: Import necessary Airflow modules and other dependencies.

**Common Imports**:
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.email import EmailOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
```

**Explanation**:
- `DAG`: The main class for defining a DAG
- `PythonOperator`: Executes Python functions as tasks
- `BashOperator`: Executes bash commands
- `EmailOperator`: Sends emails
- `days_ago`: Helper function for date calculations

---

### 2. Default Arguments (`default_args`)

**Purpose**: Define default parameters that apply to all tasks in the DAG. This promotes code reuse and consistency.

**Common Default Arguments**:

```python
default_args = {
    # Owner information
    'owner': 'data_engineering_team',
    
    # Dependency management
    'depends_on_past': False,  # Task doesn't depend on previous run
    'wait_for_downstream': False,  # Don't wait for downstream tasks
    
    # Email notifications
    'email': ['admin@example.com', 'team@example.com'],
    'email_on_failure': True,  # Send email if task fails
    'email_on_retry': False,   # Don't send email on retry
    
    # Retry configuration
    'retries': 3,  # Number of retry attempts
    'retry_delay': timedelta(minutes=5),  # Wait 5 minutes between retries
    
    # Execution timeout
    'execution_timeout': timedelta(hours=2),  # Task must complete within 2 hours
    
    # Pool and queue
    'pool': 'default_pool',  # Resource pool for task execution
    'queue': 'default',  # Queue name for task execution
    
    # SLA (Service Level Agreement)
    'sla': timedelta(hours=1),  # Task should complete within 1 hour
    
    # Trigger rules
    'trigger_rule': 'all_success',  # Run only if all upstream tasks succeed
}
```

**Key Parameters Explained**:

| Parameter | Description | Example |
|-----------|-------------|---------|
| `owner` | Person/team responsible for the DAG | `'data_team'` |
| `depends_on_past` | Task depends on previous DAG run | `True`/`False` |
| `email_on_failure` | Send email notification on failure | `True`/`False` |
| `retries` | Number of automatic retries | `3` |
| `retry_delay` | Time to wait before retry | `timedelta(minutes=5)` |
| `execution_timeout` | Maximum execution time | `timedelta(hours=2)` |
| `sla` | Service level agreement time | `timedelta(hours=1)` |

**Why Use Default Args?**:
- **DRY Principle**: Define once, apply to all tasks
- **Consistency**: All tasks share the same retry/email policies
- **Maintainability**: Change behavior in one place
- **Override**: Individual tasks can override these defaults

---

### 3. DAG Definition

**Purpose**: Create the DAG object that contains all tasks and defines when/how the workflow runs.

**DAG Constructor Parameters**:

```python
dag = DAG(
    # Required parameters
    dag_id='my_etl_pipeline',  # Unique identifier (must be unique across all DAGs)
    default_args=default_args,  # Default arguments for tasks
    
    # Scheduling
    schedule_interval=timedelta(days=1),  # How often to run (or cron expression)
    start_date=datetime(2024, 1, 1),  # When to start scheduling runs
    
    # Execution control
    catchup=False,  # Don't backfill missed runs
    max_active_runs=1,  # Maximum concurrent DAG runs
    
    # Metadata
    description='ETL pipeline for daily data processing',
    tags=['etl', 'daily', 'production'],
    
    # Additional settings
    concurrency=16,  # Maximum concurrent tasks
    default_view='tree',  # Default UI view
    orientation='LR',  # Graph orientation (LR = Left to Right)
)
```

**Key Parameters Explained**:

| Parameter | Description | Common Values |
|-----------|-------------|---------------|
| `dag_id` | Unique identifier for the DAG | `'daily_etl'`, `'hourly_report'` |
| `schedule_interval` | How often DAG runs | `timedelta(days=1)`, `'0 0 * * *'` (cron), `None` (manual) |
| `start_date` | First execution date | `datetime(2024, 1, 1)` |
| `catchup` | Backfill missed runs | `True`/`False` |
| `max_active_runs` | Max concurrent DAG runs | `1`, `3`, `10` |
| `description` | Human-readable description | `'Daily ETL pipeline'` |
| `tags` | Labels for filtering/organization | `['etl', 'production']` |

**Schedule Interval Examples**:

```python
# Run daily at midnight
schedule_interval='0 0 * * *'  # Cron format
schedule_interval=timedelta(days=1)  # Timedelta format

# Run hourly
schedule_interval='0 * * * *'  # Cron format
schedule_interval=timedelta(hours=1)  # Timedelta format

# Run every 15 minutes
schedule_interval='*/15 * * * *'  # Cron format
schedule_interval=timedelta(minutes=15)  # Timedelta format

# Manual trigger only (no schedule)
schedule_interval=None
```

**Catchup Behavior**:

```python
# catchup=False (Recommended)
# If DAG starts on Jan 1 but you deploy on Jan 10:
# - Only runs from Jan 10 onwards
# - Doesn't backfill Jan 1-9

# catchup=True
# If DAG starts on Jan 1 but you deploy on Jan 10:
# - Creates DAG runs for Jan 1-9
# - Can cause resource issues with many missed runs
```

---

### 4. Task Definitions

**Purpose**: Define individual units of work using operators.

**Common Operator Types**:

#### PythonOperator
Executes a Python function:

```python
def my_function(**context):
    """Task function receives Airflow context."""
    # Access execution date
    execution_date = context['ds']
    
    # Access task instance
    ti = context['ti']
    
    # Do work
    result = process_data()
    
    # Push result to XCom (for downstream tasks)
    ti.xcom_push(key='result', value=result)
    
    return result

python_task = PythonOperator(
    task_id='process_data',
    python_callable=my_function,
    op_kwargs={'param1': 'value1'},  # Additional keyword arguments
    dag=dag,
)
```

#### BashOperator
Executes a bash command:

```python
bash_task = BashOperator(
    task_id='run_script',
    bash_command='python /path/to/script.py',
    env={'ENV_VAR': 'value'},  # Environment variables
    dag=dag,
)
```

#### SQL Operators
Execute SQL queries:

```python
from airflow.providers.postgres.operators.postgres import PostgresOperator

sql_task = PostgresOperator(
    task_id='create_table',
    postgres_conn_id='postgres_default',
    sql='CREATE TABLE IF NOT EXISTS users (id INT, name VARCHAR);',
    dag=dag,
)
```

**Task Parameters**:

| Parameter | Description | Example |
|-----------|-------------|---------|
| `task_id` | Unique identifier within DAG | `'extract_data'` |
| `dag` | DAG object this task belongs to | `dag` |
| `retries` | Override default retries | `5` |
| `retry_delay` | Override default retry delay | `timedelta(minutes=10)` |
| `execution_timeout` | Task timeout | `timedelta(hours=1)` |
| `pool` | Resource pool | `'high_priority_pool'` |
| `priority_weight` | Task priority | `10` |

---

### 5. Task Dependencies

**Purpose**: Define the order of task execution using dependency operators.

**Dependency Syntax**:

```python
# Method 1: Using bitshift operators (Recommended)
task1 >> task2 >> task3
# task1 runs first, then task2, then task3

# Method 2: Using set_upstream/set_downstream
task1.set_downstream(task2)
task2.set_downstream(task3)

# Method 3: Using lists for parallel execution
task1 >> [task2, task3] >> task4
# task1 runs, then task2 and task3 run in parallel, then task4

# Method 4: Complex dependencies
[task1, task2] >> task3 >> [task4, task5]
```

**Dependency Patterns**:

```python
# Sequential (Linear)
extract >> transform >> load

# Parallel (Fan-out)
extract >> [transform1, transform2, transform3] >> load

# Conditional (Fan-in)
[task1, task2, task3] >> merge_task

# Complex Graph
extract >> [validate, clean] >> transform >> [load_db, load_warehouse]
```

**Trigger Rules**:

```python
from airflow.utils.trigger_rule import TriggerRule

# Default: all_success (all upstream tasks must succeed)
task = PythonOperator(
    task_id='task',
    python_callable=func,
    trigger_rule=TriggerRule.ALL_SUCCESS,  # Default
    dag=dag,
)

# Other trigger rules:
# - ALL_SUCCESS: All upstream tasks succeed
# - ALL_FAILED: All upstream tasks fail
# - ONE_SUCCESS: At least one upstream task succeeds
# - ONE_FAILED: At least one upstream task fails
# - NONE_FAILED: No upstream tasks fail (can be skipped)
# - DUMMY: Always run (ignore dependencies)
```

---

## Complete Example

Here's a complete, production-ready example of an ETL pipeline DAG:

```python
"""
Complete ETL Pipeline DAG Example
===================================
This DAG demonstrates a complete data pipeline with:
- Data extraction from multiple sources
- Data transformation and validation
- Data loading to destination
- Error handling and notifications
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.email import EmailOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
import logging

# Configure logging
logger = logging.getLogger(__name__)

# ============================================================================
# DEFAULT ARGUMENTS
# ============================================================================

default_args = {
    'owner': 'data_engineering_team',
    'depends_on_past': False,
    'email': ['data-team@example.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=2),
    'sla': timedelta(hours=1),
}

# ============================================================================
# DAG DEFINITION
# ============================================================================

dag = DAG(
    'complete_etl_pipeline',
    default_args=default_args,
    description='Complete ETL pipeline with extraction, transformation, and loading',
    schedule_interval='0 2 * * *',  # Run daily at 2 AM
    start_date=days_ago(1),
    catchup=False,
    max_active_runs=1,
    tags=['etl', 'production', 'daily'],
)

# ============================================================================
# TASK FUNCTIONS
# ============================================================================

def extract_data(**context):
    """Extract data from source systems."""
    execution_date = context['ds']
    logger.info(f"Extracting data for date: {execution_date}")
    
    # Simulate data extraction
    data = {
        'date': execution_date,
        'records': 1000,
        'source': 'database'
    }
    
    # Push to XCom for downstream tasks
    context['ti'].xcom_push(key='extracted_data', value=data)
    
    logger.info(f"Extracted {data['records']} records")
    return data

def validate_data(**context):
    """Validate extracted data."""
    ti = context['ti']
    data = ti.xcom_pull(key='extracted_data', task_ids='extract')
    
    logger.info(f"Validating data: {data}")
    
    # Perform validation
    if data['records'] == 0:
        raise ValueError("No records extracted!")
    
    logger.info("Data validation passed")
    return True

def transform_data(**context):
    """Transform and clean data."""
    ti = context['ti']
    data = ti.xcom_pull(key='extracted_data', task_ids='extract')
    
    logger.info(f"Transforming {data['records']} records")
    
    # Simulate transformation
    transformed = {
        'date': data['date'],
        'processed_records': data['records'],
        'status': 'transformed'
    }
    
    ti.xcom_push(key='transformed_data', value=transformed)
    
    logger.info("Transformation completed")
    return transformed

def load_data(**context):
    """Load transformed data to destination."""
    ti = context['ti']
    data = ti.xcom_pull(key='transformed_data', task_ids='transform')
    
    logger.info(f"Loading {data['processed_records']} records to destination")
    
    # Simulate loading
    logger.info("Data loaded successfully")
    return True

def send_success_notification(**context):
    """Send success notification."""
    logger.info("ETL pipeline completed successfully!")
    return True

# ============================================================================
# TASK DEFINITIONS
# ============================================================================

# Extract task
extract_task = PythonOperator(
    task_id='extract',
    python_callable=extract_data,
    dag=dag,
)

# Validate task
validate_task = PythonOperator(
    task_id='validate',
    python_callable=validate_data,
    dag=dag,
)

# Transform task
transform_task = PythonOperator(
    task_id='transform',
    python_callable=transform_data,
    dag=dag,
)

# Load task
load_task = PythonOperator(
    task_id='load',
    python_callable=load_data,
    dag=dag,
)

# Success notification
success_notification = PythonOperator(
    task_id='send_success_notification',
    python_callable=send_success_notification,
    dag=dag,
)

# ============================================================================
# TASK DEPENDENCIES
# ============================================================================

# Define execution order:
# 1. Extract data
# 2. Validate extracted data (in parallel with extract completion)
# 3. Transform validated data
# 4. Load transformed data
# 5. Send success notification

extract_task >> validate_task >> transform_task >> load_task >> success_notification
```

**Visual Representation**:

```
extract
  ↓
validate
  ↓
transform
  ↓
load
  ↓
send_success_notification
```

---

## Rocket Launcher Example

This example demonstrates a rocket launch sequence using Airflow DAGs. It uses the [The Space Devs API](https://ll.thespacedevs.com/2.0.0/launch/upcoming/) to fetch real upcoming rocket launch data, making it a practical example that shows:
- **API integration**: Fetching real data from external APIs
- **Parallel execution**: Multiple pre-flight checks run simultaneously
- **Conditional dependencies**: Launch only proceeds if all checks pass
- **Sequential execution**: Launch sequence must follow a specific order
- **XCom usage**: Passing data between tasks
- **Error handling**: Retries and failure notifications

### Complete Rocket Launcher DAG

```python
"""
Rocket Launcher DAG Example
============================
This DAG demonstrates a rocket launch sequence with:
- Parallel pre-flight checks (weather, fuel, systems)
- Sequential launch sequence (countdown, ignition, launch)
- Conditional execution based on check results
- Error handling and notifications
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.trigger_rule import TriggerRule
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
import requests
import random
import logging

# Configure logging
logger = logging.getLogger(__name__)

# API endpoint for upcoming launches
LAUNCH_API_URL = "https://ll.thespacedevs.com/2.0.0/launch/upcoming/"

# ============================================================================
# DEFAULT ARGUMENTS
# ============================================================================

default_args = {
    'owner': 'mission_control',
    'depends_on_past': False,
    'email': ['mission-control@spacex.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=1),
    'execution_timeout': timedelta(minutes=30),
}

# ============================================================================
# DAG DEFINITION
# ============================================================================

dag = DAG(
    'rocket_launcher',
    default_args=default_args,
    description='Rocket launch sequence with pre-flight checks and launch procedures',
    schedule_interval=None,  # Manual trigger only (safety!)
    start_date=days_ago(1),
    catchup=False,
    tags=['rocket', 'launch', 'demo'],
)

# ============================================================================
# TASK FUNCTIONS - FETCH LAUNCH DATA
# ============================================================================

def fetch_upcoming_launch(**context):
    """Fetch the next upcoming launch from The Space Devs API."""
    logger.info("Fetching upcoming launch data from API...")
    
    try:
        # Fetch upcoming launches (limit to 1 for the next launch)
        response = requests.get(LAUNCH_API_URL, params={'limit': 1})
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('count', 0) == 0 or not data.get('results'):
            raise ValueError("No upcoming launches found")
        
        launch = data['results'][0]
        
        launch_info = {
            'name': launch.get('name', 'Unknown'),
            'status': launch.get('status', {}).get('name', 'Unknown'),
            'net': launch.get('net', 'TBD'),
            'window_start': launch.get('window_start', 'TBD'),
            'window_end': launch.get('window_end', 'TBD'),
            'rocket': launch.get('rocket', {}).get('configuration', {}).get('name', 'Unknown'),
            'mission': launch.get('mission', {}).get('name', 'Unknown'),
            'location': launch.get('pad', {}).get('location', {}).get('name', 'Unknown'),
            'launch_service_provider': launch.get('launch_service_provider', {}).get('name', 'Unknown'),
        }
        
        logger.info(f"Fetched launch: {launch_info['name']}")
        logger.info(f"Status: {launch_info['status']}")
        logger.info(f"Launch Window: {launch_info['window_start']} to {launch_info['window_end']}")
        logger.info(f"Rocket: {launch_info['rocket']}")
        logger.info(f"Location: {launch_info['location']}")
        
        # Push launch info to XCom for downstream tasks
        context['ti'].xcom_push(key='launch_info', value=launch_info)
        context['ti'].xcom_push(key='launch_status', value=launch_info['status'])
        
        return launch_info
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch launch data: {e}")
        raise
    except (KeyError, IndexError) as e:
        logger.error(f"Error parsing launch data: {e}")
        raise ValueError(f"Invalid launch data format: {e}")

# ============================================================================
# TASK FUNCTIONS - PRE-FLIGHT CHECKS
# ============================================================================

def check_weather(**context):
    """Check weather conditions for launch."""
    ti = context['ti']
    
    # Get launch info from previous task
    launch_info = ti.xcom_pull(key='launch_info', task_ids='fetch_upcoming_launch')
    
    logger.info(f"Checking weather conditions for launch: {launch_info.get('name', 'Unknown')}")
    logger.info(f"Launch location: {launch_info.get('location', 'Unknown')}")
    
    # Simulate weather check (in production, you'd call a weather API)
    # Using launch location to make it more realistic
    weather_conditions = {
        'temperature': random.randint(15, 30),
        'wind_speed': random.randint(0, 25),
        'cloud_cover': random.randint(0, 100),
        'visibility': random.randint(5, 20),
        'location': launch_info.get('location', 'Unknown'),
    }
    
    # Determine if weather is suitable
    is_suitable = (
        weather_conditions['wind_speed'] < 20 and
        weather_conditions['cloud_cover'] < 50 and
        weather_conditions['visibility'] > 10
    )
    
    weather_conditions['suitable'] = is_suitable
    
    if is_suitable:
        logger.info(f"Weather check PASSED: {weather_conditions}")
    else:
        logger.warning(f"Weather check FAILED: {weather_conditions}")
        if weather_conditions['wind_speed'] >= 20:
            raise ValueError(f"Wind speed too high: {weather_conditions['wind_speed']} km/h")
        elif weather_conditions['cloud_cover'] >= 50:
            raise ValueError(f"Cloud cover too high: {weather_conditions['cloud_cover']}%")
        else:
            raise ValueError(f"Visibility too low: {weather_conditions['visibility']} km")
    
    # Push result to XCom
    ti.xcom_push(key='weather_status', value=weather_conditions)
    return weather_conditions

def check_fuel(**context):
    """Check fuel levels and systems."""
    ti = context['ti']
    
    # Get launch info from previous task
    launch_info = ti.xcom_pull(key='launch_info', task_ids='fetch_upcoming_launch')
    rocket_name = launch_info.get('rocket', 'Unknown')
    
    logger.info(f"Checking fuel systems for {rocket_name}...")
    
    # Simulate fuel check (in production, you'd check actual fuel systems)
    fuel_status = {
        'fuel_level': random.randint(80, 100),  # Percentage
        'oxidizer_level': random.randint(80, 100),
        'pressure': random.randint(90, 110),  # PSI
        'rocket': rocket_name,
    }
    
    # Determine if fuel is adequate
    is_adequate = (
        fuel_status['fuel_level'] >= 85 and
        fuel_status['oxidizer_level'] >= 85 and
        95 <= fuel_status['pressure'] <= 105
    )
    
    fuel_status['adequate'] = is_adequate
    
    if is_adequate:
        logger.info(f"Fuel check PASSED: {fuel_status}")
    else:
        logger.warning(f"Fuel check FAILED: {fuel_status}")
        raise ValueError(f"Fuel systems not ready: {fuel_status}")
    
    # Push result to XCom
    ti.xcom_push(key='fuel_status', value=fuel_status)
    return fuel_status

def check_systems(**context):
    """Check all rocket systems."""
    ti = context['ti']
    
    # Get launch info from previous task
    launch_info = ti.xcom_pull(key='launch_info', task_ids='fetch_upcoming_launch')
    launch_status = ti.xcom_pull(key='launch_status', task_ids='fetch_upcoming_launch')
    
    logger.info(f"Checking rocket systems for {launch_info.get('name', 'Unknown')}...")
    logger.info(f"Launch status from API: {launch_status}")
    
    # Check if launch status from API is "Go"
    api_status_go = launch_status == "Go"
    
    # Simulate systems check
    systems_status = {
        'navigation': random.choice([True, True, True, False]),  # 75% success rate
        'communication': random.choice([True, True, True, False]),
        'life_support': random.choice([True, True, True, False]),
        'payload': random.choice([True, True, True, False]),
        'api_status': launch_status,
        'api_status_go': api_status_go,
    }
    
    # Determine if all systems are operational
    # Also check if API status is "Go"
    all_operational = all([
        systems_status['navigation'],
        systems_status['communication'],
        systems_status['life_support'],
        systems_status['payload'],
        api_status_go  # Must be "Go" from API
    ])
    
    systems_status['all_operational'] = all_operational
    
    if all_operational:
        logger.info(f"Systems check PASSED: {systems_status}")
    else:
        failed_systems = [k for k, v in systems_status.items() if not v and k != 'api_status']
        if not api_status_go:
            failed_systems.append(f"API status: {launch_status} (expected 'Go')")
        logger.warning(f"Systems check FAILED: {failed_systems}")
        raise ValueError(f"Systems not operational: {failed_systems}")
    
    # Push result to XCom
    ti.xcom_push(key='systems_status', value=systems_status)
    return systems_status

# ============================================================================
# TASK FUNCTIONS - LAUNCH SEQUENCE
# ============================================================================

def final_go_no_go(**context):
    """Final go/no-go decision based on all checks."""
    ti = context['ti']
    
    # Pull results from all pre-flight checks
    weather = ti.xcom_pull(key='weather_status', task_ids='check_weather')
    fuel = ti.xcom_pull(key='fuel_status', task_ids='check_fuel')
    systems = ti.xcom_pull(key='systems_status', task_ids='check_systems')
    
    logger.info("Performing final go/no-go decision...")
    logger.info(f"Weather: {weather.get('suitable', False)}")
    logger.info(f"Fuel: {fuel.get('adequate', False)}")
    logger.info(f"Systems: {systems.get('all_operational', False)}")
    
    # Make final decision
    go_for_launch = (
        weather.get('suitable', False) and
        fuel.get('adequate', False) and
        systems.get('all_operational', False)
    )
    
    if go_for_launch:
        logger.info("✅ GO FOR LAUNCH! All systems ready.")
        ti.xcom_push(key='go_for_launch', value=True)
        return True
    else:
        logger.error("❌ NO GO! Launch aborted.")
        raise ValueError("Launch aborted: Pre-flight checks failed")

def countdown(**context):
    """Perform launch countdown."""
    ti = context['ti']
    
    # Get launch info
    launch_info = ti.xcom_pull(key='launch_info', task_ids='fetch_upcoming_launch')
    
    logger.info(f"Starting launch countdown for {launch_info.get('name', 'Unknown')}...")
    logger.info(f"Mission: {launch_info.get('mission', 'Unknown')}")
    logger.info(f"Launch window: {launch_info.get('window_start', 'TBD')} to {launch_info.get('window_end', 'TBD')}")
    
    # Simulate countdown
    for i in range(10, 0, -1):
        logger.info(f"T-{i}...")
    
    logger.info("T-0! Ready for ignition!")
    return True

def ignite_engines(**context):
    """Ignite rocket engines."""
    logger.info("Igniting engines...")
    logger.info("🔥 Engine 1: IGNITED")
    logger.info("🔥 Engine 2: IGNITED")
    logger.info("🔥 Engine 3: IGNITED")
    logger.info("All engines ignited successfully!")
    return True

def launch(**context):
    """Execute rocket launch."""
    ti = context['ti']
    
    # Get launch info
    launch_info = ti.xcom_pull(key='launch_info', task_ids='fetch_upcoming_launch')
    
    logger.info(f"🚀 LAUNCH! {launch_info.get('name', 'Unknown')} is ascending!")
    logger.info(f"Rocket: {launch_info.get('rocket', 'Unknown')}")
    logger.info(f"Mission: {launch_info.get('mission', 'Unknown')}")
    logger.info("Altitude: 100m... 500m... 1km... 5km...")
    logger.info("Rocket successfully launched!")
    return True

def mission_success(**context):
    """Celebrate successful launch."""
    logger.info("🎉 MISSION SUCCESS! Rocket launch completed successfully!")
    return True

# ============================================================================
# TASK DEFINITIONS - FETCH LAUNCH DATA
# ============================================================================

# Fetch upcoming launch from API
fetch_launch_task = PythonOperator(
    task_id='fetch_upcoming_launch',
    python_callable=fetch_upcoming_launch,
    dag=dag,
)

# ============================================================================
# TASK DEFINITIONS - PRE-FLIGHT CHECKS
# ============================================================================

# Pre-flight checks (run in parallel, after fetching launch data)
check_weather_task = PythonOperator(
    task_id='check_weather',
    python_callable=check_weather,
    dag=dag,
)

check_fuel_task = PythonOperator(
    task_id='check_fuel',
    python_callable=check_fuel,
    dag=dag,
)

check_systems_task = PythonOperator(
    task_id='check_systems',
    python_callable=check_systems,
    dag=dag,
)

# ============================================================================
# TASK DEFINITIONS - LAUNCH SEQUENCE
# ============================================================================

# Final decision
go_no_go_task = PythonOperator(
    task_id='final_go_no_go',
    python_callable=final_go_no_go,
    trigger_rule=TriggerRule.ALL_SUCCESS,  # All checks must pass
    dag=dag,
)

# Launch sequence
countdown_task = PythonOperator(
    task_id='countdown',
    python_callable=countdown,
    dag=dag,
)

ignite_task = PythonOperator(
    task_id='ignite_engines',
    python_callable=ignite_engines,
    dag=dag,
)

launch_task = PythonOperator(
    task_id='launch',
    python_callable=launch,
    dag=dag,
)

mission_success_task = PythonOperator(
    task_id='mission_success',
    python_callable=mission_success,
    dag=dag,
)

# ============================================================================
# TASK DEPENDENCIES
# ============================================================================

# First, fetch launch data from API
# Then pre-flight checks run in parallel
fetch_launch_task >> [check_weather_task, check_fuel_task, check_systems_task] >> go_no_go_task

# Launch sequence (sequential)
go_no_go_task >> countdown_task >> ignite_task >> launch_task >> mission_success_task
```

### Visual Representation

```
fetch_upcoming_launch
        ↓
check_weather ──┐
check_fuel     ├──> final_go_no_go ──> countdown ──> ignite_engines ──> launch ──> mission_success
check_systems ──┘
```

### API Integration

This example uses the [The Space Devs API](https://ll.thespacedevs.com/2.0.0/launch/upcoming/) to fetch real upcoming rocket launch data. The API provides:

- **Real launch information**: Actual upcoming launches from various space agencies
- **Launch status**: Current status (Go, TBD, etc.)
- **Launch windows**: Actual launch time windows
- **Rocket and mission details**: Real rocket configurations and mission information
- **Location data**: Actual launch pad locations

**API Endpoint**: `https://ll.thespacedevs.com/2.0.0/launch/upcoming/`

The `fetch_upcoming_launch` task retrieves the next upcoming launch and makes this data available to all downstream tasks via XCom.

### Key Concepts Demonstrated

1. **Parallel Execution**:
   ```python
   [check_weather_task, check_fuel_task, check_systems_task] >> go_no_go_task
   ```
   All three pre-flight checks run simultaneously, improving efficiency.

2. **Conditional Dependencies**:
   ```python
   trigger_rule=TriggerRule.ALL_SUCCESS
   ```
   The `final_go_no_go` task only runs if ALL upstream checks succeed.

3. **XCom Data Passing**:
   ```python
   context['ti'].xcom_push(key='weather_status', value=weather_conditions)
   weather = ti.xcom_pull(key='weather_status', task_ids='check_weather')
   ```
   Data flows from pre-flight checks to the final decision task.

4. **Sequential Launch Sequence**:
   ```python
   go_no_go_task >> countdown_task >> ignite_task >> launch_task >> mission_success_task
   ```
   Launch steps must execute in strict order.

5. **Error Handling**:
   - If any pre-flight check fails, the launch is aborted
   - Retries are configured for transient failures
   - Email notifications on failure

### Running the Example

**Important**: This DAG has `schedule_interval=None`, meaning it only runs when manually triggered (for safety!).

**Prerequisites**: 
- Install the `requests` library: `pip install requests`
- The DAG will fetch real launch data from [The Space Devs API](https://ll.thespacedevs.com/2.0.0/launch/upcoming/)

To trigger manually:
1. Open Airflow UI
2. Find the `rocket_launcher` DAG
3. Click "Trigger DAG" button
4. Watch the execution in the Graph View

**Note**: The API call is made in the `fetch_upcoming_launch` task, which must complete successfully before pre-flight checks can run.

### Expected Behavior

- **If all checks pass**: Launch sequence proceeds normally
- **If any check fails**: Launch is aborted, no countdown/launch tasks run
- **Retries**: Failed checks will retry up to 2 times before final failure

### Learning Points

1. **Parallel vs Sequential**: Pre-flight checks run in parallel (faster), launch sequence is sequential (safety-critical)
2. **Trigger Rules**: Use `ALL_SUCCESS` to ensure all prerequisites are met
3. **XCom**: Share data between tasks using XCom push/pull
4. **Error Propagation**: Failures in upstream tasks prevent downstream execution
5. **Manual Scheduling**: Some DAGs should only run on-demand (`schedule_interval=None`)

---

## Best Practices

### 1. DAG Organization

```python
# ✅ Good: Clear, descriptive DAG ID
dag_id='daily_sales_etl_pipeline'

# ❌ Bad: Vague or unclear
dag_id='dag1'
```

### 2. Task Naming

```python
# ✅ Good: Descriptive task IDs
task_id='extract_customer_data'
task_id='validate_sales_transactions'
task_id='load_to_data_warehouse'

# ❌ Bad: Unclear task IDs
task_id='task1'
task_id='process'
```

### 3. Error Handling

```python
# ✅ Good: Proper retry configuration
default_args = {
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': True,
}

# ❌ Bad: No retry configuration or excessive retries
default_args = {
    'retries': 0,  # No retries
}
# or
default_args = {
    'retries': 100,  # Too many retries
}
```

### 4. Resource Management

```python
# ✅ Good: Set appropriate concurrency limits
dag = DAG(
    'my_dag',
    max_active_runs=1,  # Prevent overlapping runs
    concurrency=10,  # Limit concurrent tasks
    dag=dag,
)

# Use pools for resource management
task = PythonOperator(
    task_id='heavy_computation',
    python_callable=func,
    pool='heavy_compute_pool',  # Limit resource usage
    pool_slots=2,  # Use 2 slots from pool
    dag=dag,
)
```

### 5. XCom Usage

```python
# ✅ Good: Use XCom for small data (< 48KB)
ti.xcom_push(key='result', value=small_data)

# ❌ Bad: Don't use XCom for large data
ti.xcom_push(key='result', value=large_dataframe)  # Use external storage instead
```

### 6. Idempotency

```python
# ✅ Good: Tasks are idempotent (can run multiple times safely)
def load_data(**context):
    # Use INSERT ... ON CONFLICT or similar
    # Task can be rerun without issues
    pass

# ❌ Bad: Tasks that fail on rerun
def load_data(**context):
    # Simple INSERT without conflict handling
    # Will fail if rerun
    pass
```

### 7. Documentation

```python
# ✅ Good: Well-documented DAG
dag = DAG(
    'my_dag',
    description='Daily ETL pipeline for customer data. '
                'Extracts from PostgreSQL, transforms, and loads to data warehouse.',
    tags=['etl', 'daily', 'customer-data'],
    dag=dag,
)

# Add docstrings to task functions
def extract_data(**context):
    """
    Extract customer data from PostgreSQL database.
    
    Returns:
        dict: Extracted data with metadata
    """
    pass
```

### 8. Testing

```python
# ✅ Good: Test DAG structure
def test_dag_loaded():
    """Test that DAG can be loaded without errors."""
    from airflow.models import DagBag
    dagbag = DagBag()
    assert 'my_dag' in dagbag.dags
    assert len(dagbag.dags['my_dag'].tasks) == 5
```

---

## Summary

A well-structured Airflow DAG consists of:

1. **Imports**: Required Airflow modules and dependencies
2. **Default Arguments**: Shared configuration for all tasks
3. **DAG Definition**: Workflow metadata and scheduling
4. **Task Definitions**: Individual units of work using operators
5. **Task Dependencies**: Execution order and relationships

**Key Takeaways**:

- Use `default_args` for code reuse and consistency
- Set `catchup=False` to avoid unwanted backfills
- Use descriptive `dag_id` and `task_id` values
- Define clear task dependencies
- Implement proper error handling and retries
- Keep tasks idempotent
- Document your DAGs and tasks
- Test your DAG structure

---

## Additional Resources

- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [Airflow Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
- [Airflow Concepts](https://airflow.apache.org/docs/apache-airflow/stable/concepts/index.html)

---

**Note**: This guide is based on Airflow 2.x. Some syntax may differ for Airflow 1.x.

