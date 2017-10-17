from openerp.osv import fields, osv

class stock_move(osv.osv):
    _inherit = "stock.move"
    _columns = {
               'sale_inventory_id': fields.many2one('sale.stock.inventory', 'Inventory'),
               }