'''
Created on Jan 6, 2016

@author: 7th Computing
'''
from openerp.osv import fields, osv

class res_city(osv.osv):
    _name = 'res.city'
    _inherit = 'res.country'    
    _columns = {
    
    'state_id' : fields.many2one('res.country.state', 'Division/State', ondelete='restrict'),
    'name': fields.char('City Name', size=128, required=True),
    'code': fields.char('City Code', size=3, help='The city code in max. three chars.', required=True),
                }
    
    _sql_constraints = [
        ('name_uniq', 'unique (name)',
            'The name of the city must be unique !'),
        ('code_uniq', 'unique (code)',
            'The code of the city must be unique !')
    ]
res_city()   