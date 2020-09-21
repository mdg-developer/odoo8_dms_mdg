import time
from openerp.osv import fields, osv
from openerp import http
from openerp.http import request
from openerp.tools import html_escape as escape
import json

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
            if promo_id.is_sync_woo != True:
                if promo_id.main_group:
                    cr.execute('''select pp.id product_id,name_template product_name 
                                from product_product pp,product_template pt
                                where pp.product_tmpl_id=pt.id
                                and main_group=%s
                                and pp.active=true
                                and pt.active=true''',(promo_id.main_group.id,))
                    product_record = cr.dictfetchall() 
                    if product_record:                           
                        for product in product_record:                            
                            product_id = product.get('product_id')
                            product_name = product.get('product_name')
                            wcapi.post('odoo-discount/%s'%(product_id),product_name)  
                    cr.execute('''update promos_rules set is_sync_woo=True where id=%s''',(promo_id.id,))                   
        return True
    