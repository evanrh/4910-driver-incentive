from app import app
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from app.database.db_functions import *
from app.database.db_users import *
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
    return render_template('sponsor/sponsorViewDriver.html', drivers=Driver().get_users(), suspendedUsers=suspendedUsers)

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
       sponsorid = form['sponsorid']

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
           flash('Account created!')
       else:
           flash('Username taken!')


    return render_template('admin/adminManageAcc.html', userTable=getUserTable())

@app.route("/adminNotifications")
def adminNotifications():
    if permissionCheck(["admin"]) == False:
        return redirect(url_for('home'))
    return render_template('admin/adminNotifications.html')

@app.route("/adminPointsLeader")
def adminPointsLeader():
    if permissionCheck(["admin"]) == False:
        return redirect(url_for('home'))
        
    drivers = []
    currSponsor = Sponsor()
    for sponsor in Sponsor().get_users():
        currSponsor.populate(sponsor[1])
        drivers.append(currSponsor.view_leaderboard())

    return render_template('admin/adminPointsLeader.html', drivers=drivers)

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

# Returns a string full of html code representing
# a table with all drivers to display on webpage
def getDriverTable():
    suspendedUsers = Admin().get_suspended_users()
    driverList = Driver().get_users()
    html_str = ""
    html_str = ""
    html_str += '<form id="view-drivers">'
    html_str += "<table>"
    html_str += "<tr>"
    html_str += "<th class='heading'>Drivers</th>"
    html_str += "<th>Remove</th>"
    html_str += "<th>User Name</th>"
    html_str += "<th>First Name</th>"
    html_str += "<th>Last Name</th>"
    html_str += "<th>Suspend</th>"
    html_str += "<th>Points</th>"
    html_str += "<th>Add Points</th>"
    html_str += "<th>Send Message</th>"
    html_str += "<th>Date Joined</th>"
    html_str += "</tr>"

    for driver in driverList:  
        html_str += "<tr>"
        html_str += "<td><button name='" + str(driver[3]) + "' id='edit'><a href='/updateDriver/" + str(driver[3]) + "'>Edit</a></button></td>"
        html_str += "<td><button name='" + str(driver[3]) + "' id='remove' style='color:red;'>X</button></td>"
        html_str += "<td>" + str(driver[3]) + "</td>"
        html_str += "<td>" + str(driver[0]) + "</td>"
        html_str += "<td>" + str(driver[2]) + "</td>"

        if str(driver[3]) in suspendedUsers:
            html_str += "<td><button name='" + str(driver[3]) + "' id='unsuspend' style='color:red;'>X</button></td>"
        else:
            html_str += "<td><button name='" + str(driver[3]) + "' id='suspend'>X</button></td>"

        html_str += "<td>" + str(driver[6]) + "</td>"
        html_str += "<td><input name='" + str(driver[3]) + "' id='addpoints' placeholder='Add Pts'><button id='addpoints'>+</button></td>"
        html_str += "<td><input name='" + str(driver[3]) + "' id='sendmessage' placeholder='Message'><button id='sendmessage'>Send</button></td>"
        #html_str += "<td>" + str(driver[12]) +"</td>"
        html_str += "</tr>"
    
    html_str += "</table></form>"
    return html_str

