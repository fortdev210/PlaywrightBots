import json
import random

import constants
from libs.bot_manager import BotManager
from libs.exception import BotDetectionException, AccessDeniedException
import settings


class HomeDepotOrderStatusScraper(BotManager):
    TRACKING_URL = 'https://www.homedepot.com/order/view/tracking'
    SUPPLIER_ID = constants.Supplier.HOMEDEPOT_CODE

    def fetch_ips(self):
        self.ips = self.api.get_proxy_ips(self.SUPPLIER_ID)

    def fetch_orders(self):
        self.orders = self.api.get_ds_orders(self.SUPPLIER_ID)
        start_index = self.offset
        end_index = self.offset + self.limit
        self.orders = self.orders[start_index:end_index]
        random.shuffle(self.orders)

    def run(self):
        self.fetch_ips()
        self.fetch_orders()

        if len(self.orders) == 0:
            self.sleep(5 * 60)  # sleep 5 mins if there is no order
            return

        for order in self.orders:
            random.shuffle(self.ips)
            random_ips = self.ips[:2]
            for ip in random_ips:
                order['ip'] = ip
                is_success = self.scrape_an_order(order)
                if is_success:
                    break

    def scrape_an_order(self, order):
        settings.LOGGER.info('============== Start {} =============='.format(
            order['supplier_order_numbers_str']
        ))
        # init order info
        self.order = order
        self.proxy_ip = order['ip']['ip']
        self.proxy_port = order['ip']['port']
        self.scraped_data = None

        self.create_browser()
        is_success = False
        try:
            self.perform()
        except Exception as exception:
            settings.LOGGER.error(exception)
            pass
        else:
            is_success = True

        # reset order info
        self.order = None
        self.proxy_ip = None
        self.proxy_port = None
        self.scraped_data = None

        self.close_browser()
        return is_success

    def perform(self):
        self.open_new_page()

        self.fill_order_status_form()

        self.update_order()

    def update_order(self):
        if self.scraped_data:
            settings.LOGGER.info("Update order")
            result = self.api.update_ds_order(
                self.order['id'],
                json.dumps(self.scraped_data)
            )
            settings.LOGGER.info(result)
        else:
            settings.LOGGER.info("No data is scraped")

    def fill_order_status_form(self):
        self.page.goto(self.TRACKING_URL)

        # fill order number
        self.page.wait_for_selector("input[id=order]")
        self.page.click("input[id=order]")
        self.page.type(
            "input[id=order]",
            self.order['supplier_order_numbers_str'],
            delay=200
        )

        # fill email
        self.page.wait_for_selector("input[id=email]")
        self.page.click("input[id=email]")
        self.page.type(
            "input[id=email]",
            self.order['user_email'],
            delay=200
        )

        counter = 0
        while counter < 3:
            try:
                self.page.click("button[type=submit]")
                self.page.wait_for_timeout(5000)

                page_content = self.page.content().lower()
                if "access denied".lower() in page_content:
                    raise AccessDeniedException()

                if "please try again shortly.".lower() in page_content:
                    raise BotDetectionException()

                content = '''([x]) => {return fetch('/customer/order/v1/guest/orderdetailsgroup', {method: 'POST', body: '{"orderDetailsRequest": {"orderId": "%s", "emailId": "%s"}}', headers: {'Version': 'HTTP/1.0', 'Accept': 'application/json','Content-Type': 'application/json'}}).then(res => res.json());}'''  # NOQA
                content = content % (
                    self.order['supplier_order_numbers_str'],
                    self.order['user_email']
                )
                self.scraped_data = self.page.evaluate(content, [None])
            except AccessDeniedException:
                counter = 10
                break
            except BotDetectionException:
                self.page.click("input[id=order]")
                self.page.click("input[id=email]")
                counter += 1
            except Exception:
                self.page.wait_for_timeout(2000)
                counter += 1
            else:
                break

        if counter == 10:
            raise Exception("Access Denied, IP is not USA => change IP")

        if not self.scraped_data:
            raise Exception("Max retry times exceed!")
