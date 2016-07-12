from openerp.osv import fields, osv

class purchase(osv.osv):
    _inherit = 'purchase.order'
    _name = "purchase.order"
    _description = "purchase"

    _columns = {
                'principal': fields.many2one('product.principal', 'Principal'),                
                }
    
purchase()