import random
import re

from libs.walmart.walmart_base import WalmartBase
from settings import LOGGER
from libs.exception import CaptchaResolveException


class WalmartOrderStatus(WalmartBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.order = kwargs.get('order')

    def get_order_data(self, page):
        pattern = re.search(
            "window.__WML_REDUX_INITIAL_STATE__ = (.*?);<\/script>",  # NOQA
            page.content()
        )
        if pattern:
            data = pattern[0].replace(
                'window.__WML_REDUX_INITIAL_STATE__ = ', ''
            ).replace(';</script>', '')
            return data
        # new format
        # pattern = re.search(
        #     '<script id="__NEXT_DATA__" type="application/json"(.*?)<\/script>',  # NOQA
        #     page.content()
        # )
        # if pattern:
        #     self.data_type = constants.DataType.JSON_2
        #     data_string = pattern[0].rsplit('">', 1)[1]
        #     data_string = data_string.replace('</script>', '')
        #     return data_string

    def try_to_scrape_walmart_order(self):
        self.create_browser()
        self.open_new_page()
        self.open_trackorder_page()
        # fill order number
        self.page.wait_for_selector("input[id=email]")
        self.page.click("input[id=email]")
        self.page.type(
            "input[id=email]",
            self.order['user_email'],
            delay=200
        )

        # fill email
        self.page.wait_for_selector("input[id=fullOrderId]")
        self.page.click("input[id=fullOrderId]")
        self.page.type(
            "input[id=fullOrderId]",
            self.order['supplier_order_numbers_str'],
            delay=200
        )
        self.page.keyboard.press("Enter")

        # resolve captcha
        if self.captcha_detected():
            # enable static file loading
            self.resolve_captcha(self.proxy_ip)
            LOGGER.error("[Captcha] get {}".format(self.proxy_ip))

        self.sleep(random.randint(5, 10))
        data = self.get_order_data(self.page)
        if not data:
            raise Exception("Can not parse shipment info")
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
