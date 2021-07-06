import base64
import traceback
import requests
import settings


def get_traceback_lines(ex, ex_traceback=None):
    if ex_traceback is None:
        ex_traceback = ex.__traceback__
    tb_lines = [
        line.rstrip('\n') for line in
        traceback.format_exception(ex.__class__, ex, ex_traceback)
    ]
    return tb_lines


def get_ds_orders(supplier_id):
    url = settings.GET_DS_ORDERS_URL.format(supplier_id=supplier_id)
    response = requests.get(
        url,
        headers={
            "Authorization": "Basic " + base64.b64encode(bytes('{}:{}'.format(settings.BUYBOT_USER, settings.BUYBOT_PASS), encoding="raw_unicode_escape")).decode()  # NOQA
        }
    )
    return response.json()


def update_ds_order(ds_order_id, data):
    url = settings.UPDATE_DS_ORDER_INFO_URL.format(ds_order_id=ds_order_id)
    response = requests.post(
        url,
        headers={
            "Authorization": "Basic " + base64.b64encode(bytes('{}:{}'.format(settings.BUYBOT_USER, settings.BUYBOT_PASS), encoding="raw_unicode_escape")).decode()  # NOQA
        },
        json={'data': data, 'confirmed_by': settings.CONFIRMED_BY}
    )
    return response.json()


def get_proxy_ips(supplier_id):
    url = settings.GET_PROXIES_URL.format(supplier_id=supplier_id)
    response = requests.get(
        url,
        headers={
            "Authorization": "Basic " + base64.b64encode(bytes('{}:{}'.format(settings.BUYBOT_USER, settings.BUYBOT_PASS), encoding="raw_unicode_escape")).decode()  # NOQA
        }
    )
    return response.json()
