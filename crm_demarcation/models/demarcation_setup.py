'''
Created on Jan 21, 2016

@author: NSM.7thcomputing
'''
from openerp.osv import fields, osv

class demarcation_setup(osv.osv):
    _name = 'sale.demarcation'
    _columns = {
                    'name': fields.char('Code', required=True),
                    'demarcation_desc': fields.char('Description', required=True),
                }
    _sql_constraints = [('Demarcation_code_uniq', 'unique(name)',
                                     'Demarcation Code should not be same to others!')]
demarcation_setup()
 
