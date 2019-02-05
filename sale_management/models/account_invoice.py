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

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
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
                    cursor.execute("select manual from promos_rules where id=%s",(pro_line['pro_id'],))
                    manual =cursor.fetchone()[0]
                    if manual is not None:
                        manual=manual
                    else:
                        manual=False                                    
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
    _columns = {
              'sale_order_id':fields.function(_get_corresponding_sale_order, type='many2one', relation='sale.order', string='Sale Order'),
                  'promos_line_ids':fields.one2many('account.invoice.promotion.line', 'promo_line_id', 'Promotion Lines'),           
                  'credit_line_ids':fields.one2many('account.invoice.credit.history', 'invoice_id', 'Credit History',copy=True),           
                    'ignore_credit_limit':fields.boolean('Ignore Credit Limitation',default=False,readonly=True, states={'draft': [('readonly', False)]}),
                    'credit_invoice_balance' :fields.float('Credit Invoice Balance'),   
                    'credit_limit_amount' :fields.float('Credit Limit'),   
                    'credit_balance' :fields.float('Credit Balance'),                 
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
                'branch_id':fields.many2one('res.branch','Branch'),
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
              'product_id': fields.many2one('product.product', 'Product',readonly=False),
              'is_foc': fields.boolean('Is FOC',readonly=False),
              'is_discount': fields.boolean('Is Discount',readonly=False),
              'foc_qty': fields.float('Foc Qty',readonly=False),
              'discount_amount': fields.float('Discount Amount',readonly=False),
              'discount_percent': fields.float('Discount Percent',readonly=False),                             
              }
    _defaults = {
        'manual':False,
        'is_foc':False,
        'is_discount':False,              
    }
    
    def onchange_promo_id(self, cr, uid, ids, pro_id, context=None):
            result = {}
            promo_pool = self.pool.get('promos.rules')
            datas = promo_pool.read(cr, uid, pro_id, ['from_date', 'to_date','manual'], context=context)
    
            if datas:
                result.update({'from_date':datas['from_date']})
                result.update({'to_date':datas['to_date']})
                result.update({'manual':datas['manual']})
            return {'value':result}
            
sale_order_promotion_line()    

class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
    
    _columns = {
            'invoice_available':fields.boolean('Available')
    }
    
account_invoice_line()
    
