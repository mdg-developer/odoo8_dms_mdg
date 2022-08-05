from openerp.osv import osv, fields

class sales_group(osv.osv):
    _inherit = "sales.group"

    _columns = {
        'competitor_product_ids': fields.one2many('competitor.product', 'sales_group_id', string='Competitor Product'),
    }
