import datetime
import json
import random
import re
import traceback

from playwright._impl._api_types import TimeoutError

import constants
import settings
from libs.exception import CaptchaResolveException
from libs.utils import find_value_by_markers, get_json_value_by_key_safely
from libs.walmart.mixin import WalmartMixin
from settings import LOGGER
from libs.base_scraper import BaseScraper


class WalmartDepartmentScraper(WalmartMixin, BaseScraper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_search_api = constants.Supplier.WALMART_SEARCH_API
        self.base_search_shelf_id_api = constants.Supplier.WALMART_SEARCH_SHELF_ID_API  # NOQA
        self.category_count = 0
        self.supplier_id = constants.Supplier.WALMART_CODE
        self.not_complete_categories = []
        self.categories = []

    def fetch_items(self):
        self.items = constants.Supplier.WALMART_DEPARTMENTS
        self.total_item = len(self.items)

    def process(self):
        try:
            self.page.goto('https://www.walmart.com/grocery/?veh=wmt')
            self.page.wait_for_timeout(random.randint(10000, 15000))
        except TimeoutError:
            LOGGER.error('TimeoutError')
            return
        if self.captcha_detected():
            LOGGER.error("[Captcha] get {}".format(self.current_proxy['ip']))
            # enable static file loading
            self.page.route(
                re.compile(r"(\.png)|(\.jpg)|(\.svg)|(\.jpeg)|(\.js)"),
                lambda route: route.continue_()
            )
            self.page.reload()
            self.resolve_captcha(self.current_proxy['ip'])

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
            "=============== Start scrape department: ===========\n {url}".format(  # NOQA
                url=item['url']
            ))
        item['ip'] = self.current_proxy['ip']
        # abort static file loading
        self.page.route(
            re.compile(r"(\.png)|(\.jpg)|(\.svg)|(\.jpeg)|(\.js)"),
            lambda route: route.abort()
        )
        start_url = item['url']
        self.paginate_urls = []
        self.category_count = 0

        try:
            response = self.page.goto(start_url, wait_until="domcontentloaded")
        except TimeoutError:
            LOGGER.error('TimeoutError')
            return
        if self.page.is_visible('text="Verify your identity"'):
            # enable static file loading
            self.page.route(
                re.compile(r"(\.png)|(\.jpg)|(\.svg)|(\.jpeg)|(\.js)"),
                lambda route: route.continue_()
            )
            self.page.reload()
            self.resolve_captcha(item['ip'])
            LOGGER.error("[Captcha] get {}".format(item['ip']))
            return
        else:
            self.parse(response)

    def update_result(self):
        result_file_name = "{}/logs/walmart/department_scraped_result_{}.json".format(  # NOQA
            settings.BASE_DIR,
            datetime.datetime.now().strftime(settings.DATETIME_FORMAT)
        )
        with open(result_file_name, '+a') as fp:
            fp.write(json.dumps(self.categories))
        print("Complete!")

    def parse(self, response):
        leading = ["<script id=\"category\" type=\"application/json\">"]
        trailing = "</script>"
        json_string = find_value_by_markers(
            response, leading, trailing
        )
        json_object = json.loads(json_string)
        data = get_json_value_by_key_safely(
            json_object,
            ['category', 'presoData', 'modules', 'left']
        )
        categories = {}
        for item in data:
            if item.get('moduleTitle') == 'Shop by Category':
                categories = item
                break
        if not categories:
            return
        department_name = categories['category']
        for category in categories['data']:
            for sub_category in category.get('subMenuData', []):
                sub_category_name = '{} / {} / {}'.format(
                    department_name, category['title'], sub_category['title']
                )
                if constants.Supplier.WALMART_BASE_URL not in sub_category['url']:  # NOQA
                    sub_category_url = '{}{}'.format(
                        constants.Supplier.WALMART_BASE_URL, sub_category['url']  # NOQA
                    )
                else:
                    sub_category_url = sub_category['url']
                item = {
                    'name': sub_category_name,
                    'supplier': self.supplier_id
                }
                if constants.Supplier.WALMART_BASE_BROWSER_URL in sub_category_url:  # NOQA
                    item['url'] = sub_category_url
                    self.categories.append(item)
                else:
                    # ex: https://www.walmart.com/cp/drones-by-brand/5960206
                    # uid: 3944_5525941
                    # will redirect to https://www.walmart.com/browse/drones/drones-by-brand/3944_5525941_5960206  # NOQA
                    category_id = sub_category_url.rsplit('/', 1)[-1]
                    item['url'] = '{}?cat_id={}_{}'.format(
                        sub_category_url, category.get('uid'), category_id
                    )
                LOGGER.info(item)
