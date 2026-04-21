Lecture 11 Assignment 1 submission files for `weather_unstructured_to_structured`

Workflow summary
- `fetch_weather` calls Open-Meteo with:
  - `current=temperature_2m,wind_speed_10m`
  - `hourly=temperature_2m,relative_humidity_2m,wind_speed_10m`
- `ollama_to_structured` sends the raw weather payload to local Ollama using `qwen3.5:9b`
- `validate_and_emit` validates and logs the final structured JSON

Files
- `assignment1-weather_unstructured_to_structured-airflow-success-run.png`
  Successful Airflow DAG run for `weather_unstructured_to_structured`.
- `assignment1-weather_unstructured_to_structured-fetch-weather-log.png`
  Evidence of the corrected Open-Meteo API parameters used by `fetch_weather`.
- `assignment1-weather_unstructured_to_structured-validate-and-emit-json.png`
  Final structured JSON emitted by `validate_and_emit`.
- `assignment1-weather_unstructured_to_structured-open-webui-qwen.png`
  Open WebUI running locally with `qwen3.5:9b` selected.
- `assignment1-weather_unstructured_to_structured-runtime-status.png`
  Local runtime status showing the successful DAG run, Docker containers, and available Ollama models.
