import os


BASE_URL = os.environ.get("BASE_URL")
UPDATE_DS_ORDER_INFO_URL = BASE_URL + "v2/ds_order/{ds_order_id}/update_order_status_scraped_result/"  # NOQA
GET_DS_ORDERS_URL = BASE_URL + "v2/ds_order/scrape_order_status/?supplier_id={supplier_id}"  # NOQA
GET_PROXIES_URL = "http://admin.stlpro.com/v2/ip_supplier/?is_potential_banned=false&is_buyproxies_ip=true&supplier={supplier_id}&limit=500&batch_id=order_status"  # NOQA
GET_CURRENT_PRODUCT_URL = BASE_URL + "v2/current_product/get_item_for_scrape/?use_scraped_url={active}&limit={limit}&offset={offset}&supplier_id={supplier_id}&active={active}"  # NOQA
IMPORT_CURRENT_PRODUCT_SCRAPED_DATA_URL = BASE_URL + "admin/login/?next=/history/import_current_product_scraped_data/"
WALMART_GROCERY_API = "https://www.walmart.com/grocery/v4/api/products/browse?count=60&offset=0&page=1&storeId=2086"
WALMART_SEARCH_API = "https://www.walmart.com/search/api/preso?page=1&cat_id={cat_id}&facet=retailer:Walmart.com"
