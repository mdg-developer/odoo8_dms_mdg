from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class sale_approval(osv.osv):
    
    _name = "sales.approval"
    _description = "Sales Approval"
    _inherit = ['mail.thread', 'ir.needaction_mixin']    
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id    
    
    def action_button_confirm(self, cr, uid, ids, context=None):
        
        return self.write(cr, uid, ids, {'state': 'sumit'}, context=context)

    def action_button_sumit(self, cr, uid, ids, context=None):
        
        return self.write(cr, uid, ids, {'state': 'manager_approve'}, context=context)
                
    def action_button_manager(self, cr, uid, ids, context=None):
        
        return self.write(cr, uid, ids, {'state': 'finance_approve'}, context=context)
    
    def action_button_finance(self, cr, uid, ids, context=None):
        res = {}
        credits_obj = self.pool.get('account.creditnote')        
        approval=self.browse(cr, uid, ids, context=context)
        credit_data={
                        'so_no': approval.ref_no,
                        'customer_id':approval.partner_id.id,
                        'sale_team_id':approval.sale_team_id.id,
                        'user_id':approval.user_id.id,                        
                        'type':approval.type,
                        'description':approval.name,
                        'create_date':approval.date,
                        'used_date':approval.validate_date,            
                        'm_status':'new',            
                        'amount':approval.credit_amt,                                                                                          
                         }
        credit_id = credits_obj.create(cr, uid, credit_data, context=context)         
        print ' credit_data',credit_data
        return self.write(cr, uid, ids, {'state': 'done','credit_note':credit_id}, context=context)    

    def action_cancel(self, cr, uid, ids, context=None):
        
        return self.write(cr, uid, ids, {'state': 'cancel'}, context=context)                   
         
    _columns = {
            'company_id':fields.many2one('res.company', 'Company'),
            'state': fields.selection([
                ('draft', 'New'),
                ('sumit', 'Submit To Manager'),
                ('manager_approve', 'Manager Approved'),
                ('finance_approve', 'Finance Approved'),
                ('done', 'Done'),
                ('cancel', 'Cancelled'),
            ], 'Status', readonly=True, copy=False, select=True),
        'date':fields.date('Create Date'),
        'validate_date':fields.date('Delivery Date'),
        'sale_team_id':fields.many2one('crm.case.section', 'Sales Team' , required=True),
        'user_id':fields.many2one('res.users', 'Salesman Name'  , required=True),
        'partner_id':fields.many2one('res.partner', 'Customer'  , required=True),  # 
        'name':fields.text('Description'),
        'credit_amt':fields.float('Credit Note Amount'  , required=True),
        'type':fields.selection({('cash', 'Cash Rebate')}, string='Type' , required=True),
        'ref_no':fields.char('Ref Number' ),
        'credit_note':fields.many2one('account.creditnote','Credit Note' ,readonly=True),
       'approval_line':fields.one2many('sales.approval.line', 'approval_ids', string='Sale Approval Line', copy=True , required=True),
        'description':fields.text('Terms and Conditions'),
        'note':fields.text('Note'),

  }
    _defaults = {
        'date': fields.datetime.now,
        'company_id':_get_default_company,
        'state': 'draft',
        'type':'cash',
        }   
sale_approval()        

class sale_approval_line(osv.osv):    
    _name = 'sales.approval.line'
    _columns = {
                'approval_ids': fields.many2one('sales.approval', 'Sales Approval'),
                'product_id':fields.many2one('product.product', 'Product', required=True),
                'product_uom':fields.many2one('product.uom', 'UOM', required=True),
                'product_uom_qty':fields.integer('Quantity', required=True),
                }
sale_approval_line()    
