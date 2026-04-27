Lecture 11 submission files for `weather_unstructured_to_structured`

Workflow summary
- `fetch_open_meteo_raw` calls Open-Meteo with the parameters from the assignment README.
- `ollama_to_structured` sends the raw weather payload to Docker Ollama using `qwen3.5:9b`.
- `validate_and_emit` validates the fixed assignment schema:
  - `city_label`
  - `observation_date`
  - `temp_c_current`
  - `temp_c_max`
  - `temp_c_min`
  - `conditions_short`
  - `precipitation_mm`
- Successful run ID: `manual__2026-04-27T14:21:17.481553+00:00`
- Mock mode was not used.

Structured JSON emitted by `validate_and_emit`

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

Files
- `assignment1-weather_unstructured_to_structured-airflow-success-run.png`
  Successful Airflow DAG run for `weather_unstructured_to_structured`.
- `assignment1-weather_unstructured_to_structured-fetch-weather-log.png`
  Evidence of the Open-Meteo fetch task using the assignment API request.
- `assignment1-weather_unstructured_to_structured-validate-and-emit-json.png`
  Final structured JSON emitted by `validate_and_emit`.
- `assignment1-weather_unstructured_to_structured-output-result.png`
  Clean screenshot of the final `validate_and_emit` structured JSON output.
- `assignment1-weather_unstructured_to_structured-open-webui-qwen.png`
  Docker Ollama evidence showing `qwen3.5:9b` is available.
- `assignment1-weather_unstructured_to_structured-runtime-status.png`
  Local runtime status showing the successful DAG run, Docker containers, and Ollama endpoint.
