# Lecture 11B Assignment: Hadoop + Spark ETL

This submission follows the Lecture 11B Hadoop + Spark ETL assignment:

1. Bring up a Vagrant VM.
2. Install Java and Spark in the VM.
3. Fetch raw Open-Meteo weather JSON.
4. Run a PySpark ETL job that writes curated output files.

The ETL uses Spark local mode inside the VM, which matches the lecture note that Spark local mode is enough for the first version before scaling to full Hadoop/YARN.

## Architecture

- `scripts/fetch_weather.py` extracts raw weather data from Open-Meteo and writes `data/raw_weather.json`.
- `spark/weather_etl.py` reads the raw JSON with Spark, flattens current and first-day daily forecast fields, and writes curated Parquet and CSV outputs.
- `Vagrantfile` provisions an Ubuntu VM with Java, Python, and Spark 3.5.1 for Hadoop 3.
  It selects an ARM64 Ubuntu box on Apple Silicon hosts and `ubuntu/jammy64` on x86 hosts.

## Files

- `Vagrantfile` - single Ubuntu VM with 4 GB RAM and 2 CPUs.
- `scripts/fetch_weather.py` - Open-Meteo extraction script.
- `spark/weather_etl.py` - PySpark transformation job.
- `requirements.txt` - Python dependency note.

## Run

From this directory:

```bash
vagrant up
vagrant ssh
cd /vagrant
python3 scripts/fetch_weather.py
/opt/spark/bin/spark-submit spark/weather_etl.py
ls -la out/weather_curated_csv
head -n 5 out/weather_curated_csv/part-*.csv
```

## Curated Output Fields

- `latitude`
- `longitude`
- `timezone`
- `observation_time`
- `temp_c_current`
- `humidity_percent`
- `wind_speed_kmh`
- `weather_code`
- `forecast_date`
- `temp_c_max`
- `temp_c_min`
- `precipitation_mm`

## Output Paths

- Raw input: `data/raw_weather.json`
- Curated Parquet: `out/weather_curated_parquet/`
- Curated CSV: `out/weather_curated_csv/`

Generated `data/`, `out/`, and `spark-warehouse/` directories are ignored by Git because they are runtime outputs.
