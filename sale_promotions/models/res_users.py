from openerp.osv import fields
from openerp.osv import osv
class ResPartnerCategory(osv.osv):
    
    _inherit = 'res.partner.category'    
    _columns = {
        'partner_cate_promo_ids':fields.many2many('promos.rules', 'partner_cate_rules_join_rel' , 'partner_categ_id' ,'promotion_id' , string='Exclusive Promotions'),
    }