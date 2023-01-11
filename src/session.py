# https://dev.vk.com/method/

from vk_api import VkApi, AuthError, ApiError
from loguru import logger

### TODO: make a captcha solver with AI
def captcha_handler(captcha):
    key = input('Enter captcha code {}: '.format(captcha.get_url())).strip()
    return captcha.try_again(key)

### TODO: improvement
### add a proxy
class Session():
    def __init__(self, login, password):
        self.log = logger
        self.log.add("logs/file_{time}.log")
        self.login = login
        try:
            session = VkApi(login, password, captcha_handler=captcha_handler)
            session.auth()
        except AuthError as e:
             raise SystemExit('Auth failed')
        self.log.info(f'Auth completed ({self.login})')
        self.session = session.get_api()

    def __str__(self):
        return f'{self.session}'

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
        try:
            response = self.session.wall.createComment(owner_id=owner_id, post_id=post_id, message=message)
            self.log.success(f'{response} | wall{owner_id + "_" + post_id} | Account: {self.login}')
            return response
        except ApiError as e:
            self.log.error(f'{e} | wall{owner_id + post_id} | Account: {self.login}')
            return e