from openerp.osv import fields, osv
from openerp.tools.translate import _

class stock_quant_package(osv.osv):

    _inherit = "stock.quant.package"
    
    _columns = {
        'stickering_start_date': fields.datetime('Stickering Start'),        
        'stickering_end_date': fields.datetime('Stickering End'),
        'repacking_start_date': fields.datetime('Repacking Start'),
        'repacking_end_date': fields.datetime('Repacking End'),
        'saleable': fields.boolean('Saleable'),       
       
        
    }
    