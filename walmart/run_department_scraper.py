import time

from libs.walmart.department_scraper import WalmartDepartmentScraper

from settings import LOGGER


if __name__ == "__main__":
    while True:
        try:
            scraper = WalmartDepartmentScraper(
                offset=0,
                limit=0
            )
            scraper.run()
        except Exception as ex:
            LOGGER.exception(str(ex), exc_info=True)
            time.sleep(60)
        else:
            print("Sleep {}hs".format(12))
            time.sleep(3600*12)
