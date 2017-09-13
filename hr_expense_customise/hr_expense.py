import time
from openerp import models, fields, api, _

from openerp import netsvc
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

def _employee_get(obj, cr, uid, context=None):
    if context is None:
        context = {}
    ids = obj.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
    if ids:
        return ids[0]
    return False
class uniform_name(models.Model):
    _name="uniform.name"    
    _columns = {    
    'name' :fields.char("Uniform Name" ,required=True)
    
                }
class hr_ulm_expense(osv.osv):
    _name = "hr.ulm.expense"
    _description = "HR United Living Mall Expense"
    _order = "id desc"
    def _balance_amount(self, cr, uid, ids, field_name, arg, context=None):
        res= {}
        for expense in self.browse(cr, uid, ids, context=context):
            balance = 0.0
            for line in expense.line_ids:
                balance += line.unit_amount * line.unit_quantity
            
            for payment in expense.payments:
                balance -= payment.amount;
            if balance<0:balance=0
            res[expense.id] = balance
        return res 
    
    def _amount(self, cr, uid, vals, field_name, arg, context=None):
        res= {}
        for expense in self.browse(cr, uid, vals, context=context):
            total = 0.0
            for line in expense.line_ids:
                total += line.unit_amount * line.unit_quantity
            res[expense.id] = total
        return res
    
    def _paid_amount(self, cr, uid, vals, field_name, arg, context=None):
        res= {}
        for expense in self.browse(cr, uid, vals, context=context):
            total = 0.0
            for payment in expense.payments:
                total += payment.amount
            res[expense.id] = total
        return res
    
    def _get_currency(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, [uid], context=context)[0]
        return user.company_id.currency_id.id
    
    _columns = {
        'name': fields.char('Description', size=128, required=True,),
        'date': fields.date('Date', select=True,  ),
        'employee_id': fields.many2one('hr.employee', "Employee", required=True),
        'line_ids': fields.one2many('hr.ulm.expense.line', 'expense_id', 'Expense Lines' , states={'draft':[('readonly',False)]}),
        'payments':fields.one2many('hr.ulm.payment', 'expense_id', 'Payment Lines', states={'draft':[('readonly',False)]} ),
        'note': fields.text('Note'),
        'amount': fields.function(_amount, string='Expense Amount', digits_compute=dp.get_precision('Account')),
        'paid_amount':fields.function(_paid_amount, string = 'Paid Amount',digits_compute=dp.get_precision('Account'), store=True,readonly=True),
        'balance': fields.function(_balance_amount, string='Balance', digits_compute=dp.get_precision('Account'), store=True,readonly=True),
        'currency_id': fields.many2one('res.currency', 'Currency', required=True, readonly=True ),
        'department_id':fields.many2one('hr.department','Department'),
        'job_id':fields.many2one('hr.job','Job Position'),

        'company_id': fields.many2one('res.company', 'Company', required=True),
        'user_id': fields.many2one('res.users', 'User', required=True),
        'state': fields.selection([
            ('draft', 'New'),
            ('pending','Pending'),
            ('paid', 'Paid'),
            ], 'Status', readonly=True),
   }
    _defaults = {
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'hr.employee', context=c),
        'date': fields.date.context_today,
        'state': 'draft',
        'employee_id': _employee_get,
        'user_id': lambda cr, uid, id, c={}: id,
        'currency_id': _get_currency,
    }
    
    def make_payment(self, cr, uid, ids, context=None):
        context = context or {}
        print context
        return {'type': 'ir.actions.act_window_close'}
    
    def show_payment_expense_dialog(self, cr, uid, ids, context=None):
        if not ids: return []
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'hr_ulm_expense', 'view_payment_dialog_form')
        expense = self.browse(cr,uid,ids[0], context=context)
        return{
               'name':_("Expense Payment"),
               'view_mode': 'form',
               'view_id':view_id,
               'view_type':'form',
               'res_model':'hr.ulm.expense',
               'type':'ir.actions.act_window',
               'nodestroy':True,
               'target':'new',
               'domain':'[]',
               'context':{
                          'default_name':fields.date.context_today,
                          'default_amount':expense.balance,
                          'default_payment_type':'employee',
                          }
               }
        
    def create(self, cursor, user, ids, context=None):
        ids['state']='pending'
        vals = super(hr_ulm_expense, self).create(cursor, user, ids, context=context)
        return vals
    
    def update_status(self, cursor, user, ids, context=None):
        expenses = self.browse(cursor, user, ids)
        balance=0;
        payment_exist = False
        for expense_line in expenses[0].line_ids:
            balance+=expense_line.unit_amount
        
        for payment in expenses[0].payments:
            balance -= payment.amount
            if(payment.amount>0): payment_exist= True
            
       
        if(payment_exist and balance<=0):
            cursor.execute('update hr_ulm_expense set state=%s where id in %s',('paid',tuple(ids),))
            context.update({'state':'paid'})
        else:
            cursor.execute('update hr_ulm_expense set state=%s where id in %s',('pending',tuple(ids),))
            context.update({'state':'pending'})
       
            
    def write(self, cursor, user, ids,data, context=None):
        vals=super(hr_ulm_expense,self).write(cursor, user, ids, data, context=context)
        self.update_status(cursor, user, ids, context);
        return vals;
    
    def onchange_employee_id(self, cr, uid, ids, employee_id, context=None):
        emp_obj = self.pool.get('hr.employee')
        department_id = False
        company_id = False
        job_id=False
        if employee_id:
            employee = emp_obj.browse(cr, uid, employee_id, context=context)
            department_id = employee.department_id.id
            job_id=employee.job_id.id
            company_id = employee.company_id.id
        return {'value': {'department_id': department_id, 'company_id': company_id,'job_id':job_id}}
     
