from openerp.osv import fields, osv
from openerp.osv import orm
from openerp import _
from datetime import datetime
import ast
import time
import openerp.addons.decimal_precision as dp
import webbrowser
import subprocess

class purchase_payment_approval(osv.osv):
    
    _name = "purchase.payment.approval"
    _description = "Purchase Payment Approval"

    def create(self, cursor, user, vals, context=None):
        approval_no = self.pool.get('ir.sequence').get(cursor, user,
            'purchase.payment.approval') or '/'
        vals['name'] = approval_no
        return super(purchase_payment_approval, self).create(cursor, user, vals, context=context)

    def _amount_cash(self, cr, uid, ids, field_name, arg, context=None):
        """ Wrapper because of direct method passing as parameter for function fields"""
        return self._amount_all(cr, uid, ids, field_name, arg, context=context)

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'cash_sub_total': 0.0,
            }
            val = val1 = 0.0
            for line in order.invoice_line:
                if line.selected == True:
                    val1 += line.amount
            res[order.id]['cash_sub_total'] = round(val1)
        return res

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('payment.approval.invoice.line').browse(cr, uid, ids, context=context):
            result[line.approval_id.id] = True
        return result.keys()

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
            cr.execute("""update purchase_payment_approval set denomination_sub_total=%s where id=%s  """, (val1, ids[0],))
            res[order.id]['denomination_sub_total'] = round(val1)  # cur_obj.round(cr, uid, cur, val1)
        return res

    def _get_denomination(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('payment.denomination.line').browse(cr, uid, ids, context=context):
            result[line.approval_id.id] = True
        return result.keys()

    _columns = {
            'name': fields.char('Txn', size=64, readonly=True),
            'date':fields.date('From Date'),
            'to_date':fields.date('To Date'),
            'partner_id': fields.many2one('res.partner', 'Supplier', required=True),
            'invoice_line': fields.one2many('payment.approval.invoice.line', 'approval_id', 'Purchase Payment Approval Form', copy=True),
            'denomination_line': fields.one2many('payment.denomination.line', 'approval_id', 'Purchase Approval Form', copy=True),
            'payment_line': fields.one2many('purchase.supplier.payment', 'approval_id', 'Purchase Approval Form', copy=True),
            'cash_sub_total': fields.function(_amount_cash, digits_compute=dp.get_precision('Account'), string='SubTotal',
                                          store={
                                              'purchase.payment.approval': (
                                              lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 10),
                                              'payment.approval.invoice.line': (_get_order, ['amount'], 10),
                                          },
                                          multi='sums', help="The cash total amount."),
            'denomination_sub_total': fields.function(_amount_denomination, digits_compute=dp.get_precision('Account'),
                                                  string='SubTotal',
                                                  store={
                                                      'purchase.payment.approval': (
                                                      lambda self, cr, uid, ids, c={}: ids, ['denomination_line'], 10),
                                                      'payment.denomination.line': (_get_denomination, ['amount'], 10),
                                                  },
                                                  multi='sums', help="The credit total amount."),
            'state':fields.selection([('draft', 'Draft'), ('pending', 'Confirmed'), ('done', 'Done')], 'Status'),
        'confirm_by':fields.many2one('res.users', 'Confirm By'),
        'approve_by':fields.many2one('res.users', 'Approve By'),
        'confirm_date':fields.datetime('Confirm Date'),
        'approve_date':fields.datetime('Approve Date'),
   
    }

    _order = 'id desc'
    _defaults = {
        'date': fields.datetime.now,
        'to_date' : fields.datetime.now,
        'state' : 'draft',
    }
    
    def unlink(self, cr, uid, ids, context=None):
        for data in self.browse(cr, uid, ids, context=context):
            if data.state not in ('draft', 'pending'):
                raise osv.except_osv(
                    _('Warning!'),
                    _('You cannot delete purchase payment approval record which is not draft or pending')
                )                
            elif data.state in ('pending'):
                raise osv.except_osv(
                    _('Warning!'),
                    _('You cannot delete purchase payment approval record which is not draft.You should set to draft it instead.')
                )                     
        return super(purchase_payment_approval, self).unlink(cr, uid, ids, context=context)

    def button_dummy(self, cr, uid, ids, context=None):
        self._amount_all(cr, uid, ids, ['cash_sub_total'], None, context)
        self._amount_denomination_all(cr, uid, ids, ['denomination_sub_total'], None, context)

        return True    
        
    def confirm_(self, cr, uid, ids, context=None):
        import datetime
        invoiceObj = self.pool.get('account.invoice')
        datas = self.read(cr, uid, ids, ['date', 'to_date', 'user_id', 'sale_team_id'], context=None)
        if datas:       
            cr.execute("select selected,invoice_id from payment_approval_invoice_line where approval_id=%s", (ids[0],))    
            invoice_data = cr.fetchall()
            for data in invoice_data:
                select = data[0]     
                invoice_id = data[1]
                cr.execute("update purchase_supplier_payment set selected=%s where invoice_id=%s and approval_id=%s ", (select, invoice_id, ids[0],))
                if select == False: 
                    cr.execute("update account_invoice set unselected=True where id=%s", (invoice_id,))         
            cr.execute("select id from purchase_supplier_payment where selected=True and approval_id=%s", (ids[0],)) 
            selected_data = cr.fetchone()
            if not selected_data:
                raise osv.except_osv(_('Warning'),
                                     _('Please Select At Lease One Record.'))      
        self.button_dummy(cr, uid, ids, context=context)                
        self.write(cr, uid, ids, {'state':'pending', 'confirm_by':uid,'confirm_date':datetime.datetime.now()}, context=context)
        return True   


    def cashier_approve(self, cr, uid, ids, context=None):
        import datetime
        invoiceObj = self.pool.get('account.invoice')
        datas = self.read(cr, uid, ids, ['date', 'to_date', 'partner_id'], context=None)
        if datas:       
            cr.execute("select selected,invoice_id from payment_approval_invoice_line where approval_id=%s", (ids[0],))    
            invoice_data = cr.fetchall()
            for data in invoice_data:
                select = data[0]     
                invoice_id = data[1]
                cr.execute("update purchase_supplier_payment set selected=%s where invoice_id=%s and approval_id=%s ", (select, invoice_id, ids[0],))
                if select == False: 
                    cr.execute("update account_invoice set unselected=True where id=%s", (invoice_id,))         
            cr.execute("select id from purchase_supplier_payment where selected=True and approval_id=%s", (ids[0],)) 
            selected_data = cr.fetchone()
            if not selected_data:
                raise osv.except_osv(_('Warning'),
                                     _('Please Select At Lease One Record.'))   
            self.create_journal_ms(cr, uid, ids, context)
        self.write(cr, uid, ids, {'state':'done', 'approve_by':uid,'approve_date':datetime.datetime.now()}, context=context)
        return True 
    
    
    def create_journal_ms(self, cr, uid, ids, context=None):
        invoiceObj = self.pool.get('account.invoice')
        voucherObj = self.pool.get('account.voucher')
        voucherLineObj = self.pool.get('account.voucher.line')
        last_amount = 0
        journalObj = self.pool.get('account.journal')
        noteObj = self.pool.get('account.creditnote')

        cr.execute("""select journal_id,amount,date_invoice,notes,invoice_id from purchase_supplier_payment where approval_id=%s  and selected=True""", (ids[0],)) 
        payment_data = cr.fetchall()
        if payment_data:
            for payment in payment_data:
                inv_id = []
                inv_id.append(payment[4])
                invoice = invoiceObj.browse(cr, uid, inv_id, context=context)
                partner_id = invoice.partner_id.id
                period_id = invoice.period_id.id
                invoice_num = invoice.number
                
                cr.execute('select default_credit_account_id,type from account_journal where id=%s', (payment[0],))
                data = cr.fetchall()
                if data:
                        default_credit_account_id = data[0][0]

                accountVResult = {
                                        'partner_id':partner_id,
                                        'amount':payment[1],
                                        'journal_id':payment[0],  # acc_data[0],
                                        'date':payment[2],
                                        'period_id':period_id,
                                        'account_id':default_credit_account_id,
                                        'pay_now':'pay_now',
                                        'pre_line':True,
                                        'type':'payment',
                                        'reference':invoice_num,
                                         'payment_option': "without_writeoff",
                                         'company_id':invoice.company_id.id,
                                         'name':payment[3]

                                        }
                    # create register payment voucher
                voucherId = voucherObj.create(cr, uid, accountVResult, context=context)                
                if voucherId:
                    vlist = []
                    vlist.append(voucherId)

                    cr.execute ("select account_id,credit+debit as amount_total,id,reconcile_partial_id  from  account_move_line where move_id=%s  and reconcile_id is null  and credit >0 order by credit+debit", (invoice.move_id.id,)) 
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
                                                'partner_id' : partner_id,
                                                "amount" :payment[1],
                                                "amount_original": invoice.amount_total,
                                                'type': 'dr',
                                            }
                                voucherLineObj.create(cr, uid, line_data, context=context)  
                            else:
                                    line_data = {
                                                # 'name': invoice.number,
                                                'voucher_id' : voucherId,
                                                'move_line_id' :line[2],
                                                'account_id' : line[0],  # invoice.move_id.line_id[0].account_id.id,
                                                'partner_id' : partner_id,
                                                "amount" : line[1],
                                                "amount_original": invoice.amount_total,
                                                'type': 'dr',
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
                                                'partner_id' : partner_id,
                                                "amount" : last_amount,
                                                "amount_original": invoice.amount_total,
                                                'type': 'dr',
                                            }        
                                last_amount = payment[1] - line[1]
                                voucherLineObj.create(cr, uid, line_data, context=context)  
                            else:
                                line_data = {
                                                'voucher_id' : voucherId,
                                                'move_line_id' :line[2],
                                                'account_id' : line[0],  # invoice.move_id.line_id[0].account_id.id,
                                                'partner_id' : partner_id,
                                                "amount" : payment[1],
                                                "amount_original": invoice.amount_total,
                                                'type': 'dr',
                                            }        
                                voucherLineObj.create(cr, uid, line_data, context=context)                  
                voucherObj.button_proforma_voucher(cr, uid, vlist , context=context)
                cr.execute("""update account_invoice set state='paid',unselected=False
                where id=%s and residual=0""", (invoice.id,))

         
    def set_to_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'draft'}, context=context)
        return True 
    
    def retrieve(self, cr, uid, ids, context=None):
        notes_line = [{'notes':10000, 'note_qty':False}, {'notes':5000, 'note_qty':False}, {'notes':1000, 'note_qty':False}, {'notes':500, 'note_qty':False},{'notes':200, 'note_qty':False}, {'notes':100, 'note_qty':False}, {'notes':50, 'note_qty':False},  {'notes':20, 'note_qty':False},{'notes':10, 'note_qty':False}, {'notes':5, 'note_qty':False},{'notes':1, 'note_qty':False}]
        notes_line_obj = self.pool.get('payment.denomination.line')
        cr.execute("""delete from payment_approval_invoice_line where approval_id=%s""", (ids[0],))
        result = {}
        approval_obj = self.pool.get('purchase.payment.approval')
        invoice_line_obj = self.pool.get('payment.approval.invoice.line')
        datas = approval_obj.read(cr, uid, ids, ['date', 'to_date', 'partner_id'], context=None)
        frm_date = to_date = user_id = None

        if datas:
            for data in datas:
                from_date = data['date']
                to_date = data['to_date']
                partner_id = data['partner_id'][0]

            if to_date:
                cr.execute("""select a.id,a.date_invoice,a.date_due,a.partner_id,a.residual 
                            from account_invoice a 
                            where a.state='open'
                            and a.type='in_invoice'
                            and a.date_invoice >= %s and a.date_invoice <= %s and a.partner_id=%s 
                """, (from_date, to_date, partner_id,))
            else:
                cr.execute("""select a.id,a.date_invoice,a.date_due,a.partner_id,a.residual 
                            from account_invoice a 
                            where a.state='open'
                            and a.type='in_invoice'
                            and a.date_invoice=%s and a.partner_id=%s""", (from_date, partner_id,))
            vals = cr.fetchall()
            for val in vals:
                data_id = {'invoice_id': val[0],
                           'date': val[1],
                           'date_due': val[2],
                           'amount': val[4],
                           'approval_id': ids[0],
                           }
                inv_id = invoice_line_obj.create(cr, uid, data_id, context=context)
                for details in self.browse(cr, uid, ids, context=context):
                    result[details.id] = inv_id
            cr.execute("""select a.id,a.date_invoice,a.date_due,a.partner_id,a.residual 
                        from account_invoice a 
                        where a.state='open' 
                        and a.type='in_invoice'
                        and a.partner_id=%s
                        and unselected=True""",
                       (partner_id,))
            data = cr.fetchall()
            for val_data in data:
                cr.execute("""delete from payment_approval_invoice_line where approval_id=%s and invoice_id=%s""",
                           (ids[0], val_data[0],))
                data_id = {'invoice_id': val_data[0],
                           'date': val_data[1],
                           'date_due': val_data[2],
                           'amount': val_data[4],
                           'approval_id': ids[0],
                           }
                inv_id = invoice_line_obj.create(cr, uid, data_id, context=context)
            self.generate_payment(cr, uid, ids, context=context)
            cr.execute ("delete from payment_denomination_line where approval_id =%s",(ids[0],))
            for ptl in notes_line:
                note_line_res = {                                                            
                  'approval_id':ids[0],
                  'note_qty':0,
                  'notes':ptl['notes'],
                }
                notes_line_obj.create(cr, uid, note_line_res, context=context)            
        return result

    def generate_payment(self, cr, uid, ids, context=None):
        cr.execute("""delete from purchase_supplier_payment where approval_id=%s""", (ids[0],))
        result = {}
        manual_cashier_approval_obj = self.pool.get('purchase.payment.approval')
        payment_line_obj = self.pool.get('purchase.supplier.payment') 
        invoice_data = manual_cashier_approval_obj.browse(cr, uid, ids, context=context)
        
        for invoice_line in invoice_data.invoice_line:
            cr.execute("""select (select id from account_journal where type ='cash' and is_tablet=True limit 1 ) as journal_id,a.residual,a.payment_type,a.partner_id,a.date_invoice,a.period_id,a.account_id,a.number,a.id from account_invoice a 
            where a.id=%s
            """, (invoice_line.invoice_id.id,))
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
                        'approval_id':ids[0],
                        'partner_id': val[3],
                        'date_invoice': invoice_data.to_date,
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
    

