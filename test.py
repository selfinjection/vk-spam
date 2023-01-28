import json
from urllib.parse import urlsplit, parse_qs
import requests
import hashlib
from datetime import datetime

with open('creds/links.txt', 'r', encoding='utf-8') as file:
    links = file.read().split('\n')
    result = {}
    for link in links:
        url = urlsplit(link)
        if url.path == '/challenge.html':
            params = parse_qs(url.query)
            result.update({link: params})
    
    session = requests.Session()
    past = datetime.now()
    for k, v in result.items():
        print(f'INIT URL\n{k}\n')
        response = session.get(k)
        print(f'REDIRECTED URL\n{response.url}\n')
        url = urlsplit(response.url)
        params = parse_qs(url.query)
        key = hashlib.md5(params['hash429'][0].encode('utf-8')).hexdigest()
        valid_url = response.url + '&key=' + key
        print(f'GENERATED KEY\n{key}\n{valid_url}\n')
        response = session.get(valid_url)
        print(f'PUSHING PAYLOAD\nRESULT URL\n{response.url}, {response.status_code}')
        print('*'*100)
    now = datetime.now()

    print(f'Time taken: {now - past} \n Links: {len(links)}')