import random
import re
import time
import sys

from playwright.sync_api import sync_playwright
from utils import LOGGER, get_ds_orders, update_ds_order

getDsOrdersUrl = "https://admin.stlpro.com/v2/ds_order/scrape_order_status/?supplier_id=W"


def run(playwright, order):
    LOGGER.info(order)
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
        page.wait_for_timeout(5000)
        pattern = re.search("window.__WML_REDUX_INITIAL_STATE__ = (.*?);<\/script>", page.content())
        data = pattern[0].replace('window.__WML_REDUX_INITIAL_STATE__ = ', '').replace(';</script>', '')
        result = update_ds_order(order['id'], data)
        if result['status'] == 'success':
            LOGGER.info("Success: " + order['supplier_order_numbers_str'])
    except Exception as ex:
        LOGGER.exception(ex, exc_info=True)
        LOGGER.error("Failed: " + order['supplier_order_numbers_str'])

    browser.close()
    LOGGER.info('======================= End ==========================')
    return


if __name__ == "__main__":
    start = int(sys.argv[1])
    end = int(sys.argv[2])
    while True:
        orders = get_ds_orders(getDsOrdersUrl)
        orders = orders[start:end]
        random.shuffle(orders)
        for order in orders:
            LOGGER.info('======================= Start ==========================')
            with sync_playwright() as playwright:
                run(playwright, order)
            time.sleep(5)

        time.sleep(60)
