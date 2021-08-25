import sys
import time

from homedepot.order_status import HomeDepotOrderStatusScraper


if __name__ == "__main__":
    offset = int(sys.argv[1])
    limit = int(sys.argv[2])

    while True:
        scraper = HomeDepotOrderStatusScraper(offset=offset, limit=limit)
        scraper.run()
        time.sleep(5 * 60)  # sleep 5 mins
