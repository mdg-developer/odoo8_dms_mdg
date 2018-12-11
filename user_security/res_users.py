
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID, models

class res_users(osv.osv):
    _inherit = "res.users"
    _description = "Users"
 
    def _get_group(self, cr, uid, context=None):
        dataobj = self.pool.get('ir.model.data')
        result = []
        try:
            dummy, group_id = dataobj.get_object_reference(cr, SUPERUSER_ID, 'base', 'group_user')
            result.append(group_id)
            dummy, group_id = dataobj.get_object_reference(cr, SUPERUSER_ID, 'base', 'group_partner_manager')
            result.append(group_id)
            dummy, group_id = dataobj.get_object_reference(cr, SUPERUSER_ID, 'base', 'group_allow_product')
            result.append(group_id)  
            dummy, group_id = dataobj.get_object_reference(cr, SUPERUSER_ID, 'base', 'group_allow_promotions')
            result.append(group_id)  
            dummy, group_id = dataobj.get_object_reference(cr, SUPERUSER_ID, 'base', 'group_allow_customers')
            result.append(group_id)  
            dummy, group_id = dataobj.get_object_reference(cr, SUPERUSER_ID, 'base', 'group_allow_route_plan')
            result.append(group_id)              
            dummy, group_id = dataobj.get_object_reference(cr, SUPERUSER_ID, 'base', 'group_allow_sale_plan_trip')
            result.append(group_id)                
            dummy, group_id = dataobj.get_object_reference(cr, SUPERUSER_ID, 'base', 'group_allow_stock_request')
            result.append(group_id)                 
            dummy, group_id = dataobj.get_object_reference(cr, SUPERUSER_ID, 'base', 'group_allow_stock_exchange')
            result.append(group_id)                 
            dummy, group_id = dataobj.get_object_reference(cr, SUPERUSER_ID, 'base', 'group_allow_visit_record')
            result.append(group_id)    
            dummy, group_id = dataobj.get_object_reference(cr, SUPERUSER_ID, 'base', 'group_allow_direct_sale_invoices')
            result.append(group_id)             
            dummy, group_id = dataobj.get_object_reference(cr, SUPERUSER_ID, 'base', 'group_allow_pre_sale_order')
            result.append(group_id) 
            dummy, group_id = dataobj.get_object_reference(cr, SUPERUSER_ID, 'base', 'group_allow_pending_delivery')
            result.append(group_id)         
            dummy, group_id = dataobj.get_object_reference(cr, SUPERUSER_ID, 'base', 'group_allow_credit_collection')
            result.append(group_id)   
            dummy, group_id = dataobj.get_object_reference(cr, SUPERUSER_ID, 'base', 'group_allow_collection_team')
            result.append(group_id)   
            dummy, group_id = dataobj.get_object_reference(cr, SUPERUSER_ID, 'base', 'group_allow_daily_order_report')
            result.append(group_id)            
            dummy, group_id = dataobj.get_object_reference(cr, SUPERUSER_ID, 'base', 'group_allow_daily_sale_report')
            result.append(group_id)               
            dummy, group_id = dataobj.get_object_reference(cr, SUPERUSER_ID, 'base', 'group_allow_direct_sale')
            result.append(group_id)       
            dummy, group_id = dataobj.get_object_reference(cr, SUPERUSER_ID, 'base', 'group_allow_pre_sale')
            result.append(group_id)                 
            dummy, group_id = dataobj.get_object_reference(cr, SUPERUSER_ID, 'base', 'group_allow_visit_record')
            result.append(group_id)        
            dummy, group_id = dataobj.get_object_reference(cr, SUPERUSER_ID, 'base', 'group_allow_assets')
            result.append(group_id)                                                                                             
        except ValueError:
            # If these groups does not exists anymore
            pass
        return result  
        
    _columns = {
        'section_ids':fields.many2many('crm.case.section', 'section_users_rel', 'uid', 'section_id', 'Teams', required=True),
    }
    
    _defaults = {
        'groups_id': _get_group,
    }    
  
res_users()
