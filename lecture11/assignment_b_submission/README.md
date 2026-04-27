# Lecture 11B Submission Evidence

This folder contains screenshots for the Hadoop + Spark ETL assignment.

Run summary:

- Date: 2026-04-27
- VM: Vagrant 2.4.9 + VirtualBox 7.2.8, Ubuntu ARM64 on Apple Silicon.
- Spark: Spark 3.5.1 for Hadoop 3, Java 17.
- Data source: Open-Meteo API.
- Outputs: `out/weather_curated_parquet/` and `out/weather_curated_csv/`.

Screenshots:

- `lecture11b-vagrant-status.png` - Vagrant VM running.
- `lecture11b-spark-version.png` - Java and Spark installed inside the VM.
- `lecture11b-open-meteo-raw-json.png` - Open-Meteo raw JSON fetched.
- `lecture11b-spark-etl-success.png` - Spark ETL job completed with exit code 0.
- `lecture11b-curated-output-preview.png` - Curated CSV and Parquet output preview.
