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

    db_hash = 'password'
    db_id = 'admin'

    if check_password_hash(pwd_hash, db_hash) and request.form['username'] == db_id:
        pass
 
    user = request.form['username']
    pwd_hash = generate_password_hash(request.form['password'], 'sha256')

    if if_username_exist(user) and pwd_check(user, pwd_hash):
        session['logged_in'] = True
        session['role'] = get_role(user)
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
       username = request.form['user']
       pwd = request.form['pass']
       pwd_check = request.form['pass_repeat']

    # TODO Add in password hash generation to sign up
    return render_template('signup.html')
