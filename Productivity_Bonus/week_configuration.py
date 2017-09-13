

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import workflow

MONTH_SELECTION = [('1','Jan'),
            ('2','Feb'),
            ('3', 'Mar'),
            ('4','Apr'),
            ('5 ','May'),
            ('6','Jun'),
            ('7','Jul'),
            ('8','Aug'),
            ('9','Sep'),
            ('10','Oct'),
            ('11','Nov'),
            ('12','Dec')]

class week_setting(osv.osv):
    _name = "setting.week"
    _description = "Weeks Setting"

    _columns = {
                'name':fields.char('Name'),
                'from_date':fields.date('From Date'),
                'to_date':fields.date('To Date'),
                'year':fields.char('Year'),
                'month':fields.selection(MONTH_SELECTION,'Month'),
                }
    
   
