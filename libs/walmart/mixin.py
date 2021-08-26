import random
import time

from settings import LOGGER


class WalmartMixin(object):
    def captcha_detected(self):
        time.sleep(3)
        if self.page.is_visible('div[class="captcha re-captcha"]'):
            return True
        return False

    def resolve_captcha(self, ip):
        i = 0
        captcha_detected = self.captcha_detected()
        while captcha_detected and i < 3:
            i += 1
            frame = self.page.frames[-1]
            page_frame = frame.page
            page_frame.hover('div[role="main"]')
            page_frame.focus('div[role="main"]')
            page_frame.click('div[role="main"]', delay=random.randint(15000, 20000))  # NOQA
            page_frame.wait_for_timeout(random.randint(5000, 10000))
            LOGGER.info("resolve captcha {} {} times".format(ip, i))
            captcha_detected = self.captcha_detected()
        LOGGER.info("[Captcha] resolve end {}".format(ip))
        return captcha_detected
