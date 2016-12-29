from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.osv.fields import _column
class product_product(osv.osv):
    _inherit = 'product.product'
    _columns = {
        'default_code' : fields.char('Internal Reference', select=True, required=True),
        }

class product_template(osv.osv):
    _inherit = 'product.template'
    _columns = {
        'big_uom_id': fields.many2one('product.uom', 'Bigger UOM', required=True, help="Default Unit of Measure used for all stock operation."),
        'is_foc':fields.boolean('FOC Item'),
        'is_posm':fields.boolean('POSM Item'),
        'big_list_price': fields.float('Bigger Price', digits_compute=dp.get_precision('Product Price'), help="Base price to compute the customer price. Sometimes called the catalog price."),
        'list_price': fields.float('Smaller Price', digits_compute=dp.get_precision('Product Price'), help="Base price to compute the customer price. Sometimes called the catalog price."),
         'default_code': fields.related('product_variant_ids', 'default_code', type='char', string='Internal Reference'),
                
                    }
    
    def _get_uom_id(self, cr, uid, *args):
        return self.pool["product.uom"].search(cr, uid, [], limit=1, order='id')[0]
    
    _defaults = {
        'big_uom_id': _get_uom_id,
       
    }
    
class product_pricelist(osv.osv):
    _inherit = 'product.pricelist'
product_pricelist()       
class product_pricelist_version(osv.osv):
    _inherit = 'product.pricelist.version'
    _columns = {
          'branch_id': fields.related('pricelist_id','branch_id',type='many2one',
            readonly=True, relation='res.branch', string='Branch', store=True),                         
                      'date_start': fields.date('Start Date', help="First valid date for the version.", required=True),
        'date_end': fields.date('End Date', help="Last valid date for the version.", required=True),
              }
    def retrieve_data(self, cr, uid,ids, context=None):
        item_obj=self.pool.get('product.pricelist.item')        
        product_obj=self.pool.get('product.product')        
        
        if ids:
            product_ids = product_obj.search(cr, uid, [('is_foc', '=', False),('type','=','product')], context=context) 
            for product in product_ids:
                product_data=product_obj.browse(cr, uid, product, context=context)
                uom_id=product_data.product_tmpl_id.uom_id and product_data.product_tmpl_id.uom_id.id or False,
                big_uom_id=product_data.product_tmpl_id.big_uom_id and product_data.product_tmpl_id.big_uom_id.id or False,
                big_price=product_data.big_list_price
                price=product_data.list_price
                name=product_data.product_tmpl_id.default_code
                categ_id=product_data.product_tmpl_id.categ_id.id
                item_id = item_obj.create(cr, uid, {
                                                    'product_id':product_data.id,
                                                    'name': name,
                                                'new_price':price,
                                          'list_price': price,
                                          'product_uom_id':uom_id,
                                          'base':1,
                                          'categ_id':categ_id,
                                          'price_version_id':ids[0]}, context=context)
                item_2_id = item_obj.create(cr, uid, {
                                                    'product_id':product_data.id,
                                                    'name': name,
                                                'new_price':big_price,
                                          'list_price': big_price,
                                          'product_uom_id':big_uom_id,
                                          'base':1,
                                          'categ_id':categ_id,
                                          'price_version_id':ids[0]}, context=context)
                print 'item_id',item_id ,item_2_id               
        return True
class product_pricelist_item(osv.osv):
    _inherit = "product.pricelist.item"
    _description = "Pricelist Item"        
    _columns = {
        'list_price': fields.float('Basic Price', digits_compute=dp.get_precision('Product Price'),readonly=True),
        'new_price': fields.float('New Price',
            digits_compute=dp.get_precision('New Price')),
        'price_discount': fields.float('Price Discount',digits_compute=dp.get_precision('Product Price')),
                }
    def product_id_change(self, cr, uid, ids, product_id, context=None):
        if not product_id:
            return {}
        prod = self.pool.get('product.product').read(cr, uid, [product_id], ['code', 'name', 'product_tmpl_id'])
        product_tmpl_id = prod[0]['product_tmpl_id'][0]
        temp = self.pool.get('product.template').read(cr, uid, [product_tmpl_id], ['list_price'])
        product_price = temp[0]['list_price']
        product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)                                                  
        uom_id = product.product_tmpl_id.uom_id and product.product_tmpl_id.uom_id.id or False,
        categ_id = product.product_tmpl_id.categ_id.id,
        print ' product_temp'   , product   , categ_id
        product_tmpl_id = product.product_tmpl_id and product.product_tmpl_id.id or False,
        if prod[0]['code']:
            return {'value': {'name': prod[0]['code'], 'new_price': product_price, 'list_price':product_price, 'product_uom_id':uom_id, 'base':1, 'categ_id':categ_id, 'product_tmpl_id':product_tmpl_id}
                 
                    }
        return {}
    
    def price_dis_change(self, cr, uid, ids, product_id, price_discount, new_price, price_surcharge, context=None):
        
        if not product_id:
            return {}
        prod = self.pool.get('product.product').read(cr, uid, [product_id], ['code', 'name', 'product_tmpl_id'])
        product_tmpl_id = prod[0]['product_tmpl_id'][0]
        temp = self.pool.get('product.template').read(cr, uid, [product_tmpl_id], ['list_price'])
        product_price = temp[0]['list_price']
        
        if price_discount:
            new_price = (product_price * (1 + price_discount)) + price_surcharge
            return {'value':{'new_price':new_price}}
        return {}
    def price_subcharge_change(self, cr, uid, ids, product_id, price_discount, new_price, price_surcharge, context=None):
        if not product_id:
            return {}
        prod = self.pool.get('product.product').read(cr, uid, [product_id], ['code', 'name', 'product_tmpl_id'])
        product_tmpl_id = prod[0]['product_tmpl_id'][0]
        temp = self.pool.get('product.template').read(cr, uid, [product_tmpl_id], ['list_price'])
        product_price = temp[0]['list_price']
        if price_surcharge:
            new_price = (product_price * (1 + price_discount)) + price_surcharge
            return {'value':{'new_price':new_price}}
        return {}
    
class price_list_line(osv.osv):
    _name = 'price.list.line'
    _description = 'Price List Line'           
    _columns = {                
        'team_id':fields.many2one('crm.case.section', 'Line', ondelete='cascade', select=True),
        'property_product_pricelist': fields.many2one('product.pricelist', string="Sale Pricelist", domain=[('type', '=', 'sale')]),
        'is_default':fields.boolean('Default'),
        }
