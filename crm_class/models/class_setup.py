'''
Created on Jan 21, 2016

@author: NSM.7thcomputing
'''
from openerp.osv import fields, osv

class class_setup(osv.osv):
    _name = 'sale.class'
    _columns = {
                    'name': fields.char('Class Name', required=True),
                    'class_code': fields.char('Class Code', required=True ),                    
                }
    _sql_constraints = [('Class_code_uniq', 'unique(class_code)',
                                     'Class Code should not be same to others!')]
class_setup()
