import xmlrpclib

username = 'admin' #the user
pwd = 'MDGlive@portal'      #the password of the user
dbname = 'mdg_testing_new'    #the database

# Get the uid
sock_common = xmlrpclib.ServerProxy ('http://3.0.28.170:8069/xmlrpc/common')
uid = sock_common.login(dbname, username, pwd)

#replace localhost with the address of the server
sock = xmlrpclib.ServerProxy('http://3.0.28.170:8069/xmlrpc/object')

print 'uid uid',uid

partner_id = sock.execute(dbname, uid, pwd, 'customer.target', 'create_customer_target_data')
print 'called customer'
