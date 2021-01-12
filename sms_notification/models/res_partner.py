from openerp.osv import fields, osv

class res_partner(osv.osv):
    _inherit = 'res.partner'
    
    _columns = {        
        'sms': fields.boolean('SMS',default=False),
        'viber': fields.boolean('Viber',default=False),
    }
    
