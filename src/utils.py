import requests
import time, os, json, random
import threading
from lxml.html import fromstring
from loguru import logger
import concurrent.futures
from tqdm import tqdm
import aiohttp
import asyncio

async def check_links_async(links):
    invalid_titles = ['Post deleted | VK', 'Запись удалена', 'Error | VK']
    result, html = [], []
    async with aiohttp.ClientSession() as session:
        for link in tqdm(links, ncols=90, desc='Loading links'):
            response = await session.get(link)
            url = str(response.url).replace('m.', '')
            #html = fromstring(await response.text())
            html.append([await response.text(), url])
            await asyncio.sleep(0.03)

    for content, url in html:
        invalid_titles = ['Post deleted | VK', 'Запись удалена', 'Error | VK']
        c = fromstring(content)
        if c.findtext('.//title') in invalid_titles:
                continue
        result.append(url)
    print(f"Valid posts: {len(result)}\n{'*'*90}")
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
    return message

def log_json(dicts):
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
    path_json = f'logs/succeed_post_info_{timestamp}.json'

    counter = 0
    result = {}

    for d in dicts:
        result[d['credentials']] = d['job_result']
        counter += len(d['job_result'])
    result['total_requests'] = counter
    with open(path_json, 'w', encoding='utf-8') as file:
        json.dump(result, file, indent=4, ensure_ascii=False)
        
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