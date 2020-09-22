import mysql.connector

#establish connection
database = mysql.connector.connect(
    host = 'cpsc4910.crxd6v3fbudk.us-east-1.rds.amazonaws.com',
    user = 'admin',
    password = 'cpsc4910',
    database = 'website'
)

#cursor for the database
cursor = database.cursor(buffered=True)

#having database.commit() commented still allows you to see what it would be like if you 
#modified the database however without commiting you will not change anything in the database

#adds a driver to the database. Parameters are:
#First Name, Middle Name, Last Name, Username, Address, Phone number, email, password and image url
def add_driver(fname = 'NULL', mname = 'NULL', lname = 'NULL', user = 'NULL', address = 'NULL', 
                phone = 0, email = 'NULL', pwd = 'NULL', image = 'NULL'):

    sql = "INSERT INTO driver VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s)"
    driver_id = get_next_driver_id()
    val = (fname, mname, lname, user, driver_id, 0, 0, address, phone, email, pwd, image, "NULL")
    cursor.execute(sql, val)
    add_to_users(user, 'driver', driver_id)
    #database.commit()

#adds a sponsor to the database. Parameters are:
#Title of Sponsor,  Username, Address, Phone number, email, password and image url
def add_sponsor(title = 'NULL', user = 'NULL', address = 'NULL', 
                phone = 0, email = 'NULL', pwd = 'NULL', image = 'NULL'):

    sql = "INSERT INTO sponsor VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s)"
    sponsor_id = get_next_sponsor_id()
    val = (title, user, sponsor_id, address, phone, email, pwd, image, "NULL")
    cursor.execute(sql, val)
    add_to_users(user, 'sponsor', sponsor_id)
    #database.commit()

#adds an admin to the database. Parameters are:
#First Name, Middle Name, Last Name, Username, Phone number, email, password and image url
def add_admin(fname = 'NULL', mname = 'NULL', lname = 'NULL', user = 'NULL',  
                phone = 0, email = 'NULL', pwd = 'NULL', image = 'NULL'):

    sql = "INSERT INTO admin VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s)"
    admin_id = get_next_admin_id()
    val = (fname, mname, lname, user, admin_id, phone, email, pwd, "NULL")
    cursor.execute(sql, val)
    add_to_users(user, 'admin', admin_id)
    #database.commit()

#gets the next available driver id, returns 1 if no drivers exist
def get_next_driver_id():
    cursor.execute("SELECT MAX(driver_id) FROM driver")
    num = cursor.fetchone()

    if( num[0] == None ):
        return 1
    else:
        return num[0] + 1

#gets the next available sponsor id, returns 1 if no sponsor exist
def get_next_sponsor_id():
    cursor.execute("SELECT MAX(sponsor_id) FROM sponsor")
    num = cursor.fetchone()

    if( num[0] == None ):
        return 1
    else:
        return num[0] + 1

#gets the next available admin id, returns 1 if no admin exist
def get_next_admin_id():
    cursor.execute("SELECT MAX(admin_id) FROM admin")
    num = cursor.fetchone()

    if( num[0] == None ):
        return 1
    else:
        return num[0] + 1

#adds the username and role of the user to the user table
#assumes username isn't already in table
#called on by add_driver, add_sponsor, add_admin
def add_to_users(user = 'NULL', role = 'driver', id = 0):
    if( role == 'driver' ):
        sql = "INSERT INTO users (UserName, Driver_ID, last_in) VALUES (%s, %s, CURRENT_TIMESTAMP())"
        val = (user, id)
    elif( role == 'sponsor' ):
        sql = "INSERT INTO users (UserName, Sponsor_ID, last_in) VALUES (%s, %s, CURRENT_TIMESTAMP())"
        val = (user, id)
    else:
        sql = "INSERT INTO users (UserName, Admin_ID, last_in) VALUES (%s, %s, CURRENT_TIMESTAMP())"
        val = (user, id)
    cursor.execute(sql, val)
    #database.commit()

#detirmines if username is in the table
#returns if username is in user table
#false if it isn't
def if_username_exist(user = 'NULL'):
    if( user == 'NULL' ):
        return False

    sql = "SELECT * FROM users WHERE UserName = %s"
    val = (user, )
    cursor.execute(sql, val)
    row = cursor.fetchone()
    if( row[0] == None ):
        return False
    else:
        return True

#checks to see if the password entered by the user matches password with that username
#searches through user table for username and role
#uses role to search through specific table for username and password
#returns true if the password entered mathches the one in the table
def pwd_check(user = 'NULL', pwd = 'NULL'):
    if( user == 'NULL' or pwd == 'NULL'):
        return False

    sql = 'SELECT Driver_ID, Sponsor_ID, Admin_ID FROM users WHERE UserName = %s'
    val = (user, )
    cursor.execute(sql, val)
    id = cursor.fetchone()
    if ( id[0] != None ):
        table = 'driver'
    elif( id[1] != None ):
        table = 'sponsor'
    else:
        table = 'admin'
    
    sql = 'SELECT pwd FROM ' + table + ' WHERE user = %s'
    val = (user, )
    cursor.execute(sql, val)
    current_password = cursor.fetchone()

    if( pwd == current_password[0] ):
        return True
    else: 
        return False

#prints out all of the drivers
def get_drivers():
    cursor.execute("SELECT * FROM driver")
    driver_list = cursor.fetchall()
    for driver in driver_list:
        print(driver)

#prints out all of the sponsors
def get_sponsors():
    cursor.execute("SELECT * FROM sponsor")
    sponsor_list = cursor.fetchall()
    for sponsor in sponsor_list:
        print(sponsor)

#prints out all of the admins
def get_admins():
    cursor.execute("SELECT * FROM admin")
    admin_list = cursor.fetchall()
    for admin in admin_list:
        print(admin)

#prints out all of the users 
def get_users():
    print("---ADMINS---")
    cursor.execute('SELECT UserName, Admin_ID, last_in FROM users WHERE Admin_ID > 0 ORDER BY Admin_ID DESC')
    user_list = cursor.fetchall()
    for user in user_list:
        print(user)
    print("\n---SPONSORS---")
    cursor.execute('SELECT UserName, Sponsor_ID, last_in FROM users WHERE Sponsor_ID > 0 ORDER BY Sponsor_ID DESC')
    user_list = cursor.fetchall()
    for user in user_list:
        print(user)
    print("\n---DRIVERS---")
    cursor.execute('SELECT UserName, Driver_ID, last_in FROM users WHERE Driver_ID > 0 ORDER BY Driver_ID DESC')
    user_list = cursor.fetchall()
    for user in user_list:
        print(user)

#if __name__ == "__main__":
    #add_driver('Kevin', 'NULL', 'Rodgers', 'krod', 'address', 5, 'email', 'cool', 'Null')
    #add_sponsor('Sponsor', 'spon', 'add', 0, 'email', 'pwd', '')
    #add_admin('Admin', '', 'Cool', 'admin', 0, 'email', 'pwd', '')
    #print(if_username_exist('krod'))
    #get_users()
    #print(pwd_check('krod', 'cool'))
    #print(pwd_check('spon', 'password'))
    #print(pwd_check('admin', 'pwd'))

    cursor.close()
    database.close()
    