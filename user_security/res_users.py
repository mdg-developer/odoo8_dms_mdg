
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID, models

class res_users(osv.osv):
    _inherit = "res.users"
    _description = "Users"
    _columns = {
        'section_ids':fields.many2many('crm.case.section', 'section_users_rel', 'uid', 'section_id', 'Teams', required=True),
        'allow_product':fields.boolean('Allow Product',default=True),
        'allow_promotions':fields.boolean('Allow Promotions',default=True),
        'allow_customers':fields.boolean('Allow Customers',default=True),
        'allow_route_plan':fields.boolean('Allow Product',default=True),
        'allow_sale_plan_trip':fields.boolean('Allow Sale Plan Trip',default=True),
        'allow_stock_request':fields.boolean('Allow Stock Request',default=True),
        'allow_stock_exchange':fields.boolean('Allow Stock Exchange',default=True),
        'allow_visit_record':fields.boolean('Allow Visit Record',default=True),
        'allow_pending_delivery':fields.boolean('Allow Pending Delivery',default=True),
        'allow_credit_collection':fields.boolean('Allow Credit Collection',default=True),
        'allow_collection_team':fields.boolean('Allow Collection Team',default=True),
        'allow_daily_order_report':fields.boolean('Allow Daily Order Report',default=True),
        'allow_daily_sale_report':fields.boolean('Allow Daily Sale Report',default=True),
        'allow_pre_sale':fields.boolean('Allow Pre Sale',default=True),
        'allow_direct_sale':fields.boolean('Allow Direct Sale',default=True),
        'allow_visit_record':fields.boolean('Allow Visit Record',default=True),
        'allow_assets':fields.boolean('Allow Assets',default=True),
        'allow_customer_location_update':fields.boolean('Allow Customer Location Update',default=True)
    }
    
res_users()
