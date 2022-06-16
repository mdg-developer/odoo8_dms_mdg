from openerp.osv import osv, fields

class res_currency_rate(osv.osv):
    _inherit = "res.currency.rate"
    
    _columns = {
        
        'rate': fields.float('Rate', digits=(12, 15), help='The rate of the currency to the currency of rate 1'),
        
        
    }
res_currency_rate()

class res_currency(osv.osv):
    _inherit = "res.currency"
    
    _columns = {
                'tolerance': fields.float('Exchange Rate tolerance(+-)', digits=(12, 2), help='The rate of the currency to the currency of rate 1'),
               } 