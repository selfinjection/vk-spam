import requests
import time, os, json, random
import threading
from lxml.html import fromstring
from loguru import logger
import concurrent.futures

timestamp = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
path_json = f'logs/succeed_post_info_{timestamp}.json'


def check_links(links, threads=1):
    invalid_titles = ['Post deleted | VK', 'Запись удалена', 'Error | VK']
    result, responses = [], []
    for link in links:
        responses.append(requests.get(link))
        logger.debug(f'{link} loaded...')
        time.sleep(0.5)
    
    for response in responses:
        url = response.url.replace('m.', '')
        html = fromstring(response.content)
        if html.findtext('.//title') in invalid_titles:
            logger.debug(f'{url} post DELETED')
            continue
        logger.debug(f'{url} post VALID')
        result.append(url)
    return result

def change_letter(message):
    cyrillic_codes = [1072, 1086, 1077] # cyrillic "а, о, е"
    latin_codes = [97, 111, 101] # latin "а, о, е"
    letter_index = [i for i, ltr in enumerate(message) if ord(ltr) in cyrillic_codes]
    if letter_index:
        letter_index = random.choice(letter_index)
        cyr_code = ord(message[letter_index])
        lat_code = latin_codes[cyrillic_codes.index(cyr_code)]
        change_or_not = random.choices([True, False], cum_weights=[97/100, 1])
        if change_or_not[0]:
            message = message[:letter_index] + chr(lat_code) + message[letter_index+1:]
            print(letter_index)
    return message

def json_logger(session):
    posts = len(session.dictionary.items()) - 1
    logger.info(f'{posts} posts have been done (Account: {session.credential})')
    with threading.Lock():
        if not os.path.exists(path_json):
                open(path_json, "w", encoding='utf-8').close()
                
        with open(path_json, "r", encoding='utf-8') as json_file:
                try:
                    data = json.load(json_file)
                except json.decoder.JSONDecodeError:
                    data = {}
                if 'total' not in data:
                    data['total'] = 0
                data['total'] += posts
                data[session.credential] = session.dictionary
                data[session.credential]['posts'] = posts

        with open(path_json, "w", encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)

# TODO: call total_posts_log() after all threads finished execution
'''
def total_posts_log():
    with open(path_json, "r", encoding='utf-8') as json_file:
        data = json.load(json_file)
        total = data['TOTAL']
        logger.info(f'TOTAL: {total} posts')
        
def check_alive_threads():
    while True: 
        alive_threads = [t for t in threading.enumerate() if t.is_alive() and t != threading.current_thread()]
        if len(alive_threads) <= 1:
            if len(alive_threads) == 1:
                alive_threads[0].join()
            total_posts_log()
            break
        print('checking...')
        time.sleep(1)
'''