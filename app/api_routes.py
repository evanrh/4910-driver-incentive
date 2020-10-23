from flask_restx import Resource, fields
from app import api
from app.products.etsy_driver import EtsyController
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

@api.route('/sponsor/api/<int:pid>')
class SponsorCatalog(Resource):
    def get(self, pid):
        return {'pid': pid }
