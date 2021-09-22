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
    
    def _calculate_date_due_value(self, cr, uid, ids, field_name, arg, context=None):
        
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            cr.execute("""select to_char(%s::date, 'DD/MM/YYYY');""", (invoice.date_due,))
            data = cr.fetchone()  
            if data:
                res[invoice.id] = data[0]
            else:
                res[invoice.id] = None
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
            cr.execute("""select to_char(%s::date, 'DD/MM/YYYY');""", (cash_collection_date,))
            data = cr.fetchone()  
            if data:
                cash_collection_date_value = data[0]
                invoice.write({'cash_collection_date_value':cash_collection_date_value})
            res[invoice.id] = cash_collection_date                
        return res 
    
    def _calculate_paid_date(self, cr, uid, ids, field_name, arg, context=None):
        
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            paid_date=[]
            if invoice.state=='paid':
                cr.execute("""
                    select max(A.date)::date as payment_date
                    from (
                    select  av.origin,av.section_id,payment_full.move_id ,payment_full.id move_line_id,av.number,av.partner_id,av.date_invoice,paidmove.date,aml.reconcile_id,aml.id,payment_full.ref,coalesce(payment_full.credit,0) as payment_amount
                    ,avl.amount_original invoice_amount,(avl.amount_unreconciled-avl.amount) as balance
                    from account_invoice av 
                    left join account_move am  on av.move_id =am.id
                    left join account_move_line aml on aml.move_id=am.id and aml.reconcile_id is not null
                    left join account_voucher_line avl on avl.move_line_id=aml.id and avl.amount >0
                    left join account_voucher avr on avr.id=avl.voucher_id 
                    left join account_move paidmove on paidmove.id= avr.move_id
                    left join account_move_reconcile amr on amr.id=aml.reconcile_id 
                    left join account_move_line payment_full on payment_full.reconcile_id=amr.id  and  payment_full.move_id =paidmove.id 
                    where aml.id not in (payment_full.id)
                    and payment_full.move_id !=am.id
                    and av.id= %s
                    union all 
                    select av.origin,av.section_id,payment_partial.move_id,payment_partial.id move_line_id,av.number,av.partner_id,av.date_invoice,paidmove.date,aml.reconcile_id,aml.id,payment_partial.ref,coalesce(payment_partial.credit,0) as payment_amount,avl.amount_original invoice_amount,(avl.amount_unreconciled-avl.amount) as balance
                    from account_invoice av 
                    left join account_move am  on av.move_id =am.id
                    left join account_move_line aml on aml.move_id=am.id and aml.reconcile_partial_id is not null
                    left join account_voucher_line avl on avl.move_line_id=aml.id and avl.amount >0
                    left join account_voucher avr on avr.id=avl.voucher_id 
                    left join account_move paidmove on paidmove.id= avr.move_id
                    left join account_move_reconcile amp on amp.id=aml.reconcile_partial_id
                    left join account_move_line payment_partial on payment_partial.reconcile_partial_id=amp.id and  payment_partial.move_id =paidmove.id 
                    where aml.id not in (payment_partial.id)
                    and payment_partial.move_id !=am.id
                    and av.id=  %s
                    )A,account_move am,account_journal aj,crm_case_section crm,res_partner rp
                    where  A.move_id =am.id
                    and am.journal_id = aj.id
                    and A.section_id =crm.id
                    and A.partner_id =rp.id            
                """, (invoice.id,invoice.id,))
                paid_data = cr.fetchone() 
                if paid_data:
                    cr.execute("""select to_char(%s::date, 'DD/MM/YYYY');""", (paid_data[0],))
                    paid_date = cr.fetchone()[0]  
            
            if paid_date:
                res[invoice.id] = paid_date
            else:
                res[invoice.id] = None
        return res    
     
    _columns = {        
        'overdue_noti': fields.datetime('Overdue Reminder Notification'),
        'collection_noti': fields.datetime('Collection Reminder Notification'),
        'invoice_due_pre_reminder_noti': fields.datetime('Invoice Due Pre-Reminder Notification'),
        'due_days': fields.function(_calculate_due_days, string='Calculate due days', type='integer'),
        'cash_collection_date': fields.function(_calculate_cash_collection_date, string='Calculate cash collection date', type='date'),
        'date_due_value': fields.function(_calculate_date_due_value, string='Due Date Value', type='char'),
        'cash_collection_date_value': fields.char('Cash Collection Date Value'),
        'paid_date': fields.function(_calculate_paid_date, string='Paid Date', type='char'),
        'paid_date_tmp': fields.char('Paid Date'),
        'paid_amount': fields.float('Paid Amount'),
        
        
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
                            if invoice.partner_id.mobile.startswith('09-') or invoice.partner_id.mobile.startswith('09'):
                                if invoice.partner_id.mobile.startswith('09-'):
                                    phone = '959' + str(invoice.partner_id.mobile[3:])  
                                else:
                                    phone = '959' + str(invoice.partner_id.mobile[2:])
                            if invoice.partner_id.mobile.startswith('+959'):  
                                phone = '959' + str(invoice.partner_id.mobile[4:])  
                            text_message = message_body.encode("utf-16-be")
                            hex_message = text_message.encode('hex')
                            vals = {
                                      'phone':str(phone),
                                      'message':hex_message, 
                                      'partner_id':invoice.partner_id.id,
                                      'name':invoice.number,
                                      'text_message': message_body,
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
                            if invoice.partner_id.mobile.startswith('09-') or invoice.partner_id.mobile.startswith('09'):
                                if invoice.partner_id.mobile.startswith('09-'):
                                    phone = '959' + str(invoice.partner_id.mobile[3:])  
                                else:
                                    phone = '959' + str(invoice.partner_id.mobile[2:])
                            if invoice.partner_id.mobile.startswith('+959'):  
                                phone = '959' + str(invoice.partner_id.mobile[4:])      
                            text_message = message_body.encode("utf-16-be")
                            hex_message = text_message.encode('hex')
                            vals={
                                    'phone':str(phone),
                                    'message':hex_message, 
                                    'partner_id':invoice.partner_id.id,
                                    'name':invoice.number,
                                    'text_message': message_body,
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
                            if invoice.partner_id.mobile.startswith('09-') or invoice.partner_id.mobile.startswith('09'):
                                if invoice.partner_id.mobile.startswith('09-'):
                                    phone = '959' + str(invoice.partner_id.mobile[3:])  
                                else:
                                    phone = '959' + str(invoice.partner_id.mobile[2:])
                            if invoice.partner_id.mobile.startswith('+959'):  
                                phone = '959' + str(invoice.partner_id.mobile[4:])     
                            text_message = message_body.encode("utf-16-be")
                            hex_message = text_message.encode('hex')
                            vals={
                                    'phone':str(phone),
                                    'message':hex_message, 
                                    'partner_id':invoice.partner_id.id,
                                    'name':invoice.number,
                                    'text_message': message_body,
                                } 
                            message = self.pool.get('sms.message').create(cr,uid,vals)
                            message_obj = self.pool.get('sms.message').browse(cr, uid, message, context=context)
                            if message_obj.status == 'success':
                                invoice.write({'overdue_noti':datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})                            


    def send_paid_sms(self, cr, uid,invoice_id, context=None):    
        
        if invoice_id:
            invoice_data = self.browse(cr, uid, invoice_id, context=context)         
            for invoice in invoice_data:            
                if invoice.payment_type:           
                    sms_template_objs = self.pool.get('sms.template').search(cr, uid, [('condition', '=', 'invoice_paid'),
                                                                                       ('globally_access','=',False)],limit=1)
                    
                    for sms_template_obj in sms_template_objs:
                        if invoice.partner_id.sms == True:                         
                            template_data = self.pool.get('sms.template').browse(cr, uid, sms_template_obj, context=context)                   
                            message_body =  template_data.get_body_data(invoice)
                            if invoice.partner_id.mobile.startswith('09-') or invoice.partner_id.mobile.startswith('09'):
                                if invoice.partner_id.mobile.startswith('09-'):
                                    phone = '959' + str(invoice.partner_id.mobile[3:])  
                                else:
                                    phone = '959' + str(invoice.partner_id.mobile[2:])
                            if invoice.partner_id.mobile.startswith('+959'):  
                                phone = '959' + str(invoice.partner_id.mobile[4:])      
                            text_message = message_body.encode("utf-16-be")
                            hex_message = text_message.encode('hex')
                            vals={
                                    'phone':str(phone),
                                    'message':hex_message, 
                                    'partner_id':invoice.partner_id.id,
                                    'name':invoice.number,
                                    'text_message': message_body,
                                }   
                            message = self.pool.get('sms.message').create(cr,uid,vals)
                            message_obj = self.pool.get('sms.message').browse(cr, uid, message, context=context)
                            #if message_obj.status == 'success':
                            # invoice.write({'collection_noti':datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})                               
                                                             