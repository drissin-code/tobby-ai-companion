from newsapi import NewsApiClient
import os

newsapi = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))

def get_gaming_news():
    # Query for GTA V and RDR2 updates
    query = "GTA V OR RDR2 OR Rockstar Games OR GTA VI"
    news = newsapi.get_everything(q=query, language='en', sort_by='publishedAt', page_size=3)
    titles = [art['title'] for art in news['articles']]
    return titles

def get_morning_brief():
    top_news = newsapi.get_top_headlines(language='en', page_size=3)
    titles = [art['title'] for art in top_news['articles']]
    return titles