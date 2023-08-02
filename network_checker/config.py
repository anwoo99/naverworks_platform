from settings import INSTALLED_APPS
import os
import threading

APP_NAME = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
APP_INFO = INSTALLED_APPS[APP_NAME]

NAVERWORKS_APP_NAME = APP_INFO['naverworks_app_name']
NAVERWORKS_BOT_ID = APP_INFO['bot_id']
NAVERWORKS_CAHNNEL_ID = APP_INFO['channel_id']

SLEEP_TIME = APP_INFO['check_interval']

SWITCH_INFO_MUTEX = threading.Lock()

SWITCH_INFO_TEMPLATE = {
    'hostname': '',
    'updatedTime': '',
    'interface': [

    ]
}

INTERFACE_INFO_TEMPLATE = {
    'port': '',
    'name': '',
    'status': '',
    'vlan': '',
    'duplex': '',
    'speed': '',
    'type': '',
    'traffic': {
        'intv': '',
        'rx_mbps': '',
        'rx_per': '',
        'rx_peak': '',
        'tx_mbps': '',
        'tx_per': '',
        'tx_peak': '',
        'multicast_drop': {
            '5_seconds': '',
            '10_seconds': '',
            '60_seconds': '',
            '5_minutes': '',
            '1_hours': '',
        },
        'unicast_drop': {
            '5_seconds': '',
            '10_seconds': '',
            '60_seconds': '',
            '5_minutes': '',
            '1_hours': '',
        },
        'all_drop': {
            '5_seconds': '',
            '10_seconds': '',
            '60_seconds': '',
            '5_minutes': '',
            '1_hours': '',
        },
    }
}


STATUS_TITLE_DICT = [
    { 
        'field': 'Port',
        'length': '',
        'start_index': '',
        'last_index': '',
    },
    { 
        'field': 'Name', 
        'length': '',
        'start_index': '',
        'last_index': '',
    },
    { 
        'field': 'Status', 
        'length': '',
        'start_index': '',
        'last_index': '',
    },
    { 
        'field': 'Vlan', 
        'length': '',
        'start_index': '',
        'last_index': '',
    },
    { 
        'field': 'Duplex', 
        'length': '',
        'start_index': '',
        'last_index': '',
    },
    { 
        'field': 'Speed', 
        'length': '',
        'start_index': '',
        'last_index': '',
    },
    { 
        'field': 'Type', 
        'length': '',
        'start_index': '',
        'last_index': '', 
    },
]