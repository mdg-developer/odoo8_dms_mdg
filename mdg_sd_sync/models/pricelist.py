from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.osv.fields import _column
import xmlrpclib

class product_pricelist(osv.osv):
    _inherit = 'product.pricelist'    
    _columns = {
        'is_sync_sd':fields.boolean('Is Sync SD'),
             }
    
  
        
    def sync_to_sd(self, cr, uid, ids, context=None):
                    
        # product_pricelist
        ret = super(product_pricelist, self).copy_data(cr, uid, ids[0], default=None, context=context)
        data = self.browse(cr,uid,ids[0])
        #sd_uid = common.authenticate(db, username, password, {})
        sd_uid,url,db,password = self.pool['sd.connection'].get_connection_data(cr, uid, context=None)
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
        if data.name:
            pricelist_id = models.execute_kw(db, sd_uid, password,
                'product.pricelist', 'search',
                [[['name', '=', data.name]]],
                {'limit': 1})
            if pricelist_id:
                #search sd company price list version and item
                sd_version_ids = models.execute_kw(db, sd_uid, password,
                'product.pricelist.version', 'search',
                [[['pricelist_id', '=', pricelist_id]]])
                sd_item_ids = models.execute_kw(db, sd_uid, password,
                'product.pricelist.item', 'search',
                [[['price_version_id', '=', sd_version_ids]]])
                
                #remove sd company price list version and item
                if sd_item_ids:
                    models.execute_kw(db, uid, password, 'product.pricelist.item', 'unlink', [sd_item_ids])
                if sd_version_ids:    
                    models.execute_kw(db, uid, password, 'product.pricelist.version', 'unlink', [sd_version_ids])
                    
                #search mdg company price list version 
                pricelist_version_ids = self.pool['product.pricelist.version'].search(cr,uid,[('pricelist_id','=',ids[0])],context=None)
                if pricelist_version_ids:
                    for version_id in pricelist_version_ids:
                        version_data =self.pool['product.pricelist.version'].browse(cr, uid, version_id, context=context)
                        if version_data:
                            #create sd price list version
                            version_value = {'pricelist_id':pricelist_id[0],
                                             'date_start':version_data.date_start,
                                             'date_end':version_data.date_end,
                                             'company_id':version_data.company_id.id,
                                             'active':version_data.active,
                                             'name':version_data.name
                                             }
                            version_record = models.execute_kw(db, sd_uid, password, 'product.pricelist.version', 'create', [version_value])
                            #search mdg company price list item                         
                            for version_item in self.pool['product.pricelist.item'].search(cr,uid,[('price_version_id','=',version_id)],context=None):
                                version_item_data =self.pool['product.pricelist.item'].copy_data(cr, uid, version_item, default={'price_version_id':version_record}, context=context)
                                #create sd price list itme
                                version_item_record = models.execute_kw(db, sd_uid, password, 'product.pricelist.item', 'create', [version_item_data])
                
                
            else:   
                sdid = models.execute_kw(db, sd_uid, password, 'product.pricelist', 'create', [ret]) 
        #if sdid:
        #    models.execute_kw(db, sd_uid, password, 'promos.rules', 'write', [sdid],{'branch_id':[(6, 0, [])],'sale_channel_id':[(6, 0, [])]}) 
        self.write(cr, uid, ids, {'is_sync_sd': True}, context=context)        
    
product_pricelist()   


