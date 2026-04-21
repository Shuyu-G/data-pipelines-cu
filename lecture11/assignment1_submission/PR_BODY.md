## Summary

Lecture 11 Assignment 1 submission for `weather_unstructured_to_structured`.

## What I Added

- Implemented the DAG `weather_unstructured_to_structured`
- Added Assignment 1 screenshots under `lecture11/assignment1_submission/`
- Verified the pipeline completed successfully with:
  - `fetch_weather`
  - `ollama_to_structured`
  - `validate_and_emit`

## Pipeline Details

- Open-Meteo request:
  - `current=temperature_2m,wind_speed_10m`
  - `hourly=temperature_2m,relative_humidity_2m,wind_speed_10m`
- Local Ollama model used for the successful run: `qwen3.5:9b`
- Final structured JSON fields:
  - `latitude`
  - `longitude`
  - `current_time`
  - `current_temperature_2m`
  - `current_wind_speed_10m`
  - `hourly_first_time`
  - `hourly_first_temperature_2m`
  - `hourly_first_relative_humidity_2m`
  - `hourly_first_wind_speed_10m`
  - `source`

## Evidence

- `lecture11/assignment1_submission/assignment1-weather_unstructured_to_structured-airflow-success-run.png`
- `lecture11/assignment1_submission/assignment1-weather_unstructured_to_structured-fetch-weather-log.png`
- `lecture11/assignment1_submission/assignment1-weather_unstructured_to_structured-validate-and-emit-json.png`
- `lecture11/assignment1_submission/assignment1-weather_unstructured_to_structured-open-webui-qwen.png`
- `lecture11/assignment1_submission/assignment1-weather_unstructured_to_structured-runtime-status.png`
