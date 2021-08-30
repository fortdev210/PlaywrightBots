import random

from libs.bot_manager import BotManager
from libs.walmart.mixin import WalmartMixin
from settings import LOGGER, WALMART_PASSWORD, WALMART_OLD_PASSWORDS
from settings.url import (
    WALMART_REG_LINK,
    WALMART_ACCOUNT_LINK, WALMART_ORDER_HISTORY_LINK,
    WALMART_CART_LINK, WALMART_REGISTRY_LINK, WALMART_PAYMENT_METHODS_LINK)


class WalmartBase(WalmartMixin, BotManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.order_info = kwargs.get('order_info')
        self.should_change_password = False
        self.wm_current_password = ''
        self.is_bad_email = False

    def open_sign_up_page(self):
        if self.browser is None:
            self.create_browser()
        self.open_new_page()
        self.go_to_link(WALMART_REG_LINK)

    def open_sign_in_page(self):
        self.open_sign_up_page()
        self.page.wait_for_selector(
            '[data-automation-id="signup-sign-in-btn"]')
        self.page.click('[data-automation-id="signup-sign-in-btn"]')

    def try_old_password(self, old_password, email):
        self.wait_element_loading(
            "text=Your password and email do not match.")
        self.should_change_password = True
        LOGGER.info('Trying with old password: %s', old_password)
        self.reload_page()
        self.wait_element_loading('[id="sign-in-form"]')
        self.insert_value('[id="email"]', email)

        self.insert_value('[id="password"]',
                          old_password)
        self.click_element('[data-automation-id="signin-submit-btn"]')

    def signin_walmart(self, email):
        self.wait_element_loading('[id="sign-in-form"]')
        self.insert_value('[id="email"]', email)
        try:
            self.wait_element_loading(
                '[data-automation-id="signin-continue-submit-btn"]')
            LOGGER.info('New Signin Page')
            self.press_enter()
            self.insert_value('[id="password"]', WALMART_PASSWORD)
            self.press_enter()
        except Exception:
            LOGGER.info('Old Signin Page')
            self.insert_value('[id="password"]', WALMART_PASSWORD)
            self.click_element('[data-automation-id="signin-submit-btn"]')
            try:
                self.try_old_password(WALMART_OLD_PASSWORDS[0], email)
                try:
                    self.try_old_password(WALMART_OLD_PASSWORDS[1], email)
                    try:
                        self.wait_element_loading(
                            "text=Your password and email do not match.")
                        self.is_bad_email = True
                    except Exception:
                        self.wm_current_password = WALMART_OLD_PASSWORDS[1]
                except Exception:
                    self.wm_current_password = WALMART_OLD_PASSWORDS[0]
            except Exception:
                pass

    def signup_walmart(self):
        self.wait_element_loading('[id="first-name-su"]')
        self.insert_value('[id="first-name-su"]', self.order_info['firstName'])
        self.insert_value('[id="last-name-su"]', self.order_info['lastName'])
        self.insert_value('[id="email-su"]', self.order_info['email'])
        self.insert_value('[id="password-su"]', WALMART_PASSWORD)
        self.click_element('[id="su-newsletter"]')
        self.sleep(3)
        self.wait_element_loading('[data-automation-id="signup-submit-btn"]')
        self.click_element('[data-automation-id="signup-submit-btn"]')

    def change_password(self):
        if self.should_change_password and not self.is_bad_email \
                and self.wm_current_password:
            LOGGER.info("Change password")
            self.go_to_link(WALMART_ACCOUNT_LINK)
            self.sleep(3)
            self.wait_element_loading(
                '[data-automation-id="password-edit-button"]')
            self.click_element('[data-automation-id="password-edit-button"]')
            try:
                self.wait_element_loading('[name="currentPassword"]')
                self.insert_value('[name="currentPassword"]',
                                  self.wm_current_password)
                self.insert_value('[name="newPassword"]', WALMART_PASSWORD)
                self.click_element(
                    '[data-automation-id="password-submit-button"]')
            except Exception:
                LOGGER.error("Error while changing password")

    def open_order_history(self):
        self.go_to_link(WALMART_ORDER_HISTORY_LINK)

    def open_cart_page(self):
        self.go_to_link(WALMART_CART_LINK)

    def open_registry_page(self):
        self.go_to_link(WALMART_REGISTRY_LINK)

    def open_payment_methods_page(self):
        self.go_to_link(WALMART_PAYMENT_METHODS_LINK)

    @staticmethod
    def get_random_url():
        urls = [
            'https://www.walmart.com/account/login',
            'https://www.walmart.com/account/login?tid=0&returnUrl=%2F',
            'https://www.walmart.com/account/login?tid=0&returnUrl=%2Fcp%2Felectronics%2F3944',  # NOQA
            'https://www.walmart.com/account/login?tid=0&returnUrl=%2Fbrowse%2Felectronics%2Ftouchscreen-laptops%2F3944_3951_1089430_1230091_1101633',  # NOQA
            'https://www.walmart.com/account/login?tid=0&returnUrl=%2Flists',
            'https://www.walmart.com/account/login?tid=0&returnUrl=%2Feasyreorder%3FeroType%3Dlist',  # NOQA
        ]
        url = random.choice(urls)
        return url

    def cancel_extra_item(self, extra_item_number):
        content = """
            ([extraItemNumber]) => {
                const selector = `[href="/ip/${extraItemNumber}"]`;
                const parent = document.querySelector([selector]).
                    parentElement.parentElement.parentElement.
                    parentElement.parentElement;
                return parent.querySelector(
                    '[data-automation-id="shipment-status"]').innerText;
            }
        """
        extra_item_status = self.page.evaluate(content, [extra_item_number])
        LOGGER.info(f'Extra item status is {extra_item_status}')

        if 'arrives by' in extra_item_status.lower():
            content = """
                ([extraItemNumber]) => {
                    const selector = `[href=\"/ip/${extraItemNumber}\"]`;
                    const parent = document.querySelector(
                        [selector]).parentElement.parentElement.
                        parentElement.parentElement.parentElement;
                    try {
                        parent
                        .querySelector('[class="order-details-cancellation"]')
                        .querySelector("button")
                        .click();
                    } catch (error) {
                    }
                }"""
            self.page.evaluate(content, [extra_item_number])
            self.sleep(3)

            try:
                self.wait_element_loading('form[class="cancellation-form"]')
                self.click_element('[name="subReasonCode"]')
                self.sleep(2)
                content = """
                    document
                    .querySelector('[class="cancellation-form"]')
                    .querySelector('[type="submit"]')
                    .click();
                """
                self.page.evaluate(content)
                LOGGER.info("Successfully cancelled extra item.")
            except Exception:
                LOGGER.error("Failed to select the reason.")

        return extra_item_status
