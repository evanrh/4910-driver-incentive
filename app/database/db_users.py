try:
    from .db_connection import DB_Connection
except Exception:
    from app.database.db_connection import DB_Connection

import os
from abc import ABC
from abc import abstractmethod

class AbsUser(ABC):
    DB_HOST = os.getenv('DB_HOST')
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASS = os.getenv('DB_PASS')

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
        try:
            self.database.query(query)

        except Exception as e:
            raise Exception(e)

    def check_password(self, pwd_hash):
        pass

    def check_username_available(self, username):
        pass

    def get_users(self):
        pass

class Sponsor(AbsUser):
    def __init__(self):
        pass

class Driver(AbsUser):
    def __init__(self):
        pass
