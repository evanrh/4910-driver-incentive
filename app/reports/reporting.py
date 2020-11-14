from ..database.db_users import getConnection
from io import StringIO
from datetime import datetime
from functools import reduce
import csv

class ReportController():
    def __init__(self):
        self.conn = getConnection()
    
    def number_users(self, userType):
        sql = "SELECT COUNT(*) FROM {}".format(userType)
        
        try:
            num = self.conn.exec(sql)
            return num[0][0] if num else 0
        except Exception as e:
            return 0

    def sponsor_stats(self, sid, dates=()):
        """ Get statistics about each sponsor in a date range 
            dates: tuple(start_date, end_date)
        """
        sql = "SELECT * FROM Product_Orders WHERE sponsor_id=%s"
        vals = None
        if dates:
            sql += " AND TimeStamp BETWEEN %s AND %s"
            vals = (sid, dates[0], dates[1])
        else:
            vals = (sid, )

        try:
            orders = self.conn.exec(sql, vals)
            results = {}

            # Get amount of each order
            amounts = list(map(lambda e: e[-1], orders))
            num_drivers = self.conn.exec("SELECT COUNT(*) FROM driver_bridge WHERE sponsor_id=%s", (sid, ))

            # Get number of drivers if they have any
            num_drivers = num_drivers[0][0] if num_drivers else 0
            results['spent'] = reduce(lambda x,y: x+y, amounts) if amounts else 0
            results['drivers'] = num_drivers
            return results
        except Exception as e:
            print(e)
            return None

    def __del__(self):
        self.conn.close()
