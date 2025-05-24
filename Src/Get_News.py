# https://github.com/DucHung0109/Post_News_Social

from newsapi import NewsApiClient

class News:
    """
    Class News, object of news
    """
    
    def __init__(self, title, url, img, content):
        self.title = title
        self.url = url
        self.img = img
        self.content = content  
        self.source = 'https://' + url[8:].split("/")[0]
        self.title_vn = ""
        self.content_vn = ""
        self.description = ""
        self.comment = ""

    def add_description(self, descrip):
        self.description = descrip
    
    def add_comment(self, cmt):
        self.comment = cmt

    def add_content_vn(self, content_vnese):
        self.content_vn = content_vnese

    def add_title_vn(self, title_vnese):
        self.title_vn = title_vnese
        
def get_news(api: str):
    """
    Use NEWSAPI to get top headlines news

    Input: Api key of NEWSAPI

    Output: list of News object. Each item include:
            - title(str): title of article
            - url(str)): link to article
            - img(str): link to image
            - content(str): (short) content of article
    """

    newsapi = NewsApiClient(api_key=api)

    top_headlines = newsapi.get_top_headlines()

    list_news = []

    for item in top_headlines['articles']:
        title = item['title'].split(" - ")[0].strip()
        url = item['url']   
        img = item['urlToImage']
        content = item['content']
        
        news = News(title, url, img, content)
        if url != None:
            list_news.append(news)

    return list_news

