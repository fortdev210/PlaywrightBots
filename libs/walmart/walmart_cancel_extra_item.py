from .walmart_base import WalmartBase
from libs.exception import CaptchaResolveException
from settings import LOGGER
from constants.ds_order_status import DropShipOrderStatus


class WalmartCancelExtraItem(WalmartBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.order = kwargs.get('order')
        self.extra_item_number = None
        self.main_item_number = None

    def get_item_numbers(self):
        self.extra_item_number = self.order.get(
            'extra_items')[0].get('item_number')
        self.main_item_number = self.order.get(
            'items')[0].get('supplier_item_id')

    def run(self):
        self.get_item_numbers()
        try:
            self.open_sign_up_page()
            self.signin_walmart(self.order.get(
                'account_supplier').get('username'))
            captcha_detected = self.resolve_captcha(self.proxy_ip)
            if captcha_detected:
                raise CaptchaResolveException()

            self.open_order_history()
            extra_item_status = self.cancel_extra_item(self.extra_item_number)
            main_item_status = self.get_item_status(self.main_item_number)
            LOGGER.info("Main Item Status: %s", main_item_status)

            if extra_item_status.lower() == "canceled":
                self.api.update_extra_item_status(
                    self.order.get('id'),
                    self.order.get('supplier_order_numbers_str'), "success")

                if main_item_status.lower() == "canceled":
                    self.api.update_ds_order_status(
                        self.order.get(
                            'id'), DropShipOrderStatus.CANCELLATION_REVIEW
                    )
            self.close_browser()
            LOGGER.info('Successfully updated')
        except CaptchaResolveException:
            LOGGER.error('Cant resolve captcha.Try with another proxy later.')
            self.close_browser()
        except Exception:
            LOGGER.error('Failed: %s', self.order.get('id'))
