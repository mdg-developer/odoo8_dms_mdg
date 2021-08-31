from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.osv.orm import except_orm

class res_township(osv.osv):
    _inherit = "res.township"
    
    _columns = {
               'delivery_team_id':fields.many2one('crm.case.section', 'Delivery Team',required=False),
               'branch_id':fields.many2one('res.branch', 'Branch',required=False),
               'pick_up':fields.boolean('Pick Up', default=False),
               'description': fields.text('Description'),
               'is_sync_woo':fields.boolean('Is Sync Woo', default=False),
               }
    
    def write(self, cr, uid, ids, vals, context=None):  
        data = self.browse(cr,uid,ids[0])
        if data.is_sync_woo == True: 
            vals['is_sync_woo']=False
        res = super(res_township, self).write(cr, uid, ids, vals, context=context)
        return res
    
    def sync_to_woo(self, cr, uid, ids, context=None):
        
        data = self.browse(cr,uid,ids[0])
        if data.is_sync_woo != True:        
            woo_instance_obj = self.pool.get('woo.instance.ept')
            township_obj = self.pool.get('res.township')
            instance = woo_instance_obj.search(cr, uid, [('state','=','confirmed')], limit=1)
            if instance:
                instance_obj = woo_instance_obj.browse(cr,uid,instance)
                wcapi = instance_obj.connect_for_point_in_woo()  
                township = township_obj.browse(cr,uid,data.id)
                if not township.branch_id:
                    raise except_orm(_('UserError'), _("Please define branch for %s!") % (township.name,))                               
                township_info = township.code + "," + township.name + "," + township.branch_id.name + "," + township.city.name                                         
                response = wcapi.post('insert-odoo-township',str(township_info)) 
                if response.status_code in [200,201]:                                  
                    self.write(cr, uid, ids, {'is_sync_woo': True}, context=context)
                else:
                    message = "Error in township syncing:%s"%(response.content)                        
                    raise except_orm(_('UserError'), _("%s!") % (message,))                
