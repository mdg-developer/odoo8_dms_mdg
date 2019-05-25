from openerp.osv import fields, osv

class product_template(osv.osv):
    _inherit = 'fleet.vehicle'
    
    _columns = {        
        '3pl': fields.boolean('3 PL'),
        'supplier_id': fields.many2one('res.partner', 'Supplier'),
        'weight_viss': fields.boolean('Max Weight Viss'),
        'vol_cbm': fields.boolean('Max Vol CBM'),
        'alert_weight_viss': fields.boolean('Balance Alert Weight Viss'),
        'alert_vol_cbm': fields.boolean('Balance Alert Vol CBM'),
    }
    
