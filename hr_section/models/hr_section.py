from openerp.osv import fields, osv
from openerp.tools.translate import _

class hr_section(osv.osv):

    _name = "hr.section"
    
    def _section_name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)
    
    _columns = {
        'code': fields.char('Code',size=3,required=True),        
        'name': fields.char('Name', required=True),
        'complete_name': fields.function(_section_name_get_fnc, type="char", string='Name'),
        'department_id': fields.many2one('hr.department', 'Department',required=True),
        'parent_section_id': fields.many2one('hr.section', 'Parent Section')
        
    }
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        if isinstance(ids, (int, long)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['name','parent_section_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_section_id']:
                name = record['parent_section_id'][1]+' / '+name
            res.append((record['id'], name))
        return res
hr_section()   

class hr_employee(osv.osv):

    _inherit = "hr.employee"
    
    _columns = {
        
        'section_id': fields.many2one('hr.section', 'Section',required=True)
       
        
    }

class hr_department_transfer(osv.osv):
    _inherit = "hr.department.transfer"
    
    _columns = {
        'frm_section_id': fields.many2one('hr.section', 'From Section',required=True),
        'to_section_id': fields.many2one('hr.section', 'To Section',required=True),
        'badge_id': fields.char('Badge ID'),        
                }
    def onchange_employee(self, cr, uid, ids, employee_id, context=None):

        res = {'value': {'src_id': False, 'src_contract_id': False,'badge_id':False}}

        if employee_id:
            ee = self.pool.get('hr.employee').browse(
                cr, uid, employee_id, context=context)
            res['value']['src_id'] = ee.contract_id.job_id.id
            res['value']['src_contract_id'] = ee.contract_id.id
            res['value']['src_department_id']=ee.department_id
            res['value']['frm_section_id'] = ee.section_id
            res['value']['badge_id'] = ee.employee_id
        return res    