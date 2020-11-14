from app import app
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from app.database.db_functions import *
from app.database.db_users import *
from app.database.db_connection import *
from flask.json import JSONEncoder
from tempfile import TemporaryFile
from app.products.etsy_driver import EtsyController
from app.products.catalog import CatalogController
import json
import time

# Using this to encode our class to store user data
class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, AbsUser):
            return obj.__dict__
        else:
            return ""
            #JSONEncoder.default(self, obj)

# Set default JSON encoder for Flask to allow for classes
app.json_encoder = CustomJSONEncoder

# Chooses a class to use for User
userInfo = Driver()

#Message for alerts
Message = ""

def permissionCheck(allowedRole):
    global userInfo
    suspendedUsers = Admin().get_suspended_users()

    if userInfo.getUsername() == 'NULL':
        if session['userInfo']['properties']['role'] == "admin": 
            userInfo = Admin()
        elif session['userInfo']['properties']['role'] == "sponsor":
            userInfo = Sponsor()
        else:
            userInfo = Driver()

    try:
        userInfo.populate(session['userInfo']['properties']['user'])

    except Exception as e:
        session['logged_in'] = False
        return redirect(url_for('home'))

    if userInfo.getUsername() in suspendedUsers:
        session['logged_in'] = False
        return redirect(url_for('home'))

    if not userInfo.getRole() in allowedRole:
        return False


ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']
# Check if uploaded file is an acceptable file format
def allowed_file(filename):
    return "." in filename and \
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Create temporary file to send to DB driver
def upload_file(f):
    """ Expect f to be the file-like from the form input """
    tempf = TemporaryFile()
    f.save(tempf)
    # Send tempf to driver
    tempf.close()

@app.route('/home')
@app.route('/', methods=['GET', 'POST'])
def home():
    # Using the global class to access data
    global userInfo
    global Message

    if not session.get('logged_in'):
        return render_template('landing/login.html')
    else:
        if permissionCheck(["driver", "sponsor", "admin"]) == False:
            return redirect(url_for('home'))

        session.pop('_flashes', None)

        if userInfo.getRole() == "driver" or userInfo.getSandbox() == 'driver':

            # Messages to be displayed in banner
            inbox_list = userInfo.get_inbox_list()
            if 'System Management' in inbox_list and len(inbox_list) == 1:
                Message = "You have an important message from System Management"
            elif 'System Management' in inbox_list and len(inbox_list > 1):
                Message += ' and ' + str(len(inbox_list) - 1) + ' other unread message'
            elif len(inbox_list) > 0:
                Message = "You have " + str(len(inbox_list)) + ' unread messages'
            else:
                Message = ""

            # Product page information
            recommended = []
            genres = []
            userid = session['userInfo']['properties']['id']

            if not session['userInfo']['properties']['selectedSponsor'] == None:
                genres = getgenres()
                recommended = recommend(userid)
                sponsorId = session['userInfo']['properties']['selectedSponsor'][0]
            else:
                sponsorId = None

            # Fix sponsorless driver issue
            if sponsorId:
                numproducts = getnumproducts(sponsorId)
            else:
                numproducts = 0
            
            popitems = getpopitems(sponsorId)

            return render_template('driver/driverHome.html', head = Message, genres = genres, resultrec = recommended, numprod = numproducts, popular = popitems, curspon= sponsorId)

        if userInfo.getRole() == "sponsor" or userInfo.getSandbox() == 'sponsor':
            inbox_list = userInfo.get_inbox_list()
            if len(inbox_list) > 0:
                Message = "You have " + str(len(inbox_list)) + ' unread messages'
            else:
                Message = ""
            return render_template('sponsor/sponsorHome.html', head = Message)

        if userInfo.getRole() == "admin":
            inbox_list = userInfo.get_inbox_list()
            if len(inbox_list) > 0:
                Message = "You have " + str(len(inbox_list)) + ' unread messages'
            else:
                Message = ""
            return render_template('admin/adminHome.html', head = Message)

    return render_template('landing/login.html')