hr_ulm_expense()


class hr_ulm_expense_line(osv.osv):
    _name = "hr.ulm.expense.line"
    _description = "United Living Mall Expense Line"
    
    def _amount(self, cr, uid, ids, field_name, arg, context=None):
            if not ids:
                return {}
            cr.execute("SELECT l.id,COALESCE(SUM(l.unit_amount*l.unit_quantity),0) AS amount FROM hr_ulm_expense_line l WHERE id IN %s GROUP BY l.id ",(tuple(ids),))
            res = dict(cr.fetchall())
            return res

    _columns = {
        #'name': fields.char('Expense Note', size=128, required=True),
        'name' :fields.many2one('uniform.name', 'Uniform Name',ondelete='cascade', select=True,required=True),
        
        'date_value': fields.date('Date', required=True),
        'expense_id': fields.many2one('hr.ulm.expense', 'Expense', ondelete='cascade', select=True),
        'total_amount': fields.function(_amount, string='Total', digits_compute=dp.get_precision('Account')),
        'unit_amount': fields.float('Unit Price', digits_compute=dp.get_precision('Product Price')),
        'unit_quantity': fields.float('Quantities', digits_compute= dp.get_precision('Product Unit of Measure')),
        'description': fields.text('Description'),
        'ref': fields.char('Times', size=32),
        'sequence': fields.integer('Sequence', select=True, help="Gives the sequence order when displaying a list of expense lines."),
        }
    
    _defaults = {
        'unit_quantity': 1,
        'date_value': lambda *a: time.strftime('%Y-%m-%d'),
    }
        
    _order = "sequence, date_value desc"
    
hr_ulm_expense_line()

class hr_ulm_payment(osv.osv):
    _name="hr.ulm.payment"
    _description="HR United Living Mall Payment"
    _columns ={
        'name': fields.date('Date',required=True, select=True),
        'amount':fields.float('Pay Amount', digits_compute=dp.get_precision('Payment Amount')),
        'expense_id': fields.many2one('hr.ulm.expense', 'Expense', ondelete='cascade', select=True),
        'payment_type': fields.selection([
            ('employee', 'By Employee'),
            ('company', 'By Company'),
            ], 'Payment Type', required=True),
         'is_paid':fields.boolean('Is Paid'),
        }
    
    _defaults = {
       'payment_type':'employee',
       'name': fields.date.context_today,
    }
    
hr_ulm_payment()
