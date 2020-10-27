from mysql.connector import Error
import mysql.connector as ms

class DB_Connection():
    def __init__(self, host, name, user, pwd):
        try:
            self.host = host
            self.database = name
            self.user = user
            self.pwd = pwd
            self.conn = ms.connect(host = host,
                                   database = name,
                                   user = user,
                                   password = pwd)
            self.conn.autocommit = True

        except Error as e:
            raise Error(e)

    def query(self, query, params=None, multi=False):
        try:
            cursor = self.conn.cursor(buffered=True)
        except Exception as e:
            # Fix stupid issue on production where database connection times out hopefully
            self.conn = ms.connect(host = self.host,
                                   database = self.database,
                                   user = self.user,
                                   password = self.pwd)
            self.conn.autocommit = True
            cursor = self.conn.cursor(buffered=True)

        try:
            cursor.execute(query, params, multi)
            rows = cursor.fetchall()         
            cursor.close()
            return rows
        except Error as e:
            print("Something went wrong: {}".format(e))
            print(cursor.statement)

    def insert(self, query, params=None, multi=False):
        cursor = self.conn.cursor(buffered=True)

        try:
            cursor.execute(query, params, multi)
            cursor.close()
        except Error as e:
            print("Something went wrong: {}".format(e))
            print(cursor.statement)

    def delete(self, query, params=None, multi=False):
        cursor = self.conn.cursor(buffered=True)

        try:
            cursor.execute(query, params, multi)
            cursor.close()
        except Error as e:
            print("Something went wrong: {}".format(e))
            print(cursor.statement)


    def commit(self):
        self.conn.commit()

    def __del__(self):
        self.conn.close()