@app.route('/login', methods=['POST'])
def do_admin_login():
    # Using the global class to access data
    global userInfo
    admin = Admin()
    suspendedUsers = admin.get_suspended_users()

    # Get user input from web page
    username = request.form['username']
    pwd = request.form['password']

    # Do basic login verification
    if not username_exist(username):
        flash('Incorrect login credentials!')
    elif not isActive(username):
        flash("This account has been disabled! Please contact us if you think this is a mistake.")
    elif username in suspendedUsers:
        flash('Your account is currently suspended! Please contact us if you think this is a mistake.')
    else:
        current_hash = get_password(username)
        if check_password_hash(current_hash, pwd):
            session['logged_in'] = True
            
            # Sets the class based on which user role
            id, role = get_table_id(username)
            if role == "admin": 
                userInfo = Admin()
            elif role == "sponsor":
                userInfo = Sponsor()
            else:
                userInfo = Driver()
            # Populate our class with data
            userInfo.populate(username)

            # Flask session data to store data for webpage use
            session['userInfo'] = userInfo

            flash('Login successful!')
            flash('Logged in as: ' + userInfo.getUsername())
        else:
            flash('Incorrect login credentials!')

    return redirect(url_for('home'))

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect(url_for('home'))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        form = request.form
        username = form['user']
        pwd = form['pass']
        pwd_check = form['pass_repeat']
        
        if pwd != pwd_check:
            flash('Passwords do not match!')
            return render_template('landing/signup.html')
        
        sponsor = form['sponsorid'] or 'NULL'
        fname = form['fname']
        mname = form['mname'] or 'NULL'
        lname = form['lname']
        address = form['address'] or 'NULL' # Need to look into address fetching
        phone = form['phone']
        email = form['email'] or 'NULL'
        pwd_hash = generate_password_hash(pwd, method='sha256')
        img = 'NULL'

        newDriver = Driver(fname, mname, lname, username, address, phone, email, pwd_hash, img)

        if newDriver.check_username_available():
            newDriver.add_user()
           
            if not sponsor == "NULL":
                try:
                    newDriver.apply_to_sponsor(int(sponsor))
                except:
                    flash("No sponsor found!")

            flash('Account created!')
            return redirect(url_for('home'))
        else:
           flash('Username taken!')

    return render_template('landing/signup.html')

@app.route("/about")
def about():
    return render_template('landing/about.html')

# Driver Page Routes
@app.route("/driverPointsLeader")
def driverPointsLeader():
    if permissionCheck(["driver", "sponsor", "admin"]) == False:
        return redirect(url_for('home'))
    elif not session['userInfo']['properties']['selectedSponsor']:
        flash("No sponsor selected!")
        return redirect(url_for('home'))

    currSponsor = Sponsor()
    sponsorId = session['userInfo']['properties']['selectedSponsor'][0]
    sponsorName = currSponsor.username_from_id(sponsorId)
    currSponsor.populate(sponsorName)

    drivers = currSponsor.view_leaderboard()

    return render_template('driver/driverPointsLeader.html', drivers=drivers)

@app.route("/driverNotification")
def driverNotification():
    if permissionCheck(["driver", "sponsor", "admin"]) == False:
        return redirect(url_for('home'))
    return render_template('driver/driverNotification.html')

@app.route("/driverManagePurchase")
def driverManagePurchase():
    if permissionCheck(["driver", "sponsor", "admin"]) == False:
        return redirect(url_for('home'))
    purchaseList = []
    # get purchase list
    return render_template('driver/driverManagePurchase.html', purchaseList = purchaseList)

@app.route("/driverProfile")
def driverProfile():
    if permissionCheck(["driver", "sponsor", "admin"]) == False:
        return redirect(url_for('home'))
    return render_template('driver/driverProfile.html')

