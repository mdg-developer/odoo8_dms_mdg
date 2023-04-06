from openerp import api,fields, models, _
import requests
import json
import logging
import ast
from pyfcm import FCMNotification

_logger = logging.getLogger(__name__)

class FCMNotificationMessages(models.Model):

    _name = "fcm.notification.messages"
    _rec_name = "title"
    _description = 'one signal notification messages'

    partner_id = fields.Many2one(comodel_name="res.partner", string="Customer")
    title = fields.Char(string="Message Title")
    body = fields.Char(string="Message Body")
    device_token = fields.Char(string="Device Token")
    reason = fields.Text(string="Reason")
    woo_customer_id = fields.Char("Woo Customer Id")
    has_read = fields.Boolean('Has read?', default=False)
    state = fields.Selection([
        ('draft', 'Not Send'),
        ('send', 'Send'),
        ('failed', 'Failed'),
    ], string = "State" , default = "draft", readonly=True)

    def create(self, cr, uid, vals, context=None):
        data = {}
        woo_customer_id = None
        if vals['partner_id']:
            partner_obj = self.pool.get('res.partner').browse(cr, uid, vals['partner_id'], context=context)
            for partner in partner_obj:
                if partner.woo_customer_id:
                    woo_customer_id = partner.woo_customer_id
                    vals['woo_customer_id'] = woo_customer_id
        data['title'] = vals['title']
        data['body'] = vals['body']
        data['device_token'] = vals['device_token']
        response = self.send_notification(cr,uid,data)
        if response:
            response_json = response.json()
            if response_json['results'][0]:
                vals['reason'] = response_json['results'][0]
            if response.status_code == 200:
                if response_json['success'] == 1:
                    vals['state'] = "send"
                else:
                    vals['state'] = "failed"
        else:
            vals['state'] = "failed"

        return super(FCMNotificationMessages, self).create(cr, uid, vals, context=context)

    def send_notification(self, cr, uid, data, context=None):
        result = {}
        header = {}
        payload = {}
        fcm_api_key = self.pool.get('ir.config_parameter').get_param(cr, uid, 'fcm_api_key', default=False,
                                                                     context=context)
        header = {"Content-Type": "application/json", "Authorization": "key=%s" % fcm_api_key}
        if data:
            title = data['title'] or None
            body = data['body'] or None
            device_token = data['device_token'] or None
            payload['to'] = device_token
            payload['notification'] = {}
            payload['notification'].update({'title': title})
            payload['notification'].update({'body': body})
            payload['notification'].update({'device_token': device_token})
        if header and payload:
            payload = json.dumps(payload)
            result = requests.post("https://fcm.googleapis.com/fcm/send", headers=header, data=payload)
            _logger.info('----------Your message is delivered--------- ')
        return result

    def get_device_token(self, cr, uid, partner_id, context=None):
        device_token = ""
        if partner_id:
            partner_obj = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
            for partner in partner_obj:
                if partner.woo_customer_id:
                    token_value = self.pool.get('fcm.devicetoken').search(cr, uid, [
                        ('woo_customer_id', '=', partner.woo_customer_id)], context=context)
        if token_value:
            token_data = self.pool.get('fcm.devicetoken').browse(cr, uid, token_value, context=context)
            device_token = token_data.device_token
            # woo_customer_id = str(partner.woo_customer_id).replace('1_','')
        # if woo_customer_id:
        #     response = requests.get("https://www.burmart.com/wp-json/firebasedatas/v3/searchtoken/%s" % woo_customer_id)
        # if response.status_code == 200:
        #     response_json = response.json()
        #     if response_json:
        #         device_token = response_json[0].get('token', '')

        return device_token