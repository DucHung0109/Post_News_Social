# https://github.com/DucHung0109/Post_News_Social

from google import genai
from google.genai import types
import json
import re

def list_to_json(list_news: list):
    """
    Convert list of News object into list of json

    Input: list of News object

    Output: list of json object. Each item include:
            - title(str): title of article
            - content(str): content of article
    """
    
    list_news_json = [
    {
        "title": news.title,
        "content": news.content,
    }
    for news in list_news
    ]
    
    return list_news_json

def gen_summary_comment(client, prompt_config: str, prompt: str, model: str, list_json_news: list):
    """
    Generate summary and comment using the GenAI API.

    Input: 
            - client : genai client
            - prompt_config: prompt to config model
            - prompt: prompt to ask model 
            - model: name of model
            - list_json_news: 1 list of json objects(list of new article)

    Output: 1 passage about general comment
    """

    response = client.models.generate_content(
    model=model,
    config=types.GenerateContentConfig(
        system_instruction=prompt_config),
    contents=[{"role": "user", "parts": [{"text": prompt}]},
        {"role": "user", "parts": [{"text": "list_news:\n" + json.dumps(list_json_news)}]}
    ]
    )   

    return response.text

def news_unposted(client, prompt_config: str, prompt: str, model: str, list_json_news: str, list_json_news_posted: str):
    """
    Compare 2 lists, get unposted article

    Input:
            - client : genai client
            - prompt_config: prompt to config model
            - prompt: prompt to ask model 
            - model: name of model
            - list_json_news: 1 list of json objects(list of new article)
            - list_json_posted: 1 list of json objects(list of posted article)

    Output: list of json objects. Each object contains:
            - title: str
            - reason: str, why chosen this news
    """

    response = client.models.generate_content(
    model=model,
    config=types.GenerateContentConfig(
        system_instruction=prompt_config),
    contents=[{"role": "user", "parts": [{"text": prompt}]},
        {"role": "user", "parts": [{"text": "list_news:\n" + json.dumps(list_json_news)}]},
        {"role": "user", "parts": [{"text": "posted_news\n" + json.dumps(list_json_news_posted)}]}
    ]
    )

    match = re.search(r"\[\s*{.*?}\s*\]", response.text, re.DOTALL)

    if match:
        json_text = match.group(0)
        try:
            data = json.loads(json_text)
            return data
        except json.JSONDecodeError as e:
            print("Lỗi khi parse JSON:", e)
    else:
        print("Không tìm thấy mảng JSON nào trong chuỗi.")

def gen_content(client, prompt_config: str, prompt: str, model: str, list_json_news: str):
    """
    Generate content using the GenAI API.

    Input: 
            - client : genai client
            - prompt_config: prompt to config model
            - prompt: prompt to ask model 
            - model: name of model
            - list_json_news: 1 list of json objects(list of new article)

    Output: list of json objects. Each object contains:
            - title: str
            - output: str, maybe reason(why chosen this news), description, comment, content_vn
    """
    response = client.models.generate_content(
    model=model,
    config=types.GenerateContentConfig(
        system_instruction=prompt_config),
    contents=[{"role": "user", "parts": [{"text": prompt}]},
        {"role": "user", "parts": [{"text": "list_news:\n" + json.dumps(list_json_news)}]}
    ]
    )   

    match = re.search(r"\[\s*{.*?}\s*\]", response.text, re.DOTALL)

    if match:
        json_text = match.group(0)
        try:
            data = json.loads(json_text)
            return data
        except json.JSONDecodeError as e:
            print("Lỗi khi parse JSON:", e)
    else:
        print("Không tìm thấy mảng JSON nào trong chuỗi.")