from lib.log import log
from lib.config import (
    DEBUG, ERROR, PROGRESS, MUST
)
from lib.tool import (
    telnet, cmd_to_remote
)
from lib.naverworksAPI import (
    Bot, Tool
)
from path import (
    DEVICE_DIR
)
from network_checker.config import (
    NAVERWORKS_APP_NAME, APP_INFO, APP_NAME,
    NAVERWORKS_BOT_ID, NAVERWORKS_CAHNNEL_ID, 
    STATUS_TITLE_DICT, SWITCH_INFO_TEMPLATE,
    INTERFACE_INFO_TEMPLATE, SLEEP_TIME
)
from settings import (
    REMOTE_SERVER_INFO, NETWORK_DEVICE_INFO, NETWORK_ALERT_HEADER,
    DELIMETER,
)
from datetime import datetime
import sys
import traceback
import threading
import time
import copy
import ast
import os
import json

def get_remote_server_info(server_hostname):
    try:
        remote_server = next((server for server in REMOTE_SERVER_INFO if server['hostname'] == server_hostname), None)

        if remote_server is None:
            raise Exception("There is no dictionay for {} in REMOTE_SERVER_INFO".format(server_hostname))

        return remote_server
    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()

def login_to_remote(session, remote, index):
    try:
        log(APP_NAME, PROGRESS, "(Session: {})Access to {} now..".format(index, remote['hostname']))
        
        session = telnet(
            session, 
            remote['hostname'], 
            remote['id'], 
            remote['pw'], 
            remote['login_display'], 
            remote['password_display'], 
            remote['first_display']
        )

        log(APP_NAME, PROGRESS, "(Session: {})Finish to access to {}.".format(index, remote['hostname']))

        return session
    except Exception as err:
        log(APP_NAME, ERROR, err)
        return None

def get_title_length(title, status_title_dict):
    try:
        for index, status_title in enumerate(status_title_dict):
            if index < len(status_title_dict) - 1 :
                start_index = title.find(status_title_dict[index]['field'])
                last_index  = title.find(status_title_dict[index + 1]['field'])
                status_title['length'] = last_index - start_index
                status_title['start_index'] = start_index
                status_title['last_index'] = last_index
            else:
                start_index = title.find(status_title_dict[index]['field'])
                status_title['length'] = len(title) - start_index
                status_title['start_index'] = start_index
                status_title['last_index'] = -1

        return status_title_dict
    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()

def parsing_status_output(network_device, status_output, new_switch_info):
    try:
        status_output_list = status_output.split('\n')[2:-1]

        # show interfaces status 출력 값을 저장할 딕셔너리 카피
        status_title_dict = copy.deepcopy(STATUS_TITLE_DICT)

        # 타이틀 라인 체크
        line = next((index for index, status in enumerate(status_output_list) if status_title_dict[0]['field'] in status), None)


        if line is None:
            return

        # show interfaces status 출력 값 제목 당 할당 길이 확인
        status_title_dict = get_title_length(status_output_list[line], status_title_dict)

        # 각 포트 정보가 시작되는 라인 체크
        line = next((index for index, status in enumerate(status_output_list) if "Eth" in status or 'Gi' in status), None)
        
        if line is None:
            return

        for status in status_output_list[line: network_device['number_of_port'] + line]:
            interface_info = copy.deepcopy(INTERFACE_INFO_TEMPLATE)
           
            for index, status_title in enumerate(status_title_dict):
                if index == 0:
                    start_index = status_title['start_index']
                else:
                    start_index = status_title['start_index'] - 1

                if index == len(status_title_dict) - 1:
                    end_index = status_title['last_index']
                else:
                    end_index = status_title['last_index'] - 1

                field_value = status[start_index:end_index].strip()

                if index == 0:
                    interface_info['port'] = field_value
                elif index == 1:
                    interface_info['name'] = field_value
                elif index == 2:
                    interface_info['status'] = field_value
                elif index == 3:
                    interface_info['vlan'] = field_value
                elif index == 4:
                    interface_info['duplex'] = field_value
                elif index == 5:
                    interface_info['speed'] = field_value
                elif index == 6:
                    interface_info['type'] = field_value

            new_switch_info['interface'].append(interface_info)

        return new_switch_info
    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()

def read_last_switch_info(filename):
    try:
        try:
            with open(filename, "r+") as fd:
                output = fd.read()
        except FileNotFoundError:
            output = ""

        if len(output) > 0:
            last_switch_info = ast.literal_eval(output)
        else: 
            last_switch_info = {}

        return last_switch_info
    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()

def update_last_switch_info(new_switch_info, filename, tmpfile):
    try:
        with open(filename, "w+") as fd:
            json.dump(new_switch_info, fd, indent=4)
        with open(tmpfile, "w+") as fd:
            json.dump(new_switch_info, fd, indent=4)
    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()

