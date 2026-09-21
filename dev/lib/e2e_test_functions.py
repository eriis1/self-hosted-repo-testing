import logging


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def e2e_test():
    logging.info("This is a test function from lib/e2e_test_functions.py")
    return True
