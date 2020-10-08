from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import timedelta,datetime
import calendar

class AppVersion(osv.osv):
    _name = "app.version"
    
    _columns = {
               'name':fields.char(string='App Version Name'),               
            }
                