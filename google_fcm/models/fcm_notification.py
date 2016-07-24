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
        'sales_team_id': fields.many2many('crm.case.section', string='Sales Team'),  # table name is crm_case_section_fcm_notification_rel
        'state': fields.selection([
            ('draft', 'Not Send'),
            ('send', 'Send')         
        ], 'State', readonly=True),
    }
    
    _defaults = {
            'state': 'draft',
    }
    
    def init(self, cr):
        cr.execute("insert into ir_config_parameter(key,value) values(%s,%s)", ('fcm_api_key', 'AIzaSyAQn9RESXdjzswVZpzY8aUzxnMBTki25uw',))
        
       
    def send_msg(self, cr, uid, ids, context=None):
        fcm_api_key = self.pool.get('ir.config_parameter').get_param(cr, uid, 'fcm_api_key', default=False, context=context)
        push_service = FCMNotification(api_key=fcm_api_key)
        data = self.browse(cr, uid, ids)[0]
        crm_obj = self.pool.get('crm.case.section')
        title = data.title
        body = data.body
        tag = data.reason
        result = {}
        msg_title = title
        message = body
        msg_tag = tag
    
        if ids:
            cr.execute(""" select crm_case_section_id from crm_case_section_fcm_notification_rel where fcm_notification_id =%s """, (ids[0],))
            data = cr.fetchall()
            if data:
                result = data
        for data in result:
            sale_team = crm_obj.browse(cr, uid, data, context)
            result=push_service.notify_topic_subscribers(topic_name=sale_team.name, message_body=message, message_title= msg_title, tag=msg_tag)
            print result;
        self.write(cr, uid, ids, {'state': 'send'}, context=context)
        return True   
    
fcm_notification()   

    
