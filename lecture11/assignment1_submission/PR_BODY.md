## Summary

Lecture 11 submission for `weather_unstructured_to_structured`, updated to match the latest assignment README.

## What changed

- Added the README starter DAG under `lecture11/assignment/dags/weather_ollama_dag.py`
- Updated the existing Lecture 11 DAG to use the assignment task flow:
  - `fetch_open_meteo_raw`
  - `ollama_to_structured`
  - `validate_and_emit`
- Used Docker Ollama with `qwen3.5:9b`; mock mode was not used.
- Replaced the screenshots under `lecture11/assignment1_submission/`.
- Successful run ID: `manual__2026-04-27T14:21:17.481553+00:00`

## Structured JSON schema

The final `validate_and_emit` output is validated against the required assignment fields:

- `city_label`
- `observation_date`
- `temp_c_current`
- `temp_c_max`
- `temp_c_min`
- `conditions_short`
- `precipitation_mm`

The successful run emitted:

```json
{
  "city_label": "Paris",
  "observation_date": "2026-04-27",
  "temp_c_current": 22.2,
  "temp_c_max": 22.4,
  "temp_c_min": 10.0,
  "conditions_short": "Partly cloudy with a high of 22.4°C and low of 10.0°C. No precipitation expected today.",
  "precipitation_mm": 0.0
}
```

## Evidence

- `lecture11/assignment1_submission/assignment1-weather_unstructured_to_structured-airflow-success-run.png`
- `lecture11/assignment1_submission/assignment1-weather_unstructured_to_structured-fetch-weather-log.png`
- `lecture11/assignment1_submission/assignment1-weather_unstructured_to_structured-validate-and-emit-json.png`
- `lecture11/assignment1_submission/assignment1-weather_unstructured_to_structured-output-result.png`
- `lecture11/assignment1_submission/assignment1-weather_unstructured_to_structured-open-webui-qwen.png`
- `lecture11/assignment1_submission/assignment1-weather_unstructured_to_structured-runtime-status.png`
