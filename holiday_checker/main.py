from holiday_checker.config import *
    
def get_iso_code_list():
    try:
        iso_code_list = set(exchange['iso_code'] for exchange in EXCHANGE_MAP)
        return list(iso_code_list)
    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()

def get_country_code_list():
    try:
        country_code_list = set(exchange['country_code'] for exchange in EXCHANGE_MAP)
        return list(country_code_list)
    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()

def get_exch_class_list():
    try:
        exch_class_list = set(exchange['class'] for exchange in EXCHANGE_MAP)
        return list(exch_class_list)
    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()

def get_holiday_from_iso_code(iso_code, date):
    try:
        holiday_dict = copy.deepcopy(ISO_HOLIDAY_DICT)
        holiday_dict['date'] = date
        holiday_dict['iso_code'] = iso_code
        exchange = xcals.get_calendar(iso_code)
        holiday_dict['is_session'] = exchange.is_session(date.date())
    except Exception as err:
        holiday_dict['is_session'] = True
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
    finally:
        return holiday_dict

def get_holiday_from_country_code(country_code, date):
    try:
        holiday_dict = copy.deepcopy(COUNTRY_HOLIDAY_DICT)
        holiday_dict['date'] = date
        holiday_dict['country_code'] = country_code
        holiday_dict['holiday_name'] = ""

        holiday = Holiday(APP_INFO['abstract_api_key'])

        log(APP_NAME, "DEBUG", "country code({}) | Abstract API is running now..({})".format(country_code, date.date()))
        
        try:
            if not TEST:
                holiday_infos = holiday.get_holiday_info(country_code, date.year, date.month, date.day)
                for holiday_info in holiday_infos:
                    if holiday_info["type"] == APP_INFO['holiday_type']:
                        holiday_dict['holiday_name'] = holiday_info["name"]
                        log(APP_NAME, PROGRESS, "country code({}) | Abstract API return date({}) holiday({})".format(country_code, date.date(), holiday_info["name"]))
        except Exception as err:
            log(APP_NAME, ERROR, err)
        finally:
            log(APP_NAME, "DEBUG", "country code({}) | Abstract API is done.({})".format(country_code, date.date()))
            return holiday_dict      
    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()

def get_holiday_from_database(exch_class, date):
    try:
        db = DataBase(
            host=DATABASE['host'],
            username=DATABASE['username'],
            password=DATABASE['password'],
            db_name=DATABASE['name'],
        )
        db.connect()
        where = "exchange = '{}' AND date = '{}'".format(exch_class, date.strftime("%Y-%m-%d"))
        
        holidays = db.read(table=DATABASE['table'], where=where)
        
        if len(holidays) <= 0:
            return None
        else:
            return holidays[0]

    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()

def save_holiday(date, holiday_list1, holiday_list2, holiday_list3, exchange_map):
    try:
        weekday = (date.weekday() + 1) % 7
        mode = "w+"

        for exchange in exchange_map:
            holiday_info_dict = copy.deepcopy(HOLIDAY_DICT)
            holiday_info_dict['date'] = date.strftime('%Y-%m-%d %H:%M:%S')
            holiday_info_dict['name'] = ""
            holiday_name = ""
            enrolled = False

            exch_name = exchange['name']
            iso_code = exchange['iso_code']
            country_code = exchange['country_code']
            exch_class = exchange['class']

            filename = "{}/{}-{}.txt".format(HOLIDAY_DIR, exch_name, weekday)

            with open(filename, mode) as fd:
                for holiday_dict in holiday_list1:
                    if iso_code == holiday_dict['iso_code']:
                        if holiday_dict['is_session'] == False:
                            if weekday == 0 or weekday == 6:
                                holiday_name = "Weekends"
                            else:
                                holiday_name = "Unknown Holiday"
                                enrolled = True
                for holiday_dict in holiday_list2:
                    if country_code == holiday_dict['country_code']:
                        if len(holiday_dict['holiday_name']) > 0:
                            holiday_name = holiday_dict['holiday_name']
                            enrolled = True
                for holiday_dict in holiday_list3:
                    if exch_class == holiday_dict['exchange']:
                        if len(holiday_dict['name']) > 0:
                            holiday_name = holiday_dict['name']
                            enrolled = True

                if enrolled:
                    fd.write(holiday_name)
                    holiday_info_dict['name'] = holiday_name
            exchange['holiday'].append(holiday_info_dict)
    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()

