from openerp.osv import orm
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.osv.fields import _column
import xmlrpclib

class sd_connection(osv.osv):
    _name = 'sd.connection'
    _columns = {
              'url':fields.char('URL', required=True),
              'username':fields.char('User Name',  required=True),
              'password': fields.char('Password',  required=True),
              'dbname': fields.char('Database Name',  required=True),
              
              }
        
    def test_connection(self, cr, uid, ids, context=None):
        data = self.browse(cr, uid, ids)[0]
        if data:
            url = data.url
            db =data.dbname
            username = data.username
            password = data.password
            common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
            sd_uid = common.authenticate(db, username, password, {})
            if sd_uid:
                raise orm.except_orm(_('Information :'), _("Connection Success."))
            else:
                raise orm.except_orm(_('Error :'), _("Connection Fail."))
    
    def get_connection_data(self, cr, uid, context=None): 
        record_id = self.search(cr, uid, [],limit=1, context=context)
        sd_uid = url = db = password = False
        if record_id:
            data = self.browse(cr, uid, record_id)[0]
            url = data.url
            db =data.dbname
            username = data.username
            password = data.password
            common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
            
            #sd_uid = common.authenticate(db, username, password, {})
            sd_uid = 1#common.authenticate(db, username, password, {})
            if sd_uid: 
                return sd_uid,url,db,password 
            else:
                return sd_uid,url,db,password 
        else:
            return sd_uid,url,db,password         
