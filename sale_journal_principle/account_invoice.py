import itertools
from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp


class account_invoice(models.Model):
    _inherit = "account.invoice"
    
    def _compute_payments(self):
        partial_lines = lines = self.env['account.move.line']
        cr=self._cr
        uid=self._uid
        for line in self.move_id.line_id:
            print 'line _compute_payments',line
#             if line.account_id != self.account_id:
#                 continue
            if line.reconcile_id:
                lines |= line.reconcile_id.line_id
            elif line.reconcile_partial_id:
                lines |= line.reconcile_partial_id.line_partial_ids
            partial_lines += line
            print 'self.residual self.residual ',self.residual 
            if self.residual ==0.0:
                print 'self.residual self.residual ----',self.residual 
                self.confirm_paid()
                if self.origin:
                    cr.execute("update sale_order set invoiced=True where name=%s", (self.origin,))        
                    cr.execute("update sale_order set state='done' where shipped=True and invoiced=True and name=%s", (self.origin,)) 
            if self.residual !=0.0:
                if self.origin:
                    cr.execute("update account_invoice set state='open' where id=%s", (self.id,))        
        self.payment_ids = (lines - partial_lines).sorted()
        
#     account_id = fields.Many2one('account.account', string='Account',
#                                  required=False, readonly=True, states={'draft': [('readonly', False)]},
#                 
#                 
#     def init(self, cr):
#         print 'start'
#         cr.execute("""ALTER TABLE account_invoice
#         DROP COLUMN if exists account_id CASCADE;""")
#         print 'end'
#     @api.model
#     def line_get_convert(self, line, part, date):
#         account_id = None
#         if line['price']<0:
#             
#             product = self.env['product.product'].browse(line.get('product_id', False))
#             print 'product>>>',product.id
#             print 'line.get>>>',line.get('product_id', False)
#             account_id = product.product_tmpl_id.main_group.property_account_receivable.id
#             print 'account_id>>>',account_id
#         else:
#             account_id = None
# 
#         print 'line>>>',line
#         res= {
#             'date_maturity': line.get('date_maturity', False),
#             'partner_id': part,
#             'name': line['name'][:64],
#             'date': date,
#             'debit': line['price']>0 and line['price'],
#             'credit': line['price']<0 and -line['price'],
#             'account_id': line['account_id'],
#             #'account_id': account_id,
#             'analytic_lines': line.get('analytic_lines', []),
#             'amount_currency': line['price']>0 and abs(line.get('amount_currency', False)) or -abs(line.get('amount_currency', False)),
#             'currency_id': line.get('currency_id', False),
#             'tax_code_id': line.get('tax_code_id', False),
#             'tax_amount': line.get('tax_amount', False),
#             'ref': line.get('ref', False),
#             'quantity': line.get('quantity',1.00),
#             'product_id': line.get('product_id', False),
#             'product_uom_id': line.get('uos_id', False),
#             'analytic_account_id': line.get('account_analytic_id', False),
#             'main_group': account_id,
#         }
#         print 'res>>>',res
#         return res
    @api.model
    def line_get_convert(self, line, part, date):
        print 'check>>>', line
        if line is not None:
            print 'lineeeeeeeee', line['debit'],line['credit']
            price= line['debit']+line['credit'],
            return {
                'date_maturity': line.get('date_maturity', False),
                'partner_id': part,
                'name': line['name'][:64],
                'date': date,
                'debit': line['debit'],#line['price']>0 and line['price'],
                'credit': line['credit'],#line['price']<0 and -line['price'],
                'account_id': line['account_id'],
                #'account_id': account_id,
                'analytic_lines': line.get('analytic_lines', []),
                'amount_currency': price>0 and abs(line.get('amount_currency', False)) or -abs(line.get('amount_currency', False)),
                'currency_id': line.get('currency_id', False),
                'tax_code_id': line.get('tax_code_id', False),
                'tax_amount': line.get('tax_amount', False),
                'ref': line.get('ref', False),
                'quantity': line.get('quantity',1.00),
                'product_id': line.get('product_id', False),
                'product_uom_id': line.get('uos_id', False),
                'analytic_account_id': line.get('account_analytic_id', False),
            }
    
    def line_get_convert_new(self, line, part, date):
        account_id = None
        cr=self._cr
        type='out_invoice' 
        print 'line_get_convert_newline_get_convert_new',line,part
        origin=line.get('ref', False)
        print 'originoriginorigin',origin
        if origin:
            cr.execute("select type from account_invoice where origin=%s",(origin,))
            type=cr.fetchone()
            if type:
                type=type[0]
            else:
                type=None
        print 'typeeeeeeeee',type
        if type=='out_invoice' :
            if line['price']<0:
                product = self.env['product.product'].browse(line.get('product_id', False))
                print 'product>>>',product.id
                print 'line.get>>>',line.get('product_id', False)
                if  line['name']=='Discount':
                    account_id = product.product_tmpl_id.main_group.property_account_discount.id
                    line['price']= -1* line['price']
                else:
                    account_id = product.product_tmpl_id.main_group.property_account_receivable.id
                                    #acount_id= product.product_tmpl_id.main_group.property_account_payable.id
                print 'account_id>>>',account_id        
    
                print 'line>>>',line
                res= {
                    'date_maturity': line.get('date_maturity', False),
                    'partner_id': part,
                    'name': line['name'][:64],
                    'date': date,
                    'debit': line['price']>0 and line['price'],
                    'credit': line['price']<0 and -line['price'],
                    'account_id': line['account_id'],
                    #'account_id': account_id,
                    'analytic_lines': line.get('analytic_lines', []),
                    'amount_currency': line['price']>0 and abs(line.get('amount_currency', False)) or -abs(line.get('amount_currency', False)),
                    'currency_id': line.get('currency_id', False),
                    'tax_code_id': line.get('tax_code_id', False),
                    'tax_amount': line.get('tax_amount', False),
                    'ref': line.get('ref', False),
                    'quantity': line.get('quantity',1.00),
                    'product_id': line.get('product_id', False),
                    'product_uom_id': line.get('uos_id', False),
                    'analytic_account_id': line.get('account_analytic_id', False),
                    'main_group': account_id,
                }
                print 'res111111>>>',res
                return res
        if type=='in_refund' :
            if line['price']<0:
                product = self.env['product.product'].browse(line.get('product_id', False))
                print 'product>>>',product.id
                print 'line.get>>>',line.get('product_id', False)
                account_id = product.product_tmpl_id.main_group.property_account_payable.id
                #acount_id= product.product_tmpl_id.main_group.property_account_payable.id
                print 'account_id>>>',account_id        
    
                print 'line>>>',line
                res= {
                    'date_maturity': line.get('date_maturity', False),
                    'partner_id': part,
                    'name': line['name'][:64],
                    'date': date,
                    'debit': line['price']>0 and line['price'],
                    'credit': line['price']<0 and -line['price'],
                    'account_id': line['account_id'],
                    #'account_id': account_id,
                    'analytic_lines': line.get('analytic_lines', []),
                    'amount_currency': line['price']>0 and abs(line.get('amount_currency', False)) or -abs(line.get('amount_currency', False)),
                    'currency_id': line.get('currency_id', False),
                    'tax_code_id': line.get('tax_code_id', False),
                    'tax_amount': line.get('tax_amount', False),
                    'ref': line.get('ref', False),
                    'quantity': line.get('quantity',1.00),
                    'product_id': line.get('product_id', False),
                    'product_uom_id': line.get('uos_id', False),
                    'analytic_account_id': line.get('account_analytic_id', False),
                    'main_group': account_id,
                }
                print 'res111111>>>',res
                return res            
        if type=='out_refund' :
            
            if line['price']>0:
                product = self.env['product.product'].browse(line.get('product_id', False))
                print 'product>>>',product.id
                print 'line.get>>>',line.get('product_id', False)
                if  line['name']=='Discount':
                    account_id = product.product_tmpl_id.main_group.property_account_discount.id
                else:
                    account_id = product.product_tmpl_id.main_group.property_account_receivable.id
                res= {
                    'date_maturity': line.get('date_maturity', False),
                    'partner_id': part,
                    'name': line['name'][:64],
                    'date': date,
                    'debit': line['price']>0 and line['price'],
                    'credit': line['price']<0 and -line['price'],
                    'account_id': line['account_id'],
                    #'account_id': account_id,
                    'analytic_lines': line.get('analytic_lines', []),
                    'amount_currency': line['price']>0 and abs(line.get('amount_currency', False)) or -abs(line.get('amount_currency', False)),
                    'currency_id': line.get('currency_id', False),
                    'tax_code_id': line.get('tax_code_id', False),
                    'tax_amount': line.get('tax_amount', False),
                    'ref': line.get('ref', False),
                    'quantity': line.get('quantity',1.00),
                    'product_id': line.get('product_id', False),
                    'product_uom_id': line.get('uos_id', False),
                    'analytic_account_id': line.get('account_analytic_id', False),
                    'main_group': account_id,
                }
                print 'res111111>>>',res
                return res    
        if type=='in_invoice' :
            if line['price']>0:
                product = self.env['product.product'].browse(line.get('product_id', False))
                print 'product>>>',product.id
                print 'line.get>>>',line.get('product_id', False)
                if  line['name']=='Discount':
                    account_id = product.product_tmpl_id.main_group.property_account_discount.id
                else:
                    account_id = product.product_tmpl_id.main_group.property_account_payable.id                

                res= {
                    'date_maturity': line.get('date_maturity', False),
                    'partner_id': part,
                    'name': line['name'][:64],
                    'date': date,
                    'debit': line['price']>0 and line['price'],
                    'credit': line['price']<0 and -line['price'],
                    'account_id': line['account_id'],
                    #'account_id': account_id,
                    'analytic_lines': line.get('analytic_lines', []),
                    'amount_currency': line['price']>0 and abs(line.get('amount_currency', False)) or -abs(line.get('amount_currency', False)),
                    'currency_id': line.get('currency_id', False),
                    'tax_code_id': line.get('tax_code_id', False),
                    'tax_amount': line.get('tax_amount', False),
                    'ref': line.get('ref', False),
                    'quantity': line.get('quantity',1.00),
                    'product_id': line.get('product_id', False),
                    'product_uom_id': line.get('uos_id', False),
                    'analytic_account_id': line.get('account_analytic_id', False),
                    'main_group': account_id,
                }
                print 'res111111>>>',res
                return res    
            
    def line_get_convert_dr(self, line, part, date):
        account_id = None
        discount_amt=0
        deduct=False
        cr=self._cr
        type='out_invoice' 
        print 'line_get_convert_newline_get_convert_new',line,part, self.id
        origin=line.get('ref', False)
        if origin:
            cr.execute("select type from account_invoice where origin=%s",(origin,))
            type=cr.fetchone()
            if type:
                type=type[0]
            else:
                type=None
        if type=='out_invoice' and line.get('product_id', False) != False or  line['name']=='Cash Discount':      
            if line['price']<0 or line['name']=='Discount' or line['name']=='Cash Discount':
                product = self.env['product.product'].browse(line.get('product_id', False))
                print 'product>>>',product.id
                print 'line.get>>>',line.get('product_id', False)
                if origin and line['name']!='Discount' and line['name']!='Cash Discount':
                    cr.execute('''select avl.discount_amt + (av.deduct_amt/(select avl.count from account_invoice av,account_invoice_line avl  where av.id=avl.invoice_id  and av.origin=%s  and avl.price_unit>0)) +((av.amount_untaxed * (av.additional_discount/100))/ (select avl.count from account_invoice av,account_invoice_line avl  where av.id=avl.invoice_id  and av.origin=%s and avl.price_unit>0)) 
                        from account_invoice av,account_invoice_line avl  
                        where av.id=avl.invoice_id and av.origin=%s and avl.price_unit>0 and avl.product_id=%s''',(origin,origin,origin,product.id,))
