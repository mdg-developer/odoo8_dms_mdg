from openerp.osv import fields, osv
from openerp.tools.translate import _

class stock_picking(osv.osv):
    _inherit = "stock.picking"
    
    _columns = {
        'loading_date' : fields.datetime('Loading Date & Time' , states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
        'loading_by': fields.char('Loading By', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
        'checked_by':fields.char("Checked By", states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
        'approved_by': fields.char('Approved By', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
        'transport_type': fields.char('Transport Type', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
        'transport_mode': fields.char('Transport Mode', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
        'vehicle_no': fields.char('Vehicle No', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
        'consignee': fields.char('Consignee', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
        'departure_date' : fields.datetime('Departure Date & Time', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
        'transported_by': fields.char('Transported By', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
        'received_by':fields.char("Received By" , states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
               }
    
    
