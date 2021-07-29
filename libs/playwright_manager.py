import sys
import time
import random
import settings

from playwright.sync_api import sync_playwright

class PlaywrightManager:
    def __init__(self,playwright, **kwargs):
        self.playwright = playwright
        self.browser = None
        self.page = None
        self.use_chrome = kwargs.get('use_chrome')
        self.use_proxy = kwargs.get('use_proxy')
        self.use_luminati = kwargs.get('use_luminati')
        self.proxy_ip = kwargs.get('proxy_ip')
        self.proxy_port = kwargs.get('proxy_port')

    def run_browser(self):
        proxy_data = None
        if self.use_luminati == True:
            proxy_data = {
                "server": settings.LUMINATI_DOMAIN,
                "username": settings.LUMINATI_USERNAME,
                "password": settings.LUMINATI_PASSWORD
            }
        if self.use_proxy == True:
            proxy_data = {
                "server": '{}:{}'.format(self.proxy_ip, self.proxy_port),
                "username": settings.PROXY_USER,
                "password": settings.PROXY_PASS
            }
        if self.use_chrome == True:    
            browser = self.playwright.chromium.launch(
                headless=False,
                proxy=proxy_data,
            )
            self.browser = browser
        else:
            browser = self.playwright.firefox.launch(
                    headless=False,
                    devtools=True,
                    proxy=proxy_data,
                    firefox_user_prefs={
                        'media.peerconnection.enabled': False,
                        'privacy.trackingprotection.enabled': True,
                        'privacy.trackingprotection.socialtracking.enabled': True,
                        'privacy.annotate_channels.strict_list.enabled': True,
                        'privacy.donottrackheader.enabled': True,
                        'privacy.sanitize.pending': [
                            {"id": "newtab-container", "itemsToClear": [], "options":{}}
                        ],
                        'devtools.toolbox.host': 'bottom'
                    }
                )
            self.browser = browser
    
    def open_new_page(self):
        page = self.browser.new_page()
        page.set_default_navigation_timeout(60 * 1000)
        page.set_viewport_size({"width": 1800 + random.randint(0,200), "height": 800 + random.randint(0,200)})
        self.page = page 

    def go_to_link(self, link):
        self.page.goto(link)
    
    def insert_value(self, selector, value):
        self.page.type(selector, value, delay=random.randint(100,1000))
    
    def wait_element_loading(self, selector, time=10000):
        self.page.wait_for_selector(selector, timeout=time)

    def reinsert_value(self,selector, value):
        self.page.focus(selector)
        self.page.dblclick(selector)
        self.page.press('Backspace')
        self.insert_value(selector, value)
    
    def press_enter(self):
        self.page.press('Enter')
    
    def reload_page(self):
        self.page.reload(wait_until="load")

        
    


    

