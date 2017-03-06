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

from datetime import datetime, timedelta
from openerp import tools
import time
from lxml import etree
from openerp import models, fields, api, _
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
from openerp import workflow
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp
class sale_order_line(osv.osv):

    _inherit='sale.order.line'
    
## customize_model need to calculate the dis (%) to dis(amt) or dis(amt) to dis(%)

      
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
#             if line.discount>0:
#                 if line.discount_amt>0:
#                     price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
#                     taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.product_uom_qty, line.product_id, line.order_id.partner_id)
#                     cur = line.order_id.pricelist_id.currency_id
#                     res[line.id] = cur_obj.round(cr, uid, cur, taxes['total']-line.discount_amt)
#                     
#                 #for discount_amt
#                 else:
#                     price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
#                     taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.product_uom_qty, line.product_id, line.order_id.partner_id)
#                     cur = line.order_id.pricelist_id.currency_id
#                     res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])       
            if line.discount_amt>0:

                    price = line.price_unit
                    taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.product_uom_qty, line.product_id, line.order_id.partner_id)
                    cur = line.order_id.pricelist_id.currency_id
                    res[line.id] = cur_obj.round(cr, uid, cur, taxes['total']-line.discount_amt) 
            else:
                price = line.price_unit
                taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.product_uom_qty, line.product_id, line.order_id.partner_id)
                cur = line.order_id.pricelist_id.currency_id
                res[line.id] = cur_obj.round(cr, uid, cur,taxes['total'] )              
        return res
        
        

## customize_model       
    def _amount_line1(self, cr, uid, ids, field_name, arg, context=None):
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            
            price = line.price_unit
            qty=line.product_uom_qty
            amount=price*qty
            taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.product_uom_qty, line.product_id, line.order_id.partner_id)
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, amount)
        return res
		
    def _get_price_reduce(self, cr, uid, ids, field_name, arg, context=None):
        res = dict.fromkeys(ids, 0.0)
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.net_total / line.product_uom_qty
        return res
    def onchange_discount_amount(self, cr, uid, ids, discount_amt,product_uom_qty, price_unit,context=None):
        val = {'discount': 0.0}
        print 'discount_amt',discount_amt
        if price_unit:
            discount = float(discount_amt)/(float(price_unit*product_uom_qty)) * 100
            val['discount'] = discount
            globvar=1
        return {'value': val}
    def onchange_discount_percent(self, cr, uid, ids, discount,product_uom_qty, price_unit,context=None):
        val = {'discount_amt': 0.0}
        if price_unit:
            discount_amt =float(discount) *(float(price_unit*product_uom_qty)) / 100
            val['discount_amt'] = discount_amt
        return {'value': val}     
    def foc_change(self, cr, uid, ids, product, qty=0, context=None):
        product_obj = self.pool.get('product.product')
        domain = {}
        result = {}
        if not product:
            return {'value': {'th_weight': 0,
                'product_uos_qty': qty}, 'domain': {'product_uom': [],
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
               
    _columns= { 
         'price_unit': fields.float('Unit Price', required=True, digits_compute=dp.get_precision('Product Price'), readonly=True),
        'tax_id': fields.many2many('account.tax', 'sale_order_tax', 'order_line_id', 'tax_id', 'Taxes', readonly=True, domain=['|', ('active', '=', False), ('active', '=', True)]),          
               'price_subtotal': fields.function(_amount_line1, string='Subtotal'),
               'net_total':fields.function(_amount_line, string='Total', digits_compute= dp.get_precision('Account')),
               'discount':fields.float('Discount (%)',store=True, readonly=True),
               'discount_amt':fields.float('Discount (amt)',store=True, readonly=True),
               'sale_foc':fields.boolean('FOC', readonly=True),
              # 'show_amt':fields.function(_amount_line2,string='Total Discount(-)',readonly=True)
               
               }

    _default = {
        
        'discount': 0.0,
        'price_subtotal':0.0,
        'discount_amt':0.0,
        'sale_foc':False,
        'net_total':0.0}
##to show the deduct_amt in sale_order form need to declare this field in sale_order
    def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False, context=None):
        """Prepare the dict of values to create the new invoice line for a
           sales order line. This method may be overridden to implement custom
           invoice generation (making sure to call super() to establish
           a clean extension chain).

           :param browse_record line: sale.order.line record to invoice
           :param int account_id: optional ID of a G/L account to force
               (this is used for returning products including service)
           :return: dict of values to create() the invoice line
        """
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
                'account_analytic_id': line.order_id.project_id and line.order_id.project_id.id or False,
            }

        return res

