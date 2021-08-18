import re
import json

from walmart.walmart_base import WalmartBase
from libs.api import STLPRO_API
from constants import Supplier, EmailStatus
from settings import LOGGER


class WmEmailVerifier(WalmartBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.email = kwargs.get('email')

    @staticmethod
    def get_order_data(page):
        pattern = re.search(
            "window.__WML_REDUX_INITIAL_STATE__ = (.*?);<\/script>",  # NOQA
            page.content()
        )
        data = pattern[1].replace(
            'window.__WML_REDUX_INITIAL_STATE__ = ', ''
        ).replace(';</script>', '')
        orders_json = json.loads(data)
        orders = orders_json['recentOrders']['orders']
        return orders

    @staticmethod
    def check_order_canceled(orders):
        for order in reversed(orders):
            order_status = order['superGroups'][0]['groupType']
            total_price = order['total']
            is_total_zero = float(total_price.replace('$', '')) == 0.0
            if is_total_zero and order_status == 'canceled':
                return True
        return False

    def remove_items_in_cart(self):
        try:
            self.wait_element_loading(
                '[data-automation-id="cart-item-remove"]')
        except Exception:
            LOGGER.info('Empty Cart')
        self.sleep(1000)

    def run(self):
        self.open_sign_up_page()
        self.signin_walmart(self.email)
        self.open_order_history()
        order_data = self.get_order_data(self.page)
        is_canceled = self.check_order_canceled(order_data)
        if is_canceled:
            LOGGER.info('Order is canceled. Marking as banned.')
            STLPRO_API().update_email_status(self.email, EmailStatus.BANNED)
        else:
            LOGGER.info('Checking cart and removing items in the cart.')
            self.open_cart_page()


if __name__ == '__main__':
    emails = STLPRO_API().get_email_supplier()
    proxies = STLPRO_API().get_proxy_ips(Supplier.WALMART_CODE)
    proxy_ip = proxies[0].get('ip')
    proxy_port = proxies[0].get('port')
    email = emails[0].get('email_value')
    bot = WmEmailVerifier(use_chrome=False, use_proxy=True,
                          proxy_ip=proxy_ip, proxy_port=proxy_port,
                          email=email)
    bot.run()
