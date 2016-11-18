# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
from openerp.tools.translate import _
from openerp import SUPERUSER_ID, api
import logging
_logger = logging.getLogger(__name__)



class stock_quant(osv.osv):
    _inherit = "stock.quant"

    def _prepare_account_move_line(self, cr, uid, move, qty, cost, credit_account_id, debit_account_id, context=None):
        """
        Generate the account.move.line values to post to track the stock valuation difference due to the
        processing of the given quant.
        """
        if context is None:
            context = {}
        currency_obj = self.pool.get('res.currency')
        if context.get('force_valuation_amount'):
            valuation_amount = context.get('force_valuation_amount')
        else:
                if move.origin_returned_move_id:
                    # use the original cost of the returned product to cancel the cost
                    valuation_amount = move.origin_returned_move_id.price_unit
                elif move.product_id.cost_method == 'real':
                    valuation_amount = cost
                else:
                    valuation_amount = move.product_id.standard_price                 
            #valuation_amount = move.product_id.cost_method == 'real' and cost or move.product_id.standard_price
        #the standard_price of the product may be in another decimal precision, or not compatible with the coinage of
        #the company currency... so we need to use round() before creating the accounting entries.
        origin=move.picking_id.origin
        picking_type=move.picking_id.picking_type_id.id
        account_analytic_id=False

        print 'origin',origin,picking_type
        if picking_type:
            cr.execute ('select code from stock_picking_type where id=%s',(picking_type,))
            p_code=cr.fetchone()[0]
            print p_code,move.product_id.id
        else:
            p_code=False
        if p_code =='incoming':
            if origin:
                cr.execute ('select account_analytic_id from purchase_order po ,purchase_order_line pol where po.id=pol.order_id and po.name=%s and pol.product_id=%s',(origin,move.product_id.id,))
                po_name=cr.fetchall()
                print 'po_mnddddddd',po_name
                if po_name:
                    account_analytic_id =po_name[0]
                else:
                    account_analytic_id=False
            else:
                raise osv.except_osv(_('Warning!'), _("Please Insert PO Number In Source Document!"))                
        if p_code =='outgoing':
                
            or_name=origin[:2]
            print 'or_name',or_name
            if or_name=='PO':
                cr.execute ('select max(product_id) from pos_order po ,pos_order_line pol where po.id=pol.order_id and po.name=%s',(origin,))
                sale_name=cr.fetchone()[0]
                print 'sale_name',sale_name
               
                cr.execute('select analytic_account_id from product_template pt,product_category pc,product_product pp where pt.categ_id=pc.id and pp.product_tmpl_id=pt.id and pp.id=%s',(sale_name,))
                account_analytic_id=cr.fetchone()[0]
                if account_analytic_id:
                    account_analytic_id =account_analytic_id or False
                else:
                    account_analytic_id=False
            if or_name=='SO':       
                cr.execute ('select project_id from sale_order where name=%s',(origin,))
                sale_name=cr.fetchone()
                if sale_name:
                    account_analytic_id =sale_name[0]
                else:
                    account_analytic_id=False
                   
        valuation_amount = currency_obj.round(cr, uid, move.company_id.currency_id, valuation_amount * qty)
        partner_id = (move.picking_id.partner_id and self.pool.get('res.partner')._find_accounting_partner(move.picking_id.partner_id).id) or False
        debit_line_vals = {
                    'name': move.name,
                    'product_id': move.product_id.id,
                    'quantity': qty,
                    'product_uom_id': move.product_id.uom_id.id,
                    'ref': move.picking_id and move.picking_id.name or False,
                    'date': move.date,
                    'partner_id': partner_id,
                    'debit': valuation_amount > 0 and valuation_amount or 0,
                    'credit': valuation_amount < 0 and -valuation_amount or 0,
                    'account_id': debit_account_id,
                    'analytic_account_id': account_analytic_id or False,
                    
        }
        print 'debit_line_vals11111111111',debit_line_vals
        credit_line_vals = {
                    'name': move.name,
                    'product_id': move.product_id.id,
                    'quantity': qty,
                    'product_uom_id': move.product_id.uom_id.id,
                    'ref': move.picking_id and move.picking_id.name or False,
                    'date': move.date,
                    'partner_id': partner_id,
                    'credit': valuation_amount > 0 and valuation_amount or 0,
                    'debit': valuation_amount < 0 and -valuation_amount or 0,
                    'account_id': credit_account_id,
                    'analytic_account_id': account_analytic_id or False,
                    
        }
        print 'credit_line_vals1',credit_line_vals

        return [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]