#                    discount_amt=cr.fetchone()[0]   
                    dis_amt = cr.fetchone()
                    print 'dis_amtdis_amtdis_amtdis_amt',dis_amt
                    if dis_amt is not None: 
                        discount_amt = discount_amt + dis_amt[0]; 
                    if discount_amt >0:     
                            line['price'] = line['price']+discount_amt
                            if  line['price']>0: 
                                deduct=True;
                                
#                     if dis_amt:     
#                         for amt in dis_amt:
#                             if amt[0] is not None:                                 
#                                 discount_amt = discount_amt + amt[0];                       
#                     if discount_amt:     
#                             line['price'] = line['price']+discount_amt 
                if  line['name']=='Discount': 
                    account_id = product.product_tmpl_id.main_group.property_account_discount.id
                elif  line['name']=='Cash Discount':       
                    account_id=self.company_id.discount_cash_account_id.id
                else:
                    account_id = product.product_tmpl_id.main_group.property_account_receivable.id
                print 'account_id>>>',account_id        
    
                print 'line>>>',line
                print 'line[price]',line['price']
                if line['price']<0 or deduct==True:
                    line['price'] = -line['price']
                print 'line[price]ssssss',line['price']
                    
                res= {
                    'date_maturity': line.get('date_maturity', False),
                    'partner_id': part,
                    'name': line['name'][:64],
                    'date': date,
                    'debit': line['price']>0 and line['price'],
                    'credit': line['price']<0 and -line['price'],
                    #'account_id': line['account_id'],
                    'account_id': account_id,
                    'analytic_lines': line.get('analytic_lines', []),
                    'amount_currency': line['price']>0 and abs(line.get('amount_currency', False)) or -abs(line.get('amount_currency', False)),
                    'currency_id': line.get('currency_id', False),
                    'tax_code_id': line.get('tax_code_id', False),
                    'tax_amount': line.get('tax_amount', False),
                    'ref': line.get('ref', False),
                    'quantity': line.get('quantity',1.00),
                    'product_id': line.get('product_id', False),
                    'product_uom_id': line.get('uos_id', False),
                    'analytic_account_id': line.get('account_analytic_id', False),
                    'main_group': account_id,
                }
                print 'res111111>>>',res
                return res
        if type=='in_refund' :
            if line['price']<0:
                product = self.env['product.product'].browse(line.get('product_id', False))
                print 'product>>>',product.id
                print 'line.get>>>',line.get('product_id', False)
                account_id = product.product_tmpl_id.main_group.property_account_payable.id
                print 'account_id>>>',account_id        
    
                print 'line>>>',line
                print 'line[price]',line['price']
                line['price'] = -line['price']
                print 'after>>>',line['price']
                res= {
                    'date_maturity': line.get('date_maturity', False),
                    'partner_id': part,
                    'name': line['name'][:64],
                    'date': date,
                    'debit': line['price']>0 and line['price'],
                    'credit': line['price']<0 and -line['price'],
                    'account_id': line['account_id'],
                    #'account_id': account_id,
                    'analytic_lines': line.get('analytic_lines', []),
                    'amount_currency': line['price']>0 and abs(line.get('amount_currency', False)) or -abs(line.get('amount_currency', False)),
                    'currency_id': line.get('currency_id', False),
                    'tax_code_id': line.get('tax_code_id', False),
                    'tax_amount': line.get('tax_amount', False),
                    'ref': line.get('ref', False),
                    'quantity': line.get('quantity',1.00),
                    'product_id': line.get('product_id', False),
                    'product_uom_id': line.get('uos_id', False),
                    'analytic_account_id': line.get('account_analytic_id', False),
                    'main_group': account_id,
                }
                print 'res111111>>>',res
                return res            
        if type=='out_refund' :
            if line['price']>0 or line['name']=='Discount':
                product = self.env['product.product'].browse(line.get('product_id', False))
                print 'product>>>',product.id
                print 'line.get>>>',line.get('product_id', False)
                if origin and line['name']!='Discount':
                    cr.execute("select avl.discount_amt from account_invoice av,account_invoice_line avl  where av.id=avl.invoice_id and av.origin=%s and avl.product_id=%s",(origin,product.id,))
                    dis_amt = cr.fetchall()
                    if dis_amt:     
                        for amt in dis_amt:
                            if amt[0] is not None:                                 
                                discount_amt = discount_amt + amt[0];        
                    if discount_amt:     
                            line['price'] = line['price']-discount_amt
                if  line['name']=='Discount':
                    account_id = product.product_tmpl_id.main_group.property_account_discount.id
                    line['price']=-1* line['price']
                else:
                    account_id = product.product_tmpl_id.main_group.property_account_receivable.id
                print 'account_id>>>',account_id        
                print 'line>>>',line
                print 'line[price]',line['price']
                line['price'] = -line['price']
                print 'after>>>',line['price']
                res= {
                    'date_maturity': line.get('date_maturity', False),
                    'partner_id': part,
                    'name': line['name'][:64],
                    'date': date,
                    'debit': line['price']>0 and line['price'],
                    'credit': line['price']<0 and -line['price'],
                    'account_id': line['account_id'],
                    #'account_id': account_id,
                    'analytic_lines': line.get('analytic_lines', []),
                    'amount_currency': line['price']>0 and abs(line.get('amount_currency', False)) or -abs(line.get('amount_currency', False)),
                    'currency_id': line.get('currency_id', False),
                    'tax_code_id': line.get('tax_code_id', False),
                    'tax_amount': line.get('tax_amount', False),
                    'ref': line.get('ref', False),
                    'quantity': line.get('quantity',1.00),
                    'product_id': line.get('product_id', False),
                    'product_uom_id': line.get('uos_id', False),
                    'analytic_account_id': line.get('account_analytic_id', False),
                    'main_group': account_id,
                }
                print 'res111111>>>',res
                return res
        if type=='in_invoice' :
            if line['price']>0 or line['name']=='Discount' :
                product = self.env['product.product'].browse(line.get('product_id', False))
                print 'product>>>',product.id
                print 'line.get>>>',line.get('product_id', False)
                if origin and line['name']!='Discount':
                    cr.execute("select avl.discount_amt from account_invoice av,account_invoice_line avl  where av.id=avl.invoice_id and av.origin=%s and avl.product_id=%s",(origin,product.id,))
                    discount_amt=cr.fetchone()[0]      
                    if discount_amt:     
                            line['price'] = line['price']-discount_amt
                if  line['name']=='Discount':
                    account_id = product.product_tmpl_id.main_group.property_account_discount.id
                    line['price']=-1* line['price']
                else:
                    account_id = product.product_tmpl_id.main_group.property_account_payable.id                
                print 'account_id>>>',account_id        
                print 'line>>>',line
                print 'line[price]',line['price']
                line['price'] = -line['price']
                print 'after>>>',line['price']
                res= {
                    'date_maturity': line.get('date_maturity', False),
                    'partner_id': part,
                    'name': line['name'][:64],
                    'date': date,
                    'debit': line['price']>0 and line['price'],
                    'credit': line['price']<0 and -line['price'],
                    'account_id': line['account_id'],
                    #'account_id': account_id,
                    'analytic_lines': line.get('analytic_lines', []),
                    'amount_currency': line['price']>0 and abs(line.get('amount_currency', False)) or -abs(line.get('amount_currency', False)),
                    'currency_id': line.get('currency_id', False),
                    'tax_code_id': line.get('tax_code_id', False),
                    'tax_amount': line.get('tax_amount', False),
                    'ref': line.get('ref', False),
                    'quantity': line.get('quantity',1.00),
                    'product_id': line.get('product_id', False),
                    'product_uom_id': line.get('uos_id', False),
                    'analytic_account_id': line.get('account_analytic_id', False),
                    'main_group': account_id,
                }
                print 'res111111>>>',res
                return res
        
