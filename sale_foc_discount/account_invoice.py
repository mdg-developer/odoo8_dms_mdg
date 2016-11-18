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

import itertools
from lxml import etree
from openerp.osv import orm
from openerp import models, fields, api, _
from openerp.osv import fields, osv
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp

class account(osv.osv):
    _inherit='account.invoice.line'
# # customize_model       
    def _net_total(self, cr, uid, ids, field_name, arg, context=None):
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            
            price = line.price_unit
            qty = line.quantity
            amount = price * qty
            cur = line.invoice_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, amount)
        return res    
    _columns={
               'net_total': fields.function(_net_total, string='Subtotal', type='float'),
              'discount_amt':fields.float('Dis(amt)'),
              'discount':fields.float('Dis(%)'),
             'foc':fields.boolean('FOC')

              } 
class account_invoice_line(models.Model):
    _inherit='account.invoice.line'
    
    def onchange_discount_percent(self, cr, uid, ids, discount,quantity, price_unit,context=None):
        val = {'discount_amt': 0.0}
        if price_unit:
            discount_amt =float(discount) *(float(price_unit*quantity)) / 100
            val['discount_amt'] = discount_amt
        return {'value': val}         
    
    def foc_change(self, cr, uid, ids, product, qty=0, context=None):
        product_obj = self.pool.get('product.product')
        domain = {}
        result = {}
        if not product:
            return {'value': {'th_weight': 0,
                'quantity': qty}, 'domain': {'product_uom': [],
                   'product_uos': []}}
        if qty == 0 :
            raise osv.except_osv(_('No Qty Defined!'), _("Please enter Qty"))
        else:
            result['name'] = 'FOC'
            result['price_unit'] = 0
            result['price_subtotal'] = 0
            result['discount'] = 0.0
            result['discount_amt'] = 0.0

        return {'value': result, 'domain': domain}  
