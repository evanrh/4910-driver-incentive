import mysql.connector
import datetime
from .db_users import getConnection
#establish connection
database = mysql.connector.connect(
    host = 'cpsc4910.crxd6v3fbudk.us-east-1.rds.amazonaws.com',
    user = 'admin',
    password = 'cpsc4910',
    database = 'website'
)

#cursor for the database
cursor = database.cursor(buffered=True)

#having database.commit() commented still allows you to see what 
# it would be like if you 
#modified the database however without commiting you will not change anything in the database

#adds a driver to the database. Parameters are:
#First Name, Middle Name, Last Name, Username, Address, Phone number, email, password and image url
def add_driver(fname = 'NULL', mname = 'NULL', lname = 'NULL', user = 'NULL', address = 'NULL', 
                phone = 0, email = 'NULL', pwd = 'NULL', image = 'NULL'):
    try:
        sql = "INSERT INTO driver VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s, %s)"
        driver_id = get_next_driver_id()
        val = (fname, mname, lname, user, driver_id, 0, 0, address, phone, email, pwd, "NULL", image)
        cursor.execute(sql, val)
        add_to_users(user, 'driver', driver_id)
        #database.commit()
    except Exception as e:
        raise Exception(e)

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
    if role == 'driver':
        role = "Driver_ID"
    elif role == 'sponsor':
        role = "Sponsor_ID"
    else:
        role = "Admin_ID"

    query = 'INSERT INTO users (Username, {}, last_in) VALUES (\'{}\', {}, NOW())'
    query = query.format(role, user, id)
    cursor.execute(query)





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
    cursor.execute('SELECT user, driver_id FROM driver WHERE driver_id > 0 ORDER BY driver_id DESC')
    user_list = cursor.fetchall()
    for user in user_list:
        print(user)
    print("\n---USERS---")
    cursor.execute('SELECT * FROM users ORDER BY Admin_ID DESC, Sponsor_ID DESC, Driver_ID ASC')
    user_list = cursor.fetchall()
    for user in user_list:
        print(user)


           
def get_password(user='NULL'):
    if( user == 'NULL'):
        return ''

    id, table = get_table_id(user)
    
    sql = 'SELECT pwd FROM ' + table + ' WHERE user = %s'
    val = (user, )
    current_password = getConnection().query(sql, val)

    return current_password[0][0]

#detirmines if username is in the table
#returns true if username is in user table
#false if it isn't
def username_exist(user = 'NULL'):
    if( user == 'NULL' ):
        return False

    sql = "SELECT * FROM users WHERE UserName = %s"
    val = (user, )
    row = getConnection().query(sql, val)
    if( row == None or row[0] == None ):
        return False
    else:
        return True

    #returns id and table that the user is in
def get_table_id(user):
    sql = 'SELECT Driver_ID, Sponsor_ID, Admin_ID FROM users WHERE UserName = %s'
    val = (user, )
    id = getConnection().query(sql, val)
    if id[0][0] != None:
        return id[0][0], 'driver'
    elif id[0][1] != None:
        return id[0][1], 'sponsor'
    else:
        return id[0][2], 'admin'


def cancel_suspension(username):
    query = 'DELETE FROM suspend WHERE user = %s'
    vals = (username, )
    try:
        cursor.execute(query, vals)
    except Exception as e:
        raise Exception(e)

#Clean search and translate into sql search
def product_search(search):
    cursor.execute("SELECT DISTINCT Genre FROM product")
    returngenre = cursor.fetchall()
    print(returngenre)
    strgenre = ' '.join(str(v) for v in returngenre)
    strgenre = strgenre.replace("[", "")
    strgenre = strgenre.replace("]", "")
    strgenre = strgenre.replace("(", "") 
    strgenre = strgenre.replace(")", "")
    strgenre = strgenre.replace(",", "")
    strgenre = strgenre.replace("'", "")
    print(strgenre)
    dirty_search = search
    numwords = len(dirty_search.split())
    clean_search = [None] * numwords
    sql = "SELECT name, description FROM product WHERE  available = 1 AND name = '"
    sqlgenre = "SELECT name, description FROM product WHERE  available = 1 AND Genre = '" 
    returninfo = "\n"
    for i in range(numwords):
        clean_search = dirty_search.split(' ')[i]
        clean_search = clean_search.lower()
        if clean_search in strgenre:
            print("Got a genre")
            cursor.execute(sqlgenre + clean_search + "'")                
        else:
            cursor.execute(sql + clean_search + "'")    
        got = cursor.fetchall()
        print("---Product Information---")
        print(got)
        returninfo = returninfo + "\n" +  str(got)
    returninfo = ''.join(str(v) for v in returninfo)
    returninfo = returninfo.replace("[", "")
    returninfo = returninfo.replace("]", "")
    returninfo = returninfo.replace("(", "") 
    returninfo = returninfo.replace(")", "")
#    returninfo = returninfo.replace(",", "")
    returninfo = returninfo.replace("'", "")
    print("Cleaned return----------------") 
    listt = returninfo.splitlines()
#    print(listt[3])
    return listt

def getgenres():
    cursor.execute("SELECT DISTINCT Genre FROM product")
    returngenre = cursor.fetchall()
    print(returngenre)
    strgenre = ' '.join(str(v) for v in returngenre)
    strgenre = strgenre.replace("[", "")
    strgenre = strgenre.replace("]", "")
    strgenre = strgenre.replace("(", "") 
    strgenre = strgenre.replace(")", "")
#    strgenre = strgenre.replace(",", "")
    strgenre = strgenre.replace("'", "")
    return strgenre



#main used to test functions
if __name__ == "__main__":

    cancel_suspension('wsherre')
    if username_exist('krod'):
        add_driver('Kevin', 'NULL', 'Rodgers', 'krod', 'address', 5, 'email', 'cool', 'Null')
    if username_exist('bean'):
        add_driver('Bean', 'NULL', 'Rodgers', 'bean', 'address', 5, 'email', 'cool', 'Null')
    print(is_suspended('krod'))
    add_sponsor('Sponsor', 'spon', 'add', 0, 'email', 'pwd', '')
    add_admin('Admin', '', 'Cool', 'admin', 0, 'email', 'pwd', '')
    print(username_exist('krod'))
    get_users()

    print("David Search\n")
    search = "Bike Tool car"
    product_search(search) 
    


    cursor.close()
    database.close()
    

