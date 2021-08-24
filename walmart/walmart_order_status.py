import random
import re

import constants
from .walmart_base import WalmartBase
from settings import (
    LOGGER, WALMART_SELF_RESOLVE_CAPTCHA
)
from libs.api import StlproAPI


class WalmartOrderStatus(WalmartBase):
    WALMART_PURCHASE_HISTORY_LINK = \
        "https://www.walmart.com/account/wmpurchasehistory"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start = kwargs.get('start')
        self.end = kwargs.get('end')

    @staticmethod
    def get_order_data(page):
        pattern = re.search(
            "window.__WML_REDUX_INITIAL_STATE__ = (.*?);<\/script>",  # NOQA
            page.content()
        )
        data = pattern[0].replace(
            'window.__WML_REDUX_INITIAL_STATE__ = ', ''
        ).replace(';</script>', '')
        return data

    def try_to_scrape_walmart_order(self, order):
        self.order_info = order
        url = self.get_random_url()
        self.open_new_page()
        self.go_to_link(url)
        self.sleep(3)
        self.signin_walmart()
        if self.captcha_detected():
            LOGGER.error("[Captcha] get {}".format(self.order['ip']['ip']))
            if WALMART_SELF_RESOLVE_CAPTCHA:
                self.resolve_captcha(order['ip']['ip'])
        else:
            LOGGER.info("[Captcha] none {}".format(order['ip']['ip']))

        self.go_to_link(self.WALMART_PURCHASE_HISTORY_LINK)
        self.sleep(random.randint(5, 10))
        data = self.get_order_data(self.page)
        return data

    def scrape_orders_state(self):
        orders = StlproAPI().get_ds_orders(
            supplier_id=constants.Supplier.WALMART_CODE)

        ips = StlproAPI().get_proxy_ips(
            supplier_id=constants.Supplier.WALMART_CODE)['results']
        orders = orders[self.start:self.end]
        random.shuffle(orders)
        for order in orders:
            LOGGER.info('================== Start ==================')
            random.shuffle(ips)
            random_ips = ips[:2]
            for ip in random_ips:
                order['ip'] = ip
                try:
                    self.create_browser()
                    data = self.try_to_scrape_walmart_order(order)
                    result = StlproAPI().update_ds_order(order['id'], data)
                    LOGGER.info(result)
                except Exception as e:
                    LOGGER.exception(e, exc_info=True)
                    LOGGER.error(
                        "Failed: " + order['supplier_order_numbers_str'])
                self.close_browser()
                self.sleep(5)
