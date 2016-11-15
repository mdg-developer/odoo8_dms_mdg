from openerp.osv import fields, osv
from openerp.osv import orm
from openerp import _
from datetime import datetime
import ast
import time
import openerp.addons.decimal_precision as dp
import webbrowser
import subprocess

class cashier_approval(osv.osv):
    
    _name = "cashier.approval"
    _description = "Cashier Approval"
    
    def _amount_cash(self, cr, uid, ids, field_name, arg, context=None):
        """ Wrapper because of direct method passing as parameter for function fields """
        return self._amount_all(cr, uid, ids, field_name, arg, context=context)

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {                
                'cash_sub_total': 0.0,
            }
            val = val1 = 0.0
            # cur = order.pricelist_id.currency_id
            for line in order.cashier_line:
                val1 += line.amount
                # val += self._amount_line_tax(cr, uid, line, context=context)           
            res[order.id]['cash_sub_total'] = round(val1)  # cur_obj.round(cr, uid, cur, val1)
        return res 
     
    def _amount_ar(self, cr, uid, ids, field_name, arg, context=None):
        """ Wrapper because of direct method passing as parameter for function fields """
        return self._amount_ar_all(cr, uid, ids, field_name, arg, context=context)
    
    def _amount_ar_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {                
                'ar_sub_total': 0.0,
            }
            val = val1 = 0.0            
            for line in order.ar_line:
                val1 += line.amount
                           
            res[order.id]['ar_sub_total'] = round(val1)  # cur_obj.round(cr, uid, cur, val1)
        return res 
    
    def _amount_cr(self, cr, uid, ids, field_name, arg, context=None):
        """ Wrapper because of direct method passing as parameter for function fields """
        return self._amount_cr_all(cr, uid, ids, field_name, arg, context=context)
    
    def _amount_cr_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {                
                'cr_sub_total': 0.0,
            }
            val = val1 = 0.0            
            for line in order.credit_line:
                val1 += line.amount
                           
            res[order.id]['cr_sub_total'] = round(val1)  # cur_obj.round(cr, uid, cur, val1)
        return res
    def _amount_denomination(self, cr, uid, ids, field_name, arg, context=None):
        """ Wrapper because of direct method passing as parameter for function fields """
        return self._amount_denomination_all(cr, uid, ids, field_name, arg, context=context)
    def _amount_denomination_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {                
                'denomination_sub_total': 0.0,
            }
            val = val1 = 0.0            
            for line in order.denomination_line:
                val1 += line.notes * line.note_qty
            print 'deno val>>>', val1
            cr.execute("""update cashier_approval set denomination_sub_total=%s where id=%s""", (val1, ids[0],))                 
            res[order.id]['denomination_sub_total'] = round(val1)  # cur_obj.round(cr, uid, cur, val1)
        return res
    def _amount_total_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        print 'ids', ids
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {                
                'total': 0.0,
            }
            val = val1 = 0.0 
            # cur = order.pricelist_id.currency_id
            # for line in order.id:
            print 'total', order.cash_sub_total, order.ar_sub_total, order.cr_sub_total 
            val1 += (order.cash_sub_total + order.ar_sub_total) - order.cr_sub_total 
                # val += self._amount_line_tax(cr, uid, line, context=context)    
            cr.execute("""update cashier_approval set total=%s where id=%s""", (val1, ids[0],))       
            res[order.id]['total'] = round(val1)  # cur_obj.round(cr, uid, cur, val1)
        return res      
    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('cashier.approval.invoice.line').browse(cr, uid, ids, context=context):
            result[line.cashier_id.id] = True
        return result.keys()
    def button_dummy(self, cr, uid, ids, context=None):
        self._amount_total_all(cr, uid, ids, ['total'], None, context)
        self._amount_denomination_all(cr, uid, ids, ['denomination_sub_total'], None, context)
        return True    
    def _get_ar(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('cashier.approval.ar.line').browse(cr, uid, ids, context=context):
            result[line.cashier_id.id] = True
        return result.keys()
    
    def _get_credit(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('cashier.approval.credit.line').browse(cr, uid, ids, context=context):
            result[line.cashier_id.id] = True
        return result.keys()
    def _get_denomination(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('cashier.denomination.line').browse(cr, uid, ids, context=context):
            result[line.cashier_id.id] = True
        return result.keys()
   
    _columns = {
        'name': fields.char('Order Reference', size=64),
        'user_id':fields.many2one('res.users', 'Salesman',required=True),
        'sale_team_id':fields.many2one('crm.case.section', 'Sales Team',required=True),
      'date':fields.date('Date'),
      'to_date':fields.date('To Date'),
      'cashier_line': fields.one2many('cashier.approval.invoice.line', 'cashier_id', 'Cashier Approval Form'),
      'ar_line': fields.one2many('cashier.approval.ar.line', 'cashier_id', 'Cashier Approval Form'),
      'credit_line': fields.one2many('cashier.approval.credit.line', 'cashier_id', 'Cashier Approval Form'),
      'denomination_line': fields.one2many('cashier.denomination.line', 'cashier_id', 'Cashier Approval Form'),
      'denomination_product_line': fields.one2many('cashier.denomination.product.line', 'cashier_id', 'Cashier Approval Form'),
      'cashier_customer_payment_line': fields.one2many('cashier.customer.payment', 'cashier_id', 'Cashier Approval Form'),
      'cash_sub_total': fields.function(_amount_cash, digits_compute=dp.get_precision('Account'), string='SubTotal',
            store={
                'cashier.approval': (lambda self, cr, uid, ids, c={}: ids, ['cashier_line'], 10),
                'cashier.approval.invoice.line': (_get_order, ['amount'], 10),
            },
            multi='sums', help="The cash total amount."),
      'ar_sub_total': fields.function(_amount_ar, digits_compute=dp.get_precision('Account'), string='SubTotal',
            store={
                'cashier.approval': (lambda self, cr, uid, ids, c={}: ids, ['ar_line'], 10),
                'cashier.approval.ar.line': (_get_ar, ['amount'], 10),
            },
            multi='sums', help="The AR total amount."),
      'cr_sub_total': fields.function(_amount_cr, digits_compute=dp.get_precision('Account'), string='SubTotal',
            store={
                'cashier.approval': (lambda self, cr, uid, ids, c={}: ids, ['ar_line'], 10),
                'cashier.approval.credit.line': (_get_credit, ['amount'], 10),
            },
            multi='sums', help="The credit total amount."),
       'denomination_sub_total': fields.function(_amount_denomination, digits_compute=dp.get_precision('Account'), string='SubTotal',
            store={
                'cashier.approval': (lambda self, cr, uid, ids, c={}: ids, ['denomination_line'], 10),
                'cashier.denomination.line': (_get_denomination, ['amount'], 10),
            },
            multi='sums', help="The credit total amount."),         
       'total': fields.function(_amount_total_all, digits_compute=dp.get_precision('Account'), string='Total Net',
            multi='sums', help="The credit total amount.", store=True,),
        'state':fields.selection([('draft', 'Draft'), ('pending', 'Confirmed'),('done', 'Done')], 'Status'),        
                                                               
    }
    _order = 'id desc'
    _defaults = {
        'date': datetime.now(),
        'to_date' : datetime.now(),
        'state' : 'draft',
       
    } 
    
   
    def confirm_(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'pending'}, context=context)
        return True   
     
    def set_to_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'draft'}, context=context)
        return True 
    def generate_report(self, cr, uid, ids, context=None):
        url = "http://localhost:8080/birt/frameset?__report=daily_sale_report.rptdesign"
        #url = "http://10.0.1.30:8080/birt/frameset?__report=daily_sale_report.rptdesign"
        webbrowser.open(url)        
        #webbrowser.open_new_tab(url,new=2)
    def cashier_approve(self, cr, uid, ids, context=None):
        voucherObj = self.pool.get('account.voucher')
        voucherLineObj = self.pool.get('account.voucher.line')
        mobilearObj = self.pool.get('mobile.ar.collection')
        datas = self.read(cr, uid, ids, ['date', 'to_date', 'user_id', 'sale_team_id'], context=None)
        print 'datas>>>generte_ar', datas,
        frm_date = to_date = user_id = None
            
        if datas:
            for data in datas:
                frm_date = data['date']
                to_date = data['to_date']
                user_id = data['user_id'][0]
                team_id = data['sale_team_id'][0]
               
            if to_date:
                print 'to_date>>', to_date
                cr.execute("""select so_ref,id from mobile_ar_collection where --state='pending' and 
               user_id=%s and sale_team_id=%s and date >= %s and date <= %s
                """, (user_id, team_id, frm_date, to_date,))
            else:
                print 'date>>', frm_date
                cr.execute("""select so_ref,id from mobile_ar_collection where --state='pending' and 
                user_id=%s and sale_team_id=%s and date = %s 
                """, (user_id, team_id, frm_date,))
            vals = cr.fetchall()
            
            self.create_journal_ms(cr, uid, ids, context)
            
                        
        self.write(cr, uid, ids, {'state':'done'}, context=context)
        return True   
    
    def create_journal_ms(self, cr, uid, ids, context=None):
        invoiceObj = self.pool.get('account.invoice')
        voucherObj = self.pool.get('account.voucher')
        voucherLineObj = self.pool.get('account.voucher.line')
        payment_line_obj = self.pool.get('cashier.customer.payment')
        cr.execute("""select journal_id,amount,type,partner_id,account_id,date_invoice,period_id,notes,invoice_id from cashier_customer_payment where cashier_id=%s and pre_so='t'""",(ids[0], )) 
        payment_data = cr.fetchall()
        if payment_data:
            for payment in payment_data:
                print 'test',payment[8],ids
                inv_id = []
                inv_id.append(payment[8])
                invoice = invoiceObj.browse(cr, uid, inv_id, context=context)
                print 'invoicenameeeeee',invoice.number
                #invoiceObj.invoice_pay_customer(cr, uid, inv_id, context=context)
                accountVResult = {
                                        'partner_id':payment[3],
                                        'amount':payment[1],
                                        'journal_id':payment[0],#acc_data[0],
                                        'date':payment[5],
                                        'period_id':payment[6],
                                        'account_id':payment[4],
                                        'pre_line':True,
                                        'type':'receipt',
                                        'reference':payment[7],
                                          'payment_option': "without_writeoff",
                                         'company_id':invoice.company_id.id

                                        }
                    # create register payment voucher
                voucherId = voucherObj.create(cr, uid, accountVResult, context=context)                
                if voucherId:
                    vlist = []
                    vlist.append(voucherId)                      
                    line_data = {
                                    #'name': invoice.number,
                                    'voucher_id' : voucherId,
                                    'move_line_id' : invoice.move_id.line_id[0].id,
                                    'account_id' : invoice.account_id.id,#invoice.move_id.line_id[0].account_id.id,
                                    'partner_id' : payment[3],
                                    "amount" : payment[1],
                                    "amount_original": invoice.amount_total,
                                    'type': 'cr',
                                }
                    voucherLineObj.create(cr, uid, line_data, context=context)  
                    voucherObj.button_proforma_voucher(cr, uid, vlist , context=context)
                    cr.execute("""update account_invoice set state='paid'
                    where id=%s and residual=0""",(invoice.id,))
                    cr.execute("""update sale_order set invoiced='t' from account_invoice
                    where sale_order.name=account_invoice.reference and account_invoice.residual=0 and account_invoice.id=%s""",(invoice.id,))
                    cr.execute("update mobile_ar_collection set state='done' where ref_no=%s",(invoice.number,))

    def action_generate(self, cr, uid, ids, context=None):
        cr.execute("""delete from cashier_approval_invoice_line where cashier_id=%s""", (ids[0],))
        result = {}
        invoice_line_data = []
        cashier_approval_obj = self.pool.get('cashier.approval')
        invoice_line_obj = self.pool.get('cashier.approval.invoice.line')
        
        datas = cashier_approval_obj.read(cr, uid, ids, ['date', 'to_date', 'user_id', 'sale_team_id'], context=None)
        print 'datas>>>', datas,
        frm_date = to_date = user_id = None
            
        if datas:
            for data in datas:
                frm_date = data['date']
                to_date = data['to_date']
                user_id = data['user_id'][0]
            if to_date:
                cr.execute("""select a.id,a.date_invoice,a.partner_id,a.amount_total from sale_order s,account_invoice a 
                where s.name=a.reference and s.payment_type='cash' and a.state='open' --and a.state='paid' 
                and a.date_invoice >= %s and a.date_invoice <= %s and a.user_id=%s
                """, (frm_date, to_date, user_id,))
            else:
                cr.execute("""select a.id,a.date_invoice,a.partner_id,a.amount_total from sale_order s,account_invoice a 
                where s.name=a.reference and s.payment_type='cash' and a.state='open' --and a.state='paid' 
                and a.date_invoice = %s and a.user_id=%s""", (frm_date, user_id,))
            vals = cr.fetchall() 
            for val in vals:
                data_id = {'invoice_id':val[0],
                            'date':val[1],
                            'partner_id':val[2],
                            'amount':val[3],
                            'cashier_id':ids[0],
                            'payment_type':'Cash'}
                inv_id = invoice_line_obj.create(cr, uid, data_id, context=context)
                for details in self.browse(cr, uid, ids, context=context):
                
                    result[details.id] = inv_id
            self.generte_ar(cr, uid, ids, context=context)
            self.generte_cr(cr, uid, ids, context=context) 
            self.generate_denomination(cr, uid, ids, context=context)   
            self.generate_denomination_product(cr, uid, ids, context=context)
            self.generate_payment(cr, uid, ids, context=context)
            self.generate_payment_pre_so(cr, uid, ids, context=context)     
            self.generate_payment_ar(cr, uid, ids, context=context)
            
        return result
    
    def generte_ar(self, cr, uid, ids, context=None):
        cr.execute("""delete from cashier_approval_ar_line where cashier_id=%s""", (ids[0],))
        result = {}
        cashier_approval_obj = self.pool.get('cashier.approval')
        invoice_line_obj = self.pool.get('cashier.approval.ar.line')
        datas = cashier_approval_obj.read(cr, uid, ids, ['date', 'to_date', 'user_id', 'sale_team_id'], context=None)
        frm_date = to_date = user_id = None
        if datas:
            for data in datas:
                frm_date = data['date']
                to_date = data['to_date']
                user_id = data['user_id'][0]
                team_id = data['sale_team_id'][0]
            if to_date:
                cr.execute("""select m.date,a.number,m.partner_id,m.so_amount
                            from account_invoice as a,mobile_ar_collection as m
                            where m.ref_no = a.number and m.state='draft' and 
                            m.user_id=%s and m.sale_team_id=%s and m.date >= %s and m.date <= %s
                """, (user_id, team_id, frm_date, to_date,))
            else:
                cr.execute("""select m.date,a.number,m.partner_id,m.so_amount
                            from account_invoice as a,sale_order as s,mobile_ar_collection as m
                            where m.ref_no = a.number and  m.state='draft'  and
                            m.user_id=%s and m.sale_team_id=%s and m.date = %s  
                """, (user_id, team_id, frm_date,))
            vals = cr.fetchall()             
            for val in vals:
                data_id = {'invoice_id':val[1],
                            'date':val[0],
                            'partner_id':val[2],
                            'amount':val[3],
                            'cashier_id':ids[0],
                            'payment_type':'Credit'}
                inv_id=invoice_line_obj.create(cr, uid, data_id, context=context)
                for details in self.browse(cr, uid, ids, context=context):                
                    result[details.id] = inv_id
        return result
    
    def generte_cr(self, cr, uid, ids, context=None):
        print 'generte_cr'
        cr.execute("""delete from cashier_approval_credit_line where cashier_id=%s""", (ids[0],))
        result = {}
        invoice_line_data = []
        cashier_approval_obj = self.pool.get('cashier.approval')
        invoice_line_obj = self.pool.get('cashier.approval.credit.line')
        datas = cashier_approval_obj.read(cr, uid, ids, ['date', 'to_date', 'user_id', 'sale_team_id'], context=None)
        print 'datas>>>generte_cr', datas,
        frm_date = to_date = user_id = None
            
        if datas:
            for data in datas:
                frm_date = data['date']
                to_date = data['to_date']
                user_id = data['user_id'][0]
                team_id = data['sale_team_id'][0]
            if to_date:
                print 'to_date>>', to_date
                cr.execute("""select issued_date,so_no,id,amount,customer_id from account_creditnote where m_status='used' and sale_team_id=%s and issued_date >= %s and issued_date <= %s and user_id=%s
                """, (team_id, frm_date, to_date, user_id,))
            else:
                print 'date>>', frm_date
                cr.execute("""select issued_date,so_no,id,amount,customer_id from account_creditnote where m_status='used' and sale_team_id=%s and issued_date = %s  and user_id=%s 
                """, (team_id, frm_date, user_id,))
            vals = cr.fetchall()
            print 'vals>>>generte_cr', vals
            for val in vals:
                print ':val[1]>>', val[1]
                data_id = {'invoice_id':val[1],
                            'date':val[0],
                            'credit_id':val[2],
                            'partner_id':val[4],
                            'amount':val[3],
                            'cashier_id':ids[0],
                            }
                inv_id = invoice_line_obj.create(cr, uid, data_id, context=context)
                for details in self.browse(cr, uid, ids, context=context):                
                    result[details.id] = inv_id
        return result
    
    def generate_denomination(self, cr, uid, ids, context=None):
        print 'generte_deno'
        cr.execute("""delete from cashier_denomination_line where cashier_id=%s""", (ids[0],))
        result = {}
        invoice_line_data = []
        cashier_approval_obj = self.pool.get('cashier.approval')
        invoice_line_obj = self.pool.get('cashier.denomination.line') 
        datas = cashier_approval_obj.read(cr, uid, ids, ['date', 'to_date', 'user_id', 'sale_team_id'], context=None)
        print 'datas>>>generte_cr', datas,
        frm_date = to_date = user_id = None            
        if datas:
            for data in datas:
                frm_date = data['date']
                to_date = data['to_date']
                user_id = data['user_id'][0]
                team_id = data['sale_team_id'][0]
            if to_date:
                print 'to_date>>', to_date
                cr.execute("""select * from 
                (select replace(n.notes, ',', '')::float as notes,sum(n.note_qty) from sales_denomination d,sales_denomination_note_line n
                where d.id = n.denomination_note_ids and d.sale_team_id=%s and d.user_id=%s and date::date >=%s and date::date<=%s
                group by n.notes )A
                order by notes desc
                """, (team_id,user_id, frm_date, to_date,))
            else:
                print 'date>>', frm_date
                cr.execute(""" select * from
                (select replace(n.notes, ',', '')::float as notes,sum(n.note_qty) from sales_denomination d,sales_denomination_note_line n
                where d.id = n.denomination_note_ids and d.sale_team_id=%s and d.user_id=%s and date::date=%s 
                group by n.notes )A
                order by notes desc
                """, (team_id,user_id, frm_date,))
            vals = cr.fetchall()           
        notes = [{'notes':10000, 'note_qty':False}, {'notes':5000, 'note_qty':False}, {'notes':1000, 'note_qty':False}, {'notes':500, 'note_qty':False}, {'notes':100, 'note_qty':False}, {'notes':50, 'note_qty':False}, {'notes':10, 'note_qty':False}]
        for val in vals:
            print ':val[1]>>', val
            data_id = {'notes':val[0],
                    'note_qty': val[1],
                    #'denomination_id':val[2],
                    'cashier_id':ids[0],
                    }
            print 'data_id>>>deno', data_id
            inv_id = invoice_line_obj.create(cr, uid, data_id, context=context)
            for details in self.browse(cr, uid, ids, context=context):
                
                result[details.id] = inv_id
            self._amount_denomination_all(cr, uid, ids, ['denomination_sub_total'], None, context)
        return result
    
    def generate_denomination_product(self, cr, uid, ids, context=None):
        print 'generte_deno_pr'
        cr.execute("""delete from cashier_denomination_product_line where cashier_id=%s""", (ids[0],))
        result = {}
        invoice_line_data = []
        cashier_approval_obj = self.pool.get('cashier.approval')
        invoice_line_obj = self.pool.get('cashier.denomination.product.line') 
        datas = cashier_approval_obj.read(cr, uid, ids, ['date', 'to_date', 'user_id', 'sale_team_id'], context=None)
        print 'datas>>>generte_deno_pr', datas,
        frm_date = to_date = user_id = None            
        if datas:
            for data in datas:
                frm_date = data['date']
                to_date = data['to_date']
                user_id = data['user_id'][0]
                team_id = data['sale_team_id'][0]
            if to_date:
                print 'to_date>>', to_date
                cr.execute("""select n.product_id,sum(n.product_uom_qty),sum(n.product_uom_qty*n.amount) from sales_denomination d,sales_denomination_product_line n
                where d.id = n.denomination_product_ids and d.sale_team_id=%s and d.user_id=%s and date::date >=%s and date::date<=%s
                group by n.product_id
                """, (team_id,user_id, frm_date, to_date,))
            else:
                print 'date>>', frm_date
                cr.execute("""select n.product_id,sum(n.product_uom_qty),sum(n.product_uom_qty*n.amount) from sales_denomination d,sales_denomination_product_line n
                where d.id = n.denomination_product_ids and d.sale_team_id=%s and d.user_id=%s and date::date =%s 
                group by n.product_id
                """, (team_id,user_id, frm_date,))
            vals = cr.fetchall()           
        
        for val in vals:
            print ':val[1]>>', val
            data_id = {'product_id':val[0],
                    'product_uom_qty': val[1],
                    'amount': val[2],
                    'cashier_id':ids[0],
                    }
            print 'data_id>>>deno', data_id
            inv_id = invoice_line_obj.create(cr, uid, data_id, context=context)
            for details in self.browse(cr, uid, ids, context=context):
                
                result[details.id] = inv_id
            
        return result

    def generate_payment_ar(self, cr, uid, ids, context=None):
        payment_line_obj = self.pool.get('cashier.customer.payment') 
        result = {}
        cashier_approval_obj = self.pool.get('cashier.approval')
        datas = cashier_approval_obj.read(cr, uid, ids, ['date', 'to_date', 'user_id', 'sale_team_id'], context=None)
        frm_date = to_date = None
        if datas:
            for data in datas:
                frm_date = data['date']
                to_date = data['to_date']
                user_id = data['user_id'][0]
                team_id = data['sale_team_id'][0]            
            if to_date:
                cr.execute("select a.journal_id,a.amount,a.notes,a.date,m.partner_id,ai.period_id,ai.id from mobile_ar_collection m,ar_payment a ,account_invoice ai where m.id=a.collection_id and ai.number=m.ref_no and m.state='draft' and a.date between %s and %s",(frm_date,to_date,))
            else:
                cr.execute("select a.journal_id,a.amount,a.notes,a.date,m.partner_id,ai.period_id,ai.id from mobile_ar_collection m,ar_payment a ,account_invoice ai where m.id=a.collection_id and ai.number=m.ref_no and m.state='draft'  and a.date =%s ",(frm_date,))
            pament_data=cr.fetchall()
            for payment  in pament_data:
                cr.execute('select default_credit_account_id,type from account_journal where id=%s', (payment[0],))
                data = cr.fetchall()
                if data:
                        default_credit_account_id = data[0][0]
                        type = data[0][1]

                payment_data = {'journal_id':payment[0],
                                'amount': payment[1],
                                'type':type,
                                'cashier_id':ids[0],
                                'partner_id': payment[4],
                                'date_invoice': payment[3],
                                'period_id': payment[5],
                                'account_id': default_credit_account_id,                    
                                'notes':payment[2],
                                'invoice_id':payment[6],
                                'pre_so': 't',
                        }

                inv_id=payment_line_obj.create(cr, uid, payment_data, context=context)
                for details in self.browse(cr, uid, ids, context=context):
                    result[details.id] = inv_id                
        return result
        
    def generate_payment(self, cr, uid, ids, context=None):
        print 'generte_deno'
        cr.execute("""delete from cashier_customer_payment where cashier_id=%s""", (ids[0],))
        result = {}
        invoice_line_data = []
        cashier_approval_obj = self.pool.get('cashier.approval')
        invoice_line_obj = self.pool.get('cashier.customer.payment') 
        datas = cashier_approval_obj.read(cr, uid, ids, ['date', 'to_date', 'user_id', 'sale_team_id'], context=None)
        print 'datas>>>generte_cr', datas,
        frm_date = to_date = user_id = None            
        if datas:
            for data in datas:
                frm_date = data['date']
                to_date = data['to_date']
                user_id = data['user_id'][0]
                team_id = data['sale_team_id'][0]
            if to_date:
                print 'to_date>>', to_date
                cr.execute("""select c.journal_id,c.amount,m.type,s.partner_id,c.date,a.period_id,a.account_id,c.notes,a.id,c.id from sale_order s,account_invoice a ,mobile_sale_order m,customer_payment c
                where s.name=a.reference and m.name=s.tb_ref_no and m.id=c.payment_id and s.payment_type='cash' and a.state='open'  --and a.state='paid' 
                and a.date_invoice >= %s and a.date_invoice <= %s and a.user_id=%s and c.payment_id is not null --and c.id not in(select customer_payment_id from cashier_customer_payment)
                """, (frm_date, to_date, user_id,))
            else:
                print 'date>>', frm_date
                cr.execute("""select c.journal_id,c.amount,m.type,s.partner_id,c.date,a.period_id,a.account_id,c.notes,a.id,c.id from sale_order s,account_invoice a ,mobile_sale_order m,customer_payment c
                where s.name=a.reference and m.name=s.tb_ref_no and m.id=c.payment_id and s.payment_type='cash' and a.state='open' --and a.state='paid' 
                and a.date_invoice = %s and a.user_id=%s and c.payment_id is not null --and c.id not in(select customer_payment_id from cashier_customer_payment)
                """, (frm_date,user_id,))
            vals = cr.fetchall()           
        
        for val in vals:
            print ':val[1]>>', val
            cr.execute('select default_credit_account_id from account_journal where id=%s', (val[0],))
            data = cr.fetchall()
            if data:
                    default_credit_account_id = data[0][0]
            data_id = {'journal_id':val[0],
                    'amount': val[1],
                    #'denomination_id':val[2],
                    'type':val[2],
                    'cashier_id':ids[0],
                    'partner_id': val[3],
                    'date_invoice': val[4],
                    'period_id': val[5],
                    'account_id': default_credit_account_id,                    
                    'notes':val[7],
                    'invoice_id':val[8],
                    'customer_payment_id':val[9],
                    'pre_so': 't',
                    }
            print 'data_id>>>deno', data_id
            inv_id = invoice_line_obj.create(cr, uid, data_id, context=context)
            for details in self.browse(cr, uid, ids, context=context):
                
                result[details.id] = inv_id
            #self._amount_denomination_all(cr, uid, ids, ['denomination_sub_total'], None, context)
        return result
    
    def generate_payment_pre_so(self, cr, uid, ids, context=None):
        print 'generte_pre_so'
        #cr.execute("""delete from cashier_customer_payment where cashier_id=%s""", (ids[0],))
        result = {}
        invoice_line_data = []
        cashier_approval_obj = self.pool.get('cashier.approval')
        invoice_line_obj = self.pool.get('cashier.customer.payment') 
        datas = cashier_approval_obj.read(cr, uid, ids, ['date', 'to_date', 'user_id', 'sale_team_id'], context=None)
        print 'datas>>>generte_pre_so', datas,
        frm_date = to_date = user_id = None            
        if datas:
            print 'datas',datas
            for data in datas:
                frm_date = data['date']
                to_date = data['to_date']
                user_id = data['user_id'][0]
                team_id = data['sale_team_id'][0]
            print 'to_dateto_dateto_date',to_date
                
            if to_date:
                print 'to_date>>', to_date
                cr.execute("""select c.journal_id,c.amount,m.type,s.partner_id,c.date,a.period_id,a.account_id,c.notes,a.id,c.id from sale_order s,account_invoice a ,pre_sale_order m,customer_payment c,account_journal aj
                where s.name=a.reference and m.name=s.tb_ref_no and m.id=c.pre_order_id  and c.journal_id = aj.id and s.payment_type='cash' and a.state='open' --and a.state='paid' 
                and a.date_invoice >= %s and a.date_invoice <= %s and a.user_id=%s and c.pre_order_id is not null 
                --and c.id not in(select customer_payment_id from cashier_customer_payment)
                """, (frm_date, to_date,user_id, ))
            else:
                print 'date>>', frm_date
                cr.execute("""select c.journal_id,c.amount,m.type,s.partner_id,c.date,a.period_id,a.account_id,c.notes,a.id,c.id from sale_order s,account_invoice a ,pre_sale_order m,customer_payment c
                where s.name=a.reference and m.name=s.tb_ref_no and m.id=c.pre_order_id and s.payment_type='cash' and a.state='open' --and a.state='paid' 
                and a.date_invoice = %s and a.user_id=%s and c.pre_order_id is not null --and c.id not in(select customer_payment_id from cashier_customer_payment)
                """, (frm_date,user_id,))
            vals = cr.fetchall()           
        
        for val in vals:
            cr.execute('select default_credit_account_id from account_journal where id=%s', (val[0],))
            data = cr.fetchall()
            if data:
                default_credit_account_id = data[0][0]            
            print ':val[1]>>', val
            data_id = {'journal_id':val[0],
                    'amount': val[1],
                    'type':val[2],
                    'cashier_id':ids[0],
                    'partner_id': val[3],
                    'date_invoice': val[4],
                    'period_id': val[5],
                    'account_id': default_credit_account_id,                    
                    'notes':val[7],
                    'invoice_id':val[8],
                    'customer_payment_id':val[9],
                    'pre_so': 't',
                    }
            print 'data_id>>>pre', data_id
            inv_id = invoice_line_obj.create(cr, uid, data_id, context=context)
            for details in self.browse(cr, uid, ids, context=context):
                
                result[details.id] = inv_id
            #self._amount_denomination_all(cr, uid, ids, ['denomination_sub_total'], None, context)
        return result
    
    def create(self, cr, uid, vals, context=None):
        print 'vals>>>create', vals
        new_id = super(cashier_approval, self).create(cr, uid, vals, context=context)
        return new_id
    # {'cashier_line': {'date': '2016-06-23', 'invoice_id': 8, 'amount': 2310.0, 'partner_id': 19, 'payment_type':'Bank'}}  
        # return {'value': {'cashier_line': [{'date': '2016-06-23', 'invoice_id': 8, 'amount': 2310.0, 'partner_id': 19}, {'date': '2016-06-24', 'invoice_id': 14, 'amount': 2912.0, 'partner_id': 122}, {'date': '2016-06-27', 'invoice_id': 62, 'amount': 10070.0, 'partner_id': 87}, {'date': '2016-06-27', 'invoice_id': 63, 'amount': 10070.0, 'partner_id': 49}]}}
