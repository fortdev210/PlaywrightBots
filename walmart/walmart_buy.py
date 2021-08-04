import re

from .walmart_base import WalmartBase
from settings import LOGGER, check_within_day_order


class WalmartBuy(WalmartBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def check_order_processed(self):
        self.wait_element_loading('[id="cart-active-cart-heading"]', 20000)
        heading = self.page.inner_text('[id="cart-active-cart-heading"]')
        num = re.sub('[^0-9]','',heading)
        if num < 1:
            return False
        return True
    
    def track_orders(self):
        """
        Process tracking bad order on cart page
        """
        # Click account button
        self.wait_element_loading('[aria-label="Your Account"]')
        self.click_element('[aria-label="Your Account"]')

        # Wait for account menu open
        self.wait_element_loading('[id="vh-account-menu-root"]')
        self.wait_element_loading('[title="Track Orders"]')
        self.click_element('[title="Track Orders"]')

        # Wait for purchase history page open
        try:
            self.wait_element_loading('[data-automation-id="purchase-history"]', 30000)
        except:
            self.reload_page()

        last_order_date = self.page.inner_text('[data-automation-id="order-date"]')
        LOGGER.info("Last order date is ", last_order_date)
        order_status = check_within_day_order(last_order_date)
        return order_status

    def check_order_is_gift(self):
        try:
            self.wait_element_loading('[data-tl-id="CartGiftChk"]')
            self.sleep(3)
            content = """() => {
                if (
                    !document.querySelector('[data-automation-id="gift-order-checkbox"]')
                        .checked
                ) {
                    document
                        .querySelector('[data-automation-id="gift-order-checkbox"]')
                        .click();
                }
            }"""
            self.page.evaluate(content)
            LOGGER.info("This order is gift.")
        except:
            LOGGER.error("No gift check.")
            pass
    