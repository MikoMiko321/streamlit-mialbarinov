import logging

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from data.make_data import seasonal_temperatures
from services.open_weather_map import get_current_weather


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    logger = logging.getLogger(__name__)
    logger.info(f"Loading environment variables: {load_dotenv()}")

    st.markdown(
        """
        <style>
        /* весь текст */
        .stApp {
            font-family: 'Inter', sans-serif;
            font-size: 20px;
        }

        /* заголовки */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Inter', sans-serif;
            font-size: 32px;
            font-weight: 700;
        }
        /* кнопки */
        button {
            font-family: Inter, sans-serif !important;
            font-size: 20px !important;
        }

        /* selectbox */
        div[data-baseweb="select"] * {
            font-family: Inter, sans-serif !important;
            font-size: 20px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.set_page_config(layout="wide")

    st.title("Анализ температурных данных и мониторинг текущей температуры через OpenWeatherMap API")

    uploaded_file = st.file_uploader(
        "Загрузить погодные данные из фала",
        type="csv",
    )
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        st.write(data.describe(include="all"))
    cities = list(seasonal_temperatures.keys())
    city = st.selectbox("Выберите город: ", cities)
    if st.button("Get weather"):
        weather = get_current_weather(city)
        st.write(weather)
    # with st.sidebar:
    #     st.header("Настройки")
    #     city = st.selectbox("Город", ["Berlin", "Moscow", "Beijing"])
    #     api_key = st.text_input("OpenWeather API key", type="password")


if __name__ == "__main__":
    main()
