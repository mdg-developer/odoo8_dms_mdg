from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from datetime import datetime, timedelta
import calendar
from openerp import tools

OE_DATEFORMAT = "%Y-%m-%d"
class crm_case_section(osv.osv):
    _inherit = 'res.partner'
  
    _columns = {
        'iso': fields.selection([('yes','Yes'),('no','No'),('n/a','N/A')],'ISO'),       
#         'iso_upload_file': fields.binary('File'),  
#          'binary_field':fields.binary('Your binary field'),
#         'filename':fields.char('Filename'),
        }