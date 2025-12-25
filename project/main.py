import logging

from dotenv import load_dotenv


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    logger = logging.getLogger(__name__)
    logger.info(f"Loading environment variables: {load_dotenv()}")
    # print(get_current_weather("London"))


if __name__ == "__main__":
    main()
