"""
This module handles:
    - the flask application
    - scheduled news and covid data updates (which can be deleted)
"""

#importing modules for logging
import logging

#importing API and modules to access it
import json
import time
from uk_covid19 import Cov19API

#importing from scheduler module to run scheduler function
from scheduler import get_scheduler

#Setting up logging
FORMAT = '%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'
log = logging.getLogger(__name__)
logging.basicConfig(filename = 'sys.log', encoding='utf-8', format = FORMAT, level=logging.DEBUG)

#dictionary to contain covid data
covid_data = {}

def get_covid_data():
    """
    This function handles fetching the covid data in order for schedules
    """

    if not covid_data:
        nation_location, location = locations()
        update_covid_data(nation_location = nation_location, location = location)

    return covid_data

def parse_csv_data(csv_filename):
    """
    This function opens the csv file, extracts the data from the file and returns it
    """

    log.info("Function parse_csv_data has opened file csv_filename: " + csv_filename)
    lines = open(csv_filename, 'r').readlines()

    return lines

def process_covid_csv_data(covid_csv_data):
    """
    This function is used to iterate through and extract specfic data in the covid_csv_data file
    As well as also being used in the covid_API_request for formating purposes
    """

    line_count = 0

    last7days_cases = 0
    current_hospital_cases = "0"
    total_deaths = "0"
    last7days_count = 0
    last7days_cases_found = False

    total_deaths_found = False
    current_hospital_cases_found = False

    for line in covid_csv_data:
        line_count +=1

        item = line.split(",")

        if (not current_hospital_cases_found) and (item[5].isdigit()):
            current_hospital_cases = int(item[5])
            current_hospital_cases_found = True

        if last7days_cases_found and (item[6].strip().isdigit()) and (last7days_count < 7):
            if last7days_cases_found:
                new_cases_by_specimen_date = item[6].strip()
                last7days_cases = last7days_cases + int(new_cases_by_specimen_date)
                last7days_count +=1
        if (not last7days_cases_found) and (item[6].strip().isdigit()):
            last7days_cases_found = True

        if (not total_deaths_found) and (item[4].isdigit()):
            total_deaths = int(item[4])
            total_deaths_found = True

    return last7days_cases, current_hospital_cases, total_deaths

def update_covid_data(nation_location = "England", location = "Exeter"):
    """
    This function handles updating the covid data to be used as a global function
        within scheduling any covid data updates
    Stores covid data into a dictionary
    """

    global covid_data
    log.info("Fetching covid data for both national (" + nation_location + \
             ") and local (" + location + ")")

    ltla_covid_data = covid_API_request(location = location, location_type = "ltla")
    nation_covid_data = covid_API_request(nation_location, "nation" )

    nation_current_hospital_cases = "National Hospital Cases: " \
        + str(nation_covid_data["current_hospital_cases"])
    nation_total_deaths = "National Total Deaths: " + str(nation_covid_data["total_deaths"])

    covid_data = {"location_last7days_cases": ltla_covid_data["last7days_cases"], \
                  "nation_last7days_cases" : nation_covid_data["last7days_cases"], \
                      "nation_current_hospital_cases" : nation_current_hospital_cases, \
                          "nation_total_deaths" : nation_total_deaths}

def update_covid_data_if_not_present(nation_location = "England", location = "Exeter"):
    """
    This function will fetch covid data if no data is preseent
        by using the update_covid_data function
    """

    if not covid_data:
        update_covid_data(nation_location = "England", location = "Exeter")

def covid_API_request(location = "Exeter", location_type = "ltla"):
    """
    This function uses the uk_covid19 module and the API key from it
        to extract live data to be displayed on the flask interface
    It also formats what order the data must be fetched in to be stored in a dictionary
    """

    log.info("Making a covid API request"  + location + ", type=" + location_type)
    location_filter = [
    'areaType=' + location_type,
    'areaName=' + location
    ]
    log.info("Location name fetched: " + location + ", location type fetched: " + location_type)

    cases_and_deaths = {
    "areaCode": "areaCode",
    "areaName": "areaName",
    "areaType": "areaType",
    "date": "date",
    "cumDailyNsoDeathsByDeathDate": "cumDailyNsoDeathsByDeathDate",
    "hospitalCases": "hospitalCases",
    "newCasesBySpecimenDate": "newCasesBySpecimenDate",
    }

    api = Cov19API(filters=location_filter, structure=cases_and_deaths)

    data = api.get_json()

    csv_lines =[]

    """ Structuring data into lines to be read easily """
    for line in data["data"]:
        #areaCode,areaName,areaType,date,cumDailyNsoDeathsByDeathDate,
            #hospitalCases,newCasesBySpecimenDate
        csv_line = line["areaCode"] + "," + location + "," + location_type + \
            "," + line["date"] + "," + optional_value(line["cumDailyNsoDeathsByDeathDate"]) \
                + "," + optional_value(line["hospitalCases"]) + "," + \
                    optional_value(line["newCasesBySpecimenDate"]) + "\n"
        csv_lines.append(csv_line)

    last7days_cases, current_hospital_cases, total_deaths = \
        process_covid_csv_data(csv_lines)

    return {"last7days_cases": last7days_cases, "current_hospital_cases" \
            : current_hospital_cases, "total_deaths": total_deaths}

def optional_value(data):
    """
    This function will turn any values into a string so that all data
        can be stored together as the same data types
    """

    value = str(data)

    if value != "None":
        return value
    else:
        return ""

def schedule_covid_updates(update_interval, update_name):
    """
    This function allows the user to create scheduled updates
    This function works with the scheduler module and takes the time of the
        update, a name and whether it is to be repeated or not
    """

    nation_location, location = locations()

    scheduler = get_scheduler()
    event = scheduler.enter(update_interval, 1, update_covid_data,\
                kwargs = {"nation_location":nation_location, "location":location})

    log.info("Event for {} added to scheduler {}".format(update_name, event))

    return event

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
