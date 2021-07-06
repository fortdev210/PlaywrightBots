import random
import re

from settings import LOGGER


def try_to_scrape(order, page, password):
    LOGGER.info("Login with pass: " + password)
    urls = [
        'https://www.walmart.com/account/login',
        'https://www.walmart.com/account/login?tid=0&returnUrl=%2F',
        'https://www.walmart.com/account/login?tid=0&returnUrl=%2Fcp%2Felectronics%2F3944',  # NOQA
        'https://www.walmart.com/account/login?tid=0&returnUrl=%2Fbrowse%2Felectronics%2Ftouchscreen-laptops%2F3944_3951_1089430_1230091_1101633',  # NOQA
        'https://www.walmart.com/account/login?tid=0&returnUrl=%2Flists',
        'https://www.walmart.com/account/login?tid=0&returnUrl=%2Feasyreorder%3FeroType%3Dlist',  # NOQA

    ]
    url = random.choice(urls)
    page.goto(url)
    page.wait_for_timeout(5000)
    email = order['email'] or order['username']
    page.fill("input[id=email]", email)
    page.wait_for_timeout(1000)
    page.fill("input[id=password]", password)
    page.wait_for_timeout(1000)
    page.click("button[type=submit]")
    page.wait_for_timeout(5000)
    try:
        page.goto(
            'https://www.walmart.com/account/wmpurchasehistory',
            wait_until="networkidle"
        )
    except:
        pass
    page.wait_for_timeout(10000)
    pattern = re.search(
        "window.__WML_REDUX_INITIAL_STATE__ = (.*?);<\/script>",
        page.content()
    )
    data = pattern[0].replace(
        'window.__WML_REDUX_INITIAL_STATE__ = ', ''
    ).replace(';</script>', '')
    return data
