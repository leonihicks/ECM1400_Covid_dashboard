"""
This module handles:
    - fetching news from the news API addres
    - scheduled news updates
"""

#importing modules for logging
import logging

#Importing modules
import json
import re
import requests

#Importing scheduler module to schedule news updates
from scheduler import get_scheduler

#Setting up logging
FORMAT = '%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'
log = logging.getLogger(__name__)
logging.basicConfig(filename = 'sys.log', encoding='utf-8', format = FORMAT, level=logging.DEBUG)

#A list of current news articles to be displayed on the dashboard
news_articles = []

#A list of news articles titles that have been marked as "seen"
seen_news_articles = []

def get_news_articles():
    """
    Process checks the length of news articles, so that if less than 1
    program updates the news articles so that news is present
    """
    if len(news_articles) <1:
        update_news()

    return news_articles

def add_seen_news_article(seen_article):
    """
    Adding news articles that have been seen to the dictionary of
    seen new articles
    """
    log.info("Adding new seen article "+ seen_article)
    seen_news_articles.append(seen_article)

    global news_articles
    news_articles = [news_article for news_article in news_articles \
                     if news_article['title'] != seen_article]

def news_API_request(covid_terms = "Covid COVID-19 coronavirus"):
    """
    Fetches API key from config file
    Searches for search terms for news articles
    """
    f = open('config.json',)
    config_dict = json.load(f)
    base_url = "https://newsapi.org/v2/top-headlines?"
    api_key = config_dict["covid_news_api_key"]

    search = create_search_query_term(covid_terms)
    country = "gb"
    complete_url = base_url + search + "country=" + country + "&apiKey=" + api_key
    log.info(search)
    response = requests.get(complete_url)

    return response.json()

def create_search_query_term(covid_terms):
    """
    Querying the news to be in English and search covid terms
    """
    search_query_term = "language=en&q="
    # change the covid terms to lower case and then split them into a list of words
    words = re.split('\s+', covid_terms.lower())
    first_word = True
    for word in words:
        if first_word:
            first_word = False
        else:
            search_query_term = search_query_term + "&"

        search_query_term = search_query_term + word

    return search_query_term

def covid_terms():
    """
    This function holds the terms to be searched for news articles
    """
    return "Covid COVID-19 coronavirus"

def find_new_news(excluding_seen_news, existing_news):
    """
    Finds new news from the API that is not currently in the list
    """

    # https://stackoverflow.com/questions/7271482/getting-a-list-of-values-from-a-list-of-dicts
    existing_news_titles = list(map(lambda d: d['title'], existing_news) )

    return [news_article for news_article in excluding_seen_news if \
            news_article['title'] not in  existing_news_titles]

def update_news(id="update-id"):
    """
    Process to update news artciles and finds new news articles
    Checks with function excluding_seen_news to know which news to filter out
    """
    log.info("News is being updated")

    news_result = news_API_request(covid_terms = covid_terms())
    current_news_articles = news_result["articles"]

    excluding_seen_news = [news_article for news_article in current_news_articles \
                           if news_article['title'] not in seen_news_articles]

    new_news = find_new_news(excluding_seen_news, news_articles)

    log.info("Adding {} new news articles".format(len(new_news)))

    news_articles.extend(new_news)

def schedule_update_news(update_interval, update_name):
    """
    This function allows the user to create scheduled updates
    This function works with the scheduler module and takes the time of the
        update, a name and whether it is to be repeated or not
    """
    scheduler = get_scheduler()
    event = scheduler.enter(update_interval, 1, update_news)

    log.info("News update event for {} added to scheduler {}".format(update_name, event))

    return event
