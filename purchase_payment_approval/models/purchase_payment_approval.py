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

    def retrieve(self, cr, uid, ids, context=None):
        cr.execute("""delete from payment_approval_invoice_line where approval_id=%s""", (ids[0],))
        result = {}
        invoice_line_data = []
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
                cr.execute("""select a.id,a.date_invoice,a.partner_id,a.residual 
                            from account_invoice a 
                            where a.state='open'
                            and a.type='in_invoice'
                            and a.date_invoice=%s and a.partner_id=%s""", (from_date, partner_id,))
            vals = cr.fetchall()
            for val in vals:
                data_id = {'invoice_id': val[0],
                           'date': val[1],
                           'date_due': val[2],
                           'amount': val[3],
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
                           'amount': val_data[3],
                           'approval_id': ids[0],
                           }
                inv_id = invoice_line_obj.create(cr, uid, data_id, context=context)
            self.generate_payment(cr, uid, ids, context=context)
        return result

    def generate_payment(self, cr, uid, ids, context=None):
        cr.execute("""delete from purchase_supplier_payment where cashier_id=%s""", (ids[0],))
        result = {}
        approval_obj = self.pool.get('cashier.approval')
        invoice_line_obj = self.pool.get('purchase.supplier.payment')
        datas = approval_obj.read(cr, uid, ids, ['date', 'to_date', 'partner_id'], context=None)
        frm_date = to_date = partner_id = None
        if datas:
            for data in datas:
                frm_date = data['date']
                to_date = data['to_date']
                partner_id = data['partner_id'][0]
            if to_date:
                cr.execute("""select c.journal_id,c.amount,m.type,s.partner_id,c.date,a.period_id,a.account_id,c.notes,a.id,c.id,c.cheque_no from sale_order s,account_invoice a ,mobile_sale_order m,customer_payment c
                where s.name=a.reference and m.name=s.tb_ref_no and m.id=c.payment_id and s.payment_type='cash' and a.state='open'  --and a.state='paid' 
                and a.date_invoice >= %s and a.date_invoice <= %s and a.user_id=%s  and a.section_id=%s and c.payment_id is not null --and c.id  not in (select customer_payment_id from cashier_customer_payment where customer_payment_id is not null)
                """, (frm_date, to_date, user_id, team_id,))
            else:
                cr.execute("""select c.journal_id,c.amount,m.type,s.partner_id,c.date,a.period_id,a.account_id,c.notes,a.id,c.id,c.cheque_no from sale_order s,account_invoice a ,mobile_sale_order m,customer_payment c
                where s.name=a.reference and m.name=s.tb_ref_no and m.id=c.payment_id and s.payment_type='cash' and a.state='open' --and a.state='paid' 
                and a.date_invoice = %s and a.user_id=%s  and a.section_id=%s and c.payment_id is not null --and c.id  not in (select customer_payment_id from cashier_customer_payment where customer_payment_id is not null)
                """, (frm_date, user_id, team_id,))
            vals = cr.fetchall()

            for val in vals:
                cr.execute('select default_credit_account_id from account_journal where id=%s', (val[0],))
                data = cr.fetchall()
                if data:
                    default_credit_account_id = data[0][0]
                data_id = {'journal_id': val[0],
                           'amount': val[1],
                           # 'denomination_id':val[2],
                           'type': val[2],
                           'cashier_id': ids[0],
                           'partner_id': val[3],
                           'date_invoice': val[4],
                           'period_id': val[5],
                           'account_id': default_credit_account_id,
                           'notes': val[7],
                           'invoice_id': val[8],
                           'customer_payment_id': val[9],
                           'pre_so': 't',
                           'cheque_no': val[10],
                           }
                inv_id = invoice_line_obj.create(cr, uid, data_id, context=context)
                for details in self.browse(cr, uid, ids, context=context):
                    result[details.id] = inv_id
            cr.execute("""select c.journal_id,c.amount,m.type,s.partner_id,c.date,a.period_id,a.account_id,c.notes,a.id,c.id,c.cheque_no from sale_order s,account_invoice a ,mobile_sale_order m,customer_payment c
                where s.name=a.reference and m.name=s.tb_ref_no and m.id=c.payment_id and s.payment_type='cash' and a.state='open' 
                 and a.user_id=%s and a.section_id=%s  and c.payment_id is not null and a.unselected=True
                """, (user_id, team_id,))
            data = cr.fetchall()
            for val_data in data:
                cr.execute("""delete from cashier_customer_payment where cashier_id=%s and  invoice_id=%s""",
                           (ids[0], val_data[8],))
                cr.execute('select default_credit_account_id from account_journal where id=%s', (val_data[0],))
                data = cr.fetchall()
                if data:
                    default_credit_account_id = data[0][0]
                data_id = {'journal_id': val_data[0],
                           'amount': val_data[1],
                           # 'denomination_id':val[2],
                           'type': val_data[2],
                           'cashier_id': ids[0],
                           'partner_id': val_data[3],
                           'date_invoice': val_data[4],
                           'period_id': val_data[5],
                           'account_id': default_credit_account_id,
                           'notes': val_data[7],
                           'invoice_id': val_data[8],
                           'customer_payment_id': val_data[9],
                           'pre_so': 't',
                           'cheque_no': val_data[10],

                           }
                inv_id = invoice_line_obj.create(cr, uid, data_id, context=context)
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
    }

    def onchange_invoice_id(self, cr, uid, ids, invoice_id, context=None):
        values = {}
        if invoice_id:
                invoice = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)
                values = {
                'notes':invoice.number
            }
        return {'value': values}

