import sys
import os
import logging


BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

file_handler = logging.FileHandler(
    'logs/' + sys.modules['__main__'].__file__.replace('.py', '.log'),
    mode='a',
    delay=0
)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # NOQA
file_handler.setFormatter(formatter)
LOGGER = logging.getLogger(
    sys.modules['__main__'].__file__.replace('.py', '.log')
)
LOGGER.addHandler(file_handler)
LOGGER.addHandler(logging.StreamHandler())
LOGGER.setLevel(logging.DEBUG)
