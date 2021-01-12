import time
from openerp.osv import fields, osv
from openerp import _
from openerp import http
from openerp.http import request
from openerp.tools import html_escape as escape
import json
from openerp.osv.orm import except_orm

class promotion_sync(osv.osv_memory):
    _name = 'promotion.sync'
    _description = 'Promoation Sync'
    
    _columns = {
        'sync':fields.boolean("Sync",required=True),        
        
    }

    _defaults = {
         'sync':True,         
    }    
    
    def promotion_sync_to_woo(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, context=context)[0]
        promolist_obj = self.pool.get('promos.rules')
        woo_instance_obj = self.pool.get('woo.instance.ept')
        instance = woo_instance_obj.search(cr, uid, [('state','=','confirmed')], context=context, limit=1)
        if instance:
            woo_instance = self.pool['woo.instance.ept'].browse(cr, uid, instance, context=None)
            wcapi = woo_instance.connect_for_point_in_woo() 
                                
        promo_lists=context.get('active_ids', [])
        for promo_id in self.pool.get('promos.rules').browse(cr,uid,promo_lists,context=None):
            if promo_id.ecommerce == True:
                if promo_id.is_sync_woo != True:
                    promotion_info = str(promo_id.id) + "," + promo_id.name + ","
                    if promo_id.main_group:
                        promotion_info += promo_id.main_group.name
                    cr.execute("select ((%s at time zone 'utc' )at time zone 'asia/rangoon')::date,((%s at time zone 'utc' )at time zone 'asia/rangoon')::date", (promo_id.from_date,promo_id.to_date,))    
                    date_data = cr.fetchall()
                    if date_data:
                        promotion_info += "," + str(date_data[0][0]) + "," + str(date_data[0][1])
                    response = wcapi.post('odoo-discount',promotion_info)  
                    if response.status_code not in [200,201]:
                        raise except_orm(_('Error'), _("Error in syncing for %s %s") % (promo_id.name,response.content,)) 
                    else:
                        cr.execute('''update promos_rules set is_sync_woo=True where id=%s''',(promo_id.id,)) 
            else:
                raise except_orm(_('UserError'), _("%s is not ecommerce promotion.You can sync only ecommerce promotion!") % (promo_id.name,))              
        return True
    