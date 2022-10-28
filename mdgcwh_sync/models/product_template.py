from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.osv.fields import _column
import xmlrpclib

class product_template(osv.osv):
    _inherit = 'product.template' 
        
    #sd_product_tmp_id = fields.Intger(string='SD Product ID')
    _columns = {
        
        'is_sync_cwh':fields.boolean('Is Sync CWH'),
             }
        
    def write(self, cr, uid, ids, vals, context=None):
        ''' Store the standard price change in order to be able to retrieve the cost of a product template for a given date'''
#         data = self.browse(cr,uid,ids[0])
#         if data.is_sync_sd == True: 
#             vals['is_sync_sd']=False
                    
        product = self.browse(cr,uid,ids,context)        
        if product.is_sync_cwh == True:             
            vals.update({'is_sync_cwh': False});   
        res = super(product_template, self).write(cr, uid, ids, vals, context=context)       
        return res
    
    def sync_to_cwh(self, cr, uid, ids, context=None):
        try:

            sd_uid,url,db,password = self.pool['cwh.connection'].get_connection_data(cr, uid, context=None)
            models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
            #promos.rules promos_rules
            #ret = super(product_template, self).copy_data(cr, uid, ids[0], default=None, context=context)
            data = self.browse(cr,uid,ids[0])
            product_ids= []
            
            if data.name:
                
                uom_id = uom_po_id = False
                product_ids = models.execute_kw(db, sd_uid, password,
                    'product.template', 'search',
                    [[['name', '=', data.name],['default_code','=',data.default_code]]])
                categ_ids = models.execute_kw(db, sd_uid, password,
                    'product.category', 'search',
                    [[['name', '=', data.categ_id.name]]])
                uom_ids=models.execute_kw(db, sd_uid, password, 'uom.uom', 'search',  [[('name', '=',data.uom_id.name)]],
                                                         {'limit': 1})
                uom_id = uom_ids[0]
                uom_po_ids=models.execute_kw(db, sd_uid, password, 'uom.uom', 'search',  [[('name', '=',data.report_uom_id.name)]],
                                                         {'limit': 1})
                uom_po_id = uom_po_ids[0]
                
                
                if categ_ids:
                
                    for categ_id in categ_ids:
                        value = {
                                 'default_code':data.default_code,                     
                                    
                                'name':data.name,
                                #'description_sale':data.description_sale,
                                'categ_id':categ_id,
                                'sale_ok':data.sale_ok,
                                'purchase_ok':data.purchase_ok,
                                'uom_id':uom_id,
                                'uom_po_id':uom_po_id,
                                'list_price':data.list_price,
                                'type':data.type,
                                'barcode':data.barcode_no,
                                #'standard_price':data.standard_price,
                                'ctn_weight': data.ctn_weight,
                                'ctn_height': data.ctn_height,
                                'inbound_shelf_life': data.inbound_shelf_life,
                                'viss': data.viss_value,
                                'cbm': data.cbm_value,
                                'pallet_quantity': data.ctn_pallet,
                                'ti': data.ti,
                                'hi': data.hi,
                                'tracking' : 'lot',
                                'use_expiration_date' : True,

                                 }
                if product_ids:
                    print("product write")
                    for product_id in product_ids:
                        
    
                        models.execute_kw(db, sd_uid, password, 'product.template', 'write', [[product_id], value])
                    cr.execute("""UPDATE product_template SET is_sync_cwh='t' WHERE id = %s""", (ids[0],))                   
                else: 
                    print("product create",value)       
                    sdid = models.execute_kw(db, sd_uid, password, 'product.template', 'create', [value])
                    if sdid:
                             
                        product_product_ids = models.execute_kw(db, sd_uid, password,
                        'product.product', 'search',
                        [[['product_tmpl_id', '=', sdid]]])
                  
                    
                    cr.execute("""UPDATE product_template SET is_sync_sd='t' WHERE id = %s""", (ids[0],))
               
        except Exception , e:            
            raise e              
                                        

# class stock_location(osv.osv):
#     _inherit = "stock.location"
#
#     _columns = {
#         'is_cwh_location': fields.boolean('Drop Point Location'),
#     }