cashier_approval()

class cashier_approval_invoice_line(osv.osv):
    _name = "cashier.approval.invoice.line"
    _description = "Cashier Approval Invoice Line"
    _columns = {
        'cashier_id': fields.many2one('cashier.approval', 'Cashier Approval', required=True),
        'invoice_id':fields.many2one('account.invoice', 'Invoice No', ondelete='cascade'),
        # 'invoice_id':fields.one2many('account.invoice', 'id', 'Invoice No'),
        'date':fields.date('Date'),
        # 'partner_id':fields.one2many('res.partner','id','Customer'),        
        'partner_id':fields.many2one('res.partner', 'Customer', ondelete='cascade'),
        'payment_type': fields.text('Type'),
        'amount':fields.float('Amount'),
    }
    
    
        
cashier_approval_invoice_line()

class cashier_approval_ar_line(osv.osv):
    _name = "cashier.approval.ar.line"
    _description = "Cashier Approval AR Line"
    _columns = {
        'cashier_id': fields.many2one('cashier.approval', 'Cashier Approval', required=True),
        'invoice_id':fields.char("Invoice No"),  # fields.many2one('account.invoice', 'Invoice No',ondelete='cascade'),
        # 'invoice_id':fields.one2many('account.invoice', 'id', 'Invoice No'),
        'date':fields.date('Date'),
        # 'partner_id':fields.one2many('res.partner','id','Customer'),        
        'partner_id':fields.many2one('res.partner', 'Customer', ondelete='cascade'),
        'payment_type': fields.text('Type'),
        'amount':fields.float('Amount'),
    }
    
    
        
