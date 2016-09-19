
from openerp.osv import osv, fields

class sale_team_date(osv.osv):
    
    _name='sale.team.date'
    _description = "Sales Team Date" 

    def date_change(self, cr, uid, ids, context=None):
        if ids:
            date_obj=self.pool.get('sale.team.date').browse(cr, uid, ids[0], context=context)
        cr.execute("update crm_case_section set date=%s",(date_obj.date,))
        print '-------------------'
        return True        
    _columns = {
                                'date': fields.date('Date'),
                }
sale_team_date()    