
from datetime import datetime, timedelta
import time
from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
from openerp import workflow

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
    
    def _prepare_order_line_invoice_lines(self, cr, uid, line, account_id=False, context=None):

        res = {}
        if not line.invoiced:
            if not account_id:
                if line.product_id:
                    account_id = line.product_id.property_account_income.id
                    if not account_id:
                        account_id = line.product_id.categ_id.property_account_income_categ.id
                    if not account_id:
                        raise osv.except_osv(_('Error!'),
                                _('Please define income account for this product: "%s" (id:%d).') % \
                                    (line.product_id.name, line.product_id.id,))
                else:
                    prop = self.pool.get('ir.property').get(cr, uid,
                            'property_account_income_categ', 'product.category',
                            context=context)
                    account_id = prop and prop.id or False
            uosqty = self._get_line_qty(cr, uid, line, context=context)
            uos_id = self._get_line_uom(cr, uid, line, context=context)
            pu = 0.0
            if uosqty:
                pu = round(line.price_unit * line.product_uom_qty / uosqty,
                        self.pool.get('decimal.precision').precision_get(cr, uid, 'Product Price'))
            fpos = line.order_id.fiscal_position or False
            account_id = self.pool.get('account.fiscal.position').map_account(cr, uid, fpos, account_id)
            if not account_id:
                raise osv.except_osv(_('Error!'),
                            _('There is no Fiscal Position defined or Income category account defined for default properties of Product categories.'))
            res = {
                'name': line.name,
                'sequence': line.sequence,
                'origin': line.order_id.name,
                'account_id': account_id,
                'price_unit': pu,
                'quantity': uosqty,
                'discount': line.discount,
                'discount_amt':line.discount_amt,
                'foc':line.sale_foc,
                'uos_id': uos_id,
                'product_id': line.product_id.id or False,
                'invoice_line_tax_id': [(6, 0, [x.id for x in line.tax_id])],
                'account_analytic_id':line.product_id.product_tmpl_id.categ_id.analytic_account_id.id,
             #   'account_analytic_id': line.order_id.project_id and line.order_id.project_id.id or False,
            }
        return res
    
    def invoice_line_create(self, cr, uid, ids, context=None):
        
        if context is None:
            context = {}

        create_ids = []
        sales = set()
        for line in self.browse(cr, uid, ids, context=context):
            vals = self._prepare_order_line_invoice_lines(cr, uid, line, False, context)
            if vals:
                inv_id = self.pool.get('account.invoice.line').create(cr, uid, vals, context=context)
                self.write(cr, uid, [line.id], {'invoice_lines': [(4, inv_id)]}, context=context)
                sales.add(line.order_id.id)
                create_ids.append(inv_id)
        # Trigger workflow events
        #for sale_id in sales:
        #     workflow.trg_write(uid, 'sale.order', sale_id, cr)
        return create_ids