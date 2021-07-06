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


getProxiesUrl = "https://admin.stlpro.com/v2/ip_supplier/?is_potential_banned=false&is_buyproxies_ip=true&supplier=P&limit=500";


def get_ips():
    url = getProxiesUrl
    response = requests.get(
        url,
        headers={
            "Authorization": "Basic " + base64.b64encode(b'buybot:forte1long').decode()
        }
    )
    return response.json()


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


def run(playwright, order, ip):
    chromium = playwright.chromium
    browser = chromium.launch(
        headless=False,
        proxy={
            "server": '{}:{}'.format(ip['ip'], ip['port']),
            "username": "stlpro",
            "password": "forte1"
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
        result = update_ds_order(order['id'], json.dumps(data))
        print(result)
        if result['status'] == 'success':
            return True
    except Exception as ex:
        print(ex)

    browser.close()
    return False


if __name__ == "__main__":
    start = int(sys.argv[1])
    end = int(sys.argv[2])
    ips = get_ips()['results']
    while True:
        orders = get_ds_orders()
        orders = orders[start:end]
        random.shuffle(orders)
        for order in orders:
            random.shuffle(ips)
            random_ips = ips[:2]
            print(order)
            for ip in random_ips:
                print(ip)
                with sync_playwright() as playwright:
                    if run(playwright, order, ip):
                        break
            time.sleep(5)

        time.sleep(60)