#     def line_get_product(self, line, part, date):
#         account_id = None
#         cr=self._cr
#         type='out_invoice' 
#         print 'line_get_convert_newline_get_convert_new',line,part
#         origin=line.get('ref', False)
#         print 'originoriginoriginoriginorigin',origin
#         if origin:
#             cr.execute("select type from account_invoice where origin=%s",(origin,))
#             type=cr.fetchone()
#             if type:
#                 type=type[0]
#             else:
#                 type='out_invoice' 
#         if type=='out_invoice' :
#             if line['price']<0:
#                 product = self.env['product.product'].browse(line.get('product_id', False))
#                 print 'product>>>',product.id
#                 print 'line.get>>>',line.get('product_id', False)
#                 account_id = product.product_tmpl_id.main_group.property_account_receivable.id
#                 print 'account_id>>>',account_id        
#     
#                 print 'line>>>',line
#                 res= {
#                     
#                     'product_id': line.get('product_id', False),                
#                     'main_group': account_id,
#                 }
#                 print 'res222>>>',res
#                 return res 
#         if type=='in_refund' :
#             if line['price']<0:
#                 product = self.env['product.product'].browse(line.get('product_id', False))
#                 print 'product>>>',product.id
#                 print 'line.get>>>',line.get('product_id', False)
#                 account_id = product.product_tmpl_id.main_group.property_account_payable.id
#                 print 'account_id>>>',account_id        
#     
#                 print 'line>>>',line
#                 res= {
#                     
#                     'product_id': line.get('product_id', False),                
#                     'main_group': account_id,
#                 }
#                 print 'res222>>>',res
#                 return res            
#         if type=='out_refund' :
#             if line['price']>0:
#                 product = self.env['product.product'].browse(line.get('product_id', False))
#                 print 'product>>>',product.id
#                 print 'line.get>>>',line.get('product_id', False)
#                 account_id = product.product_tmpl_id.main_group.property_account_receivable.id
#                 print 'account_id>>>',account_id        
#     
#                 print 'line>>>',line
#                 res= {
#                     
#                     'product_id': line.get('product_id', False),                
#                     'main_group': account_id,
#                 }
#                 print 'res222>>>',res
#                 return res           
#         if type=='in_invoice' :
#             if line['price']>0:
#                 product = self.env['product.product'].browse(line.get('product_id', False))
#                 print 'product>>>',product.id
#                 print 'line.get>>>',line.get('product_id', False)
#                 account_id = product.product_tmpl_id.main_group.property_account_payable.id
#                 print 'account_id>>>',account_id        
#     
#                 print 'line>>>',line
#                 res= {
#                     
#                     'product_id': line.get('product_id', False),                
#                     'main_group': account_id,
#                 }
#                 print 'res222>>>',res
#                 return res         
            
    def line_dr_convert_account_with_principle(self, line):
        list_one = line
        print 'list_one>>>',list_one
        list_group = [i['main_group'] for i in list_one if i is not None]
        print 'i>>>',list_group
        val = set(map(lambda x:x, list_group))
        print 'val',val
        arr_list = []
        for v in val:
            print 'v',v
            price = 0
            date_maturity = partner_id = name = date  = account_id = analytic_lines = amount_currency = currency_id = tax_code_id = tax_amount = ref = quantity = product_id = product_uom_id = analytic_account_id = None
            debit = credit=0
            result = [a for a in list_one if a is not None and a['main_group'] == v]
            print 'result>>>',result
            cr=self._cr

            for res in result:
                origin=res['ref']
                if origin:
                    cr.execute("select type from account_invoice where origin=%s",(origin,))
                    type=cr.fetchone()
                    if type:
                        type=type[0]
                    else:
                        type=None   
                if type=='out_invoice' or (type=='out_invoice' and res['credit']>0):
                    debit += res['debit']-res['credit']
                if type=='in_invoice':             
                    credit += res['credit']    
                if type=='out_refund':             
                    credit += res['credit']       
                if type=='in_refund':             
                    debit += res['debit']                                             
                date_maturity = res['date_maturity']
                partner_id = res['partner_id']
                name = res['name']
                date = res['date']
                account_id = res['main_group'] #replace with product principle AR account
                analytic_lines = res['analytic_lines']
                amount_currency = res['amount_currency']
                currency_id = res['currency_id']
                tax_code_id = res['tax_code_id']
                tax_amount = res['tax_amount']
                ref = res['ref']
                quantity = res['quantity']
                product_id = res['product_id']
                product_uom_id = res['product_uom_id']
                analytic_account_id = res['analytic_account_id']
            price=credit+debit
            if price!=0.0:
                rec = {
                            'date_maturity': date_maturity,
                            'partner_id': partner_id,
                            'name': name,
                            'date': date,
                            'debit': debit,
                            'credit': credit,
                            'account_id': account_id,
                            'analytic_lines': analytic_lines,
                            'amount_currency': amount_currency,
                            'currency_id': currency_id,
                            'tax_code_id': tax_code_id,
                            'tax_amount': tax_amount,
                            'ref': ref,
                            'quantity': quantity,
                            'product_id': product_id,
                            'product_uom_id': product_uom_id,
                            'analytic_account_id': analytic_account_id,
                           
                        }
                arr_list.append(rec)
        return arr_list           
    
