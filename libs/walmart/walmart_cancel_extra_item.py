from .walmart_base import WalmartBase
from libs.exception import CaptchaResolveException
from settings import LOGGER


class WalmartCancelExtraItem(WalmartBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.order = kwargs.get('order')
        self.extra_item_number = None

    def get_extra_item_number(self):
        self.extra_item_number = self.order.get(
            'extra_items')[0].get('item_number')

    def run(self):
        try:
            self.open_sign_up_page()
            captcha_detected = self.resolve_captcha()
            if captcha_detected:
                raise CaptchaResolveException()

            self.open_order_history()
            self.cancel_extra_item(self.extra_item_number)

        except CaptchaResolveException:
            LOGGER.error('Cant resolve captcha. Try with another proxy later.')
            self.close_browser()
