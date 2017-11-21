# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2013 Camptocamp
#    Copyright 2015 Vauxoo
#    Author: Yanina Aular
#            Osval Reyes
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

from openerp.osv import fields, osv
from getpass import fallback_getpass

class StockWarehouse(osv.osv):

    _inherit = "stock.warehouse"

StockWarehouse()

class stock_picking(osv.osv):
    _inherit = "stock.picking"
    
    def _get_invoice_vals(self, cr, uid, key, inv_type, journal_id, move, context=None):
        if context is None:
            context = {}
        record_id = context and context.get('active_ids', [])
        pick_obj = self.pool.get('stock.picking')
        pick = pick_obj.browse(cr, uid, record_id, context=context)
        sale_analytic_id=False   
        id_ana=False 
        
        partner, currency_id, company_id, user_id = analytic_account_id= key
        if inv_type in ('out_invoice', 'out_refund'):
            account_id = partner.property_account_receivable.id
            payment_term = partner.property_payment_term.id or False
        else:
            account_id = partner.property_account_payable.id
            payment_term = partner.property_supplier_payment_term.id or False
        
        if move.picking_id.sale_id.id:
            cr.execute("""SELECT * from sale_order_line where order_id=%s""",(move.picking_id.sale_id.id,))
            emp_res = cr.dictfetchall()
            if emp_res:
                for e in emp_res:
                    sale_analytic_id=e['analytic_account_id']
                    
        cr.execute("""SELECT * from account_journal where id=%s""",(journal_id,))
        j_res = cr.dictfetchone()
        
        if j_res:
            if j_res['type']=='sale_refund':
                id_ana=sale_analytic_id
                if not payment_term:
                    payment_term=move.picking_id.sale_id.payment_term.id
            if j_res['type']=='purchase_refund':
                if move.purchase_line_id:
                    id_ana = move.purchase_line_id.order_id.analytic_account_id.id,
                    if not payment_term:
                        payment_term = move.purchase_line_id.order_id.payment_term_id.id,       
                else:
                    for move in pick.move_lines:
                        cr.execute("""SELECT purchase_line_id from stock_move where id=%s""",(move.origin_returned_move_id.id,))
                        o_res = cr.dictfetchone()
                        cr.execute("""SELECT * from purchase_order_line where id=%s""",(o_res['purchase_line_id'],))
                        p_res = cr.dictfetchall()
                        if p_res:
                            for p in p_res:
                                id_ana=p['account_analytic_id'] 
                        if not payment_term:  
                            cr.execute("""SELECT * from purchase_order where id=%s""",(p['order_id'],))
                            payment_res = cr.dictfetchall()
                            if payment_res:
                                for pm in payment_res:
                                    payment_term=pm['payment_term_id']           
            
        return {
            'origin': move.picking_id.name,
            'date_invoice': context.get('date_inv', False),
            'user_id': user_id,
            'partner_id': partner.id,
            'account_id': account_id,
            'payment_term':payment_term or False,
            'type': inv_type,
            'fiscal_position': partner.property_account_position.id,
            'company_id': company_id,
            'currency_id': currency_id,
            'journal_id': journal_id,
            'analytic_account_id':id_ana or False,
        }
        
    def _invoice_create_line(self, cr, uid, moves, journal_id, inv_type='out_invoice', context=None):
        invoice_obj = self.pool.get('account.invoice')
        move_obj = self.pool.get('stock.move')
        invoices = {}
        is_extra_move, extra_move_tax = move_obj._get_moves_taxes(cr, uid, moves, inv_type, context=context)
        product_price_unit = {}
        for move in moves:
            company = move.company_id
            origin = move.picking_id.name
            partner, user_id, currency_id = move_obj._get_master_data(cr, uid, move, company, context=context)

            key = (partner, currency_id, company.id, user_id)
            invoice_vals = self._get_invoice_vals(cr, uid, key, inv_type, journal_id, move, context=context)

            if key not in invoices:
                # Get account and payment terms
                invoice_id = self._create_invoice_from_picking(cr, uid, move.picking_id, invoice_vals, context=context)
                invoices[key] = invoice_id
            else:
                invoice = invoice_obj.browse(cr, uid, invoices[key], context=context)
                merge_vals = {}
                if not invoice.origin or invoice_vals['origin'] not in invoice.origin.split(', '):
                    invoice_origin = filter(None, [invoice.origin, invoice_vals['origin']])
                    merge_vals['origin'] = ', '.join(invoice_origin)
                if invoice_vals.get('name', False) and (not invoice.name or invoice_vals['name'] not in invoice.name.split(', ')):
                    invoice_name = filter(None, [invoice.name, invoice_vals['name']])
                    merge_vals['name'] = ', '.join(invoice_name)
                if merge_vals:
                    invoice.write(merge_vals)
            invoice_line_vals = move_obj._get_invoice_line_vals(cr, uid, move, partner, inv_type, context=dict(context, fp_id=invoice_vals.get('fiscal_position', False)))
            invoice_line_vals['invoice_id'] = invoices[key]
            if not invoice_line_vals['account_analytic_id']:
                invoice_line_vals['account_analytic_id']=invoice_vals['analytic_account_id']
            invoice_line_vals['origin'] = origin
            if not is_extra_move[move.id]:
                product_price_unit[invoice_line_vals['product_id'], invoice_line_vals['uos_id']] = invoice_line_vals['price_unit']
            if is_extra_move[move.id] and (invoice_line_vals['product_id'], invoice_line_vals['uos_id']) in product_price_unit:
                invoice_line_vals['price_unit'] = product_price_unit[invoice_line_vals['product_id'], invoice_line_vals['uos_id']]
            if is_extra_move[move.id]:
                desc = (inv_type in ('out_invoice', 'out_refund') and move.product_id.product_tmpl_id.description_sale) or \
                    (inv_type in ('in_invoice','in_refund') and move.product_id.product_tmpl_id.description_purchase)
                invoice_line_vals['name'] += ' ' + desc if desc else ''
                if extra_move_tax[move.picking_id, move.product_id]:
                    invoice_line_vals['invoice_line_tax_id'] = extra_move_tax[move.picking_id, move.product_id]
                #the default product taxes
                elif (0, move.product_id) in extra_move_tax:
                    invoice_line_vals['invoice_line_tax_id'] = extra_move_tax[0, move.product_id]

            move_obj._create_invoice_line_from_vals(cr, uid, move, invoice_line_vals, context=context)
            move_obj.write(cr, uid, move.id, {'invoice_state': 'invoiced'}, context=context)

        invoice_obj.button_compute(cr, uid, invoices.values(), context=context, set_total=(inv_type in ('in_invoice', 'in_refund')))
        return invoices.values()
