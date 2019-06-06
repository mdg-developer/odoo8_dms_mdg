from openerp.osv import fields, osv


class truck_type(osv.osv):
    _name = 'truck.type'
    _columns = {        
        'name': fields.char('Name'),
        'est_cbm': fields.float('CBM(Est.)'),
        'est_viss': fields.float('Viss(Est.)'),
    }

    
class product_template(osv.osv):
    _inherit = 'fleet.vehicle'
    
    _columns = {        
        '3pl': fields.boolean('3 PL'),
        'supplier_id': fields.many2one('res.partner', 'Supplier'),
        'branch_id': fields.many2one('res.branch', 'Branch'),
        'truck_type_id': fields.many2one('truck.type', 'Truck Type'),
        'weight_viss': fields.float('Max Weight Viss'),
        'vol_cbm': fields.float('Max Vol CBM'),
        'alert_weight_viss': fields.float('Balance Alert Weight Viss'),
        'alert_vol_cbm': fields.float('Balance Alert Vol CBM'),
    }
    
