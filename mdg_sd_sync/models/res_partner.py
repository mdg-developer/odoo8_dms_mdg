from openerp.osv import fields, osv
from openerp import tools
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import calendar
from datetime import datetime
import time
from datetime import date
from dateutil import relativedelta

class res_partner(osv.osv):

    _inherit = 'res.partner'    
    _columns = {  
                'sd_customer': fields.boolean('Sub D' , default=False),
            } 