class payment_approval_invoice_line(osv.osv):
    _name = "payment.approval.invoice.line"
    _description = "Payment Approval Invoice Line"

    _columns = {
        'approval_id': fields.many2one('purchase.payment.approval', 'Purchase Payment Approval'),
        'invoice_id':fields.many2one('account.invoice', 'Invoice No', ondelete='cascade'),
        'date':fields.date('Date'),
        'date_due': fields.date('Due Date'),
        'amount':fields.float('Amount'),
        'selected':fields.boolean('Selected', default=True),
    }

class payment_denomination_line(osv.osv):
    _name = 'payment.denomination.line'

    _columns = {
              'approval_id':fields.many2one('purchase.payment.approval', 'Purchase Payment Approval'),
              'notes':fields.float('Notes', required=True),
              'note_qty':fields.integer('Qty', required=True),
              }

class purchase_supplier_payment(osv.osv):
    _name = "purchase.supplier.payment"
    _columns = {
        'approval_id': fields.many2one('purchase.payment.approval', 'Purchase Payment Approval'),
        'invoice_id': fields.many2one('account.invoice', 'Invoice'),
        'date_invoice': fields.date('Date'),
        'type': fields.selection([
            ('cash', 'Cash'),
            ('bank', 'Bank'),
            ('cheque', 'Cheque')
        ], 'Payment Type'),
        'journal_id': fields.many2one('account.journal', 'Journal', domain=[('type', 'in', ('cash', 'bank'))]),
        'amount': fields.float('Amount'),
        'selected': fields.boolean('Selected', default=True),
        'notes':fields.char('Payment Ref'),
       
    }

    def onchange_invoice_id(self, cr, uid, ids, invoice_id, context=None):
        values = {}
        if invoice_id:
                invoice = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)
                values = {
                'notes':invoice.number
            }
        return {'value': values}

