# Lecture 2: Data Pipeline Tutorials

This directory contains three comprehensive tutorials covering fundamental data pipeline concepts with practical Python examples.

## Tutorials Overview

### Tutorial 1: Basic ETL Pipeline (`tutorial1_basic_etl.py`)

**Learning Objectives:**
- Understand the ETL (Extract, Transform, Load) pattern
- Implement data extraction from different sources (JSON, CSV, API, Database)
- Apply data transformations (cleaning, validation, enrichment, normalization)
- Load data to various destinations
- Handle errors and data validation

**Key Concepts:**
- Extract: Getting data from source systems
- Transform: Cleaning, validating, and modifying data
- Load: Writing data to destination systems
- Error handling and logging
- Data validation and schema checking

**Demo Examples:**
1. **JSON to JSON ETL**: Simple pipeline moving data from JSON to JSON
2. **CSV to JSON ETL**: Converting CSV format to JSON
3. **API to Database ETL**: Mock API ingestion to database
4. **Custom Transformations**: Advanced transformation pipeline with data cleaning

**Usage:**
```bash
python tutorial1_basic_etl.py
```

---

### Tutorial 2: Data Ingestion (`tutorial2_data_ingestion.py`)

**Learning Objectives:**
- Understand different data ingestion patterns
- Implement ingestion from various sources (files, APIs, databases, streams)
- Handle streaming vs batch ingestion
- Implement error handling and retry mechanisms
- Validate data during ingestion

**Key Concepts:**
- File-based ingestion (JSON, CSV)
- API-based ingestion with retry logic
- Streaming data ingestion
- Database ingestion
- Schema validation
- Multi-source ingestion pipelines

**Demo Examples:**
1. **File Ingestion**: Ingesting data from JSON files with schema validation
2. **API Ingestion**: API-based ingestion with retry logic and error handling
3. **Streaming Ingestion**: Simulated streaming data ingestion in batches
4. **Multi-Source Ingestion**: Combining data from multiple sources into a single pipeline

**Usage:**
```bash
python tutorial2_data_ingestion.py
```

---

### Tutorial 3: Pipeline Orchestration (`tutorial3_pipeline_orchestration.py`)

**Learning Objectives:**
- Understand pipeline orchestration concepts
- Implement task dependencies
- Create schedulable pipelines
- Handle task failures and retries
- Monitor pipeline execution
- Implement parallel and sequential execution patterns

**Key Concepts:**
- Task definition and dependencies
- Topological sorting for execution order
- Sequential vs parallel execution
- Retry logic and error handling
- Pipeline scheduling
- Status monitoring and logging

**Demo Examples:**
1. **Sequential Pipeline**: Simple linear pipeline execution
2. **Parallel Pipeline**: Parallel task execution with dependency management
3. **Pipeline with Retries**: Handling failures with automatic retries
4. **Scheduled Pipeline**: Scheduling pipelines for periodic execution
5. **Complex Dependencies**: Managing complex task dependency graphs

**Usage:**
```bash
python tutorial3_pipeline_orchestration.py
```

---

### Tutorial 4: Rocket Launcher Pipeline (`tutorial4_rocket_launcher.py`)

**Learning Objectives:**
- Understand API integration in pipelines
- Implement parallel and sequential task execution
- Handle conditional dependencies
- Pass data between tasks using XCom
- Implement proper error handling and retries
- Work with real-world APIs

**Key Concepts:**
- API integration with external services
- Parallel pre-flight checks
- Sequential launch sequence
- Conditional task execution
- Data passing between tasks
- Error handling and retry logic

**Demo Examples:**
1. **Complete Launch Sequence**: Full rocket launch pipeline with real API data
2. **Failure Handling**: Demonstrates how the pipeline handles failures and retries

