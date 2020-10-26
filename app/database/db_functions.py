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
    return row

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
    
def getSponsorName(ident):
    ID = str(ident)
    cursor.execute("SELECT user FROM sponsor WHERE sponsor_id = '" +ID+"'")
    got = cursor.fetchall()
    returninfo = ''.join(str(v) for v in got)
    returninfo = returninfo.replace("[", "")
    returninfo = returninfo.replace("]", "")
    returninfo = returninfo.replace("(", "") 
    returninfo = returninfo.replace(")", "")
    returninfo = returninfo.replace(",", "")
    returninfo = returninfo.replace("'", "")
    print(returninfo)
    return returninfo

#Clean search and translate into sql search
def product_search(search, spon_id, mylist, order):
    print(mylist)

    dirty_search = search
    numwords = len(dirty_search.split())
    clean_search = [None] * numwords

    #for loop to add as many spon_ids to search
#    print(spon_id[1])    
    multigenrelong = "SELECT name,price,rating, description FROM product WHERE available = 1 AND ("
    
    for i in spon_id[:-1]:
        multigenrelong += "sponsor_id = '"+ str(i)+"' OR "
    else:
        multigenrelong += "sponsor_id = '"+ str(spon_id[-1])+"' "
    multigenrelong += ")"
    if mylist != "None":
        multigenrelong += " AND ("

    

    #This searches by multiple genres
#    multigenrelong = "SELECT name,price,rating, description FROM product WHERE available = 1 AND ("
    multiOR = " OR "
    multigenre = "Genre ="
    returninfo = "\n"
    searchup = "priceup: ratingup:"
    searchdown = "pricedown: ratingdown:"
    one = 0
    priceup = 0
    pricedown = 0
    ratingup = 0
    ratingdown = 0

    dirty_search.lower()
    if(dirty_search != " "):
        multigenrelong += "name= '"+dirty_search +"' AND "


    print(multigenrelong)
    if order == "priceup":
         priceup = 1
    elif order == "ratingup":
         ratingup = 1
    elif order == "pricedown":
         pricedown = 1
    elif order == "ratingdown":
         ratingdown = 1
    if mylist != "None":
        multigenrelong += "Genre = '" +mylist+"')"
    multigenrelong = multigenrelong.replace(":","")

    if priceup == 1:
        multigenrelong = multigenrelong + " ORDER BY price DESC"
    elif pricedown == 1:
        multigenrelong = multigenrelong + " ORDER BY price ASC"
    elif ratingup == 1:
        multigenrelong = multigenrelong + " ORDER BY rating DESC"
    elif ratingdown == 1:
        multigenrelong = multigenrelong + " ORDER BY rating ASC"    
    print(multigenrelong)
    cursor.execute(multigenrelong) 
    got = cursor.fetchall()
#    print(got)
    returninfo = '\n'.join(str(v) for v in got)
#    print(returninfo)
    returninfo = returninfo.replace("[", "")
    returninfo = returninfo.replace("]", "")
    returninfo = returninfo.replace("(", "") 
    returninfo = returninfo.replace(")", "")
#    returninfo = returninfo.replace(",", "")
    returninfo = returninfo.replace("'", "")
#    print(returninfo)
    listt = returninfo.splitlines()
#    print(listt[1])
    return listt

def getgenres():
    cursor.execute("SELECT DISTINCT Genre FROM product")
    returngenre = cursor.fetchall()
    print(returngenre)
    # Return a list of all genres
    return list(map(lambda x: x[0], returngenre))

def getnumproducts(spon_id):

    sql = "SELECT COUNT(sponsor_id) FROM product WHERE "
    for i in spon_id[:-1]:
        sql += "sponsor_id = '"+ str(i)+"' OR "
    else:
        sql += "sponsor_id = '"+ str(spon_id[-1])+"' "

    cursor.execute(sql)
    returnnum = cursor.fetchall()
    listt = list(returnnum)
    returnnum = str(listt[0])
    returnnum = returnnum.replace("(","")
    returnnum = returnnum.replace(")","")
    returnnum = returnnum.replace(",","")
    print(returnnum)
    return returnnum

