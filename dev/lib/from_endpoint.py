import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def testing():
    logging.info("This is a test function from custom_functions.py")
    return "This is a test function from custom_functions.py"