# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp

class purchase_requisitions(osv.osv):
    _name = "purchase.requisitions"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    def _get_po_line(self, cr, uid, ids, field_names, arg=None, context=None):
        result = dict((res_id, []) for res_id in ids)
        for element in self.browse(cr, uid, ids, context=context):
            for po in element.purchase_ids:
                result[element.id] += [po_line.id for po_line in po.order_line]
        return result
    
    _columns = {
        'name': fields.char('Purchase Requisition No', required=True, copy=False),
        'partner_id': fields.many2one('res.partner', 'Requested By'),
        'date_requisition': fields.date('Requested Date'),
        'date_expected': fields.date('Expected Date'),
        'state': fields.selection([('draft', 'Draft'), 
                                   ('confirmed', 'Confirmed'), 
                                   ('done', 'Done'),
                                   ('cancel', 'Cancelled')],
                                  'Status', track_visibility='onchange', required=True,
                                  copy=False),
        'warehouse_id': fields.many2one('stock.warehouse', 'Requested Warehouse'),
        'purchase_ids': fields.one2many('purchase.order', 'requisition_id', 'Purchase Orders', states={'done': [('readonly', True)]}),
        'po_line_ids': fields.function(_get_po_line, method=True, type='one2many', relation='purchase.order.line', string='Products by supplier'),
        'line_ids': fields.one2many('purchase.requisitions.line', 'requisition_id', 'Products to Purchase', states={'done': [('readonly', True)]}, copy=True),
        'description': fields.text('Description')
    }
    _defaults = {
        'state': 'draft',
        'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'purchase.order.requisitions'),
    }
       
    def action_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        
    def action_confirmed(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'confirmed'}, context=context)

    def generate_po(self, cr, uid, ids, context=None):
        """
        Generate all purchase order based on selected lines, should only be called on one tender at a time
        """
        po = self.pool.get('purchase.order')
        pr = self.pool.get('purchase.requisitions')
        poline = self.pool.get('purchase.order.line')
        id_per_supplier = {}
        for tender in pr.browse(cr, uid, ids, context=context):
            if tender.state == 'done':
                raise osv.except_osv(_('Warning!'), _('You have already generate the purchase order(s).'))

            confirm = False
            #check that we have at least confirm one line
            for po_line in tender.line_ids:
                if tender.state == 'confirmed':
                    confirm = True
                    break
            if not confirm:
                raise osv.except_osv(_('Warning!'), _('You have no line selected for buying.'))

            #check for complete RFQ
            for quotation in tender.purchase_ids:
                if (self.check_valid_quotation(cr, uid, quotation, context=context)):
                    #use workflow to set PO state to confirm
                    po.write(cr, uid, [quotation.id], 'purchase_confirm', context=context)

            #get other confirmed lines per supplier
            for po_line in tender.line_ids:
                #only take into account confirmed line that does not belong to already confirmed purchase order
                if po_line.state == 'confirmed' and po_line.order_id.state in ['draft', 'sent', 'bid']:
                    if id_per_supplier.get(po_line.partner_id.id):
                        id_per_supplier[po_line.partner_id.id].append(po_line)
                    else:
                        id_per_supplier[po_line.partner_id.id] = [po_line]

            #generate po based on supplier and cancel all previous RFQ
            ctx = dict(context or {}, force_requisition_id=True)
            for supplier, product_line in id_per_supplier.items():
                #copy a quotation for this supplier and change order_line then validate it
                quotation_id = po.search(cr, uid, [('requisition_id', '=', tender.id), ('partner_id', '=', supplier)], limit=1)[0]
                vals = self._prepare_po_from_tender(cr, uid, tender, context=context)
                new_po = po.copy(cr, uid, quotation_id, default=vals, context=context)
                #duplicate po_line and change product_qty if needed and associate them to newly created PO
                for line in product_line:
                    vals = self._prepare_po_line_from_tender(cr, uid, tender, line, new_po, context=context)
                    poline.copy(cr, uid, line.id, default=vals, context=context)
                #use workflow to set new PO state to confirm
                po.write(cr, uid, [new_po], 'purchase_confirm', context=context)

            #cancel other orders
            self.cancel_unconfirmed_quotations(cr, uid, tender, context=context)

            #set tender to state done
            self.write(cr, uid, [tender.id], 'done', context=context)
        return True
    
    def cancel_unconfirmed_quotations(self, cr, uid, tender, context=None):
        #cancel other orders
        po = self.pool.get('purchase.order')
        for quotation in tender.purchase_ids:
            if quotation.state in ['draft', 'sent', 'bid']:
                self.pool.get('purchase.order').signal_workflow(cr, uid, [quotation.id], 'purchase_cancel')
                po.message_post(cr, uid, [quotation.id], body=_('Cancelled by the Purchase Requisitions associated to this request for quotation.'), context=context)
        return True

    def check_valid_quotation(self, cr, uid, quotation, context=None):
        """
        Check if a quotation has all his order lines bid in order to confirm it if its the case
        return True if all order line have been selected during bidding process, else return False

        args : 'quotation' must be a browse record
        """
        for line in quotation.order_line:
            if line.state != 'confirmed' or line.product_qty != line.quantity_bid:
                return False
        return True

    def _prepare_po_from_tender(self, cr, uid, tender, context=None):
        """ Prepare the values to write in the purchase order
        created from a tender.

        :param tender: the source tender from which we generate a purchase order
        """
        return {'order_line': [],
                'requisition_id': tender.id,
                'origin': tender.name}

    def _prepare_po_line_from_tender(self, cr, uid, tender, line, purchase_id, context=None):
        """ Prepare the values to write in the purchase order line
        created from a line of the tender.

        :param tender: the source tender from which we generate a purchase order
        :param line: the source tender's line from which we generate a line
        :param purchase_id: the id of the new purchase
        """
        return {'product_qty': line.quantity_bid,
                'order_id': purchase_id}
    
