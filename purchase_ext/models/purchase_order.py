from datetime import datetime
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
from datetime import datetime
from openerp.tools.float_utils import float_compare

class purchase_order(osv.osv):
    _inherit = "purchase.order"

    _columns = {
        'pr_ref' : fields.char('Sale PR Ref'),              
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
        'pr_ref_purchase' : fields.char('Purchse PR Ref'),
    }
    
    def product_tree_view(self, cr, uid, res_id, context=None):
            return self.pool['product.template'].wizard_view(cr, uid, res_id, context)

    def date_change(self, cr, uid, ids, context=None):
        pickingObj = self.pool.get('stock.picking')
        
        if ids:     
            purchase_data = self.browse(cr, uid, ids, context=context)
            order_no = purchase_data.name
            date = purchase_data.minimum_planned_date
            picking_ids = pickingObj.search(cr, uid, [('origin', '=', order_no), ('state', 'not in', ('cancel', 'done'))])
            for picking_id in picking_ids:
                pickingObj.write(cr, uid, picking_id, {'min_date':date})          
            self.message_post(cr, uid, ids, body=_(" Expected Date Change"), context=context)
            
        return True                                                                                                             
            
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
        
        
    def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id, group_id, context=None):
        ''' prepare the stock move data from the PO line. This function returns a list of dictionary ready to be used in stock.move's create()'''
        product_uom = self.pool.get('product.uom')
        price_unit = order_line.price_unit
        if order_line.taxes_id:
            taxes = self.pool['account.tax'].compute_all(cr, uid, order_line.taxes_id, price_unit, 1.0,
                                                             order_line.product_id, order.partner_id)
            price_unit = taxes['total']
        if order_line.product_uom.id != order_line.product_id.uom_id.id:
            price_unit *= order_line.product_uom.factor / order_line.product_id.uom_id.factor
        if order.currency_id.id != order.company_id.currency_id.id:
            #we don't round the price_unit, as we may want to store the standard price with more digits than allowed by the currency
            price_unit = self.pool.get('res.currency').compute(cr, uid, order.currency_id.id, order.company_id.currency_id.id, price_unit, round=False, context=context)
        res = []
        if order.location_id.usage == 'customer':
            name = order_line.product_id.with_context(dict(context or {}, lang=order.dest_address_id.lang)).display_name
        else:
            name = order_line.name or ''
        move_template = {
            'name': name,
            'product_id': order_line.product_id.id,
            'product_uom': order_line.product_uom.id,
            'product_uos': order_line.product_uom.id,
            'date': order.date_order,
            'date_expected': fields.date.date_to_datetime(self, cr, uid, order_line.date_planned, context),
            'location_id': order.partner_id.property_stock_supplier.id,
            'location_dest_id': order.location_id.id,
            'picking_id': picking_id,
            'partner_id': order.partner_id.id,
            'move_dest_id': False,
            'state': 'draft',
            'purchase_line_id': order_line.id,
            'company_id': order.company_id.id,
            'price_unit': price_unit,
            'picking_type_id': order.picking_type_id.id,
            'group_id': group_id,
            'procurement_id': False,
            'origin': order.name,
            'route_ids': order.picking_type_id.warehouse_id and [(6, 0, [x.id for x in order.picking_type_id.warehouse_id.route_ids])] or [],
            'warehouse_id':order.picking_type_id.warehouse_id.id,
            'invoice_state': order.invoice_method == 'picking' and '2binvoiced' or 'none',
        }

        diff_quantity = order_line.product_qty
        for procurement in order_line.procurement_ids:
            procurement_qty = product_uom._compute_qty(cr, uid, procurement.product_uom.id, procurement.product_qty, to_uom_id=order_line.product_uom.id)
            tmp = move_template.copy()
            tmp.update({
                'product_uom_qty': min(procurement_qty, diff_quantity),
                'product_uos_qty': min(procurement_qty, diff_quantity),
                'move_dest_id': procurement.move_dest_id.id,  #move destination is same as procurement destination
                'group_id': procurement.group_id.id or group_id,  #move group is same as group of procurements if it exists, otherwise take another group
                'procurement_id': procurement.id,
                'invoice_state': procurement.rule_id.invoice_state or (procurement.location_id and procurement.location_id.usage == 'customer' and procurement.invoice_state=='2binvoiced' and '2binvoiced') or (order.invoice_method == 'picking' and '2binvoiced') or 'none', #dropship case takes from sale
                'propagate': procurement.rule_id.propagate,
            })
            diff_quantity -= min(procurement_qty, diff_quantity)
            res.append(tmp)
        #if the order line has a bigger quantity than the procurement it was for (manually changed or minimal quantity), then
        #split the future stock move in two because the route followed may be different.
        if float_compare(diff_quantity, 0.0, precision_rounding=order_line.product_uom.rounding) > 0:
            move_template['product_uom_qty'] = diff_quantity
            move_template['product_uos_qty'] = diff_quantity
            res.append(move_template)
        return res
        
purchase_order()


    
    
