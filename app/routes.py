from app import app
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from app.database.db_functions import *

@app.route('/')
def home():
    session['user'] = "Sign Up"

    if not session.get('logged_in'):
        return render_template('login.html', user=session.get('user'))
    else:
        session['user'] = request.args.get('user', None)
        return render_template('template.html', user=session.get('user'))

        if session.get('role') == "driver":
            return "Driver log in successful!  <a href='/logout'>Logout</a>"
        if session.get('role') == "sponsor":
            return "Sponsor log in successful!  <a href='/logout'>Logout</a>"
        if session.get('role') == "admin":
            return "Admin log in successful!  <a href='/logout'>Logout</a>"

@app.route('/login', methods=['POST'])
def do_admin_login():

    #Temp
    db_id = 'admin'
    db_hash = 'password'

    pwd_hash = generate_password_hash(request.form['password'], 'sha256')

    if check_password_hash(pwd_hash, db_hash) and request.form['username'] == db_id:
        session['user'] = request.form['username']
        session['logged_in'] = True
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
    return render_template('signup.html', user=session.get('user'))
