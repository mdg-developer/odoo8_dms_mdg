from openerp.osv import osv, fields

class sales_group(osv.osv):
    _inherit = "sales.group"

    _columns = {
        'competitor_product_ids': fields.many2many('competitor.product', string='Competitor Product'),
    }