@app.route("/driverCart")
def driverCart():
    if permissionCheck(["driver", "sponsor", "admin"]) == False:
        return redirect(url_for('home'))

    def getProductInfo(id):
        return Admin().getProductInfo(id)
    
    return render_template('driver/driverCart.html', getProductInfo = getProductInfo)

# Sponsor Page Routes
@app.route("/sponsorNotification")
def sponsorNotification():
    if permissionCheck(["sponsor", "admin"]) == False:
        return redirect(url_for('home'))
    return render_template('sponsor/sponsorNotification.html')

@app.route("/sponsorPointsLeader")
def sponsorPointsLeader():
    if permissionCheck(["sponsor", "admin"]) == False:
        return redirect(url_for('home'))

    currSponsor = Sponsor()
    
    if (userInfo.getRole() == "sponsor"):
        currSponsor.populate(userInfo.getUsername())
        drivers = currSponsor.view_leaderboard()
    else:
        sponsorId = session['userInfo']['properties']['selectedSponsor'][0]
        sponsorName = currSponsor.username_from_id(sponsorId)
        currSponsor.populate(sponsorName)
        drivers = currSponsor.view_leaderboard()

    return render_template('sponsor/sponsorPointsLeader.html', drivers=drivers)

@app.route("/sponsorProfile")
def sponsorProfile():
    if permissionCheck(["sponsor", "admin"]) == False:
        return redirect(url_for('home'))
    return render_template('sponsor/sponsorProfile.html')

@app.route("/sponsorSystemSettings", methods=['GET', 'POST'])
def sponsorSystemSettings():
    if permissionCheck(["sponsor", "admin"]) == False:
        return redirect(url_for('home'))

    if request.method == 'POST':
        rate = request.form['rate']
        sid = session['userInfo']['properties']['id']
        userInfo.properties['point_value'] = rate
        update_sponsor_rate(sid, rate)
        flash('Conversion rate updated!')

    return render_template('sponsor/sponsorSystemSettings.html', rate=userInfo.properties['point_value'])

@app.route("/sponsorViewDriver")
def sponsorViewDriver():
    if permissionCheck(["sponsor", "admin"]) == False:
        return redirect(url_for('home'))
    suspendedUsers = Admin().get_suspended_users()

    currSponsor = Sponsor()

    if userInfo.getRole() == 'admin' or userInfo.getSandbox() == 'sponsor':
        sponsor = currSponsor.get_users()[0][1]
        drivers = currSponsor.view_drivers()
    else:
        sponsor = userInfo.getUsername()
        drivers = userInfo.view_drivers()

    currSponsor.populate(sponsor)
    applications = currSponsor.view_applications()

    return render_template('sponsor/sponsorViewDriver.html', drivers=drivers, applications = applications, suspendedUsers=suspendedUsers, sponsor=sponsor)

@app.route("/adminManageAcc", methods=["GET", "POST"])
def adminManageAcc():
    if permissionCheck(["admin"]) == False:
        return redirect(url_for('home'))

    if request.method == "POST":
       form = request.form
       username = form['user']
       pwd = form['pass']
       role = form['roleSelect']
       title = form['title']
       sponsorid = form['sponsorid'] or 'Null'

       fname = 'NULL'
       mname = 'NULL'
       lname = 'NULL'
       address = 'NULL'
       phone = 'NULL'
       email = 'NULL'
       pwd_hash = generate_password_hash(pwd, method='sha256')
       img = 'NULL'

       if role == "driver":
           newUser = Driver(fname, mname, lname, username, address, phone, email, pwd_hash, img)
       elif role == "sponsor":
           newUser = Sponsor(title, username, address, phone, email, pwd_hash, img)
       else:
           newUser = Admin(fname, mname, lname, username, phone, email, pwd_hash, img)
    
       if newUser.check_username_available():
           newUser.add_user()
           if sponsorid != 'Null':
               Admin().add_to_sponsor(newUser.getID(), sponsorid)
           flash('Account created!')
       elif role == "driver":
            newUser.populate(username)
            if sponsorid != 'Null':
                Admin().add_to_sponsor(newUser.getID(), sponsorid)
            else:
                flash('No sponsor id entered!')
       else:
           flash('Username taken!')
    
    admin = Admin()
    suspendedUsers = admin.get_suspended_users()
    adminList = admin.get_users()
    sponsorList = Sponsor().get_users()
    sponsorlessDrivers = admin.get_sponsorless_drivers()
    disabledDrivers = admin.get_disabled_drivers()
    disabledSponsors = admin.get_disabled_sponsors()
    disabledAdmins = admin.get_disabled_admins()
    def getDriverList(sponsorName):
        currSponsor = Sponsor()
        currSponsor.populate(sponsorName)
        return currSponsor.view_drivers()
    
    return render_template('admin/adminManageAcc.html', sponsorList = sponsorList, adminList = adminList, 
                                                        suspendedUsers = suspendedUsers, getDriverList = getDriverList, 
                                                        sponsorlessDrivers = sponsorlessDrivers, disabled = (disabledDrivers, disabledSponsors, disabledAdmins))

