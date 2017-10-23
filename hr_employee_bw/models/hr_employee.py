from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date,datetime
from dateutil import parser
from openerp.osv.osv import osv_abstract

class hr_employee(osv.osv):
    _inherit = "hr.employee"

    _columns = {
        'myanmar_name': fields.char('Myanmar Name'),
        'weight': fields.char('Weight'),
        'height': fields.char('Height'),
        'facebook': fields.char('Facebook'),
        'ethnic': fields.char('Ethnic'),
        'is_management':fields.boolean('Management'),
        'payroll_cash':fields.boolean('By Cash'),    
        'payroll_bank':fields.boolean('By Card'),
    }   
hr_employee() 
    
    