def update_naverworks_calendar(exchange_map):
    try:
        naverworks_app_name = APP_INFO['naverworks_app_name']
        user_name = APP_INFO['user_name']
        calendar_name = APP_INFO['calendar_name']
        exchange_class_list = []

        for exchange in exchange_map:
            exchange_class = exchange['class']

            if exchange_class not in exchange_class_list:
                exchange_class_list.append(exchange_class)
                
                holidays = exchange['holiday']

                for holiday in holidays:
                    name = holiday.get('name')
                    date = datetime.strptime(holiday.get('date'), '%Y-%m-%d %H:%M:%S')
                    
                    if name and name != "Weekends":
                        log(APP_NAME, PROGRESS, "Class({}) Date({}) Event({}) is being created now on calendar({})..".format(exchange_class, date, name, calendar_name))
                        summary = "{} 휴장일({})".format(exchange_class, name)

                        try:
                            response = Tool().create_unique_calendar_event(naverworks_app_name, user_name, calendar_name, summary, date)
                            
                            if isinstance(response, str):
                                log(APP_NAME, PROGRESS, "Response: {}".format(response))
                            else:
                                log(APP_NAME, PROGRESS, "Response: {}".format(response.json()))
                        except Exception as err:
                            traceback_error = traceback.format_exc()
                            log(APP_NAME, ERROR, traceback_error)
                    
                    time.sleep(5)
                
    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()

def write_exchange_map(exchange_map):
    try:
        filename = "{}/exchange_map.txt".format(HOLIDAY_DIR)
        mode = "w+"
        with open(filename, mode) as fd:
            json.dump(exchange_map, fd, indent=4)
        
    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()

def copy_holidays_to_remote():
    try:
        for server in REMOTE_SERVER_INFO:
            if server['holiday_check']:
                file_list = os.listdir(HOLIDAY_DIR)
                
                for file in file_list:
                    source_path = os.path.join(HOLIDAY_DIR, file)
                    destination_path = os.path.join(REMOTE_HOLIDAY_DIR, file)
                    
                    try:
                        log(APP_NAME, "DEBUG", "Copying {} to {}:{}".format(source_path, server['hostname'], destination_path))
                        scp(server['hostname'], source_path, destination_path, "PUT")
                        log(APP_NAME, "DEBUG", "Successfully copied {} to {}:{}".format(source_path, server['hostname'], destination_path))
                    except FileNotFoundError:
                        log(APP_NAME, "ERROR", "File not found: {}".format(source_path))
                    except Exception as err:
                        log(APP_NAME, "ERROR", "Failed to copy {} to {}:{}".format(source_path, server['hostname'], destination_path))
                        log(APP_NAME, "ERROR", str(err))
                    else:
                        log(APP_NAME, "DEBUG", "Copy {} to {}:{} is done.".format(source_path, server['hostname'], destination_path))
    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, "ERROR", traceback_error)
        sys.exit()

def holiday_checker():
    try:
        iso_code_list = get_iso_code_list()
        country_code_list = get_country_code_list()
        exch_class_list = get_exch_class_list()

        now = datetime.now()

        # For test(Christmas)
        # now = datetime(2023, 12, 25)

        exchange_map = copy.deepcopy(EXCHANGE_MAP)

        for ii in range(APP_INFO['check_date']['later']):
            holiday_list1 = []
            holiday_list2 = []
            holiday_list3 = []
            date = now + timedelta(days=ii)
            
            # Use Python Library(trading-calendars)
            for iso_code in iso_code_list:
                holiday_dict1 = get_holiday_from_iso_code(iso_code, date)
                holiday_list1.append(holiday_dict1)
            # Use Abstract API for Holiday
            for country_code in country_code_list:
                holiday_dict2 = get_holiday_from_country_code(country_code, date)
                holiday_list2.append(holiday_dict2)
            # Get the holiday information from our database
            for exch_class in exch_class_list:
                holiday_dict3 = get_holiday_from_database(exch_class, date)
                
                if holiday_dict3 is not None:
                    holiday_list3.append(holiday_dict3)
            
            save_holiday(date, holiday_list1, holiday_list2, holiday_list3, exchange_map)

        write_exchange_map(exchange_map)

        # Update the holidays on Naverworks Calendar
        update_naverworks_calendar(exchange_map)

        # scp holidays file to con servers
        if not TEST:
            copy_holidays_to_remote()
            
    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()