@app.route("/adminNotifications")
def adminNotifications():
    if permissionCheck(["admin"]) == False:
        return redirect(url_for('home'))
    return render_template('admin/adminNotifications.html')

@app.route("/adminPointsLeader")
def adminPointsLeader():
    if permissionCheck(["admin"]) == False:
        return redirect(url_for('home'))
        
    sponsors = []
    currSponsor = Sponsor()
    for sponsor in Sponsor().get_users():
        currSponsor.populate(sponsor[1])
        sponsors.append(currSponsor.view_leaderboard())

    return render_template('admin/adminPointsLeader.html', sponsors=sponsors)

@app.route("/adminReports")
def adminReports():
    if permissionCheck(["admin"]) == False:
        return redirect(url_for('home'))
    return render_template('admin/adminReports.html')

@app.route("/adminSysSettings")
def adminSysSettings():
    if permissionCheck(["admin"]) == False:
        return redirect(url_for('home'))
    return render_template('admin/adminSysSettings.html')

# Consolidated Inbox route 
@app.route('/inbox', defaults={'username': None}, methods=["GET","POST"])
@app.route("/inbox/<username>", methods=["GET","POST"])
def inbox(username):
    if permissionCheck(["driver", "sponsor", "admin"]) == False:
        return redirect(url_for('home'))

    if userInfo.getRole() == "driver":
        currentDriver = Driver()
        currentDriver.populate(session['userInfo']['properties']['user'])
        messages = currentDriver.view_messages()
        inbox_list = currentDriver.get_inbox_list()
        def mark_as_seen(username):
            currentDriver.messages_are_seen(username)

        return render_template('driver/driverInbox.html', messages = messages, selectedUser = username, seen = mark_as_seen, inbox_list = inbox_list)
    if userInfo.getRole() == "sponsor":
        currentDriver = Sponsor()
        currentDriver.populate(session['userInfo']['properties']['user'])
        messages = currentDriver.view_messages()
        inbox_list = currentDriver.get_inbox_list()
        def mark_as_seen(username):
            currentDriver.messages_are_seen(username)

        return render_template('sponsor/sponsorInbox.html', messages = messages, selectedUser = username, seen = mark_as_seen, inbox_list = inbox_list)

    if userInfo.getRole() == "admin":
        currentDriver = Admin()
        currentDriver.populate(session['userInfo']['properties']['user'])
        messages = currentDriver.view_messages()
        inbox_list = currentDriver.get_inbox_list()
        def mark_as_seen(username):
            currentDriver.messages_are_seen(username)

        return render_template('admin/adminInbox.html', messages = messages, selectedUser = username, seen = mark_as_seen, inbox_list = inbox_list)


