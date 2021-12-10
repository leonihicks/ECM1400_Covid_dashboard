# ECM1400_2021_Covid_Coursework

## Introduction
This is python program is a dashboard to fetch the latest COVID-19 statistics and information. The project uses extracts data from the Public Health England API service. As well as to fetch recent COVID-19 news articles with a newsapi.org API address. The project is ran with flask to allow a user interface. This project has been created for the ECM1400 Programming Continuous Assessment (University of Exeter), therefore languages and methods have been given.

## Prerequisites
Python 3.8.8 was used for this project. It was ran on Spyder and Safari. 

Modules used for this projects were:

- logging
- json
- re
- datetime
- sched
- time

- flask
- requests
- uk_covid19
- pytest

### API key
- You will need a news API key to obtain the news articles. If you do not already have an active API key, you can register for free at: https://newsapi.org/register

### Installations
- You must also make sure you have the following installed within your project environment, use pip to install the following:

#### Flask:

` $pip install flask`

#### Public Health England COVID-19 Module:

` $pip install uk_covid19`

#### Requests:
` $pip install requests`

#### Pytest:
` $pip install -U pytest`


## Using the Program

### Customising your data

#### Config file

Before executing the program, you must fill out the figures in the config file to customise the program.

Make sure to copy your news Api key into the quotes next to `covid_news_api_key `. 

Then enter your nation location (e.g., England) into the string by `nation_location ` and your location (e.g., Exeter) into the string by `location `. 

- nation_location - can be set to a region, nation, ltla, overview, nhsRegion or utla
- location - can be any city in the UK

### Running the Program

To execute the program, open a programming environment that runs python 3.8.8 or newer. Once you have  installed all modules, you can run the dashboard from `main.py`

In order to access the dashboard on a browser, you can copy the given url: 
`http://127.0.0.1:5000/`

To quit the program, press CTRL + C in the terminal. 

### Testing

To execute the tests, make sure pytest has been installed into your programming environment. To run the tests, simply execute them in your project directory will the following line:

`python -m pytest covid_tests.py `

It'll then output how many tests have been passed. 

### Errors 

Any errors/warnings that need to be outputted, will be displayed in the logging file. 

### Scheduling

The data structures for scheduling are held in `scheduler.py`. They consist of a list of python scheduled events and a shadow list of dictionaries that control that are related to the python scheduled events but allow for cancelling events (aka jobs) for creating scheduled events for repeating jobs.

The news and covid data jobs are scheduled with a different delay in case the user schedules a combined update. Also the absolute data in the shadow list is slightly later to make sure these jobs are first run.

Generally there will be one event/job (in python scheduled events) for each shadow list of dictionaries - unless the users selects both "Update Covid data" and "Update news articles" as below

### SHADOW LIST OF DICTIONARY:

ITEM  1   {'title': 'repeat-both', 'update_time': '16:10', 'update_covid_data': 'covid-data', 'update_news': 'news', 'repeat': 'repeat', 'update_covid_event': Event(time=1639066210.0001369, priority=1, action=<function update_covid_data at 0x10d4b5a60>, argument=(), kwargs={'nation_location': 'England', 'location': 'Exeter'}), 'update_news_event': Event(time=1639066220.0000348, priority=1, action=<function update_news at 0x10d4b71f0>, argument=(), kwargs={}), 'absolute_delay_time': 1639066229.999995}

LIST OF SCHEDULER EVENTS/JOBS

JOB  1   Event(time=1639066210.0001369, priority=1, action=<function update_covid_data at 0x10d4b5a60>, argument=(), kwargs={'nation_location': 'England', 'location': 'Exeter'})
JOB  2   Event(time=1639066220.0000348, priority=1, action=<function update_news at 0x10d4b71f0>, argument=(), kwargs={})

## Details
### Author 
Leoni Hicks

### Course
ECM1400 Programming Continuous Assessment

### License
MIT License

## References

[Convert Epoch Seconds to Time](https://www.epochconverter.com/)
