from flask_restx import Resource, fields
from flask_restx import reqparse
from flask import request
from app import api
from app import app
from app.products.etsy_driver import EtsyController
from app.database import *
from itsdangerous import (TimedJSONWebSignatureSerializer
                            as Serializer, BadSignature, SignatureExpired)
from functools import wraps
import os

conn = EtsyController(os.getenv('ETSY_API_KEY'))

def verify_auth_token(token):
    # Fetch token from database
    pass

# Decorator to do token based auth
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'X-API-KEY' in request.headers:
            token = request.headers['X-API-KEY']
        if not token:
            return {'message': 'Token is missing'}

        if token != 'mytoken':
            return {'message': 'Your token is wrong'}
        print('TOKEN: {}'.format(token))
        return f(*args, **kwargs)
    return decorated
@api.route('/hello')
class Hello(Resource):
    def get(self):
        return {'hello': 'world'}

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

    @api.expect(catalog_item)
    def post(self):
        item = api.payload
        print(item)
        return {'data': 'Item added'}, 200
        
@api.route('/sponsor/api/auth')
class SponsorAPIAuth(Resource):
    def get(self):
        token = generate_auth_token()
        return {'token': token.decode('ascii')}, 200
