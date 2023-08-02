from settings import (
    INSTALLED_APPS, REMOTE_SERVER_INFO,
    OCC_NOTICE_ALERT_HEADER, DELIMETER
)
from lib.log import log
from lib.config import (
	MUST, ERROR, PROGRESS, DEBUG,
)
from lib.tool import (
    telnet, cmd_to_remote
)
from lib.naverworksAPI import (
    Tool
)
from path import (
    OCC_DIR
)

from bs4 import BeautifulSoup as bs
import os
import traceback
import sys
import time
import json
import requests

APP_NAME = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
APP_INFO = INSTALLED_APPS[APP_NAME]

NAVERWORKS_APP_NAME = APP_INFO['naverworks_app_name']
NAVERWORKS_BOT_ID = APP_INFO['bot_id']
NAVERWORKS_CAHNNEL_ID = APP_INFO['channel_id']

SLEEP_TIME = APP_INFO['check_interval']
BASE_SERVER = APP_INFO['base_server']
OCC_URL = APP_INFO["occ_url"]
EACH_NOTICE_URL = APP_INFO["each_notice_url"]

SYMBOL_GET_COMMAND = "cat /mdfsvc/fep/etc/{}-symb.csv"
NOTI_FILE = os.path.join(OCC_DIR, "{}.json".format(APP_NAME))
SYMBOL_FILE = os.path.join(OCC_DIR, "symbol.txt")