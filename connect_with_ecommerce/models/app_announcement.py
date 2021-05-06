from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import timedelta,datetime
import calendar
# from pyfcm import FCMNotification

class AppAnnouncement(osv.osv):
    _name = "app.announcement"
    
    _columns = {
               'image': fields.binary("Image"),
               'from_date': fields.date('From Date'),              
               'to_date': fields.date('To Date'),                   
            }
    