from kakao_client_updater.config import *



def client_to_kakao(client_contact_list):
    try:
        kakao_object_list = []
        tag_map = Tool.get_all_contact_tag_map(
            naverworks_app_name=NAVERWORKS_APP_NAME
        )

        for client_contact in client_contact_list:
            kakao_object = copy.deepcopy(KAKAO_CONTACT_TEMPLATE)
            
            # Phone
            telephones = client_contact.get("telephones")

            for telephone in telephones:
                if telephone["type"] == "CELLPHONE" and len(telephone["telephone"]) > 0:
                    kakao_object["id"] = telephone["telephone"]
                    break
            
            if not kakao_object["id"]:
                continue

            # Name
            contactName = client_contact.get("contactName")
            fullname = contactName['lastName'] + contactName['firstName']
            if not fullname.strip():
                continue
            kakao_object['field']['이름'] = fullname.strip()
    
            
            # 태그 아이디 <-> 태그 명 매핑 정보 가져오기
            contactTagIds = client_contact.get("contactTagIds")

            for contactTagId in contactTagIds:
                tag_name = tag_map[contactTagId]

                if not tag_name:
                    continue

                # Company
                if tag_name in COMPANY_CLASS.keys():
                    kakao_object['field']["회사명"] = COMPANY_CLASS[tag_name]
                    continue

                # Mokdong
                if tag_name in MOKDONG_CLASS.keys():
                    kakao_object['field']["목동발송클래스"] = MOKDONG_CLASS[tag_name]
                    continue

                # SangArm
                if tag_name in SANGARM_CLASS.keys():
                    kakao_object['field']["상암발송클래스"] = SANGARM_CLASS[tag_name]
                    continue
            
            kakao_object_list.append(kakao_object)
        return kakao_object_list
    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()

def team_to_kakao(our_team_list):
    try:
        kakao_object_list = []

        for our_team in our_team_list:
            kakao_object = copy.deepcopy(KAKAO_CONTACT_TEMPLATE)

            # Phone
            cellphone = our_team.get("cellPhone")

            if cellphone is None:
                continue

            kakao_object["id"] = cellphone

            # Name
            userName = our_team.get("userName")
            fullname = userName['lastName'] + userName['firstName']
            if not fullname.strip():
                continue
            
            kakao_object['field']['이름'] = fullname.strip()

            # 구분 클래스 (Adjust the company_name as needed)
            company_name = "코라이즈테크놀로지"

            # Set the appropriate class based on the company_name
            kakao_object['field']["회사명"] = COMPANY_CLASS[company_name]
            kakao_object['field']["목동발송클래스"] = MOKDONG_CLASS[company_name]
            kakao_object['field']["상암발송클래스"] = SANGARM_CLASS[company_name]
            
            kakao_object_list.append(kakao_object)
        return kakao_object_list
    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()

def get_stored_kakao_contact_list():
    try:
        result = []
        with open(KAKAO_CONTACT_LIST_FILENAME, "r+") as fd:
            # Load the JSON data if the file exists and has content
            result = json.load(fd)

        return result
    except FileNotFoundError:
        # If the file is not found, return an empty list
        return []
    except json.JSONDecodeError:
        # If the file exists but is empty or has invalid JSON content, return an empty list
        return []
    except Exception as err:
        # For any other unexpected errors, log the error and return an empty list
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        return []

def save_stored_kakao_contact_list(kakao_contact_list):
    try:
        with open(KAKAO_CONTACT_LIST_FILENAME, "w+", encoding='utf-8') as fd:
            json.dump(kakao_contact_list, fd, indent=4, ensure_ascii=False)
    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()


def update_kakao_contact(kakao_contact_list):
    try:
        saved_kakao_contact_list = get_stored_kakao_contact_list()

        file_id = None
        delete_list = []

        channel = Channel(
            rest_api_key=KAKAO_APP_REST_API,
            channel_public_id=KAKAO_CHANNEL_PROFILE_ID
        )

        # 파일 아이디 얻어오기
        res = channel.check_cient_files()
        results = res.get("results")

        for result in results:
            if result.get("file_name") == KAKAO_CLIENT_FILENAME:
                file_id = result.get("file_id")
                break

        if file_id is None:
            raise Exception("There is no {} file".format(KAKAO_CLIENT_FILENAME))

        # 파일 비교(삭제할 파일 찾기)
        for saved_kakao_contact in saved_kakao_contact_list:
            if saved_kakao_contact not in kakao_contact_list:
                delete_list.append(saved_kakao_contact.get("id"))

        # 고객 삭제
        res = channel.delete_client(
            fileId=file_id,
            user_ids=delete_list,
        )
        log(APP_NAME, MUST, res)

        # 고객 업데이트
        res = channel.add_client(
            fileId=file_id,
            users=kakao_contact_list,
        )
        log(APP_NAME, MUST, res.json())

        save_stored_kakao_contact_list(kakao_contact_list)
    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()

def main():
    try:
        while True:
            kakao_contact_list = []

            # 네이버웍스에서 특정 태그에 속해있는 고객사 주소록 가져오기
            client_contact_list = Tool.get_contact_in_tags(
                naverworks_app_name=NAVERWORKS_APP_NAME,
                tag_name_list=COMPANY_TAG_LIST,
                phone_number_check=True
            )
            
            # 네이버웍스 고객사 주소 json => 카카오 포맷
            kakao_clients = client_to_kakao(client_contact_list)

            # 네이버웍스에서 해외데이터팀 리스트 정보 가져오기
            our_team_list = Tool.get_user_list(
                naverworks_app_name=NAVERWORKS_APP_NAME,
                korean_name_list=OUR_TEAM_LIST
            )

            # 네이버웍스 해외데이터팀 리스트 정보 json => 카카오 포맷
            kakao_our_team = team_to_kakao(our_team_list)
            
            kakao_contact_list = kakao_clients + kakao_our_team

            update_kakao_contact(kakao_contact_list)

            time.sleep(SLEEP_TIME)
    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()

if __name__ == "__main__":
    main()
