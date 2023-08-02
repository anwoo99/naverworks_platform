from settings import INSTALLED_APPS

import os

APP_NAME = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
APP_INFO = INSTALLED_APPS[APP_NAME]

NAVERWORKS_APP_NAMES = APP_INFO['naverworks_app_names']
REFRESH_INTERVAL = APP_INFO['refresh_interval']