from app import app
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return "Log in successful!  <a href='/logout'>Logout</a>"

@app.route('/login', methods=['POST'])
def do_admin_login():

    # TODO Fetch login info from DB
    pwd_hash = generate_password_hash(request.form['password'], 'sha256')
    db_hash = 'password'
    db_id = 'admin'

    if check_password_hash(pwd_hash, db_hash) and request.form['username'] == db_id:
        session['logged_in'] = True
    else:
        flash('Incorrect login credentials!')
    return redirect(url_for('home'))

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect(url_for('home'))

@app.route("/signup")
def signup():
    # TODO Add in password hash generation to sign up
    return render_template('signup.html')
 