# Returns a string full of html code representing
# a table with all drivers and sponsors to display on webpage
def getUserTable():
    start_time = time.time()
    admin = Admin()
    suspendedUsers = admin.get_suspended_users()
    adminList = admin.get_users()
    sponsorList = Sponsor().get_users()

    html_str = ""

    html_str += '<form id="view-drivers">'
    html_str += "<table>"
    html_str += "<tr>"
    html_str += "<th class='heading'>Admins</th>"
    html_str += "<th>Delete</th>"
    html_str += "<th>User Name</th>"
    html_str += "<th>First Name</th>"
    html_str += "<th>Last Name</th>"
    html_str += "</tr>"

    for admin in adminList:
        html_str += "<tr>"
        html_str += "<td></td>"
        html_str += "<td><button name='" + str(admin[3]) + "' id='remove' style='color:red;'>X</button></td>"
        html_str += "<td>" + admin[3] + "</td>"
        html_str += "<td>" + admin[0] + "</td>"
        html_str += "<td>" + admin[2] + "</td>"
        html_str += "</tr>"

    for sponsor in sponsorList:
        html_str += "<tr>"
        html_str += "<th class='heading'> Sponsor </th>"
        html_str += "<th>Delete</th>"
        html_str += "<th>User Name</th>"
        html_str += "<th>Title</th>"
        html_str += "<th>Sponsor ID</th>"
        html_str += "<th>Suspend</th>"
        html_str += "<th>Date Joined</th>"
        html_str += "</tr>"

        html_str += "<tr>"
        html_str += "<td></td>"
        html_str += "<td><button name='" + str(sponsor[1]) + "' id='remove' style='color:red;'>X</button></td>"
        html_str += "<td>" + str(sponsor[1]) + "</td>"
        html_str += "<td>" + str(sponsor[0]) + "</td>"
        html_str += "<td>" + str(sponsor[2]) + "</td>"
        if str(sponsor[1]) in suspendedUsers:
            html_str += "<td><button name='" + str(sponsor[1]) + "' id='unsuspend' style='color:red;'>X</button></td>"
        else:
            html_str += "<td><button name='" + str(sponsor[1]) + "' id='suspend'>X</button></td>"
        html_str += "<td>" + str(sponsor[7]) + "</td>"
        html_str += "</tr>"

        html_str += "<tr>"
        html_str += "<td class='driverRow'>Drivers</td>"
        html_str += "<td class='driverRow'>Delete</td>"
        html_str += "<td class='driverRow'>User Name</td>"
        html_str += "<td class='driverRow'>First Name</td>"
        html_str += "<td class='driverRow'>Last Name</td>"
        html_str += "<td class='driverRow'>Suspend</td>"
        html_str += "<td class='driverRow'>Points</td>"
        html_str += "<td class='driverRow'>Add Points</td>"
        html_str += "<td class='driverRow'>Send Message</td>"
        html_str += "<td class='driverRow'>Date Joined</td>"
        html_str += "</tr>"

        currSponsor = Sponsor()
        currSponsor.populate(str(sponsor[1]))
        for driver in currSponsor.view_drivers():
            html_str += "<tr>"
            html_str += "<td></td>"
            html_str += "<td><button name='" + str(driver[3]) + "' id='remove' style='color:red;'>X</button></td>"
            html_str += "<td>" + str(driver[3]) + "</td>"
            html_str += "<td>" + str(driver[0]) + "</td>"
            html_str += "<td>" + str(driver[2]) + "</td>"

            if str(driver[3]) in suspendedUsers:
                html_str += "<td><button name='" + str(driver[3]) + "' id='unsuspend' style='color:red;'>X</button></td>"
            else:
                html_str += "<td><button name='" + str(driver[3]) + "' id='suspend'>X</button></td>"

            html_str += "<td>" + str(driver[6]) + "</td>"
            html_str += "<td><input name='" + str(driver[3]) + "' id='addpoints"+ str(driver[3]) +"' placeholder='Add Pts'><button name='" + str(driver[3]) + "' id='addpoints'>+</button></td>"
            html_str += "<td><input name='" + str(driver[3]) + "' id='sendmessage"+ str(driver[3]) +"' placeholder='Message'><button name='" + str(driver[3]) + "' id='sendmessage'>Send</button></td>"
            html_str += "<td>" + str(driver[12]) +"</td>"
            html_str += "</tr>"

    """
    for driver in sponsorless_drivers():
            html_str += "<tr>"
            html_str += "<td></td>"
            html_str += "<td><button name='" + str(driver[3]) + "' id='remove' style='color:red;'>X</button></td>"
            html_str += "<td>" + str(driver[3]) + "</td>"
            html_str += "<td>" + str(driver[0]) + "</td>"
            html_str += "<td>" + str(driver[2]) + "</td>"

            if str(driver[3]) in suspendedUsers:
                html_str += "<td><button name='" + str(driver[3]) + "' id='unsuspend' style='color:red;'>X</button></td>"
            else:
                html_str += "<td><button name='" + str(driver[3]) + "' id='suspend'>X</button></td>"

            html_str += "<td>" + str(driver[6]) + "</td>"
            html_str += "<td><input name='" + str(driver[3]) + "' id='addpoints"+ str(driver[3]) +"' placeholder='Add Pts'><button name='" + str(driver[3]) + "' id='addpoints'>+</button></td>"
            html_str += "<td><input name='" + str(driver[3]) + "' id='sendmessage"+ str(driver[3]) +"' placeholder='Message'><button name='" + str(driver[3]) + "' id='sendmessage'>Send</button></td>"
            html_str += "<td>" + str(driver[12]) +"</td>"
            html_str += "</tr>"
    """
    html_str += "</table></form>"

    print("--- %s seconds ---" % (time.time() - start_time))
    
    return html_str

@app.route("/suspend", methods=["GET","POST"])
def suspend():
    user = request.get_data().decode("utf-8") 
    Admin().suspend_user(user, 9999, 12, 30)
    return ('', 204)

@app.route("/unsuspend", methods=["GET","POST"])
def unsuspend():
    user = request.get_data().decode("utf-8") 
    Admin().cancel_suspension(user)
    return ('', 204)

@app.route("/remove", methods=["GET","POST"])
def remove():
    user = request.get_data().decode("utf-8") 
    Admin().remove_user(user)
    return ('', 204)

@app.route("/addpts", methods=["GET","POST"])
def addpts():
    data = request.get_data().decode("utf-8").split("&")
    user = data[0].split("=")
    points = data[1].split("=")
    sponsor = data[2].split("=")

    driver = Driver()
    driver.populate(user)
    driver_id = driver.get_user_data()[0][4]

    sponsor = Sponsor()
    sponsor.populate(sponsor)
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
    
    numresults = len(results) -2
    return render_template('driver/driverResults.html', numresults = numresults, query = search, results = results)

@app.route("/updateDriver/<username>", methods=["GET","POST"])
def updateDriver(username):
    """ Render page for a sponsor to update their drivers. Driver to be updated is the endpoint of the URL.
        Provides an endpoint for AJAX calls as well. Expects a JSON object with keys corresponding to driver
        attributes in database"""
    dl = Driver().get_users()
    driver = list(filter(lambda d: d[3] == username, dl))[0]
    if request.method == 'POST':
        driverObj = Driver()
        driverObj.populate(username)
        data = request.json

        # Data should be formatted in the way update_info expects
        driverObj.update_info(data)
        flash("Information updated!")
        return json.dumps({'status': 'OK', 'user': username})

    return render_template("sponsor/sponsorEditDriver.html", driver=driver)
