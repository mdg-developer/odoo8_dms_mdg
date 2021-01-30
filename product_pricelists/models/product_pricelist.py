from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
class product_pricelist(osv.osv):

    _inherit = "product.pricelist"
    _columns = {
                'main_group_id':fields.many2one('product.maingroup','Main Group'),
                'branch_id':fields.many2one('res.branch',string='Branch'),
                'sales_channel':fields.many2one('sale.channel', 'Sale Channel'),
                'consumer':fields.boolean('Is Consumer Pricelist' , default=False),
                }
product_pricelist()

    