# Naverworks Platform - 네이버웍스 기반 업무 관리 플랫폼
네이버웍스 기반 업무 관리 플랫폼은 NaverWorks에서 제공하는 API를 사용하여 일부 업무를 자동화하도록 개발하였습니다.

 [NAVERWORKS API Document 바로가기](https://developers.worksmobile.com/kr/docs/introduction?lang=ko)

## 0.목차

1. [사용 환경](#1사용-환경)
2. [작동원리](#2작동원리)
3. [제어커맨드](#3제어커맨드)
4. [실행중인 앱](#4실행중인-앱)

<br>

## 1.사용 환경
이 프로그램은 반드시 ![Python 3 or higher](https://img.shields.io/badge/python-3+-blue.svg) 이상의 버전으로 실행 바랍니다.

**운영위치**
```plaintext
CMEFND:/mdfsvc/NaverWorks/
```
<br>

## 2.작동원리
Daemon 프로그램이 [앱](#4실행중인-앱)의 실행, 종료를 관리하며, [제어커맨드](#3제어커맨드)를 통해 [앱](#4실행중인-앱)의 실행을 제어할 수 있다.

<br>

## 3.제어커맨드
### 3.1.커맨드 사용법

```plaintext
usage: python3 manage.py [-h] command ...

Management script of the program based on the NaverWorks

options:
  -h, --help    show this help message and exit

commands:
  runserver       Execute the main server (run in the background)

  run             Query the running signal to the main server

  runcheck        Check what process is running now

  killall         Send the exit signal to the main server

  createapp       Create a new app
                  Required argument:
                  - app_name: Name of the app to create

  authcodeurl     Print the authorization code URL for a Naverworks app
                  Required argument:
                  - app_name: Name of the Naverworks app

  refreshtoken    Get a refresh token
                  Required argument:
                  - app_name: Name of the Naverworks app

  holiday         Processing the holiday database
                  Actions:
                  - crud: Perform CRUD operations on holidays
                  - loaddata: Load data from a file
                    Required argument:
                    - filename: Name of the file to load
                  - calendarupdate: Update holiday on Naverworks calendar
```
### 3.2 커맨드 설명
#### - runserver
```plaintext
데몬 서버를 실행할 때 사용한다.
```
#### - run
```plaintext
settings.py 내의 'INSTALLED_APPS' 에 변경사항을 감지하여 변경된 내역이 있는 앱만 재시작한다.
```
#### - runcheck
```plaintext
현재 실행되고 있는 앱들의 Running State, Process Id 를 보여준다

예시)
╒════════════════════════════╤═════════╤═══════╕
│ app_name                   │ state   │   pid │
╞════════════════════════════╪═════════╪═══════╡
│ holiday_alerter            │ Running │ 22506 │
├────────────────────────────┼─────────┼───────┤
│ holiday_checker            │ Running │ 22507 │
├────────────────────────────┼─────────┼───────┤
│ market_alert               │ Running │ 22508 │
├────────────────────────────┼─────────┼───────┤
│ network_checker            │ Running │ 14197 │
├────────────────────────────┼─────────┼───────┤
│ occ_checker                │ Running │ 14851 │
├────────────────────────────┼─────────┼───────┤
│ token_refresher            │ Running │ 11709 │
├────────────────────────────┼─────────┼───────┤
│ auto_weekly_report_creater │ Running │  1956 │
├────────────────────────────┼─────────┼───────┤
│ kakao_client_updater       │ Running │ 20332 │
╘════════════════════════════╧═════════╧═══════╛
```
#### - killall
```plaintext
실행되고있는 모든 앱을 종료시킨다.
```
#### - createapp [APP_NAME]
```plaintext
신규 앱 추가 시 createapp으로 기본 개발 환경을 세팅한다.
```
#### - authcodeurl [NAVERWORKS_APP_NAME]
```plaintext
네이버웍스 앱 추가 시 authcode를 발급받기 위한 authcode URL 정보를 반환한다.
```
#### - refreshtoken [NAVERWORKS_APP_NAME]
```plaintext
발급받은 authcode로 refreshtoken을 발급받는다. 해당 토큰으로 access token 을 갱신한다.
```
#### - holiday <crud | loaddata | calendar_update>
```plaintext
거래소 휴장일 관련 커맨드

[인자 설명]
- crud : 휴장일을 수동으로 Create, Read, Update, Delete 한다
- loaddata [filename] : 파일에 저장되어있는 휴장일 정보를 일괄적으로 DB에 저장한다.
- calendar_update : DB에 저장된 휴장일 정보를 네이버웍스 캘린더에 업데이트한다.
```

<br>

## 4.실행중인 앱
### - auto_weekly_report_creater
```plaintext
매주 목요일 주간보고서 양식 업데이트
```
### - holiday_alerter
```plaintext
당일의 휴장 정보를 네이버웍스 메신저로 알림
```
### - holiday_checker
```plaintext
매주 휴장일 관련 정보를 **Abstract API, exchange_calendars 파이썬 라이브러리를 통해 업데이트함
```
[**Abstract API 바로가기**](https://app.abstractapi.com/api/holidays/pricing)

### - kakao_client_updater
```plaintext
NaverWorks 주소록과 카카오 채널 친구그룹을 동기화한다
```
### - market_alert
```plaintext
각 CON서버에서 실행되고있는 fepmsg를 통해 발생되는 Alert를 수신하여 네이버웍스 메신저로 전달한다
```
### - network_checker
```plaintext
당사 네트워크 장비(Cisco Switch, Router)의 status를 모니터링하여 이상이 감지될 경우 네이버웍스 메신저로 전달한다
```
### - occ_checker
```plaintext
OCC에서 새로운 공지가 발생할 경우, 메신저로 해당 공지내용과 파일 URL을 전달한다
```
### - token_refresher
```plaintext
Refresh Token을 가지고 Access Token을 매일 갱신한다.
```

