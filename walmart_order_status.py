from walmart.walmart_order_status import WalmartOrderStatus

if __name__ == '__main__':
    scraper = WalmartOrderStatus(start=0, end=100)
    scraper.scrape_orders_state()
