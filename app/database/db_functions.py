import mysql.connector
import datetime

#establish connection
database = mysql.connector.connect(
    host = 'cpsc4910.crxd6v3fbudk.us-east-1.rds.amazonaws.com',
    user = 'admin',
    password = 'cpsc4910',
    database = 'website'
)

#cursor for the database
cursor = database.cursor()

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
    if( row == None or row[0] == None ):
        return False
    else:
        return True

#returns id and table that the user is in
def get_table_id(user):
    sql = 'SELECT Driver_ID, Sponsor_ID, Admin_ID FROM users WHERE UserName = %s'
    val = (user, )
    cursor.execute(sql, val)
    id = cursor.fetchone()
    if id[0] != None:
        return id[0], 'driver'
    elif id[1] != None:
        return id[1], 'sponsor'
    else:
        return id[2], 'admin'


#checks to see if the password entered by the user matches password with that username
#searches through user table for username and role
#uses role to search through specific table for username and password
#returns true if the password entered mathches the one in the table
def pwd_check(user = 'NULL', pwd = 'NULL'):
    if( user == 'NULL' or pwd == 'NULL'):
        return False

    id, table = get_table_id(user)
    
    sql = 'SELECT pwd FROM ' + table + ' WHERE user = %s'
    val = (user, )
    cursor.execute(sql, val)
    current_password = cursor.fetchone()

    if pwd == current_password[0]:
        return True
    else: 
        return False

#changes the password for a user
#any username of any role can be passed into this function
def change_password(user, pwd):
    id, table = get_table_id(user)

    sql = 'UPDATE ' + table + ' SET pwd = %s WHERE user = %s'
    val = (pwd, user)
    cursor.execute(sql, val)

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

#this function updates the last log in time of the user
#will set the time to the current time the user logs in
def update_last_log_in(user):

    sql = 'UPDATE users SET last_in = CURRENT_TIMESTAMP() WHERE UserName = %s'
    val = (user, )
    cursor.execute(sql, val)
    #database.commit()



#this function removes the association between a driver and sponsor
def remove_driver_from_sponsor(driver_username):

    sql = 'UPDATE driver SET sponsor_id = 0 WHERE user = %s'
    val = (driver_username, )

    cursor.execute(sql, val)
    #database.commit()

#this function adds a driver to a suspension list and their length of suspension
def suspend_driver(driver_username, year, month, day):

    cursor.execute('SELECT driver_id, sponsor_id FROM driver WHERE user = %s', (driver_username, ))
    id = cursor.fetchall()

    if month < 10:
        month = '0' + str(month)
    else:
        month = str(month)

    year = str(year)
    day = str(day)
    
    str_date = year + '-' + month + '-' + day

    sql = 'INSERT INTO suspend VALUES (%s, %s, %s, %s)'
    val = (driver_username, id[0][0], id[0][1], str_date)
    cursor.execute(sql, val)
    #database.commit()

#this function returns true if a driver is currently suspended
def is_driver_suspended(user):
    
    #this will remove suspended driver's whos suspensions are over
    cursor.execute('DELETE from suspend WHERE date_return <= NOW()')
    #database.commit()

    sql = 'SELECT user FROM suspend WHERE user = %s'
    val = (user, )
    cursor.execute(sql, val)
    suspended_user = cursor.fetchone()
    if suspended_user == None:
        return False
    else:
        return True
           
#this function edits the suspension date of the driver
def edit_driver_suspension(user, year, month, day):

    #delete the driver from the suspended table and add them back with new dates
    cursor.execute('DELETE FROM suspend WHERE user = %s', (user, ))
    suspend_driver(user, year, month, day)

#this function cancels a driver's suspension
def cancel_suspension(user):
    cursor.execute('DELETE FROM suspend WHERE user = %s', (user, ))

def view_point_leaders(sponsor_id):
    
    sql = 'SELECT first_name, mid_name, last_name, user, driver_id, points, image, date_join'
    sql += ' FROM driver WHERE sponsor_id = %s ORDER BY points DESC'
    val = (sponsor_id, )
    cursor.execute(sql, val)
    drivers = cursor.fetchall()
    return drivers

