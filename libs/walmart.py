import random
import re

from settings import LOGGER, WM_SELF_RESOLVE_CAPTCHA


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
    # page.goto('https://bing.com')
    # page.fill('input[id="sb_form_q"]', 'walmart.com')
    # page.keyboard.press('Enter')
    # page.fill("input[id='DeepLinkDD_c']", 'lcd')
    # page.keyboard.press('Enter')
    # page.wait_for_timeout(1000)

    url = random.choice(urls)
    page.goto(url)
    page.wait_for_timeout(random.randint(3000, 10000))
    email = order['email'] or order['username']
    page.fill("input[id=email]", email)
    page.wait_for_timeout(random.randint(1000, 5000))
    page.fill("input[id=password]", password)
    page.wait_for_timeout(random.randint(1000, 5000))
    page.click("button[type=submit]")
    page.wait_for_timeout(random.randint(5000, 10000))
    if page.is_visible('div[class="captcha re-captcha"]'):
        LOGGER.error("[Captcha] get {}".format(order['ip']['ip']))
        if WM_SELF_RESOLVE_CAPTCHA:
            resolve_captcha(page, order['ip']['ip'])
    else:
        LOGGER.info("[Captcha] none {}".format(order['ip']['ip']))
    page.goto(
        'https://www.walmart.com/account/wmpurchasehistory',
        wait_until="networkidle"
    )
    page.wait_for_timeout(random.randint(5000, 12000))
    pattern = re.search(
        "window.__WML_REDUX_INITIAL_STATE__ = (.*?);<\/script>",  # NOQA
        page.content()
    )
    data = pattern[0].replace(
        'window.__WML_REDUX_INITIAL_STATE__ = ', ''
    ).replace(';</script>', '')
    return data


def resolve_captcha(page, ip):
    i = 0
    while page.is_visible('div[class="captcha re-captcha"]') and i < 3:
        i += 1
        frame = page.frames[-1]
        page_frame = frame.page
        page_frame.hover('div[role="main"]')
        page_frame.click(random.randint(0, 100), random.randint(0, 100), delay=500)  # NOQA
        page_frame.focus('div[role="main"]')
        page_frame.click('div[role="main"]', delay=random.randint(15000, 20000))  # NOQA
        page_frame.wait_for_timeout(random.randint(5000, 10000))
        LOGGER.info("resolve captcha {} {} times".format(ip, i))
    LOGGER.info("[Captcha] resolve end {}".format(ip))
