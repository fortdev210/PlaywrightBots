import settings
import time
import us

from .bot_manager import BotManager
from .utils import schedule_date, get_full_state_name


class WalmarManager(BotManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reg_order_info = kwargs.get('reg_order_info')

    def open_sign_up_page(self):
        if self.browser == None:
            self.run_browser()
        self.open_new_page()
        self.go_to_link(settings.WALMART_REG_LINK)
        
    def open_sign_in_page(self):
        self.open_sign_up_page()
        self.page.wait_for_selector('[data-automation-id="signup-sign-in-btn"]')
        self.page.click('[data-automation-id="signup-sign-in-btn"]')

    def signin_walmart(self):
        self.insert_value('[id="email"]', self.reg_order_info['email'])
        try:
            self.wait_element_loading('[data-automation-id="signin-continue-submit-btn"]', time=10000)
            print("New signin page.")
            self.press_enter()
            self.insert_value('[id="password"]', settings.WM_CURRENT_PASSWORD)
            self.press_enter()
        except:  
            print("Old signin page now.")
            self.insert_value('[id="password"]', settings.WM_CURRENT_PASSWORD)
            self.click_element('[data-automation-id="signin-submit-btn"]')
            try:
                self.page.wait_element_loading("text=Your password and email do not match.", time=10000)
                self.reinsert_value('[id="password"]', settings.WM_OLD_PASSWORD)
                self.click_element('[data-automation-id="signin-submit-btn"]')
            except:
                pass

    def signup_walmart(self):
        self.wait_element_loading('[id="first-name-su"]')
        self.insert_value('[id="first-name-su"]', self.reg_order_info['firstName'])
        self.insert_value('[id="last-name-su"]', self.reg_order_info['lastName'])
        self.insert_value('[id="email-su"]', self.reg_order_info['email'])
        self.insert_value('[id="password-su"]', settings.WM_CURRENT_PASSWORD)
        self.click_element('[id="su-newsletter"]')
        time.sleep(3)
        self.wait_element_loading('[data-automation-id="signup-submit-btn"]')
        self.click_element('[data-automation-id="signup-submit-btn"]')

    def add_event_date(self):
        event_date = schedule_date()
        try:
            self.wait_element_loading('#eventDate')
            self.insert_value('[id="eventDate"]', event_date)
        except:
            self.reload_page()
            self.wait_element_loading('#eventDate')
            self.insert_value('[id="eventDate"]', event_date)
    
    def add_location(self):
        state = us.states[self.reg_order_info['state']]
        self.wait_element_loading('#regstate')
        self.insert_value("#regstate", state)
    
    def add_organization(self):
        self.wait_element_loading('#lastname')
        self.reinsert_value('#lastname', self.reg_order_info['lastName'])
 
    def remove_old_address(self):
        try:
            self.wait_element_loading('[class="shipping-address-footer"]')
            self.click_element('[class*="delete-button "]')
        except:
            print('No old address found')
            pass
    
    def add_personal_data(self):
        try:
            self.wait_element_loading('#firstName')
        except:
            self.reload_page()
            self.add_event_date()
            self.add_location()
            self.add_organization()
            self.remove_old_address()
        self.insert_value('#firstName', self.reg_order_info['firstName'])
        self.insert_value('#lastName', self.reg_order_info['lastName'])
        self.insert_value('#phone', self.reg_order_info['phoneNum'])
        self.insert_value('#addressLineOne', self.reg_order_info['addressOne'])
        self.insert_value('#addressLineTwo', self.reg_order_info['addressTwo'])
        self.insert_value('#city', self.reg_order_info['city'])
        self.insert_value('#state', self.reg_order_info['state'])
        self.insert_value('#postalCode', self.reg_order_info['zipCode'])
        self.click_element('[data-automation-id="address-form-submit"]')
        print('All information successfully registered')

    def register_customer_info(self):
        self.add_event_date()
        self.add_location()
        self.add_organization()
        self.remove_old_address()
        self.add_personal_data()
    
    def make_registry_public(self):
        # check make registry public
        self.wait_element_loading("text=Make my registry public")
        content = """() => {
            document
            .querySelectorAll(".LNR-PrivacyOptions")[0]
            .childNodes[1].querySelector("input").click()
        }"""
        self.page.evaluate(content)
        # click looking goog button
        time.sleep(3)
        self.click_element("text=Looking good, create it!")
    
    def verify_address(self):
        try:
            self.wait_element_loading('[class*="alert-warning"]', 20000)
            time.sleep(1)
            self.click_element('[data-automation-id="address-form-submit"]')
        except:
            pass

        try:
            self.wait_element_loading('[class="validation-wrap"]', 30000)
            time.sleep(1)
            self.click_element('[class*="button-save-address"]')
        except:
            pass
    
    def check_registration_status(self):
        time.sleep(5)
        current_url = self.page.url
        if "created" in current_url:
            return True
        return False

    def add_primary_item(self):
        primary_item_link = settings.WALMART_ITEM_LINK.format(self.reg_order_info['primaryItem'])
        self.open_new_page()
        self.go_to_link(primary_item_link)
        self.wait_element_loading('[class*="AddToRegistry-text"]', 30000)
        self.click_element('[class*="AddToRegistry-text"]')
        self.wait_element_loading('[class="Registry-btn-row"]', 30000)
        content = """()=> {
            document
            .querySelector('[class="Registry-btn-row"]')
            .querySelector("button").click()
        }"""
        self.page.evaluate(content)
        self.wait_element_loading('[class="select-field"]')
        time.sleep(2)
        self.click_element('[data-tl-id="cta_add_to_cart_button"]')
        print("Primary Item Added.")

        # Add qty in the cart
        if self.reg_order_info['qty'] != 1:
            try:
                self.go_to_link(settings.WALMART_CART_LINK)
                self.wait_element_loading('[class*="field-input "]', 45000)
                self.select_option('[aria-label="Quantity"]', label=self.reg_order_info['qty'])
            except:
                print("Error: Should reload page")
                self.reload_page()
                self.wait_element_loading('[class*="field-input "]', 45000)
                self.select_option('[aria-label="Quantity"]', label=self.reg_order_info['qty'])
    
    def add_extra_item(self):
        extra_item_link = settings.WALMART_ITEM_LINK.format(self.reg_order_info['extraItem'])
        self.open_new_page()
        self.go_to_link(extra_item_link)
        self.wait_element_loading('[data-tl-id="ProductPrimaryCTA-cta_add_to_cart_button"]')
        time.sleep(2)
        self.click_element('[data-tl-id="ProductPrimaryCTA-cta_add_to_cart_button"]')
        
    def wm_register(self):
        self.manage_proxy_by_dsh('ON', [self.reg_order_info['ip'], self.reg_order_info['port']])
        time.sleep(3)
        self.open_sign_in_page()
        if self.reg_order_info['extraItem'] != None:
            self.signin_walmart()
        else:
            self.signup_walmart()
        self.manage_proxy_by_dsh('OFF')
        self.register_customer_info()
        self.verify_address()
        self.make_registry_public()
        registered = self.check_registration_status()
        
        if registered == True:
            self.page.close()
            self.add_primary_item()
            if self.reg_order_info['extraItem'] != None:
                self.add_extra_item()
            else:
                pass
