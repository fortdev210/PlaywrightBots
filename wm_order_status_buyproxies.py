import random
import re
import time
import sys

from playwright.sync_api import sync_playwright
from utils import LOGGER, get_ds_orders, update_ds_order, get_ips


getDsOrdersUrl = "https://admin.stlpro.com/v2/ds_order/scrape_order_status/?supplier_id=W"  # NOQA
getProxiesUrl = "https://admin.stlpro.com/v2/ip_supplier/?is_potential_banned=false&is_buyproxies_ip=true&supplier=W&limit=500&batch_id=order_status"  # NOQA


def try_to_scrape(order, page, password):
    LOGGER.info("Login with pass: " + password)
    urls = [
        'https://www.walmart.com/account/login',
        'https://www.walmart.com/account/login?tid=0&returnUrl=%2F',
        'https://www.walmart.com/account/login?tid=0&returnUrl=%2Fcp%2Felectronics%2F3944',  # NOQA
        'https://www.walmart.com/account/login?tid=0&returnUrl=%2Fbrowse%2Felectronics%2Ftouchscreen-laptops%2F3944_3951_1089430_1230091_1101633',  # NOQA
        'https://www.walmart.com/account/login?tid=0&returnUrl=%2Flists',
        'https://www.walmart.com/account/login?tid=0&returnUrl=%2Feasyreorder%3FeroType%3Dlist',  # NOQA

    ]
    url = random.choice(urls)
    page.goto(url)
    page.wait_for_timeout(5000)
    email = order['email'] or order['username']
    page.fill("input[id=email]", email)
    page.wait_for_timeout(1000)
    page.fill("input[id=password]", password)
    page.wait_for_timeout(1000)
    page.click("button[type=submit]")
    page.wait_for_timeout(5000)
    try:
        page.goto(
            'https://www.walmart.com/account/wmpurchasehistory',
            wait_until="networkidle"
        )
    except:
        pass
    page.wait_for_timeout(10000)
    pattern = re.search(
        "window.__WML_REDUX_INITIAL_STATE__ = (.*?);<\/script>",
        page.content()
    )
    data = pattern[0].replace(
        'window.__WML_REDUX_INITIAL_STATE__ = ', ''
    ).replace(';</script>', '')
    return data


def run(playwright, order, ip):
    LOGGER.info(order)
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
        # page.on("request", lambda request: print(">>", request.method, request.url))  # NOQA
        # page.on("response", lambda response: print("<<", response.status, response.url))  # NOQA
        data = try_to_scrape(order, page, 'Forte1long!')
        if "signInWidget" in data:
            data = try_to_scrape(order, page, 'forte1long')
        result = update_ds_order(order['id'], data)
        LOGGER.info(result)
    except Exception as ex:
        LOGGER.exception(ex, exc_info=True)
        LOGGER.error("Failed: " + order['supplier_order_numbers_str'])
    browser.close()
    LOGGER.info('================== End ==================')
    return


if __name__ == "__main__":
    start = int(sys.argv[1])
    end = int(sys.argv[2])
    ips = get_ips(getProxiesUrl)['results']
    while True:
        orders = get_ds_orders(getDsOrdersUrl)
        orders = orders[start:end]
        random.shuffle(orders)
        for order in orders:
            LOGGER.info('================== Start ==================')
            random.shuffle(ips)
            random_ips = ips[:2]
            for ip in random_ips:
                order['ip'] = ip
                with sync_playwright() as playwright:
                    if run(playwright, order, ip):
                        break
            time.sleep(5)

        time.sleep(60)
