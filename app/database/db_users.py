try:
    from .db_connection import *
    from .db_functions import *
except Exception:
    from app.database.db_connection import *
    from app.database.db_functions import *

import os
from abc import ABC
from abc import abstractmethod
from werkzeug.security import check_password_hash

config = {'host': os.getenv('DB_HOST'), 'database': os.getenv('DB_NAME'), 'user': os.getenv('DB_USER'), 'password': os.getenv('DB_PASS'), 'autocommit': True}
global pool1 
pool1 = ConnectionPool(size = 10, name = 'pool1', **config )

def getConnection(ex=0):
    if ex == 1:
        connection.close()
        connection = pool1.get_connection()
        return connection
        print(pool1.size())

    return pool1.get_connection()

def getNewConnection():
    return pool1.get_connection()
    
def isActive(username):
    conn = getConnection()
    sql = 'SELECT Driver_ID, Sponsor_ID, Admin_ID FROM users WHERE UserName = \'{}\''.format(username)
    id = conn.exec(sql)
    if id[0][0] != None:
        role =  'driver'
    elif id[0][1] != None:
        role =  'sponsor'
    else:
        role = 'admin'
    query = "SELECT active FROM " + role + ' WHERE user = \'{}\''.format(username)
    active = conn.exec(query)
    conn.close()
    return active[0][0] == 1

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
        self.properties['selectedSponsor'] = [1, 99999999]

        self.database = getConnection()

    def setLogIn(self, loggedIn):
        self.loggedIn = loggedIn

    def get_next_id(self):
        query = 'SELECT MAX(admin_id) FROM admin'
        rows = self.database.exec(query)
        #self.database.close()
        
        if rows[0][0] == None:
            return 1
        else:
            return rows[0][0] + 1

    def add_user(self):
        self.properties['id'] = self.get_next_id()
        self.properties['END'] = 'NULL'
        self.properties['active'] = 1
        query = 'INSERT INTO admin VALUES (\'{fname}\', \'{mname}\', \'{lname}\', \'{user}\', \'{id}\', \'{phone}\', \'{email}\', \'{pwd}\', NOW(), \'{END}\', \'{active}\')'.format(**self.properties)
        
        
        try:
            self.database.exec(query)
            self.add_to_users()
            #self.database.close()

        except Exception as e:
            raise Exception(e)

    def check_password(self, pwd_hash):
        query = "SELECT pwd FROM admin WHERE user=%s"
        db_pwd = self.database.exec(query, self.properties['user'])
        #self.database.close()

        return check_password_hash(pwd_hash, db_pwd)

    def check_username_available(self):
        query = "SELECT COUNT(*) FROM users WHERE UserName=\"{}\"".format(self.properties['user'])

        out = self.database.exec(query)
        #self.database.close()

        return out[0][0] == 0 or out == None

    def update_info(self, data: dict):
        
        query = "UPDATE admin SET "

        q_list = []
        for key in data.keys():
            q_list.append("{} = %s".format(key))

        query += ", ".join(q_list) + " WHERE user=\"{}\"".format(self.properties['user'])

        try:
            self.database.exec(query, args=tuple(data.values()))
            #self.database.close()

        except Exception as e:
            raise Exception(e)

    def get_users(self):
        query = "SELECT * FROM admin WHERE active = 1"

        try:
            out = self.database.exec(query)
            #self.database.close()
        except Exception as e:
            raise Exception(e)
        if out:
            return out
        else:
            return []

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
            data = self.database.exec(query, val)
            #self.database.close()
            return data

        except Exception as e:
            raise Exception(e)
    
    def add_to_users(self):

        query = 'INSERT INTO users (Username, {}, last_in) VALUES (\'{}\', {}, CURRENT_TIMESTAMP())'
        query = query.format('Admin_ID', self.properties['user'], self.properties['id'])
        self.database.exec(query)
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
        #self.database = getNewConnection()
        query = 'SELECT first_name, mid_name, last_name, user, admin_id, phone, email, date_join FROM admin WHERE user = %s'
        vals = (username, )

        try:
            data = self.database.exec(query, vals)
            #self.database.close()

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
            self.database.exec('DELETE from suspend WHERE date_return <= NOW()')
            suspended_user = self.database.exec(sql, val)
            #self.database.close()
        except Exception as e:
            raise Exception(e)
        
        if suspended_user == None:
            return False
        else:
            return True

    #this function adds a driver to a suspension list and their length of suspension
    def suspend_user(self, username, year, month, day):

        #self.database = getNewConnection()
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
            self.database.exec(query, vals)
            #self.database.close()
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
            self.database.exec(query, vals)
            #self.database.close()
        except Exception as e:
            raise Exception(e)

    def get_suspended_users(self):
        try:
            sus = self.database.exec('SELECT user FROM suspend')
            #self.database.close()
        except Exception as e:
            raise Exception(e)
        sus_list = []
    
        if sus:
            for s in sus:
                sus_list.append(s[0])
        return sus_list

    def cancel_suspension(self, username):

        #self.database = getNewConnection()
        query = 'DELETE FROM suspend WHERE user = %s'
        vals = (username, )
        try:
            self.database.exec(query, vals)
            #self.database.close()
        except Exception as e:
            raise Exception(e)
        

    def remove_user(self, username):

        #self.database = getNewConnection()
        username = str(username).strip()
        sql = 'SELECT Driver_ID, Sponsor_ID FROM users WHERE UserName = \'{}\''.format(username)

        id = self.database.exec(sql)
        if id[0][0] != None:
            role = 'driver'
        elif id[0][1] != None:
            role = 'sponsor'
        else:
            role = 'admin'


        try:
            self.database.exec('DELETE FROM suspend WHERE user = %s', (username, ))
            self.database.exec('UPDATE ' + role + ' SET active = 0 WHERE user = %s', (username, ))
            #self.database.close()
        except Exception as e:
            raise Exception(e)


    def add_to_sponsor(self, driver_id, sponsor_id):
        bridge_query = 'INSERT INTO driver_bridge VALUES (%s, %s, 0, 0)'
        points_query = 'INSERT INTO points_leaderboard VALUES (%s, %s, 0)'
        vals = (driver_id, sponsor_id)
    
        try:
            self.database.exec(bridge_query, vals)
            self.database.exec(points_query, vals)
            #self.database.close()
        except Exception as e:
            raise Exception(e)

    def get_sponsorless_drivers(self):
        sql = 'SELECT driver.user, driver.first_name, driver.last_name, driver.driver_id, driver.date_join FROM driver WHERE driver.driver_id NOT IN (select driver.driver_id from driver inner join driver_bridge where driver.driver_id = driver_bridge.driver_id) AND active = 1'
        
        try:
            data = self.database.exec(sql)
            #self.database.close()
        except Exception as e:
            raise Exception(e)
        if data:
            return data
        else:
            return []

    def get_disabled_drivers(self):
        sql = 'select user, first_name, last_name, driver_id, date_join FROM driver WHERE active = 0'
        
        try:
            data = self.database.exec(sql)
            #self.database.close()
        except Exception as e:
            raise Exception(e)
        if data:
            return data
        else:
            return []
    
    def get_disabled_sponsors(self):
        sql = 'select user, title, sponsor_id, date_join FROM sponsor WHERE active = 0'
        
        try:
            data = self.database.exec(sql)
            #self.database.close()
        except Exception as e:
            raise Exception(e)
        if data:
            return data
        else:
            return []

    def get_disabled_admins(self):
        sql = 'select user, first_name, last_name, admin_id, date_join FROM admin WHERE active = 0'
        
        try:
            data = self.database.exec(sql)
            #self.database.close()
        except Exception as e:
            raise Exception(e)
        if data:
            return data
        else:
            return []

    def reactivate_user(self, username):
        sql = 'SELECT Driver_ID, Sponsor_ID, Admin_ID FROM users WHERE UserName = \'{}\''.format(username)
        id = self.database.exec(sql)
        if id[0][0] != None:
            role =  'driver'
        elif id[0][1] != None:
            role =  'sponsor'
        else:
            role = 'admin'
        
        query = 'UPDATE ' + role + ' SET active = 1 WHERE user = \'{}\''.format(username)
        try:
            data = self.database.exec(query)
            #self.database.close()
        except Exception as e:
            raise Exception(e)

    def get_inbox_list(self):
        message_query = 'SELECT * FROM messages WHERE (target = %s AND seent = 0) OR (sender = %s AND seens = 0) '
        vals = (self.properties['user'], self.properties['user'])

        try:
            data = self.database.exec(message_query, vals)
            #self.database.close()
        except Exception as e:
            raise Exception(e)

        user_list = []
        if data:
            for d in data:
                if (d[0] not in user_list) and (d[0] != self.properties['user']):
                    user_list.append(d[0])
                elif (d[1] not in user_list) and (d[1] != self.properties['user']):                       
                    user_list.append(d[1])

        return user_list

    def messages_are_seen(self, user):
        if user == "MARK_ALL":
            query = 'UPDATE messages SET seens = 1 WHERE sender = %s'
            query2 = 'UPDATE messages SET seent = 1 WHERE target = %s'
            val = (self.properties['user'], )
            try:
                self.database.exec(query, val)
                self.database.exec(query2, val)
                #self.database.close()
            except Exception as e:
                raise Exception(e)
        else:
            query = 'UPDATE messages SET seent = 1 WHERE (target = %s AND sender = %s)'
            query2 = 'UPDATE messages SET seens = 1 WHERE (target = %s AND sender = %s)'
            val1 = (self.properties['user'], user)
            val2 = (user, self.properties['user'])
            try:
                self.database.exec(query, val1)
                self.database.exec(query2, val2)
                #self.database.close()
            except Exception as e:
                raise Exception(e)



    def get_msg_info(self, user):
        sql = 'SELECT Driver_ID, Sponsor_ID, Admin_ID FROM users WHERE UserName = %s'
        val = (user, )
        id = self.database.exec(sql, val)
        if id[0][0] != None:
            role =  'driver'
        elif id[0][1] != None:
            role =  'sponsor'
        else:
            role = 'admin'
        
        if role == 'driver' or role == 'admin':
            query = 'SELECT first_name, last_name, active FROM ' + role + ' WHERE user = %s'
        else:
            query = 'SELECT title, active FROM sponsor WHERE user = %s'
        val = (user, )
        
        try:
            data = self.database.exec(query, val)
            #self.database.close()
        except Exception as e:
            raise Exception(e)

        data_list = list(data[0])
        data_list.insert(0, role)
        return data_list


    def view_messages(self):
        message_query = 'SELECT * FROM messages WHERE target = %s OR sender = %s ORDER BY time ASC'
        vals = (self.properties['user'], self.properties['user'])

        try:
            data = self.database.exec(message_query, vals)
        except Exception as e:
            raise Exception(e)

        message_dict = {}

        if data:
            for d in data:
                user_list = list(message_dict.keys())
                if (d[0] not in user_list) and (d[0] != self.properties['user']):
                    message_dict[d[0]] = []
                    #get info about user from database
                    info = self.get_msg_info(d[0])
                    #if user is inactive add disabled tag to their last name and remove the tag from the list
                    if info[len(info) - 1] == 0:
                        info[len(info) - 2] += '(Disabled)'
                    info.pop(len(info) - 1)
                    message_dict[d[0]].append(info)
                    user = 0
                elif (d[1] not in user_list) and (d[1] != self.properties['user']):
                    message_dict[d[1]] = []
                    info = self.get_msg_info(d[1])
                    if info[len(info) - 1] == 0:
                        info[len(info) - 2] += '(Disabled)'
                    info.pop(len(info) - 1)
                    message_dict[d[1]].append(info)
                    user = 1
                elif(d[0] == self.properties['user'] and d[1] == self.properties['user'] and d[0] not in user_list):
                    message_dict[d[0]] = []
                    info = self.get_msg_info(d[0])
                    if info[len(info) - 1] == 0:
                        info[len(info) - 2] += '(Disabled)'
                    info.pop(len(info) - 1)
                    message_dict[d[0]].append(info)
                    user = 0
                else:
                    if d[0] != self.properties['user']:
                        user = 0
                    else:
                        user = 1
                    
                message_dict[d[user]].insert(1, (d[1], d[2], d[3]))
        
        return message_dict

    def send_message(self, target, message):
        time = 'SET time_zone = \'{}\''.format("America/New_York")
        query = 'INSERT INTO messages VALUES (%s, %s, %s, NOW(), 0, 1)'
        vals = (target, self.properties['user'], message)

        try:
            self.database.exec(time)
            self.database.exec(query, vals)
            #self.database.close()
        except Exception as e:
            raise Exception(e)
    
    def getProductInfo(self, id):
        query = 'SELECT name, price, img_url FROM product WHERE product_id = %s'
        val = (id)

        try:
            data = self.database.exec(query, val)
        except Exception as e:
            raise Exception(e)

        datalist = list(data[0])
        return datalist

    def upload_image(self, tempf):
        with open(tempf, 'rb') as file:
            image = file.read()

        sql = 'UPDATE driver SET image = %s WHERE user = %s'
        vals = (image, self.properties['user'])

        try:
            self.database.exec(sql, vals)
            self.properties['image'] = image
            #self.database.close()
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
            self.database.exec(query, vals)
            #self.database.close()
        except Exception as e:
            raise Exception(e)

    def delete(self):
        """ Disables an admin """
        

        query = "UPDATE admin SET active = 0 WHERE admin_id=%s"
        vals = (self.properties['id'], )
        try:
            self.database.exec(user_query, user_vals)
            self.database.exec(query, vals)
            #self.database.close()
        except Exception as e:
            raise Exception(e)

    def __del__(self):
        global pool1
        self.database.close()
        

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
        self.properties['selectedSponsor'] = [1, 9999999]
        self.properties['point_value'] = 0.01
        self.database = getConnection()

    def setLogIn(self, loggedIn):
        self.loggedIn = loggedIn

    def get_next_id(self):
        query = 'SELECT MAX(sponsor_id) FROM sponsor'
        rows = self.database.exec(query)
        #self.database.close()
        
        if rows[0][0] == None:
            return 1
        else:
            return rows[0][0] + 1
    
    def add_user(self):
        self.properties['id'] = self.get_next_id()
        self.properties['active'] = 1
        query = 'INSERT INTO sponsor VALUES (%(title)s, %(user)s, %(id)s, %(address)s, %(phone)s, %(email)s, %(pwd)s, %(image)s, NOW(), %(END)s, 0.01, %(active)s)'
        self.properties['END'] = 'NULL'

        # Filter properties to be all except selectedSponsor because list issue
        params = dict(filter(lambda x: x[0] != 'selectedSponsor', self.properties.items()))
        try:
            self.database.exec(query, params=params)
            self.add_to_users()
            #self.database.close()

        except Exception as e:
            raise Exception(e)

    def check_password(self, pwd_hash):
        query = "SELECT pwd FROM sponsor WHERE user=%s"
        db_pwd = self.database.exec(query, self.properties['user'])
        #self.database.close()

        return check_password_hash(pwd_hash, db_pwd)


    def check_username_available(self):
        query = "SELECT COUNT(*) FROM users WHERE UserName=\"{}\"".format(self.properties['user'])

        out = self.database.exec(query) 
        #self.database.close()

        return out[0][0] == 0 or out == None

    def update_info(self, data: dict):
        
        query = "UPDATE sponsor SET "

        q_list = []
        for key in data.keys():
            q_list.append("{} = %s".format(key))

        query += ", ".join(q_list) + " WHERE user=\"{}\"".format(self.properties['user'])

        try:
            self.database.exec(query, args=tuple(data.values()))
            #self.database.close()

        except Exception as e:
            raise Exception(e)

    def get_users(self):
        query = "SELECT title, user, sponsor_id, address, phone, email, image, date_join FROM sponsor where active = 1"

        try:
            out = self.database.exec(query)
            #self.database.close()
        except Exception as e:
            raise Exception(e)
        if out:
            return out
        else:
            return []

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
            data = self.database.exec(query, val)
            #self.database.close()
            return data

        except Exception as e:
            raise Exception(e)

    def add_to_users(self):
        query = 'INSERT INTO users (Username, {}, last_in) VALUES (\'{}\', {}, CURRENT_TIMESTAMP())'
        query = query.format('Sponsor_ID', self.properties['user'], self.properties['id'])
        self.database.exec(query)
        #self.database.close()

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

    def username_from_id(self, id):
        sql = "SELECT user FROM sponsor WHERE sponsor_id = %s"
        val = (id, )

        try:
            data = self.database.exec(sql, val)
            #self.database.close()
        except Exception as e:
            raise Exception(e)
        
        return data[0][0]

    def populate(self, username: str):
        #self.database = getNewConnection()
        query = 'SELECT title, user, sponsor_id, address, phone, email, image, date_join, point_value FROM sponsor WHERE user = %s'
        vals = (username, )

        try:
            data = self.database.exec(query, vals)
            #self.database.close()
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
            self.properties['point_value'] = data[0][8]

    def is_suspended(self):
        
        sql = 'SELECT user FROM suspend WHERE user = %s'
        val = (self.properties['user'], )

        try:
            #this will remove suspended driver's whos suspensions are over
            self.database.exec('DELETE from suspend WHERE date_return <= NOW()')
            suspended_user = self.database.exec(sql, val)
            #self.database.close()
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
            self.database.exec(query, vals)
            #self.database.close()
        except Exception as e:
            raise Exception(e)

    def get_suspended_users(self):
        #self.database = getNewConnection()
        sus = self.database.exec('SELECT user FROM suspend')
        sus_list = []
        
        for s in sus:
            sus_list.append(s[0])
        return sus_list

    def cancel_suspension(self, username):
        query = 'DELETE FROM suspend WHERE user = %s'
        vals = (username, )
        try:
            self.database.exec(query, vals)
            #self.database.close()
        except Exception as e:
            raise Exception(e)

    def view_applications(self):
        query = 'SELECT driver.user, driver.first_name, driver.last_name, driver.driver_id FROM driver INNER JOIN driver_bridge ON driver.driver_id = driver_bridge.driver_id WHERE driver_bridge.sponsor_id = %s AND apply = 1 AND active = 1'
        vals = (self.properties['id'], )

        try: 
            apps = self.database.exec(query, vals)
            #self.database.close()
        except Exception as e:
            raise Exception(e)

        return apps


    def view_drivers(self):
        query = 'SELECT driver.first_name, driver.mid_name, driver.last_name, driver.user, driver_bridge.points, driver.date_join FROM driver INNER JOIN driver_bridge ON driver.driver_id = driver_bridge.driver_id WHERE driver_bridge.sponsor_id = %s AND apply = 0 AND active = 1 ORDER BY driver_bridge.points DESC'
        vals = (self.properties['id'], )

        try: 
            drivers = self.database.exec(query, vals)
            #self.database.close()
        except Exception as e:
            raise Exception(e)

        return drivers


    def accept_application(self, driver_id):
        bridge = 'UPDATE driver_bridge SET apply = 0 WHERE driver_id = %s AND sponsor_id = %s'
        leader = 'INSERT INTO points_leaderboard VALUES (%s, %s, 0)'
        vals = (driver_id, self.properties['id'])

        try: 
            self.database.exec(bridge, vals)
            self.database.exec(leader, vals)
            #self.database.close()
        except Exception as e:
            raise Exception(e)
    
    def decline_application(self, driver_id):
        query = 'DELETE FROM driver_bridge WHERE driver_id = %s AND sponsor_id = %s'
        vals = (driver_id, self.properties['id'])

        try: 
            self.database.exec(query, vals)
            #self.database.close()
        except Exception as e:
            raise Exception(e)

    def add_points(self, driver_id, add_points):
        #self.database = getNewConnection()

        data = self.database.exec('SELECT points FROM driver_bridge WHERE driver_id = %s AND sponsor_id = %s AND apply = 0', (driver_id, self.properties['id']))
        #self.database.close()
        current_points = data[0][0]

        current_points += add_points

        query = 'UPDATE driver_bridge SET points = %s WHERE driver_id = %s AND sponsor_id = %s'
        vals = (current_points, driver_id, self.properties['id'])
        try: 
            self.database.exec(query, vals)
            self.database.commit()
        except Exception as e:
            raise Exception(e)

        data = self.database.exec('SELECT points FROM points_leaderboard WHERE driver_id = %s AND sponsor_id = %s', (driver_id, self.properties['id']))
        current_points = data[0][0]

        current_points += add_points
        vals = (current_points, driver_id, self.properties['id'])
        
        leader = 'UPDATE points_leaderboard SET points = %s WHERE driver_id = %s AND sponsor_id = %s'
        try: 
            self.database.exec(leader, vals)
            self.database.close()
        except Exception as e:
            raise Exception(e)

    def view_leaderboard(self):
        query = 'SELECT driver.first_name, driver.mid_name, driver.last_name, driver.user, points_leaderboard.points FROM driver INNER JOIN points_leaderboard ON driver.driver_id = points_leaderboard.driver_id WHERE sponsor_id = %s  AND active = 1 ORDER BY points_leaderboard.points DESC'
        val = (self.properties['id'], )

        try: 
            leaders = self.database.exec(query, val)
            #self.database.close()
        except Exception as e:
            raise Exception(e)

        return leaders


    def remove_driver(self, driver_id):
        query = 'DELETE FROM driver_bridge WHERE driver_id = %s AND sponsor_id = %s'
        remove_leader = 'DELETE FROM points_leaderboard WHERE driver_id = %s and sponsor_id = %s'
        vals = (driver_id, self.properties['id'])

        try: 
            self.database.exec(query, vals)
            self.database.exec(remove_leader, vals)
            #self.database.close()
        except Exception as e:
            raise Exception(e)

    def get_inbox_list(self):
        message_query = 'SELECT * FROM messages WHERE (target = %s AND seent = 0) OR (sender = %s AND seens = 0) '
        vals = (self.properties['user'], self.properties['user'])

        try:
            data = self.database.exec(message_query, vals)
            #self.database.close()
        except Exception as e:
            raise Exception(e)

        user_list = []
        if data:
            for d in data:
                if (d[0] not in user_list) and (d[0] != self.properties['user']):
                    user_list.append(d[0])
                elif (d[1] not in user_list) and (d[1] != self.properties['user']):                       
                    user_list.append(d[1])

        return user_list

    def messages_are_seen(self, user):
        if user == "MARK_ALL":
            query = 'UPDATE messages SET seens = 1 WHERE sender = %s'
            query2 = 'UPDATE messages SET seent = 1 WHERE target = %s'
            val = (self.properties['user'], )
            try:
                self.database.exec(query, val)
                self.database.exec(query2, val)
                #self.database.close()
            except Exception as e:
                raise Exception(e)
        else:
            query = 'UPDATE messages SET seent = 1 WHERE (target = %s AND sender = %s)'
            query2 = 'UPDATE messages SET seens = 1 WHERE (target = %s AND sender = %s)'
            val1 = (self.properties['user'], user)
            val2 = (user, self.properties['user'])
            try:
                self.database.exec(query, val1)
                self.database.exec(query2, val2)
                #self.database.close()
            except Exception as e:
                raise Exception(e)



    def get_msg_info(self, user):
        sql = 'SELECT Driver_ID, Sponsor_ID, Admin_ID FROM users WHERE UserName = %s'
        val = (user, )
        id = self.database.exec(sql, val)
        if id[0][0] != None:
            role =  'driver'
        elif id[0][1] != None:
            role =  'sponsor'
        else:
            role = 'admin'
        
        if role == 'driver' or role == 'admin':
            query = 'SELECT first_name, last_name, active FROM ' + role + ' WHERE user = %s'
        else:
            query = 'SELECT title, active FROM sponsor WHERE user = %s'
        val = (user, )
        
        try:
            data = self.database.exec(query, val)
            #self.database.close()
        except Exception as e:
            raise Exception(e)

        data_list = list(data[0])
        data_list.insert(0, role)
        return data_list


    def view_messages(self):
        message_query = 'SELECT * FROM messages WHERE target = %s OR sender = %s ORDER BY time ASC'
        vals = (self.properties['user'], self.properties['user'])

        try:
            data = self.database.exec(message_query, vals)
            #self.database.close()
        except Exception as e:
            raise Exception(e)

        message_dict = {}

        if data:
            for d in data:
                user_list = list(message_dict.keys())
                if (d[0] not in user_list) and (d[0] != self.properties['user']):
                    message_dict[d[0]] = []
                    #get info about user from database
                    info = self.get_msg_info(d[0])
                    #if user is inactive add disabled tag to their last name and remove the tag from the list
                    if info[len(info) - 1] == 0:
                        info[len(info) - 2] += '(Disabled)'
                    info.pop(len(info) - 1)
                    message_dict[d[0]].append(info)
                    user = 0
                elif (d[1] not in user_list) and (d[1] != self.properties['user']):
                    message_dict[d[1]] = []
                    info = self.get_msg_info(d[1])
                    if info[len(info) - 1] == 0:
                        info[len(info) - 2] += '(Disabled)'
                    info.pop(len(info) - 1)
                    message_dict[d[1]].append(info)
                    user = 1
                elif(d[0] == self.properties['user'] and d[1] == self.properties['user'] and d[0] not in user_list):
                    message_dict[d[0]] = []
                    info = self.get_msg_info(d[0])
                    if info[len(info) - 1] == 0:
                        info[len(info) - 2] += '(Disabled)'
                    info.pop(len(info) - 1)
                    message_dict[d[0]].append(info)
                    user = 0
                else:
                    if d[0] != self.properties['user']:
                        user = 0
                    else:
                        user = 1
                    
                message_dict[d[user]].insert(1, (d[1], d[2], d[3]))
        
        return message_dict

    def send_message(self, target, message):
        time = 'SET time_zone = \'{}\''.format("America/New_York")
        query = 'INSERT INTO messages VALUES (%s, %s, %s, NOW(), 0, 1)'
        vals = (target, self.properties['user'], message)

        try:
            self.database.exec(time)
            self.database.exec(query, vals)
            #self.database.close()
        except Exception as e:
            raise Exception(e)


    
    def upload_image(self, tempf):
        with open(tempf, 'rb') as file:
            image = file.read()

        sql = 'UPDATE driver SET image = %s WHERE user = %s'
        vals = (image, self.properties['user'])

        try:
            self.database.exec(sql, vals)
            #self.database.close()
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
            self.database.exec(query, vals)
            #self.database.close()
        except Exception as e:
            raise Exception(e)

    def change_password(self, new_pwd):
        query = 'UPDATE sponsor SET pwd = %s WHERE user = %s'
        vals = (new_pwd, self.properties['user'])

        try:
            self.database.exec(query, vals)
            #self.database.close()
        except Exception as e:
            raise Exception(e)


    def delete(self):
        """ Deletes a sponsor from the users table and from the sponsor table """

        query = "UPDATE sponsor SET active = 0 WHERE sponsor_id=%s"
        vals = (self.properties['id'], )
        try:
            self.database.exec(user_query, user_vals)
            self.database.exec(query, vals)
            #self.database.close()
        except Exception as e:
            raise Exception(e)

    def __del__(self):
        global pool1
        self.database.close()
        


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
        self.properties['selectedSponsor'] = None

        self.database = getConnection()

    def setLogIn(self, loggedIn):
        self.loggedIn = loggedIn
        
    def get_next_id(self):
        query = 'SELECT MAX(driver_id) FROM driver'
        rows = self.database.exec(query)
        
        if rows[0][0] == None:
            return 1
        else:
            return rows[0][0] + 1

    def add_user(self):
        self.properties['id'] = self.get_next_id()
        self.properties['END'] = 'NULL'
        self.properties['active'] = 1
        query = 'INSERT INTO driver VALUES (\'{fname}\', \'{mname}\', \'{lname}\', \'{user}\', \'{id}\', \'{address}\', \'{phone}\', \'{email}\', \'{pwd}\', NOW(), \'{END}\', \'{image}\', \'{active}\')'.format(**self.properties)

        try:
            self.database.exec(query)
            self.add_to_users()
            #self.database.close()

        except Exception as e:
            raise Exception(e)

    def check_password(self, pwd_hash):
        query = "SELECT pwd FROM driver WHERE user=%s"
        db_pwd = self.database.exec(query, self.properties['user'])
        #self.database.close()
        return check_password_hash(pwd_hash, db_pwd)

    def check_username_available(self):
        query = "SELECT COUNT(*) FROM users WHERE UserName=\"{}\"".format(self.properties['user'])

        out = self.database.exec(query) 
        #self.database.close()

        return out[0][0] == 0 or out == None

    def get_current_id(self):
        query = "SELECT driver_id FROM driver WHERE email=\"{}\" AND user=\"{}\""
        query = query.format(self.properties['email'], self.properties['user'])

        try:
            d_id = self.database.exec(query)
            #self.database.close()
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
            self.database.exec(query, args=tuple(data.values()))
            #self.database.close()

        except Exception as e:
            raise Exception(e)

    def get_users(self):
        main_query = "SELECT first_name, mid_name, last_name, user, date_join, driver_id FROM driver where active = 1"
        try:
            out = self.database.exec(main_query)
            #self.database.close()
        except Exception as e:
            raise Exception(e)

        final_list = []

        for driver in out:
            sponsors = 'SELECT sponsor_id, points FROM driver_bridge WHERE driver_id = %s and apply = 0'
            val = (driver[5], )
            try:
                sponsor = self.database.exec(sponsors, val)
                #self.database.close()
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
            username = self.database.exec(query, val)
            #self.database.close()
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
            data = self.database.exec(query, val)
            #self.database.close()
            return data

        except Exception as e:
            raise Exception(e)

    def add_to_users(self):
        query = 'INSERT INTO users (Username, {}, last_in) VALUES (\'{}\', {}, CURRENT_TIMESTAMP())'
        query = query.format("Driver_ID", self.properties['user'], self.properties['id'])
        self.database.exec(query)
        #self.database.close()

    def getSponsorView(self):
        return self.properties['selectedSponsor']

    def setSponsorView(self, view):
        self.properties['selectedSponsor'] = view

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

    #def isActive(self):


    def is_suspended(self):
        
        sql = 'SELECT user FROM suspend WHERE user = %s'
        val = (self.properties['user'], )

        try:
            #this will remove suspended driver's whos suspensions are over
            self.database.exec('DELETE from suspend WHERE date_return <= NOW()')
            suspended_user = self.database.exec(sql, val)
            #self.database.close()
        except Exception as e:
            raise Exception(e)

        if suspended_user == None:
            return False
        else:
            return True


    def populate(self, username: str):
        #Connection()
        query = 'SELECT first_name, mid_name, last_name, user, driver_id, address, phone, email, image, date_join FROM driver WHERE user = %s'
        vals = (username, )

        try:
            data = self.database.exec(query, vals)
            #self.database.close()

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
            spon_list = self.view_sponsors()
            if not spon_list:
                sponsorid = None
                points = None
            else:
                sponsorid = spon_list[0][0]
                points = spon_list[0][1]

            if sponsorid:
                self.properties['selectedSponsor'] = [sponsorid, points]
            else:
                self.properties['selectedSponsor'] = None

            query = 'SELECT sponsor_id, points FROM driver_bridge WHERE driver_id = %s AND apply = 0'
            vals = (self.properties['id'], )

            try:
                data = self.database.exec(query, vals)
                #self.database.close()
            except Exception as e:
                raise Exception(e)

            for d in data:
                sponsor_id = '{}'.format(d[0])
                self.properties['sponsors'][sponsor_id] = d[1] 

            if self.properties['selectedSponsor'] is not None:
                id = next(iter(self.properties['sponsors']))
                points = self.properties['sponsors'].get(id)
                self.properties['selectedSponsor'] = [id, points]
                


    def apply_to_sponsor(self, sponsor_id):
        query = 'INSERT INTO driver_bridge VALUES (%s, %s, %s, %s)'
        vals = (self.properties['id'], sponsor_id, 0, 1)

        try:
            self.database.exec(query, vals)
            #self.database.close()
        except Exception as e:
            raise Exception(e)

    def get_inbox_list(self):
        message_query = 'SELECT * FROM messages WHERE (target = %s AND seent = 0) OR (sender = %s AND seens = 0) '
        vals = (self.properties['user'], self.properties['user'])

        try:
            data = self.database.exec(message_query, vals)
            #self.database.close()
        except Exception as e:
            raise Exception(e)

        user_list = []
        if data:
            for d in data:
                if (d[0] not in user_list) and (d[0] != self.properties['user']):
                    user_list.append(d[0])
                elif (d[1] not in user_list) and (d[1] != self.properties['user']):                       
                    user_list.append(d[1])

        return user_list

    def messages_are_seen(self, user):
        if user == "MARK_ALL":
            query = 'UPDATE messages SET seens = 1 WHERE sender = %s'
            query2 = 'UPDATE messages SET seent = 1 WHERE target = %s'
            val = (self.properties['user'], )
            try:
                self.database.exec(query, val)
                self.database.exec(query2, val)
                #self.database.close()
            except Exception as e:
                raise Exception(e)
        else:
            query = 'UPDATE messages SET seent = 1 WHERE (target = %s AND sender = %s)'
            query2 = 'UPDATE messages SET seens = 1 WHERE (target = %s AND sender = %s)'
            val1 = (self.properties['user'], user)
            val2 = (user, self.properties['user'])
            try:
                self.database.exec(query, val1)
                self.database.exec(query2, val2)
                #self.database.close()
            except Exception as e:
                raise Exception(e)


    def get_msg_info(self, user):
        sql = 'SELECT Driver_ID, Sponsor_ID, Admin_ID FROM users WHERE UserName = %s'
        val = (user, )
        id = self.database.exec(sql, val)

        if id[0][0] != None:
            role =  'driver'
        elif id[0][1] != None:
            role =  'sponsor'
        else:
            role = 'admin'
        
        if role == 'driver' or role == 'admin':
            query = 'SELECT first_name, last_name, active FROM ' + role + ' WHERE user = %s'
        else:
            query = 'SELECT title, active FROM sponsor WHERE user = %s'
        val = (user, )
        
        try:
            data = self.database.exec(query, val)
            #self.database.close()
        except Exception as e:
            raise Exception(e)

        data_list = list(data[0])
        data_list.insert(0, role)
        return data_list


    def view_messages(self):
        message_query = 'SELECT * FROM messages WHERE target = %s OR sender = %s ORDER BY time ASC'
        vals = (self.properties['user'], self.properties['user'])

        try:
            data = self.database.exec(message_query, vals)
            #self.database.close()
        except Exception as e:
            raise Exception(e)

        message_dict = {}

        if data:
            for d in data:
                user_list = list(message_dict.keys())
                if (d[0] not in user_list) and (d[0] != self.properties['user']):
                    message_dict[d[0]] = []
                    #get info about user from database
                    info = self.get_msg_info(d[0])
                    #if user is inactive add disabled tag to their last name and remove the tag from the list
                    if info[len(info) - 1] == 0:
                        info[len(info) - 2] += '(Disabled)'
                    info.pop(len(info) - 1)
                    message_dict[d[0]].append(info)
                    user = 0
                elif (d[1] not in user_list) and (d[1] != self.properties['user']):
                    message_dict[d[1]] = []
                    info = self.get_msg_info(d[1])
                    if info[len(info) - 1] == 0:
                        info[len(info) - 2] += '(Disabled)'
                    info.pop(len(info) - 1)
                    message_dict[d[1]].append(info)
                    user = 1
                elif(d[0] == self.properties['user'] and d[1] == self.properties['user'] and d[0] not in user_list):
                    message_dict[d[0]] = []
                    info = self.get_msg_info(d[0])
                    if info[len(info) - 1] == 0:
                        info[len(info) - 2] += '(Disabled)'
                    info.pop(len(info) - 1)
                    message_dict[d[0]].append(info)
                    user = 0
                else:
                    if d[0] != self.properties['user']:
                        user = 0
                    else:
                        user = 1
                    
                message_dict[d[user]].insert(1, (d[1], d[2], d[3]))
        
        return message_dict

    def send_message(self, target, message):
        time = 'SET time_zone = \'{}\''.format("America/New_York")
        query = 'INSERT INTO messages VALUES (%s, %s, %s, NOW(), 0, 1)'
        vals = (target, self.properties['user'], message)

        try:
            self.database.exec(time)
            self.database.exec(query, vals)
            #self.database.close()
        except Exception as e:
            raise Exception(e)
    
    def upload_image(self, tempf):
        with open(tempf, 'rb') as file:
            image = file.read()

        sql = 'UPDATE driver SET image = %s WHERE user = %s'
        vals = (image, self.properties['user'])

        try:
            self.database.exec(sql, vals)
            #self.database.close()
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
            self.database.exec(query, vals)
            #self.database.close()
        except Exception as e:
            raise Exception(e)

    def delete(self):
        """ Deletes a driver from the users table and from the driver table """

        query = "UPDATE driver SET active = 0 WHERE driver_id=%s"
        vals = (self.properties['id'], )
        try:
            self.database.exec(user_query, user_vals)
            self.database.exec(query, vals)
            #self.database.close()
        except Exception as e:
            raise Exception(e)

    def __del__(self):
        global pool1
        self.database.close()
        