def main():
    try:
        check_time = APP_INFO['check_date']['time']
        
        if TEST:
            holiday_checker()
            sys.exit()

        schedule.every().sunday.at(check_time).do(holiday_checker)
       
        log(APP_NAME, MUST, "This program check the holiday every {} on Sunday..".format(check_time))

        while True:
            log(APP_NAME, DEBUG, "Run this program..!")
            schedule.run_pending()
            log(APP_NAME, DEBUG, "Sleep for {} seconds.. (wake up every {} on Sunday)".format(SLEEP_TIME, check_time))

            time.sleep(SLEEP_TIME)

    except Exception as err:
        log(APP_NAME, ERROR, err)
        sys.exit()

def db_create_holiday(db):
    try:
        step = 0
        model = copy.deepcopy(DB_MODEL)

        while True:
            # exchange 
            if step == 0:
                found = False
                exch_name = input('Exchange name:')

                for exch in EXCHANGE_MAP:
                    if exch['class'] == exch_name:
                        found = True
                        break
                
                if not found:
                    print("Invalid exchange name. Please enter a valid exchange name.")
                    continue

                model['exchange'] = exch_name
                step += 1

            # date
            if step == 1:
                holiday_date = input('Holiday date (YYYY-MM-DD):')

                try:
                    datetime.strptime(holiday_date, '%Y-%m-%d')
                except ValueError:
                    print('Invalid date format. Please enter the date in YYYY-MM-DD format.')
                    continue
                
                model['date'] = holiday_date
                step += 1

            # name
            if step == 2:
                holiday_name = input('Holiday name:')

                if len(holiday_name) <= 0:
                    print('Invalid holiday name. Please enter a valid holiday name.')
                    continue

                model['name'] = holiday_name
                step += 1

            # Confirmation
            if step == 3:
                print('Your command:')
                print('exchange:', model['exchange'])
                print('holiday date:', model['date'])
                print('holiday name:', model['name'])

                confirm = input('Create the holiday with the new values? [Y|N]')

                if confirm.lower() == 'y':
                    db.create(table=DATABASE['table'], data=model)
                    break
                elif confirm.lower() == 'n':
                    step = 0
                    continue
                else:
                    print('Invalid input. Please try again.')
                    continue

        return db
    except Exception as err:
        db.close()
        traceback_error = traceback.format_exc()
        print(traceback_error)
        sys.exit()

def db_read_holiday(db):
    try:
        step = 0

        while True:
            # exchange
            if step == 0:
                found = False
                exch_name = input('Exchange name:')

                if len(exch_name) <= 0:
                    exch_where = ""
                    step += 1
                    continue

                for exch in EXCHANGE_MAP:
                    if exch['class'] == exch_name:
                        found = True
                        break
                
                if not found:
                    print("Invalid exchange name. Please enter a valid exchange name.")
                    continue

                exch_where = "exchange = '{}'".format(exch_name)
                step += 1
            
            # date
            if step == 1:
                option = input("Select date field validation option [0: No filter, 1: Exact Match, 2: Year, 3: Month, 4: Day]: ")

                if option not in ['0', '1', '2', '3', '4']:
                    print("Invalid option. Please try again.")
                    continue
                
                if option == '0':
                    date_where = ""
                elif option == '1':
                    date_value = input("Enter the exact date value: ")
                    date_where = "date = '{}'".format(date_value)
                elif option == '2':
                    year_value = input("Enter the year: ")
                    date_where = "date LIKE '{}%'".format(year_value)
                elif option == '3':
                    month_value = input("Enter the month: ")
                    date_where = "date LIKE '%-{}-%'".format(month_value)
                elif option == '4':
                    day_value = input("Enter the day: ")
                    date_where = "date LIKE '%-{}'".format(day_value)

                step += 1
            
            # Confirmation
            if step == 2:
                if exch_where and not date_where:
                    where = exch_where
                elif not exch_where and date_where:
                    where = date_where
                elif exch_where and date_where:
                    where = "{} AND {}".format(exch_where, date_where)
                else:
                    where = None
                break

        holidays = db.read(table=DATABASE['table'], where=where)
        
        if not holidays:
            text = text_color(text = "No holidays found.\n", color = YELLOW, is_bold = True)
            print(text)
        else:
            headers = holidays[0].keys()
            rows = [list(holiday.values()) for holiday in holidays]
            print(tabulate(rows, headers=headers, tablefmt='fancy_grid'))

        return db
    except Exception as err:
        db.close()
        traceback_error = traceback.format_exc()
        print(traceback_error)
        sys.exit()

