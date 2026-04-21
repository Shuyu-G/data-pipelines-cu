## Summary

Lecture 11 Assignment 1 submission for `weather_unstructured_to_structured`.

## What I Added

- Implemented the DAG `weather_unstructured_to_structured`
- Added Assignment 1 screenshots under `lecture11/assignment1_submission/`
- Verified the pipeline completed successfully with:
  - `fetch_weather`
  - `ollama_to_structured`
  - `validate_and_emit`

## Evidence

- `lecture11/assignment1_submission/assignment1-weather_unstructured_to_structured-airflow-success-run.png`
- `lecture11/assignment1_submission/assignment1-weather_unstructured_to_structured-validate-and-emit-json.png`
- `lecture11/assignment1_submission/assignment1-weather_unstructured_to_structured-open-webui-qwen.png`
- `lecture11/assignment1_submission/assignment1-weather_unstructured_to_structured-runtime-status.png`

## Notes

- The local Ollama model used for the successful run was `qwen3.5:9b`
- The pipeline reads weather data from Open-Meteo, sends the raw payload to Ollama, and validates the final structured JSON output
