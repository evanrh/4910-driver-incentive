from flask_restx import Resource, fields
from app import api
from app.products.etsy_driver import EtsyController
from app.database import *
import os

conn = EtsyController(os.getenv('ETSY_API_KEY'))

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
    def get(self):
        return {'pid': 1}
    @api.expect(catalog_item)

    def post(self):
        item = api.payload
        print(item)
        return {'data': 'Item added'}, 200
        
