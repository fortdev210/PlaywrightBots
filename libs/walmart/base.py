import random

from settings import LOGGER


def resolve_captcha(page, ip):
    i = 0
    while page.is_visible('text="Verify your identity"') and i < 3:
        i += 1
        frame = page.frames[-1]
        page_frame = frame.page
        page_frame.hover('div[role="main"]')
        # page_frame.click(random.randint(0, 100), delay=500)  # NOQA
        page_frame.focus('div[role="main"]')
        page_frame.click('div[role="main"]', delay=random.randint(15000, 20000))  # NOQA
        page_frame.wait_for_timeout(random.randint(5000, 10000))
        LOGGER.info("resolve captcha {} {} times".format(ip, i))
    LOGGER.info("[Captcha] resolve end {}".format(ip))