# Settings page
@app.route("/settings", methods=["GET","POST"])
def settings():
        if permissionCheck(["driver", "sponsor", "admin"]) == False:
            return redirect(url_for('home'))
        userInfo.setSandbox("NULL")

        if request.method == 'POST':
            if 'delete-account' in request.form.keys():
                userInfo.delete()
                session['logged_in'] = False
                flash('Account successfully deleted')
                return redirect(url_for('home'))
            if 'change-info' in request.form.keys():
                
                # Filter out form items that are not filled in
                data = dict(filter(lambda elem: elem[1] != '', request.form.items()))
                
                # Check if no form boxes were filled in
                if not len(data):
                    flash("Please fill in at least one box")
                    return render_template(userInfo.getRole() + "/settings.html")
                
                userInfo.update_info(data)
                return render_template(userInfo.getRole() + "/settings.html")

            elif 'pwd-submit' in request.form.keys():
                oldPwd = request.form['old_pass']
                currentHash = get_password(session['userInfo']['properties']['user'])
                if not check_password_hash(currentHash, oldPwd):
                    flash("Wrong old password!")
                    return render_template(session['userInfo']['properties']['role'] + "/settings.html")
                pwd = generate_password_hash(request.form['pass'], 'sha256')
                userInfo.update_info({'pwd': pwd})
                return render_template(userInfo.getRole() + "/settings.html")

        if userInfo.getRole() == "driver":
            return render_template('driver/settings.html')
        if userInfo.getRole() == "sponsor":
            return render_template('sponsor/settings.html')
        if userInfo.getRole() == "admin":
            return render_template('admin/settings.html')

# App Functions
@app.route("/switchSponsor", methods=['GET', 'POST'])
def switchSponsor():
    if permissionCheck(["driver", "sponsor", "admin"]) == False:
            return redirect(url_for('home'))

    if not userInfo.getRole() == ("admin" or "sponsor"):
        newSponsorid = request.form.get('sponsorSelect')
        sponsorlist = userInfo.view_sponsors()
        points = 0

        for sponsor in sponsorlist:
            if int(sponsor[0]) == int(newSponsorid):
                points = sponsor[1]

        userInfo.setSponsorView([newSponsorid, points])
        session['userInfo']['properties']['selectedSponsor'] = [newSponsorid, points]
        session.modified = True

    return redirect(url_for('home'))

@app.route("/sponsorView")
def sponsorView():
    if userInfo.getRole() == "admin":
        userInfo.setSandbox("sponsor")
    return render_template('sponsor/sponsorHome.html')

@app.route("/driverView")
def driverView():
    if userInfo.getRole() == ("admin" or "sponsor"):
        userInfo.setSandbox("driver")
    genres = getgenres()
    
    return render_template('driver/driverHome.html', genres = genres)

@app.route("/returnView")
def returnView():
    userInfo.setSandbox("NULL")
    return redirect(url_for('home'))

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

@app.route("/acceptapp", methods=["GET","POST"])
def acceptapp():
    data = request.get_data().decode("utf-8").split("&")
    user = data[0].split("=")
    sponsorname = data[1].split("=")

    sponsor = Sponsor()
    sponsor.populate(sponsorname[1])

    sponsor.accept_application(user[1].strip('+'))
    return ('', 204)

@app.route("/rejectapp", methods=["GET","POST"])
def rejectapp():
    data = request.get_data().decode("utf-8").split("&")
    user = data[0].split("=")
    sponsorname = data[1].split("=")

    sponsor = Sponsor()
    sponsor.populate(sponsorname[1])
    sponsor.decline_application(user[1].strip('+'))
    return ('', 204)

@app.route("/suspend", methods=["GET","POST"])
def suspend():
    user = request.get_data().decode("utf-8") 
    user = user.strip()
    Admin().suspend_user(user, 9999, 12, 30)
    return ('', 204)

@app.route("/unsuspend", methods=["GET","POST"])
def unsuspend():
    user = request.get_data().decode("utf-8") 
    user = user.strip()
    Admin().cancel_suspension(user)
    return ('', 204)

