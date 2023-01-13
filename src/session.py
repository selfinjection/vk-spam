# https://dev.vk.com/method/
import vk_captchasolver as vc
import sys
from urllib.parse import urlparse
from vk_api import VkApi, AuthError, ApiError
from loguru import logger
import random
import time
import json
import os
from twocaptcha import TwoCaptcha
### TODO: make a captcha solver with AI (GOVNO CODE NO RABOTAET!)
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

### TODO: improvement
### add a proxy
class Session():
    def __init__(self, login, password):
        self.log = logger
        self.log.add("logs/file_{time}.log")
        self.login = login
        self.dictionary = {}
        try:
            session = VkApi(login, password, captcha_handler=captcha_handler)
            session.auth()
            self.connected = True
        except AuthError as e:
             logger.error(f'Authentication failed: {e} | Account: {self.login}')
             sys.exit()
        self.log.info(f'Auth completed ({self.login})')
        self.session = session.get_api()

    def __str__(self):
        return f'{self.session}'

    def is_connected(self):
        return self.connected

    def get_session(self):
        return self.session

    # TODO: improve error handling 
    def like_post(self, owner_id: int, item_id: int):
        response = self.session.likes.add(type='post', owner_id=owner_id, item_id=item_id)

        if not response:
            raise SystemExit(f'wrong owner_id or/and item_id')
        return response

    # TODO: improve error handling
    # После успешного выполнения возвращает идентификатор добавленного 
    # комментария в поле comment_id (integer) и 
    # массив идентификаторов родительских комментариев в поле parent_stack (array).
    def comment_post(self, owner_id: int, post_id: int, message: str):
        time.sleep(3)
        try:
            response = self.session.wall.createComment(owner_id=owner_id, post_id=post_id, message=message)
            self.log.success(f'{response} | wall{owner_id + "_" + post_id} | Account: {self.login}')
            return response
        except ApiError as e:
            self.log.error(f'{e} | wall{owner_id + post_id} | Account: {self.login}')
            return e

    def comment_posts(self, links, messages):
        spaces = 4
        dictionary_json = {}
        path_json = f'logs/succeed_post_info_{time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())}.json'
        with open(path_json, 'a+', encoding= 'utf-8') as log_json:
            for lnk in links:
                owner_id, post_id = urlparse(lnk).path[5:].split('_')
                try:
                    message = messages[random.randint(0, len(messages) - 1)]
                    response = self.session.wall.createComment(owner_id=owner_id, post_id=post_id, message=message)
                    self.log.success(f'{response} | wall{owner_id + "_" + post_id} | Account: {self.login}')
                    self.dictionary[lnk] = message
                    dictionary_json.update({
                        self.login : {}
                        })
                    dictionary_json[self.login].update(self.dictionary)
                    time.sleep(3)
                except ApiError as e:
                    self.log.error(f'{e} | wall{owner_id + post_id} | Account: {self.login}')
                    pass
            if os.stat(path_json).st_size != 0:
                loaded_json = json.load(log_json)
                loaded_json.update(dictionary_json)
                dictionary_json = loaded_json
                print(dictionary_json)
                log_json.truncate(0)
            log_json.write(json.dumps(dictionary_json, indent=spaces, ensure_ascii=False))


