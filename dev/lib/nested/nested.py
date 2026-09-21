import logging


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def e2e_test_nested():
    logging.info("This is a test function from lib/nested/nested.py")
    return True
