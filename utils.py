import base64
import traceback

import logging
import sys

import requests

file_handler = logging.FileHandler(
    'logs/' + sys.modules['__main__'].__file__.replace('.py', '.log'),
    mode='a',
    delay=0
)
LOGGER = logging.getLogger(
    sys.modules['__main__'].__file__.replace('.py', '.log')
)
LOGGER.addHandler(file_handler)
LOGGER.addHandler(logging.StreamHandler())
LOGGER.setLevel(logging.DEBUG)
UPDATE_DS_ORDER_INFO_URL = "https://admin.stlpro.com/v2/ds_order/"


def get_traceback_lines(ex, ex_traceback=None):
    if ex_traceback is None:
        ex_traceback = ex.__traceback__
    tb_lines = [
        line.rstrip('\n') for line in
        traceback.format_exception(ex.__class__, ex, ex_traceback)
    ]
    return tb_lines


def get_ds_orders(url):
    # url = getDsOrdersUrl
    response = requests.get(
        url,
        headers={
            "Authorization": "Basic " + base64.b64encode(b'buybot:forte1long').decode()  # NOQA
        }
    )
    return response.json()


def update_ds_order(ds_order_id, data):
    url = UPDATE_DS_ORDER_INFO_URL + str(ds_order_id) + "/update_order_status_scraped_result/"  # NOQA
    response = requests.post(
        url,
        headers={
            "Authorization": "Basic " + base64.b64encode(b'buybot:forte1long').decode()  # NOQA
        },
        json={'data': data, 'confirmed_by': 5}
    )
    return response.json()


def get_ips(url):
    response = requests.get(
        url,
        headers={
            "Authorization": "Basic " + base64.b64encode(b'buybot:forte1long').decode()  # NOQA
        }
    )
    return response.json()
