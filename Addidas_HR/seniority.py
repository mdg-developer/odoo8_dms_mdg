import time
from openerp import models, fields, api, _

from openerp import netsvc
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class seniority(models.Model):
    _name="hr.seniority"    
    _columns = {    
    'from_month' :fields.integer("From Month" ,required=True),
    'to_month' :fields.integer("To Month" ,required=True),
    'amount' :fields.float("Amount(Kyat)" ,required=True)
    
                }