purchase_requisitions()

class purchase_requisitions_line(osv.osv):
    _name = "purchase.requisitions.line"

    _columns = {
        'product_id': fields.many2one('product.product', 'Product', domain=[('purchase_ok', '=', True)]),
        'product_uom_id': fields.many2one('product.uom', 'Product Unit of Measure'),
        'product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure')),
        'requisition_id': fields.many2one('purchase.requisitions', 'Purchase Requisitions', ondelete='cascade'),
    }

    def onchange_product_id(self, cr, uid, ids, product_id, product_uom_id,context=None):
        """ Changes UoM and name if product_id changes.
        @param name: Name of the field
        @param product_id: Changed product_id
        @return:  Dictionary of changed values
        """
        value = {'product_uom_id': ''}
        if product_id:
            prod = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            value = {'product_uom_id': prod.uom_id.id, 'product_qty': 1.0}
        return {'value': value}
    
purchase_requisitions_line()

class purchase_order(osv.osv):
    _inherit = "purchase.order"

    _columns = {
        'requisition_id': fields.many2one('purchase.requisition', 'Purchase Requisitions', copy=False),
    }

    def wkf_confirm_order(self, cr, uid, ids, context=None):
        res = super(purchase_order, self).wkf_confirm_order(cr, uid, ids, context=context)
        proc_obj = self.pool.get('procurement.order')
        for po in self.browse(cr, uid, ids, context=context):
            if po.requisition_id and (po.requisition_id.exclusive == 'exclusive'):
                for order in po.requisition_id.purchase_ids:
                    if order.id != po.id:
                        proc_ids = proc_obj.search(cr, uid, [('purchase_id', '=', order.id)])
                        if proc_ids and po.state == 'confirmed':
                            proc_obj.write(cr, uid, proc_ids, {'purchase_id': po.id})
                        order.signal_workflow('purchase_cancel')
                    po.requisition_id.tender_done(context=context)
        return res

    def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id, group_id, context=None):
        stock_move_lines = super(purchase_order, self)._prepare_order_line_move(cr, uid, order, order_line, picking_id, group_id, context=context)
        if order.requisition_id and order.requisition_id.procurement_id and order.requisition_id.procurement_id.move_dest_id:
            for i in range(0, len(stock_move_lines)):
                stock_move_lines[i]['move_dest_id'] = order.requisition_id.procurement_id.move_dest_id.id
        return stock_move_lines


class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line'

    _columns = {
        'quantity_bid': fields.float('Quantity Bid', digits_compute=dp.get_precision('Product Unit of Measure'), help="Technical field for not loosing the initial information about the quantity proposed in the bid"),
    }

    def action_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)

    def action_confirm(self, cr, uid, ids, context=None):
        super(purchase_order_line, self).action_confirm(cr, uid, ids, context=context)
        for element in self.browse(cr, uid, ids, context=context):
            if not element.quantity_bid:
                self.write(cr, uid, ids, {'quantity_bid': element.product_qty}, context=context)
        return True

    def generate_po(self, cr, uid, tender_id, context=None):
        #call generate_po from tender with active_id. Called from js widget
        return self.pool.get('purchase.requisition').generate_po(cr, uid, [tender_id], context=context)