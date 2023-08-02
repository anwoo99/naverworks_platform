from lib.config import *

class Tool():
    def __str__(self):
        return "This is the class for useful tool using Naverworks API"

    @staticmethod
    def get_stored_access_token(naverworks_app_name):
        try:
            file_name = "{}/access_token.txt".format(os.path.join(AUTH_DIR, naverworks_app_name))
            with open(file_name, "r") as fd:
                access_token = fd.read().strip()
                return access_token
        except FileNotFoundError:
            raise Exception("Access token file not found for {}".format(naverworks_app_name))
        except Exception as err:
            raise Exception("Failed to get stored access token for {}: {}".format(naverworks_app_name, err)) from err

    @staticmethod
    def get_user(naverworks_app_name, korean_name):
        try:
            directory = Directory(naverworks_app_name=naverworks_app_name)
            cursor = None
            user_info = None
            
            while True: 
                response = directory.member_list_check(cursor=cursor)
                users = response.json().get('users')
            
                for user in users:
                    username = user["userName"]
                    lastname = username["lastName"]
                    firstname = username["firstName"]
                    name = lastname + firstname

                    if name == korean_name:
                        user_info = user
                        break

                if user_info:
                    break
                else:
                    next_cursor = response.json().get('responseMetaData').get('nextCursor')
                    if next_cursor:
                        cursor = next_cursor
                        continue
                    else:
                        user_info = None
                        break
            return user_info
        except Exception as err:
            raise Exception("Failed to get user id for {}".format(korean_name)) from err

    @staticmethod
    def get_user_list(naverworks_app_name, korean_name_list):
        try:
            directory = Directory(naverworks_app_name=naverworks_app_name)
            cursor = None
            user_info_list = []
            
            while True: 
                response = directory.member_list_check(cursor=cursor)
                users = response.json().get('users')
            
                for user in users:
                    username = user["userName"]
                    lastname = username["lastName"]
                    firstname = username["firstName"]
                    name = lastname + firstname

                    if name in korean_name_list:
                        user_info_list.append(user)

                next_cursor = response.json().get('responseMetaData').get('nextCursor')

                if not next_cursor:
                    break
                
                cursor = next_cursor 
            return user_info_list
        except Exception as err:
            raise Exception("Failed to get user id list") from err

    @staticmethod
    def get_group(naverworks_app_name, korean_name):
        try:
            directory = Directory(naverworks_app_name=naverworks_app_name)
            cursor = None
            group_info = None

            while True:
                response = directory.group_list_check(cursor=cursor)
                groups = response.json().get('groups')

                for group in groups:
                    group_name = group.get('groupName')

                    if korean_name == group_name:
                        group_info = group
                        break
                if group_info:
                    break
                else:
                    next_cursor = response.json().get('responseMetaData').get('nextCursor')
                    if next_cursor:
                        cursor = next_cursor
                        continue
                    else:
                        group_info = None
                        break
            return group_info        
        except Exception as err:
            raise Exception("Failed to get the group id for {}".format(korean_name)) from err
        
    @staticmethod
    def get_calendar(naverworks_app_name, username, calendar_name):
        try:
            calendar = Calendar(naverworks_app_name, username)
            cursor = None
            calendar_info = None

            while True:
                response = calendar.personal_calendar_list_check(cursor=cursor)
                calendars = response.json().get("calendarPersonals")

                for calendar_data in calendars:
                    calendar_name_data = calendar_data["calendarName"]
                    
                    if calendar_name_data == calendar_name:
                        calendar_info = calendar_data
                        break

                if calendar_info:
                    break
                else:
                    next_cursor = response.json().get('responseMetaData').get('nextCursor')
                    if next_cursor:
                        cursor = next_cursor
                        continue
                    else:
                        calendar_info = None
                        break
            return calendar_info
        except Exception as err:
            raise Exception("Failed to get calendar id for {}".format(calendar_name)) from err

    # 현재 세팅되어있는 모든 태그 값 가져오기
    @staticmethod
    def get_all_contact_tag(naverworks_app_name):
        try:
            contact = Contact(naverworks_app_name=naverworks_app_name)
            cursor = None
            tag_list = []

            while True:
                response = contact.tag_list_check(cursor=cursor, count=100)  # Adjust count if needed
                contactTags = response.json().get("contactTags")
                tag_list.extend(contactTags)

                next_cursor = response.json().get('responseMetaData').get('nextCursor')
                if not next_cursor:
                    break

                cursor = next_cursor

            return tag_list
        except requests.exceptions.RequestException as err:
            raise ValueError("Failed to get all contact tags") from err

    # 태그 아이디를 넘겨주면, [{"태그 아이디": "태그 이름"}] 형태로 리턴
    @staticmethod
    def get_all_contact_tag_map(naverworks_app_name):
        try:
            tag_dict = Tool.get_all_contact_tag(naverworks_app_name)
            tag_map = {}

            for tag in tag_dict:
                tag_map[tag["contactTagId"]] = tag["contactTagName"]

            return tag_map
        except Exception as err:
            raise Exception("Failed to get the contact tag map")

    # 현재 저장되어있는 모든 연락처 정보 중, 특정 태그에 해당하는 연락처만 분류하여 리턴
    @staticmethod
    def get_contact_in_tags(naverworks_app_name, tag_name_list, phone_number_check=False):
        try:
            contact = Contact(naverworks_app_name=naverworks_app_name)
            tag_dict = Tool.get_all_contact_tag(naverworks_app_name)
            
            if not tag_dict:
                raise ValueError("Tag dict is empty")

            cursor = None
            contact_list = []

            while True:
                response = contact.contact_list_check(cursor=cursor)
                contacts = response.json().get("contacts")

                for contact_data in contacts:            
                    
                    # 폰 번호가 있는지 확인
                    if phone_number_check:
                        contact_telephones = contact_data["telephones"]
                        is_phone = False
                        
                        for telephone in contact_telephones:
                            if telephone.get("type") == "CELLPHONE" and len(telephone.get("telephone")) > 0:
                                is_phone = True
                                break

                        if not is_phone:
                            continue
                    
                    # tag dictionary 에 속해있는 연락처인지 확인
                    contact_tagIds = contact_data["contactTagIds"]
                    is_company = False

                    for tagId in contact_tagIds:
                        for tag in tag_dict:
                            if tag["contactTagId"] == tagId:
                                if tag["contactTagName"] in tag_name_list:
                                    is_company = True
                                    break
                        if is_company:
                            break

                    if not is_company:
                        continue

                    contact_list.append(contact_data)
                
                next_cursor = response.json().get("responseMetaData").get("nextCursor")

                if not next_cursor:
                    break

                cursor = next_cursor

            return contact_list
        except Exception as err:
            raise Exception("Failed to get the contact in the tags")
    

    @staticmethod
    def get_group_file(naverworks_app_name, groupName, pathList):
        try:
            group_drive = GroupAndTeamDrive(
                naverworks_app_name=naverworks_app_name,
                groupName=groupName
            )
            cursor = None
            file_info = None

            for step, path in enumerate(pathList):
                new_file_info = None

                while True:
                    if step == 0:
                        response = group_drive.check_file_list(
                            cursor=cursor
                        )
                    else:
                        response = group_drive.check_file_list(
                            fileId=file_info.get('fileId'),
                            cursor=cursor,
                            is_root=False
                        )

                    fileList = response.json().get('files')

                    for file in fileList:
                        if file.get('fileName') == path:
                            new_file_info = file
                            break
                        else:
                            new_file_info = None
                    
                    if new_file_info:
                        file_info = new_file_info
                        break
                    else:
                        next_cursor = response.json().get('responseMetaData').get('nextCursor')
                        
                        if next_cursor:
                            cursor = next_cursor
                            continue
                        else:
                            return None

            return file_info
        except Exception as err:
            raise Exception("Failed to get group file information")

    @staticmethod
    def download_group_file(naverworks_app_name, groupName, pathList):
        try:
            file_info = Tool.get_group_file(
                naverworks_app_name=naverworks_app_name,
                groupName=groupName,
                pathList=pathList
            )

            if file_info is None:
                raise Exception
            
            group_drive = GroupAndTeamDrive(
                naverworks_app_name=naverworks_app_name,
                groupName=groupName
            )

            fileId = file_info.get('fileId')

            fileData = group_drive.download(fileId=fileId)
            return fileData
        except Exception as err:
            raise Exception("Failed to download group file")

    @staticmethod
    def upload_group_file(naverworks_app_name, groupName, file_location, pathList=None, is_root=True):
        try:
            fileId = None

            if not is_root:
                file_info = Tool.get_group_file(
                    naverworks_app_name=naverworks_app_name,
                    groupName=groupName,
                    pathList=pathList
                )

                if file_info is None:
                    raise Exception
                
                fileId = file_info.get('fileId')
            
            group_drive = GroupAndTeamDrive(
                naverworks_app_name=naverworks_app_name,
                groupName=groupName
            )

            fileName = os.path.basename(file_location)
            fileSize = os.path.getsize(file_location)

            fileData = open(file_location, 'rb')
            
            response = group_drive.upload(
                fileName=fileName,
                fileSize=fileSize,
                fileData=fileData,
                fileId=fileId,
                is_root=is_root
            )
            return response
        except Exception as err:
            raise Exception("Failed to upload group file")

    @staticmethod
    def create_unique_calendar_event(naverworks_app_name, username, calendar_name: str, summary: str, start: datetime, **kwargs):
        try:
            calendar = Calendar(naverworks_app_name, username)
            response = calendar.check_calendar_event_list(calendar_name, start.replace(hour=0, minute=0, second=0), kwargs.get('end', start + timedelta(seconds=10)))
            event_dict = response.json()
            events = event_dict['events']
            
            for event in events:
                eventComponents = event['eventComponents']
                event_summaries = [eventComponent['summary'] for eventComponent in eventComponents]
                
                if summary in event_summaries:
                    return ("This summary({}) is already existed on {} (date: {})".format(summary, calendar_name, start.date()))
                
            response = calendar.create_calendar_events(calendar_name, summary, start, **kwargs)
            return response
        except Exception as err:
            raise Exception("Failed to create unique calendar event..!") from err
    
    @staticmethod
    def send_text_message_to_bot(naverworks_app_name, naverworks_bot_id, naverworks_channel_id, text):
        try:
            bot = Bot(naverworks_app_name, naverworks_bot_id)
            template = copy.deepcopy(MESSAGE_TEMPLATE)
            params = template["text"]
            params["content"]["text"] = text

            response = bot.send_message_to_channel(naverworks_channel_id, params)

            if response.status_code != 201:
                raise Exception("Sending result: {}".format(response.json()))

        except Exception as err:
            raise Exception("Failed to send text message to NaverWorks Bot({})".format(err)) from err

    @staticmethod
    def send_link_message_to_bot(naverworks_app_name, naverworks_bot_id, naverworks_channel_id, contentText, linkText, link):
        try:
            bot = Bot(naverworks_app_name, naverworks_bot_id)
            template = copy.deepcopy(MESSAGE_TEMPLATE)
            params = template["link"]
            params["content"]["contentText"] = contentText
            params["content"]["linkText"] = linkText
            params["content"]["link"] = link

            response = bot.send_message_to_channel(naverworks_channel_id, params)

            if response.status_code != 201:
                raise Exception("Sending result: {}".format(response.json()))

        except Exception as err:
            raise Exception("Failed to send text message to NaverWorks Bot({})".format(err)) from err

    @staticmethod
    def send_alert_text_message_to_bot(naverworks_app_name, naverworks_bot_id, naverworks_channel_id, text, alert_type:str):
        try:
            bot = Bot(naverworks_app_name, naverworks_bot_id)
            template = copy.deepcopy(MESSAGE_TEMPLATE)
            params = template['flexible']['alert']

            alert_message_info = copy.deepcopy(FLEXIBLE_MESSAGE_INFO).get('alert').get(alert_type)
            title_info = alert_message_info.get('title')
            body_info = alert_message_info.get('body')
            body_info['content']['text'] = text

            params['content']['altText'] = text
            params['content']['contents']["header"]["backgroundColor"] = title_info.get('backgroundColor')
            params['content']['contents']["header"]["contents"].append(title_info['content'])
            params['content']['contents']["body"]["contents"].append(body_info['content'])
            response = bot.send_message_to_channel(naverworks_channel_id, params)

            if response.status_code != 201:
                raise Exception("Sending result: {}".format(response.json()))

        except Exception as err:
            raise Exception("Failed to send text alert message to NaverWorks Bot({})".format(err)) from err

    @staticmethod
    def send_alert_link_message_to_bot(naverworks_app_name, naverworks_bot_id, naverworks_channel_id, link, text, alert_type:str):
        try:
            bot = Bot(naverworks_app_name, naverworks_bot_id)
            template = copy.deepcopy(MESSAGE_TEMPLATE)
            params = template['flexible']['alert']

            alert_message_info = copy.deepcopy(FLEXIBLE_MESSAGE_INFO).get('alert').get(alert_type)
            title_info = alert_message_info.get('title')
            body_info = alert_message_info.get('body')
            body_info['contents'][0]['text'] = text
            body_info['contents'][1]['action']['uri'] = link

            params['content']['altText'] = text
            params['content']['contents']["header"]["backgroundColor"] = title_info.get('backgroundColor')
            params['content']['contents']["header"]["contents"].append(title_info['content'])
            params['content']['contents']["body"]["contents"] = body_info['contents']
            response = bot.send_message_to_channel(naverworks_channel_id, params)

            if response.status_code != 201:
                raise Exception("Sending result: {}".format(response.json()))

        except Exception as err:
            raise Exception("Failed to send link alert message to NaverWorks Bot({})".format(err)) from err

    @staticmethod
    def make_message_formatting(header, delimeter, message):
        return f"{header}\n{delimeter}\n{message}\n{delimeter}"

