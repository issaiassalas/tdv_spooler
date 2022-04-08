import xmlrpc.client

common = xmlrpc.client.ServerProxy('http://localhost:8070/xmlrpc/2/object')

# # Mitchell Admin
partner = common.execute_kw('odoo', '2', '5bca2101b14b1cc648eddeace4b17b4f3d8a05d9', 'account.move', 'tdv_fp_get_invoices',[[]],{'connection_type': 'server'})

# # Marc Demo
# # partner = common.execute_kw('odoo', '6', 'be9a70c58e7c9481944b4cde3006396017683af3', 'account.move', 'tdv_fp_get_invoices',[[]])

# # Henry
# # partner = common.execute_kw('odoo', '9', 'c2a7831da28bfcf94b56825003b3e5bd27fee726', 'account.move', 'tdv_fp_get_invoices',[[]])

print(partner)


## deee19d6ccdf649151c314fc719649662130b36e