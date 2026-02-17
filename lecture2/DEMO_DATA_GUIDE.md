# Demo Data Guide

This document describes all the demo data files created by the tutorials.

## Tutorial 1: Basic ETL Pipeline (`tutorial1_basic_etl.py`)

### Demo 1: JSON to JSON ETL
- **Source File**: `demo1_source_data.json`
  - Contains 3 user records with id, name, email, and age
- **Output File**: `demo1_output_data.json`
  - Transformed and enriched user data

### Demo 2: CSV to JSON ETL
- **Source File**: `demo2_source_products.csv`
  - Contains 5 product records with id, product_id, product_name, price, and stock
- **Output File**: `demo2_output_products.json`
  - Converted CSV data to JSON format with transformations

### Demo 3: API to Database ETL
- **Source**: Mock API endpoint (`https://api.example.com/users`)
  - Simulates API data extraction
  - No files created (mock implementation)

### Demo 4: Custom Transformations
- **Source File**: `demo4_source_data.json`
  - Contains 5 user records with some data quality issues:
    - Extra whitespace in names
    - Missing fields (age, id)
    - Data that needs cleaning
- **Output File**: `demo4_output_cleaned.json`
  - Cleaned, validated, enriched, and normalized data

---

## Tutorial 2: Data Ingestion (`tutorial2_data_ingestion.py`)

### Demo 1: File-Based Data Ingestion
- **Source File**: `demo1_products.json`
  - Contains 5 product records with id, name, price, and stock
  - Used for schema validation demonstration

### Demo 2: API-Based Data Ingestion
- **Source**: Mock API endpoint
  - No files created (simulated API calls)

### Demo 3: Streaming Data Ingestion
- **Source**: Simulated streaming source
  - No files created (generates data on-the-fly)

### Demo 4: Multi-Source Data Ingestion
- **Source Files**:
  - `demo4_users.json`: 3 user records
  - `demo4_orders.csv`: 4 order records
- **Output File**: `demo4_combined_data.json`
  - Combined data from all sources (files + API)

---

## Tutorial 3: Pipeline Orchestration (`tutorial3_pipeline_orchestration.py`)

This tutorial doesn't create data files. It demonstrates:
- Task execution and dependencies
- Pipeline orchestration patterns
- Scheduling and monitoring

All data is generated in-memory during execution.

---

## File Naming Convention

All demo files use prefixes to avoid conflicts:
- `demo1_*` - Files from Demo 1
- `demo2_*` - Files from Demo 2
- `demo3_*` - Files from Demo 3
- `demo4_*` - Files from Demo 4
- `demo5_*` - Files from Demo 5 (if applicable)

---

## Running the Tutorials

All tutorials automatically create their demo data when run. You don't need to prepare any files beforehand.

```bash
# Run Tutorial 1
python tutorial1_basic_etl.py

# Run Tutorial 2
python tutorial2_data_ingestion.py

# Run Tutorial 3
python tutorial3_pipeline_orchestration.py
```

---

## Cleaning Up Demo Files

After running the tutorials, you can clean up the generated files:

```bash
# Remove all demo files
rm demo*.json demo*.csv

# Or keep them for reference
# (They will be overwritten on next run)
```

---

## Notes

- All demo files are created in the same directory as the tutorial scripts
- Files are overwritten each time you run the tutorials
- Demo data is designed to be realistic but simple for learning purposes
- Some demos use mock implementations (APIs, databases) to avoid external dependencies