# 참고사항
class Note():
    @staticmethod
    def file_download(url, access_token):
        try:
            headers = {
                'Authorization': 'Bearer {}'.format(access_token),
            }

            response = requests.get(url, headers=headers)
            response.raise_for_status()
            file_data = response.content
            return file_data
        except requests.exceptions.RequestException as err:
            raise Exception("Failed to download materials in Naverworks") from err

    @staticmethod
    def file_upload(url, access_token, fileData):
        try:
            headers = {
                'Authorization': 'Bearer {}'.format(access_token),
            }
            files = {
                'file': fileData
            }

            response = requests.post(url, headers=headers, files=files)
            return response
        except requests.exceptions.RequestException as err:
            raise Exception("Failed to upload materials in Naverworks") from err

class Auth():
    def __init__(self, naverworks_app_name):
        self.naverworks_app_name = naverworks_app_name
    def __str__(self):
        return "This is the class for NaverWorks authorization"
    def __get_app_info(self):
        try:
            return(NAVERWORKS_APP_INFO[self.naverworks_app_name])
        except Exception as err:
            raise Exception("Invalid app name: {}".format(self.naverworks_app_name)) from err
    def __make_auth_code_params(self, app_info):
        try:
            params = {
                'client_id': app_info['client_id'],
                'redirect_uri': app_info['redirect_uri'],
                'scope': app_info['scope'],
                'response_type': "code",
                'state': app_info['state'],
                'domain': app_info['domain']
            }
            return params
        except KeyError as err:
            raise Exception("Missing required keys in app_info") from err
    
    # Authorization code 발급
    def get_auth_code_url(self):
        try:
            app_info = self.__get_app_info()
            params = self.__make_auth_code_params(app_info)
            encoded_params = urllib.parse.urlencode(params)
            get_url = "{}?{}".format(AUTH_URL['Oauth']['AuthorizationCode'], encoded_params)
            return get_url
        except Exception as err:
            raise Exception("Failed to get auth code URL") from err
    def __make_get_access_token_params(self, app_info):
        try:
            if len(app_info['auth_code']) <= 0:
                raise Exception("'auth_code' 값이 비어있습니다. python manage.py authcodeURL {} 을 통해 code를 받아오세요..!".format(self.naverworks_app_name))
            
            params = {
                    'code': app_info['auth_code'],
                    'grant_type': "authorization_code",
                    'client_id': app_info['client_id'],
                    'client_secret': app_info['client_secret'],
                    'domain': app_info['domain']
            }
            
            return params
        except KeyError as err:
            raise Exception("Missing required keys in app_info") from err
        except Exception as err:
            raise Exception("Failed to make access token params") from err

    # Access Token 발급
    def get_access_token(self):
        try:
            app_info = self.__get_app_info()
            header = {'Content-Type': 'application/x-www-form-urlencoded'}
            params = self.__make_get_access_token_params(app_info)
            response = requests.post(AUTH_URL['Oauth']['AccessToken'], headers=header, data=params)
            return response.json()
        except Exception as err:
            raise(Exception("Failed to get access token")) from err

    def __make_refresh_access_token_params(self, app_info):
        try:
            if len(app_info['refresh_token']) <= 0:
                raise Exception("'refresh_token' 값이 비어있습니다.")

            params = {
                    'refresh_token': app_info['refresh_token'],
                    'grant_type': "refresh_token",
                    'client_id': app_info['client_id'],
                    'client_secret': app_info['client_secret'],
            }

            return params
        except KeyError as err:
            raise Exception("Missing required keys in app_info") from err
        except Exception as err:
            raise Exception("Failed to make access token params") from err

    # Access Token 갱신
    def refresh_access_token(self):
        try:
            app_info = self.__get_app_info()
            header = {'Content-Type': 'application/x-www-form-urlencoded'}
            params = self.__make_refresh_access_token_params(app_info)
            response = requests.post(AUTH_URL['Oauth']['RefreshAccessToken'], headers=header, data=params)
            return response.json()
        except Exception as err:
            raise(Exception("Failed to refresh access token")) from err

