import base64
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

    # st.markdown(
    #     """
    #     <style>
    #     /* базовый текст всего приложения */
    #     .stApp {
    #         font-family: 'Inter', sans-serif;
    #         font-size: 20px;
    #     }

    #     /* заголовки */
    #     .stApp h1,
    #     .stApp h2,
    #     .stApp h3,
    #     .stApp h4,
    #     .stApp h5,
    #     .stApp h6 {
    #         font-family: 'Inter', sans-serif;
    #         font-size: 32px;
    #         font-weight: 700;
    #     }

    #     /* кнопки */
    #     .stButton > button {
    #         font-family: 'Inter', sans-serif !important;
    #         font-size: 20px !important;
    #     }

    #     /* selectbox: label + value */
    #     label,
    #     div[data-baseweb="select"] > div {
    #         font-family: 'Inter', sans-serif !important;
    #         font-size: 20px !important;
    #     }

    #     /* selectbox dropdown (portal!) */
    #     div[data-baseweb="popover"] * {
    #         font-family: 'Inter', sans-serif !important;
    #         font-size: 20px !important;
    #     }
    #     </style>
    #     """,
    #     unsafe_allow_html=True,
    # )
    # st.markdown(
    #     """
    #     <style>
    #     .stApp {
    #         background-image: url("https://images.unsplash.com/photo-1501785888041-af3ef285b470");
    #         background-size: cover;
    #         background-position: center;
    #         background-repeat: no-repeat;
    #         background-attachment: fixed;
    #     }
    #     </style>
    #     """,
    #     unsafe_allow_html=True,
    # )
    with open("data/bg_image.png", "rb") as f:
        bg_image = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        header[data-testid="stHeader"] {{ display:none; }}
        div[data-testid="stDecoration"] {{ display:none; }}
        div[data-testid="stAppViewContainer"] .block-container {{
            padding-top: 0rem;
            padding-bottom: 0rem;
        }}
        .stApp {{
            background-image: url("data:image/png;base64,{bg_image}");
            background-size: 200px 200px;
            /* background-size: auto;*/
            background-position: top left;
            background-repeat: repeat;
            background-attachment: scroll;
        }}
        /* заголовки */
        .stApp h1,
        .stApp h2,
        .stApp h3,
        .stApp h4,
        .stApp h5,
        .stApp h6 {{
        font-family: 'Inter', sans-serif;
        font-size: 34px; /* Here is the header font size!!*/
        font-weight: 700;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.set_page_config(
        page_title="Weather Analysis",
        page_icon="🌦️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

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
