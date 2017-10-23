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
        #'purchase_ids': fields.one2many('purchase.order', 'requisition_id', 'Purchase Orders', states={'done': [('readonly', True)]}),
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
            for po_line in tender.line_ids:
                #only take into account confirmed line that does not belong to already confirmed purchase order
                if tender.state == 'confirmed':
                    if id_per_supplier.get(po_line.product_id.supplier_code):
                        id_per_supplier[po_line.product_id.supplier_code].append(po_line)
                    else:
                        id_per_supplier[po_line.product_id.supplier_code] = [po_line]

            #generate po based on supplier and cancel all previous RFQ
            ctx = dict(context or {}, force_requisition_id=True)
            for supplier, product_line in id_per_supplier.items():
                if tender:
                        cr.execute("select company_id from res_users where id=%s", (uid,))
                        company_id = cr.fetchone()[0]
                        cr.execute("select id from res_currency where active='t' and base='t'",)
                        currency_id = cr.fetchone()[0]
                        cr.execute("select id from stock_picking_type where warehouse_id=%s", (tender.warehouse_id.id,))
                        pickingtype_id = cr.fetchone()[0]
                        cr.execute("select lot_stock_id from stock_warehouse where id=%s", (tender.warehouse_id.id,))
                        location_id = cr.fetchone()[0]
                        poResult = {'partner_id':tender.partner_id.id or False,
                                    'pr_ref':tender.name or '/',
                                    'date_order':tender.date_requisition ,
                                    'company_id':company_id or False,
                                    'currency_id':currency_id or False,
                                    'pricelist_id':tender.partner_id.pricelist_id.id or False,
                                    'location_id':location_id or False,
                                    'picking_type_id':pickingtype_id or False,
                                    'state': 'draft',                                
                                    'warehouse_id':tender.warehouse_id.id or False,
                                    'due_date':tender.date_expected ,
                                    'note':tender.description,
                                            }
                        poId = po.create(cr, uid, poResult, context=context)
                for line in product_line:
                        if poId and line:
                            polResult = {
                                        'order_id':poId,
                                        'product_id':line.product_id.id,
                                        'name':line.product_id.name_template,
                                        'product_uom':line.product_uom_id.id,
                                        'product_qty':line.product_qty,
                                        'price_unit':line.price_unit,
                                        'date_planned':tender.date_expected ,
                                        'state':'draft',
                                        }                                
                            pol_id =poline.create(cr, uid, polResult, context=context)
            #set tender to state done
            self.write(cr, uid, ids,  {'state':'done'}, context=context)
        return True
    
purchase_requisitions()

class purchase_requisitions_line(osv.osv):
    _name = "purchase.requisitions.line"

    _columns = {
        'product_id': fields.many2one('product.product', 'Product', domain=[('purchase_ok', '=', True)]),
        'product_uom_id': fields.many2one('product.uom', 'Product Unit of Measure'),
        'product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure')),
        'price_unit': fields.float('Price Unit'),
        'requisition_id': fields.many2one('purchase.requisitions', 'Purchase Requisitions', ondelete='cascade'),
    }

    def onchange_product_id(self, cr, uid, ids, product_id, product_uom_id,context=None):
        """ Changes UoM and name if product_id changes.
        @param name: Name of the field
        @param product_id: Changed product_id
        @return:  Dictionary of changed values
        """
        value = {'product_uom_id': '', 'price_unit': 0.0}
        if product_id:
            prod = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            value = {'product_uom_id': prod.uom_id.id, 'price_unit': prod.list_price, 'product_qty': 1.0}
        return {'value': value}
    
purchase_requisitions_line()