def add_points_to_driver(driver_username, sponsor_id, points_to_add):

    sql = 'SELECT points FROM driver WHERE (user = %s AND sponsor_id = %s)'
    val = (driver_username, sponsor_id)
    cursor.execute(sql, val)
    current_points = cursor.fetchone()

    points_to_add += current_points[0]

    sql = 'UPDATE driver SET points = %s WHERE (user = %s AND sponsor_id = %s)'
    val = (points_to_add, driver_username, sponsor_id)
    cursor.execute(sql, val)
    #database.commit()

def sponsorless_drivers():
    
    sql = 'SELECT first_name, mid_name, last_name, user, driver_id, points, image, date_join '
    sql += 'FROM driver WHERE sponsor_id = 0'
    cursor.execute(sql)
    return cursor.fetchall()

def assign_driver_to_sponsor(driver_username, sponsor_id):

    sql = 'UPDATE driver SET sponsor_id = %s WHERE user = %s'
    val = (sponsor_id, driver_username)
    cursor.execute(sql, val)
    #database.commit()

def add_points_for_leading_drivers(sponsor_id, first, second, third):
    sql = 'SELECT COUNT(*) FROM driver WHERE sponsor_id = %s'
    val = (sponsor_id, )
    cursor.execute(sql, val)
    count = cursor.fetchone()[0]

    sql = 'SELECT user FROM driver WHERE sponsor_id = %s ORDER BY points DESC LIMIT 3'

    val = (sponsor_id, )
    cursor.execute(sql, val)
    drivers = cursor.fetchall()

    if count > 2:
        add_points_to_driver(drivers[2][0], sponsor_id, third)
    if count > 1:
        add_points_to_driver(drivers[1][0], sponsor_id, second)
    if count > 0:
        add_points_to_driver(drivers[0][0], sponsor_id, first)
    
    

#main used to test functions
if __name__ == "__main__":
    add_driver('Kevin', 'NULL', 'Rodgers', 'krod', 'address', 5, 'email', 'cool', 'Null')
    add_driver('Bean', 'NULL', 'Rodgers', 'bean', 'address', 5, 'email', 'cool', 'Null')
    add_sponsor('Sponsor', 'spon', 'add', 0, 'email', 'pwd', '')
    add_admin('Admin', '', 'Cool', 'admin', 0, 'email', 'pwd', '')
    print(if_username_exist('krod'))
    get_users()

    drivers = sponsorless_drivers()
    for row in drivers:
        print(str(row[3]) +' is sponsorless')
    assign_driver_to_sponsor('krod', 1)
    assign_driver_to_sponsor('bean', 1)
    
    add_points_to_driver('krod', 1, 50)
    add_points_to_driver('bean', 1, 100)
    drivers = view_point_leaders(1)
    print(str(drivers[0][3]) + ': ' + str(drivers[0][5]))
    print(str(drivers[1][3]) + ': ' + str(drivers[1][5]))

    print("Add 200 to bean for being in top place, 100 to krod for second")

    add_points_for_leading_drivers(1, 200, 100, 50)
    drivers = view_point_leaders(1)
    print(str(drivers[0][3]) + ': ' + str(drivers[0][5]))
    print(str(drivers[1][3]) + ': ' + str(drivers[1][5]))
    

    print('krod\'s password \"cool\": ' + str(pwd_check('krod', 'cool')))
    print('spon\'s password \"password\": ' + str(pwd_check('spon', 'password')))
    print('admin\'s password \"pwd\": ' + str(pwd_check('admin', 'pwd')))

    change_password('krod', 'kool')
    print('krod\'s new password \"kool\": ' + str(pwd_check('krod', 'kool')))
    print("Suspending krod...")
    suspend_driver('krod', 2020, 11, 30)
    print('Is krod suspended: ' + str(is_driver_suspended('krod')))
    
    
    cursor.close()
    database.close()