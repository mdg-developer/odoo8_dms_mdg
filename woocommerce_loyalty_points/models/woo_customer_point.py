from openerp.osv import fields, osv

class WooCustomerPoint(osv.osv):
    _name = "woo.customer.point"

    _columns = {
        'woo_user_id': fields.char('Woo User ID'),
        'total_points':fields.float('Total Points'),
    }
