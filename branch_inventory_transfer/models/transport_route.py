from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.osv.fields import _column

class transport_route(osv.osv):    
    _name = 'transport.route'
    
    _columns = {
         'name': fields.char('Route Name'),    
         'route_line':fields.one2many('transport.route.line', 'line_id', 'Route Lines', copy=True),     
        }
    
class transport_route_line(osv.osv):  
    _name = 'transport.route.line'
    _description = 'Request Line'
    
    _columns = {                
        'line_id':fields.many2one('transport.route', 'Line', ondelete='cascade', select=True),
        'supplier_id': fields.many2one('res.partner', 'Supplier'),
        'vehicle_id': fields.many2one('fleet.vehicle', 'Vehicle'),
        'transport_cost' : fields.float(string='Transport Cost'),
        'labor_cost': fields.float(string='Labor Cost'),
        }