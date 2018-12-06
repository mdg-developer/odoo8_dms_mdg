from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from datetime import datetime, timedelta
import calendar
from openerp import tools
from openerp.tools import amount_to_text_en


class AccountInvoice(osv.osv):
    _inherit = "account.invoice"    
    _description = "Invoice"
  
    def amount_to_text(self, amount, currency):
        convert_amount_in_words = amount_to_text_en.amount_to_text(amount, lang='en', currency='')        
        convert_amount_in_words = convert_amount_in_words.replace(' and Zero Cent', ' Only ')         
        return convert_amount_in_words  