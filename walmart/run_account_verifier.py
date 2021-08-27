import random
from datetime import datetime, timedelta

from constants.verifier_type import VerifierType
from constants.supplier import Supplier
from settings import LOGGER, DATETIME_FORMAT
from libs.api import StlproAPI
from libs.walmart.walmart_verifier import WalmartVerifier


if __name__ == '__main__':
    verifier_type = VerifierType.ACCOUNT_VERIFIER
    last_used_date = (datetime.utcnow() - timedelta(days=90)
                      ).strftime(DATETIME_FORMAT).replace('T', ' ')
    emails = StlproAPI().get_account_supplier(
        last_used_date=last_used_date)

    proxies = StlproAPI().get_proxy_ips(Supplier.WALMART_CODE)
    for email in emails:
        LOGGER.info('-------------------------------------------')
        LOGGER.info(email)
        proxy = random.choice(proxies)
        proxy_ip = proxy.get('ip')
        proxy_port = proxy.get('port')
        LOGGER.info('proxy: {proxy_ip}:{proxy_port}'.format(
            proxy_ip=proxy_ip, proxy_port=proxy_port))
        bot = WalmartVerifier(
            use_chrome=False, use_luminati=False, use_proxy=True,
            proxy_ip=proxy_ip, proxy_port=proxy_port,
            email=email, verifier_type=verifier_type)

        bot.run()
        LOGGER.info('')
