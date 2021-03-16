from openerp.osv import fields, osv
from openerp.tools.translate import _
from dateutil.relativedelta import relativedelta
from datetime import datetime

class account_creditnote(osv.osv):
    _name = 'account.creditnote'
    _columns = {
                'name': fields.char('Credit Note Number' ,readonly=True),
                'create_date': fields.date('Create Date',readonly=True),
                'issued_date': fields.date('Redeemed Date',readonly=True),
                'used_date': fields.date('Claimed Date',readonly=True),
                'ref_no': fields.char('Approval No'),
                'so_no': fields.char('Source Document'),
                'customer_id':fields.many2one('res.partner', 'Customer', domain="[('customer','=',True)]" , required=True),
                'customer_code': fields.char(string='Customer Code',readonly=True),                
                'branch_id':fields.many2one('res.branch', 'Branch'),
                'sale_team_id':fields.many2one('crm.case.section', 'Sales Team',readonly=True),
                'user_id':fields.many2one('res.users', 'Redeemed By',readonly=True),
                'description': fields.char('Description'),
                'terms_and_conditions': fields.char('Terms and Conditions'),
                'm_status':fields.selection([('new', 'New'),
                                             ('used', 'Used')], string='Used Status',default='new',readonly=True),
                'type':fields.selection({('invoice_offset', 'Invoice Offset'),('cash', 'Cash Rebate')}, string='Type' , required=True, default='invoice_offset'),
                'amount': fields.float('Amount'),                
                'program_id':fields.many2one('program.form.design', 'Program' , required=True), 
                'principle_id':fields.many2one('product.maingroup', 'Principal'),
                
#                 'principle_id': fields.related('program_id', 'principle_id', type='many2one', relation='product.maingroup',
#                             string='Principle', store=True, readonly=True),
                'redeemed_user_id':fields.many2one('res.users', 'Redeemedby'),
                'approved_date': fields.date('Approved Date',readonly=True),
                'used_by': fields.date('Used By',readonly=True),
                'approved_user_id':fields.many2one('res.users', 'Approved By',readonly=True),
                'from_date': fields.date('From Date'),
                'to_date': fields.date('To Date'),
                'invoice_number': fields.char('Invoice Number',readonly=True),
                'remark': fields.char('Remark',readonly=False),

                'state':fields.selection([
                    ('draft','Draft'),
                    ('approved','Approved'),
                    ('redeemed','Redeemed'),
                    ('claimed','Claimed'),
                    
        ], string='Status', index=True, readonly=True, default='draft', copy=False)
                }
    _defaults = {
        'type':'cash',
        'state': 'draft',
        }
    
    def on_change_program_id(self, cr, uid,ids,program_id, context=None):
        values = {}
        if program_id:
            program_data = self.pool.get('program.form.design').browse(cr, uid, program_id, context=context)
            program_data_id = program_data
            if program_data_id:
                
                values = {
                     'principle_id':program_data_id.principle_id.id or False,
                     'from_date':program_data.from_date,
                     'to_date':program_data.to_date,
                     'amount':program_data.amount,
                     'terms_and_conditions': program_data.term_and_condition,
                }
        return {'value': values}  
    
    def on_change_customer_id(self, cr, uid,ids,partner_id, context=None):
        values = {}
        if partner_id:
            partner_data = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
            if partner_data:                
                values = {
                        'customer_code':partner_data.customer_code or None,
                }
        return {'value': values}   
    
    def set_to_approved(self, cr, uid, ids, context=None):
        used_by = datetime.today() + relativedelta(months=+6)
        self.write(cr, uid, ids, {'state':'approved','approved_user_id':uid,'approved_date':fields.date.context_today(self,cr,uid,context=context),'used_by':used_by}, context=None)
        move_Obj = self.pool.get('account.move')
        journal_obj = self.pool.get('account.journal')
        journal_id = journal_obj.search(cr, uid, [('code', '=', 'MIS')],context=None)
        if ids:
                for resVal in self.browse(cr, uid, ids, context=context):
                    if not resVal.principle_id:
                        raise osv.except_osv(_('Configuration Error!'), _('Please select the principle.'))
                    account_move = {
                                        'journal_id': journal_id[0],
                                        'state': 'draft',
                                        'date': resVal.approved_date,
                                        'amount': resVal.amount,
                                        'ref': resVal.name,
                                        'partner_id': resVal.customer_id.id,
                                        'branch_id': resVal.branch_id.id,
                                        
                                        }
                    company_id = resVal.create_uid.company_id.id
                    cr.execute("select * from account_period where %s >=date_start and %s <=date_stop", (resVal.approved_date, resVal.approved_date,))         
                    period_id = cr.fetchone()[0]
                    move_id = move_Obj.create(cr, uid, account_move, context=context)
                    cr.execute("""insert into account_move_line (partner_id,name,account_id,date_maturity,move_id,credit,debit,journal_id,date,company_id,period_id) 
                        values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s),
                              (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                              ( resVal.customer_id.id,resVal.name , resVal.principle_id.property_receivable_clearing_account.id,   resVal.approved_date, move_id, 0.0, resVal.amount, journal_id[0], resVal.approved_date,company_id, period_id, 
                               resVal.customer_id.id,resVal.name,resVal.principle_id.property_trade_payable_account.id,resVal.approved_date, move_id, resVal.amount, 0.0, journal_id[0], resVal.approved_date,company_id, period_id,))
            
        return True
        
        
    def set_to_redeemed(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'redeemed','user_id':uid,'issued_date':fields.date.context_today(self,cr,uid,context=context)}, context=context)
#         move_Obj = self.pool.get('account.move')
#         journal_obj = self.pool.get('account.journal')
#         journal_id = journal_obj.search(cr, uid, [('code', '=', 'CN')],context=None)
#         if ids:
#                 for resVal in self.browse(cr, uid, ids, context=context):
#                     if not resVal.principle_id:
#                         raise osv.except_osv(_('Configuration Error!'), _('Please select the principle.'))
#                     account_move = {
#                                         'journal_id': journal_id[0],
#                                         'state': 'draft',
#                                         'date': resVal.issued_date,
#                                         'amount': resVal.amount,
#                                         'ref': resVal.name,
#                                         'partner_id': resVal.customer_id.id,
#                                         'branch_id': resVal.branch_id.id,
#                                         
#                                         }
#                     company_id = resVal.create_uid.company_id.id
#                     cr.execute("select * from account_period where %s >=date_start and %s <=date_stop", (resVal.approved_date, resVal.approved_date,))         
#                     period_id = cr.fetchone()[0]
#                     move_id = move_Obj.create(cr, uid, account_move, context=context)
#                     cr.execute("""insert into account_move_line (partner_id,name,account_id,date_maturity,move_id,credit,debit,journal_id,date,company_id,period_id) 
#                         values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s),
#                               (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
#                               ( resVal.customer_id.id,resVal.name , resVal.principle_id.property_trade_payable_account.id,resVal.approved_date, move_id, 0.0, resVal.amount, journal_id[0], resVal.approved_date,company_id, period_id, 
#                                resVal.customer_id.id,resVal.name,resVal.principle_id.property_account_receivable_clearing.id,resVal.approved_date, move_id, resVal.amount, 0.0, journal_id[0], resVal.approved_date,company_id, period_id,))
#         
        return True 
    
    def set_to_claimed(self, cr, uid, ids, context=None):
        #self.write(cr, uid, ids, {'state':'claimed','used_date':fields.date.context_today(self,cr,uid,context=context)}, context=context)
        
        mod_obj = self.pool.get('ir.model.data')
        wiz_view = mod_obj.get_object_reference(cr, uid, 'account_creditnote', 'redeemed_journal_view')
        for move in self.browse(cr, uid, ids, context=context):
            ctx = {
                'active_ids': move.id,
                
            }
            
              
            act_import = {
                'name': _('Credit Note State'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'redeemed.journal',
                'view_id': [wiz_view[1]],
                'nodestroy': True,
                'target': 'new',
                'type': 'ir.actions.act_window',
                'context': ctx,
            }
            return act_import
        
        return True
          
    def create(self, cursor, user, vals, context=None):
        credit_no = self.pool.get('ir.sequence').get(cursor, user,
            'creditnote.code') or '/'
        vals['name'] = credit_no
        if vals.get('program_id'):
            program_data = self.pool.get('program.form.design').browse(cursor, user, vals.get('program_id'), context=context)
            if program_data:
                vals['principle_id'] = program_data.principle_id.id if program_data.principle_id else None
                vals['from_date'] = program_data.from_date
                vals['to_date'] = program_data.to_date
        if vals.get('customer_id'):
            partner_data = self.pool.get('res.partner').browse(cursor, user, vals.get('customer_id'), context=context)
            if partner_data:
                vals['customer_code'] = partner_data.customer_code or None
        return super(account_creditnote, self).create(cursor, user, vals, context=context)
    
    def write(self, cursor, user, ids, vals, context=None):
        
        for data in self.browse(cursor, user, ids, context):
            if vals.get('program_id'):
                program_data = self.pool.get('program.form.design').browse(cursor, user, vals.get('program_id'), context=context)
                if program_data:
                    vals['principle_id'] = program_data.principle_id.id if program_data.principle_id else None
                    vals['from_date'] = program_data.from_date
                    vals['to_date'] = program_data.to_date
            elif data.program_id: 
                program_data = self.pool.get('program.form.design').browse(cursor, user, data.program_id.id, context=context)
                if program_data:
                    vals['principle_id'] = program_data.principle_id.id if program_data.principle_id else None
                    vals['from_date'] = program_data.from_date
                    vals['to_date'] = program_data.to_date
            if vals.get('customer_id'):
                partner_data = self.pool.get('res.partner').browse(cursor, user, vals.get('customer_id'), context=context)
                if partner_data:
                    vals['customer_code'] = partner_data.customer_code or None
            elif data.customer_id: 
                partner_data = self.pool.get('res.partner').browse(cursor, user, data.customer_id.id, context=context)
                if partner_data:
                    vals['customer_code'] = partner_data.customer_code or None
        res = super(account_creditnote, self).write(cursor, user, ids, vals, context=context)
        return res  
     
account_creditnote()     