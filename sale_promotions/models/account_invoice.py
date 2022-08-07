from openerp.osv import fields
from openerp.osv import osv
class account_invoice_line(osv.osv):

    _inherit = 'account.invoice.line'    
    _columns = {
        'promotion_id': fields.many2one('promos.rules', 'Promotion', readonly=True)
    }