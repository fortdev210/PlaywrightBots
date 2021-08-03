import settings
import random
import re
import time
import os
from .utils import get_orders_link, get_correct_state, get_hostname
from .playwright_manage import PlaywrightManager


class AdminManager(PlaywrightManager):
    def __init__(self, playwright,  **kwargs):
        super().__init__(playwright, **kwargs)

    def admin_login(self):
        self.page.type('[name="username"]', settings.BUYBOT_USER, delay=random.randint(0,100))
        self.page.type('[name="password"]', settings.BUYBOT_PASS, delay=random.randint(0,100))
        self.page.click('[type="submit"]')

    def init_step(self):
        self.run_browser()
        self.open_new_page()
    
    def get_ds_orders(self):
        """
        Get ds orders from the certain folder to process
        """
        order_link = get_orders_link()
        self.init_step()
        self.go_to_link(order_link)
        self.admin_login() 
        try:
            self.page.wait_for_selector("text=There is no matched Item", timeout=10000)
            print("There is no orders at the moment.")
            self.browser.close()
            return []
        except:
            pass

        javascript_expression = '''() => {
            document.querySelector('th[class="sorting"]').innerText = "ItemScrapeMe"
            var ths = document.querySelector('[id="itemsSearch"]').getElementsByTagName("th")
            var trs = document.querySelector('[id="itemsSearch"]').getElementsByTagName("tr")
            orderItemColumn = []
            for (var i = 0; i < ths.length; i++) {
                if (ths[i].innerHTML.indexOf("ItemScrapeMe") !== -1) {
                if (ths[i].innerHTML == "i am gay") {
                    // do nothing
                } else {
                    var oicId = i;
                    break;
                }
                }
            }
            for (var i = 0; i < trs.length; i++) {
                orderItemColumn.push(trs[i].children[oicId]);
            }
            scrapedOrderItemIDs = [];
            for (var i = 0; i < orderItemColumn.length; i++) {
                if (i < 2) {
                // fuck off
                } else {
                scrapedOrderItemIDs.push(orderItemColumn[i].innerText);
                }
            }
            return scrapedOrderItemIDs
        }
        '''
        order_item_ids = self.page.evaluate(javascript_expression)
        time.sleep(3)
        self.browser.close()
        return order_item_ids
    
    def get_order_details(self, current_order_id):
        """
        Get detailed order information and ip and port
        """
        ds_link = "http://admin.stlpro.com/products/getdsorders/"
        self.init_step()
        self.go_to_link(ds_link)
        try:
            self.page.wait_for_selector('[name="password"]', timeout=5000)
            self.admin_login()
        except:
            pass
        
        self.page.wait_for_selector('[name="object_type"]')
        content = '''() => {
            return (document.querySelector('[name="object_type"]').selectedIndex = 1);
        }'''
        self.page.evaluate(content)
        self.page.type('[id="orders"]', current_order_id)
        self.page.click('[value="Submit"]')
        self.page.wait_for_selector('[id="updateAllItemsForm"]')
        
        # ds for chrome 
        self.browser.new_page()
        self.go_to_link("http://admin.stlpro.com/products/getdsforchrome/")
        self.wait_element_loading('#picked_ip')
        
        # get proxy ip and port from db
        ip = self.page.inner_text('#picked_ip')
        port = self.page.inner_text('#picked_port')

        # get order id  
        order_id = self.page.inner_text('[id="ds_order_id"]')

        # get drop ship info
        content = '''() => {
            var customer_info = document
                .querySelector('[id*="for_button_"]')
                .innerHTML.replace("&amp;", "&");
            try {
                var customerEmail = document.querySelector(
                '[id="picked_username"]'
                ).innerHTML;
            } catch (error) {
                var customerEmail = document.querySelector(
                '[id="picked_email"]'
                ).innerHTML;
            }

            if (
                document
                .querySelectorAll('[class="slimcell"]')[11]
                .querySelector("a") !== null
            ) {
                var freeshipItem = document
                .querySelectorAll('[class="slimcell"]')[11]
                .querySelector("a").innerHTML;
            } else {
                var freeshipItem = "N/A";
            }
            if (
                document.querySelectorAll('[class="slimcell"]')[7].innerHTML.trim() ==
                "1"
            ) {
                var primaryItemQty = "1";
            } else {
                var primaryItemQty = document
                .querySelectorAll('[class="slimcell"]')[7]
                .querySelector("em").innerHTML;
            }
            var price = parseFloat(
                document.querySelectorAll(".slimcell")[8].innerText
            );
            return [customer_info, customerEmail, freeshipItem, primaryItemQty, price];
        }'''
        dropship_info = self.page.evaluate(content)
        
        customer_info = dropship_info[0].split('|')
        
        if len(customer_info[7])> 5:
            customer_info[7] = customer_info[7][0:5]
        customer_info[8] = re.sub('\D', "", customer_info[8])
        customer_info[9] = get_correct_state(customer_info[9])

        clean_customer_info = {}
        clean_customer_info['supplier'] = customer_info[0]
        clean_customer_info['primaryItem'] = customer_info[1]
        clean_customer_info["extraItem"] = dropship_info[2]
        clean_customer_info['orderId'] = order_id
        hostname = get_hostname()
        if ('rebuy' in hostname.lower()):
            clean_customer_info['firstName'] =  re.sub('[^A-Za-z]','', customer_info[3]) 
            clean_customer_info['lastName'] = re.sub('[^A-Za-z]','', customer_info[2]) 
        else:
            clean_customer_info['firstName'] = re.sub('[^A-Za-z]','', customer_info[2]) 
            clean_customer_info['lastName'] = re.sub('[^A-Za-z]','', customer_info[3]) 
        
        clean_customer_info['addressOne'] = re.sub('[&\/\\_+():$"~%*?<>®-]','', customer_info[4])
        clean_customer_info['addressTwo'] = re.sub('[&\/\\_+():$"~%*?<>®-]','', customer_info[5])
        clean_customer_info['city'] = customer_info[6]
        clean_customer_info['zipCode'] = customer_info[7]
        clean_customer_info['phoneNum'] = customer_info[8]
        clean_customer_info['state'] = customer_info[9]
        clean_customer_info['email'] = dropship_info[1]
        clean_customer_info['qty'] = dropship_info[3]
        clean_customer_info['price'] = dropship_info[4]
        customer_info = clean_customer_info
        
        
        if customer_info['firstName'] != "" and customer_info['lastName'] == "":
            customer_info['lastName'] = customer_info['firstName']
        elif customer_info['firstName'] == "" and customer_info['lastName'] != "":
            customer_info['firstName'] = customer_info['lastName']


        if (len(customer_info['phoneNum']) == 11):
            customer_info['phoneNum'] = customer_info['phoneNum'][1:10]
        

        if customer_info['phoneNum'][0] == "0":
            customer_info['phoneNum'] = "314" + customer_info['phoneNum'][3:10]
        

        if customer_info.get('addressOne') == "" and customer_info.get('addressTwo') != "":
            customer_info['addressOne'] = customer_info.get('addressTwo')
            customer_info['addressTwo'] = ""
        customer_info['ip'] = ip
        customer_info['port'] = port
        self.browser.close()
        return customer_info