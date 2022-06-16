from openerp.osv import fields, osv
from openerp.tools.translate import _

class account_invoice(osv.osv):
    _inherit = "account.invoice"
    
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
    
class account_voucher(osv.osv):
    _inherit = "account.voucher"
    
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
    
class account_creditnote(osv.osv):
    _inherit = "account.creditnote"
    
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
    
    
class account_move(osv.osv):
    _inherit = "account.move"

    def _check_centralisation(self, cursor, user, ids, context=None):
        for move in self.browse(cursor, user, ids, context=context):
            if move.journal_id.centralisation:
                move_ids = self.search(cursor, user, [
                    ('period_id', '=', move.period_id.id),
                    ('journal_id', '=', move.journal_id.id),
                    ('branch_id', '=', move.branch_id.id),

                    ])
                if len(move_ids) > 1:
                    return False
        return True
        
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
    
    _constraints = [
        (_check_centralisation,
            'You cannot create more than one move per period on a centralized journal.',
            ['journal_id']),
    ]    
class account_move_line(osv.osv):
    _inherit = "account.move.line"
    
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