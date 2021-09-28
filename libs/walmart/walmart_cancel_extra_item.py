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

    def handle_new_walmart(self):
        self.wait_element_loading('text=View details')
        self.click_element('text=View details')
        self.wait_element_loading('text=Shipping')
        main_item_status_text = ''
        extra_item_status_text = ''
        try:
            content = """
                () => {
                    let states = []
                    const items = document.querySelectorAll(
                        '[class*="flex-column order-0"]')
                    for (let item of items) {
                        states.push(item.innerText.replace('Shipping',''))
                    }
                    return states
            }
            """
            item_states = self.page.evaluate(content)
            print("item states", item_states)
            href_content = """
                () => {
                    let numbers = []
                    const items = document.querySelectorAll(
                        '[link-identifier="itemClick"]')
                    for (let item of items) {
                        numbers.push(item.href.split('/').slice(-1)[0])
                    }
                    return numbers
            }
            """
            item_numbers = self.page.evaluate(href_content)
            print("item numbers", item_numbers)
            extra_item_status_text = item_states[item_numbers.index(
                self.extra_item_number)].strip()
            main_item_status_text = item_states[item_numbers.index(
                self.main_item_number)].strip()
        except IndexError:
            try:
                self.wait_element_loading('text=canceled')
                extra_item_status_text = 'canceled'
            except Exception:
                pass
        LOGGER.info("Extra Item Status: %s", extra_item_status_text)

        if 'Arrives by' in extra_item_status_text:
            self.wait_element_loading('text=Request cancellation')
            cancel_btns = self.page.query_selector_all(
                'text=Request cancellation')
            cancel_btns[-1].click()
            self.wait_element_loading('text=Ordered wrong item or amount.')
            self.click_element('text=Ordered wrong item or amount.')
            self.sleep(2)
            self.click_element('[data-testid="panel-cancel-cta"]')
            self.sleep(2)
            LOGGER.info('Extra item successfully canceled.')

        if extra_item_status_text.lower() == "canceled":
            LOGGER.info('Extra item is in canceled state.')
            self.api.update_extra_item_status(
                self.order.get('id'),
                self.order.get('supplier_order_numbers_str'), "success")

            if main_item_status_text.lower() == "canceled":
                self.api.update_ds_order_status(
                    self.order.get(
                        'id'), DropShipOrderStatus.CANCELLATION_REVIEW
                )
            LOGGER.info('Successfully updated')
        self.close_browser()

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
            self.sleep(3)
            current_link = self.page.url

            if current_link == 'https://www.walmart.com/orders':
                LOGGER.info('New Walmart Page...')
                self.handle_new_walmart()
                return
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
                LOGGER.info('Successfully updated')
            self.close_browser()
        except CaptchaResolveException:
            LOGGER.error('Cant resolve captcha.Try with another proxy later.')
            self.close_browser()
        except Exception as e:
            self.close_browser()
            print(e)
            LOGGER.error('Failed: %s', self.order.get('id'))
