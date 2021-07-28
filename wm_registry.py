import sys
import time
import random
import time
from playwright.sync_api import sync_playwright
from libs.admin import AdminManager


if __name__ == "__main__":
    ds_order_ids = []
    with sync_playwright() as playwright:
        db = AdminManager(playwright, use_chrome=True, use_proxy=False)
        ds_order_ids = db.get_ds_orders()
    if (len(ds_order_ids) != 0):
        with sync_playwright() as playwright:
            db = AdminManager(playwright, use_chrome=True, use_proxy=False)
            
