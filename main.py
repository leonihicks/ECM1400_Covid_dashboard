"""
This is the main module, it handles:
    - the flask application
    - scheduling news and covid data updates (which can be deleted)
"""

#importing modules for logging
import logging

#Importing modules
import json
import time

#Importing flask modules to run flask
from flask import Flask
from flask import render_template, request

#Importing covid_data_handler module
from covid_data_handler import schedule_covid_updates, update_covid_data, get_covid_data

#Importing covid_news_handling modules
from covid_news_handling import add_seen_news_article
from covid_news_handling import update_news
from covid_news_handling import schedule_update_news
from covid_news_handling import get_news_articles

#Importing scheduler modules
from scheduler import get_updates_scheduled
from scheduler import add_new_update_scheduled
from scheduler import remove_scheduled_job
from scheduler import log_scheduler
from scheduler import log_updates_scheduled
from scheduler import run_scheduler
from scheduler import update_name_in_updates_scheduled
from scheduler import remove_item_from_scheduled_updates
from scheduler import calculate_delay
from scheduler import calc_absolute_delay_time

#Calling Flask and assigning it to a variable
app = Flask(__name__)

#Title of the Dashboard
title = "Covid Data Dashboard"

#Setting up logging
FORMAT = '%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'
log = logging.getLogger(__name__)
logging.basicConfig(filename = 'sys.log',  encoding='utf-8', \
                    format = FORMAT, level=logging.DEBUG)


@app.route('/')
def home_page():
    """
    Opening the home page, fetches the area and area type from the config file
        to be used to insert data into the render template
    """
    log.info("Home page is running")

    nation_location, location = locations()

    covid_data =  get_covid_data()
    updates_scheduled = get_updates_scheduled()
    news_articles = get_news_articles()

    return render_template("index.html", updates = updates_scheduled, title = title,location= location, local_7day_infections = covid_data["location_last7days_cases"], nation_location = nation_location, national_7day_infections = covid_data["nation_last7days_cases"], hospital_cases = covid_data["nation_current_hospital_cases"], deaths_total = covid_data["nation_total_deaths"], news_articles = news_articles, image = "covid_molecule.jpg")

@app.route('/index')
def process_index_url():
    """
    Process calls to the application "index page" from
    - adding a scheduled (in future or instant)
    - deleting schedule
    - delete news item
    - automatic refresh from the index.html page every minute
        (from  <meta http-equiv="refresh" content="60;url='/index'">)

    As well as processing the data from the web page, also run the scheduler and
    check if any items in the updates_scheduled that need reviewing
    """

    log.info("request on /index ============")
    log_updates_scheduled("on /index")
    log_scheduler("on /index")

    run_scheduler()
    review_updates_scheduled()

    news_article = request.args.get('notif')
    update_item = request.args.get('update_item')

    if news_article:
        return remove_news_article(news_article)
    elif update_item:
        return delete_item_from_schedule(update_item)
    else:
        update_name = request.args.get('two')
        if update_name:
            return  schedule_data_updates(update_name)
        else:
            return index_refreshed()

def schedule_data_updates(update_name):
    """
    This can be an instant update (schedule now if nothing is in the
        update field or at a later date if there is something in the update field)
    No update is made if the update title (label) is already used
    """

    news_selected = request.args.get('news')
    covid_data_selected = request.args.get('covid-data')
    repeat_selected = request.args.get('repeat')
    update_time = request.args.get('update')

    content = "This is an update scheduled for " + update_time
    log.info("form data: label selected {}, news selected {}, covid data selected {},\
             repeat selected{}, update time selected = [{}]".format(update_name,\
             news_selected, covid_data_selected,repeat_selected, update_time))

    nation_location, location = locations()

    if update_name_in_updates_scheduled(update_name):
        log.warning("Title is already on the updates scheduled - ignoring request")
    elif update_time:
        log.info("scheduling an update")

        if (news_selected is not None):
            update_interval = calculate_delay(update_time, 20)
            update_news_event = schedule_update_news(update_interval \
                                                     = update_interval, update_name = update_name)
            log_scheduler("News Update Job Added")
        else:
            update_news_event = None

        if (covid_data_selected is not None):
            update_interval = calculate_delay(update_time, 10)
            update_covid_event = schedule_covid_updates \
                (update_interval = update_interval, update_name = update_name)
            log_scheduler("Covid Data Update Job Added")
        else:
            update_covid_event = None

        """ Adding a new schedule update event with all needed data """
        add_new_update_scheduled(title = update_name, content = content, update_time = update_time, update_covid_data = covid_data_selected, update_news = news_selected, repeat = repeat_selected, update_covid_event = update_covid_event, update_news_event = update_news_event)
        log_updates_scheduled("New Schedule added with title: " + update_name)

        """ Checking whether value is None,
        if so it logs that an update has been requested for that job """
    else:
        logging.warning("No time entered - instant update has been done")
        if (news_selected is not None):
            log.info("News update requested")
            update_news()

        if (covid_data_selected is not None):
            log.info("Covid data update requested")
            update_covid_data(nation_location, location)

    news_articles = get_news_articles()
    covid_data = get_covid_data()
    updates_scheduled = get_updates_scheduled()

    return render_template("index.html", updates = updates_scheduled, title = title, content = content, location= location, local_7day_infections = covid_data["location_last7days_cases"], nation_location = nation_location, national_7day_infections = covid_data["nation_last7days_cases"], hospital_cases = covid_data["nation_current_hospital_cases"], deaths_total = covid_data["nation_total_deaths"], news_articles = news_articles, image = "covid_molecule.jpg")

