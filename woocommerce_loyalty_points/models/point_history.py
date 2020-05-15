from openerp.osv import fields, osv

class point_history(osv.osv):
    
    _name = "point.history"
    
    _columns = {
            'partner_id':fields.many2one('res.partner', 'Customer'),            
            'date':fields.date('Date'),
            'redeem_point':fields.integer('Redeem Point'),
            'balance_point':fields.integer('Balance Point'),
            'getting_point':fields.integer('Getting Point per Order'),
            'membership_id':fields.many2one('membership.config', 'Membership Level'),      
            'order_id':fields.many2one('sale.order', 'Sale Order'),     
    }