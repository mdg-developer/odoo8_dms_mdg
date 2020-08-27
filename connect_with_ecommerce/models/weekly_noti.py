from openerp.osv import fields, osv
from openerp.tools.translate import _

class NotifiedDays(osv.osv):
    _name = "notified.days"
    
    _columns = {
               'name':fields.char(string='Name'),               
            }

class WeeklyNotification(osv.osv):
    _name = "weekly.noti"
    
    _columns = {
               'partner_id':fields.many2one('res.partner', 'Customer'),
               'notified_days_ids': fields.many2many('notified.days', 'weekly_noti_days_rel', 'weekly_noti_id', 'day_id', 'Notified Days'),
               'message':fields.text(string='Message'), 
            }
