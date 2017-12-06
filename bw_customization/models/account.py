from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from datetime import datetime, timedelta
import calendar
from openerp import tools

OE_DATEFORMAT = "%Y-%m-%d"


class account_fiscalyear(osv.osv):
    _inherit = "account.fiscalyear"
   
    _columns = {
        'trading_no(ka_tha)': fields.char('Trading Numer(Ka Tha)'),
        }