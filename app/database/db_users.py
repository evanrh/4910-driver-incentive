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
            role = "Driver_ID
        elif role == 'sponsor':
            role = "Sponsor_ID"
        else:
            role = "Admin_ID"

        query = 'INSERT INTO users (Username, {}, last_in) VALUES (\'{}\', {}, CURRENT_TIMESTAMP())'
        query = query.format(role, user, id)
        self.database.insert(query)

        
        
class Admin(AbsUser):
    def __init__(self, fname='NULL', mname='NULL', lname='NULL', user='NULL', 
                 phone='NULL', email='NULL', pwd='NULL', image='NULL'):
        self.properties = {}
        self.properties['fname'] = fname
        self.properties['mname'] = mname
        self.properties['lname'] = lname
        self.properties['user'] = user
        self.properties['phone'] = phone
        self.properties['email'] = email
        self.properties['pwd'] = pwd
        self.properties['image'] = image

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
        query = 'INSERT INTO admin VALUES ({}, {}, {}, {}, {}, {}, {}, {}, NOW(), {}'
        query = query.format(*list(self.properties.values()))

        # TODO Clean up admin signup
        add_query = 'INSERT INTO users (UserName, Admin_ID, last_in) (%s, %s, CURRENT_TIMESTAMP())'
        vals = (self.properties['name'])
        try:
            

        except Exception as e:
            raise Exception(e)

    def check_password(self, pwd_hash):
        pass

    def check_username_available(self, username):
        pass

    def get_users(self):
        pass

class Sponsor(AbsUser):
    role = 'sponsor'
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
        self.properties['sponsor_id'] = self.get_next_id()

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
        query = 'INSERT INTO sponsor VALUES (%(title)s, %(user)s, %(sponsor_id)s, %(address)s, %(phone)s, %(email)s, %(pwd)s, %(image)s, NOW(), %(END)s)'
        self.properties['END'] = 'NULL'

        try:
            self.database.insert(query, params=self.properties)
            self.add_to_users(self.properties['user'], self.properties['sponsor_id'], role)
            self.database.commit()

        except Exception as e:
            raise Exception(e)

    def check_password(self, pwd_hash):
        query = "SELECT pwd FROM sponsor WHERE user=%s"
        db_pwd = self.database.query(query, self.properties['user'])

        return check_password_hash(pwd_hash, db_pwd)


    def check_username_available(self):
        query = "SELECT COUNT(*) FROM sponsor WHERE user=\"{}\"".format(self.properties['user'])
        print(query)

        out = self.database.query(query) 
        print(out)
        return out[0][0] == 0

    def update_info(self, data: dict):
        
        query = "UPDATE sponsor SET "

        q_list = []
        for key in data.keys():
            q_list.append("{} = %s".format(key))

        query += ", ".join(q_list) + " WHERE user=\"{}\"".format(self.properties['user'])
        print(query)

        try:
            self.database.query(query, params=list(data.values()))
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

class Driver(AbsUser):
    role = 'driver'
    def __init__(self, fname='NULL', mname='NULL', lname='NULL', user='NULL', 
                 address='NULL', phone='NULL', email='NULL', pwd='NULL', image='NULL'):
        # Dictionary to keep track of driver data
        self.properties = {}
        self.properties['fname'] = fname
        self.properties['mname'] = mname
        self.properties['lname'] = lname
        self.properties['user'] = user
        self.properties['address'] = address
        self.properties['phone'] = phone
        self.properties['email'] = email
        self.properties['pwd'] = pwd
        self.properties['image'] = image

        self.database = DB_Connection(self.DB_HOST, self.DB_NAME, 
                                      self.DB_USER, self.DB_PASS)

        self.properties['driver_id'] = self.get_current_id()

    def get_next_id(self):
        query = 'SELECT MAX(driver_id) FROM driver'
        rows = self.database.query(query)
        
        if rows[0][0] == None:
            return 1
        else:
            return rows[0][0] + 1

    def add_user(self):
        self.properties['driver_id'] = self.get_next_id()
        query = 'INSERT INTO driver VALUES (%(fname)s, %(mname)s, %(lname)s, %(user)s, %(driver_id)s, 0, 0, %(address)s, %(phone)s, %(email)s, %(pwd)s, %(image)s, NOW(), %(END)s)'
        self.properties['END'] = 'NULL'

        """add_query = 'INSERT INTO users (UserName, Driver_ID, last_in) VALUES (%s, %s, CURRENT_TIMESTAMP())'
        vals = (self.properties['user'], self.properties['driver_id'])"""

        try:
            self.database.insert(query, params=self.properties)
            self.add_to_users(self.properties['user'], self.properties['driver_id'], role)
            self.database.commit()

        except Exception as e:
            raise Exception(e)

    def check_password(self, pwd_hash):
        query = "SELECT pwd FROM driver WHERE user=%s"
        db_pwd = self.database.query(query, self.properties['user'])

        return check_password_hash(pwd_hash, db_pwd)

    def check_username_available(self):
        query = "SELECT COUNT(*) FROM driver WHERE user=\"{}\"".format(self.properties['user'])
        print(query)

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
                each key is a named attribute of driver, and is followed by a key that is not None
        """
        
        query = "UPDATE driver SET "

        # Generate list of items to update in query
        q_list = []
        for key in data.keys():
            q_list.append("{} = %s".format(key))

        # Add items to update in query and add in WHERE to find correct user
        query += ", ".join(q_list) + " WHERE user=\"{}\"".format(self.properties['user'])
        print(query)

        try:
            self.database.query(query, params=list(data.values()))
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
