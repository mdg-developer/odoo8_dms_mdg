
from openerp import models, fields, api, _
from openerp.osv.osv import except_osv
from openerp.exceptions import Warning


class sale_order(models.Model):
    _inherit = "sale.order"
    
    auto_workflow_process_id = fields.Many2one('sale.workflow.process.ept', string='Workflow Process',readonly=True)    
    payment_id = fields.Many2one('account.voucher', string= 'Payment')

    
    @api.cr_uid_ids_context
    def action_ship_create(self,cr,uid,ids,context={}):
        result=super(sale_order,self).action_ship_create(cr,uid,ids,context)
        picking_ids=[]
        for order in self.browse(cr,uid,ids,context):
            if order.auto_workflow_process_id.auto_check_availability:                
                for picking in order.picking_ids:
                    picking_ids.append(picking.id)
        if picking_ids:
            self.pool.get("stock.picking").action_assign(cr,uid,picking_ids,context)         
        return result

    @api.model
    def _prepare_invoice(self, order, lines):
        invoice_vals = super(sale_order, self)._prepare_invoice(order, lines)
        if order.auto_workflow_process_id and order.auto_workflow_process_id.invoice_date_is_order_date:
            invoice_vals['date_invoice'] = order.date_order        
        return invoice_vals
    
    @api.multi
    def copy(self,default={}):
        default.update({
            'payment_id': False,
            'auto_workflow_process_id':False
        })
        return super(sale_order,self).copy(default)
    
    
    @api.model
    def pay_sale_order(self,order,invoice,journal, amount, date):
        """
        Generate a voucher for the payment

        It will try to match with the invoice of the order by
        matching the payment ref and the invoice origin.

        The invoice does not necessarily exists at this point, so if yes,
        it will be matched in the voucher, otherwise, the voucher won't
        have any invoice lines and the payment lines will be reconciled
        later with "auto-reconcile" if the option is used.
        """
        
        voucher_obj = self.env['account.voucher']
        voucher_line_obj = self.env['account.voucher.line']
        move_line_obj = self.env['account.move.line']
        partner=self.env['res.partner']._find_accounting_partner(invoice.partner_id)
        #journal = self.env['account.journal'].browse(journal_id)

        voucher_vals = {'reference': order.name,
                        'journal_id': journal.id,
                        'period_id': self.env['account.period'].find(dt=date).id,
                        'amount': amount,
                        'date': date,
                        'partner_id': partner.id,
                        'account_id': journal.default_credit_account_id.id,
                        'currency_id': journal.company_id.currency_id.id,
                        'company_id': journal.company_id.id,
                        'type': 'receipt', }

        # Set the payment rate if currency are different
        if journal.currency.id and journal.company_id.currency_id.id != journal.currency.id:
            ctx = dict(self._context)
            ctx.update({'date': date})
            
            currency = journal.company_id.currency_id.with_context(ctx)
            payment_rate_currency = journal.currency.with_context(ctx)
            payment_rate = payment_rate_currency.rate / currency.rate
            voucher_vals.update({
                'payment_rate_currency_id': payment_rate_currency.id,
                'payment_rate': payment_rate,
            })

        voucher_id = voucher_obj.create(voucher_vals)

        # call on change to search the invoice lines
        onchange_voucher = voucher_obj.onchange_partner_id(
            partner_id=partner.id,
            journal_id=journal.id,
            amount=amount,
            currency_id=journal.company_id.currency_id.id,
            ttype='receipt',
            date=date)['value']
            
        # keep in the voucher only the move line of the
        # invoice (eventually) created for this order
        matching_line = {}
        if onchange_voucher.get('line_cr_ids'):
            voucher_lines = onchange_voucher['line_cr_ids']
            line_ids = map(lambda x:x.get('move_line_id'),voucher_lines)
            #line_ids = [line['move_line_id'] for line in voucher_lines]
            matching_ids = move_line_obj.search([('id','in',line_ids),('ref','=',order.name)])
            if len(matching_ids) == len(voucher_lines):
                matching_lines = voucher_lines
            else:
                matching_lines = filter(lambda x:x['move_line_id'] in matching_ids.ids,voucher_lines)    
#             matching_ids = [line.id for line
#                             in move_line_obj.browse(line_ids)
#                             if line.ref == order.name]
#             matching_lines = [line for line
#                               in voucher_lines
#                               if line['move_line_id'] in matching_ids]
            if matching_lines:
                matching_line = matching_lines[0]
                matching_line.update({
                    'amount': amount,
                    'voucher_id': voucher_id.id,
                })

        if matching_line:
            voucher_line_obj.create(matching_line)
        
        voucher_id.signal_workflow('proforma_voucher')
        order.write({'payment_id': voucher_id.id})
        return True    
    @api.multi
    def button_order_confirm(self):
        for order in self:
            if order.auto_workflow_process_id and order.auto_workflow_process_id.order_policy=="prepaid" and not order.payment_id:
                raise Warning(_('User Error!'),
                    _('The sale Order %s Must be paid before validation') % (order.name))
        return super(sale_order, self).button_order_confirm()
    
    
class account_invoice(models.Model):
    _inherit = "account.invoice"
        #TODO propose a merge to add this field by default in acount module
    sale_ids = fields.Many2many("sale.order","sale_order_invoice_rel","invoice_id","order_id",string="Sale Orders")
    
    @api.model
    def reconcile_invoice(self):
        """
        Simple method to reconcile the invoice with the payment generated on the sale order
        """
        obj_move_line = self.env['account.move.line']
        for invoice in self:
            line_ids = []
            payment_amount = 0
            invoice_amount = 0
            if invoice.sale_ids and invoice.sale_ids[0].payment_id and invoice.move_id:
                for move in invoice.sale_ids[0].payment_id.move_ids:
                    if move.credit > 0 and not move.reconcile_id:
                        line_ids.append(move.id)
                        payment_amount += move.credit
                for move in invoice.move_id.line_id:
                    if move.debit > 0 and not move.reconcile_id:
                        line_ids.append(move.id)
                        invoice_amount += move.debit
            balance = abs(payment_amount-invoice_amount)
            precision = self.env['decimal.precision'].precision_get('Account')
            if line_ids and not round(balance, precision):
                account_move_lines = obj_move_line.search([('id','in',line_ids)])
                account_move_lines.reconcile()
        return True
