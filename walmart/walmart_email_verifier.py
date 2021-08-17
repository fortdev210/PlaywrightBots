import re
import json

from walmart.walmart_base import WalmartBase
from libs.api import STLPRO_API
from constants import Supplier


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
        data = pattern[0].replace(
            'window.__WML_REDUX_INITIAL_STATE__ = ', ''
        ).replace(';</script>', '')
        return data

    def run(self):
        self.open_sign_up_page()
        self.signin_walmart(self.email)
        self.open_order_history()
        order_data = self.get_order_data(self.page)
        orders = json.loads(order_data)
        print(orders)


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
