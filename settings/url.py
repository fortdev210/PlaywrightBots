import os


BASE_URL = os.environ.get("BASE_URL")
UPDATE_DS_ORDER_INFO_URL = BASE_URL + "v2/ds_order/{ds_order_id}/update_order_status_scraped_result/"  # NOQA
GET_DS_ORDERS_URL = BASE_URL + "v2/ds_order/scrape_order_status/?supplier_id={supplier_id}"  # NOQA
GET_PROXIES_URL = BASE_URL + "v2/ip_supplier/?is_potential_banned=false&is_buyproxies_ip=true&supplier={supplier_id}&limit=500&batch_id=order_status"  # NOQA
CONFIRMED_BY = 5  # Playwright bot

WALMART_PREP_ORDERS_LINK = BASE_URL + "products/order_items/new/?supplier=-1&box_size=-1&dummy=None&flag=Walmart+Prep{bot_number}&quantity_ordered=-1&ship_service_level=All&free_delivery=-1&az_account=" 
WALMART_BUY_ORDERS_LINK = BASE_URL + "products/order_items/new/?supplier=-1&box_size=-1&dummy=None&flag=Walmart+PP{bot_number}&quantity_ordered=-1&ship_service_level=All&free_delivery=-1&az_account="
WALMART_PRIO_ORDERS_LINK = BASE_URL + "products/order_items/new/?supplier=-1&box_size=-1&dummy=None&flag=Walmart+Priority&quantity_ordered=-1&ship_service_level=All&az_account="
WALMART_REBUY_ORDERS_LINK = BASE_URL + "products/order_items/new/?supplier=W&box_size=-1&dummy=None&flag=Walmart+Rebuy{bot_number}&quantity_ordered=-1&ship_service_level=All&free_delivery=-1&az_account="
WALMART_REG_LINK = "https://www.walmart.com/account/signup?returnUrl=%2Flists%2Fcreate-events-registry%3Fr%3Dyes"
WALMART_ITEM_LINK = "http://www.walmart.com/ip/{item}?selected=true"
WALMART_CART_LINK = "https://www.walmart.com/cart"