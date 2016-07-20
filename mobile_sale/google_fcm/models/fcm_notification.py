from openerp.osv import fields, osv
from pyfcm import FCMNotification

class fcm_notification(osv.osv):

    _name = "fcm.notification"
    _rec_name = "reason"
    
    _columns = {
        'reason': fields.char('Notification Reason'),
        'date' : fields.datetime('Date'),
        'title' : fields.char('Message Title'),
        'body': fields.text('Message Body'),
        'sales_team_id': fields.many2many('crm.case.section', string='Sales Team'),
        'state': fields.selection([
            ('draft', 'Not Send'),
            ('send', 'Send')         
        ], 'State', readonly=True),
    }
    
    _defaults = {
            'state': 'draft',
    }
    
    def init(self, cr):
        
        cr.execute("insert into ir_config_parameter(key,value) values(%s,%s)", ('fcm_api_key','AIzaSyAtKOmIyDj0O0jT7sc7wKoPhniVO_f90dU',))
       
    def send_msg(self, cr, uid, ids, context=None):

        data = self.browse(cr, uid, ids)[0]
        title = data.title
        body = data.body
        sales_team = data.sales_team_id
        fcm_api_key=self.pool.get('ir.config_parameter').get_param(cr, uid, 'fcm_api_key', default=False, context=context)
        push_service = FCMNotification(api_key=fcm_api_key)
        message_title = title
        message_body = body
        result = push_service.notify_topic_subscribers(topic_name="news", message_title=message_title, message_body=message_body)
        print result
        self.write(cr, uid, ids, {'state': 'send'}, context=context)
        return True   
    
fcm_notification()   

    
