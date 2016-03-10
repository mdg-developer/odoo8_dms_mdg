from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
class product_pricelist(osv.osv):

    _inherit = "product.pricelist"
    _columns = {
                'main_group_id':fields.many2one('product.maingroup','Main Group')
                }
product_pricelist()