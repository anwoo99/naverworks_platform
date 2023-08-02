import argparse
import sys
import ast
import os
from tabulate import tabulate

from lib.naverworksAPI import Auth
from settings import (
    INSTALLED_APPS, PYTHON, NAVERWORKS_APP_INFO, 
    EXIT_FLAG, RUN_FLAG, END_FLAG, CHK_FLAG
)
from lib.config import (
    DEBUG, PROGRESS, ERROR, MUST,
    YELLOW, RED, GREEN, BLUE, BOLD, WHITE, MAGENTA, RESET
)
from lib.tool import text_color
from lib.log import log
from holiday_checker.main import holiday_crud, holiday_loaddata, holiday_calendar_update
from runserver import runserver 
from path import BASE_DIR, MAIN_PIPE, MAIN_PIPE2

def send_request(message):
    try:
        if not os.path.exists(MAIN_PIPE):
            raise Exception("Main server is not running now. Please run 'python3 manage.py runserver'.")

        with open(MAIN_PIPE, "w") as pipe:
            pipe.write(message)

    except Exception as err:
        print(err)
        sys.exit()

def read_request():
    try:
        if not os.path.exists(MAIN_PIPE2):
            raise Exception("Main server is not running now. Please run 'python3 manage.py runserver'.")

        with open(MAIN_PIPE2, "r") as pipe:
            flag = pipe.read()

            return flag
    except Exception as err:
        print(err)
        sys.exit()

def run():
    message = RUN_FLAG + str(INSTALLED_APPS)
    send_request(message)

    while True:
        flag = read_request()

        if flag == END_FLAG:
            break

    print("Request successfully done.")

def killall():
    send_request(EXIT_FLAG)

    while True:
        flag = read_request()

        if flag == END_FLAG:
            break

    print("Request successfully done.")

def print_table(table):
    try:
        headers = table[0].keys()
        rows = [list(row.values()) for row in table]
        table_output = tabulate(rows, headers=headers, tablefmt="fancy_grid")
        print(table_output)
    except Exception as err:
        print(err)
        sys.exit()

def runcheck():
    send_request(CHK_FLAG)

    while True:
        message = read_request()

        if len(message) > 0:
            data = ast.literal_eval(message)
            print_table(data)
            break

def create_app(name):
    try:
        directory = os.path.join(BASE_DIR, name)
        os.mkdir(directory)
        fileList = ["__init__.py", "main.py", "config.py"]

        for index, file in enumerate(fileList):
            filename = os.path.join(directory, file)

            with open(filename, "w+") as fd:
                if index == 0:
                    fd.write("")
                elif index == 1:
                    fd.write("from {}.config import *\n".format(name))
                elif index == 2:
                    fd.write("from settings import INSTALLED_APPS\n")
                    fd.write("from lib.log import log\n")
                    fd.write("from lib.config import (\n\tMUST, ERROR, PROGRESS, DEBUG,\n)\n")
                    fd.write("import os\n\n")
                    fd.write("APP_NAME = os.path.basename(os.path.dirname(os.path.abspath(__file__)))\n")
                    fd.write("APP_INFO = INSTALLED_APPS[APP_NAME]\n")

    except Exception as err:
        print(err)
        sys.exit()
        
def print_auth_code_url(naverworks_app_name):
    try:
        app_info = NAVERWORKS_APP_INFO.get(naverworks_app_name)
        
        if app_info is None:
            raise Exception("=> 존재하지 않는 Naverworks 앱 이름입니다({}).".format(naverworks_app_name))
        
        auth = Auth(naverworks_app_name)
        url = auth.get_auth_code_url()
        print(url)
        print("=> 해당 값을 복사하여 크롬을 통해 로그인 후 \"code\" 값을 가져오세요.")

    except Exception as err:
        print(err)
        sys.exit()

def get_refresh_token(naverworks_app_name):
    try:
        app_info = NAVERWORKS_APP_INFO.get(naverworks_app_name)

        if app_info is None:
            raise Exception("=> 존재하지 않는 Naverworks 앱 이름입니다({}).".format(naverworks_app_name))

        auth = Auth(naverworks_app_name)
        response = auth.get_access_token()
        refresh_token = response['refresh_token']
        print(refresh_token)
        print("=> 해당 값을 settings.py 내 'NAVERWORKS_APP_INFO - \"{}\" - \"refresh_token\"' 에 복사하세요.".format(naverworks_app_name))

    except Exception as err:
        print(err)
        sys.exit()

def main():
    parser = argparse.ArgumentParser(prog="python3 manage.py", description="Management script of the program based on the NaverWorks")
    subparsers = parser.add_subparsers(title="commands", dest="command", metavar="command")

    # Runserver command
    runserver_parser = subparsers.add_parser("runserver", help="Execute the main server (run in the background)")

    # Run command
    run_parser = subparsers.add_parser("run", help="Query the running signal to the main server")

    # Check the running process command
    check_parser = subparsers.add_parser("runcheck", help="Check what process is running now")

    # Exit command
    exit_parser = subparsers.add_parser("killall", help="Send the exit signal to the main server")

    # Createapp command
    createapp_parser = subparsers.add_parser("createapp", help="Create a new app")
    createapp_parser.add_argument("app_name", help="Name of the app to create")

    # AuthcodeURL command
    authcodeURL_parser = subparsers.add_parser("authcodeurl", help="Print the authorization code URL for a Naverworks app")
    authcodeURL_parser.add_argument("app_name", help="Name of the Naverworks app")

    # RefreshToken command
    refreshToken_parser = subparsers.add_parser("refreshtoken", help="Get a refresh token")
    refreshToken_parser.add_argument("app_name", help="Name of the Naverworks app")

    # Holiday command
    holiday_parser = subparsers.add_parser("holiday", help="Processing the holiday database")
    holiday_subparsers = holiday_parser.add_subparsers(title="actions", dest="action", metavar="action")

    # CRUD subcommand
    crud_parser = holiday_subparsers.add_parser("crud", help="Perform CRUD operations on holidays")

    # Loaddata subcommand
    loaddata_parser = holiday_subparsers.add_parser("loaddata", help="Load data from a file")
    loaddata_parser.add_argument("filename", help="Name of the file to load")

    # Loaddata subcommand
    calendar_update_parser = holiday_subparsers.add_parser("calendarupdate", help="Update holiday on naverworks calendar")

    args = parser.parse_args()

    if args.command == "runserver":
        runserver()
    elif args.command == "run":
        run()
    elif args.command == "killall":
        killall()
    elif args.command == "createapp":
        create_app(args.app_name)
    elif args.command == "authcodeurl":
        print_auth_code_url(args.app_name)
    elif args.command == "refreshtoken":
        get_refresh_token(args.app_name)
    elif args.command == "runcheck":
        runcheck()
    elif args.command == "holiday":
        if args.action is None:
            print("Error: 'holiday' command requires an action (crud or loaddata or calendarupdate).")
        elif args.action == "crud":
            holiday_crud()
        elif args.action == "loaddata":
            if len(args.filename) <= 0:
                print("Please input a file name.")
                sys.exit()
            holiday_loaddata(args.filename)
        elif args.action == "calendarupdate":
            holiday_calendar_update()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

