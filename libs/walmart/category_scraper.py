import random
import re
import traceback
from copy import deepcopy

from furl import furl
from playwright._impl._api_types import TimeoutError

import constants
import settings
from libs.exception import CaptchaResolveException
from libs.walmart.mixin import WalmartMixin
from settings import LOGGER
from libs.base_scraper import BaseScraper
from libs.api import StlproAPI


class WalmartCategoryScraper(WalmartMixin, BaseScraper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_grocery_api = constants.Supplier.WALMART_GROCERY_API
        self.base_search_api = constants.Supplier.WALMART_SEARCH_API
        self.base_search_shelf_id_api = constants.Supplier.WALMART_SEARCH_SHELF_ID_API  # NOQA
        self.paginate_urls = []
        self.product_count = 0
        self.supplier_id = constants.Supplier.WALMART_CODE

    def fetch_items(self):
        self.items = StlproAPI().get_category_suppliers(
            self.supplier_id, self.limit, self.offset
        )
        self.total_item = len(self.items)

    def build_api_url(self, item):
        url = item['url']
        regex = r"/\d{3,9}\_\d{3,9}\?|/\d{3,9}\_\d{3,9}$|/\d{3,9}_\d{3,9}_\d{3,9}\?|\d{3,9}_\d{3,9}_\d{3,9}$|/\d{3,9}_\d{3,9}_\d{3,9}_\d{3,9}\?|/\d{3,9}_\d{3,9}_\d{3,9}_\d{3,9}$|/\d{3,9}_\d{3,9}_\d{3,9}_\d{3,9}_\d{3,9}\?|/\d{3,9}_\d{3,9}_\d{3,9}_\d{3,9}_\d{3,9}$"  # NOQA
        matches = re.findall(regex, url, re.MULTILINE)
        cat_str = ''
        if matches:
            cat_str = matches[0]
            cat_str = cat_str.strip('/').strip('?')
        parsed = furl(url)
        if 'grocery' in url:
            extended_uri = ''
            if 'aisle' in url:
                extended_uri = '&{}={}'.format(
                    'taxonomyNodeId', parsed.args['aisle']
                )
            elif 'shelfId' in url:
                extended_uri = '&{}={}'.format(
                    'shelfId', parsed.args['shelfId']
                )
            return self.base_grocery_api + extended_uri
        elif '_be_shelf_id' in url:
            return self.base_search_shelf_id_api.format(_be_shelf_id=parsed.args['_be_shelf_id'])  # NOQA
        elif 'cat_id=' in url:
            return self.base_search_api.format(cat_id=parsed.args['cat_id'])
        elif cat_str:
            return self.base_search_api.format(cat_id=cat_str)
        return url

    def process(self):
        try:
            self.page.goto('https://www.walmart.com/grocery/?veh=wmt')
            self.page.wait_for_timeout(random.randint(10000, 15000))
        except TimeoutError:
            LOGGER.error('TimeoutError')
            return
        if self.captcha_detected():
            # enable static file loading
            self.page.route(
                re.compile(r"(\.png)|(\.jpg)|(\.svg)|(\.jpeg)|(\.js)"),
                lambda route: route.continue_()
            )
            self.page.reload()
            self.resolve_captcha(self.current_proxy['ip'])
            LOGGER.error("[Captcha] get {}".format(self.current_proxy['ip']))

        for item in self.items:
            try:
                self.process_item(item)
            except CaptchaResolveException as ex:
                raise ex
            except Exception as e:
                LOGGER.exception(str(e), exc_info=True)
                traceback.print_exc()
                continue

    def process_item(self, item):
        LOGGER.info(
            "=============== Start scrape category: {name} ===========\n {url}".format(  # NOQA
                name=item['name'], url=item['url']
            ))
        item['ip'] = self.current_proxy['ip']
        # abort static file loading
        self.page.route(
            re.compile(r"(\.png)|(\.jpg)|(\.svg)|(\.jpeg)|(\.js)"),
            lambda route: route.abort()
        )
        start_url = self.build_api_url(item)
        self.paginate_urls = []
        self.product_count = 0
        self.paginate_urls.append(start_url)

        while self.paginate_urls:
            url = self.paginate_urls.pop(0)
            LOGGER.info(url)
            try:
                response = self.page.goto(url, wait_until="domcontentloaded")
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
                self.parse(response, url)
        item['product_count'] = self.product_count

    def update_result(self):
        if not self.total_item or not self.items:
            return
        self.update_scraped_results()
        for item in self.items:
            if not item['product_count']:
                continue
            StlproAPI().update_product_count(
                category_supplier_id=item['id'],
                product_count=item['product_count']
            )

    def parse(self, response, url):
        base_url = url.split('?')[0]
        if base_url in constants.Supplier.WALMART_SEARCH_API:
            return self.process_search_api_data(response)
        else:
            return self.process_grocery_api_data(response)

    def process_search_api_data(self, response):
        data = response.json()
        base_url = response.request.url.split('?')[0]
        rows = data['items']
        next_page = data.get('pagination', {}).get('next', {}).get('url')
        if next_page:
            next_url = '{}?{}'.format(base_url, next_page)
            self.paginate_urls.append(next_url)

        for row in rows:
            try:
                result = deepcopy(settings.BASE_SCRAPED_ITEM)
                # variants = row.get('variants', {}).get('variantData')
                # if variants:
                #     variant = variants[0]
                available_online = row.get('inventory', {}).get('availableOnline', False)  # NOQA
                current_price = None
                savings_amount = None
                savings_percent = None
                if row.get('primaryOffer') and available_online:
                    current_price = self.get_price(row['primaryOffer'])
                    list_price = self.get_list_price(row['primaryOffer'])
                    if list_price is None:
                        list_price = current_price
                    if current_price is not None:
                        savings_amount = list_price - current_price
                        savings_amount = round(savings_amount, 3)
                        savings_percent = round(float(savings_amount) / list_price, 2)  # NOQA
                in_stock_for_shipping = available_online
                is_limited_qty = row['is_limited_qty']
                if is_limited_qty:
                    quantity_limit = 12
                else:
                    quantity_limit = 99
                result.update({
                    'proxy': self.current_proxy['ip'],
                    'item_id': row['usItemId'],
                    'original_item_id': row['usItemId'],
                    'description': row['title'],
                    'upc': row['standardUpc'][0],
                    'price': current_price,
                    'saving_amount': savings_amount,
                    'saving_percent': savings_percent,
                    'in_stock_for_shipping': in_stock_for_shipping,
                    'brand': row.get('brand', [])[0],
                    'quantity_limit': quantity_limit,
                    'is_limited_qty': is_limited_qty,
                    'quantity': row['quantity'],  # quantity_available
                    'specials': row.get('specialOfferText'),
                    'seller_name': row['sellerName'],
                    'url': 'https://www.walmart.com' + row['productPageUrl'],
                })
                LOGGER.info(result)
                self.results.append(result)
                self.product_count += 1
            except Exception as ex:
                LOGGER.exception(msg=str(ex), exc_info=True)
                continue

    def process_grocery_api_data(self, response):
        data = response.json()
        total_count = data.get('totalCount', 0)
        url_parsed = furl(response.request.url)
        count = int(url_parsed.args.get('count', '60'))
        offset = int(url_parsed.args.get('offset', '0'))
        page = int(url_parsed.args.get('page', '1'))
        next_offset = offset + count
        if next_offset < total_count:
            page += 1
            offset = next_offset
            url_parsed.args['count'] = count
            url_parsed.args['offset'] = offset
            url_parsed.args['page'] = page
            next_url = url_parsed.url
            self.paginate_urls.append(next_url)
        rows = data.get('products', [])
        for row in rows:
            try:
                result = deepcopy(settings.BASE_SCRAPED_ITEM)
                current_price = row['store']['price']['displayPrice']
                list_price = row['store']['price']['list']
                savings_amount = list_price - current_price
                savings_amount = round(savings_amount, 3)
                savings_percent = None
                if (current_price is not None) and (savings_amount is not None):  # NOQA
                    savings_percent = round(float(savings_amount) / list_price, 2)  # NOQA
                in_stock_for_shipping = not row['store']['isOutOfStock']
                quantity_limit = row['basic']['maxAllowed']
                is_limited_qty = True
                if quantity_limit and quantity_limit >= 12:
                    quantity_limit = 99
                    is_limited_qty = False

                result.update({
                    'proxy': self.current_proxy['ip'],
                    'item_id': row['USItemId'],
                    'original_item_id': row['USItemId'],
                    'description': row['basic']['name'],
                    'upc': None,
                    'price': current_price,
                    'saving_amount': savings_amount,
                    'saving_percent': savings_percent,
                    'in_stock_for_shipping': in_stock_for_shipping,
                    'brand': None,
                    'model': None,
                    'shipping_surcharge': None,
                    'quantity_limit': quantity_limit,
                    'is_limited_qty': is_limited_qty,
                    'quantity': None,  # quantity_available
                    'categories': None,
                    'specials': None,
                    'seller_name': None,
                    'url': 'https://www.walmart.com' + row['basic']['productUrl']  # NOQA
                })
                LOGGER.info(result)
                self.results.append(result)
                self.product_count += 1
            except Exception as ex:
                LOGGER.exception(msg=str(ex), exc_info=True)
                continue

    def get_list_price(self, price_map):
        list_price = price_map.get('listPrice')
        if not list_price:
            list_price = price_map.get('wasPrice')
        if not list_price:
            list_price = price_map.get('price')
        if not list_price:
            list_price = price_map.get('minPrice')  # "productType": "REGULAR"
        return list_price

    def get_price(self, price_map):
        current_price = price_map.get('offerPrice')
        if not current_price:
            current_price = price_map.get('minPrice')  # "productType": "VARIANT"  # NOQA
        return current_price
