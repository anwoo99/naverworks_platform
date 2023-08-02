from settings import INSTALLED_APPS
from lib.log import log
from lib.config import (
	MUST, ERROR, PROGRESS, DEBUG,
)
from lib.naverworksAPI import (
    GroupAndTeamDrive, Tool
)
from path import (
    WEEKLY_REPORT_DIR
)
from datetime import datetime
import datetime as dt
import os
import traceback
import schedule
import sys
import time
import copy
import openpyxl
from openpyxl.styles import Font
from openpyxl.styles import PatternFill

APP_NAME = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
APP_INFO = INSTALLED_APPS[APP_NAME]

NAVERWORKS_APP_NAME = APP_INFO['naverworks_app_name']
NAVERWORKS_BOT_ID = APP_INFO['bot_id']
NAVERWORKS_GROUP_NAME = APP_INFO['group_name']

CREATE_TIME = APP_INFO['create_time']
REPORT_DIR = APP_INFO['report_dir']
REPORT_FILE = APP_INFO['report_file']
SHEET_NAME = APP_INFO['sheet_name']
SLEEP_TIME = 10