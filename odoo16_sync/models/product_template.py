from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.osv.fields import _column
import xmlrpclib

class product_template(osv.osv):
    _inherit = 'product.template' 
        
    #odoo16_pp_id = fields.intger(string='Odoo16 Product ID')
    _columns = {
        
        'is_sync_cellar':fields.boolean('Is Sync Cellar18'),
             }
        
    def write(self, cr, uid, ids, vals, context=None):
        ''' Store the standard price change in order to be able to retrieve the cost of a product template for a given date'''
#         data = self.browse(cr,uid,ids[0])
#         if data.is_sync_sd == True: 
#             vals['is_sync_sd']=False
                    
        product = self.browse(cr,uid,ids,context)        
        if product.is_sync_cellar == True:
            vals.update({'is_sync_cellar': False});
        res = super(product_template, self).write(cr, uid, ids, vals, context=context)       
        return res
    
    def sync_to_cellar(self, cr, uid, ids, context=None):
        
        sd_uid,url,db,password = self.pool['odoo16.connection'].get_connection_data(cr, uid, context=None)
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
        #promos.rules promos_rules
        ret = super(product_template, self).copy_data(cr, uid, ids[0], default=None, context=context)
        data = self.browse(cr,uid,ids[0])
        product_ids= []



        if data.name:
            lang_id = models.execute_kw(db, sd_uid, password, 'res.lang', 'search',
                                        [[('code', '=', 'en_US')]])

            # Get the display name of the UOM with name 'Units' in English
            uom_name = models.execute_kw(db, sd_uid, password, 'uom.uom', 'name_get',
                                         [[], {'name': data.uom_id.name, 'lang': lang_id[0]}])[0][1]
            po_uom_name = models.execute_kw(db, sd_uid, password, 'uom.uom', 'name_get',
                                         [[], {'name': data.uom_po_id.name, 'lang': lang_id[0]}])[0][1]
            uom_id = models.execute_kw(db, sd_uid, password,
                              'uom.uom', 'search',
                              [[['name', '=', uom_name]]],
                              {'limit': 1})
            uom_po_id = models.execute_kw(db, sd_uid, password,
                                       'uom.uom', 'search',
                                       [[['name', '=',po_uom_name]]],
                                       {'limit': 1})
            categ_id = models.execute_kw(db, sd_uid, password,
                                          'product.category', 'search',
                                          [[['name', '=', data.categ_id.name]]],
                                          {'limit': 1})
            uom_categ_id = models.execute_kw(db, sd_uid, password,
                                       'uom.category', 'search',
                                       [[['name', '=', data.uom_id.category_id.name]]],
                                       {'limit': 1})
            if not uom_categ_id:
                value = {
                    'name': data.uom_id.category.name,

                }
                uom_categ_id = models.execute_kw(db, sd_uid, password, 'uom.category', 'create', [value])

            if not categ_id:
                value = {
                    'name':data.categ_id.name,
                    'property_valuation':data.valuation,
                    'property_cost_method':data.cost_method if data.cost_method in ['standard','average'] else 'fifo'
                }
                categ_id = models.execute_kw(db, sd_uid, password, 'product.category', 'create', [value])
            if not uom_po_id:
                value = {
                    'name': data.uom_po_id.name,
                    'category_id': uom_categ_id[0],
                    'factor': data.uom_po_id.factor,
                    'uom_type': data.uom_po_id.uom_type,
                    'rounding':data.uom_po_id.rounding,
                }
                uom_po_id = models.execute_kw(db, sd_uid, password, 'uom.uom', 'create', [value])

            if not uom_id:
                value = {
                    'name': data.uom_id.name,
                    'category_id': uom_categ_id[0],
                    'factor': data.uom_id.factor,
                    'uom_type': data.uom_id.uom_type,
                    'rounding':data.uom_id.rounding,
                }
                uom_id = models.execute_kw(db, sd_uid, password, 'uom.uom', 'create', [value])

            value =  {
                'name': data.name,
                'uom_id': uom_id[0],
                'uom_po_id': uom_po_id[0],
                'default_code':data.default_code,
                'list_price':data.list_price,
                'standard_price':data.standard_price,
                'sale_ok':data.sale_ok,
                'purchase_ok':data.purchase_ok,
                'available_in_pos':True,
                'categ_id':categ_id,
                'detailed_type':data.type,
                }
            
            product_ids = models.execute_kw(db, sd_uid, password,
                'product.template', 'search',
                [[['name', '=', data.name],['default_code','=',data.default_code]]])
            if product_ids:
            
                for product_id in product_ids:
                    #models.execute_kw(db, uid, password, 'product.template', 'unlink', [product_ids])
                    models.execute_kw(db, uid, password, 'product.template', 'write', [[product_id],value
                                        ]) 
                cr.execute("""UPDATE product_template SET is_sync_cellar='t' WHERE id = %s""", (ids[0],))
            else:        
                sdid = models.execute_kw(db, sd_uid, password, 'product.template', 'create', [value])
                if sdid:
                    product_product_ids = models.execute_kw(db, sd_uid, password,
                    'product.product', 'search',
                    [[['product_tmpl_id', '=', sdid]]])
                    # for product_product_id in product_product_ids:
                    #     models.execute_kw(db, uid, password, 'product.product', 'write', [[product_product_id], {
                    #                             'default_code':data.default_code
                    #                         }])
                
                cr.execute("""UPDATE product_template SET is_sync_cellar='t' WHERE id = %s""", (ids[0],))
            
                    
                                        
              