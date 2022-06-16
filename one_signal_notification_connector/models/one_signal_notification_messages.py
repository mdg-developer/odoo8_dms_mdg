from openerp import api,fields, models, _
import requests
import json
import logging
import ast
_logger = logging.getLogger(__name__)


class OneSignalNotification(models.Model):
    _name = "one.signal.notification.messages"
    _rec_name = 'contents'
    _description = 'one signal notification messages'
    
    def _get_company(self):
        return self.env.user.company_id

    contents = fields.Char(string="Contents", required=True, help="Content display to end user")
    headings = fields.Char(string="Headings", required=False, help="Heading display to end user")
    partner_id = fields.Many2one('res.partner', string="Customer")
    app_id = fields.Many2one(comodel_name="one.signal.notification.apps", string="App", required=False,
                             help="Message send to the application")
    company_id = fields.Many2one(comodel_name="res.company", string="Company", required=False, default=_get_company)

    status = fields.Selection(string="Status", selection=[('draft', 'Draft'), ('sent', 'Sent'), ('fail', 'Failed'), ],
                              required=False, default="draft", help="Status of the notification")
    # Response from One Signal
    reason = fields.Text(string="Reason", required=False, help="Response of the Notification")
    external_id = fields.Char(string="One Signal External Id", required=False, )
    one_signal_notification_id = fields.Char(string="Notification Id", required=False, )
    recipients_count = fields.Integer(string="Recipients Count", required=False, )
    has_read = fields.Boolean('Has read?', default=False)
    woo_customer_id = fields.Char("Woo Customer Id", related='partner_id.woo_customer_id')
    
    def create(self, cursor, user, vals, context=None):       
        data={}
        user_obj = self.pool.get('res.users').browse(cursor, user, [user], context=context)
        search_condition = [("active", "=", True)]
        search_condition.append(("company_id", "=", user_obj.company_id.id))

        apps_object = self.pool.get('one.signal.notification.apps').search(cursor, user, search_condition, limit=1)[0]
        apps = self.pool.get('one.signal.notification.apps').browse(cursor, user, [apps_object], context=context)
        
        for app_record in apps:
            data['app_api_key'] = app_record.app_api_key
            data['app_id'] = app_record.app_id
        woo_user_ids =[]
        if vals['partner_id']:
            partner_obj = self.pool.get('res.partner').browse(cursor, user, vals['partner_id'], context=context)
            for partner in partner_obj:
                if partner.woo_customer_id:          
                    woo_id = partner.woo_customer_id.split("_")      
                    woo_user_ids.append(woo_id[1])
        data['include_external_user_ids'] = woo_user_ids
        data['contents'] = vals['contents']
        if vals['headings']:
            data['headings'] =  vals['headings']
        response = self.send_notification(data)
        response_json = response.json()
        if response.status_code == 200:
            vals['status'] = "sent"
            vals['reason'] = str(response.status_code) + " " + str(response.reason)

            vals['external_id'] = response_json.get('external_id', False) or False
            vals['one_signal_notification_id']  = response_json['id'] or False
            vals['recipients_count']  = response_json['recipients'] or False
            if 'errors' in response_json:
                vals['reason']  += " " + str(response_json['errors'])
            if 'warnings' in response_json:
                vals['reason'] += " " + str(response_json['warnings'])
        else:
            vals['status'] = "fail"
            vals['reason'] = str(response.status_code) + " " + str(response.reason) + " " + str(response_json['errors'])
            vals['external_id']  = False
            vals['one_signal_notification_id'] = False
            vals['recipients_count']  = False
            if 'warnings' in response_json:
                vals['reason']  += " " + str(response_json['warnings'])
                
        return super(OneSignalNotification, self).create(cursor, user, vals, context=context)

    
    def action_retry(self):
        self.status = "draft"

    @staticmethod
    def send_notification(data):
        header = {}
        response = False
        payload = {}
        headings={}
        messages={}
        external_user_id = data.get('include_external_user_ids')
        app_id = data.get('app_id', False) or False
        app_api_auth_key = data.get('app_api_key', False) or False
        if app_id and app_api_auth_key:
            header = {"Content-Type": "application/json; charset=utf-8",
                      "Authorization": "Basic %s" % app_api_auth_key}
            payload["app_id"] = app_id
            payload["include_external_user_ids"] = external_user_id
            #payload["include_player_ids"] = ['93ef2cbe-fc83-4733-bfeb-730a75ade297','df5ae148-ee4e-4bfe-9565-9eb7f4bf22de']
            if data.get("contents" or False) or False:
                messages["en"]=data.get("contents")
                payload['contents'] = messages 
            else:
                _logger.info('Please provide the "contents" '
                             'eg: {"en": "English Message", "es": "Spanish Message"} '
                             'in the Input Request to the send_notification() method')
            if data.get("headings" or False) or False:
                headings["en"]=data.get("headings")
                payload['headings'] = headings
            else:
                _logger.info('Please provide the "headings" '
                             'eg: {"en": "English Title", "es": "Spanish Title"} '
                             'in the Input Request to the send_notification() method')

        else:
            _logger.info('Please provide the "app_id" & "app_api_key" in the Input Request to the '
                         'send_notification() method')

        if header and payload:
            payload = json.dumps(payload)            
            response = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=payload)
            _logger.info("Response: %s" % str(response.status_code)+" "+str(response.reason))
            _logger.info("Response Json: %s" % str(response.json()))

            # return str(response.status_code)+" "+str(response.reason)

        return response
