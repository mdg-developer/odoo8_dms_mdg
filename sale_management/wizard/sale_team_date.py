
from openerp.osv import osv, fields

class sale_team_date(osv.osv):
    
    _name='sale.team.date'
    _description = "Sales Team Date" 

    def date_change(self, cr, uid, ids, context=None):
        mod_obj = self.pool.get('ir.model.data')        
        act_obj = self.pool.get('ir.actions.act_window')
        
        if ids:
            date_obj=self.pool.get('sale.team.date').browse(cr, uid, ids[0], context=context)
        cr.execute("update crm_case_section set date=%s",(date_obj.date,))
        return True
#         result = mod_obj.get_object_reference(cr, uid, 'sales_team', 'crm_case_section_salesteams_act')
#         print 'result-----------------------------',result
#         id = result and result[1] or False
#         result = act_obj.read(cr, uid, [id], context=context)[0]
#         return result        
    
    _columns = {
                 'date': fields.date('Date'),
                }
sale_team_date()    