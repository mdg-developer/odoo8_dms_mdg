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
               
    def send_collection_sms(self, cr, uid, ids, context=None):    
        print 'datetime.datetime.now()',datetime.datetime.now()
        current_date = datetime.datetime.now().date()
        invoice_obj = self.pool.get('account.invoice').search(cr, uid, [('type', '=', 'out_invoice'),
                                                                        ('state', '=', 'open'),
                                                                        ('date_due', '=', current_date)])
#         invoice_obj = self.pool.get('account.invoice').search(cr, uid, [('id', '=', 1253264)])
        invoice_data = self.browse(cr, uid, invoice_obj, context=context) 
        print 'invoice_obj',invoice_obj
        for invoice in invoice_data:            
            if not invoice.collection_noti:            
                data = self.browse(cr, uid, ids, context=context) 
                sms_template_objs = self.pool.get('sms.template').search(cr, uid, [('condition', '=', 'collection_noti'),
                                                                                   ('globally_access','=',False)])
                
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
                        #time.sleep(1)
                        print "response post"
                        
                        response = requests.post(sms_url,  json = sms_payload, headers = header,verify=False)
                        print "response",response.text
                        if response.status_code == 200:
                            invoice.write({'collection_noti':datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                            print" sms send completed "                          
                
    def send_overdue_sms(self, cr, uid, ids, context=None):    
        
        print 'send_collection_sms' 
        invoice_obj = self.pool.get('account.invoice').search(cr, uid, [('type', '=', 'out_invoice'),
                                                                        ('state', '=', 'open'),
                                                                        ('date_due', '<', fields.date.today())])
#         invoice_obj = self.pool.get('account.invoice').search(cr, uid, [('id', '=', 1253264)])
        invoice_data = self.browse(cr, uid, invoice_obj, context=context) 
        for invoice in invoice_data:            
            if not invoice.overdue_noti:
                data = self.browse(cr, uid, ids, context=context) 
                sms_template_objs = self.pool.get('sms.template').search(cr, uid, [('condition', '=', 'overdue_noti'),
                                                                                   ('globally_access','=',False)])
                
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
                        #time.sleep(1)
                        print "response post"
                        
                        response = requests.post(sms_url,  json = sms_payload, headers = header,verify=False)
                        print "response",response.text
                        if response.status_code == 200:
                            invoice.write({'overdue_noti':datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                            print" sms send completed "       
