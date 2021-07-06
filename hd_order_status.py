import random
import requests
import re
import base64
import json
import time
import sys

from playwright.sync_api import sync_playwright


getDsOrdersUrl = "https://admin.stlpro.com/v2/ds_order/scrape_order_status/?supplier_id=P"
updateDsOrderInfoUrl = "https://admin.stlpro.com/v2/ds_order/"


def get_ds_orders():
    url = getDsOrdersUrl
    response = requests.get(
        url,
        headers={
            "Authorization": "Basic " + base64.b64encode(b'buybot:forte1long').decode()
        }
    )
    return response.json()


def update_ds_order(ds_order_id, data):
    url = updateDsOrderInfoUrl + str(ds_order_id) + "/update_order_status_scraped_result/";
    response = requests.post(
        url,
        headers={
            "Authorization": "Basic " + base64.b64encode(b'buybot:forte1long').decode()
        },
        json={'data': data}
    )
    return response.json()


def run(playwright, order):
    chromium = playwright.chromium
    browser = chromium.launch(
        headless=False,
        proxy={
            "server": "zproxy.lum-superproxy.io:22225",
            "username": "lum-customer-c_62f63918-zone-residential2-country-us",
            "password": "bf1b7c15d2de"
        }
    )
    try:
        page = browser.new_page()
        page.set_default_navigation_timeout(60 * 1000)
        # Subscribe to "request" and "response" events.
        # page.on("request", lambda request: print(">>", request.method, request.url))
        # page.on("response", lambda response: print("<<", response.status, response.url))
        urls = [
            'https://www.homedepot.com/order/view/tracking',
        ]

        url = random.choice(urls)
        page.goto(url)
        page.wait_for_timeout(5000)
        page.fill("input[id=order]", order['supplier_order_numbers_str'])
        page.wait_for_timeout(1000)
        page.fill("input[id=email]", order['user_email'])
        page.wait_for_timeout(1000)
        page.click("button[type=submit]")
        page.wait_for_timeout(5000)

        content = '''([x]) => {return fetch('/customer/order/v1/guest/orderdetailsgroup', {method: 'POST', body: '{"orderDetailsRequest": {"orderId": "%s", "emailId": "%s"}}', headers: {'Accept': 'application/json','Content-Type': 'application/json'}}).then(res => res.json());}'''
        content = content % (order['supplier_order_numbers_str'], order['user_email'])
        data = page.evaluate(content, [None])
        print(data)
        print(update_ds_order(order['id'], json.dumps(data)))
    except Exception as ex:
        print(ex)

    browser.close()


if __name__ == "__main__":
    start = int(sys.argv[1])
    end = int(sys.argv[2])
    while True:
        orders = get_ds_orders()
        orders = orders[start:end]
        random.shuffle(orders)
        for order in orders:
            print(order)
            with sync_playwright() as playwright:
                run(playwright, order)
            time.sleep(5)

        time.sleep(60)
