from urllib.parse import urlparse
import requests
from lxml.html import fromstring
from loguru import logger

### TODO: replace with a regular expression 
### https://vk.com/wall-42446186_33429 -> [-42446186, 33429]
def wall_link_parse(link: str):
    return urlparse(link).path[5:].split('_')

def check_link(link):
    invalid_titles = ['Post deleted | VK', 'Запись удалена', 'Error | VK']

    response = requests.get(link)
    response = fromstring(response.content)
    if response.findtext('.//title') in invalid_titles:
        logger.error(f'{link} post DELETED')
        return False
    return True