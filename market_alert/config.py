from settings import INSTALLED_APPS
from lib.log import log
from settings import (
    MESSAGE_TEMPLATE, REMOTE_SERVER_INFO, MARKET_ALERT_HEADER,
    DELIMETER, SYSTEM_ALERT_HEADER
)
from lib.config import (
    MUST, ERROR, PROGRESS, DEBUG,
)
from lib.naverworksAPI import Bot, Tool

import socket
import threading
import signal
import sys
import os
import traceback

APP_NAME = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
APP_INFO = INSTALLED_APPS[APP_NAME]

NAVERWORKS_APP_NAME = APP_INFO['naverworks_app_name']
NAVERWORKS_BOT_ID = APP_INFO['bot_id']
NAVERWORKS_CHANNEL_ID = APP_INFO['channel_id']

SERVER_IP = APP_INFO['server_ip']
SERVER_PORT = APP_INFO['server_port']

MESSAGE_TYPE = "text"

MARKET_ALERT_TOKEN = "1"
SYSTEM_ALERT_TOKEN = "2"
DELIM = "\001"
EQUAL_DELIM = "="
