from etsy2 import Etsy
import json

class EtsyController():
    def __init__(self, api_key=''):
        self.conn = Etsy(api_key=api_key)

    def get_products_keywords(self, keywords=''):
        # TODO Parse results for relevant information
        results = self.conn.findAllListingActive(keywords=keywords)

        return results

    def get_products_tags(self, tags=[]):
        results = self.conn.findAllListingActive(tags=tags)
        return results

    def get_product_id(self, pid=''):
        results = self.conn.getListing(listing_id=pid)
        results = json.loads(results)
        return results
