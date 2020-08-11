from openerp.osv import osv, fields

class PromotionsRules(osv.Model):
    "Promotion Rules"
    _inherit = "promos.rules"
    
    _columns = {
                'ecommerce':fields.boolean('For E-commerce', default=False),
    }
    