import sys
import time

from libs.walmart.product_scraper import WalmartProductScraper

from settings import LOGGER


if __name__ == "__main__":
    active = int(sys.argv[1])
    start = int(sys.argv[2])
    end = int(sys.argv[3])
    offset = int(start)
    limit = int(end) - int(start)
    while True:
        try:
            scraper = WalmartProductScraper(
                active=active,
                offset=offset,
                limit=limit
            )
            scraper.run()
        except Exception as ex:
            LOGGER.exception(str(ex), exc_info=True)
        time.sleep(10)
