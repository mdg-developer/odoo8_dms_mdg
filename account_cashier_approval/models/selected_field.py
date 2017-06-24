import itertools
from lxml import etree
from openerp.osv import fields, osv
from openerp import models, fields, api, _
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp

class account_invoice(models.Model):
    _inherit = "account.invoice"
    
    
    unselected = fields.Boolean(string='Uncleared Check',default=False)   
    
class mobile_ar_collection(models.Model):
    _inherit = "mobile.ar.collection"
     
    unselected = fields.Boolean(string='Uncleared Check',default=False)   
   
    
