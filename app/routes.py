from app import app
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from app.database.db_functions import *

@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        user = request.args.get('user', None)
        return render_template('template.html', user=user)
        if session.get('role') == "driver":
            return "Driver log in successful!  <a href='/logout'>Logout</a>"
        if session.get('role') == "sponsor":
            return "Sponsor log in successful!  <a href='/logout'>Logout</a>"
        if session.get('role') == "admin":
            return "Admin log in successful!  <a href='/logout'>Logout</a>"

@app.route('/login', methods=['POST'])
def do_admin_login():
    user = "Username"
    
    if request.form['password'] == 'password' and request.form['username'] == 'admin':
            session['logged_in'] = True

    user = request.form['username']
    password = request.form['password']

    if if_username_exist(user) and pwd_check(user, password):
        session['logged_in'] = True
        #session['role'] = get_role(user)
    else:
        flash('Incorrect login credentials!')
    return redirect(url_for('home', user=user))

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()

@app.route("/signup")
def signup():
    # TODO Add in password hash generation to sign up
    return render_template('signup.html')