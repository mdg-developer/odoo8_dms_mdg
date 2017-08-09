from openerp.osv import fields, osv
from openerp.tools.translate import _

class product_move_type(osv.osv):

    _name = "product.move.type"
    
    
    
    _columns = {
                
        'name': fields.char('Name', required=True),
       
        
    }
    
    
product_move_type()   

class product_template(osv.osv):

    _inherit = "product.template"
    
    _columns = {
        
        'product_move_type_id': fields.many2one('product.move.type', 'Moving Type',required=True),
        'max_height': fields.integer("Max Shelf Level"),
        'stickering_chk': fields.boolean("Stickering Process"),
        'repacking_chk': fields.boolean("Repacking Process"),
    }
	
product_template()	

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
    