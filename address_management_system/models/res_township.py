'''
Created on Jan 6, 2016

@author: Administrator
'''
from openerp.osv import fields, osv

class res_township(osv.osv):
    
    _name = 'res.township'

    _columns = {
                
    'city' : fields.many2one('res.city', 'City', ondelete='restrict',required=True),
    'name': fields.char('Township Name', required=True),
    'code': fields.char('Township Code', size=4, help='The township code in max. three chars.', required=True)
               }
    _sql_constraints = [
        ('name_uniq', 'unique (name)',
            'The name of the township must be unique !'),
        ('code_uniq', 'unique (code)',
            'The code of the township must be unique !')
    ]
    

res_township    
    
        