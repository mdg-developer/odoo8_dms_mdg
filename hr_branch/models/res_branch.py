'''
Created on Jan 21, 2016

@author: NSM.7thcomputing
'''
from openerp.osv import fields, osv


class branch(osv.osv):
    _name = 'res.branch'
    _columns = {
                    'name': fields.char('Branch Name', required=True),
                    'branch_code': fields.char('Branch Code', required=True),
                                        'name': fields.char('Branch Name', required=True),
                    'address': fields.text('Address'),
                    'active': fields.boolean('Active')  ,
                    'branch_region':fields.char('Branch Region'),
                    'res_company_id' : fields.many2one('res.company', 'Company'),
               
                }

    _sql_constraints = [('Branch_code_uniq', 'unique(branch_code)',
    
                                     'Branch Code should not be same to others!')]
    
    _defaults = {
        'active': True,
 
    }


branch()
