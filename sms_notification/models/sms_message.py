# -*- coding: utf-8 -*-
##########################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2017-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
##########################################################################

from openerp import models, fields, api, _
from openerp import SUPERUSER_ID
import re
import operator
from openerp.exceptions import except_orm, Warning, RedirectWarning
import requests
import json
import logging
import datetime
class SmsMessage(models.Model):
    """SMS message for every mobile number of sms."""

    _name = "sms.message"    
    _description = "Model for sms history."
    
    status = fields.Selection([
        ('success', 'Success'),
        ('fail', 'Fail'),        
    ], string="Status")
    partner_id = fields.Many2one("res.partner", string="Customer")
    phone = fields.Char(string="Phone")
    message = fields.Text(string="Message")
    error_log = fields.Text(string="Error Log")
    name = fields.Char(string="Reference")
    
    def create(self, cursor, user, vals, context=None):     
        
        try: 
            headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}            
            sms_user= 'mdgpro'
            password= 'fcdaa533-e23d-4f9e-8480-416454b2dfc2'
            url='https://mpg-ids.mytel.com.mm/auth/realms/eis/protocol/openid-connect/token'
            payload = {'grant_type': 'client_credentials'}
            response = requests.post(url,headers=headers,auth=(sms_user, password), data=payload, verify=False)
            if response.status_code == 200:                
                content = json.loads(response.content)
                token = content['access_token'] 
                header = {'Content-Type': 'application/json',
                          'Authorization': 'Bearer {0}'.format(token)}                    
                sms_url = 'https://mytelapigw.mytel.com.mm/msg-service/v1.3/smsmt/sent'
                sms_payload = {
                               "source":"MDG",
                               "dest":vals['phone'],
                               "content":vals['message']
                        }                 
                response = requests.post(sms_url,  json = sms_payload, headers = header,verify=False)                
                if response.status_code == 200:
                    vals['status']='success'                    
                else:
                    vals['status']='fail'            
            
        except Exception as e:         
            error_msg = 'Error Message: %s' % (e) 
            logging.error(error_msg)  
            vals['status']='fail' 
            vals['errorlog']=error_msg    
               
        return super(SmsMessage, self).create(cursor, user, vals, context=context)
    
    def retry_sms(self, cr, uid, context=None):    
        
        message_obj = self.pool.get('sms.message').search(cr, uid, ['|', ('status', '=', 'fail'),('status', '=', False)])
        if message_obj:
            message_data = self.browse(cr, uid, message_obj, context=context)         
            for message in message_data:       
                try: 
                    headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}            
                    sms_user= 'mdgpro'
                    password= 'fcdaa533-e23d-4f9e-8480-416454b2dfc2'
                    url='https://mpg-ids.mytel.com.mm/auth/realms/eis/protocol/openid-connect/token'
                    payload = {'grant_type': 'client_credentials'}
                    response = requests.post(url,headers=headers,auth=(sms_user, password), data=payload, verify=False)
                    if response.status_code == 200:                
                        content = json.loads(response.content)
                        token = content['access_token'] 
                        header = {'Content-Type': 'application/json',
                                  'Authorization': 'Bearer {0}'.format(token)}                    
                        sms_url = 'https://mytelapigw.mytel.com.mm/msg-service/v1.3/smsmt/sent'
                        sms_payload = {
                                       "source":"MDG",
                                       "dest":message.phone,
                                       "content":message.message,
                                }                 
                        response = requests.post(sms_url,  json = sms_payload, headers = header,verify=False)                
                        if response.status_code == 200:
                            message.write({'status':'success'})                  
                        else:
                            message.write({'status':'fail'})            
                    
                except Exception as e:         
                    error_msg = 'Error Message: %s' % (e) 
                    logging.error(error_msg)
                    message.write({'status':'fail'})  
                    message.write({'errorlog':error_msg})                    
