try:
    from .db_connection import DB_Connection
except Exception:
    from app.database.db_connection import DB_Connection

import os
from abc import ABC
from abc import abstractmethod
from werkzeug.security import check_password_hash
from app.database.db_functions import *

connection = DB_Connection(os.getenv('DB_HOST'), os.getenv('DB_NAME'), os.getenv('DB_USER'), os.getenv('DB_PASS'))

def getConnection():
    global connection
    if not connection:
        connection = DB_Connection(os.getenv('DB_HOST'), os.getenv('DB_NAME'), os.getenv('DB_USER'), os.getenv('DB_PASS'))
    return connection

def getNewConnection():
    return DB_Connection(os.getenv('DB_HOST'), os.getenv('DB_NAME'), os.getenv('DB_USER'), os.getenv('DB_PASS'))

class AbsUser(ABC):
    DB_HOST = os.getenv('DB_HOST')
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASS = os.getenv('DB_PASS')

    def __init__(self):
        self.database = getConnection()

    @abstractmethod
    def add_user(self) -> None:
        """ Adds a user to the database """
        pass
    @abstractmethod
    def check_password(self, pwd_hash: str) -> bool:
        """ Checks if a user's password matches the one in the database"""
        pass
    @abstractmethod
    def check_username_available(self, username: str) -> bool:
        """ checkUsernameAvailable = True iff username not in db"""
        pass
    @abstractmethod
    def get_next_id(self) -> int:
        """ Returns the next available userID """
        pass
    @abstractmethod
    def get_users(self) -> list:
        """ Returns a list of all users in the DB """
        pass

    @abstractmethod
    def update_info(self) -> None:
        """ Updates a user's account info, e.g password, email, etc."""
        pass

    @abstractmethod
    def add_to_users(self):
        """adds to the user table"""

    @abstractmethod
    def get_user_data(self):
        """returns the user's data as a 2D array"""

    @abstractmethod
    def getUsername(self) -> str:
        """ Returns the username"""

    @abstractmethod
    def getRole(self) -> str:
        """ Returns the role"""

    @abstractmethod
    def getPoints(self) -> int:
        """ Returns points"""

    @abstractmethod
    def populate(self, username: str):
        """ populates the class with the data from the database"""

    @abstractmethod
    def delete(self):
        """ Deletes the user from the database """


        
        
