import os


BASE_URL = os.environ.get("BASE_URL")
UPDATE_DS_ORDER_INFO_URL = BASE_URL + "v2/ds_order/{ds_order_id}/update_order_status_scraped_result/"  # NOQA
GET_DS_ORDERS_URL = BASE_URL + "v2/ds_order/scrape_order_status/?supplier_id={supplier_id}"  # NOQA
SET_ORDER_FLAG_URL = BASE_URL + "v1/order_item/{ds_order_id}"
GIFT_CARD_SEND_TOTAL_URL = BASE_URL + "v2/ds_order/{ds_order_id}"
GIFT_CARD_SEND_CURRENT_CARD_URL = BASE_URL + \
    "v2/ds_order/{ds_order_id}/update_gift_card_usage/"
GIFT_CARD_GET_NEXT_CARD_URL = BASE_URL + \
    "v2/ds_order/{ds_order_id}/next_gift_card/"
GET_PROXIES_URL = BASE_URL + "v2/ip_supplier/?is_potential_banned=false&is_buyproxies_ip=true&supplier={supplier_id}&limit=500&batch_id=order_status"  # NOQA
CONFIRMED_BY = 5  # Playwright bot
WALMART_REG_LINK = 'https://www.walmart.com/account/login'
GET_EMAIL_SUPPLIER = BASE_URL + \
    "v2/email_supplier_verify/?status=0&supplier=W&email_type=0&limit=500"
UPDATE_EMAIL_STATUS = BASE_URL + "v2/email_supplier_verify/"
