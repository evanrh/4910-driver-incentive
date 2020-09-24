from app import app
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from app.database.db_functions import *

@app.route('/')
def home():
    if not session.get('logged_in'):
        session['user'] = "Sign Up"
        return render_template('landing/login.html', user=session.get('user'))
    else:
        if session.get('role') == "driver":
            return render_template('driver/driverHome.html', user=session.get('user'))
        if session.get('role') == "sponsor":
            return render_template('sponsor/sponsorHome.html', user=session.get('user'))
        if session.get('role') == "admin":
            return render_template('admin/adminHome.html', user=session.get('user'))

@app.route('/login', methods=['POST'])
def do_admin_login():

    #Temp
    db_id = 'admin'
    db_hash = 'password'

    pwd_hash = generate_password_hash(request.form['password'], 'sha256')

    if check_password_hash(pwd_hash, db_hash) and request.form['username'] == db_id:
        session['user'] = request.form['username']
        session['logged_in'] = True
        session['role'] = 'admin'
        return redirect(url_for('home', user=session.get('user')))
    #Temp

    user = session.get('user')

    if if_username_exist(user) and pwd_check(user, pwd_hash):
        session['logged_in'] = True
        #session['role'] = get_role(user)
    else:
        flash('Incorrect login credentials!')
    return redirect(url_for('home', user=session.get('user')))

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect(url_for('home', user=session.get('user')))

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":
       username = request.form['user']
       pwd = request.form['pass']
       pwd_check = request.form['pass_repeat']

    # TODO Add in password hash generation to sign up
    return render_template('landing/signup.html', user=session.get('user'))

@app.route("/about")
def about():
    return render_template('landing/about.html', user=session.get('user'))

# Route that does nothing, used in the templates for now until routes are made.
@app.route("/na")
def na():
    return ('', 204)