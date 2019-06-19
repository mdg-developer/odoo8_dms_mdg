from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.osv.fields import _column


class transport_route(osv.osv):    
    _name = 'transport.route'
    
    _columns = {
         'name': fields.char('Route Name'),
        'from_dest_id': fields.many2one('res.branch', 'To Destination'),
        'to_dest_id': fields.many2one('res.branch', 'From Destination'),
         'route_line':fields.one2many('transport.route.line', 'line_id', 'Route Lines', copy=True),
        }

    
class transport_route_line(osv.osv):  
    _name = 'transport.route.line'
    _description = 'Request Line'
    
    def on_change_vehicle_id(self, cr, uid,ids,vehicle_id, context=None):
        values = {}
        if vehicle_id:
            vehicle_data = self.pool.get('fleet.vehicle').browse(cr, uid, vehicle_id, context=context)
            truck_type_id = vehicle_data.truck_type_id
            if truck_type_id:
                type_id=truck_type_id.id
                values = {
                     'truck_type':type_id,
    
                }
        return {'value': values}   
      
    def _total_value(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}               
        for order in self.browse(cr, uid, ids, context=context):
            val1 = 0.0            

            val1 = order.labor_cost+order.transport_cost                      
            res[order.id] = val1
        return res 
            
    _columns = {                
        'line_id':fields.many2one('transport.route', 'Line', ondelete='cascade', select=True),
        'supplier_id': fields.many2one('res.partner', 'Supplier'),
        'vehicle_id': fields.many2one('fleet.vehicle', 'Vehicle'),
        'transport_cost' : fields.float(string='Transport Cost'),
        'labor_cost': fields.float(string='Labor Cost'),
        'total_cost':fields.function(_total_value,string= 'Total Cost', digits=(16, 0),type='float', readonly=True),
        'git_day': fields.integer(string='GIT Days'),
        'truck_type': fields.many2one('truck.type', 'Truck Type'),
        }
