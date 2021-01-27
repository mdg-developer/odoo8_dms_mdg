
'''
Created on Jan 22, 2016

@author: 7th Computing
'''

from openerp.osv import fields, osv

class sale_order(osv.osv):
    _inherit = "sale.order"     
    _columns = {
               'credit_to_cash':fields.boolean('Credit To Cash' ,readonly=True),
               }
    

