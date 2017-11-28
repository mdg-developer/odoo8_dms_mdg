from openerp.osv import fields, osv

class hr_employee(osv.osv):
    
    _inherit = ['hr.employee']
    _columns = {
       'hr_mic_id': fields.many2one('hr.mic', 'MIC'),
    } 
    
hr_employee()