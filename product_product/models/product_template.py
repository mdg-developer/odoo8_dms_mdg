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
            for p in product.product_variant_ids:
                self.write(cr,uid,p.product_tmpl_id.id,{'sequence_new':p.sequence},context=None)
        return res
    
    def _search_product_quantity(self, cr, uid, obj, name, domain, context):
        prod = self.pool.get("product.product")
        res = []
        for field, operator, value in domain:
            # to prevent sql injections
            assert field in ('qty_available', 'virtual_available', 'incoming_qty', 'outgoing_qty'), 'Invalid domain left operand'
            assert operator in ('<', '>', '=', '<=', '>='), 'Invalid domain operator'
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
                # 'default_code': fields.char('Product Code'),
                # new column add
                'product_principal_ids':fields.many2one('product.principal', 'Product Principal'),
                #################
                 
                 # copy from panasonic_producty.py of "panansonic_modulue"
                
                'uom_lines':fields.many2many('product.uom'),
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
                'weight_liter': fields.float('Net Weight (Liter)', digits_compute=dp.get_precision('Stock Weight'), help="The net weight in Kg."),
                'weight_net': fields.float('Net Weight(Viss)', digits_compute=dp.get_precision('Stock Weight'), help="The net weight in Kg."),  
                'sequence': fields.related('product_variant_ids', 'sequence', type='integer', string='Sequence', required=True,),
                'sequence_new': fields.integer('Sequence', size=3),
                #'company_id': fields.related('journal_id', 'company_id', type='many2one', relation='res.company', string='Company', store=True, readonly=True)
                      }
     
    _defaults = {
        'valuation': 'manual_periodic',
    }
    
    def create(self, cr, uid,  vals, context=None):
        sequence = 0
        if vals.get('sequence'):
            sequence = vals['sequence']
            print 'vals[sequence]>>>>',vals['sequence']
        new_id = super(product_template, self).create(cr, uid, vals, context=context)
        if sequence != 0: 
           self.write(cr,uid,new_id,{'sequence_new':sequence,'sequence':sequence},context=None)
        return new_id    
    def write(self, cr, uid, ids, vals, context=None):   
        
        if vals.get('sequence'):
            sequence = vals['sequence']
            self.write(cr,uid,ids,{'sequence_new':sequence},context=None)
        
        new_id = super(product_template, self).write(cr, uid, ids, vals, context=context)
        return new_id 
    
product_template()

