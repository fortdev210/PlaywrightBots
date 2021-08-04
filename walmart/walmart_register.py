import us

from libs.utils import schedule_date
from settings import LOGGER, WALMART_ITEM_LINK, WALMART_CART_LINK
from .walmart_base import WalmartBase


class WalmartRegister(WalmartBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
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
        state = us.states[self.order_info['state']]
        self.wait_element_loading('#regstate')
        self.insert_value("#regstate", state)
    
    def add_organization(self):
        self.wait_element_loading('#lastname')
        self.reinsert_value('#lastname', self.order_info['lastName'])
 
    def remove_old_address(self):
        try:
            self.wait_element_loading('[class="shipping-address-footer"]')
            self.click_element('[class*="delete-button "]')
        except:
            LOGGER.info("--- No old address found")
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
        self.insert_value('#firstName', self.order_info['firstName'])
        self.insert_value('#lastName', self.order_info['lastName'])
        self.insert_value('#phone', self.order_info['phoneNum'])
        self.insert_value('#addressLineOne', self.order_info['addressOne'])
        self.insert_value('#addressLineTwo', self.order_info['addressTwo'])
        self.insert_value('#city', self.order_info['city'])
        self.insert_value('#state', self.order_info['state'])
        self.insert_value('#postalCode', self.order_info['zipCode'])
        self.click_element('[data-automation-id="address-form-submit"]')
        LOGGER.info('All information successfully registered')

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
        self.sleep(3)
        self.click_element("text=Looking good, create it!")
    
    def verify_address(self):
        try:
            self.wait_element_loading('[class*="alert-warning"]', 20000)
            self.sleep(2)
            self.click_element('[data-automation-id="address-form-submit"]')
        except:
            pass

        try:
            self.wait_element_loading('[class="validation-wrap"]', 30000)
            self.sleep(2)
            self.click_element('[class*="button-save-address"]')
        except:
            pass
    
    def check_registration_status(self):
        self.sleep(3)
        current_url = self.page.url
        if "created" in current_url:
            return True
        return False

    def add_primary_item(self):
        primary_item_link = WALMART_ITEM_LINK.format(self.order_info['primaryItem'])
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
        self.sleep(2)
        self.click_element('[data-tl-id="cta_add_to_cart_button"]')
        LOGGER.info("--- Primar Item Added")

        # Add qty in the cart
        if self.order_info['qty'] != 1:
            try:
                self.go_to_link(WALMART_CART_LINK)
                self.wait_element_loading('[class*="field-input "]', 45000)
                self.select_option('[aria-label="Quantity"]', label=self.order_info['qty'])
            except:
                print("Error: Should reload page")
                self.reload_page()
                self.wait_element_loading('[class*="field-input "]', 45000)
                self.select_option('[aria-label="Quantity"]', label=self.order_info['qty'])
    
    def add_extra_item(self):
        extra_item_link = WALMART_ITEM_LINK.format(self.order_info['extraItem'])
        self.open_new_page()
        self.go_to_link(extra_item_link)
        self.wait_element_loading('[data-tl-id="ProductPrimaryCTA-cta_add_to_cart_button"]')
        self.sleep(2)
        self.click_element('[data-tl-id="ProductPrimaryCTA-cta_add_to_cart_button"]')
        
    def wm_register(self):
        self.manage_proxy_by_dsh('ON', [self.order_info['ip'], self.order_info['port']])
        self.sleep(3)
        self.open_sign_in_page()
        if self.order_info['extraItem'] != None:
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
            if self.order_info['extraItem'] != None:
                self.add_extra_item()
            else:
                pass