import itertools
from lxml import etree
import time
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp


class account_invoice(models.Model):
    _inherit = "account.invoice"
    
    def cancel_credit(self, cr, uid, ids, context=None):
        invoice_obj = self.pool.get('account.invoice')
        #invoice_obj.action_cancel(cr, uid, ids, context=context)
        #action_invoice_cancel
        invoice = self.browse(cr, uid, ids[0], context=context)
        invoice.signal_workflow('invoice_cancel')
        order_no=invoice.origin
        cr.execute("update sale_order set  credit_to_cash =True where name=%s",(order_no,))
        
        return True            
        
    
    @api.multi
    def action_cancel(self):
        moves = self.env['account.move']
        obj_move_line = self.pool.get('account.move.line')
        move_obj = self.pool.get('account.move')
       
        cr = self._cr
        uid = self._uid
        context=self._context
        unreconcile_id=[]        
        
        for inv in self:
            if inv.move_id:
                if inv.payment_type =='credit':
                    move_data = move_obj.browse(cr, uid,inv.move_id.id,context=context)
                    print 'move_data',move_data
                    
                    for moveline in move_data.line_id:
                        if moveline.name=="/" or moveline.name=='Control':  
                            unreconcile_id.append(moveline.id)          
                    obj_move_line._remove_move_reconcile(cr, uid, unreconcile_id,context=context)
                moves += inv.move_id
            if inv.payment_ids:
                for move_line in inv.payment_ids:
                    if move_line.reconcile_partial_id.line_partial_ids:
                        raise except_orm(_('Error!'), _('You cannot cancel an invoice which is partially paid. You need to unreconcile related payment entries first.'))

        # First, set the invoices as cancelled and detach the move ids
        self.write({'state': 'cancel', 'move_id': False})
        if moves:
            # second, invalidate the move(s)
            moves.button_cancel()
            # delete the move this invoice was pointing to
            # Note that the corresponding move_lines and move_reconciles
            # will be automatically deleted too
            moves.unlink()
        self._log_event(-1.0, 'Cancel Invoice')
        return True
    
    def credit_approve(self, cr, uid, ids, context=None):
        invoice_obj = self.pool.get('account.invoice')
        move_obj =self.pool.get('account.move')
        move_line_obj=self.pool.get('account.move.line')
        period_obj = self.pool.get('account.period')
        date = False
        period_id = False
        journal_id= False
        account_id = False

        if context is None:
            context = {}

        date = time.strftime('%Y-%m-%d')
        period_ids = period_obj.find(cr, uid, dt=date, context=context)
        if period_ids:
            period_id = period_ids[0]            
        line_id=[]

        if ids:
            invoice = self.browse(cr, uid, ids[0], context=context)
            move_id=invoice.move_id.id
            move = move_obj.browse(cr, uid,move_id, context=context)
            for moveline in move.line_id:
                if moveline.name=="/":
                    line_id=[]
                    control_account_id =moveline.account_id.id
                    cr.execute("select property_account_receivable_clearing from product_maingroup where property_account_receivable_control =%s",(control_account_id,) )
                    clearing_account_id=cr.fetchone()[0]
                    line_id.append(moveline.id)
                    vals = {
                                'move_id':move_id,
                                'date_maturity': moveline.date_maturity,
                                'partner_id': moveline.partner_id.id,
                                'name': 'Control',
                                'date': moveline.date,
                                'debit': moveline.credit,
                                'credit': moveline.debit,
                                'account_id': moveline.account_id.id,
                                'analytic_lines': moveline.analytic_lines,
                                'amount_currency': moveline.amount_currency,
                                'currency_id': moveline.currency_id,
                                'tax_code_id': moveline.tax_code_id,
                                'tax_amount': moveline.tax_amount,
                                'ref': moveline.ref,
                                'quantity': moveline.quantity,
                                'product_id': moveline.product_id.id,
                                'product_uom_id': moveline.product_uom_id.id,
                                'analytic_account_id': moveline.analytic_account_id.id,
                            }
                    move_line_id =move_line_obj.create(cr, uid, vals)
                    line_id.append(move_line_id)          
                
                    vals_1 = {
                                'move_id':move_id,
                                'date_maturity': moveline.date_maturity,
                                'partner_id': moveline.partner_id.id,
                                'name': 'Clearing',
                                'date': moveline.date,
                                'debit': moveline.debit,
                                'credit': 0,
                                'account_id': clearing_account_id,
                                'analytic_lines': moveline.analytic_lines,
                                'amount_currency': moveline.amount_currency,
                                'currency_id': moveline.currency_id,
                                'tax_code_id': moveline.tax_code_id,
                                'tax_amount': moveline.tax_amount,
                                'ref': moveline.ref,
                                'quantity': moveline.quantity,
                                'product_id': moveline.product_id.id,
                                'product_uom_id': moveline.product_uom_id.id,
                                'analytic_account_id': moveline.analytic_account_id.id,
                            }
                    move_line_obj.create(cr, uid, vals_1) 
                    move_line_obj.reconcile(cr, uid, line_id, 'manual', account_id,
                                        period_id, journal_id, context=context) 
            self.write(cr, uid, ids, {'state':'open' , 'credit_approve_by':uid,'credit_control':True})   
        return True    
        
    def _compute_payments(self):
        partial_lines = lines = self.env['account.move.line']
        cr = self._cr
        uid = self._uid
        for line in self.move_id.line_id:
            print 'line_compute_payments', line
