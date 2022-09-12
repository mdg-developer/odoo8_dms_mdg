from openerp.osv import fields, osv
import logging
from openerp.tools.translate import _
from openerp import api

class product_oos(osv.osv):

    _name = "product.oos"
    _description = "Minimum Stock Quantity Control"


    _columns = {
        # 'branch_id': fields.many2one('res.branch', 'Branch'),
        'branch_id': fields.many2one('res.branch', string="Branch"),
        'updated_by': fields.many2one('res.users', string="Last Updated By"),
        'updated_time': fields.datetime(string='Last Updated On'),
        'retrieved_by': fields.many2one('res.users', string="Last Retrieved By"),
        'retrieved_time': fields.datetime(string='Last Retrieved On'),
        'sku_count':fields.integer('OOS SKU Count',default=0, compute='_compute_sku_count',readonly=1),
        'product_oos_line': fields.one2many('product.oos.line', 'product_oos_id', 'Product OOS Lines'),

    }

    @api.depends('product_oos_line')
    def _compute_sku_count(self):
        sku_count = self.sku_count
        for line in self.product_oos_line:
            if line.oos:
                sku_count +=1

        self.update({
            'sku_count':sku_count
        })


    def retrieve_product(self, cr, uid, ids, context={}):
        oos_line_obj = self.pool.get('product.oos.line')
        product_obj = self.pool.get('product.product')
        oos_obj = self.browse(cr, uid, ids, context=context)

        product_ids = product_obj.search(cr, uid,[('sale_ok', '=', True)], context=context)
        cr.execute('delete from product_oos_line where product_oos_id=%s', (ids[0],))
        for product_id in product_ids:
            flag_prod_obj = product_obj.browse(cr, uid, product_id, context=context)
            oos_line_obj.create(cr, uid, {'product_oos_id': ids[0],
                                          'ecommerce_uom_id':flag_prod_obj.ecommerce_uom_id.id,
                                           'product_id': product_id,
                                         }, context=context)
        oos_obj.update({'retrieved_by': uid, 'retrieved_time': fields.datetime.now()});

    def write(self, cr, uid, ids, vals, context=None):
        vals['updated_by']= uid
        vals['updated_time'] = fields.datetime.now()
        res = super(product_oos, self).write(cr, uid, ids, vals, context=context)
        return res

    def sync_to_woo(self, cr, uid, ids, context=None):

        return
product_oos()


class product_oos_line(osv.osv):

    _name = "product.oos.line"
    _description = "Minimum Stock Quantity Control Line"
    _columns = {
        'product_oos_id': fields.many2one('product.oos', 'Product OOS', required=True, ondelete='cascade'),
        'product_id': fields.many2one('product.product', 'Product Name', readonly=True),
        'ecommerce_uom_id': fields.many2one('product.uom', 'Ecommerce UOM',realated="product_id.ecommerce_uom_id"),
        'min_qty': fields.integer('Minimum Qty(Pcs)'),
        'oos' : fields.boolean("OOS", default=False),

    }


product_oos_line()