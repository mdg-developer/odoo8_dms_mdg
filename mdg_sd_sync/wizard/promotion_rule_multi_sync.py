
import time
from openerp.osv import fields, osv
from openerp import http
from openerp.http import request
from openerp.tools import html_escape as escape
import json

class promos_rules_multi_sync(osv.osv_memory):
    _name = 'promos.rules.multi.sync'
    _description = 'Promoation Rule Multi Sync'
    _columns = {
        'sync':fields.boolean("Sync",required=True),        
        
    }

    _defaults = {
         'sync':True,         
    }
    
    
    def promo_rule_sync_sd(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, context=context)[0]
        promolist_obj = self.pool.get('promos.rules')
        
        
        promo_lists=context.get('active_ids', [])
        for promo_id in self.pool['promos.rules'].browse(cr,uid,promo_lists,context=None):
            promolist_obj.sync_to_sd(cr,uid,[promo_id.id],context=None)
        return True
    
  
               