class Bot():
    def __init__(self, naverworks_app_name, botId, botSecret=None):
        self.naverworks_app_name = naverworks_app_name
        self.botId = botId
        self.botSecret = botSecret
        self.initialize()

    def initialize(self):
        try:
            self.__access_token = Tool().get_stored_access_token(self.naverworks_app_name)
        except Exception as err:
            raise Exception("Bot initialization error") from err
        
    def __str__(self):
        return "This is the class for NaverWorks Bot"
        
    def __confirmation(self, header, body):
        try:
            # Bot ID Confirmation
            if self.botId != header.get('X-WORKS-BotId'.lower()):
                return False

            # Signature Confirmation
            # hash = hmac.new(self.botSecret.encode('utf-8'), bytes(json.dumps(body), 'utf-8'), hashlib.sha256).digest()
            # signature = base64.b64encode(hash).decode('utf-8')

            # if signature != header.get('X-WORKS-Signature'.lower()):
            #     return False
            
            return True
        except Exception as err:
            return False

    def callback_validation(self, request):
        try:
            header = request.headers
            body = request.get_json()
            is_ok = self.__confirmation(header, body)
            
            return is_ok, body
        except Exception as err:
            raise Exception("Failed to execute callback function") from err

    # 메세지 전송 - 채널 대상
    def send_message_to_channel(self, channelid, params):
        try:
            self.initialize()
            post_url = BOT_URL["MessageSending"]["Channel"].format(self.botId, channelid)
            header = {
                'Authorization': 'Bearer {}'.format(self.__access_token),
                'Content-Type': 'application/json'
            }
            
            response = requests.post(post_url, headers=header, json=params)
            return response
        except Exception as err:
            raise(Exception("Failed to send_message_to_channel({})".format(channelid))) from err

