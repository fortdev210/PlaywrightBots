import base64
import os
import re
import traceback
import requests
from datetime import date, timedelta, datetime

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
            "Authorization": "Basic " + base64.b64encode(bytes('{}:{}'.format(settings.BUYBOT_USERNAME, settings.BUYBOT_PASSWORD), encoding="raw_unicode_escape")).decode()  # NOQA
        }
    )
    return response.json()


def update_ds_order(ds_order_id, data):
    url = settings.UPDATE_DS_ORDER_INFO_URL.format(ds_order_id=ds_order_id)
    response = requests.post(
        url,
        headers={
            "Authorization": "Basic " + base64.b64encode(bytes('{}:{}'.format(settings.BUYBOT_USERNAME, settings.BUYBOT_PASSWORD), encoding="raw_unicode_escape")).decode()  # NOQA
        },
        json={'data': data, 'confirmed_by': settings.CONFIRMED_BY}
    )
    return response.json()


def get_proxy_ips(supplier_id):
    url = settings.GET_PROXIES_URL.format(supplier_id=supplier_id)
    response = requests.get(
        url,
        headers={
            "Authorization": "Basic " + base64.b64encode(bytes('{}:{}'.format(settings.BUYBOT_USERNAME, settings.BUYBOT_PASSWORD), encoding="raw_unicode_escape")).decode()  # NOQA
        }
    )
    return response.json()

def get_dsh_extension(target):
    if target.get('title') == 'STL Pro Dropship Helper' and target.get('type') == 'background_page':
        return True
    return False

def get_hostname():
    hostname = os.uname()[1].lower()
    return hostname

def get_bot_number(hostname):
    return int(re.sub('[^0-9]','',hostname))

def get_bot_username():
    hostname = get_hostname()
    bot_number = get_bot_number()
    if 'prior' in hostname or 'prep' in hostname:
        return settings.BUYBOT_USER
    elif 'rebuy' in hostname:
        if bot_number == 1:
            return 'buybot-rebuy'
        else:
            return 'buybot-rebuy2'
    else:
        return settings.BUYBOT_USER + str(bot_number)

def schedule_date():
    future_date = date.today() + timedelta(days=14)
    format_date = '{month}/{day}/{year}'.format(month=future_date.month, day=future_date.day, year=future_date.year)
    return format_date

def check_within_day_order(last_order_date):
    order_datetime = datetime.fromisoformat(last_order_date)
    order_date = order_datetime.date()
    today = date.today()
    delta = (today - order_date).days
    if delta > 1:
        return True
    else:
        return False