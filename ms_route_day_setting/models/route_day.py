from openerp.osv import fields, osv

class route_day(osv.osv):
    _name = 'route.day'
    
    _columns = {
                'name': fields.char('Day'),   
                'sequence':fields.integer('Sequence'),              
               }