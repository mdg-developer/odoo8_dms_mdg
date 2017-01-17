from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
class product_pricelist(osv.osv):

    _inherit = "product.pricelist"
    _columns = {
                'main_group_id':fields.many2one('product.maingroup','Main Group'),
                'branch_id':fields.many2one('res.branch',string='Branch'),

                }
product_pricelist()