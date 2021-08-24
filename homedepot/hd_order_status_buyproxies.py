import random
import json
import time
import sys

from playwright.sync_api import sync_playwright
from libs.api import StlproAPI

from settings import (
    LOGGER, BUY_PROXIES_PASSWORD, BUY_PROXIES_USERNAME
)
import constants


def run(playwright, order):
    LOGGER.info(order)
    firefox = playwright.firefox
    browser = firefox.launch(
        headless=False,
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
                {"id": "newtab-container", "itemsToClear": [], "options": {}}],
            'devtools.toolbox.host': 'bottom'
        }
    )
    try:
        page = browser.new_page()
        page.set_default_navigation_timeout(60 * 1000)
        # Subscribe to "request" and "response" events.
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
        content = '''([x]) => {return fetch('/customer/order/v1/guest/orderdetailsgroup', {method: 'POST', body: '{"orderDetailsRequest": {"orderId": "%s", "emailId": "%s"}}', headers: {'Version': 'HTTP/1.0', 'Accept': 'application/json','Content-Type': 'application/json'}}).then(res => res.json());}'''  # NOQA
        content = content % (order['supplier_order_numbers_str'], order['user_email'])  # NOQA
        counter = 0
        data = ""
        while counter < 3:
            try:
                page.click("button[type=submit]")
                page.wait_for_timeout(5000)
                data = page.evaluate(content, [None])
            except Exception:
                time.sleep(5)
                counter += 1
            else:
                break
        if not data:
            raise Exception("Max retry times exceed!")
        result = StlproAPI().update_ds_order(order['id'], json.dumps(data))
        LOGGER.info(result)
        if result['status'] == 'success':
            return True
    except Exception as ex:
        LOGGER.exception(ex, exc_info=True)
        LOGGER.error("Failed: " + order['supplier_order_numbers_str'])

    browser.close()
    return False


if __name__ == "__main__":
    start = int(sys.argv[1])
    end = int(sys.argv[2])
    ips = StlproAPI().get_proxy_ips(
        supplier_id=constants.Supplier.HOMEDEPOT_CODE
    )['results']
    while True:
        orders = StlproAPI().get_ds_orders(constants.Supplier.HOMEDEPOT_CODE)
        orders = orders[start:end]
        random.shuffle(orders)
        for order in orders:
            LOGGER.info('============== Start {} =============='.format(
                order['supplier_order_numbers_str']
            ))
            random.shuffle(ips)
            random_ips = ips[:2]
            for ip in random_ips:
                order['ip'] = ip
                with sync_playwright() as playwright:
                    if run(playwright, order):
                        playwright.stop()
                        break
            time.sleep(5)

        time.sleep(60)
