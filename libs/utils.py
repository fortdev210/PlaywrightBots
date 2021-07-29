import base64
import traceback
import requests
import settings
import os
import re
# hostname = os.uname()[1].lower()
hostname = 'wm-prep02'
bot_number = int(re.sub('[^0-9]','',hostname))

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

def get_orders_link():
    order_link = ''
    if 'prep' in hostname:
        order_link = settings.WALMART_PREP_ORDERS_LINK.format(bot_number=bot_number)
    elif 'buy' in hostname:
        order_link = settings.WALMART_BUY_ORDERS_LINK.format(bot_number=bot_number)
    elif 'prior' in hostname:
        order_link = settings.WALMART_PRIO_ORDERS_LINK
    else:
        order_link = settings.WALMART_REBUY_ORDERS_LINK.format(bot_number=bot_number)
    
    return order_link

def get_bot_username():
    if 'prior' in hostname or 'prep' in hostname:
        return settings.BUYBOT_USER
    elif 'rebuy' in hostname:
        if bot_number == 1:
            return 'buybot-rebuy'
        else:
            return 'buybot-rebuy2'
    else:
        return settings.BUYBOT_USER + str(bot_number)

def ds_us_states(): 
    return [
      {"name": "ALABAMA", "abbreviation": "AL" },
      {"name": "ALASKA", "abbreviation": "AK" },
      {"name": "AMERICAN SAMOA", "abbreviation": "AS" },
      {"name": "ARIZONA", "abbreviation": "AZ" },
      {"name": "ARKANSAS", "abbreviation": "AR" },
      {"name": "CALIFORNIA", "abbreviation": "CA" },
      {"name": "COLORADO", "abbreviation": "CO" },
      {"name": "CONNECTICUT", "abbreviation": "CT" },
      {"name": "DELAWARE", "abbreviation": "DE" },
      {"name": "DISTRICT OF COLUMBIA", "abbreviation": "DC" },
      {"name": "FEDERATED STATES OF MICRONESIA", "abbreviation": "FM" },
      {"name": "FLORIDA", "abbreviation": "FL" },
      {"name": "GEORGIA", "abbreviation": "GA" },
      {"name": "GUAM", "abbreviation": "GU" },
      {"name": "HAWAII", "abbreviation": "HI" },
      {"name": "IDAHO", "abbreviation": "ID" },
      {"name": "ILLINOIS", "abbreviation": "IL" },
      {"name": "INDIANA", "abbreviation": "IN" },
      {"name": "IOWA", "abbreviation": "IA" },
      {"name": "KANSAS", "abbreviation": "KS" },
      {"name": "KENTUCKY", "abbreviation": "KY" },
      {"name": "LOUISIANA", "abbreviation": "LA" },
      {"name": "MAINE", "abbreviation": "ME" },
      {"name": "MARSHALL ISLANDS", "abbreviation": "MH" },
      {"name": "MARYLAND", "abbreviation": "MD" },
      {"name": "MASSACHUSETTS", "abbreviation": "MA" },
      {"name": "MICHIGAN", "abbreviation": "MI" },
      {"name": "MINNESOTA", "abbreviation": "MN" },
      {"name": "MISSISSIPPI", "abbreviation": "MS" },
      {"name": "MISSOURI", "abbreviation": "MO" },
      {"name": "MONTANA", "abbreviation": "MT" },
      {"name": "NEBRASKA", "abbreviation": "NE" },
      {"name": "NEVADA", "abbreviation": "NV" },
      {"name": "NEW HAMPSHIRE", "abbreviation": "NH" },
      {"name": "NEW JERSEY", "abbreviation": "NJ" },
      {"name": "NEW MEXICO", "abbreviation": "NM" },
      {"name": "NEW YORK", "abbreviation": "NY" },
      {"name": "NORTH CAROLINA", "abbreviation": "NC" },
      {"name": "NORTH DAKOTA", "abbreviation": "ND" },
      {"name": "NORTHERN MARIANA ISLANDS", "abbreviation": "MP" },
      {"name": "OHIO", "abbreviation": "OH" },
      {"name": "OKLAHOMA", "abbreviation": "OK" },
      {"name": "OREGON", "abbreviation": "OR" },
      {"name": "PALAU", "abbreviation": "PW" },
      {"name": "PENNSYLVANIA", "abbreviation": "PA" },
      {"name": "PUERTO RICO", "abbreviation": "PR" },
      {"name": "RHODE ISLAND", "abbreviation": "RI" },
      {"name": "SOUTH CAROLINA", "abbreviation": "SC" },
      {"name": "SOUTH DAKOTA", "abbreviation": "SD" },
      {"name": "TENNESSEE", "abbreviation": "TN" },
      {"name": "TEXAS", "abbreviation": "TX" },
      {"name": "UTAH", "abbreviation": "UT" },
      {"name": "VERMONT", "abbreviation": "VT" },
      {"name": "VIRGIN ISLANDS", "abbreviation": "VI" },
      {"name": "VIRGINIA", "abbreviation": "VA" },
      {"name": "WASHINGTON", "abbreviation": "WA" },
      {"name": "WEST VIRGINIA", "abbreviation": "WV" },
      {"name": "WISCONSIN", "abbreviation": "WI" },
      {"name": "WYOMING", "abbreviation": "WY" },
    ]

def get_correct_state(state): 
    states = ds_us_states()
    state_map = {}
    for ds_state in states:
        state_map[ds_state.get('name')] = ds_state.get('abbreviation')

    state = state.replace(".", "").upper()
    if (len(state) > 2): 
        state = state_map[state]
    return state
  