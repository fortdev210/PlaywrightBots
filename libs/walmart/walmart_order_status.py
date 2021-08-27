import random
import re


from libs.walmart.walmart_base import WalmartBase
from settings import LOGGER
from libs.exception import CaptchaResolveException


class WalmartOrderStatus(WalmartBase):
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
        self.signin_walmart(self.order.get('username')
                            or self.order.get('email'))
        # resolve captcha
        captcha_detected = self.resolve_captcha(self.proxy_ip)
        if captcha_detected:
            raise CaptchaResolveException()

        self.open_order_history()
        self.sleep(random.randint(5, 10))
        data = self.get_order_data(self.page)
        return data

    def run(self):
        try:
            data = self.try_to_scrape_walmart_order()
            result = self.api.update_ds_order(self.order['id'], data)
            LOGGER.info(result)
        except CaptchaResolveException:
            LOGGER.error('Unable to solve captcha. Try with another proxy.')
        except Exception as e:
            LOGGER.exception(e, exc_info=True)
            LOGGER.error("Failed: " + self.order['supplier_order_numbers_str'])
        self.close_browser()
        self.sleep(5)
