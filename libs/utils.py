import os
import re
import json
import random
import traceback
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


def get_hostname():
    hostname = os.uname()[1].lower()
    return hostname


def get_bot_number(hostname):
    return int(re.sub('[^0-9]', '', hostname))


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
    format_date = '{month}/{day}/{year}'.format(
        month=future_date.month, day=future_date.day, year=future_date.year)
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


def update_scraped_results(page, supplier, results, start_time, total_item):
    if not results:
        return False
    page.goto(settings.IMPORT_CURRENT_PRODUCT_SCRAPED_DATA_URL)
    # login
    page.fill("input[id=id_username]", settings.BUYBOT_USERNAME)
    page.fill("input[id=id_password]", settings.BUYBOT_PASSWORD)
    page.click("input[type=submit]")
    page.wait_for_timeout(5000)
    end_time = datetime.datetime.utcnow()
    start_time_str = start_time.strftime(settings.DATETIME_FORMAT)
    end_time_str = end_time.strftime(settings.DATETIME_FORMAT)
    file_name = f'{start_time_str}_{end_time_str}_{total_item}.txt'
    # fill form
    page.select_option("select[id=id_last_scraped_by]", str(settings.PLAYWRIGHT))  # NOQA
    page.select_option("select[id=id_supplier]", supplier)
    buffer = '\n'.join([json.dumps(row) for row in results])
    # Upload buffer from memory
    page.set_input_files(
        "input[id=id_file]",
        files=[
            {
                "name": file_name, "mimeType": "text/plain",
                "buffer": buffer.encode()
            }
        ],
    )
    page.click('button[class="btn btn-outline-primary"]')
    page.wait_for_timeout(random.randint(3000, 5000))
    print(page.url)


def find_value_by_markers(response, start_list, end_marker, to_end=False):
    """
    Returns the value found at the designated key. Iterates through the tree
    structure of the supplied JSON object drilling down one layer per item in
    the supplied list. An item in the ['product']['description'] field would be
    retrieved by calling this function with a keylist value of
      ['product', 'description']
    Returns None if any of the keys in the list are not found.
    """
    result = None
    start = 0

    # Handle scrapy responses as well as plain strings
    try:
        text = response.text()
    except AttributeError:  # Object doesn't have a text attribute
        text = response

    for value in start_list:
        offset = text[start:].find(value) + start
        if offset > -1:
            start = offset + len(value)
        else:
            start = -1
            break

    end = text[start:].find(end_marker) + start

    # If the to_end parameter is set to true then the end of the string
    # can be used when the end_marker is not found.
    if to_end and (end == -1):
        end = len(text)

    if (start != -1) and (end != -1):
        result = text[start:end]

    return result


def get_json_value_by_key_safely(data, keylist):
    for key in keylist:
        if data is not None:
            data = data.get(key, None)

    return data
