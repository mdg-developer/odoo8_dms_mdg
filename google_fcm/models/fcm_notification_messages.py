from openerp import api,fields, models, _
import requests
import json
import logging
import ast
from pyfcm import FCMNotification

class FCMNotificationMessages(models.Model):

    _name = "fcm.notification.messages"
    _description = 'one signal notification messages'

    partner_id = fields.Many2one(comodel_name="res.partner", string="Customer")
    topic_name = fields.Char(string="Topic Name")
    message_title = fields.Char(string="Message Title")
    message_body = fields.Char(string="Message Body")
    fcm_message_id = fields.Char(string="Message ID")
    devie_token = fields.Char(string="Device Token")
    reason = fields.Text(string="Reason")
    woo_customer_id = fields.Char("Woo Customer Id")
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
        response = self.send_notification(cr,uid,data)
        response_json = response.json()
        if response == 200:
            if response_json['success'] == 1:
                vals['state'] = "sent"
        else:
            vals['state'] = "fail"
            if 'results' in response_json:
                vals['reason'] += " " + str(response_json['results'])

        return super(FCMNotificationMessages, self).create(cr, uid, vals, context=context)

    def send_notification(self, cr, uid, data, context=None):
        fcm_api_key = self.pool.get('ir.config_parameter').get_param(cr, uid, 'fcm_api_key', default=False, context=context)
        push_service = FCMNotification(api_key=fcm_api_key)
        title = data.message_title
        body = data.message_body
        tag = data.reason
        device_token = data.device_token
        result = {}
        result = push_service.notify_single_device(registration_id=device_token,message_title= title, message_body= body, tag=tag)
        return result