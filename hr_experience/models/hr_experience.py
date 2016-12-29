from openerp.osv import fields, osv
class hr_experience(osv.osv):

    _name = "hr.experience"
  
    _columns = {
        'name': fields.char('Name', required=True),
        'employee_id': fields.many2one('hr.employee', 'Employee',required=True),
        'start_date' : fields.date('Start date'),
        'end_date' : fields.date('End date'),
        'description': fields.text('Description'),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'location': fields.char('Location', help="Location"),
         'expire': fields.boolean('Expire', help="Expire", default=True)
        
    }
hr_experience()   

class hr_employee(osv.osv):
    _inherit = 'hr.employee'
    _columns = {
                'experience_ids':fields.one2many('hr.experience','employee_id',' Professional Experiences'),
    }
hr_employee()
    