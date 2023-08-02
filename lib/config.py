from settings import (
    NAVERWORKS_APP_INFO, MESSAGE_TEMPLATE, FLEXIBLE_MESSAGE_INFO, 
    REMOTE_SERVER_INFO, LOG_LEVEL
)
from path import (
    AUTH_DIR, LOG_DIR
)

from datetime import datetime, timedelta

import requests
import urllib.parse
import os
import copy
import time
import paramiko
import time
import telnetlib
import inspect
import pymysql
import base64
import hashlib
import hmac
import json


# Log
LOG_LEVEL_MAP = {
    "MUST": 3,
    "ERROR": 2,
    "PROGRESS": 1,
    "DEBUG": 0
}

DEBUG = "DEBUG"
PROGRESS = "PROGRESS"
ERROR = "ERROR"
MUST = "MUST"

# @ Auth
AUTH_URL = {
    'Oauth': {
        "AuthorizationCode" : "https://auth.worksmobile.com/oauth2/v2.0/authorize",
        "AccessToken": "https://auth.worksmobile.com/oauth2/v2.0/token",
        "RefreshAccessToken": "https://auth.worksmobile.com/oauth2/v2.0/token",
        "RevokeAccessToken": "https://auth.worksmobile.com/oauth2/v2.0/revoke"
    }
}

# @ Bot
BOT_URL = {
    'MessageSending': {
        "Channel" : "https://www.worksapis.com/v1.0/bots/{}/channels/{}/messages",
        "User": "https://www.worksapis.com/v1.0/bots/{}/users/{}/messages"
    }
}

# @ Directory
DIRECTORY_URL = {
    "Member": {
        "ListCheck": "https://www.worksapis.com/v1.0/users",
    },
    "Group": {
        "ListCheck": "https://www.worksapis.com/v1.0/groups",
    }
}

# @ Calendar
CALENDAR_URL = {
    "Calendar": {
        "Create": "https://www.worksapis.com/v1.0/calendars",
        "PersonalListCheck": "https://www.worksapis.com/v1.0/users/{}/calendar-personals",
    },
    "Event": {
        "Create": "https://www.worksapis.com/v1.0/users/{}/calendars/{}/events",
        "ListCheck": "https://www.worksapis.com/v1.0/users/{}/calendars/{}/events",
    }
}

# @ Drive
DRIVE_URL = {
    "GroupAndTeam" : {
        "File": {
            "RootFileListCheck": "https://www.worksapis.com/v1.0/groups/{}/folder/files",
            "FileListCheck": "https://www.worksapis.com/v1.0/groups/{}/folder/files/{}/children",
            "FileDownload" : "https://www.worksapis.com/v1.0/groups/{}/folder/files/{}/download",
            'RootFileUpload': "https://www.worksapis.com/v1.0/groups/{}/folder/files",
            'FileUpload': "https://www.worksapis.com/v1.0/groups/{}/folder/files/{}",
        },
        "Folder": {
            "Create": "https://www.worksapis.com/v1.0/groups/{}/folder/files/{}/createfolder",
            "RootCreate": "https://www.worksapis.com/v1.0/groups/{}/folder/files/createfolder"
        }
    }
}

# @ Contact
CONTACT_URL = {
    "ContactList": {
        "ListCheck": "https://www.worksapis.com/v1.0/contacts",
        "InfoCheck": "https://www.worksapis.com/v1.0/contacts/{}"
    },
    "ContactTag": {
        "ListCheck": "https://www.worksapis.com/v1.0/contact-tags"
    }
}


# @ Abstract API
ABSTRACT_URL = {
    "Holiday": "https://holidays.abstractapi.com/v1/",
}


# @ KAKAO API
KAKAO_CHANNEL_URL = {
    "CheckClient": "https://kapi.kakao.com/v1/talkchannel/target_user_file",
    "AddClient": "https://kapi.kakao.com/v1/talkchannel/update/target_users",
    "DeleteClient" : "https://kapi.kakao.com/v1/talkchannel/delete/target_users"
}

# TELNET TIMEOUT(Default)
DEFAULT_TELNET_TIMEOUT = 30

# TEXT Color
YELLOW = "\033[93m"
RED = '\033[91m'
GREEN = '\033[92m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'
WHITE = '\033[97m'
MAGENTA = '\033[95m'