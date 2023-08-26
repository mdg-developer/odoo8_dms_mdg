from openerp.osv import osv, fields, expression
from openerp import api, tools, SUPERUSER_ID

class price_change(osv.osv):
    _name = "price.change"
    
    _columns = {  
        'name': fields.char('Txn', size=64, readonly=True),
        'requested_date': fields.date('Requested Date', readonly=True),
        'requested_by': fields.many2one('res.users', 'Requested By', readonly=True),
        'confirmed_by': fields.many2one('res.users', 'Confirmed By', readonly=True),
        'confirmed_date': fields.date('Confirmed Date', readonly=True),
        'sale_pricelist_id': fields.many2one('product.pricelist', 'Sale Pricelist'),
        'description': fields.text('Description'),
        'approved_by': fields.many2one('res.users', 'Approved By', readonly=True),
        'approved_date': fields.date('Approved Date', readonly=True),
        'cost_pricelist_id': fields.many2one('product.pricelist', 'Cost Pricelist'),
        'line_ids': fields.one2many('price.change.line', 'price_change_id', 'Price Change Lines'),
        'state': fields.selection([('draft', 'Draft'), ('requested', 'Requested'), ('confirmed', 'Confirmed'), ('approved', 'Approved'), ('cancelled', 'Cancelled')], 'Status'),
    }

    _order = 'id desc'
    _defaults = {
        'requested_date': fields.datetime.now,
        'state': 'draft',
    }

class price_change_line(osv.osv):
    _name = "price.change.line"
    _description = "Price Change Line"

    _columns = {
        'price_change_id': fields.many2one('price.change', 'Price Change'),
        'product_id':fields.many2one('product.product', 'Product'),
        'product_code':fields.char('Product Code'),
        'uom_ratio': fields.char('Packing Size'),
        'uom_id':fields.many2one('product.uom', 'UOM'),
        'cost_price': fields.float('Cost Price'),
        'current_price': fields.float('Current Price'),
        'new_price': fields.float('New Price'),
        'current_margin': fields.float('Current Margin(%)'),
        'new_margin': fields.float('New Margin(%)'),
    }

    def create(self, cursor, user, vals, context=None):
        if vals.get('product_id'):
            product_obj = self.pool.get('product.product')
            product_obj = product_obj.browse(cr, uid, vals.get('product_id'), context=context)
            product_code = product_obj.default_code
            uom_ratio = product_obj.uom_ratio
            uom_id = product_obj.report_uom_id.id if product_obj.report_uom_id else None
            vals['product_code'] = product_code
            vals['uom_ratio'] = uom_ratio
            vals['uom_id'] = uom_id
        return super(price_change_line, self).create(cursor, user, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        data = self.browse(cr, uid, ids, context)
        if data.product_id:
            product_obj = self.pool.get('product.product')
            product_obj = product_obj.browse(cr, uid, vals.get('product_id'), context=context)
            product_code = product_obj.default_code
            uom_ratio = product_obj.uom_ratio
            uom_id = product_obj.report_uom_id.id if product_obj.report_uom_id else None
            vals.update({'product_code': product_code,
                         'uom_ratio': uom_ratio,
                         'uom_id': uom_id,
                        })
        res = super(price_change_line, self).write(cr, uid, ids, vals, context=context)
        return res

    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        product_obj = self.pool.get('product.product')
        product_code = None
        uom_ratio = None
        uom_id = None
        if product_id:
            product_obj = product_obj.browse(cr, uid, product_id, context=context)
            product_code = product_obj.default_code
            uom_ratio = product_obj.uom_ratio
            uom_id = product_obj.report_uom_id.id if product_obj.report_uom_id else None
        return {'value': {'product_code': product_code,
                          'uom_ratio': uom_ratio,
                          'uom_id': uom_id,
                          }}

    