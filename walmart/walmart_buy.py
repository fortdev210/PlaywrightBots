import re

from .walmart_base import WalmartBase
from settings import LOGGER, check_within_day_order
from libs.api import STLPRO_API
from constants import MAX_WAIT_TIME


class WalmartBuy(WalmartBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.payment = kwargs.get('payment_method')

    def check_order_processed(self):
        self.wait_element_loading(
            '[id="cart-active-cart-heading"]', MAX_WAIT_TIME)
        heading = self.page.inner_text('[id="cart-active-cart-heading"]')
        num = re.sub('[^0-9]', '', heading)
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
            self.wait_element_loading(
                '[data-automation-id="purchase-history"]', MAX_WAIT_TIME)
        except TimeoutError:
            self.reload_page()

        last_order_date = self.page.inner_text(
            '[data-automation-id="order-date"]')
        LOGGER.info("Last order date is ", last_order_date)
        order_status = check_within_day_order(last_order_date)
        return order_status

    def check_order_is_gift(self):
        try:
            self.wait_element_loading('[data-tl-id="CartGiftChk"]')
            self.sleep(3)
            is_checked = self.page.is_checked(
                '[data-automation-id="gift-order-checkbox"]')
            if not is_checked:
                self.click_element(
                    '[data-automation-id="gift-order-checkbox"]')
            LOGGER.info("This order is gift.")
        except TimeoutError:
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
            self.wait_element_loading(
                '[data-automation-id="fulfillment-continue"]', MAX_WAIT_TIME)
        except TimeoutError:
            LOGGER.error("Unexpected error while loading. Reloading the page.")
            self.reload_page()
            try:
                self.wait_element_loading(
                    '[data-automation-id="fulfillment-continue"]',
                    MAX_WAIT_TIME)
            except TimeoutError:
                LOGGER.error("Error while loading page again.")
        self.click_element('[data-automation-id="fulfillment-continue"]')

    def confirm_address(self):
        LOGGER.info("Confirm recipient's address.")
        try:
            self.wait_element_loading(
                '[class="address-tile-clickable"]', MAX_WAIT_TIME)
        except TimeoutError:
            LOGGER.error("Error while waiting for address. Reloading...")
            self.reload_page()
            self.continue_steps()
            self.wait_element_loading(
                '[class="address-tile-clickable"]', MAX_WAIT_TIME)

        content = """() => {
            return document.
                querySelector('[class="address-tile-clickable"]').
                querySelector("input").checked}
        """
        address_selected = self.page.evaluate(content)

        if not address_selected:
            LOGGER.info("Should select address")
            content = """() => {
                document.querySelector('[class="address-tile-clickable"]')
                        .querySelector('input').click()
            }"""
            self.page.evaluate(content)
        self.wait_element_loading(
            '[data-automation-id="address-book-action-buttons-on-continue"]')
        self.sleep(2)
        self.click_element(
            '[data-automation-id="address-book-action-buttons-on-continue"]')

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
            self.wait_element_loading(
                '[id="CXO-modal-unfulfillable-dialog"]', MAX_WAIT_TIME)
            LOGGER.info("Sorry, cant ship to this address")
            return True
        except TimeoutError:
            LOGGER.info("Can ship to this address")
            return False

    def handle_gift_options(self):
        try:
            self.wait_element_loading(
                '[class*="gifting-module-body"]', MAX_WAIT_TIME)
            self.wait_element_loading('[name="recipientEmail"]')
            self.insert_value('[name="recipientEmail"]',
                              self.order_info['email'])
            self.wait_element_loading('[name="senderName"]')
            self.reinsert_value('[name="senderName"]',
                                self.order_info['lastName'])
            self.wait_element_loading('[data-automation-id="gift-message"]')
            self.reinsert_value('[data-automation-id="gift-message"]', "...")
            self.wait_element_loading('[data-automation-id="gifting-submit"]')
            self.click_element('[data-automation-id="gifting-submit"]')
            LOGGER.info("Successfully inserted gift message.")
        except TimeoutError:
            LOGGER.info("No gift message.")

    def prepare_for_checkout(self):
        self.continue_steps()
        self.confirm_address()
        self.check_address_confirmed()
        self.check_ship_address()
        self.handle_gift_options()

    def select_payment_method(self):
        if self.payment == 'GiftCard':
            self.click_element('[id="payment-option-radio-1"]')
        else:
            self.click_element('[id="payment-option-radio-2"]')
            self.wait_element_loading('[class*="cash-payment-option"]')
            content = """() => {
                document.querySelector('[class*="cash-payment-option"])
                        .querySelector('button).click()
            }"""
            self.page.evaluate(content)
            self.sleep(3)

    def fill_cash_modal_form(self):
        self.wait_element_loading('[id="cash-modal-form"]')
        # Check modal empty
        input_text = self.page.inner_text('[id="firstName"]')

        if len(input_text) == 0:
            self.insert_value('[id="firstName"]', self.order_info['firstName'])
            self.insert_value('[id="lastName"]', self.order_info['lastName'])
            self.insert_value('[id="addressLineOne"]',
                              self.order_info['addressOne'])
            self.insert_value('[id="addressLineTwo"]',
                              self.order_info['addressTwo'])
            self.insert_value('[id="city"]', self.order_info['city'])
            self.insert_value('[id="postalCode"]', self.order_info['zipCode'])
            self.insert_value('[id="state"]', self.order_info['state'])
            self.insert_value('[id="phone"]', self.order_info['phoneNum'])
            self.insert_value('[id="email"]', self.order_info['email'])

    def send_total_order_price(self):
        try:
            total_price = self.page.inner_text(
                '[data-automation-id="pos-grand-total-amount"]')
            total_price = total_price.replace('$', '')
            STLPRO_API().gift_card_send_total_price(
                self.order_info['id'], total_price)
        except TimeoutError:
            LOGGER.error('Error sending total price of order to db.')

    def add_new_gift_card(self, id):
        LOGGER.info(f'Adding {id+1}th gift card using api...')
        if id != 0:
            # click add new gift card button
            self.wait_element_loading(
                '[data-automation-id="payment-add-new-gift-card"]')
            self.sleep(2)
            self.click_element(
                '[data-automation-id="payment-add-new-gift-card"]')
        new_gift_card = STLPRO_API().gift_card_get_next_card(
            self.order_info['id'])
        self.wait_element_loading(
            '[data-automation-id="enter-gift-card-number"]')
        self.insert_value(
            '[data-automation-id="enter-gift-card-number"]',
            new_gift_card.get('cardNumber')
        )
        self.wait_element_loading('[data-tl-id="submit"]')
        self.sleep(2)
        self.click_element('[data-tl-id="submit"]')
        self.sleep(5)
        content = """([i]) => {
            let value = document.querySelectorAll(
                '[class="price gc-amount-paid-price"]')[{i}]
                .querySelector('[class="visuallyhidden"]').innerText
            value = value.replace("$", "");\
            return value;
        }"""
        used_gift_card_amount = self.page.evaluate(content, [id])
        LOGGER.info(
            f"Gift card number is {new_gift_card.get('cardNumber')} \
             and amount is {used_gift_card_amount}")

        try:
            STLPRO_API().gift_card_send_current_card_info(
                self.order_info['id'],
                new_gift_card.get('cardNumber'),
                used_gift_card_amount
            )
        except Exception:
            LOGGER.error('Error while sending current card info.')

        balance_status = self.page.query_selector(
            '[data-automation-id="pos-balance-due"]')

        if balance_status is None:
            return True

        self.wait_element_loading(
            '[data-automation-id="payment-add-new-gift-card"]')
        self.sleep(2)
        self.click_element('[data-automation-id="payment-add-new-gift-card"]')
        return False

    def get_already_added_gift_cards(self):
        try:
            self.wait_element_loading('[class="gift-card-tile"]')
            number = len(self.page.query_selector_all(
                '[class="gift-card-tile"]'))
            LOGGER.info(f'{number} gift cards are already added.')

            # apply each card to order
            for i in range(number):
                try:
                    content = """
                        ([i])=> {
                            document.querySelectorAll(
                                '[class="gift-card-tile"]'
                            )[{i}].querySelector(
                                '[type=\"checkbox\"]').click()
                    """
                    self.page.evaluate(content, [i])
                    self.sleep(4)
                except Exception:
                    LOGGER.error(f'Cant apply {i}th card again')
            return number
        except TimeoutError:
            return 0

    def pay_with_gift_cards(self):
        try:
            self.wait_element_loading(
                '[id="payment-option-radio-1"]', MAX_WAIT_TIME)
            self.select_payment_method()
        except TimeoutError:
            self.prepare_for_checkout()
            self.select_payment_method()
        self.sleep(3)
        self.send_total_order_price()
        number_of_cards_applied = self.get_already_added_gift_cards()
        for i in range(number_of_cards_applied, self.number_of_cards_to_use):
            pay_done = self.add_new_gift_card(i)
            if pay_done:
                LOGGER.info("Good news! Your order total is covered.")
                break

        self.wait_element_loading('[data-automation-id="submit-payment-gc"]')
        self.sleep(1)
        self.click_element('[data-automation-id="submit-payment-gc"]')

    def pay_with_cash(self):
        try:
            self.wait_element_loading(
                '[id="payment-option-radio-1"]', MAX_WAIT_TIME)
            self.select_payment_method()
        except TimeoutError:
            self.prepare_for_checkout()
            self.select_payment_method()

        self.fill_cash_modal_form()
        self.sleep(2)

        try:
            self.wait_element_loading(
                '[data-automation-id="review-your-order-cash"]')
            self.sleep(2)
            self.click_element('[data-automation-id="review-your-order-cash"]')
            LOGGER.info("Checkout successfully.")
        except TimeoutError:
            LOGGER.error("Error while attempting the Pay with cash button")

    def checkout(self):
        if self.payment == 'GiftCard':
            LOGGER.info('Paying with gift card')
            self.pay_with_gift_cards()
        else:
            LOGGER.info('Paying with cash card')
            self.pay_with_cash()

    def place_order(self):
        self.sleep(3)
        self.wait_element_loading(
            '[data-automation-id="summary-place-holder"]')
        self.click_element('[button[class*="auto-submit-place-order"]]')

    def get_order_number(self):
        self.sleep(3)
        self.wait_element_loading('[class="thankyou-main-heading"]')
        order_info = self.page.inner_text('[class="thankyou-main-heading"]')
        order_number = order_info.split('#')[1]
        LOGGER.info(f'Order number is {order_number}')
        return order_number
