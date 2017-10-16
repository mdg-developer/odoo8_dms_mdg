import time
from openerp import models, fields, api, _

from openerp import netsvc
#from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class hr_contract(models.Model):
    _inherit="hr.contract"    

    is_management = fields.Boolean(related='employee_id.is_management', store=True)