def recommend(userna):

    #Get ID from username
    cursor.execute("SELECT driver_id FROM driver WHERE user='"+userna+"'")
    ID = cursor.fetchall()
    print(ID) 
    List = list(ID)
    print(List)
    returninfo = str(List[0])
    returninfo = returninfo.replace("[", "")
    returninfo = returninfo.replace("]", "")
    returninfo = returninfo.replace("(", "") 
    returninfo = returninfo.replace(")", "")
    returninfo = returninfo.replace(",", "")
    returninfo = returninfo.replace("'", "")
    print(returninfo)
    #Get Latest product bought
    cursor.execute("SELECT Product_ID FROM Product_Orders WHERE Driver_ID = '"+returninfo+"' ORDER BY TimeStamp ASC")
    ID = cursor.fetchall()
    List2 = list(ID)
    got = str(List2[0])
    got = got.replace("[", "")
    got = got.replace("]", "")
    got = got.replace("(", "") 
    got = got.replace(")", "")
    got = got.replace(",", "")
    got = got.replace("'", "")
    print(got)
    #Get a similarity with another user ordered by time
    cursor.execute("SELECT Driver_ID FROM Product_Orders WHERE Driver_ID != '"+returninfo+"' AND Product_ID= '"+got+"' ORDER BY TimeStamp ASC" )
    result = cursor.fetchall()
    print(result)
    List = list(result)
    print(List)
    returninfo = str(List[0])
    returninfo = returninfo.replace("[", "")
    returninfo = returninfo.replace("]", "")
    returninfo = returninfo.replace("(", "") 
    returninfo = returninfo.replace(")", "")
    returninfo = returninfo.replace(",", "")
    returninfo = returninfo.replace("'", "")
    print(returninfo)
    #Select the Product_ID history from the other user
    cursor.execute("SELECT Product_ID FROM Product_Orders WHERE Product_ID !=  '"+got+"' AND Driver_ID = '"+returninfo+"' ORDER BY TimeStamp ASC")
    gotcha = cursor.fetchall()
    print(gotcha)
    List = list(gotcha)
    print(List)
    returninfo = str(List[0])
    returninfo = returninfo.replace("[", "")
    returninfo = returninfo.replace("]", "")
    returninfo = returninfo.replace("(", "") 
    returninfo = returninfo.replace(")", "")
    returninfo = returninfo.replace(",", "")
    returninfo = returninfo.replace("'", "")
    print(returninfo)
    cursor.execute("SELECT name FROM product WHERE product_id = '"+returninfo+"'")
    final = cursor.fetchall()
    List = list(final)
    print(List)
    returninfo = str(List[0])
    returninfo = returninfo.replace("[", "")
    returninfo = returninfo.replace("]", "")
    returninfo = returninfo.replace("(", "") 
    returninfo = returninfo.replace(")", "")
    returninfo = returninfo.replace(",", "")
    returninfo = returninfo.replace("'", "")
    print(returninfo)
    return(returninfo)
#    cursor.execute("SELECT Product_ID FROM Product_Orders WHERE ")

def getpopitems():
    cursor.execute("SELECT Product_ID FROM   Product_Orders GROUP BY Product_ID ORDER BY COUNT(*) DESC ")
    poptuple = cursor.fetchall()
    popstr = "\n".join(str(v) for v in poptuple)
    popstr = popstr.replace("(","")
    popstr = popstr.replace(")","")
    popstr = popstr.replace(",","")
    poplist = popstr.split()
    print(poplist)
    popname = poplist[:3]
    for i in range(0, 3):
        cursor.execute("SELECT name FROM product WHERE product_id = '" +poplist[i]+"'")
        poptuple = cursor.fetchall()
        popstr = "\n".join(str(v) for v in poptuple)
        popstr = popstr.replace("(","")
        popstr = popstr.replace(")","")
        popstr = popstr.replace(",","")
        popstr = popstr.replace("'","")
        popname[i] = popstr
    print(popname)
    return popname

def get_products_by_name(search):
    query = "SELECT name FROM product WHERE name REGEXP(%s)"
    cursor.execute(query, (search, ))
    matches = list(map(lambda x: x[0], cursor.fetchall()))
    print(matches)
    return matches

def getSponsorName(ident):
    ID = str(ident)
    cursor.execute("SELECT title FROM sponsor WHERE sponsor_id = '" +ID+"'")
    got = cursor.fetchall()
    returninfo = ''.join(str(v) for v in got)
#    print(returninfo)
    returninfo = returninfo.replace("[", "")
    returninfo = returninfo.replace("]", "")
    returninfo = returninfo.replace("(", "") 
    returninfo = returninfo.replace(")", "")
    returninfo = returninfo.replace(",", "")
    returninfo = returninfo.replace("'", "")
    print(returninfo)
    return returninfo

    #main used to test functions
if __name__ == "__main__":
    """
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
     print(admin_view_users())
    spons = [1,2,3]
 #   getnumproducts(3)    
    product_search("bike", spons, "None", "pricedown")


    """
    print("David recoo\n")
    recommend("testdrive")
    getpopitems()
    """
    print("David Search\n")
    search = "Bike Tool: car: Luxury: sponge priceup"
    product_search(search) 
   
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
    #suspend_driver('krod', 2020, 11, 30)
    print('Is krod suspended: ' + str(is_suspended('krod')))
    print("suspending spon...")
    #suspend_sponsor('spon', 2020, 12, 25)
    print("Is spon suspended: " + str(is_suspended('spon')))
    print(get_suspended_users())
    edit_suspension('krod', 2020, 11, 12)
    print(get_suspended_users())
    cancel_suspension('krod')
    print(get_suspended_users())
    print(if_username_exist('remove'))
    """
    cursor.close()
    database.close()
    

