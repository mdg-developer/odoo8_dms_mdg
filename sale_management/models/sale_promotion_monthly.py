from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class sale_promotion(osv.osv):
    
    _name = "sales.promotion"
    _description = "Sale Promotion"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _columns = {
            'state': fields.selection([
                ('draft', 'New'),
                ('submit', 'Submit To Approval'),
                ('manager_approve', 'Approved'),
                ('cancel', 'Cancel'),

            ], 'Status', readonly=True, copy=False, select=True),
                
        'description':fields.char('Description'),
        'promotion':fields.many2many('promos.rules', string='Promotion'),
        'create_date':fields.date('Create Date'),
        'user_id':fields.many2one('res.users', 'Salesman'),
        'officer_id':fields.many2one('res.users', 'Approved Officer'),
        'approved_date':fields.date('Approved Date'),
        'from_date':fields.date('From Date'),
        'to_date':fields.date('To Date'),
        'note':fields.text('Notes'),
        'chatting_message':fields.text('Chatting Message'),
        'product_id':fields.many2one('product.product', 'Product'),
        'category_id': fields.many2one('product.category', 'Product Category'),
        'promotion_line':fields.one2many('sales.promotion.line', 'promotion_ids', string='Promotion Monthly Line', copy=True , required=True),

  }
    _defaults = {
        'create_date': fields.datetime.now,
        'state': 'draft',
        }
    
    def action_button_confirm(self, cr, uid, ids, context=None):
        
        return self.write(cr, uid, ids, {'state': 'submit'}, context=context)
    
    def action_button_submit(self, cr, uid, ids, context=None):
        
        return self.write(cr, uid, ids, {'state': 'manager_approve'}, context=context)
    
    def action_cancel(self, cr, uid, ids, context=None):
        
        return self.write(cr, uid, ids, {'state': 'cancel'}, context=context) 
    
    
                
sale_promotion()        

class sale_promotion_line(osv.osv):    
    _name = 'sales.promotion.line'
    _columns = {
                'promotion_ids': fields.many2one('sales.promotion', 'Sales Promotion'),
                'branch_id': fields.many2one('res.branch', 'Branch'),
                'month': fields.selection([
                ('Jan', 'January'),
                ('Feb', 'February'),
                ('Mar', 'March'),
                ('Apr', 'April'),
                ('May', 'May'),
                ('June', 'June'),
                ('Jul', 'July'),
                ('Aug', 'August'),
                ('Sep', 'September'),
                ('Oct', 'October'),
                ('Nov', 'November'),
                ('Dec', 'December'),

            ], 'Month', copy=False, select=True),
                'channel_id':fields.many2one('sale.channel' , string='Channel'),
                'quantity':fields.float('Quantity'),
                'promo_qty':fields.integer('Promotion Qty'),
                'allowed_amt':fields.float('Allowed Amount'),
                'cus_class':fields.many2one('sale.class', 'Customer Class'),
                'num_cus':fields.integer('No Of Customer'),
                'reward_amt':fields.float('Reward Amount'),
                'reward_percentage': fields.float('Reward (%)', help='For example, enter 50.0 to apply a percentage of 50%'),
                }
sale_promotion_line()    

class sale_monthly_promotion(osv.osv):
    _name = "sale.monthly.promotion"
    _description = 'Monthly Promotion'
    
    _columns = {
                            'code':fields.char('Code', required=True),
                            'name':fields.char('Description', required=True),
                            'date':fields.date('Date', required=True),
                            'from_date':fields.date('Promotion Start Date', required=True),
                            'to_date':fields.date('Promotion End Date', required=True),
                            'product_id':fields.many2one('product.product', string='Product'),
                            'product_categ_id':fields.many2one('product.category', string='Product Category'),
                            'sale_channel_id':fields.many2many('sale.channel', 'sale_monthly_promo_rel', 'sale_promo_id', 'sale_channel_id', string='Sales Channels'),
                            'branch_id':fields.many2one('res.branch', string='Branch'),
                            'product_uom_id':fields.many2one('product.uom', string='Sale UOM'),
                            'sale_qty':fields.float(string='Sales Qty'),
                            'rebate_percentage':fields.float(string='Rebate Percentage'),
                            'foc_qty':fields.float('FOC Quantity'),
                            'foc_product_id':fields.many2one('product.product', string='FOC To Give Product'),
                            'rebate_amount':fields.float('Rebate Amount'),
                            'remark':fields.text('Remark')
                        }
    
sale_monthly_promotion()
