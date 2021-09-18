import sys
import random
import time

from constants import Supplier
from libs.walmart.walmart_order_status import WalmartOrderStatus
from settings import LOGGER
from libs.api import StlproAPI

if __name__ == '__main__':
    start = int(sys.argv[1])
    end = int(sys.argv[2])
    while True:
        orders = StlproAPI().get_ds_orders(supplier_id=Supplier.WALMART_CODE)
        LOGGER.info(f"Get {len(orders)} orders")
        proxies = StlproAPI().get_proxy_ips(Supplier.WALMART_CODE)
        orders = orders[start:end]
        random.shuffle(orders)

        for order in orders:
            LOGGER.info('-------------------------------------------')
            LOGGER.info(order)
            proxy = random.choice(proxies)
            proxy_ip = proxy.get('ip')
            proxy_port = proxy.get('port')
            LOGGER.info('proxy: {proxy_ip}:{proxy_port}'.format(
                proxy_ip=proxy_ip, proxy_port=proxy_port))
            bot = WalmartOrderStatus(
                use_chrome=False, use_luminati=False, use_proxy=True,
                proxy_ip=proxy_ip, proxy_port=proxy_port, order=order
            )
            try:
                bot.run()
            except Exception as ex:
                LOGGER.exception(ex, exc_info=True)
            finally:
                bot.close_browser()
            LOGGER.info('')
        time.sleep(5*60)
