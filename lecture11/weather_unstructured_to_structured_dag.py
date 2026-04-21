"""
Lecture 11 - Airflow + Ollama
=============================

Weather ETL DAG:
1. Fetch raw Open-Meteo JSON
2. Send the raw payload to Ollama for schema-normalized JSON
3. Validate and emit the final structured payload

Designed for Dockerized Airflow on macOS, where Ollama is reachable at
http://host.docker.internal:11434 by default.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any

from airflow import DAG
from airflow.models import Variable

try:
    from airflow.providers.standard.operators.python import PythonOperator
except ImportError:
    try:
        from airflow.operators.python import PythonOperator
    except ImportError:
        from airflow.operators.python_operator import PythonOperator


logger = logging.getLogger(__name__)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
DEFAULT_OLLAMA_BASE_URL = "http://host.docker.internal:11434"
DEFAULT_OLLAMA_MODEL = "qwen3.5:9b"
DEFAULT_LATITUDE = "53.0736"
DEFAULT_LONGITUDE = "8.8064"
DEFAULT_OLLAMA_TIMEOUT_SECONDS = 600
HOURLY_POINTS_FOR_LLM = 6

REQUIRED_KEYS = [
    "latitude",
    "longitude",
    "current_time",
    "current_temperature_2m",
    "current_wind_speed_10m",
    "hourly_first_time",
    "hourly_first_temperature_2m",
    "hourly_first_relative_humidity_2m",
    "hourly_first_wind_speed_10m",
    "source",
]

WMO_SHORT_CONDITIONS = {
    0: "clear",
    1: "mainly clear",
    2: "partly cloudy",
    3: "overcast",
    45: "fog",
    48: "depositing rime fog",
    51: "light drizzle",
    53: "moderate drizzle",
    55: "dense drizzle",
    56: "light freezing drizzle",
    57: "dense freezing drizzle",
    61: "slight rain",
    63: "moderate rain",
    65: "heavy rain",
    66: "light freezing rain",
    67: "heavy freezing rain",
    71: "slight snow",
    73: "moderate snow",
    75: "heavy snow",
    77: "snow grains",
    80: "slight rain showers",
    81: "moderate rain showers",
    82: "violent rain showers",
    85: "slight snow showers",
    86: "heavy snow showers",
    95: "thunderstorm",
    96: "thunderstorm with slight hail",
    99: "thunderstorm with heavy hail",
}

default_args = {
    "owner": "data_engineering",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retry_delay": timedelta(minutes=2),
}


def _get_variable(name: str, default: str) -> str:
    return Variable.get(name, default_var=default)


def _coerce_float(value: Any, field_name: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Field '{field_name}' must be numeric, got {value!r}") from exc


def _coerce_int(value: Any, field_name: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Field '{field_name}' must be an integer, got {value!r}") from exc


def _coerce_float_list(values: Any, field_name: str) -> list[float]:
    if not isinstance(values, list) or not values:
        raise ValueError(f"Field '{field_name}' must be a non-empty list")
    return [_coerce_float(value, f"{field_name}[]") for value in values]


def _coerce_string_list(values: Any, field_name: str) -> list[str]:
    if not isinstance(values, list) or not values:
        raise ValueError(f"Field '{field_name}' must be a non-empty list")
    output: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Field '{field_name}' must contain non-empty strings")
        output.append(value)
    return output


def _compact_open_meteo_payload(raw_payload_text: str) -> str:
    raw_payload = json.loads(raw_payload_text)
    hourly = raw_payload.get("hourly", {})
    compact_hourly = {}

    for key in ("time", "temperature_2m", "relative_humidity_2m", "wind_speed_10m"):
        values = hourly.get(key)
        if isinstance(values, list):
            compact_hourly[key] = values[:HOURLY_POINTS_FOR_LLM]

    compact_payload = {
        "latitude": raw_payload.get("latitude"),
        "longitude": raw_payload.get("longitude"),
        "current": raw_payload.get("current", {}),
        "hourly": compact_hourly,
    }
    return json.dumps(compact_payload, ensure_ascii=False)


def _build_mock_structured_payload(raw_payload_text: str) -> str:
    raw_payload = json.loads(raw_payload_text)
    current = raw_payload.get("current", {})
    hourly = raw_payload.get("hourly", {})

    structured = {
        "latitude": _coerce_float(raw_payload.get("latitude"), "latitude"),
        "longitude": _coerce_float(raw_payload.get("longitude"), "longitude"),
        "current_time": current.get("time"),
        "current_temperature_2m": _coerce_float(
            current.get("temperature_2m"), "current.temperature_2m"
        ),
        "current_wind_speed_10m": _coerce_float(
            current.get("wind_speed_10m"), "current.wind_speed_10m"
        ),
        "hourly_first_time": _coerce_string_list(
            (hourly.get("time") or [])[:1], "hourly.time"
        )[0],
        "hourly_first_temperature_2m": _coerce_float_list(
            (hourly.get("temperature_2m") or [])[:1], "hourly.temperature_2m"
        )[0],
        "hourly_first_relative_humidity_2m": _coerce_float_list(
            (hourly.get("relative_humidity_2m") or [])[:1], "hourly.relative_humidity_2m"
        )[0],
        "hourly_first_wind_speed_10m": _coerce_float_list(
            (hourly.get("wind_speed_10m") or [])[:1], "hourly.wind_speed_10m"
        )[0],
        "source": "open-meteo",
    }
    if not isinstance(structured["current_time"], str) or not structured["current_time"].strip():
        raise ValueError("Field 'current_time' must be a non-empty string")
    return json.dumps(structured, ensure_ascii=False)


def fetch_weather(**context: Any) -> str:
    import requests

    latitude = _get_variable("weather_latitude", DEFAULT_LATITUDE)
    longitude = _get_variable("weather_longitude", DEFAULT_LONGITUDE)

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,wind_speed_10m",
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m",
    }

    logger.info("Fetching Open-Meteo weather data with params=%s", params)
    response = requests.get(OPEN_METEO_URL, params=params, timeout=30)
    response.raise_for_status()

    payload = response.json()
    payload_text = json.dumps(payload, ensure_ascii=False)
    logger.info("Fetched Open-Meteo payload successfully (%d chars)", len(payload_text))
    return payload_text


def ollama_to_structured(**context: Any) -> str:
    import requests

    ti = context["ti"]
    raw_payload_text = ti.xcom_pull(task_ids="fetch_weather")
    if not raw_payload_text:
        raise ValueError("No raw weather payload found in XCom from fetch_weather")

    if os.getenv("WEATHER_PIPELINES_MOCK_OLLAMA") == "1":
        logger.info("WEATHER_PIPELINES_MOCK_OLLAMA=1 set; skipping Ollama HTTP call")
        return _build_mock_structured_payload(raw_payload_text)

    ollama_base_url = _get_variable("ollama_base_url", DEFAULT_OLLAMA_BASE_URL).rstrip("/")
    ollama_model = _get_variable("ollama_model", DEFAULT_OLLAMA_MODEL)
    ollama_timeout_seconds = int(
        os.getenv("WEATHER_PIPELINES_OLLAMA_TIMEOUT_SECONDS", str(DEFAULT_OLLAMA_TIMEOUT_SECONDS))
    )
    compact_payload_text = _compact_open_meteo_payload(raw_payload_text)

    prompt = f"""
