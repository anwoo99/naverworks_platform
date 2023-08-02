from auto_weekly_report_creater.config import *

def get_week(date):
    firstDate = date.replace(day = 1)
    
    while firstDate.weekday() != 6:
        firstDate += dt.timedelta(days=1)
    
    if date < firstDate:
        week = 1
    else:
        week = ((date - firstDate).days // 7 + 2)
    
    return week

def get_path_list(date, file):
    year = str(date.year)
    return [REPORT_DIR, year, file]

def get_report_name(date):
    year = date.year
    month = str(date.month).zfill(2)
    week = get_week(date)
    return REPORT_FILE.format(year, month, week)

def make_this_week_report(date, location):
    try:
        report_date = date + dt.timedelta(days=4)
        step = 0
        workbook = openpyxl.load_workbook(location)
        workSheet = workbook[SHEET_NAME]
        B_index = 2
        C_index = 3

        for row in workSheet.iter_rows():
            row_values = list(row)

            for cell in row_values:
                if cell.value is None:
                    continue

                temp_font = copy.copy(cell.font)

                if step == 0: # 주간 업무 보고---
                    if '주간 업무 보고' in cell.value:
                        cell.value = '주간 업무 보고({}년 {}월 {}주)'.format(date.year, date.month, get_week(date))
                        cell.font = copy.copy(temp_font)
                        step = 1
                        continue
                if step == 1: # '보고일' 까지 이동
                    if '보고일' in cell.value:
                        step = 2
                        continue
                if step == 2: # 보고일--
                    cell.value = '{}월 {}일'.format(report_date.month, report_date.day)
                    cell.font = copy.copy(temp_font)
                    step = 3
                    continue
                if step == 3: # 업무:'해외시세' 까지 이동
                    if cell.value == '해외시세':
                        step = 4
                    continue
                if step == 4: # 직원별 전주업무, 금주업무 초기화
                    cell.fill = PatternFill(fill_type=None)
                    if cell.column == B_index:
                        cell.value = None
                    elif cell.column == C_index:
                        row_values[B_index - 1].value = cell.value
                        cell.value = None
                    elif cell.value == "비고":
                        step = 5
                        continue
                    else:
                        continue
                if step == 5: # '비고'란 삭제
                    cell.value = None
                    continue
            row = tuple(row_values)     
        workbook.save(location)
    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()

def auto_create():
    try:
        curr = datetime.now()
        last = curr - dt.timedelta(days=7)

        c_file = get_report_name(curr)
        l_file = get_report_name(last)
        c_path = get_path_list(curr, c_file)
        l_path = get_path_list(last, l_file)
        c_save_location = os.path.join(WEEKLY_REPORT_DIR, c_file)

        # 현재 만들려는 파일이 이미 있는 경우 프로그램 종료
        c_file_info = Tool.get_group_file(
            naverworks_app_name=NAVERWORKS_APP_NAME, 
            groupName=NAVERWORKS_GROUP_NAME, 
            pathList=c_path,
        )
        if c_file_info:
            log(APP_NAME, MUST, "There has been already this file({}) in this path({})".format(c_file, c_path))
            return
        
        # 지난 주 파일 다운로드
        l_fileData = Tool.download_group_file(
            naverworks_app_name=NAVERWORKS_APP_NAME,
            groupName=NAVERWORKS_GROUP_NAME,
            pathList=l_path,
        )

        # 지난 주 파일 내용 현재 파일로 복사
        with open(c_save_location, "wb+") as fd:
            fd.write(l_fileData)

        # 이번 주 파일 생성
        make_this_week_report(curr, c_save_location)
        
        # 네이버웍스 드라이브에 업로드
        response = Tool.upload_group_file(
            naverworks_app_name=NAVERWORKS_APP_NAME,
            groupName=NAVERWORKS_GROUP_NAME,
            file_location=c_save_location,
            pathList=c_path[0:-1],
            is_root=False
        )
    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()

def main():
    try:
        if len(sys.argv) >= 2 and sys.argv[1] == '-f':
            auto_create()
            sys.exit()
        
        schedule.every().thursday.at(CREATE_TIME).do(auto_create)

        log(APP_NAME, MUST, "This program create the weekly report every {} on Thursday..".format(CREATE_TIME))

        while True:
            log(APP_NAME, DEBUG, "Run this program..!")
            schedule.run_pending()
            log(APP_NAME, DEBUG, "Sleep for {} seconds.. (wake up every {} on Sunday)".format(SLEEP_TIME, CREATE_TIME))

            time.sleep(SLEEP_TIME)

    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()

if __name__ == "__main__":
    main()