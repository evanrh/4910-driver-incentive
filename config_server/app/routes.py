from flask import url_for, redirect, request
from app.auth import AdminAuth
from app import app
import json

# TODO
# Add JSON template for command updates

@app.route('/', methods=['POST'])
def index():
    return 'Hello, world!\n'

@app.route('/commands', methods=['POST'])
def commands():
    """ Send a command in JSON to get a result 
        Required params:
            user: a string of the admin username
            password: a string of the password for the requested user
            command: a string for the command to be executed
    """

    if request.json:
        data = request.json
        if len(data.keys()) < 3:
            return json.dumps({'message': 'Bad format'})
        elif sorted(data.keys()) != sorted(['user', 'password', 'command']):
            return json.dumps({'message': 'Bad format'})
        user = data['user']
        pwd = data['password']
        cmd = data['command']

        with AdminAuth(user, pwd) as auth:
            if auth.check_username() and auth.check_password():
                return json.dumps({'message': 'Doing good so far'})
            else:
                return json.dumps({'message': 'Unauthorized'})
    else:
        return json.dumps({'message': 'Not allowed'})