class Admin(AbsUser):
    def __init__(self, fname='NULL', mname='NULL', lname='NULL', user='NULL', 
                 phone='NULL', email='NULL', pwd='NULL', image='NULL'):
        self.properties = {}
        self.properties['fname'] = fname
        self.properties['mname'] = mname
        self.properties['lname'] = lname
        self.properties['user'] = user
        self.properties['id'] = 0
        self.properties['phone'] = phone
        self.properties['email'] = email
        self.properties['pwd'] = pwd
        self.properties['image'] = image
        self.properties['date_join'] = 'NULL'
        self.properties['suspension'] = False
        self.properties['role'] = 'admin'
        self.properties['sandbox'] = 'NULL'
        self.properties['points'] = 99999999

        self.database = getConnection()

    def setLogIn(self, loggedIn):
        self.loggedIn = loggedIn

    def get_next_id(self):
        query = 'SELECT MAX(admin_id) FROM admin'
        rows = self.database.query(query)
        
        if rows[0][0] == None:
            return 1
        else:
            return rows[0][0] + 1

    def add_user(self):
        self.properties['id'] = self.get_next_id()
        query = 'INSERT INTO admin VALUES (%(fname)s, %(mname)s, %(lname)s, %(user)s, %(id)s, %(phone)s, %(email)s, %(pwd)s, NOW(), %(END)s)'
        self.properties['END'] = 'NULL'
        
        try:
            self.database.insert(query, self.properties)
            self.add_to_users()
            self.database.commit()

        except Exception as e:
            raise Exception(e)

    def check_password(self, pwd_hash):
        query = "SELECT pwd FROM admin WHERE user=%s"
        db_pwd = self.database.query(query, self.properties['user'])

        return check_password_hash(pwd_hash, db_pwd)

    def check_username_available(self):
        query = "SELECT COUNT(*) FROM users WHERE UserName=\"{}\"".format(self.properties['user'])

        out = self.database.query(query) 
        print(out)
        return out[0][0] == 0 or out == None

    def update_info(self, data: dict):
        
        query = "UPDATE admin SET "

        q_list = []
        for key in data.keys():
            q_list.append("{} = %s".format(key))

        query += ", ".join(q_list) + " WHERE user=\"{}\"".format(self.properties['user'])

        try:
            self.database.insert(query, params=tuple(data.values()))
            self.database.commit()

        except Exception as e:
            raise Exception(e)

    def get_users(self):
        query = "SELECT * FROM admin"

        try:
            out = self.database.query(query)
            return out
        except Exception as e:
            raise Exception(e)

    # returns user data as a 2D array in the following format
    # [0][0] = first name
    # [0][1] = middle name
    # [0][2] = last name
    # [0][3] = username
    # [0][4] = id number
    # [0][5] = phone
    # [0][6] = email
    # [0][7] = image which should be null
    # [0][8] = date_join
    def get_user_data(self):
        query = 'SELECT first_name, mid_name, last_name, user, admin_id, phone, email, image, date_join FROM admin WHERE user = %s'
        val = (self.properties['user'], )


        try:
            data = self.database.query(query, val)
            return data

        except Exception as e:
            raise Exception(e)
    
    def add_to_users(self):

        query = 'INSERT INTO users (Username, {}, last_in) VALUES (\'{}\', {}, CURRENT_TIMESTAMP())'
        query = query.format('Admin_ID', self.properties['user'], self.properties['id'])
        self.database.insert(query)
        self.database.commit()

    def setSandbox(self, sandbox):
        self.properties['sandbox'] = sandbox

    def getUsername(self):
        return self.properties['user']
    
    def getRole(self):
        return self.properties['role']

    def getSandbox(self):
        return self.properties['sandbox']

    def getPoints(self):
        return self.properties['points']

    def populate(self, username: str):
        query = 'SELECT first_name, mid_name, last_name, user, admin_id, phone, email, date_join FROM admin WHERE user = %s'
        vals = (username, )

        try:
            data = self.database.query(query, vals)

        except Exception as e:
            raise Exception(e)

        if data:
            self.properties['fname'] = data[0][0]
            self.properties['mname'] = data[0][1]
            self.properties['lname'] = data[0][2]
            self.properties['user'] = data[0][3]
            self.properties['id'] = data[0][4]
            self.properties['phone'] = data[0][5]
            self.properties['email'] = data[0][6]
            self.properties['pwd'] = 'NULL'
            self.properties['date_join'] = data[0][7]

    #this function returns true if a driver is currently suspended
    def is_suspended(self):
        
        sql = 'SELECT user FROM suspend WHERE user = %s'
        val = (self.properties['user'], )

        
        #this will remove suspended driver's whos suspensions are over
        try:
            self.database.delete('DELETE from suspend WHERE date_return <= NOW()')
            suspended_user = self.database.query(sql, val)
            self.database.commit()
        except Exception as e:
            raise Exception(e)
        
        if suspended_user == None:
            return False
        else:
            return True

    #this function adds a driver to a suspension list and their length of suspension
    def suspend_user(self, username, year, month, day):

        self.database = getNewConnection()
        if month < 10:
            month = '0' + str(month)
        else:
            month = str(month)

        year = str(year)
        day = str(day)
        
        str_date = year + '-' + month + '-' + day

        query = 'INSERT INTO suspend VALUES (%s, %s)'
        vals = (username, str_date)
        try:
            self.database.insert(query, vals)
            self.database.commit()
        except Exception as e:
            raise Exception(e)

    def edit_suspension(self, username, year, month, day):       
        if month < 10:
            month = '0' + str(month)
        else:
            month = str(month)

        year = str(year)
        day = str(day)
        
        str_date = year + '-' + month + '-' + day
        query = 'UPDATE suspend SET date_return = %s WHERE user = %s'
        vals = (str_date, username)
        try:
            self.database.insert(query, vals)
            self.database.commit()
        except Exception as e:
            raise Exception(e)

    def get_suspended_users(self):
        self.database = getNewConnection()
        sus = self.database.query('SELECT user FROM suspend')
        sus_list = []
        
        for s in sus:
            sus_list.append(s[0])
        return sus_list

    def cancel_suspension(self, username):

        self.database = getNewConnection()
        query = 'DELETE FROM suspend WHERE user = %s'
        vals = (username, )
        try:
            self.database.delete(query, vals)
            self.database.commit()
        except Exception as e:
            raise Exception(e)
        

    def remove_user(self, username):

        self.database = getNewConnection()
        username = str(username).strip()
        sql = 'SELECT Driver_ID, Sponsor_ID FROM users WHERE UserName = \'{}\''.format(username)
        print(sql)
        id = self.database.query(sql)
        if id[0][0] != None:
            role = 'driver'
        elif id[0][1] != None:
            role = 'sponsor'
        else:
            role = 'admin'


        try:
            self.database.delete('DELETE FROM suspend WHERE user = %s', (username, ))
            self.database.delete('DELETE FROM users WHERE UserName = \'{}\''.format(username))
            self.database.delete('DELETE FROM ' + role + ' WHERE user = %s', (username, ))
            if role == 'driver':
                id = id[0][0]
                self.database.delete('DELETE FROM Product_Orders WHERE Driver_ID = %s', (id, ))
                self.database.delete('DELETE FROM driver_bridge WHERE driver_id = %s', (id, ))
                self.database.delete('DELETE FROM points_leaderboard WHERE driver_id = %s', (id, ))
            if role == 'sponsor':
                id = id[0][1]
                self.database.delete('DELETE FROM driver_bridge WHERE sponsor_id = {}'.format(id))
                self.database.delete('DELETE FROM points_leaderboard WHERE sponsor_id = {}'.format(id))
            self.database.commit()
        except Exception as e:
            raise Exception(e)


    def add_to_sponsor(self, driver_id, sponsor_id):
        bridge_query = 'INSERT INTO driver_bridge VALUES (%s, %s, 0, 0)'
        points_query = 'INSERT INTO points_leaderboard VALUES (%s, %s, 0)'
        vals = (driver_id, sponsor_id)
    
        try:
            self.database.insert(bridge_query, vals)
            self.database.insert(points_query, vals)
        except Exception as e:
            raise Exception(e)

    def get_sponsorless_drivers(self):
        sql = 'select driver.user, driver.first_name, driver.last_name, driver.driver_id, driver.date_join from driver where driver.driver_id not in (select driver.driver_id from driver inner join driver_bridge where driver.driver_id = driver_bridge.driver_id)'
        
        try:
            data = self.database.query(sql)
        except Exception as e:
            raise Exception(e)
        return data

    def upload_image(self, tempf):
        with open(tempf, 'rb') as file:
            image = file.read()

        sql = 'UPDATE driver SET image = %s WHERE user = %s'
        vals = (image, self.properties['user'])

        try:
            self.database.insert(sql, vals)
            self.database.commit()
            self.properties['image'] = image
        except Exception as e:
            raise Exception(e)


    def download_image(self, tempf):
        with open(tempf, 'wb') as file:
            file.write(self.properties['image'])

        return file

    def change_password(self, new_pwd):
        query = 'UPDATE admin SET pwd = %s WHERE user = %s'
        vals = (new_pwd, self.properties['user'])

        try:
            self.database.insert(query, vals)
            self.database.commit()
        except Exception as e:
            raise Exception(e)

    def delete(self):
        """ Deletes an admin from the users table and from the admin table """
        user_query = "DELETE FROM users WHERE Admin_ID=%s"
        user_vals = (self.properties['id'], )

        query = "DELETE FROM admin WHERE admin_id=%s"
        vals = (self.properties['id'], )
        try:
            self.database.query(user_query, user_vals)
            self.database.query(query, vals)
            self.database.commit()
        except Exception as e:
            raise Exception(e)

class Sponsor(AbsUser):
    def __init__(self, title='NULL', user='NULL', address='NULL', phone='NULL', 
                    email='NULL', pwd='NULL', image='NULL'):
        self.properties = {}
        self.properties['title'] = title
        self.properties['user'] = user
        self.properties['address'] = address
        self.properties['phone'] = phone
        self.properties['email'] = email
        self.properties['pwd'] = pwd
        self.properties['image'] = image
        self.properties['id'] = 0
        self.properties['date_join'] = 'NULL'
        self.properties['suspension'] = False
        self.properties['role'] = 'sponsor'
        self.properties['sandbox'] = 'NULL'
        self.properties['points'] = 99999999
        self.database = getConnection()

    def setLogIn(self, loggedIn):
        self.loggedIn = loggedIn

    def get_next_id(self):
        query = 'SELECT MAX(sponsor_id) FROM sponsor'
        rows = self.database.query(query)
        
        if rows[0][0] == None:
            return 1
        else:
            return rows[0][0] + 1
    
    def add_user(self):
        self.properties['id'] = self.get_next_id()
        query = 'INSERT INTO sponsor VALUES (%(title)s, %(user)s, %(id)s, %(address)s, %(phone)s, %(email)s, %(pwd)s, %(image)s, NOW(), %(END)s)'
        self.properties['END'] = 'NULL'

        try:
            self.database.insert(query, params=self.properties)
            self.add_to_users()
            self.database.commit()

        except Exception as e:
            raise Exception(e)

    def check_password(self, pwd_hash):
        query = "SELECT pwd FROM sponsor WHERE user=%s"
        db_pwd = self.database.query(query, self.properties['user'])

        return check_password_hash(pwd_hash, db_pwd)


    def check_username_available(self):
        query = "SELECT COUNT(*) FROM users WHERE UserName=\"{}\"".format(self.properties['user'])

        out = self.database.query(query) 
        print(out)
        return out[0][0] == 0 or out == None

    def update_info(self, data: dict):
        
        query = "UPDATE sponsor SET "

        q_list = []
        for key in data.keys():
            q_list.append("{} = %s".format(key))

        query += ", ".join(q_list) + " WHERE user=\"{}\"".format(self.properties['user'])

        try:
            self.database.query(query, params=tuple(data.values()))
            self.database.commit()

        except Exception as e:
            raise Exception(e)

    def get_users(self):
        query = "SELECT title, user, sponsor_id, address, phone, email, image, date_join FROM sponsor"

        try:
            out = self.database.query(query)
            return out
        except Exception as e:
            raise Exception(e)

    # returns user data as a 2D array in the following formart
    # [0][0] = title
    # [0][1] = username
    # [0][2] = id number
    # [0][3] = address
    # [0][4] = phone
    # [0][5] = email
    # [0][6] = image should be null for now
    # [0][7] = date that was join
    def get_user_data(self):
        query = 'SELECT title, user, sponsor_id, address, phone, email, image, date_join FROM sponsor WHERE user = %s'
        val = (self.properties['user'], )


        try:
            data = self.database.query(query, val)
            return data

        except Exception as e:
            raise Exception(e)

    def add_to_users(self):
        query = 'INSERT INTO users (Username, {}, last_in) VALUES (\'{}\', {}, CURRENT_TIMESTAMP())'
        query = query.format('Sponsor_ID', self.properties['user'], self.properties['id'])
        self.database.insert(query)
        self.database.commit()

    def setSandbox(self, sandbox):
        self.properties['sandbox'] = sandbox

    def getUsername(self):
        return self.properties['user']
    
    def getRole(self):
        return  self.properties['role']

    def getSandbox(self):
        return self.properties['sandbox']

    def getPoints(self):
        return 999999

    def populate(self, username: str):
        query = 'SELECT title, user, sponsor_id, address, phone, email, image, date_join FROM sponsor WHERE user = %s'
        vals = (username, )

        try:
            data = self.database.query(query, vals)
            self.database.commit()
        except Exception as e:
            raise Exception(e)


        if data:
            self.properties['title'] = data[0][0]
            self.properties['user'] = data[0][1]
            self.properties['id'] = data[0][2]
            self.properties['address'] = data[0][3]
            self.properties['phone'] = data[0][4]
            self.properties['email'] = data[0][5]
            self.properties['pwd'] = 'NULL'
            self.properties['image'] = data[0][6]
            self.properties['date_join'] = data[0][7]

    def is_suspended(self):
        
        sql = 'SELECT user FROM suspend WHERE user = %s'
        val = (self.properties['user'], )

        try:
            #this will remove suspended driver's whos suspensions are over
            self.database.delete('DELETE from suspend WHERE date_return <= NOW()')
            suspended_user = self.database.query(sql, val)
            self.database.commit()
        except Exception as e:
            raise Exception(e)
        
        if suspended_user == None:
            return False
        else:
            return True

    def edit_suspension(self, username, year, month, day):       
        if month < 10:
            month = '0' + str(month)
        else:
            month = str(month)

        year = str(year)
        day = str(day)
        
        str_date = year + '-' + month + '-' + day
        query = 'UPDATE suspend SET date_return = %s WHERE user = %s'
        vals = (str_date, username)
        try:
            self.database.insert(query, vals)
            self.database.commit()
        except Exception as e:
            raise Exception(e)

    def get_suspended_users(self):
        self.database = getNewConnection()
        sus = self.database.query('SELECT user FROM suspend')
        sus_list = []
        
        for s in sus:
            sus_list.append(s[0])
        return sus_list

    def cancel_suspension(self, username):
        query = 'DELETE FROM suspend WHERE user = %s'
        vals = (username, )
        try:
            self.database.delete(query, vals)
            self.database.commit()
        except Exception as e:
            raise Exception(e)

    def view_applications(self):
        query = 'SELECT driver.user, driver.first_name, driver.last_name, driver.driver_id FROM driver INNER JOIN driver_bridge ON driver.driver_id = driver_bridge.driver_id WHERE driver_bridge.sponsor_id = %s AND apply = 1'
        vals = (self.properties['id'], )

        try: 
            apps = self.database.query(query, vals)
        except Exception as e:
            raise Exception(e)

        return apps


    def view_drivers(self):
        query = 'SELECT driver.first_name, driver.mid_name, driver.last_name, driver.user, driver_bridge.points, driver.date_join FROM driver INNER JOIN driver_bridge ON driver.driver_id = driver_bridge.driver_id WHERE driver_bridge.sponsor_id = %s AND apply = 0 ORDER BY driver_bridge.points DESC'
        vals = (self.properties['id'], )

        try: 
            drivers = self.database.query(query, vals)
        except Exception as e:
            raise Exception(e)

        return drivers


    def accept_application(self, driver_id):
        query = 'UPDATE driver_bridge SET apply = 0 WHERE driver_id = %s AND sponsor_id = %s'
        vals = (driver_id, self.properties['id'])

        try: 
            self.database.insert(query, vals)
            self.database.commit()
        except Exception as e:
            raise Exception(e)
    
    def decline_application(self, driver_id):
        query = 'DELETE FROM driver_bridge WHERE driver_id = %s AND sponsor_id = %s'
        vals = (driver_id, self.properties['id'])

        try: 
            self.database.delete(query, vals)
            self.database.commit()
        except Exception as e:
            raise Exception(e)

    def add_points(self, driver_id, add_points):
        self.database = getNewConnection()

        data = self.database.query('SELECT points FROM driver_bridge WHERE driver_id = %s AND sponsor_id = %s AND apply = 0', (driver_id, self.properties['id']))
        current_points = data[0][0]

        current_points += add_points

        query = 'UPDATE driver_bridge SET points = %s WHERE driver_id = %s AND sponsor_id = %s'
        vals = (current_points, driver_id, self.properties['id'])
        try: 
            self.database.insert(query, vals)
            self.database.commit()
        except Exception as e:
            raise Exception(e)

        data = self.database.query('SELECT points FROM points_leaderboard WHERE driver_id = %s AND sponsor_id = %s', (driver_id, self.properties['id']))
        current_points = data[0][0]

        current_points += add_points
        vals = (current_points, driver_id, self.properties['id'])
        
        leader = 'UPDATE points_leaderboard SET points = %s WHERE driver_id = %s AND sponsor_id = %s'
        try: 
            self.database.insert(leader, vals)
            self.database.commit()
        except Exception as e:
            raise Exception(e)

    def view_leaderboard(self):
        query = 'SELECT driver.first_name, driver.mid_name, driver.last_name, driver.user, points_leaderboard.points FROM driver INNER JOIN points_leaderboard ON driver.driver_id = points_leaderboard.driver_id WHERE sponsor_id = %s ORDER BY points_leaderboard.points DESC'
        val = (self.properties['id'], )

        try: 
            leaders = self.database.query(query, val)
        except Exception as e:
            raise Exception(e)

        return leaders


    def remove_driver(self, driver_id):
        query = 'DELETE FROM driver_bridge WHERE driver_id = %s AND sponsor_id = %s'
        remove_leader = 'DELETE FROM points_leaderboard WHERE driver_id = %s and sponsor_id = %s'
        vals = (driver_id, self.properties['id'])

        try: 
            self.database.delete(query, vals)
            self.database.delete(remove_leader, vals)
            self.database.commit()
        except Exception as e:
            raise Exception(e)

    
    def upload_image(self, tempf):
        with open(tempf, 'rb') as file:
            image = file.read()

        sql = 'UPDATE driver SET image = %s WHERE user = %s'
        vals = (image, self.properties['user'])

        try:
            self.database.insert(sql, vals)
            self.database.commit()
            self.properties['image'] = image
        except Exception as e:
            raise Exception(e)

    def download_image(self, tempf):
        with open(tempf, 'wb') as file:
            file.write(self.properties['image'])

        return file
        
    #this function adds a driver to a suspension list and their length of suspension
    def suspend_user(self, username, year, month, day):

        if month < 10:
            month = '0' + str(month)
        else:
            month = str(month)

        year = str(year)
        day = str(day)
        
        str_date = year + '-' + month + '-' + day

        query = 'INSERT INTO suspend VALUES (%s, %s)'
        vals = (username, str_date)
        try:
            self.database.insert(query, vals)
            self.database.commit()
        except Exception as e:
            raise Exception(e)

    def change_password(self, new_pwd):
        query = 'UPDATE sponsor SET pwd = %s WHERE user = %s'
        vals = (new_pwd, self.properties['user'])

        try:
            self.database.insert(query, vals)
            self.database.commit()
        except Exception as e:
            raise Exception(e)


    def delete(self):
        """ Deletes a sponsor from the users table and from the sponsor table """
        user_query = "DELETE FROM users WHERE Sponsor_ID=%s"
        user_vals = (self.properties['id'], )

        query = "DELETE FROM sponsor WHERE sponsor_id=%s"
        vals = (self.properties['id'], )
        try:
            self.database.query(user_query, user_vals)
            self.database.query(query, vals)
            self.database.commit()
        except Exception as e:
            raise Exception(e)



