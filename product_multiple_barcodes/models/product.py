from openerp.osv import fields, osv
    
class product_template(osv.osv):
    _inherit = "product.template"
    
    _columns = {
                'barcode_ids' : fields.one2many('product.multi.barcode','product_tmpl_id',string='Barcodes')
    }

    
    
