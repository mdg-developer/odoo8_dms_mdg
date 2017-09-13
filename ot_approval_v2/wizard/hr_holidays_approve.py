from openerp.osv import fields, osv
from openerp.tools.translate import _

class hr_holidas_approve(osv.osv_memory):
    _name = "hr.holidays.approve"
    
    def approve_request(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, context=context)
        holidays_obj = self.pool.get('hr.holidays')
        datas = {
             'ids': context.get('active_ids', []),
              'model': 'hr.holidays',
              'form': data
            }
        holidays_id=datas['ids']
        for id in holidays_id: 
            holidays_obj.holidays_validate(cr, uid, id,context=context)   
        return True 
hr_holidas_approve()