**API Integration:**
This tutorial uses [The Space Devs API](https://ll.thespacedevs.com/2.0.0/launch/upcoming/) to fetch real upcoming rocket launch data, making it a practical example of API integration in data pipelines.

**Prerequisites:**
- Internet connection (for API calls)
- `requests` library: `pip install requests`

**Usage:**
```bash
python tutorial4_rocket_launcher.py
```

---

## Running the Tutorials

### Prerequisites

Most tutorials use only Python standard library. However:

- **Tutorial 4** requires the `requests` library for API integration:
  ```bash
  pip install requests
  ```

For production use, you might also want to install:
```bash
pip install pandas    # For data manipulation
```

### Running Individual Tutorials

Each tutorial can be run independently:

```bash
# Tutorial 1: Basic ETL
python tutorial1_basic_etl.py

# Tutorial 2: Data Ingestion
python tutorial2_data_ingestion.py

# Tutorial 3: Pipeline Orchestration
python tutorial3_pipeline_orchestration.py

# Tutorial 4: Rocket Launcher Pipeline
python tutorial4_rocket_launcher.py
```

### Running All Tutorials

You can run all tutorials sequentially:

```bash
python tutorial1_basic_etl.py
python tutorial2_data_ingestion.py
python tutorial3_pipeline_orchestration.py
python tutorial4_rocket_launcher.py
```

---

## Tutorial Structure

Each tutorial follows a consistent structure:

1. **Documentation**: Comprehensive docstrings explaining concepts
2. **Class Definitions**: Reusable classes implementing core functionality
3. **Demo Examples**: Multiple practical examples demonstrating different use cases
4. **Logging**: Detailed logging for understanding execution flow
5. **Error Handling**: Robust error handling and validation

---

## Key Learning Path

1. **Start with Tutorial 1** to understand the fundamental ETL pattern
2. **Move to Tutorial 2** to learn about data ingestion from various sources
3. **Continue with Tutorial 3** to understand pipeline orchestration and scheduling
4. **Complete with Tutorial 4** to see API integration and real-world pipeline examples

---

## Concepts Covered

### Data Pipeline Fundamentals
- ETL (Extract, Transform, Load) pattern
- Data ingestion patterns
- Pipeline orchestration
- Task dependencies
- Error handling and retries

### Data Sources
- File-based sources (JSON, CSV)
- API endpoints
- Databases
- Streaming sources

### Data Processing
- Data cleaning
- Data validation
- Data enrichment
- Data normalization
- Schema validation

### Pipeline Management
- Sequential execution
- Parallel execution
- Task scheduling
- Dependency management
- Status monitoring
- API integration
- Real-world data pipelines

---

## Next Steps

After completing these tutorials, you should be able to:

1. Design and implement basic ETL pipelines
2. Ingest data from multiple sources
3. Transform and validate data
4. Orchestrate complex pipelines with dependencies
5. Handle errors and implement retry logic
6. Schedule and monitor pipeline execution

---

## Notes

- All tutorials use mock implementations for APIs and databases to avoid external dependencies
- In production environments, you would use actual libraries like:
  - `requests` for API calls
  - `sqlalchemy` or `pymongo` for database connections
  - `pandas` for data manipulation
  - `apache-airflow` or `prefect` for advanced orchestration

---

## File Structure

```
Lecture2/
├── README.md                          # This file
├── tutorial1_basic_etl.py            # ETL pipeline tutorial
├── tutorial2_data_ingestion.py       # Data ingestion tutorial
├── tutorial3_pipeline_orchestration.py # Pipeline orchestration tutorial
├── tutorial4_rocket_launcher.py      # Rocket launcher pipeline with API integration
├── tutorial2_data_ingestion.py        # Data ingestion tutorial
└── tutorial3_pipeline_orchestration.py  # Pipeline orchestration tutorial
```

---

## Questions and Exercises

After completing each tutorial, try to:

1. Modify the examples to work with your own data sources
2. Add additional transformation functions
3. Implement custom error handling strategies
4. Create more complex dependency graphs
5. Add monitoring and alerting capabilities

---

Happy Learning! 🚀

