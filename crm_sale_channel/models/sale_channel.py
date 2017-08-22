'''
Created on Jan 21, 2016

@author: NSM.7thcomputing
'''
from openerp.osv import fields, osv
  
class sale_channel(osv.osv):
    _name = 'sale.channel'
    _columns = {              
                'name': fields.char('Channel Name', required=True),
                'code':fields.char('Channel Code', required=True),
                'active':fields.boolean('Active')      
               }
    _default = {
              'active':True
              }
    _sql_constraints = [('Channel_code_uniq', 'unique(code)',
                                     'Channel Code should not be same to others!')]
sale_channel()
