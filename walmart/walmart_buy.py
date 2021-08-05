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
            is_checked = self.page.is_checked('[data-automation-id="gift-order-checkbox"]')
            if is_checked == False:
                self.click_element('[data-automation-id="gift-order-checkbox"]')
            LOGGER.info("This order is gift.")
        except:
            LOGGER.error("No gift check.")
            pass
    
    def go_to_checkout(self):
        self.wait_element_loading('[data-tl-id="CartCheckOutBtnBottom"]')
        self.sleep(3)
        self.click_element('[data-tl-id="CartCheckOutBtnBottom"]')
        LOGGER.info("----- Go to checkout.")
   
    def continue_steps(self):
        self.sleep(3)
        try:
            self.wait_element_loading('[data-automation-id="fulfillment-continue"]',20000)
        except:
            LOGGER.error("Unexpected error while loading. Reloading the page.")
            self.reload_page()
            try:
                self.wait_element_loading('[data-automation-id="fulfillment-continue"]', 20000)
            except:
                LOGGER.error("Error while loading page again.")
        self.click_element('[data-automation-id="fulfillment-continue"]')
    
    def confirm_address(self):
        LOGGER.info("Confirm recipient's address.")
        try:
            self.wait_element_loading('[class="address-tile-clickable"]', 20000)
        except:
            LOGGER.error("Error while waiting for address. Reloading...")
            self.reload_page()
            self.continue_steps()
            self.wait_element_loading('[class="address-tile-clickable"]', 20000)
        
        content = """() => {
            return document.
                querySelector('[class="address-tile-clickable"]').
                querySelector("input").checked}
        """
        address_selected = self.page.evaluate(content)

        if address_selected == False:
            LOGGER.info("Should select address")
            content = """() => {
                document.querySelector('[class="address-tile-clickable"]')
                        .querySelector('input').click()
            }"""
            self.page.evaluate(content)
        self.wait_element_loading('[data-automation-id="address-book-action-buttons-on-continue"]')
        self.sleep(2)
        self.click_element('[data-automation-id="address-book-action-buttons-on-continue"]')
    
    def check_address_confirmed(self):
        self.sleep(3)
        current_url = self.page.url
        if current_url == "https://www.walmart.com/checkout/#/fulfillment":
            LOGGER.info("Should repeat the process again.")
            self.continue_steps()
            LOGGER.info("Confirm recipient's address")
            self.confirm_address()
   
    def check_ship_address(self):
        try:
            self.wait_element_loading('[id="CXO-modal-unfulfillable-dialog"]', 20000)
            LOGGER.info("Sorry, cant ship to this address")
            return True
        except:
            LOGGER.info("Can ship to this address")
            return False
   
