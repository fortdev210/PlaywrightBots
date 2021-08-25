import random
import re
import sys

from constants import Supplier
from walmart.walmart_base import WalmartBase
from settings import LOGGER
from libs.api import StlproAPI
from libs.exception import BotDetectionException


class WmOrderStatus(WalmartBase):
    WALMART_PURCHASE_HISTORY_LINK = \
        "https://www.walmart.com/account/wmpurchasehistory"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.order = kwargs.get('order')

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

    def try_to_scrape_walmart_order(self):
        self.open_sign_up_page()
        self.signin_walmart(self.order.get('username'))
        # resolve captcha
        captcha_detected = self.resolve_captcha(self.proxy_ip)
        if captcha_detected:
            raise BotDetectionException()

        self.open_order_history()
        self.sleep(random.randint(5, 10))
        data = self.get_order_data(self.page)
        print("data success")
        return data

    def run(self):
        try:
            data = self.try_to_scrape_walmart_order()
            result = self.api.update_ds_order(self.order['id'], data)
            LOGGER.info(result)
        except BotDetectionException:
            LOGGER.error('Unable to solve captcha. Try with another proxy.')
        except Exception as e:
            LOGGER.exception(e, exc_info=True)
            LOGGER.error("Failed: " + self.order['supplier_order_numbers_str'])
            self.close_browser()
            self.sleep(5)


if __name__ == '__main__':
    start = int(sys.argv[1])
    end = int(sys.argv[2])
    orders = StlproAPI().get_ds_orders(supplier_id=Supplier.WALMART_CODE)
    LOGGER.info(f"Get {len(orders)} orders")
    proxies = StlproAPI().get_proxy_ips(Supplier.WALMART_CODE)
    orders = orders[start:end]
    random.shuffle(orders)

    for order in orders:
        LOGGER.info('-------------------------------------------')
        LOGGER.info(order)
        proxy = random.choice(proxies)
        proxy_ip = proxy.get('ip')
        proxy_port = proxy.get('port')
        LOGGER.info('proxy: {proxy_ip}:{proxy_port}'.format(
            proxy_ip=proxy_ip, proxy_port=proxy_port))
        bot = WmOrderStatus(
            use_chrome=False, use_luminati=False, use_proxy=True,
            proxy_ip=proxy_ip, proxy_port=proxy_port, order=order
        )
        bot.run()