def index_refreshed():
    """
    Process calls  to the application when the page is beiing refreshed
    Ensures that all data is still present
    """
    nation_location, location = locations()

    news_articles = get_news_articles()
    covid_data =  get_covid_data()
    updates_scheduled = get_updates_scheduled()

    return render_template("index.html", updates = updates_scheduled, title = title,location= location, local_7day_infections = covid_data["location_last7days_cases"], nation_location = nation_location, national_7day_infections = covid_data["nation_last7days_cases"], hospital_cases = covid_data["nation_current_hospital_cases"], deaths_total = covid_data["nation_total_deaths"], news_articles = news_articles, image = "covid_molecule.jpg")

def remove_news_article(news_article):
    """
    Process will remove news articles that have been seen already and removed
    Data is fetched again to make sure all data is present
    """
    log.info("Processing notifications, news article removed")
    add_seen_news_article(news_article)

    nation_location, location = locations()

    news_articles = get_news_articles()
    covid_data =  get_covid_data()
    updates_scheduled = get_updates_scheduled()

    return render_template("index.html", updates = updates_scheduled, title = title, location= location, local_7day_infections = covid_data["location_last7days_cases"], nation_location = nation_location, national_7day_infections = covid_data["nation_last7days_cases"], hospital_cases = covid_data["nation_current_hospital_cases"], deaths_total = covid_data["nation_total_deaths"], news_articles = news_articles, image = "covid_molecule.jpg")

def delete_item_from_schedule(update_item):
    """
    Process wiill remove an item from the scheduler
    This is used with the remove_scheduled_job from scheduler
    """
    log.info("Scheduled item to delete: " + update_item)
    remove_scheduled_job(update_item)

    nation_location, location = locations()

    news_articles = get_news_articles()
    covid_data = get_covid_data()
    updates_scheduled = get_updates_scheduled()

    return render_template("index.html", updates = updates_scheduled, title = title,location= location, local_7day_infections = covid_data["location_last7days_cases"], nation_location = nation_location, national_7day_infections = covid_data["nation_last7days_cases"], hospital_cases = covid_data["nation_current_hospital_cases"], deaths_total = covid_data["nation_total_deaths"], news_articles = news_articles, image = "covid_molecule.jpg")

def review_updates_scheduled():
    """
    Go through all dictionaries in updates_scheduled and
        check if any have a absolute_delay_time in the past.
    If in the past:
    - if repeat is set then create jobs in python scheduler for
        covid data (if set) and covid news (if set)
    - else remove the item from updates_scheduled
    """

    log.info("Reviewing the list of scheduled updates" )
    updates_scheduled = get_updates_scheduled()
    for index, item in enumerate(updates_scheduled):
        log.info("Checking ITEM {} {}".format(index + 1, item))
        absolute_delay_time = item["absolute_delay_time"]
        if time.time() > absolute_delay_time:
            if item["repeat"]:
                update_time = item["update_time"]
                log.info("Creating new jobs in python scheduler for tomorrow at "+ update_time)
                if item["update_covid_data"]:
                    update_interval = calculate_delay(update_time, 10)
                    update_covid_event = schedule_covid_updates(update_interval, item["title"])
                    item["update_covid_event"] = update_covid_event
                if item["update_news"]:
                    update_interval = calculate_delay(update_time, 20)
                    update_news_event = schedule_update_news(update_interval, item["title"])
                    item["update_news_event"] = update_news_event
                absolute_delay_time = calc_absolute_delay_time(update_time)
                item["absolute_delay_time"] = absolute_delay_time
                log_updates_scheduled("After review")
                log_scheduler("After review")
            else:
                title = item["title"]
                remove_item_from_scheduled_updates(title)
                log_updates_scheduled("Removed " + title + " from scheduled updates ")

def locations():
    """
    This function extracts data from the configuration file to set up
        the national_location and location variable
    This will help set up the locations for data to be pulled from the API
    """
    f = open('config.json',)
    config_dict = json.load(f)
    nation_location = config_dict["nation_location"]
    location = config_dict["location"]

    return nation_location, location


if __name__ == '__main__':
    """
    Running the main app
    """
    app.run()
