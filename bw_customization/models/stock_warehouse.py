from openerp.osv import fields, osv

class stock_warehouse_settings(osv.osv):
    _inherit = 'stock.warehouse'
    _columns={
         'return_location_id': fields.many2one('stock.location', 'Return Location'),
         
         }