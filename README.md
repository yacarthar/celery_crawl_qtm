# celery_crawl_qtm

#usage:
	Crawl data from quantrimang.com post 
#setup:
- virtual env: \
	`virtualenv env` \
	`source env/bin/activate` \
	`pip install -r requirements.txt` \
- start redis:`redis-server`
- start celery task:: \
	`celery worker -A tasks --autoscale=10,5 -l INFO`
- start app: \
	python3 client.py