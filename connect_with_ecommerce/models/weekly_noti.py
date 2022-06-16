from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import timedelta,datetime
import calendar
import logging

class NotifiedDays(osv.osv):
    _name = "notified.days"
    
    _columns = {
               'name':fields.char(string='Name'),               
            }

class WeeklyNotification(osv.osv):
    _name = "weekly.noti"
    
    _columns = {
               'state_id':fields.many2one('res.country.state', 'State'),
               'city_id':fields.many2one('res.city', 'City'),
               'township_ids': fields.many2many('res.township', 'weekly_noti_township_rel', 'weekly_noti_id', 'township_id', 'Township'),
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
                        domain = []
                        if weekly_noti.state_id:                
                            domain += [('state_id', '=', weekly_noti.state_id.id)]
                        if weekly_noti.city_id:                
                            domain += [('city', '=', weekly_noti.city_id.id)]
                        if weekly_noti.township_ids:  
                            domain += [('township', 'in', weekly_noti.township_ids.ids)] 
                        domain += [('woo_customer_id', '!=', False),('type', '!=', 'delivery')] 
                        partner_obj = self.pool.get('res.partner').search(cr, uid, domain)
                        partner_ids = self.pool.get('res.partner').browse(cr, uid, partner_obj, context=context)
                        for partner in partner_ids:
                            one_signal_values = {
                                                    'partner_id': partner.id,
                                                    'contents': weekly_noti.message,
                                                    'headings': "Burmart"
                                                }     
                            self.pool.get('one.signal.notification.messages').create(cr, uid, one_signal_values, context=context)
                