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
                )
                self.browser = browser
    
    def open_new_page(self):
        self.run_browser()
        page = self.browser.new_page()
        page.set_default_navigation_timeout(60 * 1000)
        page.set_viewport_size({"width": 1800 + random.randint(0,200), "height": 800 + random.randint(0,200)})
        self.page = page
    
    def go_to_link(self, link):
        self.page.goto(link)
    

    

