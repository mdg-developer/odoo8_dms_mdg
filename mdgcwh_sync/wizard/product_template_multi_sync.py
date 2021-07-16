
import time
from openerp.osv import fields, osv
from openerp import http
from openerp.http import request
from openerp.tools import html_escape as escape
import json

class product_template_multi_cwh_sync(osv.osv_memory):
    _name = 'product.template.multi.cwh.sync'
    _description = 'Product Template Multi CWH Sync'
    _columns = {
        'cwh_sync':fields.boolean("Sync",required=True),        
        
    }

    _defaults = {
         'sync':True,         
    }
    
    
    def product_template_sync_cwh(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, context=context)[0]
        product_obj = self.pool.get('product.template')
        
        
        product_lists=context.get('active_ids', [])
        for product_id in self.pool['product.template'].browse(cr,uid,product_lists,context=None):
            product_obj.sync_to_cwh(cr,uid,[product_id.id],context=None)
        return True
    
  
               
