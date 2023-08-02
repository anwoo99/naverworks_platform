from lib.config import *

class DataBase():
    def __init__(self, host, username, password, db_name):
        self.host = host
        self.username = username
        self.password = password
        self.db_name = db_name
        self.connection = None
        self.cursor = None
    
    def connect(self):
        self.connection = pymysql.connect(
            host=self.host, 
            user=self.username,
            password=self.password,
            db=self.db_name,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        self.cursor = self.connection.cursor()
    
    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
    
    def create(self, table, data):
        try:
            placeholders = ', '.join(['%s'] * len(data))
            columns = ', '.join(data.keys())
            values = tuple(data.values())
            
            sql = f"INSERT INTO `{table}` ({columns}) VALUES({placeholders})"
            self.cursor.execute(sql, values)
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise Exception("Error occurred:", e)
    
    def read(self, table, where=None):
        try:
            if where:
                sql = f"SELECT * FROM `{table}` WHERE {where}"
            else:
                sql = f"SELECT * FROM `{table}`"
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            raise Exception("Error occurred:", e)
    
    def update(self, table, data, where):
        try:
            set_values = ', '.join([f"{column} = %s" for column in data.keys()])
            values = tuple(data.values())
            
            sql = f"UPDATE `{table}` SET {set_values} WHERE {where}"
            self.cursor.execute(sql, values)
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise Exception("Error occurred:", e)

    def delete(self, table, where):
        try:
            sql = f"DELETE FROM `{table}` WHERE {where}"
            self.cursor.execute(sql)
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise Exception("Error occurred:", e)