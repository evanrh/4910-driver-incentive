
from werkzeug.security import generate_password_hash, check_password_hash

# TODO Fetch login info from DB
    pwd_hash = generate_password_hash(request.form['password'], 'sha256')
    db_hash = 'password'
    db_id = 'admin'

    if check_password_hash(pwd_hash, db_hash) and request.form['username'] == db_id:

