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
    
    def _calculate_cash_collection_date(self, cr, uid, ids, field_name, arg, context=None):
        
        res = {}       
        for invoice in self.browse(cr, uid, ids, context=context):              
            if invoice.date_due < fields.date.today():
                cr.execute("select (%s::date + interval '3' day)::date;",(invoice.date_due,))    
                next_three_days = cr.fetchall()
                if next_three_days:
                    cash_collection_date = next_three_days[0][0]                    
            else:
                cash_collection_date = invoice.date_due
            cr.execute("select min(date),max(date) from public_holidays_line")    
            min_max_data = cr.fetchall()  
            if min_max_data:
                min_date = min_max_data[0][0]
                max_date = min_max_data[0][1]     
                cr.execute('''select date
                            from public_holidays_line
                            union
                            SELECT 
                                mydate::date
                            FROM
                                generate_series(timestamp %s, %s, '1 day') AS g(mydate)
                            WHERE
                                EXTRACT(DOW FROM mydate) = 0
                            order by date asc''',(min_date,max_date,))    
                holidays = cr.fetchall()           
                for holiday in holidays:                
                    if cash_collection_date == holiday[0] and holiday[0] >= invoice.date_due:                                            
                        cr.execute("select (%s::date+ interval '1' day)::date",(cash_collection_date,))    
                        next_date = cr.fetchall()
                        if next_date:
                            cash_collection_date = next_date[0][0]                
                    
            cr.execute("select extract(dow from date %s);",(cash_collection_date,))    
            sunday_data = cr.fetchall()
            if sunday_data:
                if sunday_data[0][0] == 0:
                    cr.execute("select (%s::date+ interval '1' day)::date",(cash_collection_date,))    
                    next_date = cr.fetchall()
                    if next_date:
                        cash_collection_date = next_date[0][0]
                else:
                    cash_collection_date = cash_collection_date
            res[invoice.id] = cash_collection_date                
        return res 
    
    _columns = {        
        'overdue_noti': fields.datetime('Overdue Reminder Notification'),
        'collection_noti': fields.datetime('Collection Reminder Notification'),
        'invoice_due_pre_reminder_noti': fields.datetime('Invoice Due Pre-Reminder Notification'),
        'due_days': fields.function(_calculate_due_days, string='Calculate due days', type='integer'),
        'cash_collection_date': fields.function(_calculate_cash_collection_date, string='Calculate cash collection date', type='date'),
    }         
                
    def send_invoice_due_pre_reminder_sms(self, cr, uid, ids=None, context=None):    
        
        cr.execute("select id from account_invoice where type='out_invoice' and state='open' and date_due=current_date+3")    
        invoice_data = cr.fetchall()   
        if invoice_data:    
            for inv in invoice_data:
                invoice = self.pool.get('account.invoice').browse(cr, uid, inv[0], context=context)
                if not invoice.invoice_due_pre_reminder_noti and invoice.payment_type == 'credit': 
                    sms_template_objs = self.pool.get('sms.template').search(cr, uid, [('condition', '=', 'before_invoice_is_due'),
                                                                                       ('globally_access','=',False)],limit=1)
                    for sms_template_obj in sms_template_objs:
                        if invoice.partner_id.sms == True:                         
                            template_data = self.pool.get('sms.template').browse(cr, uid, sms_template_obj, context=context)                   
                            message_body =  template_data.get_body_data(invoice)  
                            text_message = message_body.encode("utf-16-be")
                            hex_message = text_message.hex()
                            vals = {
                                      'phone':invoice.partner_id.mobile,
                                      'message':hex_message, 
                                      'partner_id':invoice.partner_id.id,
                                      'name':invoice.number
                                }
                            message = self.pool.get('sms.message').create(cr,uid,vals)
                            message_obj = self.pool.get('sms.message').browse(cr, uid, message, context=context)
                            if message_obj.status =='success':
                                invoice.write({'invoice_due_pre_reminder_noti':datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})                                                                                         
                          
    def send_collection_sms(self, cr, uid, ids=None, context=None):    
        
        current_date = datetime.datetime.now().date()
        invoice_obj = self.pool.get('account.invoice').search(cr, uid, [('type', '=', 'out_invoice'),
                                                                        ('state', '=', 'open'),
                                                                        ('date_due', '=', current_date)])
        if invoice_obj:
            invoice_data = self.browse(cr, uid, invoice_obj, context=context)         
            for invoice in invoice_data:            
                if not invoice.collection_noti and invoice.payment_type == 'credit':           
                    sms_template_objs = self.pool.get('sms.template').search(cr, uid, [('condition', '=', 'collection_noti'),
                                                                                       ('globally_access','=',False)],limit=1)
                    
                    for sms_template_obj in sms_template_objs:
                        if invoice.partner_id.sms == True:                         
                            template_data = self.pool.get('sms.template').browse(cr, uid, sms_template_obj, context=context)                   
                            message_body =  template_data.get_body_data(invoice)   
                            text_message = message_body.encode("utf-16-be")
                            hex_message = text_message.hex()
                            vals={
                                    'phone':invoice.partner_id.mobile,
                                    'message':hex_message, 
                                    'partner_id':invoice.partner_id.id,
                                    'name':invoice.number
                                }   
                            message = self.pool.get('sms.message').create(cr,uid,vals)
                            message_obj = self.pool.get('sms.message').browse(cr, uid, message, context=context)
                            if message_obj.status == 'success':
                                invoice.write({'collection_noti':datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})                               
                                                             
    def send_overdue_sms(self, cr, uid, ids=None, context=None):
            
        cr.execute("select id from account_invoice where type='out_invoice' and state='open' and date_due=current_date-3")    
        invoice_data = cr.fetchall()   
        if invoice_data:    
            for inv in invoice_data:
                invoice = self.pool.get('account.invoice').browse(cr, uid, inv[0], context=context)
                if not invoice.overdue_noti and invoice.payment_type == 'credit':                     
                    sms_template_objs = self.pool.get('sms.template').search(cr, uid, [('condition', '=', 'overdue_noti'),
                                                                                       ('globally_access','=',False)],limit=1)
                    
                    for sms_template_obj in sms_template_objs:                        
                        if invoice.partner_id.sms == True:                         
                            template_data = self.pool.get('sms.template').browse(cr, uid, sms_template_obj, context=context)                   
                            message_body =  template_data.get_body_data(invoice) 
                            text_message = message_body.encode("utf-16-be")
                            hex_message = text_message.hex()
                            vals={
                                    'phone':invoice.partner_id.mobile,
                                    'message':hex_message, 
                                    'partner_id':invoice.partner_id.id,
                                    'name':invoice.number
                                } 
                            message = self.pool.get('sms.message').create(cr,uid,vals)
                            message_obj = self.pool.get('sms.message').browse(cr, uid, message, context=context)
                            if message_obj.status == 'success':
                                invoice.write({'overdue_noti':datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})                            
