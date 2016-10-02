import itertools
from lxml import etree
from openerp.osv import fields, osv
from openerp import models, fields, api, _
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp

# mapping invoice type to journal type
TYPE2JOURNAL = {
    'out_invoice': 'sale',
    'in_invoice': 'purchase',
    'out_refund': 'sale_refund',
    'in_refund': 'purchase_refund',
}
class account_invoice(models.Model):
    _inherit = "account.invoice"
    
    @api.model
    def _default_journal(self):
        print ' _default_journal'
        inv_type = self._context.get('type', 'out_invoice')
        inv_types = inv_type if isinstance(inv_type, list) else [inv_type]
        company_id = self._context.get('company_id', self.env.user.company_id.id)
        payment_type=self.payment_type
        if (payment_type=='cash'):
            domain = [
                ('type', 'in', filter(None, map(TYPE2JOURNAL.get, inv_types))),
                ('direct_cash_sale','=',True),
                ('company_id', '=', company_id),
            ]
        elif (payment_type=='credit'):
            domain = [
                ('type', 'in', filter(None, map(TYPE2JOURNAL.get, inv_types))),
                ('credit_journal','=',True),                
                ('company_id', '=', company_id),
            ]
        else:         
            domain = [
                ('type', 'in', filter(None, map(TYPE2JOURNAL.get, inv_types))),
                ('company_id', '=', company_id),
            ]            
        return self.env['account.journal'].search(domain, limit=1)
    
    state = fields.Selection([
                    ('draft','Draft'),
                    ('proforma','Pro-forma'),
                    ('proforma2','Pro-forma'),
                    ('fm_approve','Finance Manager Approved'),
                    ('open','Cashier Approved'),
                    ('paid','Paid'),
                    ('cancel','Cancelled'),
                ], string='Status', index=True, readonly=True, default='draft',
                track_visibility='onchange', copy=False,
                help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Invoice.\n"
                     " * The 'Pro-forma' when invoice is in Pro-forma status,invoice does not have an invoice number.\n"
                     " * The 'Open' status is used when user create invoice,a invoice number is generated.Its in open status till user does not pay invoice.\n"
                     " * The 'Paid' status is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled.\n"
                     " * The 'Cancelled' status is used when user cancel invoice.")
    payment_type = fields.Selection([
                    ('credit', 'Credit'),
                    ('cash', 'Cash'),
                    ('consignment', 'Consignment'),
#                     ('advanced', 'Advanced')
                    ],string= 'Payment Type',default='credit')
    
    account_id = fields.Many2one('account.account', string='Account',
        required=True, readonly=True, states={'draft': [('readonly', False)]},
        help="The partner account used for this invoice.")
    
    def finance_approve(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'fm_approve'}, context=None)
        return True   
    
    @api.multi    
    def invoice_validate(self):    
        payment_type = self.payment_type
        if payment_type =='cash':
            return self.write({'state': 'paid'})
        else:    
            return self.write({'state': 'open'})