cashier_approval_ar_line()

class cashier_approval_credit_line(osv.osv):
    _name = "cashier.approval.credit.line"
    _description = "Cashier Approval Credit Line"
    _columns = {
        'cashier_id': fields.many2one('cashier.approval', 'Cashier Approval', required=True),
        # 'invoice_id':fields.many2one('account.invoice', 'Invoice No',ondelete='cascade'),
        'invoice_id':fields.char('Invoice No'),
        # 'invoice_id':fields.one2many('account.invoice', 'id', 'Invoice No'),
        'credit_id':fields.many2one('account.creditnote', 'Credit Note', ondelete='cascade'),
        'date':fields.date('Date'),
        # 'partner_id':fields.one2many('res.partner','id','Customer'),        
        'partner_id':fields.many2one('res.partner', 'Customer', ondelete='cascade'),
        'account_id':fields.many2one('account.account', 'Account', ondelete='cascade'),
        'journal_id':fields.many2one('account.journal', 'Journal', ondelete='cascade'),
        'amount':fields.float('Amount'),
    }       
        
cashier_approval_credit_line()    

class cashier_denomination_line(osv.osv):
    _name = 'cashier.denomination.line'
    _columns = {              
              'cashier_id':fields.many2one('cashier.approval', 'Cashier Approval', required=True),
              #'notes':fields.char('Notes', required=True),
              'notes':fields.float('Notes', required=True),
              'note_qty':fields.integer('Qty', required=True),
              #'denomination_id': fields.many2one('sales.denomination','Sale Denomination'),
              }