@app.route("/remove", methods=["GET","POST"])
def remove():
    user = request.get_data().decode("utf-8") 
    user = user.strip()
    Admin().remove_user(user)
    return ('', 204)

@app.route("/reactivate", methods=["GET","POST"])
def reactivate():
    user = request.get_data().decode("utf-8") 
    user = user.strip()
    Admin().reactivate_user(user)
    return ('', 204)

@app.route("/removeFromSponsor", methods=["GET","POST"])
def removeFromSponsor():
    data = request.get_data().decode("utf-8").split("&")
    user = data[0].split("=")
    sponsorname = data[1].split("=")

    driver = Driver()
    driver_username = user[1].strip('+')
    driver.populate(driver_username)
    driver_id = driver.getID()

    sponsor = Sponsor()
    sponsor.populate(sponsorname[1])
    sponsor.remove_driver(driver_id)

    return ('', 204)

@app.route("/addpts", methods=["GET","POST"])
def addpts():
    data = request.get_data().decode("utf-8").split("&")
    user = data[0].split("=")
    points = data[1].split("=")
    sponsorname = data[2].split("=")

    driver = Driver()
    driver_username = user[1].strip('+')
    driver.populate(driver_username)
    driver_id = driver.getID()

    sponsor = Sponsor()
    sponsor.populate(sponsorname[1])
    sponsor.add_points(driver_id, int(points[1]))

    return ('', 204)

@app.route("/sendmessage", methods=["GET","POST"])
def sendmessage():
    data = request.get_data().decode("utf-8").split("&")
    reciever = data[0].split("=")
    sender = data[1].split("=")
    message = data[2].split("=")

    id, role = get_table_id(sender[1])

    if role == "admin":
        user = Admin()
    elif role == "sponsor":
        user = Sponsor()
    else:
        user = Driver()
    
    username = sender[1].strip('+')

    if not message == "":
        user.populate(username)
        user.send_message(reciever[1].strip('+'), message[1].replace('+', " "))

    return ('', 204)

@app.route("/addToCart", methods=["GET","POST"])
def addToCart():
    data = request.get_data().decode("utf-8").split("&")
    id = data[0].split("=")[1]

    if not 'shoppingCart' in session:
        session['shoppingCart'] = dict()
    
    if id in session['shoppingCart']:
        session['shoppingCart'][id] += 1
    
    else:
        session['shoppingCart'][id] = 1

    session.modified = True

    return ('', 204)

@app.route("/removeFromCart", methods=["GET","POST"])
def removeFromCart():
    data = request.get_data().decode("utf-8").split("&")
    id = data[0].split("=")[1]
    session['shoppingCart'].pop(id)
    session.modified = True
    return ('', 204)

@app.route("/checkout", methods=["GET","POST"])
def checkout():
    if permissionCheck(["driver", "sponsor", "admin"]) == False:
        return redirect(url_for('home'))

    cartTotal = 0
    success = True
    purchase = session['shoppingCart'].copy()
    now = datetime.datetime.now()

    for item in session['shoppingCart']:
        print(getprodinfo(item))
        cartTotal += getprodinfo(item)[1]
    
    if cartTotal > session['userInfo']['properties']['selectedSponsor'][1]:
        success = False
    
    else:
        sponsor = Sponsor()
        name = getSponsorName(session['userInfo']['properties']['selectedSponsor'][0])
        sponsor.populate(name)

        # Subtract the points
        sponsor.add_points(session['userInfo']['properties']['id'], -cartTotal)
        session['userInfo']['properties']['selectedSponsor'][1] -= cartTotal
        session.modified = True

        # Add to the database

        # Clear the cart
        session['shoppingCart'].clear()
        session.modified = True
    
    def getProductInfo(id):
        return Admin().getProductInfo(id)

    return render_template('driver/driverReciept.html', purchase = purchase, success = success, total = cartTotal, date = now, getProductInfo = getProductInfo)

