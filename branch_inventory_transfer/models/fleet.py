from openerp.osv import fields, osv
#===============================================================================
# from validators.length import length
#===============================================================================


class truck_type(osv.osv):
    _name = 'truck.type'
    _columns = {        
        'name': fields.char('Name'),
        'est_cbm': fields.float('CBM(Max.Est)'),
        'est_viss': fields.float('Viss(Max.Est)'),
        'order_cbm': fields.float('CBM(Min.Order)'),
        'order_viss': fields.float('Viss(Min.Order)'),
        
    }

    
class fleet_vehicle(osv.osv):
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
        'length': fields.float('Box Length(Meter)'),
        'width': fields.float('Box Width(Meter)'),
        'height': fields.float('Box Height(Meter)'),
        'cbm': fields.float('Box CBM(Meter)'),
        
        'engine': fields.char('Engine'),
        'displacement_id': fields.float('Displacement(CC)'),
        'gvw_id': fields.float('GVW(kg)'),
        'payload_id': fields.float('Payload(kg)'),
        'gvw_viss': fields.float('GVW(viss)'),
        'payload_viss': fields.float('Payload(viss)'),
        'gear_box': fields.char('Gear Box'),
        'clutch': fields.char('Clutch'),
        'steering': fields.char('Steering'),
        'brake': fields.char('Brake'),
        'suspension': fields.char('Suspension'),
        'fuel_tank_litre': fields.float('Fuel Tank Capacity(litre)'),
        'fuel_tank_gal': fields.float('Fuel Tank Capacity(gal)'),
        'type_size': fields.char('Tyre Size'),
        'warranty': fields.char('Warranty'),
        'image': fields.binary("Images", help="This field holds the image used as logo for the brand, limited to 1024x1024px."),
        'image2': fields.binary("Images", help="This field holds the image used as logo for the brand, limited to 1024x1024px."),
        'image3': fields.binary("Images", help="This field holds the image used as logo for the brand, limited to 1024x1024px."),
        'image4': fields.binary("Images", help="This field holds the image used as logo for the brand, limited to 1024x1024px."),
        'image5': fields.binary("Images", help="This field holds the image used as logo for the brand, limited to 1024x1024px."),
        'image6': fields.binary("Images", help="This field holds the image used as logo for the brand, limited to 1024x1024px."),
        'wheel_tax': fields.binary("Wheel Tax", help="This field holds the image used as logo for the brand, limited to 1024x1024px."),
        
        'fleet_manager': fields.char('Fleet Manager'),
        'fleet_auditor': fields.char('Fleet Auditor'),
        'average_monthly_mileage': fields.float('Average Monthly Mileage'),
        'average_daily_paylood': fields.float('Average Daily Payload (viss)'),
        'average_fuel_consumption': fields.float('Average Fuel Consumption(gal)'),
        
        'office_vehicle': fields.boolean('Office Vehicle'),
        'sale_vehicle': fields.boolean('Sale Vehicle'),
        'logistic_vehicle': fields.boolean('Logistic Vehicle'),
        
        
           
    }
         

      
    def onchange_payload_calculate(self, cr, uid, ids, payload_id, payload_viss, context=None):
        payload_id = float(payload_id)
        payload_viss = float(payload_viss)
        return {'value' : {'payload_viss' : round(payload_id / 1.63293), }}
    
    def onchange_fuel_tank_capacity_calculate(self, cr, uid, ids, fuel_tank_litre, fuel_tank_gal , context=None):
        fuel_tank_litre = float(fuel_tank_litre)
        fuel_tank_gal = float(fuel_tank_gal)
        return {'value' : {'fuel_tank_gal' : round(fuel_tank_litre / 4.54609), }}
        
    def onchange_gvw_calculate(self, cr, uid, ids, gvw_id, gvw_viss, context=None):
        gvw_id = float(gvw_id)
        gvw_viss = float(gvw_viss)
        return {'value' : {'gvw_viss' : round(gvw_id / 1.63293), }}
            
    def onchange_box_calculation(self, cr, uid, ids, length, width, height, cbm, context=None):
        length = float(length)
        width = float(width)
        height = float(height)
        cbm = float(cbm)
        
        return {'value' : {'cbm' : round(length * width * height), }}
    
fleet_vehicle()    
class Partner(osv.osv):
    _inherit = 'res.partner'
       
    _columns = {        
        'transporter': fields.boolean('Transporter',default=False),
     }
