import re
import json


from libs.walmart.walmart_base import WalmartBase

from libs.exception import CaptchaResolveException
from constants import EmailStatus, WaitTimeout, VerifierType
from settings import LOGGER


class WalmartVerifier(WalmartBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.email = kwargs.get('email')
        self.verifier_type = kwargs.get('verifier_type')

    @staticmethod
    def get_order_data(page):
        pattern = re.search(
            "window.__WML_REDUX_INITIAL_STATE__ = (.*?);<\/script>",  # NOQA
            page.content()
        )
        try:
            if pattern:
                data = pattern[1].replace(
                    'window.__WML_REDUX_INITIAL_STATE__ = ', ''
                ).replace(';</script>', '')
                orders_json = json.loads(data)
                orders = orders_json['recentOrders']['orders']
                return orders
        except Exception as e:
            LOGGER.exception(e, exc_info=True)
            LOGGER.error('Error while getting order info.')
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
                try:
                    self.wait_element_loading(
                        '[data-tl-id*="confirm-delete"]',
                        WaitTimeout.MIN_WAIT_TIME)
                    self.click_element('[data-tl-id*="confirm-delete"]')
                except Exception:
                    pass
                self.sleep(2)
            LOGGER.info('Remove gift card.')

        except Exception:
            LOGGER.info('No Gift cards available.')

    def update_status(self):
        if self.verifier_type == VerifierType.EMAIL_VERIFIER:
            self.api.update_email_status(
                self.email.get('id'), EmailStatus.GOOD)
        else:
            self.api.update_account_status(
                self.email.get('id'),
                EmailStatus.GOOD,
                None)
        self.close_browser()

    def run(self):
        try:
            self.open_sign_up_page()
            if self.verifier_type == VerifierType.EMAIL_VERIFIER:
                self.signin_walmart(self.email.get('email_value'))
            elif self.verifier_type == VerifierType.ACCOUNT_VERIFIER:
                self.signin_walmart(self.email.get('email'))

            captcha_detected = self.resolve_captcha(self.proxy_ip)
            if captcha_detected:
                raise CaptchaResolveException()

            if self.is_bad_email:
                LOGGER.info('This email is bad.')
                if self.verifier_type == VerifierType.EMAIL_VERIFIER:
                    self.api.update_email_status(
                        self.email.get('id'), EmailStatus.BANNED)
                else:
                    self.api.update_account_status(
                        self.email.get('id'), EmailStatus.BANNED)
                self.close_browser()
                return
            self.change_password()
            self.open_order_history()
            order_data = self.get_order_data(self.page)
            is_canceled = self.check_order_canceled(order_data)
            if is_canceled:
                LOGGER.info('Order is canceled. Marking as banned.')
                self.api.update_email_status(
                    self.email.get('id'), EmailStatus.BANNED)
                self.close_browser()
                return
            else:
                LOGGER.info('Checking cart and removing items in the cart.')
                self.open_cart_page()
                self.remove_items_in_cart()
                self.delete_address_registry()
                self.remove_gift_cards()
                self.update_status()
            LOGGER.info('success.')
        except CaptchaResolveException:
            LOGGER.error('Cant resolve captcha. Try with another proxy later.')
            self.close_browser()
        except Exception as e:
            LOGGER.exception(e, exc_info=True)
            LOGGER.error('Failed: ' + self.email['email'] or self.email['email_value'])  # NOQA
            self.close_browser()
