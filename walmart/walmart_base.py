from libs.bot_manager import BotManager
from settings import (LOGGER, WALMART_PASSWORD,
                      WALMART_OLD_PASSWORDS, WALMART_REG_LINK)


class WalmartBase(BotManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.order_info = kwargs.get('order_info')

    def open_sign_up_page(self):
        if self.browser is None:
            self.run_browser()
        self.open_new_page()
        self.go_to_link(WALMART_REG_LINK)

    def open_sign_in_page(self):
        self.open_sign_up_page()
        self.page.wait_for_selector(
            '[data-automation-id="signup-sign-in-btn"]')
        self.page.click('[data-automation-id="signup-sign-in-btn"]')

    def signin_walmart(self):
        self.insert_value('[id="email"]', self.order_info['email'])
        try:
            self.wait_element_loading(
                '[data-automation-id="signin-continue-submit-btn"]')
            LOGGER.info('========== New Signin Page ==========')
            self.press_enter()
            self.insert_value('[id="password"]', WALMART_PASSWORD)
            self.press_enter()
        except TimeoutError:
            LOGGER.info('========== Old Signin Page ==========')
            self.insert_value('[id="password"]', WALMART_PASSWORD)
            self.click_element('[data-automation-id="signin-submit-btn"]')
            try:
                self.page.wait_element_loading(
                    "text=Your password and email do not match.")
                self.reinsert_value('[id="password"]',
                                    WALMART_OLD_PASSWORDS[0])
                self.click_element('[data-automation-id="signin-submit-btn"]')
            except TimeoutError:
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

    def cancel_extra_item(self, extra_item_number):
        content = "\
            () => {\
                const selector = '[href=\"/ip/{extraItemNumber}\"]'; \
                const parent = document.querySelector([selector]).\
                    parentElement.parentElement.parentElement.\
                    parentElement.parentElement;\
                return parent.querySelector(\
                    '[data-automation-id=\"shipment-status\"]').innerText; \
            }\
        ".format(extraItemNumber=extra_item_number)
        extra_item_status = self.page.evaluate(content)
        LOGGER.info(f'Extra item status is {extra_item_status}')

        if 'arrives by' in extra_item_status.lower():
            content = """
                (extraItemNumber) => {
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
                }, extraItemNumber"""
            self.page.evaluate(content)
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
