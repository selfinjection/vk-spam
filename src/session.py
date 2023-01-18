# https://dev.vk.com/method/
import vk_captchasolver as vc
import sys
from urllib.parse import urlparse
from vk_api import VkApi, AuthError, ApiError, Captcha
from loguru import logger as log
import random
import time
import threading
from src.utils import json_logger
from twocaptcha import TwoCaptcha

log.add("logs/file_{time}.log")

def captcha_handler(captcha):
    '''
    Working 50%50

    sid = ''
    url = urlparse(captcha.get_url()).query[4:]

    for c in url:
        if c == '&':
            break
        sid = sid + c

    key = vc.solve(s=1, sid=sid)
    time.sleep(1.5)
    logger.info(f"Captacha detected. Solving... {captcha.get_url()}, {key}")
    '''
    #solver = TwoCaptcha('19f9aeb567e6b68b677a353c23db159b')
    #key = solver.normal(captcha.get_url())
    key = input('Enter captcha code {}: '.format(captcha.get_url())).strip()
    return captcha.try_again(key)


class Session():
    def __init__(self, login=None, password=None, token=None):

        self.log_lock = threading.Lock()
        self.credential = login or token[:11]
        self.dictionary = {'posts' : 0}
        try:
            if token:
                session = VkApi(token=token, captcha_handler=captcha_handler)
            session = VkApi(login, password, captcha_handler=captcha_handler)
            session.auth()
            with self.log_lock:
                log.info(f'Auth completed | Accounts: {self.credential})')
        except AuthError as e:
            with self.log_lock:
                log.error(f'Authentication failed: {e} | Account: {self.credential}')
            sys.exit()
        self.session = session.get_api()

    def __str__(self):
        return f'{self.session}'

    def get_session(self):
        return self.session
  
    def comment_posts(self, links, messages):
        vk_url = '{} | wall{}_{} | Account: {}'
        for lnk in links:
            owner_id, post_id = urlparse(lnk).path[5:].split('_')
            message = messages[random.randint(0, len(messages) - 1)]
            try:
                response = self.session.wall.createComment(owner_id=owner_id, post_id=post_id, message=message)
                with self.log_lock:
                    log.success(vk_url.format(response, owner_id, post_id, self.credential))
                self.dictionary[lnk] = message
                code_10_error = 0

            except Captcha as e:
                captcha_handler(e)

            except ApiError as e:
                if e.code == 10:
                    code_10_error += 1
                    if code_10_error == 5: # 5 times in a row an error 10 "internal server error"
                        with self.log_lock:
                            log.warning('The account has probably reached the post limit')
                        break
                with self.log_lock:
                    log.error(vk_url.format(response, owner_id, post_id, self.credential))
                pass
            
        json_logger(self)