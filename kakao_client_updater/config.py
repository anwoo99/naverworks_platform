from settings import INSTALLED_APPS, COMPANY_CLASS, MOKDONG_CLASS, SANGARM_CLASS
from lib.naverworksAPI import Tool
from lib.kakaoAPI import Channel
from lib.log import log
from path import KAKAO_DIR
from lib.config import (
	MUST, ERROR, PROGRESS, DEBUG,
)
import os
import traceback
import sys
import json
import time
import copy

APP_NAME = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
APP_INFO = INSTALLED_APPS[APP_NAME]

COMPANY_TAG_LIST = APP_INFO['company_tag_list']
OUR_TEAM_LIST = APP_INFO['our_team_list']
NAVERWORKS_APP_NAME = APP_INFO['naverworks_app_name']
SLEEP_TIME= APP_INFO["update_interval"]
KAKAO_CLIENT_FILENAME = APP_INFO['kakao_client_filename']

KAKAO_APP = APP_INFO["kakao_app"]
KAKAO_APP_REST_API = KAKAO_APP["app_keys"]["rest_api_key"]

KAKAO_CHANNEL = APP_INFO["kakao_channel"]
KAKAO_CHANNEL_PROFILE_ID = KAKAO_CHANNEL["profile_id"]

KAKAO_CONTACT_LIST_FILENAME = os.path.join(KAKAO_DIR, "kakao_contact_list.json")

KAKAO_CONTACT_TEMPLATE = {
    "id": "",
    "field" : {
        "이름": "",
        "회사명": "DEFAULT",
        "목동발송클래스": "DEFAULT",
        "상암발송클래스": "DEFAULT",
    }
}