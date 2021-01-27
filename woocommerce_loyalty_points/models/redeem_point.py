from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import timedelta,datetime
import calendar

class RedeemPoint(osv.osv):
    _name = "redeem.point"
    
    _columns = {
               'name':fields.char(string='Name'),     
               'description':fields.char(string='Description'),    
               'point':fields.float('Points'),          
               'start_date':fields.date('Start Date'),
               'end_date':fields.date('End Date'),   
               'state': fields.selection([('draft', 'Draft'),('approved', 'Approved')], 'Status', default='draft'),                 
            }
    
    def approve(self, cr, uid, ids, context=None):
        
        return self.write(cr, uid, ids, {'state':'approved' })   
    