import random
import requests
import re
import base64
import json
import time
import sys

from playwright.sync_api import sync_playwright


getDsOrdersUrl = "https://admin.stlpro.com/v2/ds_order/scrape_order_status/?supplier_id=W"
updateDsOrderInfoUrl = "https://admin.stlpro.com/v2/ds_order/"


getProxiesUrl = "https://admin.stlpro.com/v2/ip_supplier/?is_potential_banned=false&is_buyproxies_ip=true&supplier=W&limit=500";


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
            'https://www.walmart.com/account/login',
            'https://www.walmart.com/account/login?tid=0&returnUrl=%2F',
            'https://www.walmart.com/account/login?tid=0&returnUrl=%2Fcp%2Felectronics%2F3944',
            'https://www.walmart.com/account/login?tid=0&returnUrl=%2Fbrowse%2Felectronics%2Ftouchscreen-laptops%2F3944_3951_1089430_1230091_1101633',
            'https://www.walmart.com/account/login?tid=0&returnUrl=%2Flists',
            'https://www.walmart.com/account/login?tid=0&returnUrl=%2Feasyreorder%3FeroType%3Dlist',

        ]
        url = random.choice(urls)
        page.goto(url)
        page.wait_for_timeout(5000)
        email = order['email'] or order['username']
        page.fill("input[id=email]", email)
        page.wait_for_timeout(1000)
        page.fill("input[id=password]", 'Forte1long!')
        page.wait_for_timeout(1000)
        page.click("button[type=submit]")
        page.wait_for_timeout(5000)
        try:
            page.goto('https://www.walmart.com/account/wmpurchasehistory', wait_until="networkidle")
        except:
            pass
        page.wait_for_timeout(20000)
        pattern = re.search("window.__WML_REDUX_INITIAL_STATE__ = (.*?);<\/script>", page.content())
        data = pattern[0].replace('window.__WML_REDUX_INITIAL_STATE__ = ', '').replace(';</script>', '')
        result = update_ds_order(order['id'], data)
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
