from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from datetime import datetime, timedelta
import calendar
from openerp import tools

OE_DATEFORMAT = "%Y-%m-%d"
class crm_case_section(osv.osv):
    _inherit = 'crm.case.section'
  
    _columns = {
               'weekly_sales_target': fields.char('Weekly Sales Target'),
               'monthly_sales_target': fields.char('Monthly Sales Target'),
               'annual_sales_target': fields.char('Annual Sales Target'),
                           
        }