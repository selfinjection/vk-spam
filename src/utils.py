import requests
import time, os, json, random
from lxml.html import fromstring
from loguru import logger
from urllib.parse import urlparse
from src.screenshot import Screenshot
from tqdm.asyncio import tqdm
import aiohttp
import asyncio
from selenium  import webdriver
from selenium.webdriver.common.by import By

async def check_links_async(links):
    invalid_titles = ['Post deleted | VK', 'Запись удалена', 'Error | VK']
    result, html = [], []
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        sem = asyncio.Semaphore(10)
        for link in tqdm(links, ncols=90, desc='Links'):
            await sem.acquire()
            task = asyncio.create_task(session.get(link))
            task.add_done_callback(lambda _: sem.release())
            tasks.append(task)
            await asyncio.sleep(0.1)
            
        for fut in asyncio.as_completed(tasks):
            response = await fut
            text = await response.text()
            html.append([text, str(response.url).replace('m.', '')])

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

# Concept
def get_screenshots(links):
    driver = webdriver.Chrome()
    driver.maximize_window()
    ob = Screenshot()
    for link in links:
        driver.get(link)
        owner_id, post_id = urlparse(link).path[5:].split('_')
        driver.implicitly_wait(3)
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        driver.execute_script("window.scrollTo(0, 0)")
        box_wrap = driver.find_element(By.ID, 'box_layer_wrap')
        box_bg = driver.find_element(By.ID, 'box_layer_bg')
        driver.execute_script("arguments[0].remove();", box_wrap)
        driver.execute_script("arguments[0].remove();", box_bg)
        img_url = ob.full_Screenshot(driver, save_path=r'./imgs', image_name=f'wall{owner_id}_{post_id}.png', multi_images=True)
    driver.close()