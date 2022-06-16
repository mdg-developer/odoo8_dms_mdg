from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import timedelta,datetime
import calendar
from pyfcm import FCMNotification

class AppVersion(osv.osv):
    _name = "app.version"
    
    _columns = {
               'name':fields.char(string='App Version Name'), 
               'play_store_version':fields.char(string='Play Store Version Name'), 
               'state':fields.selection([('draft', 'Draft'), ('confirm', 'Confirmed')], 'Status'),              
            }
            
    _defaults = {
        'state': 'draft',
    }   
        
    def notify_app(self, cr, uid, ids, context=None):
        
        fcm_api_key = self.pool.get('ir.config_parameter').get_param(cr, uid, 'retail_fcm_api_key', default=False, context=context)
        if fcm_api_key:
            push_service = FCMNotification(api_key=fcm_api_key)
            result = push_service.notify_topic_subscribers(topic_name="app_changes", message_title="Burmart", message_body="Your app is out of date! Please go and download new app in play store!")
            self.write(cr, uid, ids, {'state':'confirm'}, context=None)
        return True 
    