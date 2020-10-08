try:
    from .db_connection import DB_Connection
except Exception:
    from app.database.db_connection import DB_Connection

import os
from abc import ABC
from abc import abstractmethod
from werkzeug.security import check_password_hash

class AbsUser(ABC):
    DB_HOST = os.getenv('DB_HOST')
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASS = os.getenv('DB_PASS')
    role = ''
    user = ''
    id = -1

    def __init__(self):
        self.database = DB_Connection(self.DB_HOST, self.DB_NAME, 
                                      self.DB_USER, self.DB_PASS)

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
    def add_to_users(self, username: str, id: int, role: str):
        
        if role == 'driver':
            role = "Driver_ID"
        elif role == 'sponsor':
            role = "Sponsor_ID"
        else:
            role = "Admin_ID"

        query = 'INSERT INTO users (Username, {}, last_in) VALUES (\'{}\', {}, CURRENT_TIMESTAMP())'
        query = query.format(role, username, id)
        self.database.insert(query)

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

        
        
class Admin(AbsUser):
    def __init__(self, fname='NULL', mname='NULL', lname='NULL', user='NULL', 
                 phone='NULL', email='NULL', pwd='NULL', image='NULL'):
        self.properties = {}
        self.properties['fname'] = fname
        self.properties['mname'] = mname
        self.properties['lname'] = lname
        self.properties['user'] = user
        self.properties['id'] = self.get_next_id()
        self.properties['phone'] = phone
        self.properties['email'] = email
        self.properties['pwd'] = pwd
        self.properties['image'] = image
        self.properties['date_join'] = 'NULL'

        self.suspension = False
        self.role = 'admin'

        self.database = DB_Connection(self.DB_HOST, self.DB_NAME, 
                                      self.DB_USER, self.DB_PASS)

    def get_next_id(self):
        query = 'SELECT MAX(admin_id) FROM admin'
        rows = self.database.query(query)
        
        if rows[0][0] == None:
            return 1
        else:
            return rows[0][0] + 1

    def add_user(self):
        query = 'INSERT INTO admin VALUES (%(fname)s, %(mname)s, %(lname)s, %(user)s, %(id)s, %(phone)s, %(email)s, %(pwd)s, NOW(), %(END)s)'

        try:
            self.database.insert(query, params=self.properties)
            self.add_to_users(self.properties['user'], self.properties['id'], role)
            self.database.commit()

        except Exception as e:
            raise Exception(e)

    def check_password(self, pwd_hash):
        query = "SELECT pwd FROM admin WHERE user=%s"
        db_pwd = self.database.query(query, self.properties['user'])

        return check_password_hash(pwd_hash, db_pwd)

    def check_username_available(self, username):
        query = "SELECT COUNT(*) FROM admin WHERE user=\"{}\"".format(self.properties['user'])

        out = self.database.query(query) 
        print(out)
        return out[0][0] == 0

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
        pass

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
        super().add_to_users(self.properties['user'], self.properties['id'], self.role)

    def getUsername(self):
        return self.properties['user']
    
    def getRole(self):
        return self.role

    def getPoints(self):
        return 999999

    def populate(self, username: str):
        query = 'SELECT first_name, mid_name, last_name, user, admin_id, phone, email, date_join FROM admin WHERE user = %s'
        vals = (username, )

        try:
            data = self.database.query(query, vals)

        except Exception as e:
            raise Exception(e)

        self.properties['fname'] = data[0][0]
        self.properties['mname'] = data[0][1]
        self.properties['lname'] = data[0][1]
        self.properties['user'] = data[0][3]
        self.properties['id'] = data[0][4]
        self.properties['phone'] = data[0][5]
        self.properties['email'] = data[0][6]
        self.properties['pwd'] = 'NULL'
        self.properties['date_join'] = data[0][7]

        self.suspension = False
        self.role = 'admin'

        
        

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
        self.properties['id'] = self.get_next_id()
        self.properties['date_join'] = 'NULL'

        self.suspension = False
        self.role = 'sponsor'

        self.database = DB_Connection(self.DB_HOST, self.DB_NAME, 
                                      self.DB_USER, self.DB_PASS)

    
    def get_next_id(self):
        query = 'SELECT MAX(sponsor_id) FROM sponsor'
        rows = self.database.query(query)
        
        if rows[0][0] == None:
            return 1
        else:
            return rows[0][0] + 1
    
    def add_user(self):
        query = 'INSERT INTO sponsor VALUES (%(title)s, %(user)s, %(id)s, %(address)s, %(phone)s, %(email)s, %(pwd)s, %(image)s, NOW(), %(END)s)'
        self.properties['END'] = 'NULL'

        try:
            self.database.insert(query, params=self.properties)
            self.add_to_users(self.properties['user'], self.properties['id'], role)
            self.database.commit()

        except Exception as e:
            raise Exception(e)

    def check_password(self, pwd_hash):
        query = "SELECT pwd FROM sponsor WHERE user=%s"
        db_pwd = self.database.query(query, self.properties['user'])

        return check_password_hash(pwd_hash, db_pwd)


    def check_username_available(self):
        query = "SELECT COUNT(*) FROM sponsor WHERE user=\"{}\"".format(self.properties['user'])

        out = self.database.query(query) 
        print(out)
        return out[0][0] == 0

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
        super().add_to_users(self.properties['user'], self.properties['id'], self.role)

    def getUsername(self):
        return self.properties['user']
    
    def getRole(self):
        return self.role

    def getPoints(self):
        return 999999

    def populate(self, username: str):
        query = 'SELECT title, user, sponsor_id, address, phone, email, image, date_join FROM sponsor WHERE user = %s'
        vals = (username, )

        try:
            data = self.database.query(query, vals)

        except Exception as e:
            raise Exception(e)

        self.properties['title'] = data[0][0]
        self.properties['user'] = data[0][1]
        self.properties['id'] = data[0][2]
        self.properties['address'] = data[0][3]
        self.properties['phone'] = data[0][4]
        self.properties['email'] = data[0][5]
        self.properties['pwd'] = 'NULL'
        self.properties['image'] = data[0][6]
        self.properties['date_join'] = data[0][7]

        self.suspension = False

