"""
This module contains the schedular data used by the other modules
"""

#importing modules for logging
import logging

from datetime import datetime
import sched
import time

#Setting up logging
FORMAT = '%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'
log = logging.getLogger(__name__)
logging.basicConfig(filename = 'sys.log', encoding='utf-8', format = FORMAT, level=logging.DEBUG)

#python schedular
scheduler = sched.scheduler(time.time, time.sleep)

# updates_scheduled: a list of future scheduled updates stored in a dictionary
#(this can have one or two jobs if both covid data and news are requested).
updates_scheduled = []

def get_scheduler():
    """
    Process to fetch scheduler and be used in other modules
    """
    return scheduler

def update_scheduler(updated_scheduler):
    """
    Getting scheduler to run the sched module
    Process to update the scheduler
    """
    global scheduler
    scheduler = updated_scheduler

def log_scheduler(message):
    """
    Process used to log information easily in other modules
    Gathers number of items in schedule queue
    """
    log.info("Scheduler size: {}".format(len(scheduler.queue)))

    for index, job in enumerate(scheduler.queue):
        log.info("JOB {} {}".format((index + 1), job))

def log_updates_scheduled(message):
    """
    Process used to log information easily in other modules
    Gathers number of items that have been updates
    """
    log.info(" updates_scheduled size: {}".format(len(updates_scheduled)))

    for index, item in enumerate(updates_scheduled):
        log.info("ITEM {} {} ".format(index + 1, item))

def get_updates_scheduled():
    """
    Returns updates_scheduled to be used in the main module for updating
    """
    return updates_scheduled

def run_scheduler():
    """
    Process for schduling, states the size of the scheduler queue
    Makes sure blocking is set to False
    """
    log.info("Size of scheduler queue (before testing) {}".format(len(scheduler.queue)))
    if not scheduler.empty():
        #Since blocking = false, this executes the scheduled events due to expire soonest (if any)
        scheduler.run(blocking=False)
        log_scheduler("Post schedular run")

def calc_absolute_delay_time(update_time):
    """
    Calculating sum of time and delay
    """
    return time.time() + calculate_delay(update_time, 30)

def add_new_update_scheduled(title, content, update_time, \
        update_covid_data, update_news, repeat, update_covid_event, update_news_event):
    """
    Process adds a new schedule event and tracks what needs to be done
    """
    absolute_delay_time = calc_absolute_delay_time(update_time)
    new_schedule = {"title": title, "content": content, "update_time": update_time, "update_covid_data": update_covid_data, "update_news": update_news, "repeat": repeat, "update_covid_event": update_covid_event, "update_news_event": update_news_event, "absolute_delay_time": absolute_delay_time}
    updates_scheduled.append(new_schedule)

def update_name_in_updates_scheduled(title):
    """
    Checking whether this update name already exists
    If so no new update is created and a warning is outputted into the log
    """
    item_list = [item for item in updates_scheduled if item['title'] == title]
    if (len(item_list) ==0):
        return False
    else:
        log.warning("Item already in list")
        return True

def remove_item_from_scheduled_updates(title):
    """
    Removes an item from updates_scheduled
    """
    global updates_scheduled
    updates_scheduled = [item for item in updates_scheduled if item['title'] != title]

def remove_scheduled_job(title):
    """
    Gets the event(s) from updates_scheduled in order to cancel the event (job)
    Removes the item from the list
    """

    global updates_scheduled

    item_list = [item for item in updates_scheduled if item['title'] == title]
    item_dict = item_list[0]

    if item_dict["update_covid_data"]:
        update_covid_event = item_dict["update_covid_event"]
        try:
            scheduler.cancel(update_covid_event)
            log.info("Scheduler size: {} ".format(len(scheduler.queue)))
        except ValueError:
            log.warning("Covid update job already completed or not present")

    if item_dict["update_news"]:
        update_covid_event = item_dict["update_news_event"]
        try:
            scheduler.cancel(update_covid_event)
            log.info("Scheduler size: {} ".format(len(scheduler.queue)))
        except ValueError:
            log.warning("News update job already completed or no present")

    log.info("Update scheduled before, length = {} ".format(len(updates_scheduled)))
    updates_scheduled = [item for item in updates_scheduled if item['title'] != title]

    log.info("Update scheduled now, length = {} ".format(len(updates_scheduled)))

#Refactor
def calculate_delay(hours_minutes:str, delay_delta_seconds):
    """
    Calculate the delay for a scheduled event
    hours_minutes in HH:MN format (e.g. 12:30)
    delay_delta_seconds - used to prevent missing a schedule at the same time as hours_minutes
    and when a user schedules updates to both covid data and news
    """

    hours_minutes_list = hours_minutes.split(':')
    hours = int(hours_minutes_list[0])
    minutes = int (hours_minutes_list[1])
    seconds = ( ( hours * 60 * 60) + (minutes * 60))

    now = datetime.now()
    seconds_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()

    if seconds > (seconds_since_midnight + delay_delta_seconds):
        delay = (seconds + delay_delta_seconds) - seconds_since_midnight
    else:
        delay = ((24 * 60 * 60) + delay_delta_seconds + seconds) - seconds_since_midnight

    log.info("Delay: {} , hours_minutes: {}".format(delay, hours_minutes))
    return delay
