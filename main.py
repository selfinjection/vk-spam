from src import session, utils
from loguru import logger
from threading import Thread, Barrier
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, wait
import asyncio
THREADS = 40

def worker(session: session.Session, links, msg):
    result = session.comment_posts(links, msg)
    return result

def create_session(ac):
    return session.Session(token=ac[0]) if len(ac) == 1 else session.Session(ac[0], ac[1])

def main():
    links = []
    with open('creds/links.txt', encoding="utf-8") as lnk_file, open('creds/messages.txt', encoding="utf-8") as msg, open('creds/accounts.txt') as accounts:
        lnk, msg, accounts = lnk_file.read().split('\n'), msg.read().split('\n'), [ac.split(':') for ac in accounts.read().split('\n')]
        loop = asyncio.get_event_loop()

        with ThreadPoolExecutor(max_workers=5) as executor:
            sessions = list(tqdm(executor.map(create_session, accounts), ncols=90, desc='Accounts auth'))
        
        links = loop.run_until_complete(utils.check_links_async(lnk))
        
        with ThreadPoolExecutor(max_workers=THREADS) as executor:
            futures = [executor.submit(worker, s, links, msg) for s in sessions]
            done, not_done = wait(futures)

    with open('creds/links.txt', 'w', encoding="utf-8") as lnk_file: # leave only valid links
        lnk_file.writelines('\n'.join(link for link in links))

    utils.log_json([future.result() for future in done])
    utils.get_screenshots(links)
if __name__ == '__main__':
   main()