import requests
from lxml.html import fromstring
from loguru import logger

def check_links(links):
    result = []
    for link in links:
        invalid_titles = ['Post deleted | VK', 'Запись удалена', 'Error | VK']
        response = requests.get(link)
        response = fromstring(response.content)
        if response.findtext('.//title') in invalid_titles:
            logger.debug(f'{link} post DELETED')
            continue
        logger.debug(f'{link} post VALID')
        result.append(link)
    return result