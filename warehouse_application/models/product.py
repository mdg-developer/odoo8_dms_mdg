from openerp.osv import osv, fields, expression
from openerp import api, tools, SUPERUSER_ID

class product_template(osv.osv):
    _inherit = "product.template"
    
    _columns = {  
        'carton_image': fields.binary("Carton Image"),
        'bypass_barcode':fields.boolean('By Pass Barcode' , default=False),
    }
    