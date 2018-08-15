#from odoo import api, fields, models, tools, _
#from locale import currency

from openerp.exceptions import ValidationError, RedirectWarning, except_orm

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.tools import float_compare

class ResCurrenyRate(models.Model):
    _inherit = "res.currency.rate"
    
    #rate = fields.Float(string='Rate', compute='_compute_current_reverse_rate', digits=(12, 15), help='The rate of the currency to the currency of rate 1'),
    #rate = fields.Float(digits=(12, 15), help='The rate of the currency to the currency of rate 1')
    rate_new = fields.Float(string='Rate New',digits=(12, 2), help='The rate of the currency to the currency of rate 1')
     
    @api.multi
    @api.onchange('rate_new') 
    def _compute_current_reverse_rate(self):
        res = []
        vals = {}
        rate_new = 0 
        for currency in self:       
            if currency.currency_id.base != True:
                 
                      
                if currency.rate_new !=0:
                    currency.rate = 1 / currency.rate_new 
#                     vals['rate'] = 1 / currency.rate_new
#                     self.update(vals)                    
#                     return currency.rate_new
                else:
                    currency.rate  = currency.rate_new 
                                      
            else:
                currency.rate  = currency.rate_new 
                
                   
        return res
    
    def convert_rate(self,currency):
        res = []
         
        if currency.company_id.currency_id.id != currency.id:
            if currency.rate !=0:
                return 1 / currency.rate
            else:
                return currency.rate  
             
        else:
            return currency.rate     
        return res

#     @api.multi
#     def name_get(self):
#           
#         return [(currency.id, tools.ustr(currency.rate_new)) for currency in self]
     
#     @api.multi
#     def name_get(self):
#          
#         return [(currency.id, tools.ustr(self.convert_rate(currency))) for currency in self]
        