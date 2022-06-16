from openerp.osv import fields, osv

class sale_order(osv.osv):

    _inherit = 'sale.order'    
    
    _columns = {
         'getting_point': fields.float('Getting Point'),
         'redeem_point': fields.float('Redeem Point'),
    }