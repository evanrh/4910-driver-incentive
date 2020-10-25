from flask_restx import Resource, fields
from flask_restx import reqparse
from flask import request
from app import api
from app import app
from app.products.etsy_driver import EtsyController
from app.database.db_users import *
from itsdangerous import (TimedJSONWebSignatureSerializer
                            as Serializer, BadSignature, SignatureExpired)
from functools import wraps
import os

conn = EtsyController(os.getenv('ETSY_API_KEY'))

def generate_auth_token(sponsor_username, expiration = 3600):
    s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
    db = getConnection()
    query = "SELECT sponsor_id FROM sponsor WHERE user=%s"
    results = db.query(query, (sponsor_username, ))
    if results:
        return s.dumps({'id': results[0][0]})
    else:
        return None

def verify_auth_token(token):
    # Fetch token from database
    s = Serializer(app.config['SECRET_KEY'])

    try:
        data = s.loads(token)
    except SignatureExpired:
        return False
    except BadSignature:
        return False
    return True

# Decorator to do token based auth
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'X-API-KEY' in request.headers:
            token = request.headers['X-API-KEY']
            if not token:
                return {'message': 'Token is missing'}

            if not verify_auth_token(token):
                return {'message': 'Your token is bad. Generate a new one.'}
            print('TOKEN: {}'.format(token))
            return f(*args, **kwargs)
        else:
            return {'message': 'Token is missing'}
    return decorated

catalog_item = api.model('Catalog_Item', {
    'title': fields.String,
    'url': fields.Url,
    'price': fields.Float,
    'description': fields.String,
    'img_url': fields.Url
})

@api.route('/sponsor/api/')
class SponsorCatalog(Resource):

    @token_required
    @api.doc(security='apikey')
    def get(self):
        return {'pid': 1}

    @token_required
    @api.doc(security='apikey')
    @api.expect(catalog_item)
    def post(self):
        item = api.payload
        print(item)
        return {'data': 'Item added'}, 200
        
@api.route('/sponsor/api/auth/<string:sponsor_username>')
class SponsorAPIAuth(Resource):
    def get(self, sponsor_username):
        token = generate_auth_token(sponsor_username)
        if token:
            return {'token': token.decode('ascii')}, 200
        else:
            return {'message': 'Sponsor name not found'}, 400