class Directory():
    def __init__(self, naverworks_app_name):
        self.naverworks_app_name = naverworks_app_name
        self.initialize()

    def initialize(self):
        try:
            self.__access_token = Tool().get_stored_access_token(self.naverworks_app_name)
        except Exception as err:
            raise Exception("Directory initialization error") from err
    
    def __str__(self):
        return "This is the class for NaverWorks Calendar"
    
    def __make_member_list_check_params(self, **kwargs):
        try:
            params = {
                "domainId": kwargs.get('domainId', None) ,
                "count": kwargs.get('count', None),
                "cursor": kwargs.get('cursor', None),
                "searchFilterType": kwargs.get('searchFilterType', None),
                "orderBy": kwargs.get('orderBy', None),
                "sortOrder": kwargs.get('sortOrder', None),
            }
            return params
        except KeyError as err:
            raise Exception("Missing required keys in member_list_check") from err

    # 구성원 - 목록조회
    def member_list_check(self, **kwargs):
        try:
            self.initialize()

            headers = {
                'Authorization': 'Bearer {}'.format(self.__access_token)
            }
            params = self.__make_member_list_check_params(**kwargs)
            response = requests.get(DIRECTORY_URL["Member"]["ListCheck"], headers=headers, params=params)
            response.raise_for_status()
            return response
        except Exception as err:
            raise Exception("Failed to check the list of members") from err

    def __make_group_list_check_params(self, domainId, count, cursor):
        try:
            params = {
                "domainId": domainId,
                "count": count,
                "cursor": cursor,
            }
            return params
        except KeyError as err:
            raise Exception("Missing required keys in member_list_check") from err

    # 그룹 - 목록 조회
    def group_list_check(self, domainId = None, count = None, cursor = None):
        try:
            self.initialize()
            headers = {
                'Authorization': 'Bearer {}'.format(self.__access_token)
            }
            get_url = DIRECTORY_URL["Group"]["ListCheck"]
            params = self.__make_group_list_check_params(domainId, count, cursor)
            response = requests.get(get_url, headers=headers, params=params)
            response.raise_for_status()
            return response
        except Exception as err:
            raise Exception("Failed to check the list of groups") from err
        