# ## customize_model
    @api.one
    @api.depends('price_unit', 'discount','discount_amt', 'invoice_line_tax_id', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id')
    def _compute_price(self):
        price=show=0.0
        if self.discount_amt>0:
            show=self.discount_amt
            price = self.price_unit
            taxes = self.invoice_line_tax_id.compute_all(price, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
            self.price_subtotal = taxes['total']-self.discount_amt
#         if self.discount>0:
#             show=(self.price_unit) *(self.discount / 100.0)
#             price=self.price_unit * (1 - (self.discount or 0.0) / 100.0)
#             taxes = self.invoice_line_tax_id.compute_all(price, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
#             self.price_subtotal = taxes['total']
#         if (self.discount>0 and self.discount_amt>0) or (self.discount_amt >0 and self.discount>0) :
#             show=((self.price_unit) *(self.discount / 100.0))
#             show+=self.discount_amt
#             price = (self.price_unit * (1 - (self.discount or 0.0) / 100.0))
#             taxes = self.invoice_line_tax_id.compute_all(price, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
#             self.price_subtotal = taxes['total']-self.discount_amt
        if self.discount<=0 and self.discount_amt<=0:
            show=0.0
            price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
            taxes = self.invoice_line_tax_id.compute_all(price, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
            self.price_subtotal = taxes['total']

        if self.invoice_id:
            self.price_subtotal = self.invoice_id.currency_id.round(self.price_subtotal)
        return True
    
    @api.model
#     def _default_price_unit(self):
#         if not self._context.get('check_total'):
#             return 0
#         total = self._context['check_total']
#         for l in self._context.get('invoice_line', []):
#             if isinstance(l, (list, tuple)) and len(l) >= 3 and l[2]:
#                 vals = l[2]
#                 price = vals.get('price_unit', 0) * (1 - vals.get('discount', 0) / 100.0)
#                 total = total - (price * vals.get('quantity'))
#                 taxes = vals.get('invoice_line_tax_id')
#                 if taxes and len(taxes[0]) >= 3 and taxes[0][2]:
#                     taxes = self.env['account.tax'].browse(taxes[0][2])
#                     tax_res = taxes.compute_all(price, vals.get('quantity'),
#                         product=vals.get('product_id'), partner=self._context.get('partner_id'))
#                     for tax in tax_res['taxes']:
#                         total = total - tax['amount']
#         return total
# 
#     @api.model
#     def _default_account(self):
#         # XXX this gets the default account for the user's company,
#         # it should get the default account for the invoice's company
#         # however, the invoice's company does not reach this point
#         if self._context.get('type') in ('out_invoice', 'out_refund'):
#             return self.env['ir.property'].get('property_account_income_categ', 'product.category')
#         else:
#             return self.env['ir.property'].get('property_account_expense_categ', 'product.category')
# 
    @api.model
    def move_line_get_item(self, line):
        return {
            'type': 'src',
            'name': line.name.split('\n')[0][:64],
            'price_unit': line.price_unit,
            'quantity': line.quantity,
            'price': line.price_subtotal+line.discount_amt,
            'account_id': line.account_id.id,
            'product_id': line.product_id.id,
            'uos_id': line.uos_id.id,
            'account_analytic_id': line.account_analytic_id.id,
            'taxes': line.invoice_line_tax_id,
            'foc':line.foc,
        }   

    @api.model
    def move_line_get(self,invoice_id):
        inv = self.env['account.invoice'].browse(invoice_id)
        currency = inv.currency_id.with_context(date=inv.date_invoice)
        company_currency = inv.company_id.currency_id
        discount_account_id=discount_cash_account_id=None
        
        dis_per=dis_amt=deduct_amt=total=0.0
        discount_cash_account_id=inv.company_id.discount_cash_account_id.id
        discount_account_id=inv.company_id.discount_account_id.id
        if discount_cash_account_id and discount_account_id==None:
            raise orm.except_orm(_('Error :'), _("Please select the Discount code and Cash Discount Code in Sale setting!"))
        res = []
        deduct_amt=inv.deduct_amt
        discount_total=inv.discount_total
        
        for line in inv.invoice_line:
            
            mres = self.move_line_get_item(line)
            print 'mres',mres
            if not mres:
                continue
            res.append(mres)
            tax_code_found = False
            taxes = line.invoice_line_tax_id.compute_all(
                (line.price_unit * (1.0 - (line.discount or 0.0) / 100.0)),
                line.quantity, line.product_id, inv.partner_id)['taxes']
            for tax in taxes:
                if inv.type in ('out_invoice', 'in_invoice'):
                    tax_code_id = tax['base_code_id']
                    tax_amount = line.price_subtotal * tax['base_sign']
                else:
                    tax_code_id = tax['ref_base_code_id']
                    tax_amount = line.price_subtotal * tax['ref_base_sign']

                if tax_code_found:
                    if not tax_code_id:
                        continue
                    res.append(dict(mres))
                    res[-1]['price'] = 0.0
                    res[-1]['account_analytic_id'] = False
                elif not tax_code_id:
                    continue
                tax_code_found = True

                res[-1]['tax_code_id'] = tax_code_id
                res[-1]['tax_amount'] = currency.compute(tax_amount, company_currency)
        
        #print 'this is deduct amount',deduct_amt
        if discount_cash_account_id==discount_account_id:
            for line in inv.invoice_line:
                
                if line.discount:
                    dis_per+=(line.price_unit*line.quantity) *(line.discount/ 100.0)
                    #total+=dis_per
                    
                if line.discount_amt:
                    dis_amt+=line.discount_amt
                    #total+=dis_amt
            
            #print 'this is ddiscount_total',discount_total

            total=deduct_amt+discount_total
            val1={'type': 'src',
                    'name': 'Discount',
                    'price_unit': total,
                    'quantity': 1,
                    'price':-1* total,
                    'account_id': discount_account_id,
                    'product_id': False,
                    'foc':False,
                    'account_analytic_id': inv.invoice_line[0].account_analytic_id.id,
                    'taxes': False,
                    }
            if total>0:
                res.append(val1)
        else:
            for line in inv.invoice_line:
                if line.discount:
                    dis_per+=(line.price_unit*line.quantity) *(line.discount / 100.0)
                if line.discount_amt:
                    dis_amt+=line.discount_amt
            total=discount_total

            val1={'type': 'src',
                    'name': 'Discount',
                    'price_unit': total,
                    'quantity': 1,
                    'price':-1* total,
                    'account_id': discount_account_id,
                    'product_id': False,
                     'foc':False,
                    'account_analytic_id': inv.invoice_line[0].account_analytic_id.id,
                    'taxes': False,
                    }
            if total>0:
                res.append(val1)
            if deduct_amt>0:
                val2={'type': 'src',
                            'name': 'Cash Discount',
                            'price_unit': deduct_amt,
                            'quantity': 1,
                            'price':-1*(deduct_amt),
                            'account_id': discount_cash_account_id,
                            'product_id': False,
                             'foc':False,
                            'account_analytic_id': inv.invoice_line[0].account_analytic_id.id,
                            'taxes': False,
                            }
                res.append(val2)

        return res

# class account_account_invoice(osv.osv):
#     _inherit='account.invoice'
#     
#     _columns={'deduct_amt':fields.float('Deduction Amount'),
#               'discount_total':fields.float('Discount Total',readonly=True)}
#     
class account_invoice(models.Model):
    _inherit='account.invoice'
    @api.depends('invoice_line.price_subtotal', 'invoice_line.discount_amt','tax_line.amount','deduct_amt')

    def _compute_amount(self):
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line)
        self.amount_tax = sum(line.amount for line in self.tax_line)
        total_discount_amt=sum(line.discount_amt for line in self.invoice_line)
        self.discount_total =total_discount_amt

        self.amount_total = self.amount_untaxed + self.amount_tax - self.deduct_amt
         
    _columns={'deduct_amt':fields.float('Deduction Amount'),
                  'discount_total':fields.float('Discount Total' ,digits=dp.get_precision('Account'),store=True, readonly=True, compute='_compute_amount', track_visibility='always'),
                    
                  }
    
    

     