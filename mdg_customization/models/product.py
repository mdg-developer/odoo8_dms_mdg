from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.osv.fields import _column
from openerp import tools
from openerp.tools.translate import _
import time
from itertools import chain
from openerp.exceptions import except_orm

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
    
    def _price_rule_get_multi(self, cr, uid, pricelist, products_by_qty_by_partner, context=None):
        context = context or {}
        date = context.get('date') or time.strftime('%Y-%m-%d')
        date = date[0:10]

        products = map(lambda x: x[0], products_by_qty_by_partner)
        currency_obj = self.pool.get('res.currency')
        product_obj = self.pool.get('product.template')
        product_uom_obj = self.pool.get('product.uom')
        price_type_obj = self.pool.get('product.price.type')

        if not products:
            return {}

        version = False
        for v in pricelist.version_id:
            if ((v.date_start is False) or (v.date_start <= date)) and ((v.date_end is False) or (v.date_end >= date)):
                version = v
                break
        if not version:
            raise osv.except_osv(_('Warning!'), _("At least one pricelist has no active version !\nPlease create or activate one."))
        categ_ids = {}
        for p in products:
            categ = p.categ_id
            while categ:
                categ_ids[categ.id] = True
                categ = categ.parent_id
        categ_ids = categ_ids.keys()

        is_product_template = products[0]._name == "product.template"
        if is_product_template:
            prod_tmpl_ids = [tmpl.id for tmpl in products]
            # all variants of all products
            prod_ids = [p.id for p in
                        list(chain.from_iterable([t.product_variant_ids for t in products]))]
        else:
            prod_ids = [product.id for product in products]
            prod_tmpl_ids = [product.product_tmpl_id.id for product in products]

        # Load all rules
        cr.execute(
            'SELECT i.id '
            'FROM product_pricelist_item AS i '
            'WHERE (product_tmpl_id IS NULL OR product_tmpl_id = any(%s)) '
                'AND (product_id IS NULL OR (product_id = any(%s))) '
                'AND ((categ_id IS NULL) OR (categ_id = any(%s))) '
                'AND (price_version_id = %s) '
            'ORDER BY sequence, min_quantity desc',
            (prod_tmpl_ids, prod_ids, categ_ids, version.id))
        
        item_ids = [x[0] for x in cr.fetchall()]
        items = self.pool.get('product.pricelist.item').browse(cr, uid, item_ids, context=context)

        price_types = {}

        results = {}
        for product, qty, partner in products_by_qty_by_partner:
            results[product.id] = 0.0
            rule_id = False
            price = False

            # Final unit price is computed according to `qty` in the `qty_uom_id` UoM.
            # An intermediary unit price may be computed according to a different UoM, in
            # which case the price_uom_id contains that UoM.
            # The final price will be converted to match `qty_uom_id`.
            qty_uom_id = context.get('uom') or items.product_uom_id.id #changes
       
            price_uom_id = items.product_uom_id.id #changes
            qty_in_product_uom = qty
            #if qty_uom_id != product.uom_id.id:
            if qty_uom_id != items.product_uom_id.id: #changes
                try:
                    qty_in_product_uom = product_uom_obj._compute_qty(
                        cr, uid, context['uom'], qty, product.uom_id.id or product.uos_id.id)
                except except_orm:
                    # Ignored - incompatible UoM in context, use default product UoM
                    pass

            for rule in items:
                if rule.min_quantity and qty_in_product_uom < rule.min_quantity:
                    continue
                if is_product_template:
                    if rule.product_tmpl_id and product.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and not (product.product_variant_count == 1 and product.product_variant_ids[0].id == rule.product_id.id):
                        # product rule acceptable on template if has only one variant
                        continue
                else:
                    if rule.product_tmpl_id and product.product_tmpl_id.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and product.id != rule.product_id.id:
                        continue

                if rule.categ_id:
                    cat = product.categ_id
                    while cat:
                        if cat.id == rule.categ_id.id:
                            break
                        cat = cat.parent_id
                    if not cat:
                        continue

                if rule.base == -1:
                    if rule.base_pricelist_id:
                        price_tmp = self._price_get_multi(cr, uid,
                                rule.base_pricelist_id, [(product,
                                qty, partner)], context=context)[product.id]
                        ptype_src = rule.base_pricelist_id.currency_id.id
                        price_uom_id = qty_uom_id
                        price = currency_obj.compute(cr, uid,
                                ptype_src, pricelist.currency_id.id,
                                price_tmp, round=False,
                                context=context)
                elif rule.base == -2:
                    seller = False
                    for seller_id in product.seller_ids:
                        if (not partner) or (seller_id.name.id != partner):
                            continue
                        seller = seller_id
                    if not seller and product.seller_ids:
                        seller = product.seller_ids[0]
                    if seller:
                        qty_in_seller_uom = qty
                        seller_uom = seller.product_uom.id
                        if qty_uom_id != seller_uom:
                            qty_in_seller_uom = product_uom_obj._compute_qty(cr, uid, qty_uom_id, qty, to_uom_id=seller_uom)
                        price_uom_id = seller_uom
                        for line in seller.pricelist_ids:
                            if line.min_quantity <= qty_in_seller_uom:
                                price = line.price

                else:
                    if rule.base not in price_types:
                        price_types[rule.base] = price_type_obj.browse(cr, uid, int(rule.base))
                    price_type = price_types[rule.base]

                    # price_get returns the price in the context UoM, i.e. qty_uom_id

                    price_uom_id = qty_uom_id
                    price = currency_obj.compute(
                            cr, uid,
                            price_type.currency_id.id, pricelist.currency_id.id,
                            product_obj._price_get(cr, uid, [product], price_type.field, context=context)[product.id],
                            round=False, context=context)

                if price is not False:
                    price_limit = price
                    price = price * (1.0+(rule.price_discount or 0.0))
                    if rule.price_round:
                        price = tools.float_round(price, precision_rounding=rule.price_round)

                    convert_to_price_uom = (lambda price: product_uom_obj._compute_price(
                                                cr, uid, items.product_uom_id.id, #changes
                                                price, price_uom_id)) 
                    if rule.price_surcharge:
                        price_surcharge = convert_to_price_uom(rule.price_surcharge)
                        price += price_surcharge

                    if rule.price_min_margin:
                        price_min_margin = convert_to_price_uom(rule.price_min_margin)
                        price = max(price, price_limit + price_min_margin)

                    if rule.price_max_margin:
                        price_max_margin = convert_to_price_uom(rule.price_max_margin)
                        price = min(price, price_limit + price_max_margin)

                    rule_id = rule.id
                break

            # Final price conversion to target UoM
            price = product_uom_obj._compute_price(cr, uid, price_uom_id, price, qty_uom_id)

            results[product.id] = (price, rule_id)
        return results    
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
    _columns = {
                 'default_code': fields.char(string="Internal Reference"),
                 'price_discount':fields.float("Price Discount",digits=(16,6)), 
                }
    def product_id_change(self, cr, uid, ids, product_id, context=None):
        if not product_id:
            return {}
        prod = self.pool.get('product.product').read(cr, uid, [product_id], ['code','name'])
        if prod[0]['code']:
            default_code= categ_id = None
            product = self.pool.get('product.product').browse(cr, uid, [product_id], context=context)
            if product:
                default_code = product.default_code
                categ_id = product.product_tmpl_id.categ_id.id 
            return {'value': {'name': prod[0]['code'],'default_code': default_code, 'categ_id':categ_id}}
        return {}    
