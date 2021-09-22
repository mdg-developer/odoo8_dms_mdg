import time
from openerp.osv import fields, osv
from openerp import http
from openerp.http import request
from openerp.tools import html_escape as escape
import json

class township_multi_sync_woo(osv.osv_memory):
    _name = 'township.multi.sync.woo'
    _description = 'Township Multi Sync to Woo'
    
    _columns = {
        'sync':fields.boolean("Sync",required=True),       
    }

    _defaults = {
         'sync':True,         
    }
        
    def towship_sync_woo(self, cr, uid, ids, context=None):
        
        data = self.read(cr, uid, ids, context=context)[0]
        township_obj = self.pool.get('res.township')        
        townships=context.get('active_ids', [])
        for township in self.pool['res.township'].browse(cr,uid,townships,context=None):
            township_obj.sync_to_woo(cr,uid,[township.id],context=None)
        return True  
