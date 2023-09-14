import pytz
from openerp import SUPERUSER_ID, workflow
from datetime import datetime
from dateutil.relativedelta import relativedelta
from operator import attrgetter
from openerp.tools.safe_eval import safe_eval as eval
from openerp.osv import fields, osv
from openerp import api
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.osv.orm import browse_record_list, browse_record, browse_null
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP
from openerp.tools.float_utils import float_compare
  
class stock_location(osv.osv):
    _inherit = 'stock.location' 
    _columns = {
                'address':fields.char('Address'),
                }     
class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}
        new_context = dict(context)
        if not context.get('default_is_burmart_order'):
            new_context.update({
                'default_burmart_order_field_hide': True
            })
        return super(purchase_order, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type,context=new_context, toolbar=toolbar, submenu=submenu)
    
    def action_picking_create(self, cr, uid, ids, context=None):
        for order in self.browse(cr, uid, ids):
            picking_vals = {
                'picking_type_id': order.picking_type_id.id,
                'partner_id': order.partner_id.id,
                'date': order.date_order,
                'origin': order.name,
                'partner_ref':order.partner_ref,
            }
            picking_id = self.pool.get('stock.picking').create(cr, uid, picking_vals, context=context)
            self._create_stock_moves(cr, uid, order, order.order_line, picking_id, context=context)
        return picking_id
    def action_paid(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'paid'}, context=context)

    def action_partial_complete(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'partial_complete'}, context=context)

    def _prepare_inv_line(self, cr, uid, account_id, order_line, context=None):
        """Collects require data from purchase order line that is used to create invoice line
        for that purchase order line
        :param account_id: Expense account of the product of PO line if any.
        :param browse_record order_line: Purchase order line browse record
        :return: Value for fields of invoice lines.
        :rtype: dict
        """
        return {
            'name': order_line.name,
            'account_id': account_id,
            'price_unit': order_line.price_unit or 0.0,
            'quantity': order_line.product_qty,
            'product_id': order_line.product_id.id or False,
            'uos_id': order_line.product_uom.id or False,
            'invoice_line_tax_id': [(6, 0, [x.id for x in order_line.taxes_id])],
            'account_analytic_id': order_line.account_analytic_id.id or False,
            'purchase_line_id': order_line.id,
            'agreed_price':order_line.agreed_price,
            'gross_margin':order_line.gross_margin,
        }

    def write(self, cr, uid, ids, vals, context=None):
        state = vals.get('state')
        if state == 'approved':
            vals.update({
                'check_user':uid,
            })
        if state == 'confirmed':
            vals.update({
                'verify_user':uid
            })
        po_id = super(purchase_order, self).write(cr, uid, ids, vals, context=context)
        return po_id

    _columns = {
           'inword':fields.char('Amount In Words'),     
          'incoterm_id': fields.many2one('stock.incoterms', 'Incoterm', help="International Commercial Terms are a series of predefined commercial terms used in international transactions.", required=True),
          'payment_term_id': fields.many2one('account.payment.term', 'Payment Term', required=True),
#           'is_agreed': fields.boolean('Agreed Price', states={'confirmed':[('readonly', True)],
#                                                                  'approved':[('readonly', True)],
#                                                                  'done':[('readonly', True)]},),
#             'is_margin': fields.boolean('Margin', states={'confirmed':[('readonly', True)],
#                                                                  'approved':[('readonly', True)],
#                                                                  'done':[('readonly', True)]},),
      
             'is_burmart_order': fields.boolean('Is Burmart Order'),
            'payment_method_id': fields.many2one('payment.method', string="Payment Method"),
            'check_user': fields.many2one('res.users', string="Check User"),
            'verify_user': fields.many2one('res.users', string="Verify User"),
            'state': fields.selection([('draft', 'Draft'), ('sent', 'RFQ'),
                                       ('bid', 'Bid Received'), ('confirmed', 'Waiting Approval'),
                                       ('approved', 'Purchase Confirmed'), ('except_picking', 'Shipping Exception'),
                                       ('paid', 'Paid'), ('partial_complete', 'Partial Complete'),
                                       ('except_invoice', 'Invoice Exception'), ('done', 'Done'),
                                       ('cancel', 'Cancelled')], 'Status', readonly=True,
                                      help="The status of the purchase order or the quotation request. "
                                           "A request for quotation is a purchase order in a 'Draft' status. "
                                           "Then the order has to be confirmed by the user, the status switch "
                                           "to 'Confirmed'. Then the supplier must confirm the order to change "
                                           "the status to 'Approved'. When the purchase order is paid and "
                                           "received, the status becomes 'Done'. If a cancel action occurs in "
                                           "the invoice or in the receipt of goods, the status becomes "
                                           "in exception.",
                                      select=True, copy=False),
 }
    
    
    _defaults = {
        'is_burmart_order': False,
    }
