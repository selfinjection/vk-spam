import requests
from lxml.html import fromstring
from loguru import logger
import concurrent.futures
import time


def check_links(links, threads=1):
    invalid_titles = ['Post deleted | VK', 'Запись удалена', 'Error | VK']
    result = []
    responses = []
    for link in links:
        responses.append(requests.get(link))
        time.sleep(0.5)
    
    for response in responses:
        html = fromstring(response.content)
        if html.findtext('.//title') in invalid_titles:
            logger.debug(f'{response.url} post DELETED')
            continue
        logger.debug(f'{response.url} post VALID')
        result.append(response.url)
    return result