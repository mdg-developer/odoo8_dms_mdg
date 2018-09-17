from openerp.osv import fields, osv
from openerp.osv import orm
from openerp import _
from datetime import datetime
import ast
import time
import openerp.addons.decimal_precision as dp
import webbrowser
import subprocess

class manual_cashier_approval(osv.osv):
    
    _name = "manual.cashier.approval"
    _description = "Cashier Approval"

    def create(self, cursor, user, vals, context=None):
        cashier_no = self.pool.get('ir.sequence').get(cursor, user,
            'manual.cashier.approval') or '/'
        vals['name'] = cashier_no
        return super(manual_cashier_approval, self).create(cursor, user, vals, context=context)

    
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
                if line.selected == True:
                    val1 += line.amount
            res[order.id]['cash_sub_total'] = round(val1)
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
                if line.selected == True:
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
                if line.selected == True:
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
            cr.execute("""update manual_cashier_approval set denomination_sub_total=%s,denomaination_total=%s where id=%s  """, (val1,val1, ids[0],))                 
            res[order.id]['denomination_sub_total'] = round(val1)  # cur_obj.round(cr, uid, cur, val1)
        return res
    
    def _amount_total_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {                
                'total': 0.0,
            }
            val = val1 = 0.0 
            val1 += (order.cash_sub_total + order.ar_sub_total) - order.cr_sub_total 
            #cr.execute("""update manual_cashier_approval set total=%s where id=%s""", (val1, ids[0],))       
            res[order.id]['total'] = round(val1)  # cur_obj.round(cr, uid, cur, val1)
        return res     
     
    def _amount_denomination_total(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}

        denomination=self._amount_denomination_all(cr, uid, ids, ['denomination_sub_total'], None, context)
        for k, denomination_sub_total in denomination.iteritems():
            denomination_sub_total=denomination_sub_total['denomination_sub_total']
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {                
                'denomaination_total': 0.0,
            }
            val = val1 = 0.0 
            val1 += order.denomination_sub_total 
            res[order.id]['denomaination_total'] = round(denomination_sub_total)  
        return res     
  
    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('manual.cashier.approval.invoice.line').browse(cr, uid, ids, context=context):
            result[line.cashier_id.id] = True
        return result.keys()
    def button_dummy(self, cr, uid, ids, context=None):
        self._amount_total_all(cr, uid, ids, ['total'], None, context)
        self._amount_denomination_all(cr, uid, ids, ['denomination_sub_total'], None, context)
        self._amount_ar_all(cr, uid, ids, ['ar_sub_total'], None, context)
        self._amount_denomination_total(cr, uid, ids, ['denomaination_total'], None, context)
        self._get_plusorminus_diff_amount(cr, uid, ids, ['sign_diff_amount'], None, context)
        return True    
    
    def _get_ar(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('manual.cashier.approval.ar.line').browse(cr, uid, ids, context=context):
            result[line.cashier_id.id] = True
        return result.keys()
    
    def _get_credit(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('manual.cashier.approval.credit.line').browse(cr, uid, ids, context=context):
            result[line.cashier_id.id] = True
        return result.keys()
    
    def _get_denomination(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('manual.cashier.denomination.line').browse(cr, uid, ids, context=context):
            result[line.cashier_id.id] = True
        return result.keys()
    
    def onchange_sale_team_id(self, cr, uid, ids, section_id, context=None):
        team_obj = self.pool.get('crm.case.section')
        branch_id = False        
        if section_id:
            team_id = team_obj.browse(cr, uid, section_id, context=context)
            branch_id = team_id.branch_id.id         
        return {'value': {'branch_id': branch_id}}     
    
    
    def _get_plusorminus_diff_amount(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}                
             
        val1=0.0
        sign = ""
        denomination_sub_total=self._amount_denomination_all(cr, uid, ids,field_name, None, context)
        total=self._amount_total_all(cr, uid, ids, field_name, None, context)
        denomination=self._amount_denomination_total(cr, uid, ids, field_name, None, context)
        
        for k, denomination_sub_total in denomination_sub_total.iteritems():
            denomination_sub_total=denomination_sub_total['denomination_sub_total']
        for k, total in total.iteritems():
            total=total['total']
        for order in self.browse(cr, uid, ids, context=context):

            val1=total-denomination_sub_total
            cr.execute("""update manual_cashier_approval set diff_amount=%s where id=%s""", (val1, ids[0],))       
            sign = str(val1)
            if val1 > 0:

                sign = "(Deficit) " + str(val1)
            elif val1 < 0:
                val1 = val1 * -1
           
                sign = "(Surplus) " + str(val1)
                                      
            res[order.id]= sign 
        return res  
    
    def _get_diff_amount(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}                
             
        val1=0.0
        sign = ""
        for order in self.browse(cr, uid, ids, context=context):
            val1=order.total-order.denomaination_total
            res[order.id]= val1 
        return res      
        
    _columns = {
        'name': fields.char('Txn', size=64, readonly=True),
        'user_id':fields.many2one('res.users', 'Salesman', required=True),
        'sale_team_id':fields.many2one('crm.case.section', 'Sales Team', required=True),
        'account_id': fields.many2one('account.account', 'Control Account' , required=False),
        'journal_id': fields.many2one('account.journal', 'Journal' , required=False),
      'date':fields.date('Date'),
      'to_date':fields.date('To Date'),
      'cashier_line': fields.one2many('manual.cashier.approval.invoice.line', 'cashier_id', 'Cashier Approval Form', copy=True),
      'ar_line': fields.one2many('manual.cashier.approval.ar.line', 'cashier_id', 'Cashier Approval Form', copy=True),
      'credit_line': fields.one2many('manual.cashier.approval.credit.line', 'cashier_id', 'Cashier Approval Form', copy=True),
      'denomination_line': fields.one2many('manual.cashier.denomination.line', 'cashier_id', 'Cashier Approval Form', copy=True),
      'denomination_product_line': fields.one2many('manual.cashier.denomination.product.line', 'cashier_id', 'Cashier Approval Form', copy=True),
      'cashier_customer_payment_line': fields.one2many('manual.cashier.customer.payment', 'cashier_id', 'Cashier Approval Form', copy=True),
      'cash_sub_total': fields.function(_amount_cash, digits_compute=dp.get_precision('Account'), string='SubTotal',
            store={
                'manual.cashier.approval': (lambda self, cr, uid, ids, c={}: ids, ['cashier_line'], 10),
                'manual.cashier.approval.invoice.line': (_get_order, ['amount'], 10),
            },
            multi='sums', help="The cash total amount."),
      'ar_sub_total': fields.function(_amount_ar, digits_compute=dp.get_precision('Account'), string='SubTotal',
            store={
                'manual.cashier.approval': (lambda self, cr, uid, ids, c={}: ids, ['ar_line'], 10),
                'manual.cashier.approval.ar.line': (_get_ar, ['amount'], 10),
            },
  multi='sums', help="The tax amount."),
      'cr_sub_total': fields.function(_amount_cr, digits_compute=dp.get_precision('Account'), string='SubTotal',
            store={
                'manual.cashier.approval': (lambda self, cr, uid, ids, c={}: ids, ['credit_line'], 10),
                'manual.cashier.approval.credit.line': (_get_credit, ['amount'], 10),
            },
            multi='sums', help="The credit total amount."),
       'denomination_sub_total': fields.function(_amount_denomination, digits_compute=dp.get_precision('Account'), string='SubTotal',
            store={
                'manual.cashier.approval': (lambda self, cr, uid, ids, c={}: ids, ['denomination_line'], 10),
                'manual.cashier.denomination.line': (_get_denomination, ['amount'], 10),
            },
            multi='sums', help="The credit total amount."),
       'total': fields.function(_amount_total_all, digits_compute=dp.get_precision('Account'), string='Total Net',
            multi='sums', help="The credit total amount.", store=False,),
        'state':fields.selection([('draft', 'Draft'), ('pending', 'Confirmed'), ('done', 'Done')], 'Status'),
        'branch_id':fields.many2one('res.branch', 'Branch'),
        'confirm_by':fields.many2one('res.users', 'Confirm By'),
        'approve_by':fields.many2one('res.users', 'Approve By'),
        'confirm_date':fields.datetime('Confirm Date'),
        'approve_date':fields.datetime('Approve Date'), 
       'denomaination_total': fields.function(_amount_denomination_total, digits_compute=dp.get_precision('Account'), string='Denomination Total',
            multi='sums', help="The deno total amount.",store=True),        
    'sign_diff_amount': fields.function(_get_plusorminus_diff_amount, string="Difference Amount", type="char"),
    'diff_amount': fields.function(_get_diff_amount, string="Difference Amount", type="float",store=True),
        }
    
    
    _order = 'id desc'
    _defaults = {
        'date': fields.datetime.now,
        'to_date' : fields.datetime.now,
        'state' : 'draft',
       
    } 
    
    def unlink(self, cr, uid, ids, context=None):
        for cashier in self.browse(cr, uid, ids, context=context):
            if cashier.state not in ('draft', 'pending'):
                raise osv.except_osv(
                    _('Warning!'),
                    _('You cannot delete an cashier approval record  which is not draft or pending')
                )                
            elif cashier.state in ('pending'):
                raise osv.except_osv(
                    _('Warning!'),
                    _('You cannot delete an cashier approval record   which is not draft . You should set to draft  it instead.')
                )                     
        return super(manual_cashier_approval, self).unlink(cr, uid, ids, context=context)
    
    def confirm_(self, cr, uid, ids, context=None):
        import datetime
        invoiceObj = self.pool.get('account.invoice')
        datas = self.read(cr, uid, ids, ['date', 'to_date', 'user_id', 'sale_team_id'], context=None)
        if datas:       
            cr.execute("select selected,invoice_id from manual_cashier_approval_invoice_line where cashier_id=%s", (ids[0],))    
            invoice_data = cr.fetchall()
            for data in invoice_data:
                select = data[0]     
                invoice_id = data[1]
                cr.execute("update manual_cashier_customer_payment set selected=%s where invoice_id=%s and cashier_id=%s ", (select, invoice_id, ids[0],))
                if select == False: 
                    cr.execute("update account_invoice set unselected=True where id=%s", (invoice_id,))         
            cr.execute("select selected,invoice_id from manual_cashier_approval_ar_line where cashier_id=%s", (ids[0],))    
            invoice_data = cr.fetchall()
            for data in invoice_data:
                select = data[0]     
                invoice_id = data[1]
                cr.execute("update manual_cashier_customer_payment set selected=%s where invoice_id=%s and cashier_id=%s", (select, invoice_id, ids[0],))
                if select == False: 
                    invoice = invoiceObj.browse(cr, uid, invoice_id, context=context)
                    number = invoice.number
                    cr.execute("update mobile_ar_collection set unselected=True where ref_no=%s", (number,))         
            cr.execute("select id from manual_cashier_customer_payment where selected=True and cashier_id=%s", (ids[0],)) 
            selected_data = cr.fetchone()
            if not selected_data:
                raise osv.except_osv(_('Warning'),
                                     _('Please Select At Lease One Record.'))      
        self.button_dummy(cr, uid, ids, context=context)                
        self.write(cr, uid, ids, {'state':'pending', 'confirm_by':uid,'confirm_date':datetime.datetime.now()}, context=context)
        return True   
     
    def set_to_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'draft'}, context=context)
        return True 
    def generate_report(self, cr, uid, ids, context=None):
        url = "http://localhost:8080/birt/frameset?__report=daily_sale_report.rptdesign"
        # url = "http://10.0.1.30:8080/birt/frameset?__report=daily_sale_report.rptdesign"
        webbrowser.open(url)        
        # webbrowser.open_new_tab(url,new=2)
    def cashier_approve(self, cr, uid, ids, context=None):
        import datetime
        invoiceObj = self.pool.get('account.invoice')
        datas = self.read(cr, uid, ids, ['date', 'to_date', 'user_id', 'sale_team_id'], context=None)
        if datas:       
            cr.execute("select selected,invoice_id from manual_cashier_approval_invoice_line where cashier_id=%s", (ids[0],))    
            invoice_data = cr.fetchall()
            for data in invoice_data:
                select = data[0]     
                invoice_id = data[1]
                cr.execute("update manual_cashier_customer_payment set selected=%s where invoice_id=%s and cashier_id=%s ", (select, invoice_id, ids[0],))
                if select == False: 
                    cr.execute("update account_invoice set unselected=True where id=%s", (invoice_id,))         
            cr.execute("select selected,invoice_id from manual_cashier_approval_ar_line where cashier_id=%s", (ids[0],))    
            invoice_data = cr.fetchall()
            for data in invoice_data:
                select = data[0]     
                invoice_id = data[1]
                cr.execute("update manual_cashier_customer_payment set selected=%s where invoice_id=%s and cashier_id=%s", (select, invoice_id, ids[0],))
                if select == False: 
                    invoice = invoiceObj.browse(cr, uid, invoice_id, context=context)
                    number = invoice.number
                    cr.execute("update mobile_ar_collection set unselected=True where ref_no=%s", (number,))         
            cr.execute("select id from manual_cashier_customer_payment where selected=True and cashier_id=%s", (ids[0],)) 
            selected_data = cr.fetchone()
            if not selected_data:
                raise osv.except_osv(_('Warning'),
                                     _('Please Select At Lease One Record.'))   
            self.create_journal_ms(cr, uid, ids, context)
            self.create_journal_account_move(cr, uid, ids, context)
        self.write(cr, uid, ids, {'state':'done', 'approve_by':uid,'approve_date':datetime.datetime.now()}, context=context)
        return True   
    
    def create_journal_ms(self, cr, uid, ids, context=None):
        invoiceObj = self.pool.get('account.invoice')
        voucherObj = self.pool.get('account.voucher')
        voucherLineObj = self.pool.get('account.voucher.line')
        payment_line_obj = self.pool.get('manual.cashier.customer.payment')
        last_amount = 0
        cr.execute("""select journal_id,amount,type,partner_id,account_id,date_invoice,period_id,notes,invoice_id from manual_cashier_customer_payment where cashier_id=%s  and selected=True""", (ids[0],)) 
        payment_data = cr.fetchall()
        if payment_data:
            for payment in payment_data:
                inv_id = []
                inv_id.append(payment[8])
                invoice = invoiceObj.browse(cr, uid, inv_id, context=context)
                partner_id = invoice.partner_id.id
                period_id = invoice.period_id.id
                payment_type=invoice.payment_type
                if payment[7] is None:
                    invoice_num = invoice.number
                else:
                    invoice_num = payment[7]
                
                cr.execute('select default_credit_account_id,type from account_journal where id=%s', (payment[0],))
                data = cr.fetchall()
                if data:
                        default_credit_account_id = data[0][0]
                        type = data[0][1]
                  

                # invoiceObj.invoice_pay_customer(cr, uid, inv_id, context=context)
                accountVResult = {
                                        'partner_id':partner_id,
                                        'amount':payment[1],
                                        'journal_id':payment[0],  # acc_data[0],
                                        'date':payment[5],
                                        'period_id':period_id,
                                        'account_id':default_credit_account_id,
                                        'pre_line':True,
                                        'type':'receipt',
                                        'reference':invoice_num,
                                          'payment_option': "without_writeoff",
                                         'company_id':invoice.company_id.id

                                        }
                    # create register payment voucher
                voucherId = voucherObj.create(cr, uid, accountVResult, context=context)                
                if voucherId:
                    vlist = []
                    vlist.append(voucherId)
                    if payment_type !='credit':
                        cr.execute ("select account_id,credit+debit as amount_total,id,reconcile_partial_id  from  account_move_line where move_id=%s and name='/'  and reconcile_id is null  order by credit+debit", (invoice.move_id.id,)) 
                        move_line_data = cr.fetchall()    
                    else:
                        cr.execute ("select account_id,credit+debit as amount_total,id,reconcile_partial_id  from  account_move_line where move_id=%s and name='Clearing'  and reconcile_id is null  order by credit+debit", (invoice.move_id.id,)) 
                        move_line_data = cr.fetchall()    

                    line_total_amount = invoice.residual
                    for line in move_line_data:
                        if line_total_amount == payment[1]:
                            if line[3] is not None:
                                line_data = {
                                                # 'name': invoice.number,
                                                'voucher_id' : voucherId,
                                                'move_line_id' :line[2],
                                                'account_id' : line[0],  # invoice.move_id.line_id[0].account_id.id,
                                                'partner_id' : payment[3],
                                                "amount" :payment[1],
                                                "amount_original": invoice.amount_total,
                                                'type': 'cr',
                                            }
                                voucherLineObj.create(cr, uid, line_data, context=context)  
                            else:
                                    line_data = {
                                                # 'name': invoice.number,
                                                'voucher_id' : voucherId,
                                                'move_line_id' :line[2],
                                                'account_id' : line[0],  # invoice.move_id.line_id[0].account_id.id,
                                                'partner_id' : payment[3],
                                                "amount" : line[1],
                                                "amount_original": invoice.amount_total,
                                                'type': 'cr',
                                            }
                                    voucherLineObj.create(cr, uid, line_data, context=context)  
                        else:
                            if line[1] <= payment[1]:
                                if last_amount == 0:
                                    last_amount = line[1]
                                else:
                                    last_amount = last_amount
                                line_data = {
                                                # 'name': invoice.number,
                                                'voucher_id' : voucherId,
                                                'move_line_id' :line[2],
                                                'account_id' : line[0],  # invoice.move_id.line_id[0].account_id.id,
                                                'partner_id' : payment[3],
                                                "amount" : last_amount,
                                                "amount_original": invoice.amount_total,
                                                'type': 'cr',
                                            }        
                                last_amount = payment[1] - line[1]
                                voucherLineObj.create(cr, uid, line_data, context=context)  
                            else:
                                line_data = {
                                                'voucher_id' : voucherId,
                                                'move_line_id' :line[2],
                                                'account_id' : line[0],  # invoice.move_id.line_id[0].account_id.id,
                                                'partner_id' : payment[3],
                                                "amount" : payment[1],
                                                "amount_original": invoice.amount_total,
                                                'type': 'cr',
                                            }        
                                voucherLineObj.create(cr, uid, line_data, context=context)                  
                voucherObj.button_proforma_voucher(cr, uid, vlist , context=context)
                cr.execute("""update account_invoice set state='paid',unselected=False
                where id=%s and residual=0""", (invoice.id,))
                cr.execute("""update sale_order set invoiced='t' from account_invoice
                where sale_order.name=account_invoice.reference and account_invoice.residual=0 and account_invoice.id=%s""", (invoice.id,))
                cr.execute("update mobile_ar_collection set state='done' ,unselected=False where ref_no=%s", (invoice.number,))




    def create_journal_account_move(self, cr, uid, ids, context=None):      

        move_Obj = self.pool.get('account.move')

        if ids:
            approval_data=self.browse(cr, uid, ids, context=context)
            partner_id=approval_data.sale_team_id.team_partner_id.id
            control_account_id=approval_data.account_id.id
            cash_account_id=approval_data.journal_id.default_credit_account_id.id
            journal_id=approval_data.journal_id.id
            date=approval_data.date
            amount=approval_data.diff_amount
            name=approval_data.name
            branch_id=approval_data.branch_id.id
            company_id=approval_data.create_uid.company_id.id
            
       
                
        if journal_id is not None and amount!=0:
             
            cr.execute("select * from account_period where %s >=date_start and %s <=date_stop",(date,date,))         
            period_id=cr.fetchone()[0]
            account_move = {
                            'journal_id': journal_id,
                            'state': 'draft',
                            'date': date,
                            'amount': amount,
                            'ref': name,
                            'company_id':company_id,
                            'branch_id': branch_id,
                            'period_id':period_id,
                            }
            move_id = move_Obj.create(cr, uid, account_move, context=context)
            #  move_Obj.write(cr, uid,{'partner_id': partner_id,'ref':name},context=context)
            cr.execute("update account_move set partner_id=%s,ref=%s where id=%s",(partner_id,name,move_id,))

            cr_account = dr_account = None                                           
            dr_account = control_account_id
            cr_account = cash_account_id      
            if amount <0 :
                amount=-1*amount;    
                
                cr.execute("""insert into account_move_line (partner_id,name,account_id,date_maturity,move_id,credit,debit,journal_id,date,company_id,period_id) 
                values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s),
                      (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", 
                      (partner_id, name , cr_account, date, move_id, 0.0,amount, journal_id, date,company_id,period_id,
                      partner_id,name, dr_account, date, move_id, amount, 0.0, journal_id, date, company_id,period_id,))
 
            else:

                cr.execute("""insert into account_move_line (partner_id,name,account_id,date_maturity,move_id,credit,debit,journal_id,date,company_id,period_id) 
                values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s),
                      (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", 
                      (partner_id, name , dr_account, date, move_id, 0.0,amount, journal_id, date,company_id,period_id,
                      partner_id,name, cr_account, date, move_id, amount, 0.0, journal_id, date, company_id,period_id,))
 
                         
            cr.execute("""UPDATE account_move as m set state='posted' where m.id=%s                            
                            """,(move_id,))    

    def action_generate(self, cr, uid, ids, context=None):
        cr.execute("""delete from manual_cashier_approval_invoice_line where cashier_id=%s""", (ids[0],))
        result = {}
        invoice_line_data = []
        manual_cashier_approval_obj = self.pool.get('manual.cashier.approval')
        invoice_line_obj = self.pool.get('manual.cashier.approval.invoice.line')
        datas = manual_cashier_approval_obj.read(cr, uid, ids, ['date', 'to_date', 'user_id', 'sale_team_id'], context=None)
        frm_date = to_date = user_id = None
            
        if datas:
            for data in datas:
                frm_date = data['date']
                to_date = data['to_date']
                user_id = data['user_id'][0]
                team_id = data['sale_team_id'][0]
                
            if to_date:
                cr.execute("""select a.id,a.date_invoice,a.partner_id,a.residual from account_invoice a 
                where a.payment_type='cash' and a.state='open' --and a.state='paid' 
                and a.date_invoice >= %s and a.date_invoice <= %s and a.user_id=%s and a.section_id =%s 
                """, (frm_date, to_date, user_id, team_id,))
            else:
                cr.execute("""select a.id,a.date_invoice,a.partner_id,a.residual from account_invoice a 
                where a.payment_type='cash' and a.state='open' --and a.state='paid' 
                and a.date_invoice = %s and a.user_id=%s  and a.section_id =%s """, (frm_date, user_id, team_id,))
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
            cr.execute("""select a.id,a.date_invoice,a.partner_id,a.residual from account_invoice a 
            where a.payment_type='cash' and a.state='open' and a.user_id=%s  and a.section_id =%s and unselected=True""", (user_id, team_id,))
            data = cr.fetchall() 
            for val_data in data:
                cr.execute("""delete from manual_cashier_approval_invoice_line where cashier_id=%s and invoice_id=%s""", (ids[0], val_data[0],))
                data_id = {'invoice_id':val_data[0],
                            'date':val_data[1],
                            'partner_id':val_data[2],
                            'amount':val_data[3],
                            'cashier_id':ids[0],
                            'payment_type':'Cash'}
                inv_id = invoice_line_obj.create(cr, uid, data_id, context=context)
            
            self.generte_ar(cr, uid, ids, context=context)
            self.generte_cr(cr, uid, ids, context=context) 
            self.generate_denomination(cr, uid, ids, context=context)   
          #  self.generate_denomination_product(cr, uid, ids, context=context)
            self.generate_payment(cr, uid, ids, context=context)
#            self.generate_payment_pre_so(cr, uid, ids, context=context)     
            self.generate_payment_ar(cr, uid, ids, context=context)
            
        return result
    
    def generte_ar(self, cr, uid, ids, context=None):
        cr.execute("""delete from manual_cashier_approval_ar_line where cashier_id=%s""", (ids[0],))
        result = {}
        manual_cashier_approval_obj = self.pool.get('manual.cashier.approval')
        invoice_line_obj = self.pool.get('manual.cashier.approval.ar.line')
        datas = manual_cashier_approval_obj.read(cr, uid, ids, ['date', 'to_date', 'user_id', 'sale_team_id'], context=None)
        frm_date = to_date = user_id = None
        if datas:
            for data in datas:
                frm_date = data['date']
                to_date = data['to_date']
                user_id = data['user_id'][0]
                team_id = data['sale_team_id'][0]
            if to_date:
                cr.execute("""select m.date,a.id,m.partner_id,a.residual,a.section_id
                            from account_invoice as a,mobile_ar_collection as m
                            where m.ref_no = a.number and m.state='draft' and 
                            m.user_id=%s and m.sale_team_id=%s and m.date >= %s and m.date <= %s
                """, (user_id, team_id, frm_date, to_date,))
            else:
                cr.execute("""select m.date,a.id,m.partner_id,a.residual,a.section_id
                            from account_invoice as a,mobile_ar_collection as m
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
                            'section_id':val[4],
                            'payment_type':'Credit'}
                inv_id = invoice_line_obj.create(cr, uid, data_id, context=context)
                for details in self.browse(cr, uid, ids, context=context):                
                    result[details.id] = inv_id
            cr.execute("""select m.date,a.id,m.partner_id,a.residual,a.id as invoice_id,a.section_id
                    from account_invoice as a,mobile_ar_collection as m
                    where m.ref_no = a.number and  m.state='draft'  and m.user_id=%s and m.sale_team_id=%s and m.unselected=True
        """, (user_id, team_id,))
            data = cr.fetchall()             
            for val_data in data:
                cr.execute("""delete from manual_cashier_approval_ar_line where cashier_id=%s and invoice_id=%s""", (ids[0], val_data[4],))
                data_id = {'invoice_id':val_data[1],
                            'date':val_data[0],
                            'partner_id':val_data[2],
                            'amount':val_data[3],
                            'cashier_id':ids[0],
                            'section_id':val_data[5],
                            'payment_type':'Credit'}
                inv_id = invoice_line_obj.create(cr, uid, data_id, context=context)                
        return result
    
    def generte_cr(self, cr, uid, ids, context=None):
        cr.execute("""delete from manual_cashier_approval_credit_line where cashier_id=%s""", (ids[0],))
        result = {}
        manual_cashier_approval_obj = self.pool.get('manual.cashier.approval')
        invoice_line_obj = self.pool.get('manual.cashier.approval.credit.line')
        datas = manual_cashier_approval_obj.read(cr, uid, ids, ['date', 'to_date', 'user_id', 'sale_team_id'], context=None)
        frm_date = to_date = user_id = None
            
        if datas:
            for data in datas:
                frm_date = data['date']
                to_date = data['to_date']
                user_id = data['user_id'][0]
                team_id = data['sale_team_id'][0]
            if to_date:
                cr.execute("""select issued_date,so_no,id,amount,customer_id from account_creditnote where m_status='used' and sale_team_id=%s and issued_date >= %s and issued_date <= %s and user_id=%s
                """, (team_id, frm_date, to_date, user_id,))
            else:
                cr.execute("""select issued_date,so_no,id,amount,customer_id from account_creditnote where m_status='used' and sale_team_id=%s and issued_date = %s  and user_id=%s 
                """, (team_id, frm_date, user_id,))
            vals = cr.fetchall()
            for val in vals:
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
        cr.execute("""delete from manual_cashier_denomination_line where cashier_id=%s""", (ids[0],))
        result = {}
        manual_cashier_approval_obj = self.pool.get('manual.cashier.approval')
        invoice_line_obj = self.pool.get('manual.cashier.denomination.line') 
        datas = manual_cashier_approval_obj.read(cr, uid, ids, ['date', 'to_date', 'user_id', 'sale_team_id'], context=None)
        frm_date = to_date = user_id = None            
        if datas:
            for data in datas:
                frm_date = data['date']
                to_date = data['to_date']
                user_id = data['user_id'][0]
                team_id = data['sale_team_id'][0]
            if to_date:
                cr.execute("""select * from 
                (select replace(n.notes, ',', '')::float as notes,sum(n.note_qty) from manual_sales_denomination d,manual_sales_denomination_note_line n
                where d.id = n.denomination_note_ids and d.sale_team_id=%s and d.user_id=%s and date::date >=%s and date::date<=%s
                group by n.notes )A
                order by notes desc
                """, (team_id, user_id, frm_date, to_date,))
            else:
                cr.execute(""" select * from
                (select replace(n.notes, ',', '')::float as notes,sum(n.note_qty) from  manual_sales_denomination d,manual_sales_denomination_note_line n
                where d.id = n.denomination_note_ids and d.sale_team_id=%s and d.user_id=%s and date::date=%s 
                group by n.notes )A
                order by notes desc
                """, (team_id, user_id, frm_date,))
            vals = cr.fetchall()           
        notes = [{'notes':10000, 'note_qty':False}, {'notes':5000, 'note_qty':False}, {'notes':1000, 'note_qty':False}, {'notes':500, 'note_qty':False}, {'notes':100, 'note_qty':False}, {'notes':50, 'note_qty':False}, {'notes':10, 'note_qty':False}]
        for val in vals:
            data_id = {'notes':val[0],
                    'note_qty': val[1],
                    # 'denomination_id':val[2],
                    'cashier_id':ids[0],
                    }
            inv_id = invoice_line_obj.create(cr, uid, data_id, context=context)
            for details in self.browse(cr, uid, ids, context=context):
                
                result[details.id] = inv_id
            self._amount_denomination_all(cr, uid, ids, ['denomination_sub_total'], None, context)
        return result
    
    def generate_denomination_product(self, cr, uid, ids, context=None):
        cr.execute("""delete from cashier_denomination_product_line where cashier_id=%s""", (ids[0],))
        result = {}
        manual_cashier_approval_obj = self.pool.get('manual.cashier.approval')
        invoice_line_obj = self.pool.get('manual.cashier.totalon.product.line') 
        datas = manual_cashier_approval_obj.read(cr, uid, ids, ['date', 'to_date', 'user_id', 'sale_team_id'], context=None)
        frm_date = to_date = user_id = None            
        if datas:
            for data in datas:
                frm_date = data['date']
                to_date = data['to_date']
                user_id = data['user_id'][0]
                team_id = data['sale_team_id'][0]
            if to_date:
                cr.execute("""select n.product_id,sum(n.product_uom_qty),sum(n.product_uom_qty*n.amount) from sales_denomination d,sales_denomination_product_line n
                where d.id = n.denomination_product_ids and d.sale_team_id=%s and d.user_id=%s and date::date >=%s and date::date<=%s
                group by n.product_id
                """, (team_id, user_id, frm_date, to_date,))
            else:
                cr.execute("""select n.product_id,sum(n.product_uom_qty),sum(n.product_uom_qty*n.amount) from sales_denomination d,sales_denomination_product_line n
                where d.id = n.denomination_product_ids and d.sale_team_id=%s and d.user_id=%s and date::date =%s 
                group by n.product_id
                """, (team_id, user_id, frm_date,))
            vals = cr.fetchall()           
        
        for val in vals:
            data_id = {'product_id':val[0],
                    'product_uom_qty': val[1],
                    'amount': val[2],
                    'cashier_id':ids[0],
                    }
            inv_id = invoice_line_obj.create(cr, uid, data_id, context=context)
            for details in self.browse(cr, uid, ids, context=context):
                
                result[details.id] = inv_id
            
        return result

    def generate_payment_ar(self, cr, uid, ids, context=None):
        payment_line_obj = self.pool.get('manual.cashier.customer.payment') 
        result = {}
        manual_cashier_approval_obj = self.pool.get('manual.cashier.approval')
        datas = manual_cashier_approval_obj.read(cr, uid, ids, ['date', 'to_date', 'user_id', 'sale_team_id'], context=None)
        frm_date = to_date = None
        if datas:
            for data in datas:
                frm_date = data['date']
                to_date = data['to_date']
                user_id = data['user_id'][0]
                team_id = data['sale_team_id'][0]            
            if to_date:
                cr.execute("select a.journal_id,a.amount,a.notes,a.date,m.partner_id,ai.period_id,ai.id from mobile_ar_collection m,ar_payment a ,account_invoice ai where m.id=a.collection_id and ai.number=m.ref_no and m.state='draft' and m.sale_team_id=%s and m.user_id=%s and a.date between %s and %s", (team_id, user_id, frm_date, to_date,))
            else:
                cr.execute("select a.journal_id,a.amount,a.notes,a.date,m.partner_id,ai.period_id,ai.id from mobile_ar_collection m,ar_payment a ,account_invoice ai where m.id=a.collection_id and ai.number=m.ref_no and m.state='draft'  and m.sale_team_id=%s and m.user_id=%s and a.date =%s ", (team_id, user_id, frm_date,))
            pament_data = cr.fetchall()
            for payment  in pament_data:
                cr.execute('select default_credit_account_id,type from account_journal where id=%s', (payment[0],))
                data = cr.fetchall()
                if data:
                        default_credit_account_id = data[0][0]
                        type = data[0][1]

                payment_data = {
                                        'journal_id':payment[0],
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

                inv_id = payment_line_obj.create(cr, uid, payment_data, context=context)
                for details in self.browse(cr, uid, ids, context=context):
                    result[details.id] = inv_id
            cr.execute("select a.journal_id,a.amount,a.notes,a.date,m.partner_id,ai.period_id,ai.id from mobile_ar_collection m,ar_payment a ,account_invoice ai where m.id=a.collection_id and ai.number=m.ref_no and m.state='draft'  and m.sale_team_id=%s and m.user_id=%s and m.unselected=True ", (team_id, user_id,))
            data = cr.fetchall()
            for pay_data  in data:
                cr.execute("""delete from manual_cashier_customer_payment where cashier_id=%s and  invoice_id=%s""", (ids[0], pay_data[6],))
                cr.execute('select default_credit_account_id,type from account_journal where id=%s', (pay_data[0],))
                data = cr.fetchall()
                if data:
                        default_credit_account_id = data[0][0]
                        type = data[0][1]

                payment_data = {
                                        'journal_id':pay_data[0],
                                        'amount': pay_data[1],
                                        'type':type,
                                        'cashier_id':ids[0],
                                        'partner_id': pay_data[4],
                                        'date_invoice': pay_data[3],
                                        'period_id': pay_data[5],
                                        'account_id': default_credit_account_id,
                                        'notes':pay_data[2],
                                        'invoice_id':pay_data[6],
                                        'pre_so': 't',
                        }

                inv_id = payment_line_obj.create(cr, uid, payment_data, context=context)                   
        return result
        
    def generate_payment(self, cr, uid, ids, context=None):
        cr.execute("""delete from manual_cashier_customer_payment where cashier_id=%s""", (ids[0],))
        result = {}
        manual_cashier_approval_obj = self.pool.get('manual.cashier.approval')
        payment_line_obj = self.pool.get('manual.cashier.customer.payment') 
        datas = manual_cashier_approval_obj.read(cr, uid, ids, ['date', 'to_date', 'user_id', 'sale_team_id'], context=None)
        frm_date = to_date = user_id = None            
        if datas:
            for data in datas:
                frm_date = data['date']
                to_date = data['to_date']
                user_id = data['user_id'][0]
                team_id = data['sale_team_id'][0]
            invoice_data=manual_cashier_approval_obj.browse(cr, uid, ids, context=context)
            for invoice_line in invoice_data.cashier_line:
                

                cr.execute("""select (select id from account_journal where type ='cash' and is_tablet=True limit 1 ) as journal_id,a.residual,a.payment_type,a.partner_id,a.date_invoice,a.period_id,a.account_id,a.number,a.id from account_invoice a 
                where  a.user_id=%s  and a.section_id=%s   and a.id=%s
                """, ( user_id, team_id,invoice_line.invoice_id.id,))
                vals = cr.fetchall()           
            
                for val in vals:
                    cr.execute('select default_credit_account_id from account_journal where id=%s', (val[0],))
                    data = cr.fetchall()
                    if data:
                            default_credit_account_id = data[0][0]
                    data_id = {'journal_id':val[0],
                            'amount': val[1],
                            # 'denomination_id':val[2],
                            'type':val[2],
                            'cashier_id':ids[0],
                            'partner_id': val[3],
                            'date_invoice': val[4],
                            'period_id': val[5],
                            'account_id': default_credit_account_id,
                            'notes':val[7],
                            'invoice_id':val[8],
                            'customer_payment_id':None,
                            'pre_so': 't',
                            }
                    inv_id = payment_line_obj.create(cr, uid, data_id, context=context)
                    for details in self.browse(cr, uid, ids, context=context):
                        result[details.id] = inv_id   
        return result
    
    def generate_payment_pre_so(self, cr, uid, ids, context=None):
        # cr.execute("""delete from manual_cashier_customer_payment where cashier_id=%s""", (ids[0],))
        result = {}
        invoice_line_data = []
        manual_cashier_approval_obj = self.pool.get('manual.cashier.approval')
        invoice_line_obj = self.pool.get('manual.cashier.customer.payment') 
        datas = manual_cashier_approval_obj.read(cr, uid, ids, ['date', 'to_date', 'user_id', 'sale_team_id'], context=None)
        frm_date = to_date = user_id = None            
        if datas:
            for data in datas:
                frm_date = data['date']
                to_date = data['to_date']
                user_id = data['user_id'][0]
                team_id = data['sale_team_id'][0]
                
            if to_date:
                cr.execute("""select c.journal_id,c.amount,m.type,s.partner_id,c.date,a.period_id,a.account_id,c.notes,a.id,c.id from sale_order s,account_invoice a ,pre_sale_order m,customer_payment c,account_journal aj
                where s.name=a.reference and m.name=s.tb_ref_no and m.id=c.pre_order_id  and c.journal_id = aj.id and s.payment_type='cash' and a.state='open' --and a.state='paid' 
                and a.date_invoice >= %s and a.date_invoice <= %s and a.user_id=%s and a.section_id=%s and c.pre_order_id is not null 
                --and c.id  not in (select customer_payment_id from manual_cashier_customer_payment where customer_payment_id is not null)
                """, (frm_date, to_date, user_id, team_id,))
            else:
                cr.execute("""select c.journal_id,c.amount,m.type,s.partner_id,c.date,a.period_id,a.account_id,c.notes,a.id,c.id from sale_order s,account_invoice a ,pre_sale_order m,customer_payment c
                where s.name=a.reference and m.name=s.tb_ref_no and m.id=c.pre_order_id and s.payment_type='cash' and a.state='open' --and a.state='paid' 
                and a.date_invoice = %s and a.user_id=%s and a.section_id=%s and c.pre_order_id is not null --and c.id  not in (select customer_payment_id from manual_cashier_customer_payment where customer_payment_id is not null)
                """, (frm_date, user_id, team_id,))
            vals = cr.fetchall()           
        
        for val in vals:
            cr.execute('select default_credit_account_id from account_journal where id=%s', (val[0],))
            data = cr.fetchall()
            if data:
                default_credit_account_id = data[0][0]            
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
            inv_id = invoice_line_obj.create(cr, uid, data_id, context=context)
            for details in self.browse(cr, uid, ids, context=context):
                
                result[details.id] = inv_id
        cr.execute("""select c.journal_id,c.amount,m.type,s.partner_id,c.date,a.period_id,a.account_id,c.notes,a.id,c.id from sale_order s,account_invoice a ,pre_sale_order m,customer_payment c
                where s.name=a.reference and m.name=s.tb_ref_no and m.id=c.pre_order_id and s.payment_type='cash' and a.state='open' --and a.state='paid' 
                and a.user_id=%s and a.section_id=%s and c.pre_order_id is not null and a.unselected=True
                """, (user_id, team_id,))
        data = cr.fetchall()           
        
        for data_val in data:
            cr.execute('select default_credit_account_id from account_journal where id=%s', (data_val[0],))
            data = cr.fetchall()
            if data:
                default_credit_account_id = data[0][0]            
            data_id = {'journal_id':data_val[0],
                    'amount': data_val[1],
                    'type':data_val[2],
                    'cashier_id':ids[0],
                    'partner_id': data_val[3],
                    'date_invoice': data_val[4],
                    'period_id': data_val[5],
                    'account_id': default_credit_account_id,
                    'notes':data_val[7],
                    'invoice_id':data_val[8],
                    'customer_payment_id':data_val[9],
                    'pre_so': 't',
                    }
            inv_id = invoice_line_obj.create(cr, uid, data_id, context=context)       
            # self._amount_denomination_all(cr, uid, ids, ['denomination_sub_total'], None, context)
        return result
    
#     def create(self, cr, uid, vals, context=None):
#         new_id = super(manual_cashier_approval, self).create(cr, uid, vals, context=context)
#         return new_id
    # {'cashier_line': {'date': '2016-06-23', 'invoice_id': 8, 'amount': 2310.0, 'partner_id': 19, 'payment_type':'Bank'}}  
        # return {'value': {'cashier_line': [{'date': '2016-06-23', 'invoice_id': 8, 'amount': 2310.0, 'partner_id': 19}, {'date': '2016-06-24', 'invoice_id': 14, 'amount': 2912.0, 'partner_id': 122}, {'date': '2016-06-27', 'invoice_id': 62, 'amount': 10070.0, 'partner_id': 87}, {'date': '2016-06-27', 'invoice_id': 63, 'amount': 10070.0, 'partner_id': 49}]}}
manual_cashier_approval()

class manual_cashier_approval_invoice_line(osv.osv):
    _name = "manual.cashier.approval.invoice.line"
    _description = "Cashier Approval Invoice Line"
    _columns = {
        'cashier_id': fields.many2one('manual.cashier.approval', 'Cashier Approval'),
        'invoice_id':fields.many2one('account.invoice', 'Invoice No', ondelete='cascade'),
        # 'invoice_id':fields.one2many('account.invoice', 'id', 'Invoice No'),
        'date':fields.date('Date'),
        # 'partner_id':fields.one2many('res.partner','id','Customer'),        
        'partner_id':fields.many2one('res.partner', 'Customer', ondelete='cascade'),
        'payment_type': fields.text('Type'),
        'amount':fields.float('Amount'),
        'selected':fields.boolean('Selected' , default=True),

    }
    
    
        
manual_cashier_approval_invoice_line()

class manual_cashier_approval_ar_line(osv.osv):
    _name = "manual.cashier.approval.ar.line"
    _description = "Cashier Approval AR Line"
    _columns = {
        'cashier_id': fields.many2one('manual.cashier.approval', 'Cashier Approval'),
        'invoice_id':fields.many2one('account.invoice', 'Invoice No'),
        # 'invoice_id':fields.one2many('account.invoice', 'id', 'Invoice No'),
        'date':fields.date('Date'),
        # 'partner_id':fields.one2many('res.partner','id','Customer'),        
        'selected':fields.boolean('Selected' , default=True),
        'partner_id':fields.many2one('res.partner', 'Customer'),
        'payment_type': fields.text('Type'),
        'amount':fields.float('Amount'),
        'section_id': fields.many2one('crm.case.section', 'Sales Team'),
    }
    
    
        
manual_cashier_approval_ar_line()

class manual_cashier_approval_credit_line(osv.osv):
    _name = "manual.cashier.approval.credit.line"
    _description = "Cashier Approval Credit Line"
    _columns = {
        'cashier_id': fields.many2one('manual.cashier.approval', 'Cashier Approval'),
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
        'selected':fields.boolean('Selected' , default=True),

    }       
        
manual_cashier_approval_credit_line()    

class manual_cashier_denomination_line(osv.osv):
    _name = 'manual.cashier.denomination.line'
    _columns = {              
              'cashier_id':fields.many2one('manual.cashier.approval', 'Cashier Approval'),
              # 'notes':fields.char('Notes', required=True),
              'notes':fields.float('Notes', required=True),
              'note_qty':fields.integer('Qty', required=True),
              # 'denomination_id': fields.many2one('sales.denomination','Sale Denomination'),
              }
manual_cashier_denomination_line() 

class cashier_denomination_product_line(osv.osv):
    _name = 'manual.cashier.denomination.product.line'
    _columns = {              
              'cashier_id':fields.many2one('manual.cashier.approval', 'Cashier Approval'),
              # 'notes':fields.char('Notes', required=True),
              'product_id':fields.many2one('product.product', 'Product', required=True),
              'product_uom_qty':fields.integer('Quantity', required=True),
              'amount':fields.float('Amount', required=True),
              }
cashier_denomination_product_line() 

class manual_cashier_customer_payment(osv.osv):
    _name = "manual.cashier.customer.payment"
    _columns = {
     'cashier_id':fields.many2one('manual.cashier.approval', 'Cashier Approval'),
     'type':fields.selection([
                ('cash', 'Cash'),
                ('bank', 'Bank'),
                ('cheque', 'Cheque')
            ], 'Payment Type'),
                
   # 'payment_id':fields.many2one('mobile.sale.order', 'Line'),
 'journal_id'  : fields.many2one('account.journal', 'Journal' , domain=[('type', 'in', ('cash', 'bank'))]),
 'amount':fields.float('Amount'),
 'partner_id':fields.many2one('res.partner', 'Customer'),
 'period_id': fields.many2one('account.period', 'Period'),
 'account_id': fields.many2one('account.account', 'Account'),
 'date_invoice': fields.date('Date'),
 'notes':fields.char('Payment Ref'),
 'invoice_id': fields.many2one('account.invoice', 'Invoice ID'),
 'customer_payment_id': fields.integer("Customer Payment ID"),
 'pre_so': fields.boolean('Pre So'),
 'selected':fields.boolean('Selected', default=True),
 'cheque_no': fields.integer("Cheque No"),

        }      
        
    def onchange_invoice_id(self, cr, uid, ids, invoice_id, context=None):
        values = {}
        if invoice_id:
                invoice = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)
                values = {  
                'notes':invoice.number             
            }
        return {'value': values}    
        
manual_cashier_customer_payment()
