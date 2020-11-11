from openerp.osv import osv, fields

class PromotionsRules(osv.Model):
    "Promotion Rules"
    _inherit = "promos.rules"
    
    _columns = {
                'ecommerce':fields.boolean('For E-commerce', default=False),
                'checking_main_group':fields.many2one('product.maingroup', 'Promotion Checking Main Group',track_visibility='always'),
                'is_sync_woo':fields.boolean('Is Sync Woo', default=False),
    }
    