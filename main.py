import base64
import logging
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
from dotenv import load_dotenv

import services.open_weather_map as owm

st.set_page_config(
    page_title="Погода ВШЭ ФКН",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def validate_api_key():
    owm.API_KEY = st.session_state["api_key_input"]
    try:
        owm.get_current_weather("Moscow")
        st.sidebar.success("Введен новый АПИ-ключ")
    except requests.HTTPError as e:
        owm.API_KEY = None
        st.sidebar.error(e.response.json())
        return


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    logger = logging.getLogger(__name__)
    logger.info(f"Loading environment variables: {load_dotenv()}")

    with open("data/bg_image.png", "rb") as f:
        bg_image = base64.b64encode(f.read()).decode()

    # Это всякая косметическая разметка страницы по подсказкам чата ГПТ
    # header[data-testid="stHeader"] {{ display:none; }}
    # div[data-testid="stDecoration"] {{ display:none; }}
    st.markdown(
        f"""
        <style>
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
        /* sidebar title */
        [data-testid="stSidebar"] h1 {{
            padding-top: 0;
            margin-top: 0;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("Анализ температурных данных и мониторинг текущей температуры через OpenWeatherMap API")

    # Все начинается с загрузки файла
    uploaded_file = st.file_uploader(
        "Загрузить погодные данные из фала",
        type="csv",
    )
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        # st.write(data.describe(include="all"))
        # cities = list(seasonal_temperatures.keys())
        cities = sorted(data["city"].unique())
        # Блок выбора города и текущей погоды для него
        city = st.selectbox("Выберите город: ", cities)
        city_data = data[data["city"] == city]
        city_data["timestamp"] = pd.to_datetime(city_data["timestamp"])
        date_from = city_data["timestamp"].min()
        date_to = city_data["timestamp"].max()
        # Общая информация
        # средняя температура и стандартное отклонение для каждого сезона в каждом городе.
        season_stats = (
            data.groupby(["city", "season"])["temperature"].agg(mean_temp="mean", std_temp="std").reset_index()
        )
        st.write(f"Период наблюдений для города {city}: {date_from} — {date_to}")
        st.write("Общие данные")
        st.dataframe(city_data.describe(include="all"))
        st.write("Сезонный профиль")
        st.dataframe(season_stats[season_stats["city"] == city])

        # Анализ временных рядов
        city_data = city_data.sort_values("timestamp")
        window = 30
        city_data["roll_mean"] = city_data["temperature"].rolling(window).mean()
        city_data["roll_std"] = city_data["temperature"].rolling(window).std()
        city_data["upper"] = city_data["roll_mean"] + 2 * city_data["roll_std"]
        city_data["lower"] = city_data["roll_mean"] - 2 * city_data["roll_std"]
        city_data["anomaly"] = (city_data["temperature"] > city_data["upper"]) | (
            city_data["temperature"] < city_data["lower"]
        )
        # Построение графика
        st.write("Анализ временных рядов")
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=city_data["timestamp"],
                y=city_data["temperature"],
                mode="lines",
                name="Температура",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=city_data["timestamp"],
                y=city_data["roll_mean"],
                mode="lines",
                name="Скользящее среднее (30 дней)",
            )
        )
        anoms = city_data[city_data["anomaly"]]
        fig.add_trace(
            go.Scatter(
                x=anoms["timestamp"],
                y=anoms["temperature"],
                mode="markers",
                name="Аномалии",
            )
        )
        st.plotly_chart(fig, use_container_width=True)

        # Тренды
        st.write("Долгосрочные тренды изменения температуры")
        window = 365
        city_data["roll_mean_365"] = city_data["temperature"].rolling(window, center=True).mean()
        # Найдем среднегодовые температуры
        yearly_avg_temp = city_data.set_index("timestamp").resample("Y")["temperature"].mean().reset_index()
        yearly_avg_temp["timestamp"] -= pd.Timedelta(days=182)
        # st.write(str(yearly_avg_temp))
        # Построим тренд на основе среднегодовых температур
        x = np.arange(len(yearly_avg_temp))
        k, b = np.polyfit(x, yearly_avg_temp["temperature"], 1)
        yearly_avg_temp["trend"] = k * x + b

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=yearly_avg_temp["timestamp"],
                y=yearly_avg_temp["temperature"],
                mode="lines",
                name="Cреднегодовая температура",
                # line=dict(width=4),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=city_data["timestamp"],
                y=city_data["roll_mean_365"],
                name="Скользящее среднее (365 дней)",
                mode="lines",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=yearly_avg_temp["timestamp"],
                y=yearly_avg_temp["trend"],
                mode="lines",
                name="Долгосрочный тренд",
                # line=dict(width=3),
            )
        )

        st.plotly_chart(fig, use_container_width=True)

        if st.button("Получить текущие данные о погоде"):
            weather = owm.get_current_weather(city)
            temp = weather["main"]["temp"]
            city = weather["name"]
            date = datetime.now().date()
            st.write(f"Температура {city} {date}: {temp} °C")
            month = date.month
            if month in [12, 1, 2]:
                season = "winter"
            elif month in [3, 4, 5]:
                season = "spring"
            elif month in [6, 7, 8]:
                season = "summer"
            else:
                season = "autumn"
            row = season_stats[(season_stats["city"] == city) & (season_stats["season"] == season)]
            mean = row["mean_temp"].iloc[0]
            std = row["std_temp"].iloc[0]
            st.dataframe(row)
            if temp > mean + 2 * std or temp < mean - 2 * std:
                st.write("Температура является аномальной")
            else:
                st.write("Температура в пределах 2σ")
            # st.write(weather)

    # Сайдбар, где мы настраиваем АПИ ключ
    st.sidebar.title("Настройки")
    st.sidebar.text_input(
        "АПИ-ключ",
        type="password",
        value=owm.API_KEY,
        key="api_key_input",
        on_change=validate_api_key,
    )


if __name__ == "__main__":
    main()
