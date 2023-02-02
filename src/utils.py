import time, os, json, random
from lxml.html import fromstring
from urllib.parse import urlparse
from src.screenshot import Screenshot
from tqdm.asyncio import tqdm
import aiohttp
import asyncio
from dotenv import load_dotenv
from selenium  import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

def check_profile():
    dotenv_path = 'selenium_profile.env'
    load_dotenv(dotenv_path=dotenv_path)

    profile = 'selenium'
    if not os.path.exists(profile):
        os.makedirs(profile)
        profile = os.path.abspath(profile)
        
        options = Options()
        options.headless = True
        options.add_argument(f'user-data-dir={profile}')
        driver = webdriver.Chrome(options=options)
        driver.get("https://vk.com")

        index_email = driver.find_element(By.ID, 'index_email')
        index_email.send_keys(os.getenv('PROFILE_LOGIN'))
        index_email.send_keys(Keys.ENTER)

        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'vkc__TextField__input')))

        pass_element = driver.find_element(By.NAME, 'password')
        pass_element.send_keys(os.getenv('PROFILE_PASSWORD'))
        pass_element.send_keys(Keys.ENTER)
        
        WebDriverWait(driver, 20).until(EC.url_contains('vk.com/feed'))
        driver.quit()
    else:
        profile = os.path.abspath(profile)
        
    return profile

# Concept
def get_screenshots(links):
    options = Options()
    options.headless = True
    options.add_argument(f'user-data-dir={check_profile()}')
    options.add_argument("window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    ob = Screenshot()
    for link in links:
        driver.get(link)
        owner_id, post_id = urlparse(link).path[5:].split('_')
        driver.implicitly_wait(3)
        
        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight); var lenOfPage=document.body.scrollHeight; return lenOfPage;")
        match = False
        while(match == False):
                lastCount = lenOfPage
                time.sleep(0.5)     # Need tests to make it less
                lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight); var lenOfPage=document.body.scrollHeight; return lenOfPage;")
                if lastCount == lenOfPage:
                    match = True
        driver.execute_script("window.scrollTo(0, 0)")
        
        box_wrap = driver.find_element(By.ID, 'box_layer_wrap')
        box_bg = driver.find_element(By.ID, 'box_layer_bg')
        reply_box = driver.find_element(By.ID, f'reply_box_wrap{owner_id}_{post_id}')
        driver.execute_script("for (let i of arguments) {i.remove();}", box_wrap, box_bg, reply_box)
        
        page_header = driver.find_element(By.ID, 'page_header_cont')
        driver.execute_script("arguments[0].style.position = 'absolute';", page_header)
        
        img_url = ob.full_Screenshot(driver, save_path=r'./imgs', image_name=f'wall{owner_id}_{post_id}.png', multi_images=True)
    driver.close()