class Contact():
    def __init__(self, naverworks_app_name):
        self.naverworks_app_name = naverworks_app_name
        self.initialize()

    def initialize(self):
        try:
            self.__access_token = Tool().get_stored_access_token(self.naverworks_app_name)
        except Exception as err:
            raise Exception("Directory initialization error") from err
    
    def __str__(self):
        return "This is the class for NaverWorks Contact"
    
    def __make_contact_list_check_params(self, count, cursor):
        try:
            params = {
                "count": count,
                "cursor": cursor,
            }
            return params
        except KeyError as err:
            raise Exception("Missing required keys in contact_list_check") from err

    def contact_list_check(self, count=None, cursor=None):
        try:
            self.initialize()
            headers = {
                'Authorization': 'Bearer {}'.format(self.__access_token)
            }
            get_url = CONTACT_URL["ContactList"]["ListCheck"]
            params = self.__make_contact_list_check_params(count, cursor)
            response = requests.get(get_url, headers=headers, params=params)
            response.raise_for_status()
            return response
        except Exception as err:
            raise Exception("Failed to check the list of contact")
    
    def __make_tag_list_check_params(self, count, cursor):
        try:
            params = {
                "count": count,
                "cursor": cursor,
            }
            return params
        except KeyError as err:
            raise Exception("Missing required keys in tag_list_check") from err

    def tag_list_check(self, count=None, cursor=None):
        self.initialize()
        headers = {
            'Authorization': 'Bearer {}'.format(self.__access_token)
        }
        get_url = CONTACT_URL["ContactTag"]["ListCheck"]
        params = self.__make_tag_list_check_params(count, cursor)
        response = requests.get(get_url, headers=headers, params=params)
        response.raise_for_status()
        return response

