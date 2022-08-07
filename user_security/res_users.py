
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID, models

class res_users(osv.osv):
    _inherit = "res.users"
    _description = "Users"
    _columns = {
        'is_entry':fields.boolean('Is entry',default=False),
        'section_ids':fields.many2many('crm.case.section', 'section_users_rel', 'uid', 'section_id', 'Teams', required=True),
        'allow_product':fields.boolean('Allow Product',default=True),
        'allow_promotion':fields.boolean('Allow Promotion',default=True),
        'allow_customer':fields.boolean('Allow Customer',default=True),
        'allow_sale_plan_day':fields.boolean('Allow Sale Plan Day',default=True),
        'allow_sale_plan_trip':fields.boolean('Allow Sale Plan Trip',default=True),
        'allow_stock_request':fields.boolean('Allow Stock Request',default=True),
        'allow_stock_exchange':fields.boolean('Allow Stock Exchange',default=True),
        'allow_visit_record':fields.boolean('Allow Visit Record',default=True),
        'allow_pending_delivery':fields.boolean('Allow Pending Delivery',default=True),
        'allow_credit_collection':fields.boolean('Allow Credit Collection',default=True),
        'allow_collection_team':fields.boolean('Allow Collection Team',default=False),
        'allow_daily_order_report':fields.boolean('Allow Daily Order Report',default=True),
        'allow_daily_sale_report':fields.boolean('Allow Daily Sale Report',default=True),
        'allow_pre_sale':fields.boolean('Allow Pre Sale',default=True),
        'allow_direct_sale':fields.boolean('Allow Direct Sale',default=True),
        'allow_assets':fields.boolean('Allow Assets',default=True),
        'allow_customer_location_update':fields.boolean('Allow Customer Location Update',default=False),
        'allow_stock_check':fields.boolean('Allow Stock Check',default=True),
        'allow_rental':fields.boolean('Allow Customer Rental',default=True),
        'allow_feedback':fields.boolean('Allow Customer Feedback',default=True),
        'allow_customer_create':fields.boolean('Allow Customer Create',default=False),


    }
    
    def automation_cashier_approval(self, cr, uid,context=None):
        cr.execute('''
        UPDATE customer_payment SET payment_id = mobile_sale_order.id FROM mobile_sale_order  WHERE mobile_sale_order.name = customer_payment.notes AND
        customer_payment.date=current_date ;
        ''')
        return True
        

    def automation_account_invoice(self, cr, uid,context=None):
        cr.execute('''
            select count(*) from account_invoice where residual =0 and state='open' and type='out_invoice' and payment_type='credit'
        ''')
        credit_count=cr.fetchone()[0]
        if credit_count>0:
            cr.execute('''
                  update account_invoice set state ='paid' where state='open' and type='out_invoice' and payment_type='credit' and residual =0 
                  ''')
        return True
    
    def automation_run_credit_invoice_job(self, cr, uid,context=None):
        cr.execute('''
            select count(*) from queue_job where is_credit_invoice=True''')
        credit_count=cr.fetchone()[0]
        if credit_count>0:
            cr.execute('''
                  update queue_job set is_credit_invoice =False where is_credit_invoice=True''')
        return True    
res_users()
