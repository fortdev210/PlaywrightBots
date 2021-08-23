from datetime import datetime
import random
import traceback
# import sentry_sdk

from playwright.sync_api import sync_playwright

from libs.exception import CaptchaResolveException
from settings import (
    LOGGER,
    BUY_PROXIES_PASSWORD, BUY_PROXIES_USERNAME
)

from libs.utils import get_proxy_ips


class BaseScraper(object):
    def __init__(self, supplier_id, **kwargs):
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
        self.proxies = get_proxy_ips(supplier_id=self.supplier_id)['results']
        if not self.proxies:
            raise

    def initial_browser(self, playwright):
        ip = random.choice(self.proxies)
        self.current_proxy = ip
        firefox = playwright.firefox
        browser = firefox.launch(
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
                    self.browser.close()
                    continue
                except Exception as ex:
                    # sentry_sdk.capture_exception()
                    traceback.print_exc()
                    self.browser.close()
                    LOGGER.exception(msg=str(ex), exc_info=True)
                    raise ex
            LOGGER.exception('Max retry exceed!')
            return False