#             if line.account_id != self.account_id:
#                 continue
            if line.reconcile_id:
                lines |= line.reconcile_id.line_id
            elif line.reconcile_partial_id:
                lines |= line.reconcile_partial_id.line_partial_ids
            partial_lines += line
            print 'self.residualself.residual ', self.residual 
            if self.residual == 0.0:
                print 'self.residualself.residual ----', self.residual 
                self.confirm_paid()
                if self.origin:
                    cr.execute("update sale_order set invoiced=True where name=%s", (self.origin,))        
                    cr.execute("update sale_order set state='done' where shipped=True and invoiced=True and name=%s", (self.origin,)) 
            if self.residual != 0.0:
                if self.origin:
                    if self.payment_type =='credit' and self.type=='out_invoice':
                        print ' self.type',self.type,self.id
                        cr.execute("update account_invoice set state='credit_state' where credit_control !=True and  id=%s", (self.id,)) 
                    else:
                        cr.execute("update account_invoice set state='open' where id=%s", (self.id,)) 
                           
        self.payment_ids = (lines - partial_lines).sorted()
        
    @api.model
    def line_get_convert(self, line, part, date):
        print 'check>>>', line
        if line is not None:
            print 'lineeeeeeeee', line['debit'], line['credit']
            price = line['debit'] + line['credit'],
            origin = line.get('ref', False)
            is_discount = line.get('is_discount', False)
            res_data=[]
            print 'originoriginorigin', origin, is_discount
            if origin:
                self.env.cr.execute("select type,payment_type from account_invoice where origin=%s and state!='cancel' ", (origin,))
                type_data = self.env.cr.fetchone()
                if type_data:
                    type = type_data[0]
                    payment_type=type_data[1]
                else:
                    type = None
                    payment_type=None
            if type == 'in_invoice':
                amount_currency = price > 0 and abs(line.get('amount_currency', False)) or -abs(line.get('amount_currency', False))
                if line['credit'] != 0:
                   if amount_currency > 0:
                      amount_currency = amount_currency * -1 
                return {
                    'date_maturity': line.get('date_maturity', False),
                    'partner_id': part,
                    'name': line['name'][:64],
                    'date': date,
                    'debit': line['debit'],  # line['price']>0 and line['price'],
                    'credit': line['credit'],  # line['price']<0 and -line['price'],
                    'account_id': line['account_id'],
                    # 'account_id': account_id,
                    'analytic_lines': line.get('analytic_lines', []),
                    'amount_currency':amount_currency,
                    #'amount_currency': price > 0 and abs(line.get('amount_currency', False)) or -abs(line.get('amount_currency', False)),
                    'currency_id': line.get('currency_id', False),
                    'tax_code_id': line.get('tax_code_id', False),
                    'tax_amount': line.get('tax_amount', False),
                    'ref': line.get('ref', False),
                    'quantity': line.get('quantity', 1.00),
                    'product_id': line.get('product_id', False),
                    'product_uom_id': line.get('uos_id', False),
                    'analytic_account_id': line.get('account_analytic_id', False),
                }
            elif type == 'in_refund':
                return {
                    'date_maturity': line.get('date_maturity', False),
                    'partner_id': part,
                    'name': line['name'][:64],
                    'date': date,
                    'debit': line['debit'],  # line['price']>0 and line['price'],
                    'credit': line['credit'],  # line['price']<0 and -line['price'],
                    'account_id': line['account_id'],
                    # 'account_id': account_id,
                    'analytic_lines': line.get('analytic_lines', []),
                    'amount_currency': line.get('amount_currency', False),
                    'currency_id': line.get('currency_id', False),
                    'tax_code_id': line.get('tax_code_id', False),
                    'tax_amount': line.get('tax_amount', False),
                    'ref': line.get('ref', False),
                    'quantity': line.get('quantity', 1.00),
                    'product_id': line.get('product_id', False),
                    'product_uom_id': line.get('uos_id', False),
                    'analytic_account_id': line.get('account_analytic_id', False),
                }    
            else:            
                return {
                    'date_maturity': line.get('date_maturity', False),
                    'partner_id': part,
                    'name': line['name'][:64],
                    'date': date,
                    'debit': line['debit'],  # line['price']>0 and line['price'],
                    'credit': line['credit'],  # line['price']<0 and -line['price'],
                    'account_id': line['account_id'],
                    # 'account_id': account_id,
                    'analytic_lines': line.get('analytic_lines', []),
                    'amount_currency': price > 0 and abs(line.get('amount_currency', False)) or -abs(line.get('amount_currency', False)),
                    'currency_id': line.get('currency_id', False),
                    'tax_code_id': line.get('tax_code_id', False),
                    'tax_amount': line.get('tax_amount', False),
                    'ref': line.get('ref', False),
                    'quantity': line.get('quantity', 1.00),
                    'product_id': line.get('product_id', False),
                    'product_uom_id': line.get('uos_id', False),
                    'analytic_account_id': line.get('account_analytic_id', False),
                }
    
    def line_get_convert_new(self, line, part, date):
        account_id = property_account_payable  = property_account_payable_clearing = None
        discount_receivable_acc=None
        cr = self._cr
        type = 'out_invoice' 
        print 'line_get_convert_newline_get_convert_new', line, part
        origin = line.get('ref', False)
        is_discount = line.get('is_discount', False)
        res_data=[]
        for inv in self:
            property_account_payable = inv.partner_id.property_account_payable.id
            property_account_payable_clearing = inv.partner_id.property_account_payable_clearing.id
        print 'originoriginorigin', origin, is_discount
        if origin:
            cr.execute("select type,payment_type from account_invoice where origin=%s and state!='cancel' ", (origin,))
            type_data = cr.fetchone()
            if type_data:
                type = type_data[0]
                payment_type=type_data[1]
            else:
                type = None
                payment_type=None
        print 'typeeeeeeeee', type
        if type == 'out_invoice' :
            if line['price'] < 0:
                product = self.env['product.product'].browse(line.get('product_id', False))
                print 'product>>>', product.id
                print 'line.get>>>', line.get('product_id', False)
                if  line['is_discount'] == True:
                    if payment_type=='credit':
                        account_id = product.product_tmpl_id.categ_id.property_account_discount_credit.id
                    else:
                        account_id = product.product_tmpl_id.categ_id.property_account_discount_cash.id
                    line['price'] = -1 * line['price']
                else:
                    if payment_type=='credit':
                        account_id = product.product_tmpl_id.main_group.property_account_receivable_control.id
                    else:
                        account_id = product.product_tmpl_id.main_group.property_account_receivable.id
                                    # acount_id= product.product_tmpl_id.main_group.property_account_payable.id
                print 'account_id>>>', account_id        
    
                print 'line>>>', line
                res = {
                    'date_maturity': line.get('date_maturity', False),
                    'partner_id': part,
                    'name': line['name'][:64],
                    'date': date,
                    'debit': line['price'] > 0 and line['price'],
                    'credit': line['price'] < 0 and -line['price'],
                    'account_id': line['account_id'],
                    # 'account_id': account_id,
                    'analytic_lines': line.get('analytic_lines', []),
                    'amount_currency': line['price'] > 0 and abs(line.get('amount_currency', False)) or -abs(line.get('amount_currency', False)),
                    'currency_id': line.get('currency_id', False),
                    'tax_code_id': line.get('tax_code_id', False),
                    'tax_amount': line.get('tax_amount', False),
                    'ref': line.get('ref', False),
                    'quantity': line.get('quantity', 1.00),
                    'product_id': line.get('product_id', False),
                    'product_uom_id': line.get('uos_id', False),
                    'analytic_account_id': line.get('account_analytic_id', False),
                    'main_group': account_id,
                    'is_discount': line.get('is_discount', False),
                }                
                return res
        if type == 'in_refund' :
            if line['price'] < 0:
                product = self.env['product.product'].browse(line.get('product_id', False))
                print 'product>>>', product.id
                print 'line.get>>>', line.get('product_id', False)
                #account_id = product.product_tmpl_id.main_group.property_account_payable.id
                account_id = property_account_payable
                if account_id is None:
                    raise except_orm(_('Warning!'), _('Please define payable control account.'))
                # acount_id= product.product_tmpl_id.main_group.property_account_payable.id
                print 'account_id>>>', account_id        
    
                print 'line>>>', line
                res = {
                    'date_maturity': line.get('date_maturity', False),
                    'partner_id': part,
                    'name': line['name'][:64],
                    'date': date,
                    'debit': line['price'] > 0 and line['price'],
                    'credit': line['price'] < 0 and -line['price'],
                    'account_id': line['account_id'],
                    # 'account_id': account_id,
                    'analytic_lines': line.get('analytic_lines', []),
                    'amount_currency': line['price'] > 0 and abs(line.get('amount_currency', False)) or -abs(line.get('amount_currency', False)),
                    #'amount_currency': line['price'] > 0 and abs(line.get('amount_currency', False)) or -abs(line.get('amount_currency', False)),
                    'currency_id': line.get('currency_id', False),
                    'tax_code_id': line.get('tax_code_id', False),
                    'tax_amount': line.get('tax_amount', False),
                    'ref': line.get('ref', False),
                    'quantity': line.get('quantity', 1.00),
                    'product_id': line.get('product_id', False),
                    'product_uom_id': line.get('uos_id', False),
                    'analytic_account_id': line.get('account_analytic_id', False),
                    'main_group': account_id,
                                        'is_discount': line.get('is_discount', False),

                }
                return res            
        if type == 'out_refund' :
            
            if line['price'] > 0:
                product = self.env['product.product'].browse(line.get('product_id', False))
                print 'product>>>', product.id
                print 'line.get>>>', line.get('product_id', False)
                if  line['is_discount'] == True:
                    if payment_type=='credit':
                        account_id = product.product_tmpl_id.categ_id.property_account_discount_credit.id
                    else:
                        account_id = product.product_tmpl_id.categ_id.property_account_discount_cash.id                
                else:
                    if payment_type=='credit':
                        account_id = product.product_tmpl_id.main_group.property_account_receivable_control.id
                    else:
                        account_id = product.product_tmpl_id.main_group.property_account_receivable.id                    
                    #account_id = product.product_tmpl_id.main_group.property_account_receivable.id
                res = {
                    'date_maturity': line.get('date_maturity', False),
                    'partner_id': part,
                    'name': line['name'][:64],
                    'date': date,
                    'debit': line['price'] > 0 and line['price'],
                    'credit': line['price'] < 0 and -line['price'],
                    'account_id': line['account_id'],
                    # 'account_id': account_id,
                    'analytic_lines': line.get('analytic_lines', []),
                    'amount_currency': line['price'] > 0 and abs(line.get('amount_currency', False)) or -abs(line.get('amount_currency', False)),
                    'currency_id': line.get('currency_id', False),
                    'tax_code_id': line.get('tax_code_id', False),
                    'tax_amount': line.get('tax_amount', False),
                    'ref': line.get('ref', False),
                    'quantity': line.get('quantity', 1.00),
                    'product_id': line.get('product_id', False),
                    'product_uom_id': line.get('uos_id', False),
                    'analytic_account_id': line.get('account_analytic_id', False),
                    'main_group': account_id,
                                        'is_discount': line.get('is_discount', False),

                }
                return res    
        if type == 'in_invoice' :
            if line['price'] > 0:
                product = self.env['product.product'].browse(line.get('product_id', False))
                print 'product>>>', product.id
                print 'line.get>>>', line.get('product_id', False)
                if  line['is_discount'] == True:
                    if payment_type=='credit':
                        account_id = product.product_tmpl_id.categ_id.property_account_discount_credit.id
                    else:
                        account_id = product.product_tmpl_id.categ_id.property_account_discount_cash.id
                else:
                    #account_id = product.product_tmpl_id.main_group.property_account_payable.id
                    account_id = property_account_payable                
                    if account_id is None:
                        raise except_orm(_('Warning!'), _('Please define payable control account.'))
                res = {
                    'date_maturity': line.get('date_maturity', False),
                    'partner_id': part,
                    'name': line['name'][:64],
                    'date': date,
                    'debit': line['price'] > 0 and line['price'],
                    'credit': line['price'] < 0 and -line['price'],
                    'account_id': line['account_id'],
                    # 'account_id': account_id,
                    'analytic_lines': line.get('analytic_lines', []),
                    'amount_currency': line['price'] > 0 and abs(line.get('amount_currency', False)) or -abs(line.get('amount_currency', False)),
                    'currency_id': line.get('currency_id', False),
                    'tax_code_id': line.get('tax_code_id', False),
                    'tax_amount': line.get('tax_amount', False),
                    'ref': line.get('ref', False),
                    'quantity': line.get('quantity', 1.00),
                    'product_id': line.get('product_id', False),
                    'product_uom_id': line.get('uos_id', False),
                    'analytic_account_id': line.get('account_analytic_id', False),
                    'main_group': account_id,
                                        'is_discount': line.get('is_discount', False),

                }
                return res    
            
    def line_get_convert_dr(self, line, part, date):
        account_id = property_account_payable = property_account_payable_clearing = None
        cr = self._cr
        type = 'out_invoice' 
        discount_amt=0
        print 'line_get_convert_newline_get_convert_new', line, part, self.id
        origin = line.get('ref', False)
        for inv in self:
            property_account_payable = inv.partner_id.property_account_payable.id
            property_account_payable_clearing = inv.partner_id.property_account_payable_clearing.id
            
        if origin:
            cr.execute("select type,payment_type from account_invoice where origin=%s and state!='cancel' ", (origin,))
            type_data = cr.fetchone()
            if type_data:
                type = type_data[0]
                payment_type=type_data[1]
            else:
                type = None
                payment_type=None
        if type == 'out_invoice'  :
            product = self.env['product.product'].browse(line.get('product_id', False))
            product_code = product.default_code
            print 'product_code', product_code
            if line['price'] < 0 or line['is_discount'] == True or product_code == 'discount1' or  product_code == 'discount2' or product_code == 'discount3' or  product_code == 'discount4' or  product_code == 'discount5' :
                product = self.env['product.product'].browse(line.get('product_id', False))
                print 'product>>>', product.id
                print 'line.get>>>', line.get('product_id', False)
                if origin and line['is_discount'] == False:
                    cr.execute("select avl.discount_amt from account_invoice av,account_invoice_line avl  where av.id=avl.invoice_id and av.origin=%s and avl.product_id=%s and av.state!='cancel' ", (origin, product.id,))
                    dis_amt = cr.fetchall()
                    if dis_amt:     
                        for amt in dis_amt:
                            discount_amt = discount_amt + amt[0];
                        line['price'] = line['price'] + discount_amt        
                if  line['is_discount'] == True:
                    if payment_type=='credit':
                        account_id = product.product_tmpl_id.categ_id.property_account_discount_credit.id
                    else:
                        account_id = product.product_tmpl_id.categ_id.property_account_discount_cash.id
                else:
                    if payment_type=='credit':
                        account_id = product.product_tmpl_id.main_group.property_account_receivable_control.id
                    else:
                        account_id = product.product_tmpl_id.main_group.property_account_receivable.id                    
                    #account_id = product.product_tmpl_id.main_group.property_account_receivable.id
                    
                print 'account_id>>>', account_id            
                print 'line>>>', line
                print 'line[price]', line['price']
                if line['price'] < 0 :
                    line['price'] = -line['price']
                res = {
                    'date_maturity': line.get('date_maturity', False),
                    'partner_id': part,
                    'name': line['name'][:64],
                    'date': date,
                    'debit': line['price'] > 0 and line['price'],
                    'credit': line['price'] < 0 and -line['price'],
                    'account_id': line['account_id'],
                    # 'account_id': account_id,
                    'analytic_lines': line.get('analytic_lines', []),
                    'amount_currency': line['price'] > 0 and abs(line.get('amount_currency', False)) or -abs(line.get('amount_currency', False)),
                    'currency_id': line.get('currency_id', False),
                    'tax_code_id': line.get('tax_code_id', False),
                    'tax_amount': line.get('tax_amount', False),
                    'ref': line.get('ref', False),
                    'quantity': line.get('quantity', 1.00),
                    'product_id': line.get('product_id', False),
                    'product_uom_id': line.get('uos_id', False),
                    'analytic_account_id': line.get('account_analytic_id', False),
                    'main_group': account_id,
                    'is_discount': line.get('is_discount', False),

                }
                return res
        if type == 'in_refund' :
            product = self.env['product.product'].browse(line.get('product_id', False))
            product_code = product.default_code
            if line['price'] < 0 or line['is_discount'] == True or product_code == 'discount1' or  product_code == 'discount2' or product_code == 'discount3' or  product_code == 'discount4' or  product_code == 'discount5' :
                product = self.env['product.product'].browse(line.get('product_id', False))
                print 'product>>>', product.id
                print 'line.get>>>', line.get('product_id', False)
                if origin and line['is_discount'] == False:
                    cr.execute("select COALESCE( avl.discount_amt , 0 ) from account_invoice av,account_invoice_line avl  where av.id=avl.invoice_id and av.origin=%s and avl.product_id=%s and av.state!='cancel' ", (origin, product.id,))
                    dis_amt = cr.fetchall()
                    if dis_amt:     
                        for amt in dis_amt:
                            discount_amt = discount_amt + amt[0];
                        line['price'] = line['price'] + discount_amt                
                if  line['is_discount'] == True:
                    if payment_type=='credit':
                        account_id = product.product_tmpl_id.categ_id.property_account_discount_credit.id
                    else:
                        account_id = product.product_tmpl_id.categ_id.property_account_discount_cash.id
                else:
                    #account_id = product.product_tmpl_id.main_group.property_account_payable.id
                    account_id = property_account_payable
                    if account_id is None:
                        raise except_orm(_('Warning!'), _('Please define payable control account.'))                
                print 'account_id>>>', account_id        
                print 'line>>>', line
                print 'line[price]', line['price']
                if line['price'] < 0:
                    line['price'] = -line['price']
                print 'after>>>', line['price']
                res = {
                    'date_maturity': line.get('date_maturity', False),
                    'partner_id': part,
                    'name': line['name'][:64],
                    'date': date,
                    'debit': line['price'] > 0 and line['price'],
                    'credit': line['price'] < 0 and -line['price'],
                    'account_id': line['account_id'],
                    # 'account_id': account_id,
                    'analytic_lines': line.get('analytic_lines', []),
                    'amount_currency': line['price'] > 0 and abs(line.get('amount_currency', False)) or -abs(line.get('amount_currency', False)),
                    'currency_id': line.get('currency_id', False),
                    'tax_code_id': line.get('tax_code_id', False),
                    'tax_amount': line.get('tax_amount', False),
                    'ref': line.get('ref', False),
                    'quantity': line.get('quantity', 1.00),
                    'product_id': line.get('product_id', False),
                    'product_uom_id': line.get('uos_id', False),
                    'analytic_account_id': line.get('account_analytic_id', False),
                    'main_group': account_id,
                                        'is_discount': line.get('is_discount', False),

                }
                return res            
        if type == 'out_refund' :
            product = self.env['product.product'].browse(line.get('product_id', False))
            product_code = product.default_code            
            if line['price'] > 0 or line['is_discount'] == True or  product_code == 'discount1' or  product_code == 'discount2' or product_code == 'discount3' or  product_code == 'discount4' or  product_code == 'discount5' :
                product = self.env['product.product'].browse(line.get('product_id', False))
                print 'product>>>', product.id
                print 'line.get>>>', line.get('product_id', False)
                if origin and line['is_discount'] == False:
                    cr.execute("select avl.discount_amt from account_invoice av,account_invoice_line avl  where av.id=avl.invoice_id and av.origin=%s and avl.product_id=%s and av.state!='cancel' ", (origin, product.id,))
                    dis_amt = cr.fetchall()
                    if dis_amt:     
                        for amt in dis_amt:
                            if amt[0] is not None:
                                discount_amt = discount_amt + amt[0];
                        line['price'] = line['price']  - discount_amt       
                if  line['is_discount'] == True:
                    if payment_type=='credit':
                        account_id = product.product_tmpl_id.categ_id.property_account_discount_credit.id
                    else:
                        account_id = product.product_tmpl_id.categ_id.property_account_discount_cash.id                    
                    line['price'] = -1 * line['price']
                else:
                    if payment_type=='credit':
                        account_id = product.product_tmpl_id.main_group.property_account_receivable_control.id
                    else:
                        account_id = product.product_tmpl_id.main_group.property_account_receivable.id                    
                    #account_id = product.product_tmpl_id.main_group.property_account_receivable.id
                print 'account_id>>>', account_id        
                print 'line>>>', line
                print 'line[price]', line['price']
                if line['price'] > 0 :
                    line['price'] = -line['price']
                print 'after>>>', line['price']
                res = {
                    'date_maturity': line.get('date_maturity', False),
                    'partner_id': part,
                    'name': line['name'][:64],
                    'date': date,
                    'debit': line['price'] > 0 and line['price'],
                    'credit': line['price'] < 0 and -line['price'],
                    'account_id': line['account_id'],
                    # 'account_id': account_id,
                    'analytic_lines': line.get('analytic_lines', []),
                    'amount_currency': line['price'] > 0 and abs(line.get('amount_currency', False)) or -abs(line.get('amount_currency', False)),
                    'currency_id': line.get('currency_id', False),
                    'tax_code_id': line.get('tax_code_id', False),
                    'tax_amount': line.get('tax_amount', False),
                    'ref': line.get('ref', False),
                    'quantity': line.get('quantity', 1.00),
                    'product_id': line.get('product_id', False),
                    'product_uom_id': line.get('uos_id', False),
                    'analytic_account_id': line.get('account_analytic_id', False),
                    'main_group': account_id,
                                        'is_discount': line.get('is_discount', False),

                }
                return res
        if type == 'in_invoice' :
            product = self.env['product.product'].browse(line.get('product_id', False))
            product_code = product.default_code            
            if line['price'] > 0  or line['is_discount'] == True or product_code == 'discount1' or  product_code == 'discount2' or product_code == 'discount3' or  product_code == 'discount4' or  product_code == 'discount5'  :
                product = self.env['product.product'].browse(line.get('product_id', False))
                print 'product>>>', product.id
                print 'line.get>>>', line.get('product_id', False)
                if origin and line['is_discount'] == False:
                    cr.execute("select avl.discount_amt from account_invoice av,account_invoice_line avl  where av.id=avl.invoice_id and av.origin=%s and avl.product_id=%s  and av.state!='cancel' ", (origin, product.id,))
                    dis_amt = cr.fetchall()
                    if dis_amt:     
                        for amt in dis_amt:
                            if  amt[0] is not None:
                                discount_amt = discount_amt + amt[0];
                            else:
                                discount_amt=0
                        line['price'] = line['price'] - discount_amt       
                if  line['is_discount'] == True:
                    #account_id = product.product_tmpl_id.main_group.property_account_discount.id
                    if payment_type=='credit':
                        account_id = product.product_tmpl_id.categ_id.property_account_discount_credit.id
                    else:
                        account_id = product.product_tmpl_id.categ_id.property_account_discount_cash.id                    
                    line['price'] = -1 * line['price']
                else:
                    #account_id = product.product_tmpl_id.main_group.property_account_payable.id
                    account_id = property_account_payable
                    if account_id is None:
                        raise except_orm(_('Warning!'), _('Please define payable control account.'))                
                print 'account_id>>>', account_id        
                print 'line>>>', line
                print 'line[price]', line['price']
                if line['price'] > 0:
                    line['price'] = -line['price']
                print 'after>>>', line['price']
                res = {
                    'date_maturity': line.get('date_maturity', False),
                    'partner_id': part,
                    'name': line['name'][:64],
                    'date': date,
                    'debit': line['price'] > 0 and line['price'],
                    'credit': line['price'] < 0 and -line['price'],
                    'account_id': line['account_id'],
                    # 'account_id': account_id,
                    'analytic_lines': line.get('analytic_lines', []),
                    'amount_currency': line['price'] > 0 and abs(line.get('amount_currency', False)) or -abs(line.get('amount_currency', False)),
                    'currency_id': line.get('currency_id', False),
                    'tax_code_id': line.get('tax_code_id', False),
                    'tax_amount': line.get('tax_amount', False),
                    'ref': line.get('ref', False),
                    'quantity': line.get('quantity', 1.00),
                    'product_id': line.get('product_id', False),
                    'product_uom_id': line.get('uos_id', False),
                    'analytic_account_id': line.get('account_analytic_id', False),
                    'main_group': account_id,
                     'is_discount': line.get('is_discount', False),

                }
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
        print 'list_one>>>', list_one
        list_group = [i['main_group'] for i in list_one if i is not None and i ['is_discount'] == False]
        print 'list_group>>>', list_group
        val = set(map(lambda x:x, list_group))
        dis_group = [i['main_group'] for i in list_one if i is not None and i ['is_discount'] == True]
        print 'dis_group>>>', dis_group
        dis_val = set(map(lambda x:x, dis_group))
        print 'val', val
        arr_list = []
        # for AR principle
        for v in val:
            print 'v', v
            price = 0
            date_maturity = partner_id = name = date = account_id = analytic_lines = amount_currency = currency_id = tax_code_id = tax_amount = ref = quantity = product_id = product_uom_id = analytic_account_id = None
            debit = credit = 0
            result = [a for a in list_one if a is not None and a['main_group'] == v]
            print 'result>>>', result
            cr = self._cr
            tmp_currency =0
            for res in result:                
                origin = res['ref']
                product = self.env['product.product'].browse(res.get('product_id', False))
                product_code = product.default_code                
                if product_code == 'discount1' or  product_code == 'discount2' or product_code == 'discount3' or  product_code == 'discount4' or  product_code == 'discount5' :
                    res['debit'] = -1 * res['debit']
                    res['credit'] = -1 * res['credit']
                if origin:
                    cr.execute("select type from account_invoice where origin=%s and state!='cancel' ", (origin,))
                    type = cr.fetchone()
                    if type:
                        type = type[0]
                    else:
                        type = None
                           
                if type == 'out_invoice':
                    debit += res['debit']
                    tmp_currency = res['amount_currency']
                if type == 'in_invoice':             
                    credit += res['credit']
                    tmp_currency +=  -1 * res['amount_currency']
                      
                if type == 'out_refund':             
                    credit += res['credit'] 
                    tmp_currency = res['amount_currency']      
                if type == 'in_refund':             
                    debit += res['debit']
                    tmp_currency += res['amount_currency']
                                                                 
                date_maturity = res['date_maturity']
                partner_id = res['partner_id']
                name = res['name']
                date = res['date']
                account_id = res['main_group']  # replace with product principle AR account
                analytic_lines = res['analytic_lines']
                amount_currency = tmp_currency#res['amount_currency']
                currency_id = res['currency_id']
                tax_code_id = res['tax_code_id']
                tax_amount = res['tax_amount']
                ref = res['ref']
                quantity = res['quantity']
                product_id = res['product_id']
                product_uom_id = res['product_uom_id']
                analytic_account_id = res['analytic_account_id']
            price = credit + debit
            if price != 0.0:
                rec = {
                            'date_maturity': date_maturity,
                            'partner_id': partner_id,
                            'name': '/',
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
        # for discount principle
        for v in dis_val:
            print 'v', v

            price = 0
            date_maturity = partner_id = name = date = account_id = analytic_lines = amount_currency = currency_id = tax_code_id = tax_amount = ref = quantity = product_id = product_uom_id = analytic_account_id = None
            debit = credit = 0
            result = [a for a in list_one if a is not None and a['main_group'] == v]
            print 'result>>>', result
            cr = self._cr

            for res in result:
                origin = res['ref']
                product = self.env['product.product'].browse(res.get('product_id', False))
                product_code = product.default_code                
                discount_receivable_acc=product.product_tmpl_id.categ_id.property_account_discount_principle_receivable.id

                if product_code == 'discount1' or  product_code == 'discount2' or product_code == 'discount3' or  product_code == 'discount4' or  product_code == 'discount5' :
                    res['debit'] = res['debit']
                    res['credit'] = res['credit']
                if origin:
                    cr.execute("select type from account_invoice where origin=%s and state!='cancel' ", (origin,))
                    type = cr.fetchone()
                    if type:
                        type = type[0]
                    else:
                        type = None   
                if type == 'out_invoice':
                    debit = res['debit']
                if type == 'in_invoice':             
                    credit = res['credit']    
                if type == 'out_refund':             
                    credit = res['credit']       
                if type == 'in_refund':             
                    debit = res['debit']                                             
                date_maturity = res['date_maturity']
                partner_id = res['partner_id']
                name = res['name']
                date = res['date']
                account_id = res['main_group']  # replace with product principle AR account
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
                price = credit + debit                
                if price != 0.0:                           
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
                    if type == 'out_invoice':
                        discount_price = res['debit']
                        
                        rec_1 = {
                                    'date_maturity': date_maturity,
                                    'partner_id': partner_id,
                                    'name': name,
                                    'date': date,
                                    'debit': 0,
                                    'credit': discount_price,
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
                        arr_list.append(rec_1)
                        rec_2 = {
                                    'date_maturity': date_maturity,
                                    'partner_id': partner_id,
                                    'name': name,
                                    'date': date,
                                    'debit': discount_price,
                                    'credit': 0,
                                    'account_id': discount_receivable_acc,
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
                        arr_list.append(rec_2)
                                                                   
                    if type == 'out_refund':             
                        refund_price = res['credit'] 
                        rec_3 = {
                                    'date_maturity': date_maturity,
                                    'partner_id': partner_id,
                                    'name': name,
                                    'date': date,
                                    'debit': refund_price,
                                    'credit': 0,
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
                        arr_list.append(rec_3)
                        rec_4 = {
                                    'date_maturity': date_maturity,
                                    'partner_id': partner_id,
                                    'name': name,
                                    'date': date,
                                    'debit': 0,
                                    'credit': refund_price,
                                    'account_id': discount_receivable_acc,
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
                        arr_list.append(rec_4)                                                           
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
                        'is_discount':False,
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
                    'ref': ref,
                 'is_discount':False,

                })

            date = date_invoice

            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)

            # line = [(0, 0, self.line_get_convert(l, part.id, date)) for l in iml]
            data = []
            for res in iml:
                res['ref'] = inv.origin
                print 'res', res
                data.append(res)
            iml = data
            print 'imllllllllllllllllllll',iml
            line_cr = [self.line_get_convert_new(l, part.id, date) for l in iml]
            print 'line_cr>>>',line_cr
            line_tmp = [self.line_get_convert_dr(l, part.id, date) for l in iml]
            print 'line_tmp>>>',line_tmp
            line_dr = self.line_dr_convert_account_with_principle(line_tmp)
            print 'line_dr>>>',line_dr
            # line_product = [self.line_get_product(l, part.id, date) for l in iml]
            # line_dr = [(0, 0, self.line_get_convert_accountid(l, part.id, date)) for l in line_cr]
            lines = line_cr + line_dr
            print 'lines>>>',lines
            line = [(0, 0, self.line_get_convert(l, part.id, date)) for l in lines  if l is not None]
            print 'line>>>',line
            line = inv.group_lines(iml, line)
            print 'line1>>>',line
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
            print 'move_valsmove_valsmove_vals', move_vals
            move = account_move.with_context(ctx_nolang).create(move_vals)

            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'period_id': period.id,
                'move_name': move.name,
                'credit_control':False,
            }
            inv.with_context(ctx).write(vals)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post()
        self._log_event()
        return True
    
    @api.multi
    def invoice_validate(self):
        state='open'
        if self.type=='out_invoice' or self.type =='out_refund':
            if self.payment_type=='credit':
                state='credit_state'
            else:
                state='open'      
        print 'statestatestatestatestatestatestatestate',state
        return self.write({'state': state})    
    account_id = fields.Many2one('account.account', string='Account',
        required=False, readonly=True, states={'draft': [('readonly', False)]},
        help="The partner account used for this invoice.")
    credit_approve_by = fields.Many2one('res.users','Credit Approve By',readonly=True)    
    
    credit_control = fields.Boolean('Credit Control',default='False',)    
    
    state = fields.Selection([
                    ('draft','Draft'),
                    ('proforma','Pro-forma'),
                    ('proforma2','Pro-forma'),
                    ('credit_state','Allow To Credit'),
                    ('open','Open'),
                    ('paid','Paid'),
                    ('cancel','Cancelled'),
                ], string='Status', index=True, readonly=True, default='draft',
                track_visibility='onchange', copy=False,
                help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Invoice.\n"
                     " * The 'Pro-forma' when invoice is in Pro-forma status,invoice does not have an invoice number.\n"
                     " * The 'Open' status is used when user create invoice,a invoice number is generated.Its in open status till user does not pay invoice.\n"
                     " * The 'Paid' status is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled.\n"
                     " * The 'Cancelled' status is used when user cancel invoice.")
    
