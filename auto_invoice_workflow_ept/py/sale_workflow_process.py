from openerp import models, fields, api, _
from openerp.api import Environment
import time

# mapping invoice type to journal type
TYPE2JOURNAL = {
    'out_invoice': 'sale',
    'in_invoice': 'purchase',
    'out_refund': 'sale_refund',
    'in_refund': 'purchase_refund',
}

class sale_workflow_process(models.Model):
    _name = "sale.workflow.process.ept"
    _description = "sale workflow process"

    @api.model
    def _default_journal(self):
        inv_type = self._context.get('type', 'out_invoice')
        inv_types = inv_type if isinstance(inv_type, list) else [inv_type]
        company_id = self._context.get('company_id', self.env.user.company_id.id)
        domain = [
            ('type', 'in', filter(None, map(TYPE2JOURNAL.get, inv_types))),
            ('company_id', '=', company_id),
        ]
        return self.env['account.journal'].search(domain, limit=1)
        
    name = fields.Char(string='Name', size=64)
    validate_order = fields.Boolean("Validate Order",default=False)
    create_invoice = fields.Boolean('Create Invoice',default=False)
    validate_invoice = fields.Boolean(string='Validate Invoice',default=False)
    register_payment=fields.Boolean(string='Register Payment',default=False)
    invoice_date_is_order_date = fields.Boolean('Force Invoice Date', help="If it's check the invoice date will be the same as the order date")
    journal_id = fields.Many2one('account.journal', string='Payment Journal',domain=[('type','in',['cash','bank'])])
    sale_journal_id = fields.Many2one('account.journal', string='Sales Journal',default=_default_journal,domain=[('type','=','sale')])
    picking_policy =  fields.Selection([('direct', 'Deliver each product when available'), ('one', 'Deliver all products at once')], string='Shipping Policy')
    invoice_on =  fields.Selection([('manual', 'On Demand'),('picking', 'On Delivery Order'),('prepaid', 'Before Delivery'),], string='Invoice On')
    auto_check_availability=fields.Boolean("Auto Check Availability",default=False)
    
    @api.onchange("validate_order")
    def onchange_invoice_on(self):
        for record in self:
            if not record.validate_order:
                record.auto_check_availability=False
    @api.model
    def auto_workflow_process(self,auto_workflow_process_id=False,ids=[]):            
        with Environment.manage():
            env_thread1 = Environment(self._cr,self._uid,self._context)
            sale_order_obj=env_thread1['sale.order']
            workflow_process_obj=env_thread1['sale.workflow.process.ept']
            if not auto_workflow_process_id:
                work_flow_process_records=workflow_process_obj.search([])
            else:
                work_flow_process_records=workflow_process_obj.browse(auto_workflow_process_id)

            if not work_flow_process_records:
                return True
            
            for work_flow_process_record in work_flow_process_records:
                if not ids:
                    orders=sale_order_obj.search([('auto_workflow_process_id','=',work_flow_process_record.id),('state','not in',('done','cancel','shipping_except','invoice_except')),('invoiced','=',False)])
                else:
                    orders=sale_order_obj.search([('auto_workflow_process_id','=',work_flow_process_record.id),('id','in',ids)]) 
                if not orders:
                    continue
                for order in orders:
                    if order.invoiced:
                        continue
                    if work_flow_process_record.validate_order:
                        order.action_button_confirm()
                    if not order.invoice_ids:
                        if work_flow_process_record.create_invoice and order.order_policy=='manual' and work_flow_process_record.invoice_on=='manual':
                            order.with_context({'date_invoice':order.date_order}).manual_invoice()
                    if work_flow_process_record.validate_invoice:
                        for invoice in order.invoice_ids:
                            invoice.signal_workflow('invoice_open')
                            journal = work_flow_process_record.journal_id
                            if work_flow_process_record.invoice_date_is_order_date:
                                date = order.date_order
                            else:
                                date = time.strftime('%Y-%m-%d %H:%M:%S')    
                            amount = invoice.amount_total

                            if work_flow_process_record.register_payment:
                                sale_order_obj.pay_sale_order(order,invoice,journal,amount,date)                    
                                invoice.reconcile_invoice()
        return True
