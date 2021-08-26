import json
from datetime import datetime
import random
import traceback
# import sentry_sdk

from playwright.sync_api import sync_playwright

import settings
from libs.exception import CaptchaResolveException
from settings import (
    LOGGER,
    BUY_PROXIES_PASSWORD, BUY_PROXIES_USERNAME
)
from libs.api import StlproAPI


class BaseScraper:
    def __init__(self, supplier_id=None, **kwargs):
        self.active = kwargs.get('active', 1)
        self.offset = kwargs.get('offset', 0)
        self.limit = kwargs.get('limit', 25)
        self.retry = 0
        self.max_retry = 3
        self.total_item = None
        self.start_time = datetime.utcnow()
        self.results = []
        self.items = []
        self.browser = None
        self.page = None
        self.supplier_id = supplier_id
        self.current_proxy = None

    def get_proxy(self):
        self.proxies = StlproAPI().get_proxy_ips(
            supplier_id=self.supplier_id
        )
        if not self.proxies:
            raise

    def initial_browser(self, playwright):
        ip = random.choice(self.proxies)
        self.current_proxy = ip
        firefox = playwright.firefox
        browser = firefox.launch(
            timeout=60000,
            headless=False,
            proxy={
                "server": '{}:{}'.format(ip['ip'], ip['port']),
                "username": BUY_PROXIES_USERNAME,
                "password": BUY_PROXIES_PASSWORD
            },
            firefox_user_prefs={
                'media.peerconnection.enabled': False,
                'privacy.trackingprotection.enabled': True,
                'privacy.trackingprotection.socialtracking.enabled': True,
                'privacy.annotate_channels.strict_list.enabled': True,
                'privacy.donottrackheader.enabled': True,
                'privacy.sanitize.pending': [
                    {
                        "id": "newtab-container", "itemsToClear": [],
                        "options": {}
                    }
                ],
            }
        )
        self.browser = browser
        LOGGER.info('Start new browser with proxy {}'.format(ip['ip']))
        return browser

    def create_new_page(self):
        self.page = self.browser.new_page()

    def process(self):
        for item in self.items:
            try:
                self.process_item(item)
            except CaptchaResolveException as ex:
                raise ex
            except Exception as e:
                LOGGER.exception(str(e), exc_info=True)
                traceback.print_exc()
                continue

    def fetch_items(self):
        raise NotImplementedError

    def process_item(self, item):
        raise NotImplementedError

    def update_result(self):
        raise NotImplementedError

    def update_scraped_results(self):
        if not self.results:
            return False
        self.page.goto(
            settings.IMPORT_CURRENT_PRODUCT_SCRAPED_DATA_URL,
            timeout=60000
        )
        # login
        self.page.fill("input[id=id_username]", settings.BUYBOT_USERNAME)
        self.page.fill("input[id=id_password]", settings.BUYBOT_PASSWORD)
        self.page.click("input[type=submit]")
        self.page.wait_for_timeout(5000)
        end_time = datetime.utcnow()
        start_time_str = self.start_time.strftime(settings.DATETIME_FORMAT)
        end_time_str = end_time.strftime(settings.DATETIME_FORMAT)
        file_name = f'{start_time_str}_{end_time_str}_{self.total_item}.txt'
        # fill form
        self.page.select_option("select[id=id_last_scraped_by]", str(settings.PLAYWRIGHT))  # NOQA
        self.page.select_option("select[id=id_supplier]", self.supplier_id)
        buffer = '\n'.join([json.dumps(row) for row in self.results])
        # Upload buffer from memory
        self.page.set_input_files(
            "input[id=id_file]",
            files=[
                {
                    "name": file_name, "mimeType": "text/plain",
                    "buffer": buffer.encode()
                }
            ],
        )
        self.page.click('button[class="btn btn-outline-primary"]')
        self.page.wait_for_timeout(random.randint(3000, 5000))
        print(self.page.url)

    def run(self):
        LOGGER.debug('Starting: %s' % self.__class__.__name__)
        self.fetch_items()
        self.get_proxy()
        with sync_playwright() as playwright:
            while self.retry < self.max_retry:
                try:
                    self.initial_browser(playwright)
                    self.create_new_page()
                    self.process()
                    self.update_result()
                    return True
                except CaptchaResolveException:
                    traceback.print_exc()
                    self.retry += 1
                    if self.browser:
                        self.browser.close()
                    continue
                except Exception as ex:
                    # sentry_sdk.capture_exception()
                    traceback.print_exc()
                    if self.browser:
                        self.browser.close()
                    LOGGER.exception(msg=str(ex), exc_info=True)
                    raise ex
            LOGGER.exception('Max retry exceed!')
            return False
