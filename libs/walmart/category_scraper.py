import json
import random
import re
import traceback
from copy import deepcopy

from furl import furl
from playwright._impl._api_types import TimeoutError

import constants
import settings
from libs.exception import CaptchaResolveException
from libs.utils import find_value_by_markers, clean_number
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

        # some category do not have more than one page of products
        # so it's api return []
        # so we use this flag for mark the request is success
        # but empty in response
        self.has_response = None

    def fetch_items(self):
        self.items = StlproAPI().get_category_suppliers(
            self.supplier_id, self.limit, self.offset
        )
        self.total_item = len(self.items)

    def build_api_url(self, item):
        url = item['url']
        regex = r"/\d{3,9}\_\d{3,9}\?|/\d{3,9}\_\d{3,9}$|/\d{3,9}_\d{3,9}_\d{3,9}\?|\d{3,9}_\d{3,9}_\d{3,9}$|/\d{3,9}_\d{3,9}_\d{3,9}_\d{3,9}\?|/\d{3,9}_\d{3,9}_\d{3,9}_\d{3,9}$|/\d{3,9}_\d{3,9}_\d{3,9}_\d{3,9}_\d{3,9}\?|/\d{3,9}_\d{3,9}_\d{3,9}_\d{3,9}_\d{3,9}$|/\d{3,9}_\d{3,9}_\d{3,9}_\d{3,9}_\d{3,9}_\d{3,9}\?|/\d{3,9}_\d{3,9}_\d{3,9}_\d{3,9}_\d{3,9}_\d{3,9}$"  # NOQA
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
        item['has_response'] = False
        self.has_response = False  # reset flag
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
                self.parse(response)
        item['product_count'] = self.product_count
        item['has_response'] = self.has_response

    def update_result(self):
        for item in self.items:
            if not item.get('has_response', False):
                continue
            StlproAPI().update_product_count(
                category_supplier_id=item['id'],
                product_count=item['product_count']
            )

        if not self.total_item or not self.items:
            return
        self.update_scraped_results()

    def parse(self, response):
        self.has_response = True  # set flag if successful fetch
        base_url = response.url.split('?')[0]
        if base_url in constants.Supplier.WALMART_SEARCH_API:
            return self.process_search_api_data(response)
        else:
            return self.process_grocery_api_data(response)

    def process_search_api_data(self, response):
        leading = ['<script id="__NEXT_DATA__" type="application/json"']  # NOQA
        trailing = "</script>"
        json_string = find_value_by_markers(
            response, leading, trailing
        )
        json_string = json_string.split('>', 1)[1]
        data = json.loads(json_string)
        rows = data['props']['pageProps']['initialData']['searchResult']['itemStacks'][0]['items']  # NOQA
        max_page = data['props']['pageProps']['initialData']['searchResult']['paginationV2']['maxPage']  # NOQA
        if max_page:
            url_parsed = furl(response.request.url)
            current_page = int(url_parsed.args['page'])
            if current_page < max_page:
                url_parsed.args['page'] = current_page + 1
                next_url = url_parsed.url
                self.paginate_urls.append(next_url)

        for row in rows:
            typename = row.get('__typename')
            if typename != 'Product':
                LOGGER.error(row)
                LOGGER.error("This item is not a product!")
                continue
            try:
                result = deepcopy(settings.BASE_SCRAPED_ITEM)
                # variants = row.get('variants', {}).get('variantData')
                # if variants:
                #     variant = variants[0]
                available_online = not row.get('isOutOfStock')
                current_price = row.get('price')
                savings_amount = None
                savings_percent = None
                if row.get('priceInfo') and available_online:
                    if not current_price:
                        current_price = self.get_new_price(row['priceInfo'])
                    list_price = self.get_new_list_price(row['priceInfo'])
                    if not list_price:
                        list_price = current_price
                    savings_amount = list_price - current_price
                    savings_percent = round(savings_amount / list_price, 2)  # NOQA
                in_stock_for_shipping = available_online
                # is_limited_qty = row.get('is_limited_qty')
                # if is_limited_qty:
                #     quantity_limit = 12
                # else:
                #     quantity_limit = 99
                is_limited_qty = True  # FIXME not parsed yet
                quantity_limit = 12  # FIXME not parsed yet
                brands = row.get('brand')
                if brands:
                    brand = brands[0]
                else:
                    brand = ''
                result.update({
                    'proxy': self.current_proxy['ip'],
                    'item_id': row['usItemId'],
                    'original_item_id': row['usItemId'],
                    'description': row['name'],
                    'upc': None,
                    'price': current_price,
                    'saving_amount': savings_amount,
                    'saving_percent': savings_percent,
                    'in_stock_for_shipping': in_stock_for_shipping,
                    'brand': brand,
                    'quantity_limit': quantity_limit,
                    'is_limited_qty': is_limited_qty,
                    'quantity': row.get('quantity'),  # quantity_available
                    'specials': row.get('specialOfferText'),
                    'seller_name': row['sellerName'],
                    'url': 'https://www.walmart.com' + row['canonicalUrl'],
                })
                LOGGER.info(result)
                self.results.append(result)
                self.product_count += 1
            except Exception as ex:
                LOGGER.exception(row)
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
                savings_amount = round(list_price - current_price, 2)
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

    def get_new_list_price(self, price_map):
        list_price = price_map.get('listPrice')
        if not list_price:
            list_price = price_map.get('wasPrice')
        if not list_price:
            list_price = price_map.get('linePrice')
        # if not list_price:
        #     list_price = price_map.get('minPrice')  # "productType": "REGULAR"  # NOQA
        return clean_number(list_price)

    def get_price(self, price_map):
        current_price = price_map.get('offerPrice')
        if not current_price:
            current_price = price_map.get('minPrice')  # "productType": "VARIANT"  # NOQA
        return current_price

    def get_new_price(self, price_map):
        current_price = price_map.get('linePrice')
        if not current_price:
            current_price = price_map.get('minPriceForVariant')  # "productType": "VARIANT"  # NOQA
        return clean_number(current_price)
