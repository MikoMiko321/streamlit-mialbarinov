import logging
import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

API_KEY = os.getenv("OPEN_WEATHER_MAP_API_KEY") or st.secrets["OPEN_WEATHER_MAP_API_KEY"]


def get_current_weather(city: str) -> dict:
    if not API_KEY:
        raise RuntimeError("OPEN_WEATHER_MAP_API_KEY not set")
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
    }

    resp = requests.get(url, params=params, timeout=10)
    logger.info(f"{params} {resp.status_code}")
    resp.raise_for_status()
    return resp.json()
