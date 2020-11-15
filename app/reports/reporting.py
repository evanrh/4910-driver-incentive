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
        sql = "SELECT * FROM Product_Orders WHERE Sponsor_Id=%s AND TimeStamp BETWEEN %s AND %s"
        start = dates[0].month
        end = dates[1].month
        vals = (sid, dates[0], dates[1])

        try:
            orders = self.conn.exec(sql, vals)
            results = dict(map(lambda i: (i, reduce(lambda x,y: x + y, map(lambda o: o[-1], filter(lambda order: order[1].month == i, orders)), 0)), range(start,end+1)))
            return results

            # Get amount of each order
            amounts = list(map(lambda e: e[-1], orders))

            results['spent'] = reduce(lambda x,y: x+y, amounts) if amounts else 0
            results['drivers'] = num_drivers
            return results
        except Exception as e:
            print(e)
            return None

    def total_sales(self, dates=()):
        """ Get total amount of sales per month in date range """
        sql = "SELECT * FROM Product_Orders WHERE TimeStamp BETWEEN %s AND %s"
        
        try:
            orders = self.conn.exec(sql, dates)
            months = dict(map(lambda i: (i, reduce(lambda x,y: x + y, map(lambda o: o[-1], filter(lambda order: order[1].month == i, orders)), 0)), range(dates[0].month,dates[1].month+1)))

            return months
        except Exception as e:
            print(e)
            return None

    def driver_purchases(self, sid): 
        """ Get list of all drivers and their purchases that are affilated with sponsor sid """
        sql = "SELECT user, name, amount FROM Product_Orders NATURAL JOIN driver, product WHERE Product_Orders.Product_ID=product.product_id AND Product_Orders.Sponsor_ID=%s"

        try:
            orders = self.conn.exec(sql, (sid, ))
            names = list(map(lambda e: e[0], orders))

            drivers = dict(map(lambda e: (e, []), names))

            def func(order):
                drivers[order[0]].append(order[1])
                return order

            orders = tuple(map(func, orders))
            return drivers
        except Exception as e:
            print(e)
            return None

    def __del__(self):
        self.conn.close()
