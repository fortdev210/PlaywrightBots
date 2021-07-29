import sys
import time
import random

from playwright.sync_api import sync_playwright
from settings import (
    LOGGER, WALMART, LUMINATI_PASSWORD, LUMINATI_DOMAIN,
    LUMINATI_USERNAME, WM_CURRENT_PASSWORD, WM_OLD_PASSWORD
)
from libs.walmart_order_status import try_to_scrape_walmart_order
from libs.utils import get_ds_orders, update_ds_order


def run(playwright, order):
    LOGGER.info(order)
    chromium = playwright.chromium
    browser = chromium.launch(
        headless=False,
        proxy={
            "server": LUMINATI_DOMAIN,
            "username": LUMINATI_USERNAME,
            "password": LUMINATI_PASSWORD
        }
    )
    try:
        page = browser.new_page()
        page.set_default_navigation_timeout(60 * 1000)
        # Subscribe to "request" and "response" events.
        # page.on("request", lambda request: print(">>", request.method, request.url))  # NOQA
        # page.on("response", lambda response: print("<<", response.status, response.url))  # NOQA
        data = try_to_scrape_walmart_order(order, page, WM_CURRENT_PASSWORD)
        if "signInWidget" in data:
            data = try_to_scrape_walmart_order(order, page, WM_OLD_PASSWORD)
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
    while True:
        orders = get_ds_orders(supplier_id=WALMART)
        orders = orders[start:end]
        random.shuffle(orders)
        for order in orders:
            LOGGER.info('================== Start ==================')
            with sync_playwright() as playwright:
                run(playwright, order)
            time.sleep(5)

        time.sleep(60)
