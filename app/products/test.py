from etsy_driver import EtsyController

api_key='5gzqdrc6x4n1sfgqfqa1b7tq'
conn = EtsyController(api_key)

items = conn.get_products_keywords('computer')
print(type(items))
for item in items:
    print(item)
