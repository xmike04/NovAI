import requests
import json
from NOVA.config import config


def get_news():
    url = f'http://newsapi.org/v2/top-headlines?sources=the-times-of-india&apiKey={config.news_api_key}'
    news = requests.get(url).text
    news_dict = json.loads(news)
    articles = news_dict['articles']
    try:
        return articles
    except:
        return False


def getNewsUrl():
    return f'http://newsapi.org/v2/top-headlines?sources=the-times-of-india&apiKey={config.news_api_key}'
