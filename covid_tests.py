"""
This module handles the testing of the scheduling and the covid data and new handling modules
"""

#importing handler module functions
from covid_data_handler import parse_csv_data
from covid_data_handler import process_covid_csv_data
from covid_data_handler import covid_API_request
from covid_data_handler import schedule_covid_updates
from covid_data_handler import get_covid_data
from covid_data_handler import optional_value

#importing news handling module functions
from covid_news_handling import get_news_articles
from covid_news_handling import find_new_news
from covid_news_handling import add_seen_news_article
from covid_news_handling import create_search_query_term
from covid_news_handling import schedule_update_news
from covid_news_handling import news_API_request
from covid_news_handling import update_news


# Covid Data Update tests
def test_parse_csv_data():
    data = parse_csv_data('nation_2021-10-28.csv')
    assert len(data) == 639

def test_process_covid_csv_data():
    last7days_cases , current_hospital_cases , total_deaths = \
        process_covid_csv_data ( parse_csv_data (
            'nation_2021-10-28.csv' ) )
    assert last7days_cases == 240_299
    assert current_hospital_cases == 7_019
    assert total_deaths == 141_544

def test_covid_API_request():
    data = covid_API_request()
    assert isinstance(data, dict)

def test_get_covid_data():
    """
    This test ensures that the covid data has been fetched and formatted correctly
    """
    data = get_covid_data()
    assert isinstance(data, dict)

def test_schedule_covid_updates():
    """
    This test checks that the scheduled covid data updates are running
    """
    schedule_covid_updates(update_interval=10, update_name='update test')

def test_optional_present():
    """
    This test ensures that when present the data is converted to
        string to conform to the file formatting
    """
    present = "present"
    value = optional_value(present)
    assert value == present

def test_optional_absent():
    """
    This test ensures that when no value is given it does not change the value
    """
    value = optional_value(None)
    assert value == ""


# News Tests
def test_news_API_request():
    assert news_API_request()
    assert news_API_request('Covid COVID-19 coronavirus') == news_API_request()

def test_update_news():
    update_news('test')

def test_find_one_new_news():
    """
    This test ensures that news is correctly found
    """
    excluding_seen_news = []
    excluding_seen_news.append({'source': {'id': None, 'name': 'The Guardian'},\
        'author': 'Jo Bloggs', 'title': 'Covid live: danger', 'url': 'guardian'})
    excluding_seen_news.append({'source': {'id': None, 'name': 'The Telegraph'}, \
        'author': 'Black Widdow', 'title': 'Delta is Dangerous', 'url': 'telegraph'})
    excluding_seen_news.append({'source': {'id': None, 'name': 'Daily Mail'},\
        'author': 'Gossip Girl', 'title': 'Covid central park alarm', 'url': 'daily mail'})

    new_news_article = {'source': {'id': None, 'name': 'The Sun'}, \
        'author': 'Captain Americ', 'title': 'Alien Covid coms', 'url': 'sun'}
    news_articles = []
    news_articles.append({'source': {'id': None, 'name': 'The Guardian'}, \
        'author': 'Jo Bloggs', 'title': 'Covid live: danger', 'url': 'guardian'})
    news_articles.append(new_news_article)
    news_articles.append({'source': {'id': None, 'name': 'The Telegraph'}, \
         'author': 'Black Widdow', 'title': 'Delta is Dangerous', 'url': 'telegraph'})

    new_news = find_new_news(excluding_seen_news, news_articles)
    print("len new news", len(new_news))
    assert len(new_news) == 1

def test_get_news_articles():
    """
    This test calls the news API request and ensures that news_articles are present
    """
    news_articles = get_news_articles()
    assert isinstance(news_articles, list)

def test_add_seen_news_article():
    """
    This test checks that a news article has been seen
    """
    add_seen_news_article("seen article")

def test_create_search_query_term():
    """
    This test checks that the search query term is correct
        and the news is filtered correctly
    """
    search_query_term = create_search_query_term("Covid COVID-19 coronavirus")
    assert search_query_term == "language=en&q=covid&covid-19&coronavirus"

def test_schedule_update_news():
    """
    This test checks that the scheduled covid news updates are running
    """
    schedule_update_news(update_interval=10, update_name='update test')
