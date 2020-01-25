from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.osv.fields import _column
import xmlrpclib

class promos_rules(osv.osv):
    _inherit = 'promos.rules'    
    _columns = {
        'is_sync_sd':fields.boolean('Is Sync SD',track_visibility='always'),
             }
    
    def sync_to_sd(self, cr, uid, ids, context=None):
        
        sd_uid,url,db,password = self.pool['sd.connection'].get_connection_data(cr, uid, context=None)
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
        #promos.rules promos_rules
        ret = super(promos_rules, self).copy_data(cr, uid, ids[0], default=None, context=context)
        data = self.browse(cr,uid,ids[0])
        if ret:
            ret['branch_id'] = [(6, 0, [])]
            ret['sale_channel_id'] = [(6, 0, [])]
        
        if data.name:
            promotion_ids = models.execute_kw(db, sd_uid, password,
                'promos.rules', 'search',
                [[['name', '=', data.name]]])
            if promotion_ids:
                for promotion_id in promotion_ids:
                    models.execute_kw(db, uid, password, 'promos.rules', 'unlink', [promotion_id])
                    
                sdid = models.execute_kw(db, sd_uid, password, 'promos.rules', 'create', [ret])
            else:        
                sdid = models.execute_kw(db, sd_uid, password, 'promos.rules', 'create', [ret]) 
         
        self.write(cr, uid, ids, {'is_sync_sd': True}, context=context)    
          
promos_rules()   