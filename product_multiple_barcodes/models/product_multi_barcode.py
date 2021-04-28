from openerp.osv import fields, osv

class ProductMultiBarcode(osv.osv):
    _name = 'product.multi.barcode'
    
    _columns = {
                'name' : fields.char('Barcode', required=True),
                'product_tmpl_id' : fields.many2one('product.template', string="Product", required=True, ondelete='cascade'),
    }

    