def db_update_holiday(db):
    try:
        step = 0
        holiday_id = input("Enter the holiday ID to update: ")
        where = "id = '{}'".format(holiday_id)

        model = db.read(table=DATABASE['table'], where=where)[0]

        if not model:
            print("Holiday not found.")
            return db

        print("Existing holiday information:")
        print(f"Exchange name: {model['exchange']}")
        print(f"Holiday date: {model['date']}")
        print(f"Holiday name: {model['name']}")
        print("Enter new values (leave empty for fields you don't want to update):")

        while True:
            # exchange
            if step == 0:
                found = False
                exch_name = input('Exchange name:')

                if len(exch_name) <= 0:
                    step += 1
                    continue

                for exch in EXCHANGE_MAP:
                    if exch['class'] == exch_name:
                        found = True
                        break
                
                if not found:
                    print("Invalid exchange name. Please enter a valid exchange name.")
                    continue

                model['exchange'] = exch_name
                step += 1
        
            # date
            if step == 1:
                holiday_date = input('Holiday date (YYYY-MM-DD):')

                if len(holiday_date) <= 0:
                    step += 1
                    continue

                try:
                    datetime.strptime(holiday_date, '%Y-%m-%d')
                except ValueError:
                    print('Invalid date format. Please enter the date in YYYY-MM-DD format.')
                    continue

                model['date'] = holiday_date
                step += 1

            # name
            if step == 2:
                holiday_name = input('Holiday name:')

                if len(holiday_name) <= 0:
                    step += 1
                    continue

                if len(holiday_name) <= 0:
                    print('Invalid holiday name. Please enter a valid holiday name.')
                    continue

                model['name'] = holiday_name
                step += 1

            # Confirmation
            if step == 3:
                print('Your command:')
                print('exchange:', model['exchange'])
                print('holiday date:', model['date'])
                print('holiday name:', model['name'])

                confirm = input('Update the holiday with the new values? [Y|N]')

                if confirm.lower() == 'y':
                    db.update(table=DATABASE['table'], data=model, where=where)
                    print("Holiday updated successfully!")
                    break
                elif confirm.lower() == 'n':
                    print("Update canceled.")
                    step = 0
                    continue
                else:
                    print('Invalid input. Please try again.')
                    continue
        return db
    except Exception as err:
        db.close()
        traceback_error = traceback.format_exc()
        print(traceback_error)
        sys.exit()

def db_delete_holiday(db):
    try:
        holiday_id = input("Enter the holiday ID to delete: ")

        where = "id = '{}'".format(holiday_id)

        db.delete(table=DATABASE['table'], where=where)
        print("Holiday deleted successfully!")
        return db
    except Exception as err:
        db.close()
        traceback_error = traceback.format_exc()
        print(traceback_error)
        sys.exit()