@app.route("/sendto", methods=["GET","POST"])
def sendto():
    data = request.get_data().decode("utf-8").split("&")
    sender = data[0].split("=")
    receiver = data[1].split("=")
    message = data[2].split("=")

    id, role = get_table_id(sender[1])

    if role == "admin":
        user = Admin()
    elif role == "sponsor":
        user = Sponsor()
    else:
        user = Driver()
    
    username = sender[1].strip('+')

    if Admin().username_exist(receiver) and not message == "":
        user.populate(username)
        user.send_message(receiver[1].strip('+'), message[1].replace('+', " "))

    return ('', 204)

@app.route("/productsearch", methods=["GET","POST"])
def productsearch():
    if permissionCheck(["driver", "sponsor", "admin"]) == False:
        return redirect(url_for('home'))

    # Setting up default variables
    search = ""
    results = "" 
    amount = 0
    sponsorId = session['userInfo']['properties']['selectedSponsor'][0]

    # On post, get information from filter form
    if request.method == 'POST':
        form = request.form
        search = form['search']
        mylist = form['mylist']
        order = form['orderby']
        amount = int(form['amount'])
        results = product_search(search, sponsorId, mylist, order)

    # Store limited amount of results and send to page
    limitedresults = []

    # Loop to the minimum of the amount of results and the amount of products to show
    for i in range(0, min(amount, len(results))):
        limitedresults.append(results[i])

    return render_template('driver/driverResults.html', numresults = len(results), query = search, results = limitedresults)


#Very much a building block, may scrap if need be
@app.route("/productpage", methods=["GET","POST"])
def productpage():
    if permissionCheck(["driver", "sponsor", "admin"]) == False:
        return redirect(url_for('home'))

    currSponsor = Sponsor()
    sponsorId = session['userInfo']['properties']['selectedSponsor'][0]

    if request.method == 'POST':
        form = request.form
        got = form['productname']
        results = product_search(got, sponsorId, "None", "priceup" )

#    print(results[0]['name'])
        return render_template('driver/driverProduct.html', results = results[0])

@app.route("/buynow", methods=["GET", "POST"])
def buynow():
    if permissionCheck(["driver", "sponsor", "admin"]) == False:
        return redirect(url_for('home'))

    currSponsor = Sponsor()
    sponsorId = session['userInfo']['properties']['selectedSponsor'][0]


    if request.method == 'POST':
        form = request.form
        got = form['buy']
        results = product_search(got, sponsorId, "None", "priceup" )

    return render_template('driver/driverBuyNow.html', results = results[0])
     
@app.route("/buynowrecipt", methods=["GET", "POST"])
def buynowrecipt():
    if permissionCheck(["driver", "sponsor", "admin"]) == False:
        return redirect(url_for('home'))

    currSponsor = Sponsor()
    sponsorId = session['userInfo']['properties']['selectedSponsor'][0]


    if request.method == 'POST':
        form = request.form
        got = form['buy']
        results = product_search(got, sponsorId, "None", "priceup" )
    
    currSponsor = Sponsor()

    userId = session['userInfo']['properties']['id']
    Davidsubpoints(userId, results[0]['price'], sponsorId)   
    print(userId, results[0]['price'], sponsorId)
     
    return render_template('driver/driverBuyNowRecipt.html', results = results[0])

@app.route("/thanks", methods=["GET","POST"])
def thanks():
    if permissionCheck(["driver", "sponsor", "admin"]) == False:
        return redirect(url_for('home'))

    userId = session['userInfo']['properties']['id']
    if request.method == "POST":
        form = request.form
        num = form['review']
        pid = form['product']


    print(num)
    print(pid)
    print(userId)
    updateproductorder(userId, pid, num)
    return render_template('driver/driverThanks.html')

@app.route("/productAJAX", methods=["POST"])
def productAJAX():
    data = request.json
    search = data['search']
    return json.dumps(get_products_by_name(search))

