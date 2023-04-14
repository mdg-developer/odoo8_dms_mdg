from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.osv.fields import _column
import xmlrpclib

class product_template(osv.osv):
    _inherit = 'product.template' 
        
    odoo16_pp_id = fields.Intger(string='Odoo16 Product ID')
    _columns = {
        
        'is_sync_sd':fields.boolean('Is Sync SD'),
             }
        
    def write(self, cr, uid, ids, vals, context=None):
        ''' Store the standard price change in order to be able to retrieve the cost of a product template for a given date'''
#         data = self.browse(cr,uid,ids[0])
#         if data.is_sync_sd == True: 
#             vals['is_sync_sd']=False
                    
        product = self.browse(cr,uid,ids,context)        
        if product.is_sync_sd == True:             
            vals.update({'is_sync_sd': False});   
        res = super(product_template, self).write(cr, uid, ids, vals, context=context)       
        return res
    
    def sync_to_sd(self, cr, uid, ids, context=None):
        
        sd_uid,url,db,password = self.pool['sd.connection'].get_connection_data(cr, uid, context=None)
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
        #promos.rules promos_rules
        ret = super(product_template, self).copy_data(cr, uid, ids[0], default=None, context=context)
        data = self.browse(cr,uid,ids[0])
        product_ids= []
        
        if data.name:
            
            product_ids = models.execute_kw(db, sd_uid, password,
                'product.template', 'search',
                [[['name', '=', data.name],['default_code','=',data.default_code]]])
            if product_ids:
            
                for product_id in product_ids:
                    #models.execute_kw(db, uid, password, 'product.template', 'unlink', [product_ids])
                    models.execute_kw(db, uid, password, 'product.template', 'write', [[product_id],ret
                                        ]) 
                cr.execute("""UPDATE product_template SET is_sync_sd='t' WHERE id = %s""", (ids[0],))                   
            else:        
                sdid = models.execute_kw(db, sd_uid, password, 'product.template', 'create', [ret])
                if sdid:
                    product_product_ids = models.execute_kw(db, sd_uid, password,
                    'product.product', 'search',
                    [[['product_tmpl_id', '=', sdid]]])
                    for product_product_id in product_product_ids:                           
                        models.execute_kw(db, uid, password, 'product.product', 'write', [[product_product_id], {
                                                'default_code':data.default_code
                                            }])                
                
                cr.execute("""UPDATE product_template SET is_sync_sd='t' WHERE id = %s""", (ids[0],))
            
                    
                                        
              