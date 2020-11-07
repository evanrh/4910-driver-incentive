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
            self.conn.exec(sql, item)
            return True
        except Exception as e:
            return False

    def fetch_catalog_items(self, sponsor_id, search = None):
        sql = "SELECT name, description, price, listing_id, img_url FROM product WHERE sponsor_id=%s"
        if search:
            sql += " AND (name REGEXP {} OR description REGEXP {}".format(search)

        try:
            out = self.conn.exec(sql, (sponsor_id, ))
            print('items found: ', out)
            items = list(map(lambda elem:
                                   {
                                        'title': elem[0],
                                        'description': elem[1],
                                        'price': elem[2],
                                        'listing_id': elem[3],
                                        'img_url': elem[4]
                                    },
                             out
                             )
                        )
            print(items)
            return {'items': items}
        except Exception as e:
            print(e)
            return {'items': []}

    def remove(self, sponsor_id, item_id):
        sql = "DELETE FROM product WHERE sponsor_id=%s and listing_id=%s"
        vals = (sponsor_id, item_id)
        
        try:
            self.conn.exec(sql, vals)
            return True
        except Exception as e:
            print(e)
            return False

    def item_in_db(self, listing_id, sponsor_id):
        """ item_in_db = True iff listing_id and sponsor_id pair is contained in database"""
        sql = "SELECT COUNT(*) FROM product WHERE listing_id=%s AND sponsor_id=%s"
        
        try:
            # Will be 0
            out = self.conn.exec(sql, (listing_id, sponsor_id))
            if out:
                return out[0][0] > 0
            print(num)
        except Exception as e:
            return False
    def __del__(self):
        global pool1
        self.conn.close()

class ItemInDB(Exception):
    pass
