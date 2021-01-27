from openerp import models,api
import time

class stock_picking(models.Model):    
    _inherit="stock.picking"    
    
    @api.model
    def do_transfer(self):
        super(stock_picking,self).do_transfer()
        for record in self:
            work_flow_process_record=record.sale_id and record.sale_id.auto_workflow_process_id
            if record.invoice_state=='2binvoiced' and work_flow_process_record and work_flow_process_record.create_invoice and record.picking_type_id.code=='outgoing':                                                                           
                stock_picking_onshipping_obj=self.pool.get('stock.invoice.onshipping')
                context=dict(self._context or {})
                context.update({'active_id':record.id,'active_ids':record.ids})
                value={'journal_id':work_flow_process_record.sale_journal_id and work_flow_process_record.sale_journal_id.id}
                invoice_wizard_record=stock_picking_onshipping_obj.create(self._cr,self._uid,value,context=context)
                stock_picking_onshipping_obj.open_invoice(self._cr,self._uid,[invoice_wizard_record],context=context)                
                if work_flow_process_record.validate_invoice:
                    for invoice in record.sale_id.invoice_ids:
                        if invoice.state=='draft' and invoice.type=='out_invoice':
                            invoice.signal_workflow('invoice_open')
                            if work_flow_process_record.register_payment:
                                if work_flow_process_record.invoice_date_is_order_date:
                                    date = record.sale_id.date_order
                                else:
                                    date = time.strftime('%Y-%m-%d %H:%M:%S')
                                amount = invoice.amount_total
                                self.env['sale.order'].pay_sale_order(record.sale_id,invoice,work_flow_process_record.journal_id,amount,date)
                                invoice.reconcile_invoice()                                             
        return True
    @api.model
    def _get_invoice_vals(self, key, inv_type, journal_id, move):
        invoice_vals = super(stock_picking,self)._get_invoice_vals(key, inv_type, journal_id, move)
        order=move.picking_id and move.picking_id.sale_id
        if order and order.auto_workflow_process_id and order.auto_workflow_process_id.invoice_date_is_order_date:
            invoice_vals['date_invoice'] = order.date_order        
        return invoice_vals
        