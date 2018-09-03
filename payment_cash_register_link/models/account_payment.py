from openerp import models, fields, api,exceptions, _

from openerp.exceptions import Warning as UserError

class AccountPayment(models.Model):
    _inherit ='account.voucher'
    
    bank_statement_id = fields.Many2one(
        'account.bank.statement', string='Bank Statement',
        domain="[('journal_id',  '=', journal_id),('date',  '=', payment_date),('state','=','open')]")
    
    
    @api.multi
    def post(self):
        """ Create the journal items for the payment and update the payment's state to 'posted'.
            A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
            and another in the destination reconciliable account (see _compute_destination_account_id).
            If invoice_ids is not empty, there will be one reconciliable move line per invoice to reconcile with.
            If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
        """
        for rec in self:

            if rec.state != 'draft':
                raise UserError(_("Only a draft payment can be posted."))

            if any(inv.state != 'open' for inv in rec.invoice_ids):
                raise exceptions.ValidationError(_("The payment cannot be processed because the invoice is not open!"))

            # Use the right sequence to set the name
            if rec.payment_type == 'transfer':
                sequence_code = 'account.payment.transfer'
            else:
                if rec.partner_type == 'customer':
                    if rec.payment_type == 'inbound':
                        sequence_code = 'account.payment.customer.invoice'
                    if rec.payment_type == 'outbound':
                        sequence_code = 'account.payment.customer.refund'
                if rec.partner_type == 'supplier':
                    if rec.payment_type == 'inbound':
                        sequence_code = 'account.payment.supplier.refund'
                    if rec.payment_type == 'outbound':
                        sequence_code = 'account.payment.supplier.invoice'
            rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(sequence_code)
            if not rec.name and rec.payment_type != 'transfer':
                raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))

            # Create the journal entry
            amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
            move = rec._create_payment_entry(amount)

            # In case of a transfer, the first journal entry created debited the source liquidity account and credited
            # the transfer account. Now we debit the transfer account and credit the destination liquidity account.
            if rec.payment_type == 'transfer':
                transfer_credit_aml = move.line_ids.filtered(lambda r: r.account_id == rec.company_id.transfer_account_id)
                transfer_debit_aml = rec._create_transfer_entry(amount)
                (transfer_credit_aml + transfer_debit_aml).reconcile()            
            
                                
            rec.write({'state': 'posted', 'move_name': move.name})
            
            if rec.bank_statement_id:
                for statement_id in self.env['account.bank.statement'].browse(rec.bank_statement_id.id):
                    
                    if statement_id:
                        if rec.partner_type == 'customer':
                            if rec.payment_type == 'inbound':
                                if amount < 0:
                                    amount = amount * -1
                            if rec.payment_type == 'outbound':
                                if amount > 0:
                                    amount = amount * -1
                        if rec.partner_type == 'supplier':
                            if rec.payment_type == 'inbound':
                                if amount < 0:
                                    amount = amount * -1
                            if rec.payment_type == 'outbound':
                                if amount > 0:
                                    amount = amount * -1
                        rec.write({'ref': statement_id.name})
                        statement_line_id =self.env['account.bank.statement.line'].create({'name':rec.communication,'amount':amount,'move_name':move.name,'partner_id':rec.partner_id.id,'date':rec.payment_date,'account_id':rec.journal_id.default_debit_account_id.id,'statement_id':statement_id.id})
                        for line in move.line_ids:
                            line.write({'statement_line_id':statement_line_id.id})
                            
        return True