# class product_pricelist_item(osv.osv):
#     _inherit = "product.pricelist.item"
#     _description = "Pricelist Item"     
#        
#     def create(self, cr, uid, data, context=None):
#         product_obj= self.pool.get('product.product')
#         product_id=data['product_id']
#         product_uom=data['product_uom_id']        
#         if product_id and product_uom:
#             product_data = product_obj.browse(cr,uid,product_id,context=None)
#             uom_id=product_data.product_tmpl_id.uom_id and product_data.product_tmpl_id.uom_id.id or False,
#             big_uom_id=product_data.product_tmpl_id.big_uom_id and product_data.product_tmpl_id.big_uom_id.id or False,
#             big_price=product_data.big_list_price
#             price=product_data.list_price                    
#             if product_uom==uom_id[0]:
#                 list_price=price
#             elif  product_uom==big_uom_id[0]:
#                 list_price=big_price
#             else:
#                 list_price=0
#             data['list_price']=list_price
#             print ' list_pricelist_price',list_price
#         return super(product_pricelist_item, self).create(cr, uid, data, context=context)
#         
#     _columns = {
#         'list_price': fields.float('Basic Price', digits_compute=dp.get_precision('Product Price'),readonly=True),
#         'new_price': fields.float('New Price',
#             digits_compute=dp.get_precision('New Price')),
#         'price_discount': fields.float('Price Discount',digits_compute=dp.get_precision('Product Price')),
#                 }
# 
#     
#     def product_id_change(self, cr, uid, ids, product_id, context=None):
#         if not product_id:
#             return {}
#         
#         prod = self.pool.get('product.product').read(cr, uid, [product_id], ['code', 'name', 'product_tmpl_id'])
#         product_tmpl_id = prod[0]['product_tmpl_id'][0]
#         temp = self.pool.get('product.template').read(cr, uid, [product_tmpl_id], ['list_price'])
#         product_price = temp[0]['list_price']
#         product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)                                                  
#         uom_id = product.product_tmpl_id.uom_id and product.product_tmpl_id.uom_id.id or False,
#         categ_id = product.product_tmpl_id.categ_id.id,
#         product_tmpl_id = product.product_tmpl_id and product.product_tmpl_id.id or False,
#         cr.execute("""SELECT uom.id FROM product_product pp 
#                       LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
#                       LEFT JOIN product_template_product_uom_rel rel ON (rel.product_template_id=pt.id)
#                       LEFT JOIN product_uom uom ON (rel.product_uom_id=uom.id)
#                       WHERE pp.id = %s""", (product.id,))
#         uom_list = cr.fetchall()
#         print 'UOM-->>',uom_list        
#         domain = {'product_uom_id': [('id', 'in', uom_list)]}
# 
#         if prod[0]['code']:
#             return {'value': {'name': prod[0]['code'], 'new_price': product_price, 'list_price':product_price, 'product_uom_id':uom_id, 'base':1, 'categ_id':categ_id, 'product_tmpl_id':product_tmpl_id}
#                     , 'domain': domain}
#         return {}
#     
#     def price_dis_change(self, cr, uid, ids, product_id, price_discount, new_price, price_surcharge, context=None):
#         
#         if not product_id:
#             return {}
#         prod = self.pool.get('product.product').read(cr, uid, [product_id], ['code', 'name', 'product_tmpl_id'])
#         product_tmpl_id = prod[0]['product_tmpl_id'][0]
#         temp = self.pool.get('product.template').read(cr, uid, [product_tmpl_id], ['list_price'])
#         product_price = temp[0]['list_price']
#         
#         if price_discount:
#             new_price = (product_price * (1 + price_discount)) + price_surcharge
#             return {'value':{'new_price':new_price}}
#         return {}
#     def price_subcharge_change(self, cr, uid, ids, product_id, price_discount, new_price, price_surcharge, context=None):
#         if not product_id:
#             return {}
#         prod = self.pool.get('product.product').read(cr, uid, [product_id], ['code', 'name', 'product_tmpl_id'])
#         product_tmpl_id = prod[0]['product_tmpl_id'][0]
#         temp = self.pool.get('product.template').read(cr, uid, [product_tmpl_id], ['list_price'])
#         product_price = temp[0]['list_price']
#         if price_surcharge:
#             new_price = (product_price * (1 + price_discount)) + price_surcharge
#             return {'value':{'new_price':new_price}}
#         return {}
    
class price_list_line(osv.osv):
    _name = 'price.list.line'
    _description = 'Price List Line'           
    _columns = {                
        'team_id':fields.many2one('crm.case.section', 'Line', ondelete='cascade', select=True),
        'property_product_pricelist': fields.many2one('product.pricelist', string="Sale Pricelist", domain=[('type', '=', 'sale')]),
        'is_default':fields.boolean('Default'),
        }
