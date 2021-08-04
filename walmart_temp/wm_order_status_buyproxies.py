import sys
import random
import time

from playwright.sync_api import sync_playwright
import constants
from libs.walmart import try_to_scrape_walmart_order
from libs.utils import get_ds_orders, update_ds_order, get_proxy_ips
from settings import (
    LOGGER, WALMART_PASSWORD, WALMART_OLD_PASSWORDS,
    BUY_PROXIES_PASSWORD, BUY_PROXIES_USERNAME
)


def run(playwright, order):
    LOGGER.info(order)
    firefox = playwright.firefox
    browser = firefox.launch(
        headless=False,
        devtools=True,
        proxy={
            "server": '{}:{}'.format(order['ip']['ip'], order['ip']['port']),
            "username": BUY_PROXIES_USERNAME,
            "password": BUY_PROXIES_PASSWORD
        },
        firefox_user_prefs={
            'media.peerconnection.enabled': False,
            'privacy.trackingprotection.enabled': True,
            'privacy.trackingprotection.socialtracking.enabled': True,
            'privacy.annotate_channels.strict_list.enabled': True,
            'privacy.donottrackheader.enabled': True,
            'privacy.sanitize.pending': [
                {"id": "newtab-container", "itemsToClear": [], "options":{}}
            ],
            'devtools.toolbox.host': 'bottom'
        }
    )
    try:
        page = browser.new_page()
        page.set_default_navigation_timeout(120000)
        data = try_to_scrape_walmart_order(
            order, page, WALMART_PASSWORD
        )
        if "signInWidget" in data:
            data = try_to_scrape_walmart_order(
                order, page, WALMART_OLD_PASSWORDS[0]
            )
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
    ips = get_proxy_ips(supplier_id=constants.Supplier.WALMART_CODE)['results']
    while True:
        orders = get_ds_orders(supplier_id=constants.Supplier.WALMART_CODE)
        orders = orders[start:end]
        random.shuffle(orders)
        for order in orders:
            LOGGER.info('================== Start ==================')
            random.shuffle(ips)
            random_ips = ips[:2]
            for ip in random_ips:
                order['ip'] = ip
                with sync_playwright() as playwright:
                    if run(playwright, order):
                        break
            time.sleep(5)

        time.sleep(60)
