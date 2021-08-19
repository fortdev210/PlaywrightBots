import re
import json
import random
from datetime import datetime

from walmart.walmart_base import WalmartBase
from libs.api import STLPRO_API
from constants import Supplier, EmailStatus
from settings import LOGGER, DATETIME_FORMAT


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
        if pattern:
            data = pattern[1].replace(
                'window.__WML_REDUX_INITIAL_STATE__ = ', ''
            ).replace(';</script>', '')
            orders_json = json.loads(data)
            orders = orders_json['recentOrders']['orders']
            return orders
        return None

    @staticmethod
    def check_order_canceled(orders):
        if orders:
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
            self.click_element('[data-automation-id="cart-item-remove"]')
        except Exception:
            LOGGER.info('Empty Cart')
        self.sleep(3)

    def delete_address_registry(self):
        self.open_registry_page()
        # open setting tab
        try:
            self.wait_element_loading('.LNR-TabBar-Tab')
            self.click_element('.LNR-TabBar-Tab[text=Settings]')
            LOGGER.info('Clicking settings tab.')
        except Exception:
            LOGGER.info('No tabs visible.')
            pass
        # delete address registry
        try:
            self.wait_element_loading('.delete-link')
            self.click_element('.delete-link')
            self.wait_element_loading('[class="delete-button btn"]')
            self.click_element('[class="delete-button btn"]')
            LOGGER.info('Remove old address registry')
        except Exception:
            pass

        # delete this registry
        try:
            self.click_element('text=Delete This Registry')
            self.wait_element_loading('text=Yes, delete it')
            self.click_element('text=Yes, delete it')
            LOGGER.info('Successfully deleted old registry.')
        except Exception:
            LOGGER.info('Already removed.')
            pass

    def remove_gift_cards(self):
        self.open_payment_methods_page()
        try:
            self.wait_element_loading('[class="gift-card-page"]')
            LOGGER.info('Gift card listed. Removing...')
            remove_btns = self.page.query_selector_all(
                '[data-automation-id*="delete-gift-card-"]')
            for btn in remove_btns:
                btn.click()
                self.sleep(2)
            LOGGER.info('Remove gift card.')

        except Exception:
            LOGGER.info('No Gift cards available.')

        now = datetime.now()
        initial_account_verifide = now.strftime(DATETIME_FORMAT)
        STLPRO_API().update_email_status(self.email, EmailStatus.GOOD)
        print(initial_account_verifide)
        self.close_browser()

    def run(self):
        self.open_sign_up_page()
        self.signin_walmart(self.email.get('email_value'))
        self.open_order_history()
        order_data = self.get_order_data(self.page)
        is_canceled = self.check_order_canceled(order_data)
        if is_canceled:
            LOGGER.info('Order is canceled. Marking as banned.')
            STLPRO_API().update_email_status(self.email, EmailStatus.BANNED)
        else:
            LOGGER.info('Checking cart and removing items in the cart.')
            self.open_cart_page()
            self.remove_items_in_cart()
            self.delete_address_registry()
            self.remove_gift_cards()


if __name__ == '__main__':
    emails = STLPRO_API().get_email_supplier()
    proxies = STLPRO_API().get_proxy_ips(Supplier.WALMART_CODE)
    for email in emails:
        proxy = random.choice(proxies)
        proxy_ip = proxy.get('ip')
        proxy_port = proxy.get('port')

        bot = WmEmailVerifier(use_chrome=False, use_proxy=True,
                              proxy_ip=proxy_ip, proxy_port=proxy_port,
                              email=email)
        bot.run()
