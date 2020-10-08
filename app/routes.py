from app import app
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from app.database.db_functions import *
from app.database.db_users import Driver
from app.User import User

@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('landing/login.html')
    else:
        session.pop('_flashes', None)
        if session['userInfo']['role'] == "driver" or session['userInfo']['sandbox'] == 'driver':
            return render_template('driver/driverHome.html')
        
        if session['userInfo']['role'] == "sponsor" or session['userInfo']['sandbox'] == 'sponsor':
            return render_template('sponsor/sponsorHome.html')

        if session['userInfo']['role'] == "admin":
            return render_template('admin/adminHome.html')

@app.route('/login', methods=['POST'])
def do_admin_login():
    pwd = request.form['password']
    username = request.form['username']

    if not if_username_exist(username):
        flash('Incorrect login credentials!')
    else:
        current_hash = get_password(username)
        if check_password_hash(current_hash, pwd):
            session['logged_in'] = True
            session['userInfo'] = User(username).__dict__
            flash('Login successful!')
            flash('Logged in as: ' + session['userInfo']['username'])
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
    return render_template('driver/driverPointsLeader.html')

@app.route("/driverNotification")
def driverNotification():
    return render_template('driver/driverNotification.html')

@app.route("/driverManagePurchase")
def driverManagePurchase():
    return render_template('driver/driverManagePurchase.html')

@app.route("/driverProfile")
def driverProfile():
    return render_template('driver/driverProfile.html')

@app.route("/driverInbox")
def driverInbox():
    return render_template('driver/driverInbox.html')

# Sponsor Page Routes
@app.route("/sponsorNotification")
def sponsorNotification():
    if not session['userInfo']['role'] == ("admin" or "sponsor"):
        return redirect(url_for('home'))
    else:
        return render_template('sponsor/sponsorNotification.html')

@app.route("/sponsorPointsLeader")
def sponsorPointsLeader():
    if not session['userInfo']['role'] == ("admin" or "sponsor"):
        return redirect(url_for('home'))
    else:
        return render_template('sponsor/sponsorPointsLeader.html')

@app.route("/sponsorProfile")
def sponsorProfile():
    if not session['userInfo']['role'] == ("admin" or "sponsor"):
        return redirect(url_for('home'))
    else:
        return render_template('sponsor/sponsorProfile.html')

@app.route("/sponsorSystemSettings")
def sponsorSystemSettings():
    if not session['userInfo']['role'] == ("admin" or "sponsor"):
        return redirect(url_for('home'))
    else:
        return render_template('sponsor/sponsorSystemSettings.html')

@app.route("/sponsorViewDriver")
def sponsorViewDriver():
    if not session['userInfo']['role'] == ("admin" or "sponsor"):
        return redirect(url_for('home'))
    else:
        return render_template('sponsor/sponsorViewDriver.html')

# Admin Page Routes
@app.route("/adminInbox")
def adminInbox():
    if not session['userInfo']['role'] == "admin":
        return redirect(url_for('home'))
    else:
        return render_template('admin/adminInbox.html')

@app.route("/adminManageAcc")
def adminManageAcc():
    if not session['userInfo']['role'] == "admin":
        return redirect(url_for('home'))
    else:
        return render_template('admin/adminManageAcc.html')

@app.route("/adminNotifications")
def adminNotifications():
    if not session['userInfo']['role'] == "admin":
        return redirect(url_for('home'))
    else:
        return render_template('admin/adminNotifications.html')

@app.route("/adminPointsLeader")
def adminPointsLeader():
    if not session['userInfo']['role'] == "admin":
        return redirect(url_for('home'))
    else:
        return render_template('admin/adminPointsLeader.html')

@app.route("/adminReports")
def adminReports():
    if not session['userInfo']['role'] == "admin":
        return redirect(url_for('home'))
    else:
        return render_template('admin/adminReports.html')

@app.route("/adminSysSettings")
def adminSysSettings():
    if not session['userInfo']['role'] == "admin":
        return redirect(url_for('home'))
    else:
        return render_template('admin/adminSysSettings.html')

@app.route("/sponsorView")
def sponsorView():
    if session['userInfo']['role'] == "admin":
        session['userInfo']['sandbox'] = "sponsor"
    return render_template('sponsor/sponsorHome.html')

@app.route("/driverView")
def driverView():
    if session['userInfo']['role'] == ("admin" or "sponsor"):
        session['userInfo']['sandbox'] = "driver"
    return render_template('driver/driverHome.html')

@app.route("/returnView")
def returnView():
    session['userInfo']['sandbox'] = 'NULL'
    return redirect(url_for('home'))

@app.route("/settings", methods=["GET","POST"])
def settings():
        if session['userInfo']['role'] == "driver":
            return render_template('driver/settings.html')
        if session['userInfo']['role'] == "sponsor":
            return render_template('sponsor/settings.html')
        if session['userInfo']['role'] == "admin":
            return render_template('admin/settings.html')

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

# Route that does nothing, used in the templates for now until routes are made.
@app.route("/na")
def na():
    return ('', 204)
