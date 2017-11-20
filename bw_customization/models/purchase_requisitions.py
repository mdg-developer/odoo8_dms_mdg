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
from collections import defaultdict
from datetime import datetime
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp

class purchase_requisitions(osv.osv):
    _name = "purchase.requisitions"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'date_requisition desc, id desc'

    def _get_po_line(self, cr, uid, ids, field_names, arg=None, context=None):
        result = dict((res_id, []) for res_id in ids)
        for element in self.browse(cr, uid, ids, context=context):
            for po in element.purchase_ids:
                result[element.id] += [po_line.id for po_line in po.order_line]
        return result
    
    _columns = {
        'name': fields.char('Purchase Requisition No', required=True, copy=False),
        'partner_id': fields.many2one('res.partner', 'Requested By'),
        'date_requisition': fields.date('Requested Date',required=True),
        'date_expected': fields.date('Expected Date',required=True),
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
        
    def action_cancel(self, cr, uid, ids, context=None):
        po = self.pool.get('purchase.order')
        pol = self.pool.get('purchase.order.line')
        self.write(cr, uid, ids, {'state': 'cancel'}, context=context)
        for tender in self.browse(cr, uid, ids, context=context):
            pid = self.pool['purchase.order'].search(cr, uid, [('pr_ref', '=', tender.name)])
            po.write(cr, uid, pid,{'state': 'cancel'}, context=context) 
            pol_ids = self.pool['purchase.order.line'].search(cr, uid, [('order_id', '=', pid)])
            pol.write(cr, uid, pol_ids,{'state': 'cancel'}, context=context)
        
    def action_confirmed(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'confirmed'}, context=context)

    def generate_po(self, cr, uid, ids, context=None):
        """
        Generate all purchase order based on selected lines, should only be called on one tender at a time
        """
        po = self.pool.get('purchase.order')
        posup = self.pool.get('product.supplierinfo')
        pr = self.pool.get('purchase.requisitions')
        poline = self.pool.get('purchase.order.line')
        res_partner = self.pool.get('res.partner')
        obj_wh = self.pool.get('stock.warehouse')
        product_ids=[]
        product_tmp_ids=[]
        wh_ids=[]
        supplier_ids=[]
        for tender in pr.browse(cr, uid, ids, context=context):
            if tender.state == 'done':
                raise osv.except_osv(_('Warning!'), _('You have already generate the purchase order(s).'))
            for po_line in tender.line_ids:
                if tender.state == 'confirmed':
                    product_ids.append(po_line.product_id.id)
                    product_tmp_ids.append(po_line.product_id.product_tmpl_id.id)                    
                    ####### Warehouse #######
                    if po_line.product_id.product_tmpl_id.warehouse_id.id:
                        wh_ids.append(po_line.product_id.product_tmpl_id.warehouse_id.id)
                    else:
                        raise osv.except_osv(_('Product Warehouse Error!'),
                                            _('Product %s has no related Warehouse.') % (po_line.product_id.name))
                    ####### Warehouse #######
                    ####### Supplier #######
                    posup_ids = posup.search(cr, uid, [('is_default', '=', True),('product_tmpl_id', '=', po_line.product_id.product_tmpl_id.id)])
                    if posup_ids:
                        if len(posup_ids) == 1:
                            cr.execute("select distinct name from product_supplierinfo where id in %s", (tuple(posup_ids),))
                            supplier_id_by_product = cr.fetchall()
                            for ssid in supplier_id_by_product:
                                supplier_ids.append(ssid[0])
                        else:
                            raise osv.except_osv(_('Product Supplier Error!'),
                                            _('Product %s has more than one Default Supplier.') % (po_line.product_id.name))
                    else:
                        raise osv.except_osv(_('Product Supplier Error!'),
                                            _('Product %s has no related Default Supplier.') % (po_line.product_id.name))
                    ####### Supplier ####### 
            product_ids= list(set(product_ids)) #### Check distinct product_ids
            product_tmp_ids = list(set(product_tmp_ids)) #### Check product_tmp_ids
            supplier_ids = list(set(supplier_ids)) #### Check distinct supplier_ids
            if supplier_ids and product_ids and wh_ids:       
                cr.execute("select distinct psi.name,pt.warehouse_id from product_product pp,product_template pt,product_supplierinfo psi where pp.product_tmpl_id=pt.id and psi.product_tmpl_id=pt.id and pp.id in %s and psi.name in %s and pt.warehouse_id in %s and psi.is_default=True order by psi.name,pt.warehouse_id", (tuple(product_ids),tuple(supplier_ids),tuple(wh_ids)))
                sp_wh_pro = cr.fetchall() 
            
            for sw_ids in sp_wh_pro:
                if tender:
                            cr.execute("select company_id from res_users where id=%s", (uid,))
                            company_id = cr.fetchone()
                            if company_id:
                                company_id = company_id[0]
                            cr.execute("select id from res_currency where active='t' and base='t'",)
                            currency_id = cr.fetchone()
                            if currency_id:
                                currency_id = currency_id[0]
                            cr.execute("select id from stock_picking_type where name='Receipts' and warehouse_id=%s", (sw_ids[1],))
                            pickingtype_id = cr.fetchone()
                            if pickingtype_id:
                                pickingtype_id = pickingtype_id[0]
                            cr.execute("select default_location_dest_id from stock_picking_type where name='Receipts' and warehouse_id=%s", (sw_ids[1],))
                            location_id = cr.fetchone()
                            if location_id:
                                location_id = location_id[0]
                            supplier_id = res_partner.browse(cr, uid, sw_ids[0], context=context)
                            wh_id = obj_wh.browse(cr, uid, sw_ids[1], context=context)
                            poResult = {'partner_id':sw_ids[0] or False,
                                        'pr_ref':tender.name or '/',
                                        'date_order':tender.date_requisition ,
                                        'company_id':company_id or False,
                                        'currency_id':supplier_id.property_product_pricelist_purchase.currency_id and supplier_id.property_product_pricelist_purchase.currency_id.id or False,
                                        'pricelist_id':supplier_id.property_product_pricelist_purchase and supplier_id.property_product_pricelist_purchase.id or False,
                                        'location_id':location_id or False,
                                        'picking_type_id':pickingtype_id or False,
                                        'state': 'draft',                                
                                        'warehouse_id':tender.warehouse_id.id or False,
                                        'due_date':tender.date_expected ,
                                        'note':tender.description,
                                                }
                            poId = po.create(cr, uid, poResult, context=context)
                for pids in product_ids:
                    for po_line in tender.line_ids:
                        if tender.state == 'confirmed':
                            posup_ids = posup.search(cr, uid, [('is_default', '=', True),('product_tmpl_id', '=', po_line.product_id.product_tmpl_id.id)])
                            if posup_ids:
                                cr.execute("select name from product_supplierinfo where id=%s", (posup_ids[0],))
                            supplier_id = cr.fetchone()
                            if supplier_id:
                                supplier_id = supplier_id[0]
                            else:
                                cr.execute("select name from product_supplierinfo where product_tmpl_id=%s", (po_line.product_id.product_tmpl_id.id,))
                                posup_id = cr.fetchone()
                                if posup_id:
                                    supplier_id = posup_id[0]
                                else:
                                    raise osv.except_osv(_('Product Supplier Error!'),
                                             _('Product %s has no related Supplier.') % (po_line.product_id.name))
                            if (sw_ids[0] == supplier_id and sw_ids[1]==po_line.product_id.product_tmpl_id.warehouse_id.id and pids==po_line.product_id.id):
                                polResult = {
                                                'order_id':poId,
                                                'product_id':po_line.product_id.id,
                                                'name':po_line.product_id.name_template,
                                                'product_uom':po_line.product_uom_id.id,
                                                'product_qty':po_line.product_qty,
                                                'price_unit':po_line.price_unit,
                                                'date_planned':tender.date_expected ,
                                                'supplier_code':po_line.product_id.supplier_code ,
                                                'state':'draft',
                                                }                                
                                pol_id =poline.create(cr, uid, polResult, context=context)
            self.write(cr, uid, ids,  {'state':'done'}, context=context)
        return True
    
purchase_requisitions()

class purchase_requisitions_line(osv.osv):
    _name = "purchase.requisitions.line"
    #prod_uom_ids=[]
    
    _columns = {
        'product_id': fields.many2one('product.product', 'Product', domain=[('purchase_ok', '=', True)]),
        'product_uom_id': fields.many2one('product.uom', 'Product Unit of Measure',),
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
        #global prod_uom_ids
        prod_uom_ids=[]
        value = {'product_uom_id': [], 'price_unit': 0.0, 'product_qty': 1.0}
        domain = {'product_uom_id': []}
        if product_id:
            prod = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            cr.execute("select product_uom_id from product_template_product_uom_rel where product_template_id=%s", (prod.product_tmpl_id.id,))
            prod_uom_ids = cr.fetchall()
            value = {'product_uom_id': prod_uom_ids, 'price_unit': prod.list_price, 'product_qty': 1.0}
            domain = {'product_uom_id': [('id', 'in', prod_uom_ids)]}
        return {'value': value, 'domain': domain}
    
purchase_requisitions_line()