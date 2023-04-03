from openerp import api,fields, models, _
import requests
import json
import logging
import ast
from pyfcm import FCMNotification

_logger = logging.getLogger(__name__)

class FCMDeviceToken(models.Model):

    _name = "fcm.devicetoken"
    _description = 'Fcm Device Token'

    name = fields.Char('Name')
    partner_id = fields.Many2one(relation='res.partner',string='Partner')
    woo_customer_id = fields.Char('Woo Customer ID')
    device_token = fields.Char('Device Token')