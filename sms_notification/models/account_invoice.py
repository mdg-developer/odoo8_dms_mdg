from openerp.osv import fields, osv
from requests.auth import HTTPBasicAuth
from requests.auth import HTTPDigestAuth
import requests
import json
import time
from requests.auth import AuthBase
import token
from datetime import datetime, timedelta
import datetime
import logging

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    
    def _calculate_due_days(self, cr, uid, ids, field_name, arg, context=None):
        
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            cr.execute('select %s::date-%s::date diff_days', (fields.date.today(), invoice.date_due,))
            diff_days = cr.fetchone()  
            if diff_days:
                if diff_days[0] >0:
                    res[invoice.id] = diff_days[0]
            else:
                res[invoice.id] = 0
        return res 
    
    _columns = {        
        'overdue_noti': fields.datetime('Overdue Reminder Notification'),
        'collection_noti': fields.datetime('Collection Reminder Notification'),
        'invoice_due_pre_reminder_noti': fields.datetime('Invoice Due Pre-Reminder Notification'),
        'due_days': fields.function(_calculate_due_days, string='Calculate due days', type='integer'),
    }         
        
    def get_sms_token(self, cr, uid, context=None): 
        headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
        print "Hello"
        user= 'mdgtest'
        password= '5329303b-4839-4c72-a1d0-fc72776755ca'
        url='https://mpg-ids.mytel.com.mm/auth/realms/eis/protocol/openid-connect/token'
        payload = {'grant_type': 'client_credentials'}
        response = requests.post(url,headers=headers,auth=(user, password), data=payload, verify=False)
        
        print "hello step1"
        
        if response.status_code == 200:
            print ("Success")
            content = json.loads(response.content)
            token = content['access_token'] 
            return token    
               
    def create_sms_history(self, cr, uid, customer_id, phone, message, status, error_log, user_id, reference, context=None):    
         
        result = {
                    'partner_id': customer_id.id,
                    'phone': phone,
                    'message': message,
                    'state': status,
                    'error_log': error_log,
                    'user_id': user_id,          
                    'name': reference,       
                    'date': datetime.datetime.now(),          
                }
        sms_history = self.pool.get('sms.history').create(cr, uid, result, context=context)
                
    def send_invoice_due_pre_reminder_sms(self, cr, uid, ids, context=None):    
        
        cr.execute("select id from account_invoice where type='out_invoice' and state='open' and date_due=current_date+3")    
        invoice_data = cr.fetchall()   
        if invoice_data:    
            for inv in invoice_data:
                invoice = self.pool.get('account.invoice').browse(cr, uid, inv[0], context=context)
                if not invoice.invoice_due_pre_reminder_noti: 
                                             
                    sms_template_objs = self.pool.get('sms.template').search(cr, uid, [('condition', '=', 'before_invoice_is_due'),
                                                                                       ('globally_access','=',False)],limit=1)
                     
                    for sms_template_obj in sms_template_objs:
                        token = self.get_sms_token(cr, uid, context)
                        if token and invoice.partner_id.sms == True:                         
                            template_data = self.pool.get('sms.template').browse(cr, uid, sms_template_obj, context=context)                   
                            message_body =  template_data.get_body_data(invoice)  
                            try:                      
                                header = {'Content-Type': 'application/json',
                                          'Authorization': 'Bearer {0}'.format(token)}
                                sms_url = 'https://mytelapigw.mytel.com.mm/msg-service/v1.3/smsmt/sent'
                                sms_payload = {
                                                "source": "MYTELFTTH",
                                                "dest": invoice.partner_id.phone,
                                                "content": message_body
                                            }                            
                                 
                                response = requests.post(sms_url,  json = sms_payload, headers = header,verify=False)                            
                                if response.status_code == 200:
                                    invoice.write({'invoice_due_pre_reminder_noti':datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                                    self.create_sms_history(cr, uid, invoice.partner_id, invoice.partner_id.phone, message_body, 'success', 'success', uid, invoice.number, context)
                                                                                            
                            except Exception as e:         
                                error_msg = 'Error Message: %s' % (e) 
                                logging.error(error_msg) 
                                                        
    def send_collection_sms(self, cr, uid, ids, context=None):    
        
        current_date = datetime.datetime.now().date()
        invoice_obj = self.pool.get('account.invoice').search(cr, uid, [('type', '=', 'out_invoice'),
                                                                        ('state', '=', 'open'),
                                                                        ('date_due', '=', current_date)])
        if invoice_obj:
            invoice_data = self.browse(cr, uid, invoice_obj, context=context)         
            for invoice in invoice_data:            
                if not invoice.collection_noti:           
                    sms_template_objs = self.pool.get('sms.template').search(cr, uid, [('condition', '=', 'collection_noti'),
                                                                                       ('globally_access','=',False)],limit=1)
                    
                    for sms_template_obj in sms_template_objs:
                        token = self.get_sms_token(cr, uid, context)
                        if token and invoice.partner_id.sms == True:                         
                            template_data = self.pool.get('sms.template').browse(cr, uid, sms_template_obj, context=context)                   
                            message_body =  template_data.get_body_data(invoice)   
                            try:                     
                                header = {'Content-Type': 'application/json',
                                          'Authorization': 'Bearer {0}'.format(token)}
                                sms_url = 'https://mytelapigw.mytel.com.mm/msg-service/v1.3/smsmt/sent'
                                sms_payload = {
                                                "source": "MYTELFTTH",
                                                "dest": invoice.partner_id.phone,
                                                "content": message_body
                                            }                            
                                
                                response = requests.post(sms_url,  json = sms_payload, headers = header,verify=False)                            
                                if response.status_code == 200:
                                    invoice.write({'collection_noti':datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                                    self.create_sms_history(cr, uid, invoice.partner_id, invoice.partner_id.phone, message_body, 'success', 'success', uid, invoice.number, context)
                                    
                            except Exception as e:         
                                error_msg = 'Error Message: %s' % (e) 
                                logging.error(error_msg)  
                                                             
    def send_overdue_sms(self, cr, uid, ids, context=None):    
        
        cr.execute("select id from account_invoice where type='out_invoice' and state='open' and date_due=current_date-3")    
        invoice_data = cr.fetchall()   
        if invoice_data:    
            for inv in invoice_data:
                invoice = self.pool.get('account.invoice').browse(cr, uid, inv[0], context=context)
                if not invoice.overdue_noti:                     
                    sms_template_objs = self.pool.get('sms.template').search(cr, uid, [('condition', '=', 'overdue_noti'),
                                                                                       ('globally_access','=',False)],limit=1)
                    
                    for sms_template_obj in sms_template_objs:
                        token = self.get_sms_token(cr, uid, context)
                        if token and invoice.partner_id.sms == True:                         
                            template_data = self.pool.get('sms.template').browse(cr, uid, sms_template_obj, context=context)                   
                            message_body =  template_data.get_body_data(invoice)                        
                            header = {'Content-Type': 'application/json',
                                      'Authorization': 'Bearer {0}'.format(token)}
                            sms_url = 'https://mytelapigw.mytel.com.mm/msg-service/v1.3/smsmt/sent'
                            sms_payload = {
                                            "source": "MYTELFTTH",
                                            "dest": invoice.partner_id.phone,
                                            "content": message_body
                                        }                            
                            
                            response = requests.post(sms_url,  json = sms_payload, headers = header,verify=False)                            
                            if response.status_code == 200:
                                invoice.write({'overdue_noti':datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})     
