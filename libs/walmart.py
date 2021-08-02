import settings
import random
import re
import time
import os
from .playwright_manager import PlaywrightManager
from .utils import schedule_date, get_full_state_name


class WalmarManager(PlaywrightManager):
    def __init__(self, playwright, **kwargs):
        super().__init__(playwright, **kwargs)
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
        state = get_full_state_name(self.reg_order_info['state'])
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
        


    
       


    