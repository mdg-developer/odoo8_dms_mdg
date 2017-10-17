import time
from lxml import etree

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp.tools import float_compare
from openerp.report import report_sxw
import openerp

class account_move_line(osv.osv):
    _inherit = 'account.move.line'
    
    _columns = {
                'is_deposit':fields.boolean('Deposit', required=False),
                }