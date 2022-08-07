from openerp.osv import fields, osv
from datetime import datetime
from openerp.tools.translate import _
from openerp.fields import Many2one
from openerp import tools

class stock_move(osv.osv):
    
    _inherit = 'stock.move'
    _columns = {
                'manual': fields.boolean('Manual', default=False) ,        
                'is_exchange':fields.boolean('Exchange', default=False),
               }
stock_move()
    
class stock_warehouse(osv.osv):
    
    _inherit = 'stock.warehouse'
    _columns = {
                    'wh_normal_return_location_id': fields.many2one('stock.location', 'Normal Return location'),
                    'wh_exp_location_id': fields.many2one('stock.location', 'Expiry location'),
                    'wh_near_exp_location_id': fields.many2one('stock.location', 'Near Expiry location'),
                    'wh_damage_location_id': fields.many2one('stock.location', 'Damage location'),
                    'wh_fresh_stock_not_good_location_id': fields.many2one('stock.location', 'Fresh stock minor damage location'),
                    'wh_temp_location_id': fields.many2one('stock.location', 'Temp location'),
               }

stock_warehouse()
