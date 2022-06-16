from openerp.osv import fields, osv

class res_company(osv.osv):
    _inherit = "res.company"
    
    _columns = {
        'credit_invoice_msg': fields.text(string="Credit invoice message"),        
    }
    