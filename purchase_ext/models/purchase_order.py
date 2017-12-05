from datetime import datetime
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp

class purchase_order(osv.osv):
    _inherit = "purchase.order"

    _columns = {
        'pr_ref' : fields.char('PR Ref'),        
        'eta' : fields.datetime('Expected Time Arrived'),
        'etd' : fields.datetime('Expected Time Departure'),
        'received_date': fields.datetime('Received Date'),
        'earning_date' : fields.datetime('Earning Date'),
        'lc_date': fields.date('L/C Date'),
        'permit_date': fields.date('Permit Date'),
        'remit_date': fields.date('Remit Balance Date'),
        'bl_date': fields.date('B/L Date'),
        'agent_date': fields.date('Agent Date'),
        'target_date': fields.date('Target Date'),
        'finished_date': fields.date('Finished Date'),
    }
    
    def product_tree_view(self, cr, uid, res_id, context=None):
            return self.pool['product.template'].wizard_view(cr, uid, res_id, context)
        
    def _prepare_invoice(self, cr, uid, order, line_ids, context=None):
        """Prepare the dict of values to create the new invoice for a
           purchase order. This method may be overridden to implement custom
           invoice generation (making sure to call super() to establish
           a clean extension chain).

           :param browse_record order: purchase.order record to invoice
           :param list(int) line_ids: list of invoice line IDs that must be
                                      attached to the invoice
           :return: dict of value to create() the invoice
        """
        journal_ids = self.pool['account.journal'].search(
                            cr, uid, [('type', '=', 'purchase'),
                                      ('currency', '=', order.currency_id.id),
                                      ('company_id', '=', order.company_id.id)],
                            limit=1)
        if not journal_ids:
            raise osv.except_osv(
                _('Error!'),
                _('Define purchase journal for this company: "%s" (id:%d).') % \
                    (order.company_id.name, order.company_id.id))
        return {
            'name': order.partner_ref or order.name,
            'reference': order.partner_ref or order.name,
            'account_id': order.partner_id.property_account_payable.id,
            'type': 'in_invoice',
            'partner_id': order.partner_id.id,
            'currency_id': order.currency_id.id,
            'journal_id': len(journal_ids) and journal_ids[0] or False,
            'invoice_line': [(6, 0, line_ids)],
            'origin': order.name,
            'fiscal_position': order.fiscal_position.id or False,
            'payment_term': order.payment_term_id.id or False,
            'company_id': order.company_id.id,
        }
        
purchase_order()


    
    
