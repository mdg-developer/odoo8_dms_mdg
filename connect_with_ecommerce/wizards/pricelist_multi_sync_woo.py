import time
from openerp.osv import fields, osv
from openerp import http
from openerp.http import request
from openerp.tools import html_escape as escape
import json

class pricelist_multi_sync_woo(osv.osv_memory):
    _name = 'pricelist.multi.sync.woo'
    _description = 'Pricelist Multi Sync to Woo'
    
    _columns = {
        'sync':fields.boolean("Sync",required=True),        
        
    }

    _defaults = {
         'sync':True,         
    }
        
    def pricelist_sync_woo(self, cr, uid, ids, context=None):
        
        data = self.read(cr, uid, ids, context=context)[0]
        pricelist_obj = self.pool.get('product.pricelist')        
        pricelists=context.get('active_ids', [])
        for price_list_id in self.pool['product.pricelist'].browse(cr,uid,pricelists,context=None):
            pricelist_obj.sync_to_woo(cr,uid,[price_list_id.id],context=None)
        return True
    
  
               