class sale_order(osv.osv):
    _inherit = 'sale.order' 
## customize_model
    def _amount_line_tax(self, cr, uid, line, context=None):
        val = 0.0
        if line.discount:
            for c in self.pool.get('account.tax').compute_all(cr, uid, line.tax_id, line.price_unit * (1-(line.discount or 0.0)/100.0), line.product_uom_qty, line.product_id, line.order_id.partner_id)['taxes']:
                val += c.get('amount', 0.0)
        elif line.discount_amt:
            for c in self.pool.get('account.tax').compute_all(cr, uid, line.tax_id, line.price_unit -line.discount_amt, line.product_uom_qty, line.product_id, line.order_id.partner_id)['taxes']:
                val += c.get('amount', 0.0)  
        else:
            for c in self.pool.get('account.tax').compute_all(cr, uid, line.tax_id, line.price_unit * (1-(line.discount or 0.0)/100.0), line.product_uom_qty, line.product_id, line.order_id.partner_id)['taxes']:
                val += c.get('amount', 0.0)
        return val
## customize_model
    def _amount_all_wrapper(self, cr, uid, ids, field_name, arg, context=None):
        """ Wrapper because of direct method passing as parameter for function fields """
        print 'field_namefield_name',field_name
        return self._amount_all(cr, uid, ids, field_name, arg, context=context)
