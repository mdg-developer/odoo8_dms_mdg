from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class crm_case_section(osv.osv):
    _inherit = 'crm.case.section'
    
    def _get_default_branch(self, cr, uid, context=None):
        branch_id = self.pool.get('res.users')._get_branch(cr, uid, context=context)
        if not branch_id:
            raise osv.except_osv(_('Error!'), _('There is no default branch for the current user!'))
        return branch_id
        
    _columns = {
               'branch_id':fields.many2one('res.branch', 'Branch',required=True),
               }
    _defaults = {
        'branch_id': _get_default_branch,
        }