from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from datetime import datetime, timedelta
import calendar
from openerp import tools

OE_DATEFORMAT = "%Y-%m-%d"

class product_template(osv.osv):
    _inherit = "product.template" 
    
    READONLY_STATES = {
        'confirmed': [('readonly', True)],
        'approved': [('readonly', True)],
        'done': [('readonly', True)]
    }

    _columns = {   
               # 'partner_id':fields.many2one('res.partner', 'Supplier'),
            'partner_id':fields.many2one('res.partner', string = 'Supplier',domain=[('supplier', '=', True)]),
                }