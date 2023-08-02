from settings import (
    INSTALLED_APPS, EXCHANGE_MAP,
    MESSAGE_TEMPLATE, HOLIDAY_ALERT_HEADER,
    DELIMETER,
)
from lib.log import log
from lib.config import (
    DEBUG, PROGRESS, ERROR, MUST
)
from lib.naverworksAPI import (
    Tool
)
from path import (
    HOLIDAY_DIR
)

import os
import traceback
import sys
import schedule
from datetime import datetime
import time
import copy

APP_NAME = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
APP_INFO = INSTALLED_APPS[APP_NAME]

NAVERWORKS_APP_NAME = APP_INFO['naverworks_app_name']
NAVERWORKS_BOT_ID = APP_INFO['bot_id']
NAVERWORKS_CHANNEL_ID = APP_INFO['channel_id']

SLEEP_TIME = 10