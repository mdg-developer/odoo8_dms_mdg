'''
Created on Jan 21, 2016

@author: NSM.7thcomputing
'''
from openerp.osv import fields, osv

class branch_setup(osv.osv):
    _name = 'sale.branch'
    _columns = {
                    'name': fields.char('Branch Name', required=True),
                    'branch_code': fields.char('Branch Code', required=True),                 
                }
    _sql_constraints = [('Branch_code_uniq', 'unique(branch_code)',
                                     'Branch Code should not be same to others!')]
branch_setup()
