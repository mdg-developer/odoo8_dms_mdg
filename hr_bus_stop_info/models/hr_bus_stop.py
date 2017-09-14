from openerp.osv import fields, osv
from openerp.tools.translate import _

class hr_bus_stop(osv.osv):

    _name = "hr.bus.stop"    
        
    _columns = {
        'name': fields.char('Name', required=True),        
        
    }    
    
hr_bus_stop()


class hr_bus(osv.osv):

    _name = "hr.bus"    
        
    _columns = {
        'name': fields.char('Name', required=True),        
        
    }    
    
hr_bus_stop()     

class hr_employee(osv.osv):

    _inherit = "hr.employee"
    _columns = {
        'bus_stop_id': fields.many2one('hr.bus.stop', 'Bus Stop',required=True),
        'bus_id': fields.many2one('hr.bus','Bus No'),


    }
hr_employee()