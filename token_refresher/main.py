import sys
import time

from token_refresher.config import (
    APP_NAME, 
    NAVERWORKS_APP_NAMES,
    REFRESH_INTERVAL
)
from settings import (
    NAVERWORKS_APP_INFO,
)
from lib.config import (
    MUST, ERROR, PROGRESS, DEBUG
)
from path import AUTH_DIR
from lib.log import log
from lib.naverworksAPI import Auth

import os

def save_access_token(naverworks_app_name, access_token):
    try:
        directory = AUTH_DIR + '/{}'.format(naverworks_app_name)
        os.makedirs(directory, exist_ok=True)
        
        file_name = directory + '/access_token.txt'
        with open(file_name, 'w+') as fd:
            fd.write(access_token)
            return
    except Exception as err:
        log(APP_NAME, ERROR, err)
        sys.exit()

def update_access_token(naverworks_app_names):
    try:
        for naverworks_app_name in naverworks_app_names:
            if naverworks_app_name in NAVERWORKS_APP_INFO:
                auth = Auth(naverworks_app_name)
                response = auth.refresh_access_token()
                access_token = response['access_token']
                save_access_token(naverworks_app_name, access_token)
            else:
                raise Exception("This {} naveworks app is not enrolled in settings.py")
    except Exception as err:
        log(APP_NAME, ERROR, err)
        sys.exit()

def main():
    try:
        while True:
            log(APP_NAME, PROGRESS, "Update Access Token now...")
            update_access_token(NAVERWORKS_APP_NAMES)
            log(APP_NAME, PROGRESS, "Update Access Token done... sleep({})".format(REFRESH_INTERVAL))
            time.sleep(REFRESH_INTERVAL)
    except Exception as err:
        log(APP_NAME, ERROR, err)
        sys.exit()

if __name__ == "__main__":
    main()