# IMPORTANT: Route becoming deprecated
# Evan: I changed the location of the edit button to use updateAccount so that it can be shared by
# both the admins and the sponsors
@app.route("/updateDriver/<username>", methods=["GET","POST"])
def updateDriver(username):
    """ Render page for a sponsor to update their drivers. Driver to be updated is the endpoint of the URL.
        Provides an endpoint for AJAX calls as well. Expects a JSON object with keys corresponding to driver
        attributes in database"""
    dl = Driver().get_users()
    driver = list(filter(lambda d: d[3] == username, dl))[0]
    driverObj = Driver()
    driverObj.populate(username)
    if request.method == 'POST':
        data = request.json
        if 'addPoints' in data.keys():
            add_points_to_driver(username, 0, data['addPoints'])
            return json.dumps({'status': 'OK', 'ptsAdded': data['addPoints']})

        # Data should be formatted in the way update_info expects
        driverObj.update_info(data)
        flash("Information updated!")
        return json.dumps({'status': 'OK', 'user': username})

    return render_template("sponsor/sponsorEditDriver.html", user=driverObj)

@app.route('/updateAccount/<username>', methods=['GET','POST'])
def updateAccount(username):
    """ Route for an admin to update any user account. Figures out role from table and generates a template
        accordingly
    """
    def posted(username, user):
        if request.method == 'POST':
            data = request.json
            if 'pwd' in data.keys():
                data['pwd'] = generate_password_hash(data['pwd'], 'sha256')
            # Data should be formatted in the way update_info expects
            user.update_info(data)
            return json.dumps({'status': 'OK', 'user': username})

    sessRole = session['userInfo']['properties']['role']
    print(sessRole)
    if sessRole == 'admin':
        uid, role = get_table_id(username)
        user = None
        if role == 'driver':
            user = Driver()
        elif role == 'sponsor':
            user = Sponsor()
        else:
            user = Admin()
        user.populate(username)
        posted(username, user)
        return render_template('admin/adminUpdateAccount.html', user=user, role=role)

    elif sessRole == 'sponsor':
        allDrivers = userInfo.view_drivers()
        driver = list(filter(lambda d: d[3] == username, allDrivers))

        if driver:
            user = Driver()
            user.populate(username)
            posted(username, user)

            return render_template('sponsor/sponsorEditDriver.html', user=user, sponsor=session['userInfo']['properties']['user'], points=driver[0][4])
        else:
            flash('Driver not in your list!')
            return redirect(url_for('sponsorViewDriver'))
        
    else:
        flash('Please login before trying to edit accounts')
        return redirect(url_for('home'))


# Sponsor Catalog Additions Search
@app.route('/sponsorSearch', methods=['GET', 'POST'])
def sponsorSearch():
    if request.method == 'POST':
        search = request.form['search']
        limit = int(request.form['limit'])

        # Send query to Etsy Controller
        cont = EtsyController(os.getenv("ETSY_API_KEY"))
        cont.limit = limit
        results = cont.get_products_keywords(search)
        return render_template('sponsor/sponsorResults.html', results=results) 

# Admin view sponsor catalog
@app.route('/catalog/<sponsor>', methods=['GET', 'POST'])
def catalog(sponsor):
    if session['userInfo']['properties']['role'] == 'admin':
        sid, role = get_table_id(sponsor)
        if role != 'sponsor':
            return redirect(url_for('home'))
        cont = CatalogController()

        search = None

        if request.method == 'POST':
            if request.json:
                data = request.json
                listing = data['listing_id']
                val = cont.remove(sid, listing)
                message = {'message': 'Item removed' if val else 'Item not removed'}
                return json.dumps(message)

            else:
                search = request.form['search']

        items = cont.fetch_catalog_items(sid, search)
        del cont
        return render_template('admin/adminViewCatalog.html', results=items['items'], sponsor=sponsor)
        
    else:
        flash('Access not allowed')
        return redirect(url_for('home'))
