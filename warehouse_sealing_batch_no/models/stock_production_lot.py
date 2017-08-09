from openerp.osv import fields, osv
from openerp.tools.translate import _

class stock_production_lot(osv.osv):

    _inherit = "stock.production.lot"
    
    
    
    _columns = {
        'arrival_date': fields.date('Arrival Date'),        
        'seal_start_date': fields.date('Sealed Date'),
        'unseal_date': fields.date('Unsealed Date'),
        'unseal': fields.boolean('Unsealed')
        
       
        
    }
    
    
stock_production_lot()   



# class product_product(osv.osv):
# 
#     _inherit = "product.product"
#     
#     _columns = {
#         
#         'product_move_type_id': fields.many2one('product.move.type', 'Moving Type',required=True),
#         'max_height': fields.integer("Max Height"),
#         
#     }
# product_product()
    