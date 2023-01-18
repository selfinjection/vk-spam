from src import session, utils
from loguru import logger
from threading import Thread, Barrier

# THREADS = 5
# from concurrent.futures import ThreadPoolExecutor

def do_job(sessions):
    logger.warning('Session loaded!')
    for s in sessions:
        s.start()

def main():
    with open('creds/links.txt', encoding="utf-8") as lnk, open('creds/messages.txt', encoding="utf-8") as msg, open('creds/accounts.txt') as accounts:
        lnk, msg, accounts = lnk.read().split('\n'), msg.read().split('\n'), [ac.split(':') for ac in accounts.read().split('\n')]
        links = utils.check_links(lnk)

        sessions = []
        for ac in accounts:
            a = session.Session(token=ac[0]) if len(ac) == 1 else session.Session(ac[0], ac[1])
            sessions.append(Thread(target=a.comment_posts, args=(links, msg)))
            
        do_job(sessions)


if __name__ == '__main__':
   main()


'''
from concurrent.futures import ThreadPoolExecutor

def worker(arg1, arg2):
    result = do_something(arg1, arg2)
    return result

with ThreadPoolExecutor() as executor:
    results = [executor.submit(worker, arg1, arg2) for arg1,arg2 in zip(arg1_list,arg2_list)]

    for f in concurrent.futures.as_completed(results):
        result = f.result()
        # process the result

'''