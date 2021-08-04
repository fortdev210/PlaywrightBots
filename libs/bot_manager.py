import os
import random
import time

from playwright.sync_api import sync_playwright

from settings import LUMINATI_USERNAME, LUMINATI_PASSWORD, LUMINATI_DOMAIN, PROXY_USER, PROXY_PASS,
from .utils import get_dsh_extension


class BotManager:
    def __init__(self, **kwargs):
        self.playwright = None
        self.browser = None
        self.page = None
        self.use_chrome = kwargs.get('use_chrome')
        self.use_proxy = kwargs.get('use_proxy')
        self.use_luminati = kwargs.get('use_luminati')
        self.proxy_ip = kwargs.get('proxy_ip')
        self.proxy_port = kwargs.get('proxy_port')

    def start_playwright(self):
        playwright = sync_playwright().start()
        self.playwright = playwright

    def stop_playwright(self):
        self.playwright.stop()

    def run_browser(self):
        proxy_data = None
        if self.use_luminati == True:
            proxy_data = {
                "server": LUMINATI_DOMAIN,
                "username": LUMINATI_USERNAME,
                "password": LUMINATI_PASSWORD
            }
        if self.use_proxy == True:
            proxy_data = {
                "server": '{}:{}'.format(self.proxy_ip, self.proxy_port),
                "username": PROXY_USER,
                "password": PROXY_PASS
            }
        if self.use_chrome == True:    
            browser = self.playwright.chromium.launch_persistent_context(
                headless=False,
                proxy=proxy_data,
                user_data_dir = os.getcwd() + '/user_tmp',
                args = [
                    f"--disable-extensions-except={os.getcwd()+'/extensions/dropship-helper'}",
                    f"--load-extension={os.getcwd()+'/extensions/dropship-helper'}",
                ]
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
    
    def check_element(self, selector):
        self.page.check(selector)

    def reload_page(self):
        self.page.reload(wait_until="load")
    
    def click_element(self, selector):
        self.page.click(selector, delay=random.randint(0,10))

    def select_option(self, selector, **kwargs):
        if kwargs.get('option_selector') == 'label':
            self.page.select(selector, label=kwargs.get('option_value'))
        elif kwargs.get('option_selector') == 'index':
            self.page.select(selector, index=kwargs.get('option_value'))
        elif kwargs.get('option_selector') == 'value':
            self.page.select(selector, value=kwargs.get('option_value'))
        
    def manage_proxy_by_dsh(self, flag, proxy_info=None):
        targets = self.browser.background_pages()
        dsh_extension = filter(get_dsh_extension, targets)
        ip = ''
        port = ''
        if proxy_info == None:
            ip = '127.0.0.1'
            port = str(random.randint(24000, 24100))
        else:
            ip = proxy_info[0]
            port = proxy_info[1]
        
        if flag == 'ON':
            content = """(ip, port) => {
                setProxyWebF(ip, port);
            }, (ip, port)"""
            dsh_extension.evaluate(content)
        else:
            content = """() => { proxyOffWebF()}"""
            dsh_extension.evaluate(content)
        
    def sleep(seconds):
        time.sleep(seconds)
    

