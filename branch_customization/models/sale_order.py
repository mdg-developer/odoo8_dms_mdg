from openerp.osv import fields, osv
from openerp.tools.translate import _

class sale_order(osv.osv):
    _inherit = "sale.order"
    
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

    def action_button_confirm(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        self.signal_workflow(cr, uid, ids, 'order_confirm')        
        if context.get('send_email'):
            self.force_quotation_send(cr, uid, ids, context=context)
        
        data = self.browse(cr, uid, ids,context=context)
        if data:
            cr.execute("update stock_picking set branch_id=%s,mobile_order_ref=%s where origin=%s",(data.branch_id.id,data.tb_ref_no,data.name,))
            cr.execute("update stock_move set branch_id=%s where picking_id in(select id from stock_picking where origin=%s)",(data.branch_id.id,data.name,))    
        return True