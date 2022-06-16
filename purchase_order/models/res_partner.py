from openerp.osv import fields, osv
from openerp import tools
from openerp.tools.translate import _

class res_partner(osv.osv):
    _inherit = 'res.partner'    
    _columns = {
                'base_on_payment': fields.selection([('bol_date', 'BOL Date'), ('etd_date', 'ETD Date'), ('eta_date', 'ETA Date'), ('received_date', 'Stock Receiving Date'), ('order_date', 'Order Confirmed Date'), ('invoice_date', 'Invoice Date')], 'Payment Term Base On', required=False),
               }
