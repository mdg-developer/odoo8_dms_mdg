from openerp.osv import fields, osv

class saleorder_configuration(osv.osv):
    _name = 'sale.order.configuration'
    _columns = {
                    'customer_type': fields.selection([
                ('pending customer', 'Pending Customer'),
                ('idle customer', 'Idle Customer'),                
            ], 'Customer Type'),
                    'day': fields.integer('Number of Day', required=True),                 
                }
    _sql_constraints = [('customer_type_uniq', 'unique(customer_type)',
                                     'Customer Type should not be same to others!')]
saleorder_configuration()
