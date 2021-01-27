import time
from openerp.osv import fields, osv
from openerp import _
from openerp import http
from openerp.http import request
from openerp.tools import html_escape as escape
import json
from openerp.osv.orm import except_orm

class uom_sync(osv.osv_memory):
    _name = 'uom.sync'
    _description = 'UOM Sync'
    
    _columns = {
        'sync':fields.boolean("Sync",required=True),        
        
    }

    _defaults = {
         'sync':True,         
    }    
    
    def uom_sync_to_woo(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, context=context)[0]
        uom_obj = self.pool.get('product.uom')
        woo_instance_obj = self.pool.get('woo.instance.ept')
        instance = woo_instance_obj.search(cr, uid, [('state','=','confirmed')], context=context, limit=1)
        if instance:
            woo_instance = self.pool['woo.instance.ept'].browse(cr, uid, instance, context=None)
            wcapi = woo_instance.connect_for_point_in_woo() 
                                
        uom_lists=context.get('active_ids', [])
        for uom_id in self.pool.get('product.uom').browse(cr,uid,uom_lists,context=None):
            if uom_id.is_sync_woo != True:
                response = wcapi.post('insert-uom-dropdown/%s'%(uom_id.id),uom_id.name)
                if response.status_code not in [200,201]:
                    raise except_orm(_('Error'), _("Error in syncing for %s %s") % (uom_id.name,response.content,))    
                else:
                    cr.execute('''update product_uom set is_sync_woo=True where id=%s''',(uom_id.id,))               
        return True
    