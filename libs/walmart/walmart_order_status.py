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

        if 'account/electrode/account/api/v2/trackorder' not in request.url:
            return None
        self.data = request.response().json()

    def try_to_scrape_walmart_order(self):

        self.open_trackorder_page()
        if self.captcha_detected():
            LOGGER.error("[Captcha] get {}".format(self.proxy_ip))
            raise BotDetectionException()
        # fill order number
        self.page.wait_for_selector("input[id=email]")
        self.page.click("input[id=email]")
        self.page.type(
            "input[id=email]",
            self.order['user_email'],
            delay=200
        )

        # fill email
        self.page.wait_for_selector("input[id=fullOrderId]")
        self.page.click("input[id=fullOrderId]")
        self.page.type(
            "input[id=fullOrderId]",
            self.order['supplier_order_numbers_str'],
            delay=200
        )
        with self.page.expect_event("requestfinished") as event_info:
            self.page.keyboard.press("Enter")
        request = event_info.value
        self.get_order_data(request)
        # resolve captcha
        if self.captcha_detected():
            LOGGER.error("[Captcha] get {}".format(self.proxy_ip))
            raise BotDetectionException()
        self.sleep(random.randint(5, 10))
        if not self.data:
            raise Exception("Can not parse shipment info")

        # Fetch tracking info an repopulate payload
        super_groups = self.data['payload']['order'].pop('superGroups', [])
        groups = []
        for group in super_groups:
            shipments = []
            for shipment in group['shipments']:
                trackings = shipment.get('tracking')
                if not trackings:
                    shipments.append(shipment)
                    continue
                tracking = trackings[0]
                tracking['tracking']['carrier'] = None
                external_url = tracking.get('tracking').get('externalUrl')
                if external_url:
                    parsed = furl(external_url)
                    content = '''([x]) => {return fetch('/api/tracking?trackingId=%s&orderId=%s', {method: 'GET', headers: {'Version': 'HTTP/1.0', 'Accept': 'application/json','Content-Type': 'application/json'}}).then(res => res.json());}'''  # NOQA
                    content = content % (parsed.args['tracking_id'], parsed.args['order_id'])  # NOQA
                    tracking_info = self.page.evaluate(content, [None])
                    if tracking_info:
                        tracking['tracking']['carrier'] = tracking_info['carrier']  # NOQA
                shipment['tracking'] = [tracking]  # FIXME: maybe shipment has more than one tracking  # NOQA
                shipments.append(shipment)
            group['shipments'] = shipments
            groups.append(group)
        self.data['payload']['order']['superGroups'] = groups
        return json.dumps(self.data)

    def run(self):
        counter = 0
        self.create_browser()
        self.open_new_page()
        data = None
        while counter <= 5:
            try:
                data = self.try_to_scrape_walmart_order()
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
        if data:
            result = self.api.update_ds_order(self.order['id'], data)
            LOGGER.info(result)
            if result.get('status') != 'success':
                LOGGER.info(data)

        self.close_browser()
        self.sleep(5)
