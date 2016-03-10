'''
Created on Jan 6, 2016

@author: 7th Computing
'''
from openerp.osv import fields, osv

class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {               
             
            'city':fields.many2one('res.city','City'),
            'township':fields.many2one('res.township','Township'),
                                  
    }   
    
res_partner()

    