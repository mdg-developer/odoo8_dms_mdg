from openerp.osv import fields, osv

class stock_requisition(osv.osv):
    _inherit = "stock.requisition"
    
    def _get_default_branch(self, cr, uid, context=None):
        branch_id = self.pool.get('res.users')._get_branch(cr, uid, context=context)
        if not branch_id:
            raise osv.except_osv(_('Error!'), _('There is no default branch for the current user!'))
        return branch_id
        
    _columns = {
               'branch_id':fields.many2one('res.branch', 'Branch'),
               }
    _defaults = {
        'branch_id': _get_default_branch,
        }
    
class good_issue_note(osv.osv):
    _inherit = "good.issue.note"
    
    def _get_default_branch(self, cr, uid, context=None):
        branch_id = self.pool.get('res.users')._get_branch(cr, uid, context=context)
        if not branch_id:
            raise osv.except_osv(_('Error!'), _('There is no default branch for the current user!'))
        return branch_id
        
    _columns = {
               'branch_id':fields.many2one('res.branch', 'Branch'),
               }
    _defaults = {
        'branch_id': _get_default_branch,
        }
    
class stock_return(osv.osv):
    _inherit = "stock.return"
    
    def _get_default_branch(self, cr, uid, context=None):
        branch_id = self.pool.get('res.users')._get_branch(cr, uid, context=context)
        if not branch_id:
            raise osv.except_osv(_('Error!'), _('There is no default branch for the current user!'))
        return branch_id
        
    _columns = {
               'branch_id':fields.many2one('res.branch', 'Branch'),
               }
    _defaults = {
        'branch_id': _get_default_branch,
        }    