def compare_interface_status(new_swith_info, last_switch_info):
    try:
        message_list = []

        if len(last_switch_info) > 0:
            last_interface_info = last_switch_info['interface']
            new_interface_info = new_swith_info['interface']

            for last, new in zip(last_interface_info, new_interface_info):
                if last['port'] != new['port']:
                    break

                if last['name'] != new['name']:
                    message_list.append("[{}] [{}] [{}] 'Name'이 변경되었습니다. ({}) --> ({})".format(new_swith_info['hostname'], new['port'], new['name'], last['name'], new['name'])) 

                if last['status'] != new['status']:
                    message_list.append("[{}] [{}] [{}] 'Status'가 변경되었습니다. ({}) --> ({})".format(new_swith_info['hostname'], new['port'], new['name'], last['status'], new['status'])) 

                if last['vlan'] != new['vlan']:
                    message_list.append("[{}] [{}] [{}] 'Vlan'이 변경되었습니다. ({}) --> ({})".format(new_swith_info['hostname'], new['port'], new['name'], last['vlan'], new['vlan'])) 

                if last['duplex'] != new['duplex']:
                    message_list.append("[{}] [{}] [{}] 'Duplex'가 변경되었습니다. ({}) --> ({})".format(new_swith_info['hostname'], new['port'], new['name'], last['duplex'], new['duplex'])) 

                if last['speed'] != new['speed']:
                    message_list.append("[{}] [{}] [{}] 'Speed'가 변경되었습니다. ({}) --> ({})".format(new_swith_info['hostname'], new['port'], new['name'], last['speed'], new['speed'])) 

            for message in message_list:
                try:
                    Tool.send_alert_text_message_to_bot(NAVERWORKS_APP_NAME, NAVERWORKS_BOT_ID, NAVERWORKS_CAHNNEL_ID, message, "network_alert")
                except Exception as err:
                    log(APP_NAME, ERROR, err)

    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()

def init_new_switch_info(network_device, now):
    try:
        weekday = (now.weekday() + 1) % 7
        filename = os.path.join(DEVICE_DIR, "{}-{}.txt".format(network_device['hostname'], weekday))
        tmpfile = os.path.join(DEVICE_DIR, "{}.txt".format(network_device['hostname']))

        new_switch_info = copy.deepcopy(SWITCH_INFO_TEMPLATE)
        new_switch_info['hostname'] = network_device['hostname']
        new_switch_info['updatedTime'] = now.strftime("%Y/%m/%d %H:%M:%S")

        return new_switch_info, filename, tmpfile
    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()

def monitor_network(network_device, index):
    try:
        # Get the information of remote server
        remote_server = get_remote_server_info(network_device['server_hostname'])

        while True:
            session = None

            # First Login to the remote server connected to network device
            session = login_to_remote(session, remote_server, index)

            if session is None:
                log(APP_NAME, ERROR, "(Session: {})Cannot access to {}".format(index, remote_server['hostname']))
                time.sleep(SLEEP_TIME)
                continue

            # Second Login to the network device
            session = login_to_remote(session, network_device, index)

            if session is None:
                log(APP_NAME, ERROR, "(Session: {})Cannot access to {}".format(index, network_device['hostname']))
                time.sleep(SLEEP_TIME)
                continue
    
            # Set terminal length
            session, _ = cmd_to_remote(session, "terminal length 300", network_device['first_display'])

            # Get the output from commands("show interfaces status")
            session, status_output = cmd_to_remote(session, "show interface status", network_device['first_display'], True)
            
            # Session close
            session.close()

            # Get the current time
            now = datetime.now()
            hm = now.strftime('%H:%M')

            # Initaialize the template of switch info
            new_switch_info, filename, tmpfile = init_new_switch_info(network_device, now)

             # show interface status 출력물을 dictionary 형태로 파싱
            new_switch_info = parsing_status_output(network_device, status_output, new_switch_info)

            # 마지막으로 저장된 switch 정보 읽어오기
            last_switch_info = read_last_switch_info(tmpfile)

            # 마지막으로 저장된 interface 상태와 현재 상태 비교
            if hm != "00:00":
                compare_interface_status(new_switch_info, last_switch_info)

            # Update the last switch information
            update_last_switch_info(new_switch_info, filename, tmpfile)

            # Done
            time.sleep(SLEEP_TIME)
    except Exception as err:
        if session is not None:
            session.close()

        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()

def main():
    try:
        threads = []
        for index, network_device in enumerate(NETWORK_DEVICE_INFO):
            if network_device['network_check'] == False:
                continue

            log(APP_NAME, "PROGRESS", "(Session: {})Montioring Thread for {} is start..!".format(index, network_device['hostname']))
            mon_network_thread = threading.Thread(target=monitor_network, args=(network_device, index, ))
            mon_network_thread.start()
            threads.append(mon_network_thread)
            
        # Wait for all threads to complete
        for thread in threads:
            thread.join()

    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()
if __name__ == "__main__":
    main()