stock_picking()

class stock_move(osv.osv):
    _inherit = "stock.move"
    
    def _get_invoice_line_vals(self, cr, uid, move, partner, inv_type, context=None):
        fp_obj = self.pool.get('account.fiscal.position')
        # Get account_id
        fp = fp_obj.browse(cr, uid, context.get('fp_id')) if context.get('fp_id') else False
        name = False
        if inv_type in ('out_invoice', 'out_refund'):
            account_id = move.product_id.property_account_income.id
            if not account_id:
                account_id = move.product_id.categ_id.property_account_income_categ.id
            if move.procurement_id and move.procurement_id.sale_line_id:
                name = move.procurement_id.sale_line_id.name
        else:
            account_id = move.product_id.property_account_expense.id
            if not account_id:
                account_id = move.product_id.categ_id.property_account_expense_categ.id
        fiscal_position = fp or partner.property_account_position
        account_id = fp_obj.map_account(cr, uid, fiscal_position, account_id)

        # set UoS if it's a sale and the picking doesn't have one
        uos_id = move.product_uom.id
        quantity = move.product_uom_qty
        if move.product_uos:
            uos_id = move.product_uos.id
            quantity = move.product_uos_qty

        taxes_ids = self._get_taxes(cr, uid, move, context=context)

        return {
            'name': name or move.name,
            'account_id': account_id,
            'product_id': move.product_id.id,
            'uos_id': uos_id,
            'quantity': quantity,
            'price_unit': self._get_price_unit_invoice(cr, uid, move, inv_type),
            'invoice_line_tax_id': [(6, 0, taxes_ids)],
            'discount': 0.0,
            'account_analytic_id': False,
        }

stock_move()