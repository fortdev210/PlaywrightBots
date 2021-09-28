import json
import random
from furl import furl

from playwright.sync_api import ViewportSize

from libs.walmart.walmart_base import WalmartBase
from settings import LOGGER
from libs.exception import BotDetectionException


class WalmartOrderStatus(WalmartBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.order = kwargs.get('order')
        self.data = None

    def open_new_page(self):
        page = self.browser.new_page(
            viewport=ViewportSize({"width": 1024, "height": 768})
        )
        page.set_default_navigation_timeout(60 * 1000*5)
        self.page = page

    def get_order_data(self, request):

        if 'https://www.walmart.com/orchestra/home/graphql' not in request.url:
            return None
        self.data = request.response().json()

    def try_to_scrape_walmart_order(self):

        self.open_trackorder_page()
        if self.captcha_detected():
            LOGGER.error("[Captcha] get {}".format(self.proxy_ip))
            raise BotDetectionException()
        # fill order number
        self.page.wait_for_selector("input[name=emailAddress]")
        self.page.focus("input[name=emailAddress]")
        self.page.type(
            "input[name=emailAddress]",
            self.order['user_email'],
            delay=200
        )

        # fill email
        self.page.wait_for_selector("input[name=orderNumber]")
        self.page.focus("input[name=orderNumber]")
        self.page.type(
            "input[name=orderNumber]",
            self.order['supplier_order_numbers_str'],
            delay=200
        )
        self.page.keyboard.press("Enter")
        count = 0
        while count <= 10 and self.data is None:
            event = self.page.wait_for_event('requestfinished')
            self.get_order_data(event)
            count += 1

        # resolve captcha
        if self.captcha_detected():
            LOGGER.error("[Captcha] get {}".format(self.proxy_ip))
            raise BotDetectionException()
        self.sleep(random.randint(5, 10))
        if not self.data:
            raise Exception("Can not parse shipment info")

        # Fetch tracking info an repopulate payload
        super_groups = self.data['data']['guestOrder'].pop('groups_2101', [])
        groups = []
        for group in super_groups:
            shipment = group.get('shipment')
            if shipment:
                tracking_number = shipment.get('trackingNumber')
                if tracking_number:
                    tracking_url = shipment.get('trackingUrl')
                    if tracking_url:
                        parsed = furl(tracking_url)
                        content = '''([x]) => {return fetch('/api/tracking?trackingId=%s&orderId=%s', {method: 'GET', headers: {'Version': 'HTTP/1.0', 'Accept': 'application/json','Content-Type': 'application/json'}}).then(res => res.json());}'''  # NOQA
                        content = content % (parsed.args['tracking_id'], parsed.args['order_id'])  # NOQA
                        tracking_info = self.page.evaluate(content, [None])
                        if tracking_info:
                            shipment['trackingCarrier'] = tracking_info['carrier']  # NOQA
            groups.append(group)
        self.data['data']['guestOrder']['groups_2101'] = groups
        # LOGGER.info(json.dumps(self.data))
        return json.dumps(self.data)

    def run(self):
        counter = 0
        self.create_browser()
        self.open_new_page()
        while counter <= 5:
            try:
                data = self.try_to_scrape_walmart_order()
                if data:
                    result = self.api.update_ds_order(self.order['id'], data)
                    LOGGER.info(result)
                    if result.get('status') != 'success':
                        LOGGER.info(data)
            except BotDetectionException:
                captcha_detected = self.resolve_captcha(self.proxy_ip)
                if captcha_detected:
                    counter = 10
                else:
                    counter += 1
            except Exception as e:
                LOGGER.exception(e, exc_info=True)
                LOGGER.exception("Failed: " + self.order['supplier_order_numbers_str'])  # NOQA
                break
            else:
                break
        self.sleep(5)
