from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.osv.fields import _column
import xmlrpclib

class promos_rules(osv.osv):
    _inherit = 'promos.rules'    
    _columns = {
        'is_sync_sd':fields.boolean('Is Sync SD'),
             }
    
    def sync_to_sd(self, cr, uid, ids, context=None):
        url ='http://www.mdgpartnersd.com'
        db ='subdeal'
        username = 'admin'
        password ='MDG@portal2019'
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
        #promos.rules promos_rules
        ret = super(promos_rules, self).copy_data(cr, uid, ids[0], default=None, context=context)
        sd_uid = common.authenticate(db, username, password, {})
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
        if ret:
            ret['branch_id'] = [(6, 0, [])]
            ret['sale_channel_id'] = [(6, 0, [])]
        sdid = models.execute_kw(db, sd_uid, password, 'promos.rules', 'create', [ret]) 
        #if sdid:
        #    models.execute_kw(db, sd_uid, password, 'promos.rules', 'write', [sdid],{'branch_id':[(6, 0, [])],'sale_channel_id':[(6, 0, [])]}) 
        self.write(cr, uid, ids, {'is_sync_sd': True}, context=context)    
          
promos_rules()   