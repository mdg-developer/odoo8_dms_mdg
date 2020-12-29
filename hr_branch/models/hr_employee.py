from openerp.osv import fields, osv

class hr_employee(osv.osv):
    
    _inherit='hr.employee'
    _columns={
              'authority_amt': fields.float('Authority Amount'),
              'manager_id':fields.many2one('hr.employee',string='Level 2 Manager'),
              'notify_date': fields.integer('Notify Date'),
              'approve_allow': fields.boolean('Approved Allowed'),
              }
     
hr_employee()