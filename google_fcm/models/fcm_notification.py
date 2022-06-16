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
            ('send', 'Send'),        
            ('failed', 'Failed'),       
        ], 'State', readonly=True),
    }
    
    _defaults = {
            'state': 'draft',
    }
    
    #def init(self, cr):
       # cr.execute("insert into ir_config_parameter(key,value) values(%s,%s)", ('fcm_api_key', 'AIzaSyAQn9RESXdjzswVZpzY8aUzxnMBTki25uw',))
        
       
    def send_msg(self, cr, uid, ids, context=None):
        fcm_api_key = self.pool.get('ir.config_parameter').get_param(cr, uid, 'fcm_api_key', default=False, context=context)
        push_service = FCMNotification(api_key=fcm_api_key)
        data = self.browse(cr, uid, ids)[0]
        crm_obj = self.pool.get('crm.case.section')
        tablet_obj = self.pool.get('tablets.information')
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
        try:
            registration_ids=[]
            for data in result:
                sale_team = crm_obj.browse(cr, uid, data, context)
                tablet_ids = tablet_obj.search(cr,uid,[('sale_team_id','=',sale_team.id)])
                for tablet_id in tablet_ids:
                    tablet_data = tablet_obj.browse(cr,uid,tablet_id,context)
                    if tablet_data.token:
                        registration_ids.append(tablet_data.token);
                #result=push_service.notify_topic_subscribers(topic_name=sale_team.name, message_body=message, message_title= msg_title, tag=msg_tag)
                
            result = push_service.notify_multiple_devices(registration_ids=registration_ids,  message_body=message, message_title= msg_title, tag=msg_tag)
            print "registiration:", registration_ids
            print result;
            self.write(cr, uid, ids, {'state': 'send'}, context=context)
        except Exception, e:
            self.write(cr, uid, ids, {'state': 'failed'},context=context)
        return True   
    
fcm_notification()   

    
