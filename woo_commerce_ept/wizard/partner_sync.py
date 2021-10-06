import time
from openerp.osv import fields, osv
from openerp import _
from openerp import http
from openerp.http import request
from openerp.tools import html_escape as escape
import json
from openerp.osv.orm import except_orm

class partner_sync(osv.osv_memory):
    _name = 'partner.sync'
    _description = 'Partner Sync'
    
    _columns = {
        'sync':fields.boolean("Sync",required=True),        
        
    }

    _defaults = {
         'sync':True,         
    }    
    
    def partner_sync_to_woo(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, context=context)[0]
        partner_obj = self.pool.get('res.partner')
        woo_instance_obj = self.pool.get('woo.instance.ept')
        instance = woo_instance_obj.search(cr, uid, [('state','=','confirmed')], context=context, limit=1)
        if instance:
            woo_instance = self.pool['woo.instance.ept'].browse(cr, uid, instance, context=None)
            customer_wcapi = woo_instance.connect_for_point_in_woo()                    
        partner_lists=context.get('active_ids', [])
        for partner in self.pool.get('res.partner').browse(cr,uid,partner_lists,context=None):
            #woo_customer_id
            if customer_wcapi and partner.woo_customer_id:
                customer_data = {} 
                if partner.property_payment_term:
                    if partner.credit_allow == True:
                        credit_allow = 'Yes'
                    else:
                        credit_allow = 'No'       
                    customer_data = credit_allow + ',' + partner.property_payment_term.name                   
                    woo_customer_id = partner.woo_customer_id.split("_")[1]                    
                    customer_response = customer_wcapi.put('credit-allow/%s'%(woo_customer_id),customer_data)  
                    if customer_response.status_code not in [200,201]:
                        raise except_orm(_('Error'), _("Error in syncing response customer for woo customer id %s %s") % (partner.woo_customer_id,customer_response.content,)) 
                else:
                    raise except_orm(_('Error'), _("Parent is not set Payment Term"))
                if customer_wcapi and partner.name:
                    woo_customer_id = partner.woo_customer_id.split("_")[1]
                    customer_name = partner.name          
                    customer_response = customer_wcapi.put('add_user_shop/%s'%(woo_customer_id),customer_name)
                    if customer_response.status_code not in [200,201]:
                        raise except_orm(_('Error'), _("Error in syncing response customer for woo customer id %s %s") % (partner.woo_customer_id,customer_response.content,))
                if customer_wcapi:
                    woo_customer_id = partner.woo_customer_id.split("_")[1]
                    contact_person_name = partner.temp_customer          
                    contact_person_response = customer_wcapi.put('add_user_contact_name/%s'%(woo_customer_id),contact_person_name)
                    if contact_person_response.status_code not in [200,201]:
                        raise except_orm(_('Error'), _("Error in syncing response customer for woo customer id %s %s") % (partner.woo_customer_id,contact_person_response.content,)) 
        return True
    