class Driver(AbsUser):
    def __init__(self, fname='NULL', mname='NULL', lname='NULL', user='NULL', 
                 address='NULL', phone='NULL', email='NULL', pwd='NULL', image='NULL'):
        # Dictionary to keep track of driver data
        self.properties = {}
        self.properties['fname'] = fname
        self.properties['mname'] = mname
        self.properties['lname'] = lname
        self.properties['user'] = user
        self.properties['id'] = self.get_next_id()
        self.properties['sponsor_id'] = 0
        self.properties['points'] = 0
        self.properties['address'] = address
        self.properties['phone'] = phone
        self.properties['email'] = email
        self.properties['pwd'] = pwd
        self.properties['image'] = image
        self.properties['date_join'] = 'NULL'

        self.suspension = False
        self.role = 'driver'

        self.database = DB_Connection(self.DB_HOST, self.DB_NAME, 
                                      self.DB_USER, self.DB_PASS)

    def get_next_id(self):
        query = 'SELECT MAX(driver_id) FROM driver'
        rows = self.database.query(query)
        
        if rows[0][0] == None:
            return 1
        else:
            return rows[0][0] + 1

    def add_user(self):
        query = 'INSERT INTO driver VALUES (%(fname)s, %(mname)s, %(lname)s, %(user)s, %(id)s, %(sponsor_id)s, %(points)s, %(address)s, %(phone)s, %(email)s, %(pwd)s, %(image)s, NOW(), %(END)s)'
        self.properties['END'] = 'NULL'

        try:
            self.database.insert(query, params=self.properties)
            self.add_to_users(self.properties['user'], self.properties['id'], self.role)
            self.database.commit()

        except Exception as e:
            raise Exception(e)

    def check_password(self, pwd_hash):
        query = "SELECT pwd FROM driver WHERE user=%s"
        db_pwd = self.database.query(query, self.properties['user'])

        return check_password_hash(pwd_hash, db_pwd)

    def check_username_available(self):
        query = "SELECT COUNT(*) FROM driver WHERE user=\"{}\"".format(self.properties['user'])

        out = self.database.query(query) 
        print(out)
        return out[0][0] == 0

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

    # Add items to update in query and add in WHERE to find correct user
        query += ", ".join(q_list) + " WHERE user=\"{}\"".format(username)

        try:
            self.database.query(query, params=tuple(data.values()))
            self.database.commit()

        except Exception as e:
            raise Exception(e)

    def get_users(self):
        query = "SELECT * FROM driver"

        try:
            out = self.database.query(query)
            return out
        except Exception as e:
            raise Exception(e)
    
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
        super().add_to_users(self.properties['user'], self.properties['id'], self.role)

    def getUsername(self):
        return self.properties['user']
    
    def getRole(self):
        return self.role

    def getPoints(self):
        return self.properties['points']
    
    def getSponsor(self):
        return self.properties['sponsor_id']

    def populate(self, username: str):
        query = 'SELECT first_name, mid_name, last_name, user, driver_id, sponsor_id, points, address, phone, email, image, date_join FROM driver WHERE user = %s'
        vals = (username, )

        try:
            data = self.database.query(query, vals)

        except Exception as e:
            raise Exception(e)

        self.properties['fname'] = data[0][0]
        self.properties['mname'] = data[0][1]
        self.properties['lname'] = data[0][2]
        self.properties['user'] = data[0][3]
        self.properties['id'] = data[0][4]
        self.properties['sponsor_id'] = data[0][5]
        self.properties['points'] = data[0][6]
        self.properties['address'] = data[0][7]
        self.properties['phone'] = data[0][8]
        self.properties['email'] = data[0][9]
        self.properties['pwd'] = 'NULL'
        self.properties['image'] = data[0][10]
        self.properties['date_join'] = data[0][11]

        self.suspension = False
