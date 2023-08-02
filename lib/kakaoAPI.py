from lib.config import *

class Channel():
    def __init__(self, rest_api_key=None, channel_public_id=None):
        self.rest_api_key = rest_api_key
        self.channel_public_id = channel_public_id

    def __str__(self):
        return "This is the class for Kakao Channel API"

    def check_cient_files(self):
        try:
            url = KAKAO_CHANNEL_URL["CheckClient"]
            headers = {
                "Authorization": "KakaoAK {}".format(self.rest_api_key)
            }
            params = {
                "channel_public_id": self.channel_public_id
            }
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()  # Parse the JSON response and return it
        except requests.exceptions.HTTPError as err:
            raise Exception("Failed to get client contact file: {}".format(err)) from err

    def add_client(self, fileId, users: list, user_type="phone"):
        try:
            url = KAKAO_CHANNEL_URL["AddClient"]
            headers = {
                "Authorization": "KakaoAK {}".format(self.rest_api_key),
                "Content-Type": "application/json"
            }
            params = {
                "file_id": fileId,
                "channel_public_id": self.channel_public_id,
                "user_type": user_type,
                "users": users
            }
            response = requests.post(url, headers=headers, json=params)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as err:
            raise Exception("Failed to add client to contact file({}): {}".format(fileId, err)) from err

    def delete_client(self, fileId, user_ids: list, user_type="phone"):
        try:
            url = KAKAO_CHANNEL_URL["DeleteClient"]
            headers = {
                "Authorization": "KakaoAK {}".format(self.rest_api_key),
                "Content-Type": "application/json"
            }
            params = {
                "file_id": fileId,
                "channel_public_id": self.channel_public_id,
                "user_type": user_type,
                "user_ids": user_ids
            }
            response = requests.post(url, headers=headers, json=params)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as err:
            raise Exception("Failed to delete client from contact file({}): {}".format(fileId, err)) from err
