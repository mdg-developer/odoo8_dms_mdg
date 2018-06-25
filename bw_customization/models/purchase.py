from openerp.osv import fields, osv
from openerp.tools.translate import _

class purchase_order(osv.osv):
    _inherit = "purchase.order"
    
    def _get_picking_in(self, cr, uid, context=None):
        obj_data = self.pool.get('ir.model.data')
        type_obj = self.pool.get('stock.picking.type')
        user_obj = self.pool.get('res.users')
        company_id = user_obj.browse(cr, uid, uid, context=context).company_id.id
        #types = type_obj.search(cr, uid, [('code', '=', 'incoming'), ('warehouse_id.company_id', '=', company_id)], context=context)
        cr.execute("""select id from stock_picking_type where code='incoming'  and warehouse_id in
                (select id from stock_warehouse where company_id=%s) order by id""", (company_id,))
        stock_picking = cr.fetchall() 
        types=stock_picking[0]
        if not types:
            types = type_obj.search(cr, uid, [('code', '=', 'incoming'), ('warehouse_id', '=', False)], context=context)
            if not types:
                raise osv.except_osv(_('Error!'), _("Make sure you have at least an incoming picking type defined"))
                #raise osv.except_osv(_('Error!'), _("Test"))
        return types[0]
    
    _defaults = {
        'picking_type_id': _get_picking_in,
    }
