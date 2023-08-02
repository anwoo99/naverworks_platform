from occ_checker.config import *

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

def parsing_output(output):
    try:
        symbol_list = []
        symb_index = None
        
        for o_line in output[1:-1]:
            if o_line.startswith(('#', '*', '/', '\0')):
                continue
            elif o_line.startswith('='):
                header_list = o_line[1:].split(',')

                for index, header in enumerate(header_list):
                    if header.strip() == 'Symbol':
                        symb_index = index

                if symb_index is None:
                    raise Exception("There is no 'Symbol' header")
            else:
                if symb_index is None:
                    raise Exception("There is no 'Symbol' header")
                
                symb_info = o_line.split(',')
                
                if len(symb_info) < symb_index + 1:
                    continue

                symbol = symb_info[symb_index].strip()
                symbol_list.append(symbol)

        return symbol_list
    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()

def save_symbol_list(symbol_list):
    with open(SYMBOL_FILE, "w+") as fd:
        for ii, symbol in enumerate(symbol_list):
            fd.write("{}.{}\n".format(ii + 1, symbol))

def get_symbol_list(exchange):
    try:
        session = None
        remote = get_remote_server_info(BASE_SERVER)
        session = telnet(
            session, 
            remote['hostname'], 
            remote['id'], 
            remote['pw'], 
            remote['login_display'], 
            remote['password_display'], 
            remote['first_display']
        )

        if session is None:
            log(APP_NAME, ERROR, "Cannot access to {}".format(remote['hostname']))
            return None
        
        command = SYMBOL_GET_COMMAND.format(exchange)
        session, output = cmd_to_remote(
            session=session, 
            command=command, 
            expected_display=remote['first_display'], 
            is_output=True
        )
        session.close()

        symbol_list = parsing_output(output.split('\n'))

        save_symbol_list(symbol_list)

        return symbol_list
    except Exception as err:
        if session is not None:
            session.close()

        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()

def get_last_notice():
    try:
        with open(NOTI_FILE) as fd:
            last_notice = json.load(fd)
    except Exception:
        last_notice = []

    return last_notice

def save_new_notice(new_notice):
    with open(NOTI_FILE, "w+") as fd:
        json.dump(new_notice, fd, indent=4)

def get_new_notice():
    try:
        new_notice = []
        response = requests.get(OCC_URL)
        soup = bs(response.text, "html.parser")
        table = soup.select_one(
            "#post > div > main > div > div > div.col-12.col-lg-8.col-xl-9 > section > div.searchResults > div.mainSearchResults"
        )
        rows = table.find_all("div", {"class": "memoContent"})

        for row in rows:
            datas = row.find_all("div", {"class": "informationMemo-Column"})
            notice = {
                'number': datas[0].text,
                'date': datas[1].text,
                'effective_date': datas[2].text,
                'title': datas[3].find("a").text,
            }
            new_notice.append(notice)

        return new_notice
    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()

def notice_checker(last_notice, new_notice, symbol_list):
    try:
        symbol_index_string = "Symbol:"

        for new in new_notice:
            if new not in last_notice:
                new_title = new['title']

                if symbol_index_string in new_title:
                    symbol_start_index = new_title.index(symbol_index_string) + len(symbol_index_string)
                    symbol_in_title = new_title[symbol_start_index:].strip().split()[0].strip()

                    if symbol_in_title in symbol_list:
                        date = "1) 등록일자 : {}\n".format(new['date'])
                        effective_date = "2) 적용일자 : {}\n".format(new['effective_date'] or "Unknown")
                        target = "3) 해당품목 : {}\n".format(symbol_in_title)
                        title = "4) 공지내용 : {}".format(new_title)
                        content = date + effective_date + target + title
                        link = EACH_NOTICE_URL.format(new["number"])

                        try:
                            log(APP_NAME, MUST, "New notification update!")
                            Tool.send_alert_link_message_to_bot(
                                NAVERWORKS_APP_NAME,
                                NAVERWORKS_BOT_ID, 
                                NAVERWORKS_CAHNNEL_ID, 
                                link,
                                content,
                                "occ_notice_alert"
                            )
                            time.sleep(5)
                        except Exception as err:
                            log(APP_NAME, ERROR, err)
                            
    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()

def main():
    log(APP_NAME, MUST, "OCC Checker start..!")
    # save_new_notice([])

    while True:
        log(APP_NAME, MUST, "Check the notifications of occ now..")
        symbol_list = get_symbol_list("OPRA")

        if symbol_list is None:
            time.sleep(SLEEP_TIME)
            continue

        last_notice = get_last_notice()
        new_notice = get_new_notice()

        notice_checker(last_notice, new_notice, symbol_list)
        
        save_new_notice(new_notice)
        
        log(APP_NAME, MUST, "Finished to check the notifications of occ now. Sleep for {} seconds..".format(SLEEP_TIME))
        time.sleep(SLEEP_TIME)

if __name__ == "__main__":
    main()