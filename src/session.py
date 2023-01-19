# https://dev.vk.com/method/
import vk_captchasolver as vc
import sys
from urllib.parse import urlparse
from vk_api import VkApi, AuthError, ApiError, Captcha
from loguru import logger as log
import random
import os
import threading
from src.utils import change_letter
from twocaptcha import TwoCaptcha
from tqdm import tqdm

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
    key = input('\nEnter captcha code {}: '.format(captcha.get_url())).strip()
    return captcha.try_again(key)


class Session():
    def __init__(self, login=None, password=None, token=None):
        self.log_lock = threading.Lock()
        self.credential = login or token[:11]
        try:
            if token:
                session = VkApi(token=token, captcha_handler=captcha_handler)
            else:
                session = VkApi(login, password, captcha_handler=captcha_handler)
                session.auth()
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
        result = {
            'credentials': self.credential,
            'job_result': {}
        }
        for lnk in tqdm(links, desc=f'id: {random.randint(0, 100)}', ncols=90, unit=' post'):
            owner_id, post_id = urlparse(lnk).path[5:].split('_')
            message = change_letter(random.choice(messages))
            try:
                response = self.session.wall.createComment(owner_id=owner_id, post_id=post_id, message=message)
                result['job_result'][lnk] = message
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
                    log.error(f'{response} | {owner_id}_{post_id}, {self.credential}')
                pass
        return result