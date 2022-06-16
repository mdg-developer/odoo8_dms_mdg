
import time
from openerp.osv import fields, osv
from openerp import http
from openerp.http import request
from openerp.tools import html_escape as escape
import json

class product_template_multi_delivery_group(osv.osv_memory):
    _name = 'product.template.multi.delivery'
    _description = 'Product Template Multi Delivery'
    _columns = {
        'delivery_id':fields.many2one('delivery.group', 'Delivery Group',required=True),        
        
    }

    
    
    
    def product_template_assign_delivery(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, context=context)[0]
        product_obj = self.pool.get('product.template')
        
        
        product_lists=context.get('active_ids', [])
        for product_id in self.pool['product.template'].browse(cr,uid,product_lists,context=None):
            product_obj.write(cr,uid,[product_id.id],{'delivery_id':data['delivery_id'][0]},context=None)
        return True
    
  
               
