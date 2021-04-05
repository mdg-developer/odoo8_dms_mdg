from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import timedelta,datetime
import calendar

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
    
    def send_weekly_notification(self, cr, uid, partner_id=None, context=None): 
                
        day_name = calendar.day_name[datetime.today().weekday()]
        noti_day_obj = self.pool.get('notified.days').search(cr, uid, [('name', '=', day_name)])
        if noti_day_obj:
            noti_day = self.pool.get('notified.days').browse(cr, uid, noti_day_obj, context=context)
            if noti_day:  
                cr.execute("""select weekly_noti_id from weekly_noti_days_rel where day_id=%s""", (noti_day.id,))    
                day_data = cr.fetchall()
                if day_data:
                    for day in day_data:                
                        weekly_noti = self.pool.get('weekly.noti').browse(cr, uid, day[0], context=context)  
                        one_signal_values = {
                                                'partner_id': weekly_noti.partner_id.id,
                                                'contents': weekly_noti.message,
                                                'headings': "RB"
                                            }     
                        self.pool.get('one.signal.notification.messages').create(cr, uid, one_signal_values, context=context)
                