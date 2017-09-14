from openerp.osv import osv,fields

class hr_contract(osv.osv):
    _inherit = 'hr.contract'
    _columns ={
               'leave_control':fields.boolean('Leave Control')
               }
hr_contract()