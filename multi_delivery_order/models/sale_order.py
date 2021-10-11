from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import time
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from openerp import SUPERUSER_ID

class sale_order(osv.osv):
    _inherit = "sale.order"
    _columns = {
         'is_confirm': fields.boolean('In Progress',readonly=True), 
         'is_revised': fields.boolean('Is Revised',readonly=True,default=False), 
               
              }
sale_order()


