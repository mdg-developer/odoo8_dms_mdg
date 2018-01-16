from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import datetime, timedelta

class stock_production_lot(osv.osv):

    _inherit = "stock.production.lot"
    
    
    def start_sealing(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'confirm'}, context=context)
        return True     

    def unseal_button(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'complete','unseal':True}, context=context)
        return True         
    
    _columns = {
        'arrival_date': fields.date('Arrival Date'),        
        'seal_start_date': fields.date('Sealed Date'),
        'unseal_date': fields.date('Unsealed Date'),
        'unseal': fields.boolean('Unsealed',readonly=True),
        'state':fields.selection([('draft', 'Sealing process required'), ('confirm', 'Under Seal State'), ('complete', 'Unseal')], 'Status')
    }
    
    _defaults = {
        'seal_start_date': datetime.now(),
        'unseal_date': datetime.now(),
        'state' : 'draft',
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
    