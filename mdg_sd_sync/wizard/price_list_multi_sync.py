
import time
from openerp.osv import fields, osv
from openerp import http
from openerp.http import request
from openerp.tools import html_escape as escape
import json

class price_list_multi_sync(osv.osv_memory):
    _name = 'price.list.multi.sync'
    _description = 'Price List Multi Sync'
    _columns = {
        'sync':fields.boolean("Sync",required=True),        
        
    }

    _defaults = {
         'sync':True,         
    }
    
    
    def price_list_sync_sd(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, context=context)[0]
        pricelist_obj = self.pool.get('product.pricelist')
        
        
        price_lists=context.get('active_ids', [])
        for price_list_id in self.pool['product.pricelist'].browse(cr,uid,price_lists,context=None):
            pricelist_obj.sync_to_sd(cr,uid,[price_list_id.id],context=None)
        return True
    
  
               
