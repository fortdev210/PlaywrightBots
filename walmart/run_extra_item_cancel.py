import time
import random

from libs.walmart.walmart_cancel_extra_item import WalmartCancelExtraItem
from libs.api import StlproAPI
from settings import LOGGER
from constants import Supplier

if __name__ == '__main__':
    while True:
        orders = StlproAPI().get_extra_item_cancel_orders()
        LOGGER.info(f"Get {len(orders)} orders")
        proxies = StlproAPI().get_proxy_ips(Supplier.WALMART_CODE)

        for order in orders:
            LOGGER.info('-------------------------------------------')
            proxy = random.choice(proxies)
            proxy_ip = proxy.get('ip')
            proxy_port = proxy.get('port')
            LOGGER.info('proxy: {proxy_ip}:{proxy_port}'.format(
                proxy_ip=proxy_ip, proxy_port=proxy_port))
            bot = WalmartCancelExtraItem(
                use_chrome=False, use_luminati=False, use_proxy=True,
                proxy_ip=proxy_ip, proxy_port=proxy_port, order=order
            )
            bot.run()
            LOGGER.info('')
        time.sleep(5*60)
