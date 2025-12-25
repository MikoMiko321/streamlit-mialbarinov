import logging
import os

import requests
import streamlit as st

logger = logging.getLogger(__name__)


def get_current_weather(city: str) -> dict:
    api_key = os.getenv("OPEN_WEATHER_MAP_API_KEY") or st.secrets["OPEN_WEATHER_MAP_API_KEY"]
    if not api_key:
        raise RuntimeError("OPEN_WEATHER_MAP_API_KEY not set")
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",
    }

    resp = requests.get(url, params=params, timeout=10)
    logger.info(f"{params} {resp.status_code}")
    resp.raise_for_status()
    return resp.json()
