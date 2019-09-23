import time
import threading
from queue import Queue

import requests
from bs4 import BeautifulSoup, element

from tasks import parsePost, handleIO

q = Queue()

def getTopic():
    url = 'https://quantrimang.com'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    # print(soup)
    leftbar = soup.find('div', {'class':'leftbar'})
    for sub_topic in [tree for tree in leftbar.div.div.ul.contents
                        if isinstance(tree, element.Tag)
                        ]:
        try:
            for item in sub_topic.ul.find_all('li'):
                topic = item.a.get('href')
                q.put(topic)
                print('q1 put success: ', topic)
        except AttributeError:
            topic = sub_topic.a.get('href')
            q.put(topic)
            print('q1 put success: ', topic)


def getPosts(topic):
    domain = 'https://quantrimang.com'
    # i = 0
    print(threading.current_thread().getName(), ' --- ', topic)
    while True:
        r = requests.get(domain + topic)
        soup = BeautifulSoup(r.text, 'lxml')
        listviews = soup.find_all('div', {'class':'listview clearfix'})
        for listview in listviews:
            data = {}
            for item in listview.ul.find_all('li'):
                data['post_url'] = item.a.get('href')
                print(data['post_url'])
                data['post_desc'] = repr(item.div.get_text())
                parsePost.delay(data)
                # i+=1
                # print(i, 'sent to celery')
        try:
            viewmore = soup.find('a', {'class':'viewmore'})
            topic = viewmore.get('href')
        except:
            break


class TopicThread(threading.Thread):
    """Threaded Url Grab"""
    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    def run(self):
        print(threading.current_thread().getName(), ' running')
        while True:
            topic = self.queue.get()
            getPosts(topic)
            self.queue.task_done()
            print('q1 size: ',q.qsize())
            time.sleep(5)
            if not q.qsize():
                break
        

def generateThread():
    for i in range(5):
        t = TopicThread(q)
        t.start()






if __name__ == '__main__':
    getTopic()
    generateThread()
    handleIO.delay({'stop': True})
    