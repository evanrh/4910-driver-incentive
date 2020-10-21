from app import app
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from app.database.db_functions import *
from app.database.db_users import *
from app.database.db_connection import DB_Connection
from flask.json import JSONEncoder
from tempfile import TemporaryFile
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

@app.route('/')
def home():
    # Using the global class to access data
    global userInfo

    if not session.get('logged_in'):
        return render_template('landing/login.html')
    else:
        if permissionCheck(["driver", "sponsor", "admin"]) == False:
            return redirect(url_for('home'))

        session.pop('_flashes', None)

        if userInfo.getRole() == "driver" or userInfo.getSandbox() == 'driver':
            genres = getgenres()
            userna = session['userInfo']['properties']['user']
            return render_template('driver/driverHome.html', genres = genres)


        if userInfo.getRole() == "sponsor" or userInfo.getSandbox() == 'sponsor':
            return render_template('sponsor/sponsorHome.html')

        if userInfo.getRole() == "admin":
            return render_template('admin/adminHome.html')

    return render_template('landing/login.html')


@app.route('/login', methods=['POST'])
def do_admin_login():
    # Using the global class to access data
    global userInfo
    suspendedUsers = Admin().get_suspended_users()

    # Get user input from web page
    username = request.form['username']
    pwd = request.form['password']

    # Do basic login verification
    if not username_exist(username):
        flash('Incorrect login credentials!')
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
           flash('Account created!')
           return redirect(url_for('home'))
       else:
           flash('Username taken!')

    # TODO Add in password hash generation to sign up
    return render_template('landing/signup.html')

@app.route("/about")
def about():
    return render_template('landing/about.html')

# Driver Page Routes
@app.route("/driverPointsLeader")
def driverPointsLeader():
    if permissionCheck(["driver", "sponsor", "admin"]) == False:
        return redirect(url_for('home'))

    currSponsor = Sponsor()
    sponsorId = session['userInfo']['properties']['selectedSponsor'][0]
    sponsorName = currSponsor.username_from_id(sponsorId)
    currSponsor.populate(sponsorName)
    print(sponsorName)
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
    return render_template('driver/driverManagePurchase.html')

@app.route("/driverProfile")
def driverProfile():
    if permissionCheck(["driver", "sponsor", "admin"]) == False:
        return redirect(url_for('home'))
    return render_template('driver/driverProfile.html')

@app.route("/driverInbox")
def driverInbox():
    if permissionCheck(["driver", "sponsor", "admin"]) == False:
        return redirect(url_for('home'))
    return render_template('driver/driverInbox.html')

@app.route("/driverCart")
def driverCart():
    if permissionCheck(["driver", "sponsor", "admin"]) == False:
        return redirect(url_for('home'))
    return render_template('driver/driverCart.html')

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
    currSponsor.populate(userInfo.getUsername())
    drivers = currSponsor.view_leaderboard()

    return render_template('sponsor/sponsorPointsLeader.html', drivers=drivers)

@app.route("/sponsorProfile")
def sponsorProfile():
    if permissionCheck(["sponsor", "admin"]) == False:
        return redirect(url_for('home'))
    return render_template('sponsor/sponsorProfile.html')

@app.route("/sponsorSystemSettings")
def sponsorSystemSettings():
    if permissionCheck(["sponsor", "admin"]) == False:
        return redirect(url_for('home'))

    return render_template('sponsor/sponsorSystemSettings.html')

@app.route("/sponsorViewDriver")
def sponsorViewDriver():
    if permissionCheck(["sponsor", "admin"]) == False:
        return redirect(url_for('home'))
    suspendedUsers = Admin().get_suspended_users()

    if userInfo.getRole() == 'admin' or userInfo.getSandbox() == 'sponsor':
        currSponsor = Sponsor()
        sponsor = currSponsor.get_users()[0][1]
        currSponsor.populate(sponsor)
        drivers = currSponsor.view_drivers()
    else:
        sponsor = userInfo.getUsername()
        drivers = userInfo.view_drivers()

    return render_template('sponsor/sponsorViewDriver.html', drivers=drivers, suspendedUsers=suspendedUsers, sponsor=sponsor)

# Admin Page Routes
@app.route("/adminInbox")
def adminInbox():
    if permissionCheck(["admin"]) == False:
        return redirect(url_for('home'))
    return render_template('admin/adminInbox.html')

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
    sponsorlessDrivers = Admin().get_sponsorless_drivers()

    def getDriverList(sponsorName):
        currSponsor = Sponsor()
        currSponsor.populate(sponsorName)
        return currSponsor.view_drivers()
    
    return render_template('admin/adminManageAcc.html', sponsorList = sponsorList, adminList = adminList, suspendedUsers = suspendedUsers, getDriverList = getDriverList, sponsorlessDrivers = sponsorlessDrivers)

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

        print(points)
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

@app.route("/productsearch", methods=["GET","POST"])
def productsearch():
    search = "no input"
    results = "blah blah blah blah"  

    if request.method == 'POST':
        form = request.form
        search = form['search']
        results = product_search(search)
    numresults = len(results) 
    return render_template('driver/driverResults.html', numresults = numresults, query = search, results = results)

@app.route("/productAJAX", methods=["POST"])
def productAJAX():
    data = request.json
    search = data['search']
    return json.dumps(get_products_by_name(search))

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

    return render_template("sponsor/sponsorEditDriver.html", driver=driverObj)
