from mysql.connector import Error
import mysql.connector as ms

class DB_Connection():
    def __init__(self, host, name, user, pwd):
        try:
            self.conn = ms.connect(host = host,
                                   database = name,
                                   user = user,
                                   password = pwd)

        except Error as e:
            raise Error(e)

    def query(self, query):
        cursor = self.conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def __del__(self):
        self.conn.close()
