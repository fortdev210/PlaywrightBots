import sys
import logging

UPDATE_DS_ORDER_INFO_URL = "https://admin.stlpro.com/v2/ds_order/{ds_order_id}/update_order_status_scraped_result/"  # NOQA
GET_DS_ORDERS_URL = "https://admin.stlpro.com/v2/ds_order/scrape_order_status/?supplier_id={supplier_id}"  # NOQA
GET_PROXIES_URL = "https://admin.stlpro.com/v2/ip_supplier/?is_potential_banned=false&is_buyproxies_ip=true&supplier={supplier_id}&limit=500&batch_id=order_status"  # NOQA
BUYBOT_USER = 'buybot'
BUYBOT_PASS = 'forte1long'
CONFIRMED_BY = 5  # Playwright bot

PROXY_USER = 'stlpro'
PROXY_PASS = 'forte1'
LUMINATI_DOMAIN = 'zproxy.lum-superproxy.io:22225'
LUMINATI_USERNAME = 'lum-customer-c_62f63918-zone-residential2-country-us'
LUMINATI_PASSWORD = 'bf1b7c15d2de'

WALMART = 'W'
WM_CURRENT_PASSWORD = 'Forte1long!'
WM_OLD_PASSWORD = 'forte1long'
WM_SELF_RESOLVE_CAPTCHA = True

HOMEDEPOT = 'P'

WALMART_PREP_ORDERS_LINK = "http://admin.stlpro.com/products/order_items/new/?supplier=-1&box_size=-1&dummy=None&flag=Walmart+Prep{bot_number}&quantity_ordered=-1&ship_service_level=All&free_delivery=-1&az_account=" 
WALMART_BUY_ORDERS_LINK = "http://admin.stlpro.com/products/order_items/new/?supplier=-1&box_size=-1&dummy=None&flag=Walmart+PP{bot_number}&quantity_ordered=-1&ship_service_level=All&free_delivery=-1&az_account="
WALMART_PRIO_ORDERS_LINK = "http://admin.stlpro.com/products/order_items/new/?supplier=-1&box_size=-1&dummy=None&flag=Walmart+Priority&quantity_ordered=-1&ship_service_level=All&az_account="
WALMART_REBUY_ORDERS_LINK = "http://admin.stlpro.com/products/order_items/new/?supplier=W&box_size=-1&dummy=None&flag=Walmart+Rebuy{bot_number}&quantity_ordered=-1&ship_service_level=All&free_delivery=-1&az_account="
WALMART_REG_LINK = "https://www.walmart.com/account/signup?returnUrl=%2Flists%2Fcreate-events-registry%3Fr%3Dyes"
WALMART_ITEM_LINK = "http://www.walmart.com/ip/{item}?selected=true"
WALMART_CART_LINK = "https://www.walmart.com/cart"

file_handler = logging.FileHandler(
    'logs/' + sys.modules['__main__'].__file__.replace('.py', '.log'),
    mode='a',
    delay=0
)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # NOQA
file_handler.setFormatter(formatter)
LOGGER = logging.getLogger(
    sys.modules['__main__'].__file__.replace('.py', '.log')
)
LOGGER.addHandler(file_handler)
LOGGER.addHandler(logging.StreamHandler())
LOGGER.setLevel(logging.DEBUG)
