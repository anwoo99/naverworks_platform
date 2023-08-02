import requests

url = "https://kapi.kakao.com/v1/talkchannel/create/target_user_file"
headers = {
            "Authorization": "KakaoAK 34b0d17f5994bb0b93d1d15ff3718b65",
            "Content-Type": "application/json"
}
params = {
    "channel_public_id": "_NaezG",
    "file_name": "해외데이터팀_고객리스트",
    "schema": {
        "이름": "string",
        "회사명": "number",
        "목동발송클래스":"number",
        "상암발송클래스":"number"
    }
}

res = requests.post(url=url, headers=headers, json=params)

print(res)