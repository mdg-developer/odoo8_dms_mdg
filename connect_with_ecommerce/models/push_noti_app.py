from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import timedelta,datetime
import calendar

class PushNotiApp(osv.osv):
    _name = "push.noti.app"
    
    _columns = {
               'name':fields.char(string='Name'),      
               'date':fields.datetime('Date'),         
            }
    
    _defaults = {
        'date': fields.datetime.now,
    } 
                