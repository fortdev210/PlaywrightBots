import sys
import random
import time

from playwright.sync_api import sync_playwright
from settings import (
    LOGGER, WALMART, WM_CURRENT_PASSWORD, WM_OLD_PASSWORD,
    PROXY_PASS, PROXY_USER
)
from libs.walmart import try_to_scrape
from libs.utils import get_ds_orders, update_ds_order, get_proxy_ips


def run(playwright, order, ip):
    LOGGER.info(order)
    chromium = playwright.chromium
    browser = chromium.launch(
        headless=False,
        proxy={
            "server": '{}:{}'.format(ip['ip'], ip['port']),
            "username": PROXY_USER,
            "password": PROXY_PASS
        }
    )
    try:
        page = browser.new_page()
        page.set_default_navigation_timeout(60 * 1000)
        # Subscribe to "request" and "response" events.
        # page.on("request", lambda request: print(">>", request.method, request.url))  # NOQA
        # page.on("response", lambda response: print("<<", response.status, response.url))  # NOQA
        data = try_to_scrape(order, page, WM_CURRENT_PASSWORD)
        if "signInWidget" in data:
            data = try_to_scrape(order, page, WM_OLD_PASSWORD)
        result = update_ds_order(order['id'], data)
        LOGGER.info(result)
        return True
    except Exception as ex:
        LOGGER.exception(ex, exc_info=True)
        LOGGER.error("Failed: " + order['supplier_order_numbers_str'])
    browser.close()
    return False


if __name__ == "__main__":
    start = int(sys.argv[1])
    end = int(sys.argv[2])
    ips = get_proxy_ips(supplier_id=WALMART)['results']
    while True:
        orders = get_ds_orders(supplier_id=WALMART)
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
