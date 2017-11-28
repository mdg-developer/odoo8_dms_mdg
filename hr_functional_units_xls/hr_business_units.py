from openerp.osv import fields, osv


class hr_business_units(osv.osv):
    _name = 'hr.business.units'
    _description = 'HR Business Units'
    _columns = {
       'name':fields.char('Business Units'),
       'manager_id': fields.many2one('hr.employee', 'Manager'),
       'company_id': fields.many2one('res.company', 'Company'),
       'parent_id': fields.many2one('hr.business.units', 'Parent Business Units'),
        
    } 
    
    
