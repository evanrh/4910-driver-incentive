import json
from ..database.db_users import getConnection

class CatalogController():
    """ Definition of a catalog item found in api_routes"""
    def __init__(self):
        self.conn = getConnection()

    def insert(self, item: dict, sponsor_id):
        """ item is dict from JSON submitted through API 
            and returns whether or not the items was added to the database """
        sql = """ INSERT INTO product (name, description, price, img_url, listing_id, sponsor_id) VALUES
                  (%(title)s, %(description)s, %(price)s, %(img_url)s, %(listing_id)s, {}) """.format(sponsor_id)
        
        # Raise exception if item in database already
        if self.item_in_db(item['listing_id'], sponsor_id):
            raise ItemInDB("Item already in database")

        try:
            self.conn.query(sql, item)
            return True
        except Exception as e:
            return False

    def item_in_db(self, listing_id, sponsor_id):
        """ item_in_db = True iff listing_id and sponsor_id pair is contained in database"""
        sql = "SELECT COUNT(*) FROM product WHERE listing_id=%s AND sponsor_id=%s"
        
        try:
            # Will be 0
            out = self.conn.query(sql, (listing_id, sponsor_id))
            if out:
                return out[0][0] > 0
            print(num)
        except Exception as e:
            return False

class ItemInDB(Exception):
    pass