#     _defaults = {
#         'is_agreed': False,
#         'is_margin':False,
#         }
#

class payment_method(osv.osv):
    _name = 'payment.method'
    _description = 'Payment Method'

    _columns = {
        'name': fields.char('name'),
    }

class purchase_order_line(osv.osv): 
    _inherit = 'purchase.order.line'
    
    def _amount_margin(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        agreed_price =0
        sale_price=0
        for line in self.browse(cr, uid, ids, context=context):
            if line.product_id.product_tmpl_id.type!='service' :
                product_qty = line.product_qty
                price_unit = line.price_unit
                sale_price = price_unit * product_qty
                agreed_price = product_qty * line.agreed_price
                res[line.id] = agreed_price -sale_price
# 
#             if line.product_id.product_tmpl_id.type=='service' and line.product_id.is_price_diff_product!=True:
#                 res[line.id] = 0

        return res    
    
    _columns = {
#                 'is_agreed': fields.related('order_id', 'is_agreed', type='boolean', string='Agreed', store=True, readonly=True),
#                 'is_margin': fields.related('order_id', 'is_margin', type='boolean', string='Margin', store=True, readonly=True),
                'agreed_price': fields.float('Agreed Price', required=False, digits_compute=dp.get_precision('Cost Price')),
                'gross_margin': fields.function(_amount_margin, string='Gross Margin', digits_compute=dp.get_precision('Cost Price'), store=True),
                'price_unit': fields.float('Unit Price', required=True, digits_compute= dp.get_precision('Cost Price')),

                'market_selling_price': fields.float('Market Price', digits_compute=dp.get_precision('Cost Price')),
                'previous_buying_price': fields.float('Previous Purchased Price',digits_compute=dp.get_precision('Cost Price')),
                'difference_amount': fields.float('Difference Amount'),
                'difference_status': fields.selection([('increased', 'Increased'), ('decreased', 'Decreased')],'Difference Status'),
                'sku_status': fields.selection([('old_sku', 'Old SKU'), ('new_sku', 'New SKU')], 'SKU Status'),
                'estimated_expiration_date': fields.char('Expiration Date(Days)'),
                'margin': fields.char('Margin'),
                'shelf_life': fields.char('Shelf Life(Days)'),
                }

    # Formula:: unit price - previous buying price
    # unit price > previous buying price  = increased
    @api.one
    @api.onchange('price_unit', 'previous_buying_price')
    def onchange_current_previouse_price(self):
        vals = {}
        amt = 0.0
        status = 'increased'
        price_unit = self.price_unit
        previous_buying_price = self.previous_buying_price
        if price_unit and previous_buying_price:
            amt = price_unit - previous_buying_price
            if amt < 0:
                status = 'decreased'
            self.difference_amount = amt
            self.difference_status = status

    @api.one
    @api.onchange('market_selling_price', 'price_unit')
    def onchange_for_margin(self):
        if self.market_selling_price and self.price_unit:
            margin = (( self.market_selling_price - self.price_unit ) / self.market_selling_price)*100
            formatted_margin = "%.2f" % margin
            self.margin = str(formatted_margin) + '%'
    def onchange_product_uom(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
            name=False, price_unit=False, state='draft',currency_id=False, context=None):
        """
        onchange handler of product_uom.
        """
        if context is None:
            context = {}
        if not uom_id:
            return {'value': {'price_unit': price_unit or 0.0, 'name': name or '', 'product_uom' : uom_id or False}}
        context = dict(context, purchase_uom_check=True)
        return self.onchange_product_id(cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=date_order, fiscal_position_id=fiscal_position_id, date_planned=date_planned,
            name=name, price_unit=price_unit, state=state,currency_id=currency_id, context=context)
        
    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
            name=False, price_unit=False, state='draft',currency_id=False, context=None):
        """
        onchange handler of product_id.
        """
        if context is None:
            context = {}

        res = {'value': {'price_unit': price_unit or 0.0, 'name': name or '', 'product_uom' : uom_id or False}}
        if not product_id:
            return res
                        
        if not partner_id:
            return res
        
        if not currency_id:
            return res
        
        product_product = self.pool.get('product.product')
        product_uom = self.pool.get('product.uom')
        res_partner = self.pool.get('res.partner')
        product_pricelist = self.pool.get('product.pricelist')
        account_fiscal_position = self.pool.get('account.fiscal.position')
        account_tax = self.pool.get('account.tax')

        # - check for the presence of partner_id and pricelist_id
        # if not partner_id:
        #    raise osv.except_osv(_('No Partner!'), _('Select a partner in purchase order to choose a product.'))
        # if not pricelist_id:
        #    raise osv.except_osv(_('No Pricelist !'), _('Select a price list in the purchase order form before choosing a product.'))

        # - determine name and notes based on product in partner lang.
        context_partner = context.copy()
        if partner_id:
            lang = res_partner.browse(cr, uid, partner_id).lang
            context_partner.update({'lang': lang, 'partner_id': partner_id})
        product = product_product.browse(cr, uid, product_id, context=context_partner)
        # call name_get() with partner in the context to eventually match name and description in the seller_ids field
        dummy, name = product_product.name_get(cr, uid, product_id, context=context_partner)[0]
        if product.description_purchase:
            name += '\n' + product.description_purchase
        res['value'].update({'name': name})
        cr.execute("""SELECT uom.id FROM product_product pp 
                      LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                      LEFT JOIN product_template_product_uom_rel rel ON (rel.product_template_id=pt.id)
                      LEFT JOIN product_uom uom ON (rel.product_uom_id=uom.id)
                      WHERE pp.id = %s""", (product.id,))
        uom_list = cr.fetchall()
        print 'UOM-->>',uom_list
        # - set a domain on product_uom
        res['domain'] = {'product_uom': [('category_id', '=', product.uom_id.category_id.id),('id', 'in', uom_list)]}

        # - check that uom and product uom belong to the same category
        product_uom_po_id = product.uom_po_id.id
        if not uom_id:
            uom_id = product_uom_po_id

        if product.uom_id.category_id.id != product_uom.browse(cr, uid, uom_id, context=context).category_id.id:
            if context.get('purchase_uom_check') and self._check_product_uom_group(cr, uid, context=context):
                res['warning'] = {'title': _('Warning!'), 'message': _('Selected Unit of Measure does not belong to the same category as the product Unit of Measure.')}
            uom_id = product_uom_po_id

        res['value'].update({'product_uom': uom_id})

        # - determine product_qty and date_planned based on seller info
        if not date_order:
            date_order = fields.datetime.now()


        supplierinfo = False
        precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Product Unit of Measure')
        for supplier in product.seller_ids:
            if partner_id and (supplier.name.id == partner_id):
                supplierinfo = supplier
                if supplierinfo.product_uom.id != uom_id:
                    res['warning'] = {'title': _('Warning!'), 'message': _('The selected supplier only sells this product by %s') % supplierinfo.product_uom.name }
                min_qty = product_uom._compute_qty(cr, uid, supplierinfo.product_uom.id, supplierinfo.min_qty, to_uom_id=uom_id)
                if float_compare(min_qty , qty, precision_digits=precision) == 1:  # If the supplier quantity is greater than entered from user, set minimal.
                    if qty:
                        res['warning'] = {'title': _('Warning!'), 'message': _('The selected supplier has a minimal quantity set to %s %s, you should not purchase less.') % (supplierinfo.min_qty, supplierinfo.product_uom.name)}
                    qty = min_qty
        dt = self._get_date_planned(cr, uid, supplierinfo, date_order, context=context).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        qty = qty or 1.0
        res['value'].update({'date_planned': date_planned or dt})
        if qty:
            res['value'].update({'product_qty': qty})

        price = price_unit
        if price_unit is False or price_unit is None:
            # - determine price_unit and taxes_id
            if pricelist_id:
                date_order_str = datetime.strptime(date_order, DEFAULT_SERVER_DATETIME_FORMAT).strftime(DEFAULT_SERVER_DATE_FORMAT)
                price = product_pricelist.price_get(cr, uid, [pricelist_id],
                        product.id, qty or 1.0, partner_id or False, {'uom': uom_id, 'date': date_order_str})[pricelist_id]
            else:
                price = product.standard_price
                
        taxes = account_tax.browse(cr, uid, map(lambda x: x.id, product.supplier_taxes_id))
        fpos = fiscal_position_id and account_fiscal_position.browse(cr, uid, fiscal_position_id, context=context) or False
        taxes_ids = account_fiscal_position.map_tax(cr, uid, fpos, taxes)

        if product.report_uom_id:
            cr.execute("""select new_price
                        from product_pricelist_item item,product_pricelist_version ppv,product_pricelist pp
                        where item.price_version_id=ppv.id
                        and ppv.pricelist_id=pp.id
                        and pp.id=%s
                        and product_id=%s
                        and product_uom_id=%s""",
                       (pricelist_id, product.id, product.report_uom_id.id,))
            cost_price_data = cr.fetchall()
            if cost_price_data:
                cost_price = cost_price_data[0][0]
                res['value'].update({'previous_buying_price': cost_price})
        
        if partner_id and currency_id and product_id:
            order = 'date desc'
            product_agree_rate_obj = self.pool.get('product.agree.rate')
            cr.execute("select %s::date",(date_order,))
            po_date = cr.fetchone()[0]
            agree_ids =product_agree_rate_obj.search(cr,uid,[('from_date','<=',po_date),('date','>=',po_date),('partner_id','=',partner_id),('currency','=',currency_id)],order=order,limit=1)
            for product_agree in product_agree_rate_obj.browse(cr,uid,agree_ids,context=None):
                for agree_line in product_agree.agress_lines:
                    if agree_line.product_id.id == product_id:
                        if agree_line.agreed_price !=0:
                            res['value'].update({'price_unit': agree_line.agreed_price / product_agree.rate, 'agreed_price': agree_line.agreed_price / product_agree.rate, 'taxes_id': taxes_ids, 'price_subtotal':(agree_line.agreed_price/ product_agree.rate) * qty})
                            return res
        res['value'].update({'price_unit': price, 'agreed_price': price, 'taxes_id': taxes_ids, 'price_subtotal':price * qty })

        return res
class account_invoice_line(osv.osv): 
    _inherit = 'account.invoice.line'    
    
    def _amount_margin(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        agreed_price =0
        sale_price=0
        for line in self.browse(cr, uid, ids, context=context):
            if line.invoice_id.type=='in_invoice' and line.product_id.product_tmpl_id.type!='service' :

                product_qty = line.quantity
                price_unit = line.price_unit
                sale_price = price_unit * product_qty
                agreed_price = product_qty * line.agreed_price
                res[line.id] = agreed_price -sale_price
#             if  line.product_id.product_tmpl_id.type=='service'and line.product_id..is_price_diff_product!=True:
#                 res[line.id] =0
        return res    
        
    _columns = {
                'agreed_price': fields.float('Agreed Price', required=False, digits_compute=dp.get_precision('Cost Price')),
                'gross_margin': fields.function(_amount_margin, string='Gross Margin', digits_compute=dp.get_precision('Cost Price'), store=True),
                }