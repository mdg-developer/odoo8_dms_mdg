
from openerp.osv import fields, osv
from openerp.tools.translate import _
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from openerp import tools
import calendar


class account_voucher(osv.osv):

    _inherit = 'account.voucher'
class res_partner(osv.osv):

    _inherit = 'res.partner'    