## customize_model
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            
            val = val1 = 0.0
            cur = order.pricelist_id.currency_id
            for line in order.order_line:
                print 'line.net_total',line.net_total
                val1 += line.net_total
                val += self._amount_line_tax(cr, uid, line, context=context)
            res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
            res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
            
        return res

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('sale.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()

    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id

    def _get_default_section_id(self, cr, uid, context=None):
        """ Gives default section by checking if present in the context """
        section_id = self._resolve_section_id_from_context(cr, uid, context=context) or False
        if not section_id:
            section_id = self.pool.get('res.users').browse(cr, uid, uid, context).default_section_id.id or False
        return section_id

    def _resolve_section_id_from_context(self, cr, uid, context=None):
        """ Returns ID of section based on the value of 'section_id'
            context key, or None if it cannot be resolved to a single
            Sales Team.
        """
        if context is None:
            context = {}
        if type(context.get('default_section_id')) in (int, long):
            return context.get('default_section_id')
        if isinstance(context.get('default_section_id'), basestring):
            section_ids = self.pool.get('crm.case.section').name_search(cr, uid, name=context['default_section_id'], context=context)
            if len(section_ids) == 1:
                return int(section_ids[0][0])
        return None
## customize_model
    _columns={
              'is_add_discount':fields.boolean('Allow Discount',default=False),
              'deduct_amt':fields.float('Discount Amount',store=True),
              'additional_discount':fields.float('Additional Discount',store=True),
              'total_dis':fields.function(_amount_all_wrapper, digits_compute=dp.get_precision('Account'), string='Total Discount',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The tax amount."),
               'amount_tax': fields.function(_amount_all_wrapper, digits_compute=dp.get_precision('Account'), string='Taxes',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The tax amount."),
        'amount_total': fields.function(_amount_all_wrapper, digits_compute=dp.get_precision('Account'), string='Total',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The total amount."),
        'amount_untaxed': fields.function(_amount_all_wrapper, digits_compute=dp.get_precision('Account'), string='Untaxed Amount',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The amount without tax.", track_visibility='always'),}
    _default={
              'amount_untaxed':0.0,
              'amount_tax':0.0,
              'amount_total':0.0
              }

    def _prepare_order_line_procurement(self, cr, uid, order, line, group_id=False, context=None):
        vals = super(sale_order, self)._prepare_order_line_procurement(cr, uid, order, line, group_id, context)
        vals['foc'] = line.sale_foc

        return vals    
## customize_model
    def button_dummy(self, cr, uid, ids, context=None):
        res=result={}
        cur_obj = self.pool.get('res.currency')
        deduct=untax=total=0.0        
        if ids:
            if (type(ids)==int):
                cr.execute('select sum(discount_amt) from sale_order_line where order_id=%s',(ids,))
                total_dis_amt=cr.fetchall()[0]
                cr.execute('select deduct_amt,amount_untaxed,amount_tax,additional_discount from sale_order where id=%s',(ids,))
                result=cr.fetchall()[0]
                deduct=result[0]
                untax=result[1]
                amount_tax=result[2]
                additional_discount=result[3]
                print result,'result and deduction',deduct,total_dis_amt
                if deduct is None:
                    deduct=0.0
                if amount_tax is None:
                    amount_tax=0.0           
                total=untax+amount_tax-deduct-(untax*(additional_discount/100))
                cr.execute('update sale_order so set amount_total=%s,total_dis=%s,deduct_amt=%s,additional_discount=%s where so.id=%s',(total,total_dis_amt,deduct,additional_discount,ids))
            else:
                cr.execute('select sum(discount_amt) from sale_order_line where order_id=%s',(ids[0],))
                total_dis_amt=cr.fetchall()[0]
                cr.execute('select deduct_amt,amount_untaxed,amount_tax,additional_discount from sale_order where id=%s',(ids[0],))
                result=cr.fetchall()[0]
                deduct=result[0]
                untax=result[1]
                amount_tax=result[2]
                additional_discount=result[3]
                print result,'result and deduction',deduct,total_dis_amt,additional_discount
                if deduct is None:
                    deduct=0.0
                if amount_tax is None:
                    amount_tax=0.0           
                print    '(untax*additional_discount)',untax,additional_discount,(additional_discount/100),amount_tax
                total=untax+amount_tax-deduct-(untax*(additional_discount/100))
                print 'total',total
                cr.execute('update sale_order so set amount_total=%s,total_dis=%s,deduct_amt=%s,additional_discount=%s where so.id=%s',(total,total_dis_amt,deduct,additional_discount,ids[0]))
        return True
    ## customize_model
    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        """Prepare the dict of values to create the new invoice for a
           sales order. This method may be overridden to implement custom
           invoice generation (making sure to call super() to establish
           a clean extension chain).

           :param browse_record order: sale.order record to invoice
           :param list(int) line: list of invoice line IDs that must be
                                  attached to the invoice
           :return: dict of value to create() the invoice
        """
        if context is None:
            context = {}
        journal_ids = self.pool.get('account.journal').search(cr, uid,
            [('type', '=', 'sale'), ('company_id', '=', order.company_id.id)],
            limit=1)
        if not journal_ids:
            raise osv.except_osv(_('Error!'),
                _('Please define sales journal for this company: "%s" (id:%d).') % (order.company_id.name, order.company_id.id))
        print 'order.partner_id.property_account_receivable.id',order.partner_id.property_account_receivable.id,order.name
        invoice_vals = {
            'name': order.client_order_ref or '',
            'origin': order.name,
            'type': 'out_invoice',
            'reference': order.client_order_ref or order.name,
            'account_id': order.partner_id.property_account_receivable.id,
            'partner_id': order.partner_invoice_id.id,
            'journal_id': journal_ids[0],
            'invoice_line': [(6, 0, lines)],
            'currency_id': order.pricelist_id.currency_id.id,
            'comment': order.note,
            'payment_term': order.payment_term and order.payment_term.id or False,
            'fiscal_position': order.fiscal_position.id or order.partner_id.property_account_position.id,
            'date_invoice': context.get('date_invoice', False),
            'company_id': order.company_id.id,
            'user_id': order.user_id and order.user_id.id or False,
            'section_id' : order.section_id.id,
            'deduct_amt':order.deduct_amt,
            'additional_discount':order.additional_discount,
            'discount_total':order.total_dis,
        }

        # Care for deprecated _inv_get() hook - FIXME: to be removed after 6.1
        invoice_vals.update(self._inv_get(cr, uid, order, context=context))
        return invoice_vals
    
    
    
class procurement_order(osv.osv):
    """
    Procurement Orders
    """
    _name = "procurement.order"
    _inherit = 'procurement.order'
    _columns = {
            'foc': fields.boolean('FOC'),
          
         }
    
    def _run_move_create(self, cr, uid, procurement, context=None):
        vals = super(procurement_order, self)._run_move_create(cr, uid, procurement, context)
        vals['foc'] = procurement.foc

        return vals

