from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import col


RAW_INPUT = "data/raw_weather.json"
PARQUET_OUTPUT = "out/weather_curated_parquet"
CSV_OUTPUT = "out/weather_curated_csv"


def publish_output(local_path: Path, output_path: Path) -> None:
    if output_path.exists():
        shutil.rmtree(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(local_path, output_path)


def main() -> None:
    spark = (
        SparkSession.builder.appName("lecture11b-weather-etl")
        .master("local[*]")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    raw = spark.read.option("multiLine", "true").json(RAW_INPUT)

    curated = raw.select(
        col("latitude").cast("double").alias("latitude"),
        col("longitude").cast("double").alias("longitude"),
        col("timezone").alias("timezone"),
        col("current.time").alias("observation_time"),
        col("current.temperature_2m").cast("double").alias("temp_c_current"),
        col("current.relative_humidity_2m").cast("integer").alias("humidity_percent"),
        col("current.wind_speed_10m").cast("double").alias("wind_speed_kmh"),
        col("current.weather_code").cast("integer").alias("weather_code"),
        col("daily.time")[0].alias("forecast_date"),
        col("daily.temperature_2m_max")[0].cast("double").alias("temp_c_max"),
        col("daily.temperature_2m_min")[0].cast("double").alias("temp_c_min"),
        col("daily.precipitation_sum")[0].cast("double").alias("precipitation_mm"),
    )

    temp_root = Path(tempfile.mkdtemp(prefix="lecture11b_weather_"))
    local_parquet = temp_root / "weather_curated_parquet"
    local_csv = temp_root / "weather_curated_csv"

    try:
        # Spark's Hadoop output committer renames temporary files in a way that
        # VirtualBox shared folders do not reliably support. Commit on the VM's
        # local disk first, then copy the finished files back to /vagrant/out.
        curated.write.mode("overwrite").parquet(str(local_parquet))
        curated.coalesce(1).write.mode("overwrite").option("header", "true").csv(
            str(local_csv)
        )
        publish_output(local_parquet, Path(PARQUET_OUTPUT))
        publish_output(local_csv, Path(CSV_OUTPUT))
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)

    print("Curated weather ETL output:")
    curated.show(truncate=False)
    print(f"Wrote Parquet output to {PARQUET_OUTPUT}")
    print(f"Wrote CSV output to {CSV_OUTPUT}")

    spark.stop()


if __name__ == "__main__":
    main()
