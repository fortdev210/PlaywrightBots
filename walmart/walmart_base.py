import random

from libs.bot_manager import BotManager
from settings import (LOGGER, WALMART_PASSWORD,
                      WALMART_OLD_PASSWORDS, WALMART_REG_LINK,
                      WALMART_ACCOUNT_LINK, WALMART_ORDER_HISTORY_LINK)


class WalmartBase(BotManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.order_info = kwargs.get('order_info')

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

    def signin_walmart(self, email):
        self.wait_element_loading('[id="sign-in-form"]')
        self.insert_value('[id="email"]', email)
        try:
            self.wait_element_loading(
                '[data-automation-id="signin-continue-submit-btn"]')
            LOGGER.info('========== New Signin Page ==========')
            self.press_enter()
            self.insert_value('[id="password"]', WALMART_PASSWORD)
            self.press_enter()
        except Exception:
            LOGGER.info('========== Old Signin Page ==========')
            self.insert_value('[id="password"]', WALMART_PASSWORD)
            self.click_element('[data-automation-id="signin-submit-btn"]')
            try:
                self.wait_element_loading(
                    "text=Your password and email do not match.")
                self.reinsert_value('[id="password"]',
                                    WALMART_OLD_PASSWORDS[0])
                self.click_element('[data-automation-id="signin-submit-btn"]')
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

    def captcha_detected(self):
        if self.page.is_visible('div[class="captcha re-captcha"]'):
            return True
        return False

    def change_password(self, current_password):
        LOGGER.info("Change password")
        self.go_to_link(WALMART_ACCOUNT_LINK)
        self.sleep(3)
        self.wait_element_loading(
            '[data-automation-id="password-edit-button"]')
        self.click_element('[data-automation-id="password-edit-button"]')
        try:
            self.wait_element_loading('[name="currentPassword"]')
            self.insert_value('[name="currentPassword"]', current_password)
            self.insert_value('[name="newPassword"]', WALMART_PASSWORD)
            self.click_element('[data-automation-id="password-submit-button"]')
        except Exception:
            LOGGER.error("Error while changing password")

    def open_order_history(self):
        self.go_to_link(WALMART_ORDER_HISTORY_LINK)

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

    def resolve_captcha(self, ip):
        i = 0
        captcha_detected = self.captcha_detected()
        while captcha_detected and i < 3:
            i += 1
            frame = self.page.frames[-1]
            page_frame = frame.page
            page_frame.hover('div[role="main"]')
            page_frame.click(random.randint(0, 100), random.randint(0, 100), delay=500)  # NOQA
            page_frame.focus('div[role="main"]')
            page_frame.click('div[role="main"]', delay=random.randint(15000, 20000))  # NOQA
            page_frame.wait_for_timeout(random.randint(5000, 10000))
            LOGGER.info("resolve captcha {} {} times".format(ip, i))
        LOGGER.info("[Captcha] resolve end {}".format(ip))

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
                LOGGER.info("Successfully cancelled extra item.")
            except Exception:
                LOGGER.error("Failed to select the reason.")

        return extra_item_status
