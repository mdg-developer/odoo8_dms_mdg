import time
from openerp import models, fields, api, _

from openerp import netsvc
#from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class hr_contract(models.Model):
    _inherit="hr.contract"    

    working_hours = fields.Many2one('resource.calendar', string='Schedule',
        required=True,states={'draft': [('readonly', False)]})
    effective_date = fields.Date(string='Effective Date')
    
    @api.model
    def default_get(self, fields):
        res = super(hr_contract, self).default_get(fields)
        employee_ids = self.env.context.get('active_ids', [])
        if not employee_ids:
            return res
        values = {}
        if employee_ids: 
            employee_obj = self.env['hr.employee']
            employees = employee_obj.browse(employee_ids)
            items = []
            for employee in employees:
                values = {
                    'date_start': employee.initial_employment_date,
                }
        res.update(values)
        return res
    
    @api.multi
    def write(self, vals):
        changes = ''
        
        if vals.get('job_id'):
            changes = ' Job Title,'
        
        if vals.get('wage'):
            changes += ' Wage,' 
        
        if vals.get('struct_id'):
            changes += ' Salary Structure,'
        
        if vals.get('working_hours'):
            changes += ' Schedule,'
        
        if vals.get('state'):
            
            if vals['state'] == 'open':
                self.message_post(body=_("Contract confirm"))
            if vals['state'] == 'pending_done':
                self.message_post(body=_("Contract end"))
            if vals['state'] == 'done':
                self.message_post(body=_("Contract done")) 
                       
        if len(changes) > 0:            
            title =  'Contract updated' + '\n' + changes[:-1]
            self.message_post(body=_(title))                            
        
        return super(hr_contract, self).write(vals)
    
class hr_contract_end(models.Model):
    _inherit="hr.contract.end" 
    badge_id = fields.Char(string='Badge ID')
    
    @api.model
    def default_get(self, fields):
        res = super(hr_contract_end, self).default_get(fields)
        employee_ids = self.env.context.get('active_ids', [])
        if not employee_ids:
            return res
        values = {}
        if employee_ids: 
            employee_obj = self.env['hr.employee']
            employees = employee_obj.browse(employee_ids)
            items = []
            for employee in employees:
                values = {
                    'badge_id': employee.employee_id,
                }
        res.update(values)
        return res
    def set_employee_inactive(self, cr, uid, ids, context=None):

        data = self.read(
            cr, uid, ids[0], [
                'employee_id', 'contract_id', 'date', 'reason_id', 'notes','badge_id'],
            context=context)
        vals = {
            'name': data['date'],
            'employee_id': data['employee_id'][0],
            'badge_id':data['badge_id'],
            'reason_id': data['reason_id'][0],
            'notes': data['notes'],
        }
        contract_obj = self.pool.get('hr.contract')
        contract = contract_obj.browse(
            cr, uid, data['contract_id'][0], context=context)
        contract_obj.setup_pending_done(
            cr, uid, contract, vals, context=context)

        return {'type': 'ir.actions.act_window_close'}