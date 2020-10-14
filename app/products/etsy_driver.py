from etsy2 import Etsy
import json

class EtsyController():
    """ Controller class for talking to the Etsy API. Will return useful results based off of need """

    def __init__(self, api_key=''):
        self.conn = Etsy(api_key=api_key)
        self.limit = 25

    def get_products_keywords(self, keywords=''):
        # TODO Parse results for relevant information
        # Get product name, description, tags, and URL
        results = self.conn.findAllListingActive(keywords=keywords, limit=self.limit)

        needed_elems = ['title', 'description', 'price', 'url']
        for i in range(0,len(results)):
            results[i] = dict(filter(lambda elem: elem[0] in needed_elems, results[i].items()))
        return results

    def get_products_tags(self, tags=[]):
        
        results = self.conn.findAllListingActive(tags=tags, limit=self.limit)
        needed_elems = ['title', 'description', 'price', 'url']

        for i in range(0, len(results)):
            results[i] = dict(filter(lambda elem: elem[0] in needed_elems, results[i]))
        return results

    def get_product_id(self, pid=''):
        results = self.conn.getListing(listing_id=pid)
        results = json.loads(results)
        return results
