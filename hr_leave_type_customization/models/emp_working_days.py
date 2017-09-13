from openerp.osv import fields, osv
from openerp.tools.translate import _
import time

class emp_working_days(osv.osv):

    _name = 'hr.emp.workingdays.permonth'
    
    _columns = {
        'employee_id': fields.many2one('hr.employee','Employee'),        
        'from_date': fields.date('From Date'),
        'to_date': fields.date('To Date'), 
        'month': fields.integer('Month'), 
        'year': fields.integer('Year'), 
        'no_of_days': fields.float('No of Days'), 
    }
    
emp_working_days()