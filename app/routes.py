from app import app
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from app.database.db_functions import *

@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        if session.get('role') == "driver":
            return "Driver log in successful!  <a href='/logout'>Logout</a>"
        if session.get('role') == "sponsor":
            return "Sponsor log in successful!  <a href='/logout'>Logout</a>"
        if session.get('role') == "admin":
            return "Admin log in successful!  <a href='/logout'>Logout</a>"

@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form['password'] == 'password' and request.form['username'] == 'admin':
      session['logged_in'] = True
    password = request.form['password']
    user = request.form['username']
    if if_username_exist(user) and pwd_check(user, password):
        session['logged_in'] = True
        session['role'] = get_role(user)
    else:
        flash('Incorrect login credentials!')
    return home()

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return url_for('home')

@app.route("/signup")
def signup():
    return render_template('signup.html')
 
