from openerp.osv import fields, osv

class res_currency_rate(osv.osv):
    
    _inherit = "res.currency.rate"
     
    _columns = {        
        'rate': fields.float('Rate', digits=(12, 15), help='The rate of the currency to the currency of rate 1'),        
    }