class Calendar():
    def __init__(self, naverworks_app_name, username):
        self.naverworks_app_name = naverworks_app_name
        self.username = username
        self.__access_token = None
        self.userId = None
        self.initialize()

    def initialize(self):
        try:
            self.__access_token = Tool().get_stored_access_token(self.naverworks_app_name)
            self.userId = Tool().get_user(self.naverworks_app_name, self.username).get('userId')
        except Exception as err:
            raise Exception("Calendar initialization error") from err
        
    def __str__(self):
        return "This is the class for NaverWorks Calendar"

    def __make_personal_calendar_list_check_params(self, **kwargs):
        try:
            params = {
                "count": kwargs.get('count'),
                "cursor": kwargs.get('cursor'),
            }
            return params
        except KeyError as err:
            raise Exception("Missing required keys in personal calendar list check") from err

    # (캘린더) 개인 속성 목록 조회
    def personal_calendar_list_check(self, **kwargs):
        try:
            self.initialize()

            get_url = CALENDAR_URL["Calendar"]["PersonalListCheck"].format(self.userId)
            headers = {
                'Authorization': 'Bearer {}'.format(self.__access_token)
            }
            params = self.__make_personal_calendar_list_check_params(**kwargs)
            response = requests.get(get_url, headers=headers, params=params)
            response.raise_for_status()
            return response
        except Exception as err:
            raise Exception("Failed to check calendar personal list") from err

    def __make_create_calendar_event_params(self, summary, start, **kwargs):
        try:
            params = {
                "eventComponents": [
                    {
                        "summary": summary,
                        "start": {
                            "dateTime": start,
                            "timeZone": "Asia/Seoul"
                        }
                    }
                ]
            }
            return params
        except KeyError as err:
            raise Exception("Missing required keys in personal calendar event create") from err

    # (일정) 생성
    def create_calendar_events(self, calendar_name: str, summary: str, start: datetime, **kwargs):
        try:
            self.initialize()

            calendarId = Tool.get_calendar(self.naverworks_app_name, self.username, calendar_name).get('calendarId')
            post_url = CALENDAR_URL['Event']['Create'].format(self.userId, calendarId)
            headers = {
                'Authorization': 'Bearer {}'.format(self.__access_token),
                'Content-Type': 'application/json'
            }
            params = self.__make_create_calendar_event_params(summary, start.strftime("%Y-%m-%dT%H:%M:%S"), **kwargs)
            response = requests.post(post_url, headers=headers, json=params)
            return response
        except Exception as err:
            raise Exception("Failed to create events on calendar({})".format(calendar_name)) from err
        
    def __make_check_calendar_events_list_params(self, fromDateTime, untilDateTime):
        try:
            params = {
                "fromDateTime": fromDateTime + '%2B09:00',
                "untilDateTime": untilDateTime + '%2B09:00',
            }
            return params
        except KeyError as err:
            raise Exception("Missing required keys in personal calendar event list check") from err


    # (일정) 조회
    def check_calendar_event_list(self, calendar_name: str, fromDateTime: datetime, untilDateTime: datetime):
        try:
            self.initialize()

            calendarId = Tool.get_calendar(self.naverworks_app_name, self.username, calendar_name).get('calendarId')
            get_url = CALENDAR_URL['Event']['ListCheck'].format(self.userId, calendarId)
            headers = {
                'Authorization': 'Bearer {}'.format(self.__access_token)
            }
            params = self.__make_check_calendar_events_list_params(fromDateTime.strftime("%Y-%m-%dT%H:%M:%S"), untilDateTime.strftime("%Y-%m-%dT%H:%M:%S"))

            response = requests.get(get_url, headers=headers, params=params)
            response.raise_for_status()
            return response
        except Exception as err:
            raise Exception("Failed to check the list of events on calendar({})".format(calendar_name))

