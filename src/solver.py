import json
from urllib.parse import urlsplit, parse_qs
import requests
import hashlib
from datetime import datetime
import asyncio
import aiohttp
from lxml.html import fromstring

async def fetch_html(session, semaphore, link):
    async with semaphore:
        while True:
            async with session.get(link, verify_ssl=False) as resp:
                url = urlsplit(str(resp.url))
                print(url.path)
                if '/challenge.html' in url.path:
                    hash429 = parse_qs(url.query)['hash429'][0].encode('utf-8')
                    key = hashlib.md5(hash429).hexdigest()
                    link = str(resp.url) + '&key=' + key
                else:
                    return [await resp.text(), str(resp.url).replace('m.', '')]

async def solve_links(path):
    links = read_links(path)
    semaphore = asyncio.Semaphore(30)  # limit to 10 concurrent requests
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        html = await asyncio.gather(*[fetch_html(session, semaphore, link) for link in links])


    result = []
    for content, url in html:
        if is_valid_html(content):
            result.append(url)

    return result

def is_valid_html(content):
    invalid_titles = ['Post deleted | VK', 'Запись удалена', 'Error | VK']
    c = fromstring(content)
    title = c.findtext('.//title')
    return title not in invalid_titles

def read_links(path):
    with open(path, 'r', encoding='utf-8') as file:
        return file.read().split('\n')