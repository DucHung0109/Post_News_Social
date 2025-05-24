# https://github.com/DucHung0109/Post_News_Social

from datetime import datetime, timedelta
from Get_News import News

def load_news(collection):
    """
    Load article from MongoDB

    Input: collection

    Output: list of json object(list of posted article)
    """

    result = []
    for doc in collection.find():
        news = {
            "title": doc['title'],
            "content": doc['content'],
            "url": doc['url'],
            "img": doc['img'],
            "description": doc['description'],
            "comment": doc['comment'],
            "title_vn": doc['title_vn'],
            "content_vn": doc['content_vn']
        }
        
        result.append(news)

    return result

def delete_too_late_news(collection):
    """
    Delete articles, which were saved more than 6 days ago.

    Input: collection
    """

    seven_days_ago = datetime.today() - timedelta(days=7)

    collection.delete_many({"date": {"$lt": seven_days_ago}})

def save_news(list_news: list, collection):
    """
    Save new article on MongoDB

    Input:
            - list_news: list of News object(list of new article)
            - collection
    """
    date = datetime.today()

    list_news_json = [
        {
            "date": date,
            "title": news.title,
            "content": news.content,
            "url": news.url,
            "img": news.img,
            "description": news.description,
            "comment": news.comment,
            "title_vn": news.title_vn,
            "content_vn": news.content_vn
        }
        for news in list_news
    ]

    collection.insert_many(list_news_json)