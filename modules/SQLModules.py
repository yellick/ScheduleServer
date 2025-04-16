# libraries
import pymysql
import inspect
import hashlib
from datetime import datetime
import os

# modules
import modules.dbConfig as dbConfig
import modules.config as config
from modules.parcer import Parser
from modules.crypto import Crypto

crypto = Crypto(os.environ.get('ENCRYPTION_KEY'))
parser = Parser()

# connect to db function
def connect_to_db():
    try:
        connection = pymysql.connect(
            host=dbConfig.host,
            port=dbConfig.port,
            user=dbConfig.login,
            password=dbConfig.password,
            database=dbConfig.db,
            cursorclass=pymysql.cursors.DictCursor,
            ssl={'ca': None},  # Отключаем SSL для docker-сети
            connect_timeout=10,
            read_timeout=10,
            write_timeout=10
        )
        return connection
    except pymysql.Error as e:
        print(f"Database connection error: {e}")
        raise

# convert date from SQL to dd-mm-yyyy
def format_date(date_obj):
    return date_obj.strftime('%d-%m-%Y')

def change_date_on_schedule(arr):
    for item in arr:
        item['lesson_date'] = format_date(item['lesson_date'])

    return arr

# func for construct and print method status
def print_debug(fn, status, response):
    print(f"Debug: {fn} - {status[1]}. code: {status[0]}.\nResponse: {response}")

# func for hash
def hash_string(input_string):
    sha256 = hashlib.sha256()
    salted_string = input_string + config.salt
    sha256.update(salted_string.encode('utf-8'))
    return sha256.hexdigest()

