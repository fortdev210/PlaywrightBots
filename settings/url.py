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
GET_EMAIL_SUPPLIER = BASE_URL + \
    "v2/email_supplier_verify/?status=0&supplier=W&limit=500"
GET_ACCOUNT_SUPPLIER = BASE_URL + \
    "v2/account_supplier_verify/?status=0&supplier=W&last_used_at_from={last_used_at_from}&limit=10000"
UPDATE_EMAIL_STATUS = BASE_URL + "v2/email_supplier/"
UPDATE_ACCOUNT_STATUS = BASE_URL + "v2/account_supplier/"
GET_CURRENT_PRODUCT_URL = BASE_URL + "v2/current_product/get_item_for_scrape/?use_scraped_url={active}&limit={limit}&offset={offset}&supplier_id={supplier_id}&active={active}"  # NOQA
IMPORT_CURRENT_PRODUCT_SCRAPED_DATA_URL = BASE_URL + \
    "admin/login/?next=/history/import_current_product_scraped_data/"
GET_CATEGORY_SUPPLIER_URL = BASE_URL + \
    'v2/category_supplier/?supplier={supplier_id}&limit={limit}&offset={offset}'
UPDATE_CATEGORY_SUPPLIER_URL = BASE_URL + \
    'v2/category_supplier/{category_supplier_id}/'
GET_EXTRA_ITEM_CANCEL_URL = BASE_URL + \
    'v2/ds_order/?buyer_name=&ds_status_filter=Purchased+Acknowledged+Confirmed&extra_items=Extra+Item&extra_items_canceled=NOT+canceled&finished=&not_found=&ordering=-ended_at&paid=&started_at_filter=Last+7+days&supplier=W'

WALMART_REG_LINK = 'https://www.walmart.com/account/login'
WALMART_ACCOUNT_LINK = 'https://www.walmart.com/account/profile'
WALMART_ORDER_HISTORY_LINK = "https://www.walmart.com/account/wmpurchasehistory"
WALMART_CART_LINK = "https://www.walmart.com/cart"
WALMART_REGISTRY_LINK = "https://www.walmart.com/lists/manage-events-registry-settings"
WALMART_PAYMENT_METHODS_LINK = "https://www.walmart.com/account/creditcards"