class Driver(AbsUser):
    def __init__(self, fname='NULL', mname='NULL', lname='NULL', user='NULL', 
                 address='NULL', phone='NULL', email='NULL', pwd='NULL', image='NULL'):
        # Dictionary to keep track of driver data
        self.properties = {}
        self.properties['fname'] = fname
        self.properties['mname'] = mname
        self.properties['lname'] = lname
        self.properties['user'] = user
        self.properties['id'] = 0
        self.properties['sponsors'] = {}
        self.properties['address'] = address
        self.properties['phone'] = phone
        self.properties['email'] = email
        self.properties['pwd'] = pwd
        self.properties['image'] = image
        self.properties['date_join'] = 'NULL'
        self.properties['suspension'] = False
        self.properties['role'] = 'driver'
        self.properties['sandbox'] = 'NULL'

        self.database = getConnection()

    def setLogIn(self, loggedIn):
        self.loggedIn = loggedIn
        
    def get_next_id(self):
        query = 'SELECT MAX(driver_id) FROM driver'
        rows = self.database.query(query)
        
        if rows[0][0] == None:
            return 1
        else:
            return rows[0][0] + 1

    def add_user(self):
        self.properties['id'] = self.get_next_id()
        self.properties['END'] = 'NULL'
        query = 'INSERT INTO driver VALUES (\'{fname}\', \'{mname}\', \'{lname}\', \'{user}\', \'{id}\', \'{address}\', \'{phone}\', \'{email}\', \'{pwd}\', NOW(), \'{END}\', \'{image}\')'.format(**self.properties)
        print(query)

        try:
            self.database.insert(query)
            self.add_to_users()
            self.database.commit()

        except Exception as e:
            raise Exception(e)

    def check_password(self, pwd_hash):
        query = "SELECT pwd FROM driver WHERE user=%s"
        db_pwd = self.database.query(query, self.properties['user'])

        return check_password_hash(pwd_hash, db_pwd)

    def check_username_available(self):
        query = "SELECT COUNT(*) FROM users WHERE UserName=\"{}\"".format(self.properties['user'])

        out = self.database.query(query) 
        print(out)
        return out[0][0] == 0 or out == None

    def get_current_id(self):
        query = "SELECT driver_id FROM driver WHERE email=\"{}\" AND user=\"{}\""
        query = query.format(self.properties['email'], self.properties['user'])

        try:
            d_id = self.database.query(query)
            if not d_id:
                return None

            return d_id
        except Exception as e:
            raise Exception(e)

    def update_info(self, data: dict):
        """ Updates user info using current state of user 
            data expects a dictionary in the following format:
                each key is a named attribute of driver, and is followed by a key that is not None"""
     
        
        query = "UPDATE driver SET "

    # Generate list of items to update in query
        q_list = []
        for key in data.keys():
            q_list.append("{} = %s".format(key))

        username = self.properties['user']
    # Add items to update in query and add in WHERE to find correct user
        query += ", ".join(q_list) + " WHERE user=\"{}\"".format(username)

        try:
            self.database.query(query, params=tuple(data.values()))
            self.database.commit()

        except Exception as e:
            raise Exception(e)

    def get_users(self):
        main_query = "SELECT first_name, mid_name, last_name, user, date_join, driver_id FROM driver"
        try:
            out = self.database.query(main_query)
        except Exception as e:
            raise Exception(e)

        final_list = []

        for driver in out:
            sponsors = 'SELECT sponsor_id, points FROM driver_bridge WHERE driver_id = %s and apply = 0'
            val = (driver[5], )
            try:
                sponsor = self.database.query(sponsors, val)
            except Exception as e:
                raise Exception(e)
            
            sponsor_dict = {}
            for s in sponsor:
                sponsor_id = '{}'.format(s[0])
                sponsor_dict[sponsor_id] = s[1]

            driver = list(driver)
            driver[5] = sponsor_dict
            final_list.append(driver)

        
        return final_list

    def view_sponsors(self):
        query = 'SELECT sponsor_id, points FROM driver_bridge WHERE driver_id = %s AND apply = 0'
        val = (self.properties['id'], )
        try:
            username = self.database.query(query, val)
        except Exception as e:
                raise Exception(e)

        spon_list = []
        for user in username:
            spon_list.append(user)

        return spon_list
    
    # returns user data as a 2D array in the following formart
    # [0][0] = first name
    # [0][1] = middle name
    # [0][2] = last name
    # [0][3] = username
    # [0][4] = id number
    # [0][5] = sponsor id number
    # [0][6] = points
    # [0][7] = addresss
    # [0][8] = phone
    # [0][9] = email
    # [0][10] = image which should be null
    # [0][11] = date_join
    def get_user_data(self):
        query = 'SELECT first_name, mid_name, last_name, user, driver_id, sponsor_id, points, address, phone, email, image, date_join FROM driver WHERE user = %s'
        val = (self.properties['user'], )

        try:
            data = self.database.query(query, val)
            return data

        except Exception as e:
            raise Exception(e)

    def add_to_users(self):
        query = 'INSERT INTO users (Username, {}, last_in) VALUES (\'{}\', {}, CURRENT_TIMESTAMP())'
        query = query.format("Driver_ID", self.properties['user'], self.properties['id'])
        self.database.insert(query)
        self.database.commit()


    def setSandbox(self, sandbox):
        self.properties['sandbox'] = sandbox

    def getUsername(self):
        return self.properties['user']
    
    def getRole(self):
        return self.properties['role']

    def getPoints(self):
        return 0
    
    def getID(self):
        return self.properties['id']

    def getSandbox(self):
        return self.properties['sandbox']

    def is_suspended(self):
        
        sql = 'SELECT user FROM suspend WHERE user = %s'
        val = (self.properties['user'], )

        try:
            #this will remove suspended driver's whos suspensions are over
            self.database.delete('DELETE from suspend WHERE date_return <= NOW()')
            suspended_user = self.database.query(sql, val)
            self.database.commit()
        except Exception as e:
            raise Exception(e)

        if suspended_user == None:
            return False
        else:
            return True


    def populate(self, username: str):
        query = 'SELECT first_name, mid_name, last_name, user, driver_id, address, phone, email, image, date_join FROM driver WHERE user = %s'
        vals = (username, )

        try:
            data = self.database.query(query, vals)

        except Exception as e:
            raise Exception(e)

        if data:
            self.properties['fname'] = data[0][0]
            self.properties['mname'] = data[0][1]
            self.properties['lname'] = data[0][2]
            self.properties['user'] = data[0][3]
            self.properties['id'] = data[0][4]
            self.properties['address'] = data[0][5]
            self.properties['phone'] = data[0][6]
            self.properties['email'] = data[0][7]
            self.properties['pwd'] = 'NULL'
            self.properties['image'] = data[0][8]
            self.properties['date_join'] = data[0][9]

            query = 'SELECT sponsor_id, points FROM driver_bridge WHERE driver_id = %s AND apply = 0'
            vals = (self.properties['id'], )

            try:
                data = self.database.query(query, vals)
            except Exception as e:
                raise Exception(e)

            for d in data:
                sponsor_id = '{}'.format(d[0])
                self.properties['sponsors'][sponsor_id] = d[1] 

    def apply_to_sponsor(self, sponsor_id):
        query = 'INSERT INTO driver_bridge VALUES (%s, %s, %s, %s)'
        vals = (self.properties['id'], sponsor_id, 0, 1)

        try:
            self.database.insert(query, vals)
        except Exception as e:
            raise Exception(e)

    
    def upload_image(self, tempf):
        with open(tempf, 'rb') as file:
            image = file.read()

        sql = 'UPDATE driver SET image = %s WHERE user = %s'
        vals = (image, self.properties['user'])

        try:
            self.database.insert(sql, vals)
            self.database.commit()
            self.properties['image'] = image
        except Exception as e:
            raise Exception(e)

    def download_image(self, tempf):
        with open(tempf, 'wb') as file:
            file.write(self.properties['image'])

        return file

    def change_password(self, new_pwd):
        query = 'UPDATE driver SET pwd = %s WHERE user = %s'
        vals = (new_pwd, self.properties['user'])

        try:
            self.database.insert(query, vals)
            self.database.commit()
        except Exception as e:
            raise Exception(e)

    def delete(self):
        """ Deletes a driver from the users table and from the driver table """
        user_query = "DELETE FROM users WHERE Driver_ID=%s"
        user_vals = (self.properties['id'], )

        query = "DELETE FROM driver WHERE driver_id=%s"
        vals = (self.properties['id'], )
        try:
            self.database.query(user_query, user_vals)
            self.database.query(query, vals)
            self.database.commit()
        except Exception as e:
            raise Exception(e)


