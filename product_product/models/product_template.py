from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class product_template(osv.osv):
    _inherit = 'product.template'

    def _product_available(self, cr, uid, ids, name, arg, context=None):
        res = dict.fromkeys(ids, 0)
        for product in self.browse(cr, uid, ids, context=context):
            res[product.id] = {
                # "reception_count": sum([p.reception_count for p in product.product_variant_ids]),
                # "delivery_count": sum([p.delivery_count for p in product.product_variant_ids]),
                "qty_available": sum([p.qty_available for p in product.product_variant_ids]),
                "virtual_available": sum([p.virtual_available for p in product.product_variant_ids]),
                "incoming_qty": sum([p.incoming_qty for p in product.product_variant_ids]),
                "outgoing_qty": sum([p.outgoing_qty for p in product.product_variant_ids]),
            }
        return res
    
    def _search_product_quantity(self, cr, uid, obj, name, domain, context):
        prod = self.pool.get("product.product")
        res = []
        for field, operator, value in domain:
            # to prevent sql injections
            assert field in ('qty_available', 'virtual_available', 'incoming_qty', 'outgoing_qty'), 'Invalid domain left operand'
            assert operator in ('<', '>', '=', '!=', '<=', '>='), 'Invalid domain operator'
            assert isinstance(value, (float, int)), 'Invalid domain right operand'
            if operator == '=':
                operator = '=='

            product_ids = prod.search(cr, uid, [], context=context)
            ids = []
            if product_ids:
                # TODO: use a query instead of this browse record which is probably making the too much requests, but don't forget
                # the context that can be set with a location, an owner...
                for element in prod.browse(cr, uid, product_ids, context=context):
                    if eval(str(element[field]) + operator + str(value)):
                        ids.append(element.id)
            res.append(('product_variant_ids', 'in', ids))
        return res
    
    _columns = {
                # copy from product.py of odoo9
                'default_code': fields.related('product_variant_ids', 'default_code', type='char', string='Internal Reference'),
                # new column add
                'product_principal_ids':fields.many2one('product.principal', 'Product Principal'),
                
                #################
                           
                 
                 # copy from panasonic_producty.py of "panansonic_modulue"
                
                'uom_lines':fields.many2many('product.uom'),
                'uom_price_lines': fields.one2many('product.uom.price', 'product_id', 'Uom Price Lines',),
                'barcode_no':fields.char('Barcode'),
                'division':fields.many2one('product.division', 'Division'),
                'main_group':fields.many2one('product.maingroup', 'Main Group'),
                'group':fields.many2one('product.group', 'Group'),
                'qty_available': fields.function(_product_available, multi='qty_available',
                type='float', digits_compute=dp.get_precision('Product Unit of Measure'),
                string='Quantity On Hand',
                fnct_search=_search_product_quantity,
                help="Current quantity of products.\n"
                 "In a context with a single Stock Location, this includes "
                 "goods stored at this Location, or any of its children.\n"
                 "In a context with a single Warehouse, this includes "
                 "goods stored in the Stock Location of this Warehouse, or any "
                 "of its children.\n"
                 "stored in the Stock Location of the Warehouse of this Shop, "
                 "or any of its children.\n"
                 "Otherwise, this includes goods stored in any Stock Location "
                 "with 'internal' type."),
                'uom_ratio':fields.char('Packing Size'),
        'categ_id': fields.many2one('product.category','Product Category', required=True, change_default=True, domain="[('type','=','normal')]" ,help="Select category for the current product"),
         'sequence': fields.related('product_variant_ids', 'sequence', type='integer', string='Sequence', required=True),
                 
         'is_price_diff_product':fields.related('product_variant_ids', 'is_price_diff_product', type='boolean', string='Is Price Diff Product'),
         'standard_price': fields.property(type = 'float', digits_compute=dp.get_precision('Cost Price'), 
                                          help="Cost price of the product template used for standard stock valuation in accounting and used as a base price on purchase orders. "
                                               "Expressed in the default unit of measure of the product.",
                                          groups="base.group_user", string="Cost Price"),

                }
     
    _defaults = {
        'valuation': 'manual_periodic',
    }
    _sql_constraints = [('default_code_uniq', 'unique(default_code)',
                                  'Product Code should not be same to others!')
                    ]
     
product_template()
class product_uom_price(osv.osv):
    _name = 'product.uom.price'
    
    def _factor_inv(self, cursor, user, ids, name, arg, context=None):
        res = {}
        for uom in self.browse(cursor, user, ids, context=context):
            res[uom.id] = self._compute_factor_inv(uom.factor)
        return res

    def _factor_inv_write(self, cursor, user, id, name, value, arg, context=None):
        return self.write(cursor, user, id, {'factor': self._compute_factor_inv(value)}, context=context)
    
    
    def onchange_product_uom(self, cr, uid, ids, product_uom,context=None):
        value = {'name': [],'category_id':[],'price': 0.0, 'factor': 1.0}
        if product_uom:
            prod = self.pool.get('product.uom').browse(cr, uid, product_uom, context=context)
            cr.execute("select floor(round(1/factor,2)) as ratio from product_uom where active = true and id=%s", (prod.id,))
            factor = cr.fetchone()[0]
            value = {'category_id':prod.category_id, 'price': 0.0, 'factor': factor}
        return {'value': value}
    
    
    _columns = {
        'uom_ratio':fields.char('Packing Size'),
        'product_id': fields.many2one('product.template', 'Product'),
        'name': fields.many2one('product.uom', 'Unit of Measure', required=True),
        'category_id': fields.many2one('product.uom.categ', 'UoM Category', required=True, ondelete='cascade',
            help="Conversion between Units of Measure can only occur if they belong to the same category. The conversion will be made based on the ratios."),
        'factor': fields.float('Ratio', required=True,readonly=True, digits=0, # force NUMERIC with unlimited precision
            help='How much bigger or smaller this unit is compared to the reference Unit of Measure for this category:\n'\
                    '1 * (reference unit) = ratio * (this unit)'),
        'factor_inv': fields.function(_factor_inv, digits=0, # force NUMERIC with unlimited precision
            fnct_inv=_factor_inv_write,
            string='Bigger Ratio',
            help='How many times this Unit of Measure is bigger than the reference Unit of Measure in this category:\n'\
                    '1 * (this unit) = ratio * (reference unit)', required=True),
        'rounding': fields.float('Rounding Precision', digits=0, required=True,
            help="The computed quantity will be a multiple of this value. "\
                 "Use 1.0 for a Unit of Measure that cannot be further split, such as a piece."),
        'active': fields.boolean('Active', help="By unchecking the active field you can disable a unit of measure without deleting it."),
        'uom_type': fields.selection([('bigger','Bigger than the reference Unit of Measure'),
                                      ('reference','Reference Unit of Measure for this category'),
                                      ('smaller','Smaller than the reference Unit of Measure')],'Type', required=1),
        'price': fields.float('Price', digits=0, required=True),
        'weight': fields.float('Weight(Viss)', required=True),
        'length': fields.float('Length', required=True),
        'width': fields.float('Width', required=True),
        'height': fields.float('Height', required=True),
        'per_pallet':fields.char('Per Pallet', required=False, readonly=False),
    }

    _defaults = {
        'active': 1,
        'rounding': 0.01,
        'factor': 1,
        'uom_type': 'reference',
        'factor': 1.0,
        'price': 0.0,
    }
    

    
product_uom_price()
