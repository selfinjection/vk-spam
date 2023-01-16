import requests
import time
import json
import os
import threading
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
    
timestamp = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
path_json = f'logs/succeed_post_info_{timestamp}.json'
    
def json_logger(session):
    with threading.Lock():
        if not os.path.exists(path_json):
                open(path_json, "w", encoding='utf-8').close()
                
        with open(path_json, "r", encoding='utf-8') as json_file:
                try:
                    data = json.load(json_file)
                except json.decoder.JSONDecodeError:
                    data = {}
                data[session.login or session.token] = session.dictionary

        with open(path_json, "w", encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)