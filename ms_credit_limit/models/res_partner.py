from openerp.osv import fields, osv

class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
                            'credit_allow':fields.boolean('Credit Allow')
                        }
    
res_partner()
