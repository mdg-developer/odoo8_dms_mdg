'''
Created on Jan 21, 2016

@author: NSM.7thcomputing
'''
from openerp.osv import fields, osv

class branch_setup(osv.osv):
    _name = 'branch'
    _columns = {
                    'name': fields.char('Branch Name', required=True),
                    'branch_code': fields.char('Branch Code', required=True),    
                    'address': fields.text('Address'),  
                    'active': fields.boolean('Active')  ,
                    'res_company_id' : fields.many2one('res.company', 'company')            
                }
    _sql_constraints = [('Branch_code_uniq', 'unique(branch_code)',
                                     'Branch Code should not be same to others!')]
    
    _defaults = {
        'active': True,
 
    }
branch_setup()
