from peewee import *

db = SqliteDatabase('data.db')

class BaseModel(Model):
    class Meta:
        database = db

class Invoice(BaseModel):
    name = CharField(unique=True)

class User(BaseModel):
    url = CharField()
    username = CharField()
    api_key = CharField()
    odoo_db_name = CharField()

def create_tables():
    db.connect()
    db.create_tables([
        Invoice, User
    ])

    return True