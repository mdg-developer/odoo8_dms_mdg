from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from pyfcm import FCMNotification

class product_pricelist(osv.osv):

    _inherit = "product.pricelist"
    _columns = {
                'main_group_id':fields.many2one('product.maingroup', 'Main Group'),
         'branch_id':fields.many2many('res.branch', 'pricelist_branch_rel', 'pricelist_id', 'branch_id', string='Branch'),
               
        'state': fields.selection([
            ('draft', 'Draft'),
            ('approve', 'Approved'),
            ], 'Status', readonly=True, copy=False, help="Gives the status of the quotation or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True),
                
                }
    _defaults = {
        'state':'draft',
    }
    
    def approve(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'approve'})


    def publish(self, cr, uid, ids, context=None):
        fcm_api_key = self.pool.get('ir.config_parameter').get_param(cr, uid, 'fcm_api_key', default=False, context=context)
        push_service = FCMNotification(api_key=fcm_api_key)
       # data = self.browse(cr, uid, ids)[0]
        crm_obj = self.pool.get('crm.case.section')
        tablet_obj = self.pool.get('tablets.information')
       # title = data.title
      #  body = data.body
      #  tag = data.reason
        result = {}
        msg_title = "PriceList has be chage"
        message = "Ready to update"
        msg_tag = ""
        
        if ids:
            cr.execute("select id from crm_case_section ")
            team_id = cr.fetchall()

            registration_ids=[]
            for data in team_id:
                tablet_ids = tablet_obj.search(cr,uid,[('sale_team_id','=',data)])
                for tablet_id in tablet_ids:
                    tablet_data = tablet_obj.browse(cr,uid,tablet_id,context)
                    if tablet_data.token:
                        registration_ids.append(tablet_data.token);                
            result = push_service.notify_multiple_devices(registration_ids=registration_ids,  message_body=message, message_title= msg_title, tag=msg_tag)
        return True       
product_pricelist()