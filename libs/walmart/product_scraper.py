import json
import re
import sys
import time
from copy import deepcopy

import constants
import settings
from libs.walmart.mixin import WalmartMixin

from libs.utils import (
    find_value_by_markers, get_json_value_by_key_safely
)
from settings import LOGGER
from libs.api import StlproAPI
from libs.base_scraper import BaseScraper


class WalmartProductScraper(WalmartMixin, BaseScraper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_key = ['item']
        self.supplier_id = constants.Supplier.WALMART_CODE

    def fetch_items(self):
        self.items = StlproAPI().get_current_products(
            self.supplier_id, self.active, self.offset, self.limit
        )
        self.total_item = len(self.items)

    def process_item(self, item):
        self.page.set_default_navigation_timeout(10000)
        item['ip'] = self.current_proxy['ip']
        # abort static file loading
        self.page.route(
            re.compile(r"(\.png)|(\.jpg)|(\.svg)|(\.jpeg)|(\.js)"),
            lambda route: route.abort()
        )
        try:
            url = item['url']
            if not url:
                url = 'https://www.walmart.com/ip/{}'.format(item['item_id'])
            LOGGER.debug(url)
            rep = self.page.goto(url, wait_until="domcontentloaded")
            self.page.wait_for_selector('text=Walmart')
        except TimeoutError:
            LOGGER.error('TimeoutError')
            return
        if self.captcha_detected():
            LOGGER.error("[Captcha] get {}".format(item['ip']))

            # enable static file loading
            self.page.route(
                re.compile(r"(\.png)|(\.jpg)|(\.svg)|(\.jpeg)|(\.js)"),
                lambda route: route.continue_()
            )
            self.page.reload()
            self.resolve_captcha(item['ip'])
            return
        else:
            result = self.parse(
                rep, proxy_ip=item['ip'], item_id=item['item_id']
            )

        if result:
            self.results.append(result)

    def update_result(self):
        self.update_scraped_results()

    def parse(self, response, proxy_ip, item_id):
        result = deepcopy(settings.BASE_SCRAPED_ITEM)
        removed = self.get_available_status(response)
        if removed:
            result.update({
                'removed': True,
                'item_id': item_id,
                'original_item_id': item_id,
                'in_stock_for_shipping': False,
                'url': response.request.url,
            })
            LOGGER.debug(result)
            return result

        leading = ['<script id="__NEXT_DATA__" type="application/json"']  # NOQA
        trailing = "</script>"
        json_string = find_value_by_markers(
            response, leading, trailing
        )

        walmart_seller_id = find_value_by_markers(response, ['"walmartSellerId":"'], '","')  # NOQA
        if not walmart_seller_id:
            walmart_seller_id = constants.Supplier.WALMART_SELLER_ID  # Some item doesn't return walmartSellerId  # NOQA
        if json_string and walmart_seller_id:
            json_string = json_string.split('>', 1)[1]
            data = json.loads(json_string)
            product = data['props']['pageProps']['initialData']['data']['product']  # NOQA
            in_stock_for_shipping = self.get_in_stock_status(
                response, product, walmart_seller_id
            )
            quantity_limit = product.get('orderLimit')
            if quantity_limit and quantity_limit >= 12:
                quantity_limit = 99

            if not in_stock_for_shipping:
                result.update({
                    'proxy': proxy_ip,
                    'item_id': product['usItemId'],
                    'original_item_id': item_id,
                    'in_stock_for_shipping': False,
                    'quantity_limit': quantity_limit,
                    'url': response.request.url,
                    'user_agent': None,
                    'keep_original_item': False,
                })
                LOGGER.debug(result)
                return result

            if not product.get('priceInfo'):
                current_price = None
                savings_amount = None
                savings_percent = None
            else:
                current_price = product['priceInfo']['currentPrice']['price']
                list_price = self.get_list_price(product['priceInfo'])
                savings_amount = list_price - current_price
                savings_amount = round(savings_amount, 3)
                savings_percent = None
                if (current_price is not None) and (savings_amount is not None):  # NOQA
                    savings_percent = round(float(savings_amount) / list_price, 2)  # NOQA

            result.update({
                'proxy': proxy_ip,
                'item_id': product['usItemId'],
                'original_item_id': item_id,
                'description': product['name'],
                'upc': product['upc'],
                'price': current_price,
                'saving_amount': savings_amount,
                'saving_percent': savings_percent,
                'in_stock_for_shipping': in_stock_for_shipping,
                'brand': product['brand'],
                'model': product['model'],
                'shipping_surcharge': None,
                'quantity_limit': quantity_limit,
                'categories': product['category'].get('path'),
                'specials': None,
                'quantity': None,
                'seller_name': product['sellerDisplayName'],
                'url': response.request.url,
                'user_agent': None,  # NOQA
                'keep_original_item': False,
            })
            LOGGER.debug(result)
            return result

    @staticmethod
    def get_list_price(price_map):
        list_price = price_map.get('listPrice')
        if not list_price:
            list_price = price_map.get('wasPrice')
        if not list_price:
            list_price = price_map.get('currentPrice')
        if list_price:
            list_price = list_price.get('price')
            return list_price

    def get_product_object(self, item_id, data):
        keylist = self.start_key + ['product', 'buyBox', 'products']
        products = get_json_value_by_key_safely(data, keylist)
        if not products:
            return None
        for product in products:
            if item_id == product.get('usItemId'):
                return product
        return None

    @staticmethod
    def get_in_stock_status(response, product, walmart_seller_id):
        response_text = response.text().lower()
        if 'delivery not available' in response_text:
            return False
        if 'price for in-store purchase only' in response_text:
            return False
        if not product:
            return False
        if product.get('shippingTitleToDisplay') == 'shipping_title_not_available':  # NOQA
            return False
        urgent_quantity = product.get('urgentQuantity')
        if urgent_quantity:
            return False
        seller_type = product.get('sellerType')
        if seller_type == 'EXTERNAL':
            return False
        product_availability = product.get('availabilityStatus')
        in_stock = product_availability == 'IN_STOCK'
        seller_id = product['sellerId']
        is_walmart = seller_id == walmart_seller_id

        return in_stock and is_walmart

    @staticmethod
    def get_available_status(response):
        if 'This item is unavailable or on backorder.' in response.text():
            return True
        if 'This page could not be found' in response.text():
            return True
        return False


if __name__ == "__main__":
    active = int(sys.argv[1])
    start = int(sys.argv[2])
    end = int(sys.argv[3])
    offset = int(start)
    limit = int(end) - int(start)
    while True:
        try:
            scraper = WalmartProductScraper(
                supplier_id=constants.Supplier.WALMART_CODE,
                active=active,
                offset=offset,
                limit=limit
            )
            scraper.run()
        except Exception as ex:
            LOGGER.exception(str(ex), exc_info=True)
        time.sleep(10)
