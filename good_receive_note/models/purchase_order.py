from openerp.osv import fields, osv

class purchase_order(osv.osv):
    _inherit = "purchase.order"
    
    def wkf_confirm_order(self, cr, uid, ids, context=None):
        receive_obj = self.pool.get('good.receive.note')        
        receive_line_obj = self.pool.get('good.receive.note.line')        
        todo = []
        for po in self.browse(cr, uid, ids, context=context):
            receive_id = receive_obj.create(cr, uid, {
                              'purchase_id':po.id,
                              'rfr_ref_no':'PO Create',})      
            if not any(line.state != 'cancel' for line in po.order_line):
                raise osv.except_osv(_('Error!'),_('You cannot confirm a purchase order without any purchase order line.'))
            if po.invoice_method == 'picking' and not any([l.product_id and l.product_id.type in ('product', 'consu') and l.state != 'cancel' for l in po.order_line]):
                raise osv.except_osv(
                    _('Error!'),
                    _("You cannot confirm a purchase order with Invoice Control Method 'Based on incoming shipments' that doesn't contain any stockable item."))
            for line in po.order_line:
                if line.state=='draft':
                    todo.append(line.id)  
                receive_line_obj.create(cr, uid, {
                                                'line_id':receive_id,
                                              'product_id':line.product_id.id,
                                            'description' :line.product_id.product_tmpl_id.description_sale,
                                            'deliver_quantity' : line.product_qty,
                                            'sequence' : line.product_id.product_tmpl_id.sequence,
                                            'product_uom' :line.product_uom.id,
                                              })      
        self.pool.get('purchase.order.line').action_confirm(cr, uid, todo, context)
        for id in ids:
            self.write(cr, uid, [id], {'state' : 'confirmed', 'validator' : uid}, context=context)
        return True