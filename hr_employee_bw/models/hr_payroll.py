from openerp.osv import fields, osv

class hr_payslip(osv.osv):
    _inherit = 'hr.payslip'
    _columns = {  
        'is_management': fields.related('employee_id','is_management',type='boolean',relation='hr.employee',string='Managements',store=True),
        }
hr_payslip() 
