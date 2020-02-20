from openerp import models, fields, api, _

class account_invoice(models.Model):
    _inherit='account.invoice'  
    
    name = fields.Char(string='Reference/Description', index=True,
        readonly=True, states={'draft': [('readonly', False)]})
    origin = fields.Char(string='Source Document',
        help="Reference of the document that produced this invoice.",
        readonly=True, states={'draft': [('readonly', False)]}, track_visibility='always')
    supplier_invoice_number = fields.Char(string='Supplier Invoice Number',
        help="The reference of this invoice as provided by the supplier.",
        readonly=True, states={'draft': [('readonly', False)]}, track_visibility='always')
    type = fields.Selection([
            ('out_invoice','Customer Invoice'),
            ('in_invoice','Supplier Invoice'),
            ('out_refund','Customer Refund'),
            ('in_refund','Supplier Refund'),
        ], string='Type', readonly=True, index=True, change_default=True,
        default=lambda self: self._context.get('type', 'out_invoice'),
        track_visibility='always')

    number = fields.Char(related='move_id.name', store=True, readonly=True, copy=False, track_visibility='always')
    internal_number = fields.Char(string='Invoice Number', readonly=True,
        default=False, copy=False,
        help="Unique number of the invoice, computed automatically when the invoice is created.", track_visibility='always')
    reference = fields.Char(string='Invoice Reference',
        help="The partner reference of this invoice.", track_visibility='always')
    reference_type = fields.Selection('_get_reference_type', string='Payment Reference',
        required=True, readonly=True, states={'draft': [('readonly', False)]},
        default='none', track_visibility='always')
    comment = fields.Text('Additional Information', track_visibility='always')

    state = fields.Selection([
            ('draft','Draft'),
            ('proforma','Pro-forma'),
            ('proforma2','Pro-forma'),
            ('open','Open'),
            ('paid','Paid'),
            ('cancel','Cancelled'),
        ], string='Status', index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False,
        help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Invoice.\n"
             " * The 'Pro-forma' when invoice is in Pro-forma status,invoice does not have an invoice number.\n"
             " * The 'Open' status is used when user create invoice,a invoice number is generated.Its in open status till user does not pay invoice.\n"
             " * The 'Paid' status is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled.\n"
             " * The 'Cancelled' status is used when user cancel invoice.")
    sent = fields.Boolean(readonly=True, default=False, copy=False,
        help="It indicates that the invoice has been sent.", track_visibility='always')
    date_invoice = fields.Date(string='Invoice Date',
        readonly=True, states={'draft': [('readonly', False)]}, index=True,
        help="Keep empty to use the current date", copy=False, track_visibility='always')
    date_due = fields.Date(string='Due Date',
        readonly=True, states={'draft': [('readonly', False)]}, index=True, copy=False,
        help="If you use payment terms, the due date will be computed automatically at the generation "
             "of accounting entries. The payment term may compute several due dates, for example 50% "
             "now and 50% in one month, but if you want to force a due date, make sure that the payment "
             "term is not set on the invoice. If you keep the payment term and the due date empty, it "
             "means direct payment.", track_visibility='always')
    partner_id = fields.Many2one('res.partner', string='Partner', change_default=True,
        required=True, readonly=True, states={'draft': [('readonly', False)]},
        track_visibility='always')
    payment_term = fields.Many2one('account.payment.term', string='Payment Terms',
        readonly=True, states={'draft': [('readonly', False)]},
        help="If you use payment terms, the due date will be computed automatically at the generation "
             "of accounting entries. If you keep the payment term and the due date empty, it means direct payment. "
             "The payment term may compute several due dates, for example 50% now, 50% in one month.", track_visibility='always')
    period_id = fields.Many2one('account.period', string='Force Period',
        domain=[('state', '!=', 'done')], copy=False,
        help="Keep empty to use the period of the validation(invoice) date.",
        readonly=True, states={'draft': [('readonly', False)]}, track_visibility='always')

    account_id = fields.Many2one('account.account', string='Account',
        required=True, readonly=True, states={'draft': [('readonly', False)]},
        help="The partner account used for this invoice.", track_visibility='always')
    invoice_line = fields.One2many('account.invoice.line', 'invoice_id', string='Invoice Lines',
        readonly=True, states={'draft': [('readonly', False)]}, copy=True, track_visibility='always')
    tax_line = fields.One2many('account.invoice.tax', 'invoice_id', string='Tax Lines',
        readonly=True, states={'draft': [('readonly', False)]}, copy=True, track_visibility='always')
    move_id = fields.Many2one('account.move', string='Journal Entry',
        readonly=True, index=True, ondelete='restrict', copy=False,
        help="Link to the automatically generated Journal Items.", track_visibility='always')

    company_id = fields.Many2one('res.company', string='Company', change_default=True,
        required=True, readonly=True, states={'draft': [('readonly', False)]},
        default=lambda self: self.env['res.company']._company_default_get('account.invoice'), track_visibility='always')
    reconciled = fields.Boolean(string='Paid/Reconciled',
        store=True, readonly=True, compute='_compute_reconciled',
        help="It indicates that the invoice has been paid and the journal entry of the invoice has been reconciled with one or several journal entries of payment.", track_visibility='always')
    partner_bank_id = fields.Many2one('res.partner.bank', string='Bank Account',
        help='Bank Account Number to which the invoice will be paid. A Company bank account if this is a Customer Invoice or Supplier Refund, otherwise a Partner bank account number.',
        readonly=True, states={'draft': [('readonly', False)]}, track_visibility='always')

    move_lines = fields.Many2many('account.move.line', string='Entry Lines',
        compute='_compute_move_lines', track_visibility='always')
    payment_ids = fields.Many2many('account.move.line', string='Payments',
        compute='_compute_payments', track_visibility='always')
    move_name = fields.Char(string='Journal Entry', readonly=True,
        states={'draft': [('readonly', False)]}, copy=False, track_visibility='always')
    user_id = fields.Many2one('res.users', string='Salesperson', track_visibility='onchange',
        readonly=True, states={'draft': [('readonly', False)]},
        default=lambda self: self.env.user)
    fiscal_position = fields.Many2one('account.fiscal.position', string='Fiscal Position',
        readonly=True, states={'draft': [('readonly', False)]}, track_visibility='always')
    commercial_partner_id = fields.Many2one('res.partner', string='Commercial Entity',
        related='partner_id.commercial_partner_id', store=True, readonly=True,
        help="The commercial entity that will be used on Journal Entries for this invoice", track_visibility='always')
    
     
