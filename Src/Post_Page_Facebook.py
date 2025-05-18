# https://github.com/DucHung0109/Post_News_FanPage

import requests
import json
import datetime
from Process_Img import load_image
from Get_News import News
    
def post_comment_facebook(comment: str, id: str, page_access_token: str):
    """
    Post comment on Facebook post

    Input: 
            - comment: content of comment
            - id: id of post
            - page_access_token: token to connect to page
    
    """

    url = f"https://graph.facebook.com/{id}/comments"
    payload = {
        "message": comment,
        "access_token": page_access_token
    }

    requests.post(url, data=payload)

    

def post_news_page_facebook(list_news: list, id: str, page_access_token:str):
    """
    Post status on Facebook, include message, image. Each image has its message.

    Input: 
            - list_news: list of News object
            - id: id of page
            - page_access_token: token to connect to page
    
    Output: - str: Id of main post
    """
    
    # Use UTC timezone, so must use the time we want to post minus 7 hours because Vietnam is UTC+7
    today = datetime.datetime.now()
    tomorrow = today + datetime.timedelta(days=1)
    post_time = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0).isoformat()


    MESSAGE = f"TIN TỨC NỔI BẬT {today.strftime('%d/%m/%Y')}!\n\n\n"

    photo_ids = []
    for i, news in enumerate(list_news):
        MESSAGE += f"{i + 1}. {news.title_vn}\n{news.description}\n\n\n"
        if news.img is None:
            continue
        image = load_image(news.img, news.source)
        if image is None:
            continue
        url = f"https://graph.facebook.com/{id}/photos"
        mess = f'{news.title_vn}\n{news.content_vn}\nLink: {news.url}'
        payload = {
            "published": "false",  # Image isn't publish
            "message": mess,
            "access_token": page_access_token
        }
        
        image = load_image(news.img, news.source)
    
        files = {
            "source": image
        }
        
        response_img = requests.post(url, data=payload, files=files)
        if response_img.status_code == 200:
            photo_id = response_img.json()["id"]
            photo_ids.append(photo_id)

    url = f"https://graph.facebook.com/{id}/feed"
    payload = {
        "message": MESSAGE,
        "access_token": page_access_token,
        "published": False,
        "scheduled_publish_time": post_time
    }

    for i, photo_id in enumerate(photo_ids):
        payload[f"attached_media[{i}]"] = f'{{"media_fbid":"{photo_id}"}}'

    response = requests.post(url, data=payload)

    for i, photo_id in enumerate(photo_ids):
        post_comment_facebook(list_news[i].comment, photo_id, page_access_token)

    return response.json()['id']
