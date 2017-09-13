
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class hr_contract(osv.osv):
    '''
    Payslip Worked Days
    '''
    _inherit = 'hr.contract'
    _description = 'Contract'
    _columns = {  
        'is_daily': fields.boolean('Is Daily Wage'),
        'trans_amt':fields.float('Transportation Allowance'),
        'contract_no':fields.char('Contract No'),
        }  