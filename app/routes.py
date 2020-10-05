from app import app
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from app.database.db_functions import *
from app.database.db_users import Driver

@app.route('/')
def home():
    if not session.get('logged_in'):
        session['user'] = "Sign Up"
        return render_template('landing/login.html')
    else:
        if session.get('role') == "driver":
            return render_template('driver/driverHome.html')
        if session.get('role') == "sponsor":
            return render_template('sponsor/sponsorHome.html')
        if session.get('role') == "admin":
            return render_template('admin/adminHome.html')

@app.route('/login', methods=['POST'])
def do_admin_login():
    
    db_id = ['admin', 'sponsor', 'driver']
    db_hash = 'password'

    pwd_hash = generate_password_hash(request.form['password'], 'sha256')

    #Temp - remove in final
    if check_password_hash(pwd_hash, db_hash) and request.form['username'] in db_id:
        session['user'] = request.form['username']
        session['logged_in'] = True
        session['role'] = request.form['username']
        return redirect(url_for('home'))
    #Temp

    user = session.get('user')

    if if_username_exist(user) and pwd_check(user, pwd_hash):
        session['logged_in'] = True
        id, session['role'] = get_table_id(user)
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
       pwd_hash = generate_password_hash(pwd, method='sha256');

       user = Driver(fname, mname, lname, username, address, phone, email, pwd_hash)

       if user.check_username_available():
           user.add_user()
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
    return render_template('sponsor/sponsorNotification.html')

@app.route("/sponsorPointsLeader")
def sponsorPointsLeader():
    return render_template('sponsor/sponsorPointsLeader.html')

@app.route("/sponsorProfile")
def sponsorProfile():
    return render_template('sponsor/sponsorProfile.html')

@app.route("/sponsorSystemSettings")
def sponsorSystemSettings():
    return render_template('sponsor/sponsorSystemSettings.html')

@app.route("/sponsorViewDriver")
def sponsorViewDriver():
    return render_template('sponsor/sponsorViewDriver.html')

# Admin Page Routes
@app.route("/adminInbox")
def adminInbox():
    return render_template('admin/adminInbox.html')

@app.route("/adminManageAcc")
def adminManageAcc():
    return render_template('admin/adminManageAcc.html')

@app.route("/adminNotifications")
def adminNotifications():
    return render_template('admin/adminNotifications.html')

@app.route("/adminPointsLeader")
def adminPointsLeader():
    return render_template('admin/adminPointsLeader.html')

@app.route("/adminReports")
def adminReports():
    return render_template('admin/adminReports.html')

@app.route("/adminSysSettings")
def adminSysSettings():
    return render_template('admin/adminSysSettings.html')

@app.route("/settings", methods=["GET","POST"])
def settings():
        if session.get('role') == "driver":
            return render_template('driver/settings.html')
        if session.get('role') == "sponsor":
            return render_template('sponsor/settings.html')
        if session.get('role') == "admin":
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
