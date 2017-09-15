from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from datetime import datetime, timedelta
import calendar
from openerp import tools

OE_DATEFORMAT = "%Y-%m-%d"
class crm_case_section(osv.osv):
    _inherit = 'crm.case.section'
  
    
    _columns = {
               'weekly_sales_target': fields.float(string='Subtotal', digits=dp.get_precision('Account'),track_visibility='always'),
               'monthly_sales_target': fields.float(string='Monthly Sales Target', digits=dp.get_precision('Account'),track_visibility='always'),
               'annual_sales_target': fields.float(string='Annual Sales Target', digits=dp.get_precision('Account'),track_visibility='always'),

        }