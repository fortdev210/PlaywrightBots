import sys
import time

from libs.walmart.category_scraper import WalmartCategoryScraper

from settings import LOGGER


if __name__ == "__main__":
    start = int(sys.argv[1])
    end = int(sys.argv[2])
    offset = int(start)
    limit = int(end) - int(start)
    while True:
        try:
            scraper = WalmartCategoryScraper(
                offset=offset,
                limit=limit
            )
            scraper.run()
        except Exception as ex:
            LOGGER.exception(str(ex), exc_info=True)
        time.sleep(60)
