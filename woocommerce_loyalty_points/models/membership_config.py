from openerp.osv import fields, osv

class membership_configuration(osv.osv):
    
    _name = "membership.config"
    
    _columns = {
            'name':fields.char('Level'),  
            'points':fields.integer('Points'),          
            'start_date':fields.date('Start Date'),
            'end_date':fields.date('End Date'),           
    }