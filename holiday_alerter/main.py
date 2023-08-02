from holiday_alerter.config import *

def get_exchange_class_list():
    try:
        exchange_class_list = []

        for exchange in EXCHANGE_MAP:
            exch_class = exchange.get("class")
            
            if exch_class not in exchange_class_list:
                exchange_class_list.append(exch_class)

        return exchange_class_list
    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()

def holiday_alerter():
    try:
        log(APP_NAME, MUST, "Holiday_alerter is running now..")

        now = datetime.now()
        weekday = (now.weekday() + 1) % 7

        if weekday == 0 or weekday == 6:
            return

        exchange_class_list = get_exchange_class_list()

        for exchange in EXCHANGE_MAP:
            exch_name = exchange.get('name')
            exch_class = exchange.get('class')
            filename = "{}/{}-{}.txt".format(HOLIDAY_DIR, exch_name, weekday)

            with open(filename, "r") as fd:
                output = fd.read()

                if output and exch_class in exchange_class_list:
                    alert = "금일 {} 거래소 휴장일({}) 입니다.".format(exch_class, output)

                    try:    
                        Tool.send_alert_text_message_to_bot(NAVERWORKS_APP_NAME, NAVERWORKS_BOT_ID, NAVERWORKS_CHANNEL_ID, alert, 'holiday_alert')
                    except Exception as err:
                        traceback_error = traceback.format_exc()
                        log(APP_NAME, ERROR, traceback_error)
                    finally:
                        exchange_class_list.remove(exch_class)

    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()

def main():
    try:
        alert_time = APP_INFO['alert_time']
        schedule.every().day.at(alert_time).do(holiday_alerter)

        log(APP_NAME, MUST, "This program alerts the holiday of exchanges every {}".format(alert_time))
        
        while True:
            log(APP_NAME, DEBUG, "Running this program..!")
            schedule.run_pending()
            log(APP_NAME, DEBUG, "Sleeping for {} seconds.. (waking up every {})".format(SLEEP_TIME, alert_time))
            
            time.sleep(SLEEP_TIME)

    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()

if __name__ == "__main__":
    main()
