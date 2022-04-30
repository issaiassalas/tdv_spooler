from peewee import *

db = SqliteDatabase('data.db')

class BaseModel(Model):
    class Meta:
        database = db

class Invoice(BaseModel):
    '''
        Odoo invoice db model
    '''
    ref_id = IntegerField() # should be unique
    name = CharField()
    ticket_ref = IntegerField()
    cn_ticket_ref = IntegerField()
    num_report_z = IntegerField()
    fp_serial_num = CharField()
    fp_serial_date = CharField()
    invoice_type = CharField() #in_invoice, out_invoice
    state = CharField() #PENDING, PROCESSING, DONE, FAILED, SENT
    data = TextField() #should save a JSON
    amount_total = FloatField()

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