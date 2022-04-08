import xmlrpc.client

class ERPConnection(object):
    uid = None
    common = None
    models = None
    def __init__(self, url='', db='', username='', password=''):
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self._set_commons()
        self.authenticate_user()
        
    def _set_commons(self):
        self.common = xmlrpc.client.ServerProxy(
            f'{self.url}/xmlrpc/2/common'
        )
        self.models = xmlrpc.client.ServerProxy(
            f'{self.url}/xmlrpc/2/object'
        )

    def get_server_version(self):
        return self.common.version()

    def authenticate_user(self):
        self.uid = self.common.authenticate(
            self.db, self.username, self.password, {}
        )

    def retrive_invoices(self, connetion_type='server'):
        return self.call_object(
            'account.move',
            'tdv_fp_get_invoices',
            [[]],
            {
                'connection_type': connetion_type
            }
        )

    def call_object(self, *args, **kwargs):
        print(*args, **kwargs)
        print(self.db, self.uid, self.password)
        return self.models.execute_kw(
            self.db, self.uid, self.password, *args, **kwargs
        )

print(ERPConnection(
    url='http://localhost:8069',
    db='odoo',
    username='admin',
    password='f80e8b7de265b14d63cf2cdf27bef93fe425dc48'
).retrive_invoices())