# 드라이브 - 그룹/팀      
class GroupAndTeamDrive():
    def __init__(self, naverworks_app_name, groupName):
        self.naverworks_app_name = naverworks_app_name
        self.groupName = groupName
        self.__access_token = None
        self.initialize()

    def initialize(self):
        try:
            self.__access_token = Tool().get_stored_access_token(self.naverworks_app_name)
            self.groupId = Tool.get_group(naverworks_app_name=self.naverworks_app_name, korean_name=self.groupName).get('groupId')
        except Exception as err:
            raise Exception("Calendar initialization error") from err
        
    def __str__(self):
        return "This is the class for NaverWorks Group And Team Drive"
    
    def __make_check_file_list_params(self, orderBy, count, cursor):
        try:
            params = {
                "orderBy": orderBy,
                "count": count,
                "cursor": cursor,
            }
            return params
        except KeyError as err:
            raise Exception("Missing required keys in check file list") from err

    def check_file_list(self, fileId:str = None, orderBy:str = None, count:int = None, cursor:str = None, is_root:bool = True):
        try:
            self.initialize()
            headers = {
                'Authorization': 'Bearer {}'.format(self.__access_token)
            }
            if is_root:
                get_url = DRIVE_URL['GroupAndTeam']['File']['RootFileListCheck'].format(self.groupId)
            else:
                get_url = DRIVE_URL['GroupAndTeam']['File']['FileListCheck'].format(self.groupId, fileId)

            params = self.__make_check_file_list_params(orderBy, count, cursor)
            response = requests.get(get_url, headers=headers, params=params)
            response.raise_for_status()
            return response
        except Exception as err:
            raise Exception("Failed to check the file list in this directory") from err

    def get_download_file_url(self, fileId:str):
        try:
            self.initialize()
            headers = {
                'Authorization': 'Bearer {}'.format(self.__access_token)
            }
            get_url = DRIVE_URL['GroupAndTeam']['File']['FileDownload'].format(self.groupId, fileId)
            response = requests.get(get_url, headers=headers, allow_redirects=False)
            response.raise_for_status()
            return response
        except Exception as err:
            raise Exception("Failed to get the file download") from err

    def download(self, fileId:str):
        try:
            response = self.get_download_file_url(fileId=fileId)
            url = response.headers.get('Location')
            fileData = Note.file_download(url=url, access_token=self.__access_token)
            return fileData
        except Exception as err:
            raise Exception("Failed to download file") from err

    def __make_upload_file_params(self, fileName, modifiedTime, fileSize, overwrite):
        try:
            params = {
                "fileName": fileName,
                "modifiedTime": modifiedTime,
                "fileSize": fileSize,
                "overwrite": overwrite,
            }
            return params
        except KeyError as err:
            raise Exception("Missing required keys in upload_file") from err

    def get_upload_file_url(self, fileName:str, fileSize:int, fileId:str = None, modifiedTime:str = None, overwrite:bool = False, is_root:bool = True):
        try:
            self.initialize()
            headers = {
                'Authorization': 'Bearer {}'.format(self.__access_token),
                'Content-Type': 'application/json'
            }

            if is_root:
                post_url = DRIVE_URL['GroupAndTeam']['File']['RootFileUpload'].format(self.groupId)
            else:
                post_url = DRIVE_URL['GroupAndTeam']['File']['FileUpload'].format(self.groupId, fileId)

            body = self.__make_upload_file_params(fileName, modifiedTime, fileSize, overwrite)

            response = requests.post(post_url, headers=headers, json=body)

            return response
        except Exception as err:
            raise Exception("Failed to create file upload url") from err

    def upload(self, fileName:str, fileSize:int, fileData, fileId:str = None, modifiedTime:str = None, overwrite:bool = False, is_root:bool = True):
        try:
            response = self.get_upload_file_url(
                fileName=fileName,
                fileSize=fileSize,
                fileId=fileId,
                modifiedTime=modifiedTime,
                overwrite=overwrite,
                is_root=is_root,
            )
            url = response.json().get("uploadUrl")

            response = Note.file_upload(
                url=url,
                access_token=self.__access_token,
                fileData=fileData,
            )
            return response
        except Exception as err:
            raise Exception("Failed to upload file") from err

    def create_folder(self, folderName:str, folderId:str = None, is_root:bool = True):
        try:
            self.initialize()
            headers = {
                'Authorization': 'Bearer {}'.format(self.__access_token),
                'Content-Type': 'application/json'
            }

            if is_root:
                post_url = DRIVE_URL['GroupAndTeam']['Folder']['RootCreate'].format(self.groupId)
            else:
                post_url = DRIVE_URL['GroupAndTeam']['Folder']['Create'].format(self.groupId, folderId)

            body = {
                'fileName': folderName
            }

            response = requests.port(post_url, headers=headers, json=body)
            return response
        except Exception as err:
            raise Exception("Failed to create folder") from err

class Mail():
    pass