cashier_denomination_line() 

class cashier_denomination_product_line(osv.osv):
    _name = 'cashier.denomination.product.line'
    _columns = {              
              'cashier_id':fields.many2one('cashier.approval', 'Cashier Approval', required=True),
              #'notes':fields.char('Notes', required=True),
              'product_id':fields.many2one('product.product', 'Product', required=True),
              'product_uom_qty':fields.integer('Quantity', required=True),
              'amount':fields.float('Amount',required=True),   
              }
cashier_denomination_product_line() 

class cashier_customer_payment(osv.osv):
    _name = "cashier.customer.payment"
    _columns = {
     'cashier_id':fields.many2one('cashier.approval', 'Cashier Approval', required=True),           
     'type':fields.selection([
                ('cash', 'Cash'),
                ('bank', 'Bank'),
#                 ('advanced', 'Advanced')
            ], 'Payment Type'),
                
   #'payment_id':fields.many2one('mobile.sale.order', 'Line'),
 'journal_id'  : fields.many2one('account.journal', 'Journal' ,domain=[('type','in',('cash','bank'))]),      
 'amount':fields.float('Amount'),
 'partner_id':fields.many2one('res.partner', 'Customer'),
 'period_id': fields.many2one('account.period', 'Period'), 
 'account_id': fields.many2one('account.account', 'Account'),
 'date_invoice': fields.date('Date'),
 'notes':fields.char('Payment Ref'),
 'invoice_id': fields.integer("Invoice ID"),
 'customer_payment_id': fields.integer("Customer Payment ID"),
 'pre_so': fields.boolean('Pre So'),
        }      
