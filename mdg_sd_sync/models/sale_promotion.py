from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.osv.fields import _column
import xmlrpclib
from openerp.tools.translate import _

class promos_rules(osv.osv):
    _inherit = 'promos.rules'    
    _columns = {
        'is_sync_sd':fields.boolean('Is Sync SD',track_visibility='always'),
             }    
    
    def write(self, cr, uid, ids, vals, context=None):  
        data = self.browse(cr,uid,ids[0])
        if data.is_sync_sd == True: 
            vals['is_sync_sd']=False
        res = super(promos_rules, self).write(cr, uid, ids, vals, context=context)
        return res
    
    def sync_to_sd(self, cr, uid, ids, context=None):
        
        sync_sd = False
        data = self.browse(cr,uid,ids[0])        
        cr.execute('select sale_channel_id from promo_sale_channel_rel where promo_id=%s', (data.id,))
        sale_channel_ids = cr.fetchall()
        if sale_channel_ids:
            for channel in sale_channel_ids:           
                channel_obj = self.pool.get('sale.channel').browse(cr, uid, channel[0], context=context)                
                if channel_obj.code == 'SD':
                    sync_sd = True
                    break
        
        if sync_sd == True:       
            sd_uid,url,db,password = self.pool['sd.connection'].get_connection_data(cr, uid, context=None)
            models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
            #promos.rules promos_rules
            ret = super(promos_rules, self).copy_data(cr, uid, ids[0], default=None, context=context)        
            if ret:
                ret['branch_id'] = [(6, 0, [])]
                channel_ids = models.execute_kw(db, sd_uid, password,
                    'sale.channel', 'search', [[['active', '=', True]]])                
                ret['sale_channel_id'] = [(6, 0, channel_ids)] 
            
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
            
            if data.is_sync_sd != True: 
                self.write(cr, uid, ids, {'is_sync_sd': True}, context=context)    
        
        else:
            raise osv.except_osv(_('Warning!'), _('You can sync to SD for only Sub Distributor Channel.'))
                          
promos_rules()   