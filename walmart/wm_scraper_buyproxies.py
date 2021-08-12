from datetime import datetime
import random
import sys
import time

from playwright.sync_api import sync_playwright

import constants
from settings import (
    LOGGER,
    BUY_PROXIES_PASSWORD, BUY_PROXIES_USERNAME
)

from libs.walmart.product_scraper import scrape_item
from libs.utils import get_proxy_ips, get_current_products, update_scraped_results


def run(playwright, random_ips, items):
    # LOGGER.info(order)
    start_time = datetime.utcnow()
    total_item = len(items)
    results = []
    firefox = playwright.firefox
    browser = firefox.launch(
        headless=False,
        proxy={
            "server": '{}:{}'.format(random_ips['ip'], random_ips['port']),
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
        }
    )
    try:
        page = browser.new_page()
        page.set_default_navigation_timeout(15000)
        for item in items:
            item['ip'] = ip['ip']
            try:
                result = scrape_item(page, item)
                if result:
                    results.append(result)
            except:
                continue
        update_scraped_results(
            page, constants.Supplier.WALMART_CODE, results,
            start_time, total_item
        )
        return True
    except Exception as ex:
        LOGGER.exception(ex, exc_info=True)
    browser.close()
    return False


if __name__ == "__main__":
    active = int(sys.argv[1])
    start = int(sys.argv[2])
    end = int(sys.argv[3])
    offset = int(start)
    limit = int(end) - int(start)
    ips = get_proxy_ips(supplier_id=constants.Supplier.WALMART_CODE)['results']
    while True:
        LOGGER.info('================== Start ==================')
        random.shuffle(ips)
        random_ips = ips[:2]
        items = get_current_products(
            constants.Supplier.WALMART_CODE, active, offset, limit
        )
        for ip in random_ips:
            with sync_playwright() as playwright:
                if run(playwright, ip, items):
                    break
        time.sleep(10)
