import socket
HOST_NAME = socket.gethostname()

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"   # 2021-08-08T01:01:01
PLAYWRIGHT = 2  # constants.CurrentProductScrapedBy.PLAYWRIGHT
CONFIRMED_BY = 5  # Playwright bot
SCRAPED_BY_BOTNAME = 'PW-{}'.format(HOST_NAME)
SCRAPER_BATCH_ID = '8889'
BASE_SCRAPED_ITEM = {
    'removed': False,
    'proxy': None,
    'item_id': None,
    'original_item_id': None,
    'description': None,
    'upc': None,
    'price': None,
    'saving_amount': None,
    'saving_percent': None,
    'in_stock_for_shipping': False,
    'brand': None,
    'model': None,
    'shipping_surcharge': None,
    'quantity_limit': None,
    'categories': None,
    'specials': None,
    'quantity': None,
    'seller_name': None,
    'stock_status': None,
    'url': None,
    'user_agent': None,
    'keep_original_item': True,
    'scraped_by_botname': SCRAPED_BY_BOTNAME,
}
