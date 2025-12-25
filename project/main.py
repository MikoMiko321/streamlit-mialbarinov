import logging

import streamlit as st
from dotenv import load_dotenv

from services.open_weather_map import get_current_weather


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    logger = logging.getLogger(__name__)
    logger.info(f"Loading environment variables: {load_dotenv()}")

    st.title("Weather app")

    if st.button("Get weather"):
        weather = get_current_weather("London")
        st.write(weather)


if __name__ == "__main__":
    main()
