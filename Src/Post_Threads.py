# https://github.com/DucHung0109/Post_News_Social

from pymongo.mongo_client import MongoClient
from datetime import datetime, timedelta
import requests
import os
import json

def load_accessToken(collection):
    for doc in collection.find():
        result = doc['token_threads']
    
    return result

def load_yesterday_news(collection):

    list_news = []
    now = datetime.utcnow()
    yesterday_start = datetime(now.year, now.month, now.day) - timedelta(days=1)
    yesterday_end = yesterday_start + timedelta(days=1)

    # Truy vấn các document có 'date' trong khoảng ngày hôm qua
    query = {
        "date": {
            "$gte": yesterday_start,
            "$lt": yesterday_end
        }
    }

    # Thực hiện truy vấn
    results = collection.find(query)
    for doc in results:
        list_news.append(doc)

    return list_news

def post_news_threads(list_news, access_token):

    if not isinstance(list_news, list):
        list_news = [list_news]

    base_url = "https://graph.threads.net/v1.0"

    for news in list_news:
        message = news['description']
        message += f"\n\nLink: {news['url']}"

        # Bước 1: Tạo container cho bài đăng
        create_url = f"{base_url}/me/threads"
        payload = {
            "media_type": "IMAGE",
            "image_url": news['img'],
            "text": message,
            "access_token": access_token
        }
        response = requests.post(create_url, data=payload)
        container_id = response.json().get("id")

        publish_url = f"{base_url}/me/threads_publish"
        publish_payload = {
            "creation_id": container_id,
            "access_token": access_token
        }
        publish_response = requests.post(publish_url, data=publish_payload)
        post_id = publish_response.json().get("id")

        comment_payload = {
            "media_type": "TEXT",
            "text": news['comment'],
            "reply_to_id": post_id,
            "access_token": access_token
        }
        
        # Thêm bình luận
        comment_response = requests.post(create_url, data=comment_payload)
        container_id = comment_response.json().get("id")

        publish_payload = {
            "creation_id": container_id,
            "access_token": access_token
        }
        publish_response = requests.post(publish_url, data=publish_payload)

username_mongo = os.environ["USERNAME_MONGO"]
password_mongo = os.environ["PASSWORD_MONGO"]
mongo_uri = f"mongodb+srv://{username_mongo}:{password_mongo}@postednews.nm9vqhx.mongodb.net/?retryWrites=true&w=majority&appName=PostedNews"
client = MongoClient(mongo_uri)
db = client['Post_News_FanPage']
postedNews_collection = db['postedNews_collection']
accessToken_collection = db['accessToken_collection']

print('Read articles')
list_news_json = load_yesterday_news(postedNews_collection)
print("Get token")
access_token = load_accessToken(accessToken_collection)
print("Post News")
post_news_threads(list_news_json, access_token)
