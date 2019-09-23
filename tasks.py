
import redis
from celery import Celery
import requests
from bs4 import BeautifulSoup, element
import pymongo


myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["zed"]
mycol = mydb["post"]


app1 = Celery('Post_queue',broker='redis://localhost:6379/0')
app2 = Celery('IO_queue',broker='redis://localhost:6379/0')
app1.config_from_object('config')

@app1.task
def parsePost(data):
    post_url = data['post_url']
    # print(post_url)
    post_id = post_url[post_url.rfind('-')+1:]
    # print(post_id)
    # id, title, url, path, content, time
    domain = 'https://quantrimang.com'
    r = requests.get(domain + post_url)
    soup = BeautifulSoup(r.text, 'lxml')
    # print(soup.prettify())
    post_title = soup.find('div', {'id': 'contentMain'}).div.h1.get_text().strip()
    # print(post_title)
    post_path = soup.find('div', {'class': 'breadcrumbs info-detail'}).text.strip().replace('   ', '/')
    # print(post_path)
    post_content = '\n'.join([item.get_text() for item in soup.find('div', {'class': 'content-detail textview'}).find_all('p')])
    # print(post_content[:15])
    time = soup.find('div', {'class': 'author-info clearfix'}).get_text().strip().partition(', ')[2]
    # print(time)

    post = {
        'post_id': post_id,
        'post_title': post_title,
        'post_url': post_url,
        'post_path': post_path,
        'post_content': post_content,
        'post_time': time
    }
    # print(mydb.list_collection_names())
    mycol.insert_one(post)



@app2.task
def handleIO(post):
    if 'stop' in post:
        print('end')
        #     # print([item['post_id'] for item in array])
        #     # x = mycol.insert_many(array)
        #     break
        # array.append(post)
        # if len(array) == 5000:
        #     # print([item['post_id'] for item in array])
        #     # x = mycol.insert_many(array)
        #     print('db inserted')
        #     array = []
