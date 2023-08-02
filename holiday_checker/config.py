from datetime import datetime, timedelta
from tabulate import tabulate
import sys
import pandas as pd
import exchange_calendars as xcals
import pytz
import schedule
import json
import time
import traceback
import copy
import os
import json

from settings import (
    INSTALLED_APPS, EXCHANGE_MAP, REMOTE_SERVER_INFO, TEST
)
from lib.log import log
from lib.abstractAPI import Holiday
from lib.naverworksAPI import Calendar, Tool
from lib.database import DataBase
from lib.tool import scp, text_color
from lib.config import (
    MUST, ERROR, PROGRESS, DEBUG,
    YELLOW
)
from path import (
    HOLIDAY_DIR
)

APP_NAME = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
APP_INFO = INSTALLED_APPS[APP_NAME]

DATABASE = APP_INFO['Database']
DB_MODEL = {
    'exchange': '',
    'date': '',
    'name': '',
}

ISO_HOLIDAY_DICT = {
    "date": "",
    "iso_code": "",
    "is_session": ""
}

COUNTRY_HOLIDAY_DICT = {
    "date": "",
    "country_code": "",
    "holiday_name": ""
}

HOLIDAY_DICT = {
    "date": "",
    "name": ""
}

DAYS_OF_WEEK = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

SLEEP_TIME = 10

REMOTE_HOLIDAY_DIR = "/mdfsvc/fep/etc/holidays"