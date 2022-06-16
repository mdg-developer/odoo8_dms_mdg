from openerp.osv import osv, fields

class PromotionsRules(osv.Model):
    "Promotion Rules"
    _inherit = "promos.rules"
    
    _columns = {
                'ecommerce':fields.boolean('For E-commerce', default=False),
                'checking_main_group':fields.many2one('product.maingroup', 'Promotion Checking Main Group',track_visibility='always'),
                'is_sync_woo':fields.boolean('Is Sync Woo', default=False, copy=False),
    }
    
    def write(self, cr, uid, ids, vals, context=None):  
        data = self.browse(cr,uid,ids[0])
        if data.is_sync_woo == True and vals.get('main_group'): 
            vals['is_sync_woo']=False
        res = super(PromotionsRules, self).write(cr, uid, ids, vals, context=context)
        return res 
    