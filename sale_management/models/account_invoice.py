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
from mako.runtime import _inherit_from
import ast
from openerp.tools.amount_to_text_en import amount_to_text


class account_voucher (osv.osv):
    _inherit = 'account.voucher'
    
    def proforma_voucher(self, cr, uid, ids, context=None):
        self.action_move_line_create(cr, uid, ids, context=context)
        voucher_data = self.browse(cr, uid, ids, context=context)
        move_id = None
        if voucher_data.move_id:
            move_id = voucher_data.move_id.id
        cr.execute('''
        update  account_invoice set offset_by=%s where move_id in (
        select move_id from account_move_line where reconcile_id in (select reconcile_id from account_move_line where move_id =%s )
        and move_id !=%s)
        ''', (uid, move_id, move_id))
        return True    

class account_invoice(osv.osv):
    _inherit = 'account.invoice'

    def amount_to_text(self, cr, uid, amount, currency_id, context=None):
        # Currency complete name is not available in res.currency model
        # Exceptions done here (EUR, USD, BRL) cover 75% of cases
        # For other currencies, display the currency code
        currency = self.pool['res.currency'].browse(cr, uid, currency_id, context=context)
        if currency.name.upper() == 'EUR':
            currency_name = 'Euro'
        elif currency.name.upper() == 'USD':
            currency_name = 'Dollars'
        elif currency.name.upper() == 'BRL':
            currency_name = 'reais'
        else:
            currency_name = currency.name
        # TODO : generic amount_to_text is not ready yet, otherwise language (and country) and currency can be passed
        # amount_in_word = amount_to_text(amount, context=context)
        return amount_to_text(amount, currency=currency_name)
        
    def invoice_validate(self, cr, uid, ids, context=None):
        res = super(account_invoice, self).invoice_validate(cr, uid, ids, context=context) 
        if ids:
            cr.execute("update account_invoice set approved_by=%s where id =%s", (uid, ids[0],))
        return res
    
    def _get_corresponding_sale_order(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        order_id = None
        for rec in self.browse(cr, uid, ids, context=context):
            print'rec >>> ', rec
            cr.execute("""select order_id from sale_order_invoice_rel where invoice_id=%s""", (rec.id,))
            data = cr.fetchall()
            if data:
                order_id = data[0]
            print 'order_id >>> ', order_id
            result[rec.id] = order_id
        return result   
    
    def _get_corresponding_sale_order_ref(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        tb_ref_no = None
        for rec in self.browse(cr, uid, ids, context=context):
            print'rec >>> ', rec
            cr.execute("""select tb_ref_no from sale_order where id in (select order_id from sale_order_invoice_rel where invoice_id=%s)""", (rec.id,))
            data = cr.fetchone()
            if data:
                tb_ref_no = data[0]
            print 'order_id >>> ', tb_ref_no
            result[rec.id] = tb_ref_no
        return result       
    def create_promotion_line(self, cursor, user, vals, context=None):
        try : 
            inv_promotion_line_obj = self.pool.get('account.invoice.promotion.line')
            str = "{" + vals + "}"
                
            str = str.replace("'',", "',")  # null
            str = str.replace(":',", ":'',")  # due to order_id
            str = str.replace("}{", "}|{")
            new_arr = str.split('|')
            result = []
            for data in new_arr:
                x = ast.literal_eval(data)
                result.append(x)
            promo_line = []
            for r in result:                
                promo_line.append(r)  
            if promo_line:
                for pro_line in promo_line:
                
                    cursor.execute('select id From account_invoice where name  = %s ', (pro_line['promo_line_id'],))
                    data = cursor.fetchall()
                    if data:
                        saleOrder_Id = data[0][0]
                    else:
                        saleOrder_Id = None
                    cursor.execute("select manual from promos_rules where id=%s", (pro_line['pro_id'],))
                    manual = cursor.fetchone()[0]
                    if manual is not None:
                        manual = manual
                    else:
                        manual = False                                    
                    promo_line_result = {
                        'promo_line_id':saleOrder_Id,
                        'pro_id':pro_line['pro_id'],
                        'from_date':pro_line['from_date'],
                        'to_date':pro_line['to_date'] ,
                        'manual':manual,

                        }
                    inv_promotion_line_obj.create(cursor, user, promo_line_result, context=context)
            return True        
        except Exception, e:
            return False         
        
    def update_invoice_paid_date_in_invoice(self, cr, uid,context=None):
        inv_obj = self.pool.get('account.invoice')
        cr.execute("select id from account_invoice where state='paid' and paid_date is null and amount_total > 0 ") 
        invoice_data =cr.fetchall() 
        print 'invoice_data',invoice_data

        for invoice_id in invoice_data:
            invoice=inv_obj.browse(cr, uid, invoice_id[0], context=context)
            cr.execute("select * from update_paid_date_in_invoice(%s)",(invoice.id,)) 
        return True
                              
    _columns = {
              'sale_order_id':fields.function(_get_corresponding_sale_order, type='many2one', relation='sale.order', string='Sale Order'),
              'tb_ref_no':fields.function(_get_corresponding_sale_order_ref, type='char', string='Order Reference',store=True),
                  'promos_line_ids':fields.one2many('account.invoice.promotion.line', 'promo_line_id', 'Promotion Lines'),
                  'credit_line_ids':fields.one2many('account.invoice.credit.history', 'invoice_id', 'Credit History', copy=True),
                    'ignore_credit_limit':fields.boolean('Ignore Credit Limitation', default=False, readonly=True, states={'draft': [('readonly', False)]}),
                    'credit_invoice_balance' :fields.float('Credit Invoice Balance'),
                    'credit_limit_amount' :fields.float('Credit Limit'),
                    'credit_balance' :fields.float('Credit Balance'),
                    'approved_by' :fields.many2one('res.users', 'Approved By', readonly=True),
                    'offset_by' :fields.many2one('res.users', 'Offset By', readonly=True),
                    'cdnreference_no' :fields.char('Reference No'),
                    'dn_currency_id':fields.many2one('res.currency', 'Currency'),
                    'dn_rate':fields.float('F/X Currency - MMK Rate'),
                    'dn_bank':fields.char('Bank'),
                    'dn_date':fields.date('Date'),
                    'document_fname1': fields.char('Filename', size=128),
                    'document_file1':fields.binary('File', required=False),
                    'document_fname2': fields.char('Filename', size=128),
                    'document_file2':fields.binary('File', required=False),
                    'document_fname3': fields.char('Filename', size=128),
                    'document_file3':fields.binary('File', required=False),
                    'principle_id':fields.many2one('product.maingroup', 'Principle'),
                    'claim_type': fields.selection([('trade_discount', 'Trade Discount Foc'),
                                      ('mis_claim', 'Mis Claim'),
                                      ('gid_loss', 'Gid Loss/Damage'),
                                      ('expired', 'Expired/Damage')], 'Type'),
                                        'is_pd_invoice':fields.boolean('Is Pending Delivery Invoice', default=False, readonly=True),
                    'paid_date': fields.date(string='Paid Date'),
                    'pre_sale_order_id':fields.many2one('sale.order', 'Original Pre Sale Order No',readonly=True),
                    'order_team':fields.many2one('crm.case.section', 'Order Team',readonly=True),

              }

    
class account_invoice_credit_history(osv.osv):
    _name = 'account.invoice.credit.history'
    _columns = {  
                'invoice_id':fields.many2one('account.invoice', 'Credit History'),
                'date':fields.date('Invoice Date'),
                'invoice_no':fields.char('Inv No.'),
                'invoice_amt':fields.float('Amount'),
                'paid_amount':fields.float('Paid Amount'),
                'balance':fields.float('Balance'),
                'due_date':fields.date('Due Date'),
                'balance_day':fields.integer('Balance Days'),
                'branch_id':fields.many2one('res.branch', 'Branch'),
                'status':fields.char('Status'),
                }    


class sale_order_promotion_line(osv.osv):
    _name = 'account.invoice.promotion.line'
    _columns = {
              'promo_line_id':fields.many2one('account.invoice', 'Promotion line'),
              'pro_id': fields.many2one('promos.rules', 'Promotion Rule', change_default=True, readonly=False),
              'from_date':fields.datetime('From Date'),
              'to_date':fields.datetime('To Date'),
              'manual':fields.boolean('Manual'),
              'product_id': fields.many2one('product.product', 'Product', readonly=False),
              'is_foc': fields.boolean('Is FOC', readonly=False),
              'is_discount': fields.boolean('Is Discount', readonly=False),
              'foc_qty': fields.float('Foc Qty', readonly=False),
              'discount_amount': fields.float('Discount Amount', readonly=False),
              'discount_percent': fields.float('Discount Percent', readonly=False),
              }
    _defaults = {
        'manual':False,
        'is_foc':False,
        'is_discount':False,
    }
    
    def onchange_promo_id(self, cr, uid, ids, pro_id, context=None):
            result = {}
            promo_pool = self.pool.get('promos.rules')
            datas = promo_pool.read(cr, uid, pro_id, ['from_date', 'to_date', 'manual'], context=context)
    
            if datas:
                result.update({'from_date':datas['from_date']})
                result.update({'to_date':datas['to_date']})
                result.update({'manual':datas['manual']})
            return {'value':result}

            
sale_order_promotion_line()    
    
