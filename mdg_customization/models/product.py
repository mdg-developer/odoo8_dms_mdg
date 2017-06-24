from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.osv.fields import _column

class product_product(osv.osv):
    _inherit = 'product.product'

class product_template(osv.osv):
    _inherit = 'product.template'
    _columns = {
        'big_uom_id': fields.many2one('product.uom', 'Bigger UOM', required=True, help="Default Unit of Measure used for all stock operation."),
        'is_foc':fields.boolean('FOC Item'),
        'is_posm':fields.boolean('POSM Item'),
        'big_list_price': fields.float('Bigger Price', digits_compute=dp.get_precision('Product Price'), help="Base price to compute the customer price. Sometimes called the catalog price."),
        'list_price': fields.float('Smaller Price', digits_compute=dp.get_precision('Product Price'), help="Base price to compute the customer price. Sometimes called the catalog price."),
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
        'items_id': fields.one2many('product.pricelist.item',
            'price_version_id', 'Price List Items', required=False, copy=True),
        'branch_id' : fields.related('pricelist_id', 'branch_id',
                                       type='many2many',
                                       readonly=True,
                                     relation='res.branch',
                                       string='Branch'),
         'date_start': fields.date('Start Date', help="First valid date for the version.", required=True),
        'date_end': fields.date('End Date', help="Last valid date for the version.", required=True),
              }
        
    def retrieve_data(self, cr, uid,ids, context=None):
        item_obj=self.pool.get('product.pricelist.item')        
        product_obj=self.pool.get('product.product')        
        list_obj=self.pool.get('product.pricelist')        
        product_price_type_obj = self.pool.get('product.price.type')
        if ids:
            price_version_data=self.browse(cr, uid, ids[0], context=context)
            price_list_id=price_version_data.pricelist_id.id
            price_list_data=list_obj.browse(cr, uid,price_list_id, context=context)
            type=price_list_data.type
            if type== 'purchase':
                product_price_type_ids = product_price_type_obj.search(cr, uid, [('field', '=', 'standard_price')], context=context)
            elif type == 'sale':
                product_price_type_ids = product_price_type_obj.search(cr, uid, [('field','=','list_price')], context=context)
            else:
                base_id= -1
            if not product_price_type_ids:
                base_id=False
            else:
                pricetype= product_price_type_obj.browse(cr, uid, product_price_type_ids, context=context)[0]
                base_id=pricetype.id
                
            cr.execute("delete from product_pricelist_item where price_version_id=%s",(ids[0],))
            product_ids = product_obj.search(cr, uid, [('is_foc', '=', False),('type','=','product')], context=context) 
            for product in product_ids:                
                product_data=product_obj.browse(cr, uid, product, context=context)
                uom_id= product_data.product_tmpl_id.uom_id.id or False,
                big_uom_id= product_data.product_tmpl_id.big_uom_id.id or False,
                big_price=product_data.big_list_price
                price=product_data.list_price
                name=product_data.product_tmpl_id.default_code
                categ_id=product_data.product_tmpl_id.categ_id.id
                if uom_id!=False:
                    uom_id=uom_id[0]
                if big_uom_id!=False:
                    big_uom_id=big_uom_id[0]
                item_id = item_obj.create(cr, uid, {
                                                    'product_id':product_data.id,
                                                    'name': name,
                                                'new_price':price,
                                          'list_price': price,
                                          'product_uom_id':uom_id,
                                          'base':base_id,
                                          'categ_id':categ_id,
                                          'price_version_id':ids[0]}, context=context)
                item_2_id = item_obj.create(cr, uid, {
                                                    'product_id':product_data.id,
                                                    'name': name,
                                                'new_price':big_price,
                                          'list_price': big_price,
                                          'product_uom_id':big_uom_id,
                                          'base':base_id,
                                          'categ_id':categ_id,
                                          'price_version_id':ids[0]}, context=context)
        return True
    
class product_pricelist_item(osv.osv):
    _inherit = "product.pricelist.item"
    _description = "Pricelist Item"     
       
    def create(self, cr, uid, data, context=None):
        product_obj= self.pool.get('product.product')
        product_id=data['product_id']
        product_uom=data['product_uom_id']        
        if product_id and product_uom:
            product_data = product_obj.browse(cr,uid,product_id,context=None)
            uom_id=product_data.product_tmpl_id.uom_id and product_data.product_tmpl_id.uom_id.id or False,
            big_uom_id=product_data.product_tmpl_id.big_uom_id and product_data.product_tmpl_id.big_uom_id.id or False,
            big_price=product_data.big_list_price
            price=product_data.list_price                    
            if product_uom==uom_id[0]:
                list_price=price
            elif  product_uom==big_uom_id[0]:
                list_price=big_price
            else:
                list_price=0
            data['list_price']=list_price
            print ' list_pricelist_price',list_price
        return super(product_pricelist_item, self).create(cr, uid, data, context=context)
        
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
        product_tmpl_id = product.product_tmpl_id and product.product_tmpl_id.id or False,
        cr.execute("""SELECT uom.id FROM product_product pp 
                      LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                      LEFT JOIN product_template_product_uom_rel rel ON (rel.product_template_id=pt.id)
                      LEFT JOIN product_uom uom ON (rel.product_uom_id=uom.id)
                      WHERE pp.id = %s""", (product.id,))
        uom_list = cr.fetchall()
        print 'UOM-->>',uom_list        
        domain = {'product_uom_id': [('id', 'in', uom_list)]}

        if prod[0]['code']:
            return {'value': {'name': prod[0]['code'], 'new_price': product_price, 'list_price':product_price, 'product_uom_id':uom_id, 'base':1, 'categ_id':categ_id, 'product_tmpl_id':product_tmpl_id}
                    , 'domain': domain}
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
