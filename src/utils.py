import requests
import time
import json
import os
import threading
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
        
def json_logger(session, link, message, file):
    dictionary_json = dict()
    session.dictionary[link] = message
    dictionary_json.update({
        session.login : {}
        })
    dictionary_json[session.login].update(session.dictionary)
    if os.stat(os.path.abspath(file.name)).st_size != 0:
        loaded_json = json.load(file)
        loaded_json.update(dictionary_json)
        dictionary_json = loaded_json
        file.truncate(0)
    json.dump(dictionary_json, file, indent=4, ensure_ascii=False)