from src import session, utils
import sys
import random
import time

def main():
   argv = sys.argv[1:]
   if len(argv) != 4:
      print("Usage: main.py LOGIN PASSWORD FILE_WITH_LINKS FILE_WITH_MESSAGES")
      sys.exit()

   
   # login pass format: +380956665454 passsword
   login, password = argv[0], argv[1]
   links, messages = argv[2], argv[3]

   account = session.Session(login, password)

   with open(links) as lnk, open(messages) as msg:
      lnk, msg = lnk.read().split('\n'), msg.read().split('\n')

      for link in lnk:
         if utils.check_link(link):
            owner_id, post_id = utils.wall_link_parse(link)
            account.comment_post(owner_id, post_id, msg[random.randint(0, len(msg))])
            time.sleep(random.randint(5, 15))
         continue

if __name__ == '__main__':
   main()
