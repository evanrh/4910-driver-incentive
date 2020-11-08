from mysql.connector import connect
from werkzeug.security import check_password_hash
import os

class AdminAuth():
    def __init__(self, user, pwd):
        self.user = user
        self.pwd = pwd

    def __enter__(self):
        self.database = connect(host = os.getenv('DB_HOST'),
                                database = os.getenv('DB_NAME'),
                                user = os.getenv('DB_USER'),
                                password = os.getenv('DB_PASS')
                                )
        self.cursor = self.database.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        self.database.close()
        
    def check_username(self):
        sql = "SELECT * FROM users WHERE UserName = '{}'".format(self.user)
        self.cursor.execute(sql)
        row = self.cursor.fetchall()
        return len(row) > 0
    def check_password(self):
        sql = "SELECT pwd FROM admin WHERE user = '{}'".format(self.user)
        self.cursor.execute(sql)
        row = self.cursor.fetchone()
        
        curHash = row[0]
        return check_password_hash(curHash, self.pwd)

