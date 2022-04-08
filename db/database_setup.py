from .models import *

db_user = None

def create_database():
    return create_tables()
    
if create_database():
    db_user = User.select().first()

def update_db_user(url='', username='', api_key='', odoo_db_name=''):
    global db_user
    if not db_user:
        db_user = User(
            url=url, 
            username=username, 
            api_key=api_key,
            odoo_db_name=odoo_db_name
        )
        db_user.save()

    else:
        db_user.url = url
        db_user.username = username
        db_user.api_key = api_key
        db_user.odoo_db_name = odoo_db_name
        db_user.save()