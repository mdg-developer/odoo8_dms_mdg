import time
from openerp import netsvc
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class hr_fine(osv.osv):
    _name = "hr.fine"
    _description = "HR Fine"
    
    _columns = {        
        'lost_date': fields.date('Date', select=True,required=True),
        'employee_id': fields.many2one('hr.employee', "Employee", required=True),
        'department_id':fields.many2one('hr.department','Department'),
        'job_id':fields.many2one('hr.job','Job Position'),
        'reason_id':fields.many2one('hr.fine.reason','Reason',required=True),
        'fine_amount': fields.float('Fine Amount'),
        'badge_id': fields.char('Badge ID'),     
   }
    
    def onchange_employee_id(self, cr, uid, ids, employee_id, context=None):
        emp_obj = self.pool.get('hr.employee')
        department_id = False
        job_id=False
        badge_id=False
        if employee_id:
            employee = emp_obj.browse(cr, uid, employee_id, context=context)
            department_id = employee.department_id.id
            job_id=employee.job_id.id
            badge_id=employee.employee_id
        return {'value': {'department_id': department_id, 'job_id':job_id,'badge_id':badge_id}}
    
    def onchange_reason_id(self, cr, uid, ids, reason_id, context=None):
        fs_obj = self.pool.get('hr.fine.reason')
        fine_amount = False
        if reason_id:
            fine_reason = fs_obj.browse(cr, uid, reason_id, context=context)
            fine_amount = fine_reason.fine_amount
        return {'value': {'fine_amount': fine_amount}}
    
class hr_fine_reason(osv.osv):
    _name = "hr.fine.reason"
    _description = "HR Fine Reason"
    
    _columns = {
        'code': fields.char('Code',required=True),
        'name': fields.char('Name',required=True),
        'fine_amount': fields.float('Fine Amount', required=True),
        }