def holiday_crud():
    try:
        step = 0
        db = None

        while True:
            if step == 0:
                action = input('Action을 선택하세요 [C(Create) | R(Read) | U(Update) | D(Delete)]: ')

                if action.lower() not in ['c', 'r', 'u', 'd', 'create', 'read', 'update', 'delete']:
                    continue
                else:
                    step += 1
            
            if step == 1:
                db = DataBase(
                    host=DATABASE['host'],
                    username=DATABASE['username'],
                    password=DATABASE['password'],
                    db_name=DATABASE['name'],
                )

                db.connect()

                # Step 1: Create holiday
                if action.lower() in ['c', 'create']:
                    # Implement the logic for creating a holiday
                    db = db_create_holiday(db)
                    step += 1

                # Step 1: Read holiday
                elif action.lower() in ['r', 'read']:
                    # Implement the logic for reading holidays
                    db = db_read_holiday(db)
                    step += 1
                
                # Step 1: Update holiday
                elif action.lower() in ['u', 'update']:
                    # Implement the logic for updating a holiday
                    db = db_update_holiday(db)
                    step += 1

                # Step 1: Delete holiday
                elif action.lower() in ['d', 'delete']:
                    # Implement the logic for deleting a holiday
                    db = db_delete_holiday(db)
                    step += 1
            
                db.close()
            if step == 2:
                print("holiday CRUD process successfully done!")
                break
            
    except Exception as err:
        if db is not None:
            db.close()

        traceback_error = traceback.format_exc()
        print(traceback_error)
        sys.exit()

def holiday_loaddata(filename):
    try:
        model_list = []

        with open(filename, "r") as fd:
            json_data = json.load(fd)

        # Validation
        for attr in json_data:

            # Exchange
            found = False
            exch_name = attr.get('exchange')

            for exch in EXCHANGE_MAP:
                if exch['class'] == exch_name:
                    found = True
                    break
                
            if not found:
                raise Exception("Invalid exchange name. Please enter a valid exchange name.")

            # Date
            holiday_date = attr.get('date')

            try:
                datetime.strptime(holiday_date, '%Y-%m-%d')
            except ValueError:
                raise Exception('Invalid date format. Please enter the date in YYYY-MM-DD format.')
                
            # Name
            holiday_name = attr.get('name')

            if len(holiday_name) <= 0:
                raise Exception("Invalid holiday name. Please enter the name of holiday")
        
            # Append model list
            db_model = copy.deepcopy(DB_MODEL)
            db_model['exchange'] = exch_name
            db_model['date'] = holiday_date
            db_model['name'] = holiday_name

            model_list.append(db_model)

        # Database Processing
        db = DataBase(
            host=DATABASE['host'],
            username=DATABASE['username'],
            password=DATABASE['password'],
            db_name=DATABASE['name'],
        )

        db.connect()

        for model in model_list:
            try:
                db.create(table=DATABASE['table'], data=model)
            except Exception as err:
                print(err)
                continue

        db.close()

    except Exception as err:
        if db is not None:
            db.close()
        print(err)

def holiday_calendar_update():
    try:
        naverworks_app_name = APP_INFO['naverworks_app_name']
        user_name = APP_INFO['user_name']
        calendar_name = APP_INFO['calendar_name']

        # Get now
        now = datetime.now()
        where = "date > '{}'".format(now.strftime('%Y-%m-%d'))

        # Database Processing
        db = DataBase(
            host=DATABASE['host'],
            username=DATABASE['username'],
            password=DATABASE['password'],
            db_name=DATABASE['name'],
        )

        db.connect()

        holidays = db.read(table=DATABASE['table'], where=where)

        for holiday in holidays:
            exchange = holiday.get('exchange')
            date = datetime.strptime(holiday.get('date').strftime("%Y-%m-%d 00:00:00"), "%Y-%m-%d %H:%M:%S")
            name = holiday.get('name')
            summary = "{} 휴장일({})".format(exchange, name)

            try:
                response = Tool().create_unique_calendar_event(naverworks_app_name, user_name, calendar_name, summary, date)
                            
                if isinstance(response, str):
                    print("Response: {}".format(response))
                else:
                    print("Response: {}".format(response.json()))
            except Exception as err:
                traceback_error = traceback.format_exc()
                print(traceback_error)
                time.sleep(5)
    except Exception as err:
        if db is not None:
            db.close()
        print(err)

if __name__ == "__main__":
    main()
