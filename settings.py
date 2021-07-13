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

file_handler = logging.FileHandler(
    'logs/' + sys.modules['__main__'].__file__.replace('.py', '.log'),
    mode='a',
    delay=0
)
LOGGER = logging.getLogger(
    sys.modules['__main__'].__file__.replace('.py', '.log')
)
LOGGER.addHandler(file_handler)
LOGGER.addHandler(logging.StreamHandler())
LOGGER.setLevel(logging.DEBUG)
