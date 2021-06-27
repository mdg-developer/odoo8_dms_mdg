from openerp import models, fields, api, _
from openerp import SUPERUSER_ID
import re
import operator
from openerp.exceptions import except_orm, Warning, RedirectWarning
import requests
import json
import logging
import datetime
from oauthlib.oauth2 import MobileApplicationClient
from requests_oauthlib import OAuth2Session
from urlparse import urlparse
from urlparse import parse_qs
from requests.structures import CaseInsensitiveDict

_logger = logging.getLogger(__name__)

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
    text_message = fields.Text(string="Text Message")
    error_log = fields.Text(string="Error Log")
    name = fields.Char(string="Reference")
    
    def create(self, cursor, user, vals, context=None):     
        
        try: 
            consumer_key = self.pool.get('ir.config_parameter').get_param(cursor, user, 'telenor_consumer_key')
            consumer_secret = self.pool.get('ir.config_parameter').get_param(cursor, user, 'telenor_consumer_secret')
            auth_url = 'https://prod-apigw.mytelenor.com.mm/oauth/v1/userAuthorize?client_id=%s&response_type=code&scope=READ'%(consumer_key)
            scopes = ['READ']
            oauth = OAuth2Session(client=MobileApplicationClient(client_id=consumer_key), scope=scopes)
            authorization_url, state = oauth.authorization_url(auth_url)
            response = oauth.get(authorization_url)
            response_url = response.url
            parsed = urlparse(response_url)
            code = parse_qs(parsed.query)['code']
            auth_code = code[0]
            
            token_url = "https://prod-apigw.mytelenor.com.mm/oauth/v1/token"
            token_headers = CaseInsensitiveDict()
            token_headers["Content-Type"] = "application/x-www-form-urlencoded"
            token_data = "grant_type=authorization_code&client_id=%s&client_secret=%s&expires_in=86400&code=%s&redirect_uri=https://cms.rbdmyanmar.com/oauth2/callback" %(consumer_key,consumer_secret,auth_code,)
            resp = requests.post(token_url, headers=token_headers, data=token_data)
            if resp.status_code == 200:
                result = resp.json()
                access_token = result['accessToken']
                        
            sms_url = "https://prod-apigw.mytelenor.com.mm/v3/mm/en/communicationMessage/send"
            sms_headers = CaseInsensitiveDict()
            sms_headers["Authorization"] = "Bearer " + access_token
            sms_headers["Content-Type"] = "application/json"
            
            sms_data = """           
            {
               "type": "MULTILINGUAL",
               "content": "%s",
               "characteristic": [         
                   {
                     "name": "Udhi",
                     "value": "1"
                  },
                  {
                     "name": "UserName",
                     "value": "B2BRBDCo"
                  },
                  {
                     "name": "Password",
                     "value": "B2BRBD"
                  }
               ],
               "sender": {
                  "@type": "5",
                  "name": "RBD MYANMAR"
               },
               "receiver": [
                  {
                     "@type": "1",
                     "phoneNumber": "%s"
                  }
               ]
            }
            """ %(vals.get('message'),vals.get('phone'),)
            resp_sms = requests.post(sms_url, headers=sms_headers, data=sms_data)
            if resp_sms.status_code in [200,201]:
                vals['status']='success'                    
            else:
                vals['status']='fail'             
            
        except Exception as e:         
            error_msg = 'Error Message: %s' % (e) 
            logging.error(error_msg)  
            vals['status']='fail' 
            vals['errorlog']=error_msg    
               
        return super(SmsMessage, self).create(cursor, user, vals, context=context)     
    
    def retry_sms(self, cursor, user, context=None):    
        
        message_obj = self.pool.get('sms.message').search(cursor, user, ['|', ('status', '=', 'fail'),('status', '=', False)])
        if message_obj:
            message_data = self.browse(cursor, user, message_obj, context=context)         
            for message in message_data:
                try: 
                    consumer_key = self.pool.get('ir.config_parameter').get_param(cursor, user, 'telenor_consumer_key')
                    consumer_secret = self.pool.get('ir.config_parameter').get_param(cursor, user, 'telenor_consumer_secret')
                    auth_url = 'https://prod-apigw.mytelenor.com.mm/oauth/v1/userAuthorize?client_id=%s&response_type=code&scope=READ'%(consumer_key)
                    scopes = ['READ']
                    oauth = OAuth2Session(client=MobileApplicationClient(client_id=consumer_key), scope=scopes)
                    authorization_url, state = oauth.authorization_url(auth_url)
                    response = oauth.get(authorization_url)
                    response_url = response.url
                    parsed = urlparse(response_url)
                    code = parse_qs(parsed.query)['code']
                    auth_code = code[0]
                    
                    token_url = "https://prod-apigw.mytelenor.com.mm/oauth/v1/token"
                    token_headers = CaseInsensitiveDict()
                    token_headers["Content-Type"] = "application/x-www-form-urlencoded"
                    token_data = "grant_type=authorization_code&client_id=%s&client_secret=%s&expires_in=86400&code=%s&redirect_uri=https://cms.rbdmyanmar.com/oauth2/callback" %(consumer_key,consumer_secret,auth_code,)
                    resp = requests.post(token_url, headers=token_headers, data=token_data)
                    if resp.status_code == 200:
                        result = resp.json()
                        access_token = result['accessToken']
                                
                    sms_url = "https://prod-apigw.mytelenor.com.mm/v3/mm/en/communicationMessage/send"
                    sms_headers = CaseInsensitiveDict()
                    sms_headers["Authorization"] = "Bearer " + access_token
                    sms_headers["Content-Type"] = "application/json"
                    
                    sms_data = """           
                    {
                       "type": "MULTILINGUAL",
                       "content": "%s",
                       "characteristic": [         
                           {
                             "name": "Udhi",
                             "value": "1"
                          },
                          {
                             "name": "UserName",
                             "value": "B2BRBDCo"
                          },
                          {
                             "name": "Password",
                             "value": "B2BRBD"
                          }
                       ],
                       "sender": {
                          "@type": "5",
                          "name": "RBD MYANMAR"
                       },
                       "receiver": [
                          {
                             "@type": "1",
                             "phoneNumber": "%s"
                          }
                       ]
                    }
                    """ %(message.message,message.phone,)                    
                    resp_sms = requests.post(sms_url, headers=sms_headers, data=sms_data)                    
                    if resp_sms.status_code in [200,201]:
                        message.write({'status':'success'})          
                    else:
                        message.write({'status':'fail'})   
                except Exception as e:         
                    error_msg = 'Error Message: %s' % (e) 
                    logging.error(error_msg)  
                    message.write({'status':'fail'})   
                    message.write({'errorlog':error_msg})