# method with execute all requests
class SQL:
    @staticmethod
    def check_connection():
        func_name = inspect.currentframe().f_code.co_name
        status = SQLStat.err_unknown()
        response = {
            'server': True,
            'database': False,
            'error': None
        }

        try:
            connection = connect_to_db()
            if connection is None:
                status = SQLStat.err_db_con()
                response['error'] = "Database connection failed"
                if config.debug_mode:
                    print_debug(func_name, status, response)
                return SQLReturn(status, response)

            connection.close()
            status = SQLStat.succ()
            response['database'] = True

        except Exception as e:
            status = SQLStat.err_db_con()
            response['error'] = str(e)

        if config.debug_mode:
            print_debug(func_name, status, response)
        return SQLReturn(status, response)


    @staticmethod
    def auth(login, password):
        func_name = inspect.currentframe().f_code.co_name
        status = SQLStat.err_unknown()
        response = {'error': None, 'user': None, 'dataType': None}

        crypto_pass = crypto.encrypt(password)

        try:
            connection = connect_to_db()
            if connection is None:
                status = SQLStat.err_db_con()
                response['error'] = 'Database connection failed'
                if config.debug_mode:
                    print_debug(func_name, status, response)
                return SQLReturn(status, response)

            try:
                with connection.cursor() as cursor:
                    sql_check = """
                        SELECT * FROM `users` 
                        WHERE `login` = %s
                    """
                    cursor.execute(sql_check, login)
                    row = cursor.fetchone()

                    if row and crypto.decrypt(row['password']) == password:
                        status = SQLStat.succ()
                        response['user'] = dict(row) 
                        response['dataType'] = 'db'                      
                    else:
                        code, parser_data = parser.get_user_data(login, password)
                        
                        if code == 0:
                            sql_insert = """
                                INSERT INTO `users` 
                                    (`login`, `password`, `name`, `email`) 
                                VALUES 
                                    (%s, %s, %s, %s)
                            """
                            cursor.execute(sql_insert, (
                                login,
                                crypto_pass,
                                parser_data["full_name"],
                                parser_data["email"]
                            ))
                            connection.commit()

                            cursor.execute(sql_check, login)
                            row = cursor.fetchone()
                            
                            if row and crypto.decrypt(row['password']) == password:
                                status = SQLStat.succ()
                                response['user'] = dict(row)
                                response['dataType'] = 'parced'  
                            else:
                                status = SQLStat.err_not_found()
                                response['error'] = 'User not found after registration'
                        else:
                            status = SQLStat(1, 'Authentication failed')
                            response['error'] = parser_data

            except pymysql.MySQLError as e:
                status = SQLStat.err_request()
                response['error'] = str(e)
                if connection:
                    connection.rollback()
                if config.debug_mode:
                    print_debug(func_name, status, response)

            finally:
                if connection:
                    connection.close()

        except Exception as e:
            status = SQLStat.err_db_con()
            response['error'] = str(e)
            if config.debug_mode:
                print_debug(func_name, status, response)

        
        if status[0] == 0:
            response.pop('error', None)
        
        if config.debug_mode and status[0] != 0:
            print_debug(func_name, status, response)

        return SQLReturn(status, response)


    @staticmethod
    def get_themes(u_id):
        func_name = inspect.currentframe().f_code.co_name
        status = SQLStat.err_unknown()
        response = {'error': None, 'themes': None, 'dataType': None}

        try:
            connection = connect_to_db()
            if connection is None:
                status = SQLStat.err_db_con()
                response['error'] = 'Database connection failed'
                if config.debug_mode:
                    print_debug(func_name, status, response)
                return SQLReturn(status, response)

            try:
                with connection.cursor() as cursor:
                    sql_get_user = "SELECT * FROM `users` WHERE id = %s"
                    cursor.execute(sql_get_user, u_id)
                    row = cursor.fetchone()

                    if row:
                        try:
                            decrypted_password = crypto.decrypt(row['password'])
                        except Exception as decrypt_error:
                            status = SQLStat.err_decrypt_error()
                            response['error'] = f"Decryption failed: {decrypt_error}"
                            return SQLReturn(status, response)
                        
                        code, parser_data = parser.get_themes(row['login'], decrypted_password)

                        if code != 0:
                            status = SQLStat.err_auth_failed()
                            response['error'] = parser_data  
                            return SQLReturn(status, response)


                        sql_themes = "SELECT * FROM `themes` WHERE u_id = %s"
                        cursor.execute(sql_themes, u_id)
                        data = cursor.fetchall()
                            
                        themes = []
                        if data:
                            themes = [dict(row) for row in data]


                        existing_themes = {theme['theme'] for theme in themes}

                        new_themes = [
                            theme for theme in parser_data
                            if theme['theme'] not in existing_themes
                        ]


                        if new_themes:
                            sql_insert = """
                                INSERT INTO `themes` 
                                    (`u_id`, `type`, `theme`, `curator`) 
                                VALUES (%s, %s, %s, %s)
                            """

                            for theme in new_themes:
                                cursor.execute(sql_insert, (
                                    u_id,
                                    theme['type'],
                                    theme['theme'],
                                    theme['curator']
                                ))

                            connection.commit()
                            cursor.execute("SELECT * FROM themes WHERE u_id = %s", (u_id,))
                            response['themes'] = [dict(row) for row in cursor.fetchall()]

                            response['dataType'] = 'parced'
                            status = SQLStat.succ()

                        else:
                            response['themes'] = themes
                            response['dataType'] = 'db'
                            status = SQLStat.succ()

                    else:
                        status = SQLStat.err_not_found()
                        response['error'] = 'User not found by id'
                        return SQLReturn(status, response)


            except pymysql.MySQLError as e:
                status = SQLStat.err_request()
                response['error'] = str(e)
                if connection:
                    connection.rollback()
                if config.debug_mode:
                    print_debug(func_name, status, response)

            finally:
                if connection:
                    connection.close()

        except Exception as e:
            status = SQLStat.err_db_con()
            response['error'] = str(e)
            if config.debug_mode:
                print_debug(func_name, status, response)

        if status[0] == 0:
            response.pop('error', None)
        
        if config.debug_mode and status[0] != 0:
            print_debug(func_name, status, response)

        return SQLReturn(status, response)


    @staticmethod
    def get_skipping(u_id):
        func_name = inspect.currentframe().f_code.co_name
        status = SQLStat.err_unknown()
        response = {'error': None, 'skipping': None, 'dataType': None}

        try:
            connection = connect_to_db()
            if connection is None:
                status = SQLStat.err_db_con()
                response['error'] = 'Database connection failed'
                if config.debug_mode:
                    print_debug(func_name, status, response)
                return SQLReturn(status, response)

            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT login, password FROM `users` WHERE id = %s", 
                        u_id
                    )
                    user_data = cursor.fetchone()

                    if not user_data:
                        status = SQLStat.err_not_found()
                        response['error'] = 'User not found by id'
                        return SQLReturn(status, response)

                    try:
                        decrypted_password = crypto.decrypt(user_data['password'])
                        
                    except Exception as decrypt_error:
                        status = SQLStat.err_decrypt_error()
                        response['userdata'] = [user_data['login'], decrypted_password]  
                        response['error'] = f"Decryption failed: {decrypt_error}"
                        return SQLReturn(status, response)

                    code, parser_data = parser.get_skipping(user_data['login'], decrypted_password)
                    if code != 0:
                        status = SQLStat.err_auth_failed()
                        response['error'] = parser_data    
                        return SQLReturn(status, response)

                    cursor.execute("""
                        SELECT year, month, day, hours 
                        FROM `skippings` 
                        WHERE u_id = %s
                    """, u_id)
                    db_records = [dict(row) for row in cursor.fetchall()]
                    existing_records = {(r['year'], r['month'], r['day']): r['hours'] for r in db_records}

                    month_map = {
                        'Январь': 1, 'Февраль': 2, 'Март': 3, 'Апрель': 4,
                        'Май': 5, 'Июнь': 6, 'Июль': 7, 'Август': 8,
                        'Сентябрь': 9, 'Октябрь': 10, 'Ноябрь': 11, 'Декабрь': 12
                    }

                    updates = []
                    new_records = []
                    data_changed = False

                    for year_data in parser_data['skipping']:
                        year = int(year_data['year'])
                        for month_data in year_data['skippings']:
                            month = month_map[month_data['month']]
                            for day_data in month_data['skipping_days']:
                                day = day_data['day']
                                hours = day_data['hours']
                                key = (year, month, day)
                                
                                if key in existing_records:
                                    if existing_records[key] != hours:
                                        updates.append((hours, u_id, year, month, day))
                                        data_changed = True
                                else:
                                    new_records.append((u_id, year, month, day, hours))
                                    data_changed = True

                    if data_changed:
                        if updates:
                            sql = """
                                UPDATE `skippings` 
                                SET hours = %s 
                                WHERE u_id = %s AND year = %s AND month = %s AND day = %s
                            """
                            cursor.executemany(sql, updates)
                        
                        if new_records:
                            sql = """
                                INSERT INTO `skippings` 
                                (u_id, year, month, day, hours) 
                                VALUES (%s, %s, %s, %s, %s)
                            """
                            cursor.executemany(sql, new_records)
                        
                        cursor.execute("""
                            SELECT year, month, day, hours 
                            FROM `skippings` 
                            WHERE u_id = %s
                        """, u_id)

                        response['skipping'] = [dict(row) for row in cursor.fetchall()]
                        response['dataType'] = 'parced'
                    else:
                        response['skipping'] = db_records
                        response['dataType'] = 'db'

                    status = SQLStat.succ()
                    connection.commit()

            except pymysql.MySQLError as e:
                status = SQLStat.err_request()
                response['error'] = str(e)
                if connection:
                    connection.rollback()
                if config.debug_mode:
                    print_debug(func_name, status, response)

            finally:
                if connection:
                    connection.close()

        except Exception as e:
            status = SQLStat.err_db_con()
            response['error'] = str(e)
            if config.debug_mode:
                print_debug(func_name, status, response)

        if status[0] == 0:
            response.pop('error', None)
        
        if config.debug_mode and status[0] != 0:
            print_debug(func_name, status, response)

        return SQLReturn(status, response)


    @staticmethod
    def get_schedule_by_group(group_id,):
        func_name = inspect.currentframe().f_code.co_name

        status = SQLStat.err_unknown()
        response = []

        try:
            connection = connect_to_db()

            if connection is None:
                status = SQLStat.err_request()

                # debug
                if config.debug_mode:
                    print_debug(func_name, status, response)

                return SQLReturn(status, response)

            try:
                with connection.cursor() as cursor:
                    sql = """
                            SELECT 
	                            teachers.name, 
                                subjects.name, 
                                lesson_date, 
                                time_type, 
                                times.time_from, 
                                times.time_to, 
                                room 
                            FROM schedule 
                            INNER JOIN teachers ON teachers.id = teacher_id 
                            INNER JOIN subjects ON subjects.id = subject_id 
                            INNER JOIN times ON times.id = time_type 
                            WHERE group_id = %s 
                          """
                    
                    cursor.execute(sql, group_id)
                    rows = cursor.fetchall()

                    
                    if rows:
                        rows = change_date_on_schedule(rows)        

                        response = rows
                        status = SQLStat.succ()

                    else:
                        status = SQLStat.err_not_found()
                    
                    # debug
                    if config.debug_mode:
                        print_debug(func_name, status, response)

            except pymysql.MySQLError as e:
                status = SQLStat.err_request()
                response = e

                # debug
                if config.debug_mode:  
                    print_debug(func_name, status, response)

            finally:
                connection.close()

        except Exception as e:
            status = SQLStat.err_db_con()
            response = e

            # debug
            if config.debug_mode:
                print_debug(func_name, status, response)
        
        return SQLReturn(status, response)


    @staticmethod
    def start_session(user_id):
        func_name = inspect.currentframe().f_code.co_name

        status = SQLStat.err_unknown()
        response = []

        try:
            connection = connect_to_db()

            if connection is None:
                status = SQLStat.err_request()

                # debug
                if config.debug_mode:
                    print_debug(func_name, status, response)

                return SQLReturn(status, response)

            try:
                with connection.cursor() as cursor:
                    sql = "DELETE FROM `sessions` WHERE user_id = %s"
                    cursor.execute(sql, (user_id,))

                    sql = "INSERT INTO `sessions`(`session_hash`, `user_id`, `date`) VALUES (%s, %s, %s)"

                    #############################################
                    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-5]
                    session_hash = date + str(user_id) + config.salt
                    session_hash = hash_string(session_hash)

                    cursor.execute(sql, (session_hash, user_id, date))

                    status = SQLStat.succ()
                    response = {'session_hash': session_hash}

                    # debug
                    if config.debug_mode:
                        print_debug(func_name, status, response)

            except pymysql.MySQLError as e:
                status = SQLStat.err_request()
                response = e

                # debug
                if config.debug_mode:
                    print_debug(func_name, status, response)

            finally:
                connection.close()

        except Exception as e:
            status = SQLStat.err_db_conn()
            response = f"{e}"

            # debug
            if config.debug_mode:
                print_debug(func_name, status, response)

        return SQLReturn(status, response)


    @staticmethod
    def check_session(hash):
        func_name = inspect.currentframe().f_code.co_name

        status = SQLStat.err_unknown()
        response = False

        try:
            connection = connect_to_db()

            if connection is None:
                status = SQLStat.err_request()

                # debug
                if config.debug_mode:
                    print_debug(func_name, status, response)

                return SQLReturn(status, response)

            try:
                with connection.cursor() as cursor:
                    sql = "SELECT user_id FROM `sessions` WHERE session_hash = %s"
                    cursor.execute(sql, hash)
                    row = cursor.fetchall()

                    if row:
                        date = datetime.now().strftime('%Y-%m-%d')
                        sql = "UPDATE sessions SET date = %s WHERE session_hash = %s"
                        cursor.execute(sql, (date, hash))

                        response = True
                        status = SQLStat.succ()
                    else:
                        status = SQLStat.err_not_found()

                    # debug
                    if config.debug_mode:
                        print_debug(func_name, status, response)

            except pymysql.MySQLError as e:
                status = SQLStat.err_request()
                response = str(e)  # Преобразуем исключение в строку

                # debug
                if config.debug_mode:
                    print_debug(func_name, status, response)

            finally:
                connection.close()

        except Exception as e:
            status = SQLStat.err_db_conn()
            response = str(e)  # Преобразуем исключение в строку

            # debug
            if config.debug_mode:
                print_debug(func_name, status, response)

        # debug
        if status == SQLStat.err_unknown() and config.debug_mode:
            print_debug(func_name, status, response)

        return SQLReturn(status, response)


# response constructor 
class SQLReturn:
    def __init__(self, status, response):
        self.code = status[0]
        self.status = status[1]
        self.response = response
    
    def to_dict(self):
        return {
            'code': self.code,
            'status': self.status,
            'response': self.response
        }


class SQLStat:

    # SUCCESS
    def succ():
        return [0, 'Success']

    # ERROR
    def err_unknown():
        return [-1, 'Unknown error']

    def err_db_con():
        return [1, 'Failed to connect to the database']

    def err_request():
        return [1, 'The request could not be completed']
    
    def err_not_found():
        return [1, 'Data not found']
    
    def err_auth_failed():
        return [1, 'Authentication failed']
    
    def err_decrypt_error():
        return [1, 'Decryption failed']