#     def line_get_convert_accountid(self, line, product, part, date):
#         account_id = None
#         print 'main>>>',line
#         [(0, 0, self.line_get_convert_accountid(l, part.id, date)) for l in line]
#         
#         values = set(map(lambda x:x[1], product))
#         newlist = [[y[0] for y in list if y[1]==x] for x in values] 
#           
#         if line['main_group'] > 0: 
#             print 'test' 
#             account_id =  line['account_id']
#             #print 'line>>>',line
#             res= {
#                 'date_maturity': line.get('date_maturity', False),
#                 'partner_id': part,
#                 'name': line['name'][:64],
#                 'date': date,
#                 'debit': line['debit'],
#                 'credit': line['credit'],
#                 'account_id': account_id,
#                 #'account_id': account_id,
#                 'analytic_lines': line.get('analytic_lines', []),
#                 'amount_currency': line['amount_currency'],
#                 'currency_id': line.get('currency_id', False),
#                 'tax_code_id': line.get('tax_code_id', False),
#                 'tax_amount': line.get('tax_amount', False),
#                 'ref': line.get('ref', False),
#                 'quantity': line.get('quantity',1.00),
#                 'product_id': line.get('product_id', False),
#                 'product_uom_id': line.get('uos_id', False),
#                 'analytic_account_id': line.get('account_analytic_id', False),
#                 'main_group': account_id,
#             }
#             #print 'res>>>',res
#             return res         
#         else:
#             account_id = 633                             
#     def line_get_convert_accountid(self, line, part, date):
#         account_id = None
#         #print 'main>>>',line
#         if line['main_group'] > 0: 
#             print 'test' 
#             account_id =  line['account_id']
#             #print 'line>>>',line
#             res= {
#                 'date_maturity': line.get('date_maturity', False),
#                 'partner_id': part,
#                 'name': line['name'][:64],
#                 'date': date,
#                 'debit': line['debit'],
#                 'credit': line['credit'],
#                 'account_id': account_id,
#                 #'account_id': account_id,
#                 'analytic_lines': line.get('analytic_lines', []),
#                 'amount_currency': line['amount_currency'],
#                 'currency_id': line.get('currency_id', False),
#                 'tax_code_id': line.get('tax_code_id', False),
#                 'tax_amount': line.get('tax_amount', False),
#                 'ref': line.get('ref', False),
#                 'quantity': line.get('quantity',1.00),
#                 'product_id': line.get('product_id', False),
#                 'product_uom_id': line.get('uos_id', False),
#                 'analytic_account_id': line.get('account_analytic_id', False),
#                 'main_group': account_id,
#             }
#             #print 'res>>>',res
#             return res         
# #         else:
# #             account_id = 633
 
        
    @api.multi
    def action_move_create(self):
        """ Creates invoice related analytics and financial move lines """
        account_invoice_tax = self.env['account.invoice.tax']
        account_move = self.env['account.move']
        
        for inv in self:
            if not inv.journal_id.sequence_id:
                raise except_orm(_('Error!'), _('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line:
                raise except_orm(_('No Invoice Lines!'), _('Please create some invoice lines.'))
            if inv.move_id:
                continue

            ctx = dict(self._context, lang=inv.partner_id.lang)
            company_currency = inv.company_id.currency_id
            if not inv.date_invoice:
                # FORWARD-PORT UP TO SAAS-6
                if inv.currency_id != company_currency and inv.tax_line:
                    raise except_orm(
                        _('Warning!'),
                        _('No invoice date!'
                            '\nThe invoice currency is not the same than the company currency.'
                            ' An invoice date is required to determine the exchange rate to apply. Do not forget to update the taxes!'
                        )
                    )                
                inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
            date_invoice = inv.date_invoice

            # create the analytical lines, one move line per invoice line
            iml = inv._get_analytic_lines()
            # check if taxes are all computed
            compute_taxes = account_invoice_tax.compute(inv.with_context(lang=inv.partner_id.lang))
            inv.check_tax_lines(compute_taxes)

            # I disabled the check_total feature
            if self.env.user.has_group('account.group_supplier_inv_check_total'):
                if inv.type in ('in_invoice', 'in_refund') and abs(inv.check_total - inv.amount_total) >= (inv.currency_id.rounding / 2.0):
                    raise except_orm(_('Bad Total!'), _('Please verify the price of the invoice!\nThe encoded total does not match the computed total.'))

            if inv.payment_term:
                total_fixed = total_percent = 0
                for line in inv.payment_term.line_ids:
                    if line.value == 'fixed':
                        total_fixed += line.value_amount
                    if line.value == 'procent':
                        total_percent += line.value_amount
                total_fixed = (total_fixed * 100) / (inv.amount_total or 1.0)
                if (total_fixed + total_percent) > 100:
                    raise except_orm(_('Error!'), _("Cannot create the invoice.\nThe related payment term is probably misconfigured as it gives a computed amount greater than the total invoiced amount. In order to avoid rounding issues, the latest line of your payment term must be of type 'balance'."))

            # one move line per tax line
            iml += account_invoice_tax.move_line_get(inv.id)

            if inv.type in ('in_invoice', 'in_refund'):
                ref = inv.reference
            else:
                ref = inv.number

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, ref, iml)

            name = inv.supplier_invoice_number or inv.name or '/'
            totlines = []
            if inv.payment_term:
                totlines = inv.with_context(ctx).payment_term.compute(total, date_invoice)[0]
            if totlines:
                res_amount_currency = total_currency
                ctx['date'] = date_invoice
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
                    else:
                        amount_currency = False

                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency
                    
                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': inv.account_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'ref': ref,
                    })
            else:
                
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'ref': ref
                })

            date = date_invoice

            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)

            #line = [(0, 0, self.line_get_convert(l, part.id, date)) for l in iml]
            data=[]
            for res in iml:
                res['ref']=inv.origin
                data.append(res)
            iml=data
            line_cr = [self.line_get_convert_new(l, part.id, date) for l in iml]
            line_tmp = [self.line_get_convert_dr(l,part.id,date) for l in iml]
            line_dr = self.line_dr_convert_account_with_principle(line_tmp)
            #line_product = [self.line_get_product(l, part.id, date) for l in iml]
            #line_dr = [(0, 0, self.line_get_convert_accountid(l, part.id, date)) for l in line_cr]
            lines = line_cr + line_dr
            line = [(0, 0, self.line_get_convert(l, part.id, date)) for l in lines  if l is not None]
            
            line = inv.group_lines(iml, line)

            journal = inv.journal_id.with_context(ctx)
            if journal.centralisation:
                raise except_orm(_('User Error!'),
                        _('You cannot create an invoice on a centralized journal. Uncheck the centralized counterpart box in the related journal from the configuration menu.'))

            line = inv.finalize_invoice_move_lines(line)

            move_vals = {
                'ref': inv.reference or inv.name,
                'line_id': line,
                'journal_id': journal.id,
                'date': inv.date_invoice,
                'narration': inv.comment,
                'company_id': inv.company_id.id,                
            }
            ctx['company_id'] = inv.company_id.id
            period = inv.period_id
            if not period:
                period = period.with_context(ctx).find(date_invoice)[:1]
            if period:
                move_vals['period_id'] = period.id
                for i in line:
                    i[2]['period_id'] = period.id

            ctx['invoice'] = inv
            ctx_nolang = ctx.copy()
            ctx_nolang.pop('lang', None)
            print 'move_valsmove_valsmove_vals',move_vals
            move = account_move.with_context(ctx_nolang).create(move_vals)

            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'period_id': period.id,
                'move_name': move.name,
            }
            inv.with_context(ctx).write(vals)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post()
        self._log_event()
        return True
    
    account_id = fields.Many2one('account.account', string='Account',
        required=False, readonly=True, states={'draft': [('readonly', False)]},
        help="The partner account used for this invoice.")
    
    
