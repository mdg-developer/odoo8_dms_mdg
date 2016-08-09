from openerp.osv import fields, osv

class mobile_sale(osv.osv):
    _inherit = 'mobile.sale.order'
    _columns = {
        'type':fields.selection([
                ('credit', 'Credit'),
                ('cash', 'Cash'),
                ('consignment', 'Consignment'),
                ('advanced', 'Advanced'),
                ('bank', 'Bank'),
                ('cheque', 'Cheque')
            ], 'Payment Type'),
        'payment_ref':fields.char('Payment Reference')
                        }
    
    
mobile_sale()
