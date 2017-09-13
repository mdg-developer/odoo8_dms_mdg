from openerp.osv import osv
from openerp.osv import fields 

class employee_report(osv.osv_memory):
    
    _name = 'employee.report'
    _description = 'employee Reporting'
    _columns = {}
employee_report()