Return only JSON.
Do not include Markdown.
Do not include explanation text.
Do not include any keys other than these exact keys:
latitude, longitude, current_time, current_temperature_2m, current_wind_speed_10m, hourly_first_time, hourly_first_temperature_2m, hourly_first_relative_humidity_2m, hourly_first_wind_speed_10m, source

Rules:
- source must be exactly "open-meteo"
- latitude, longitude, current_temperature_2m, current_wind_speed_10m must be numbers
- hourly_first_time must be the first value from hourly.time
- hourly_first_temperature_2m must be the first value from hourly.temperature_2m
- hourly_first_relative_humidity_2m must be the first value from hourly.relative_humidity_2m
- hourly_first_wind_speed_10m must be the first value from hourly.wind_speed_10m
- use only the payload provided below; it has already been compacted to the first {HOURLY_POINTS_FOR_LLM} hourly entries

Raw Open-Meteo payload:
{compact_payload_text}
""".strip()

    request_body = {
        "model": ollama_model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "format": "json",
        "think": False,
        "options": {"temperature": 0},
    }

    logger.info(
        "Calling Ollama at %s/api/chat with model=%s timeout=%ss using %d hourly points",
        ollama_base_url,
        ollama_model,
        ollama_timeout_seconds,
        HOURLY_POINTS_FOR_LLM,
    )
    response = requests.post(
        f"{ollama_base_url}/api/chat",
        json=request_body,
        timeout=ollama_timeout_seconds,
    )
    response.raise_for_status()

    body = response.json()
    message = body.get("message", {})
    content = message.get("content")
    if not content:
        raise ValueError(f"Ollama response did not include message.content: {body}")

    logger.info("Received structured response from Ollama (%d chars)", len(content))
    return content


def validate_and_emit(**context: Any) -> dict[str, Any]:
    ti = context["ti"]
    model_output = ti.xcom_pull(task_ids="ollama_to_structured")
    if not model_output:
        raise ValueError("No model output found in XCom from ollama_to_structured")

    try:
        data = json.loads(model_output)
    except json.JSONDecodeError as exc:
        logger.error("Model output is not valid JSON: %s", model_output)
        raise ValueError("Model output is not valid JSON") from exc

    missing = [key for key in REQUIRED_KEYS if key not in data]
    if missing:
        raise ValueError(f"Missing required keys: {missing}")

    for key in ("current_time", "source"):
        value = data.get(key)
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValueError(f"Field '{key}' must not be empty")

    data["latitude"] = _coerce_float(data["latitude"], "latitude")
    data["longitude"] = _coerce_float(data["longitude"], "longitude")
    data["current_temperature_2m"] = _coerce_float(
        data["current_temperature_2m"], "current_temperature_2m"
    )
    data["current_wind_speed_10m"] = _coerce_float(
        data["current_wind_speed_10m"], "current_wind_speed_10m"
    )
    if not isinstance(data["hourly_first_time"], str) or not data["hourly_first_time"].strip():
        raise ValueError("Field 'hourly_first_time' must be a non-empty string")
    data["hourly_first_temperature_2m"] = _coerce_float(
        data["hourly_first_temperature_2m"], "hourly_first_temperature_2m"
    )
    data["hourly_first_relative_humidity_2m"] = _coerce_float(
        data["hourly_first_relative_humidity_2m"], "hourly_first_relative_humidity_2m"
    )
    data["hourly_first_wind_speed_10m"] = _coerce_float(
        data["hourly_first_wind_speed_10m"], "hourly_first_wind_speed_10m"
    )

    if data["source"] != "open-meteo":
        raise ValueError(f"Field 'source' must be 'open-meteo', got {data['source']!r}")

    logger.info("Validated structured weather JSON:\n%s", json.dumps(data, indent=2, ensure_ascii=False))
    return data


dag = DAG(
    dag_id="weather_unstructured_to_structured",
    default_args=default_args,
    description="Fetch Open-Meteo JSON, transform with Ollama, validate a fixed schema",
    schedule=None,
    start_date=datetime(2026, 4, 1, tzinfo=timezone.utc),
    catchup=False,
    tags=["lecture11", "airflow", "ollama", "weather"],
)

fetch_weather_task = PythonOperator(
    task_id="fetch_weather",
    python_callable=fetch_weather,
    retries=2,
    dag=dag,
)

ollama_to_structured_task = PythonOperator(
    task_id="ollama_to_structured",
    python_callable=ollama_to_structured,
    retries=2,
    dag=dag,
)

validate_and_emit_task = PythonOperator(
    task_id="validate_and_emit",
    python_callable=validate_and_emit,
    retries=0,
    dag=dag,
)

fetch_weather_task >> ollama_to_structured_task >> validate_and_emit_task
