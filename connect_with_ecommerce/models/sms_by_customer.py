from openerp.osv import fields, osv
import requests

class sms_by_customer(osv.osv):

    _name = "sms.by.customer"
        
    _columns = {        
        'title' : fields.char('Title'),
        'message': fields.text('Message'),
        'partner_ids': fields.many2many('res.partner', string='Customers'),
        'state': fields.selection([
            ('draft', 'Not Send'),
            ('send', 'Send'),        
            ('failed', 'Failed'),       
        ], 'State', readonly=True),
    }
    
    _defaults = {
            'state': 'draft',
    }
       
    def send_msg(self, cr, uid, ids, context=None):
        
        record = self.browse(cr, uid, ids)[0]       
        message = record.message   
        data = None     
        error_msg = None  
        error_log = None       
        for partner in record.partner_ids:
            try: 
                if partner.mobile.startswith('09-') or partner.mobile.startswith('09'):
                    if partner.mobile.startswith('09-'):
                        phone = '959' + str(partner.mobile[3:])
                    else:
                        phone = '959' + str(partner.mobile[2:])
                if partner.mobile.startswith('+959'):
                    phone = '959' + str(partner.mobile[4:])
                text_message = message.encode("utf-16-be")
                hex_message = text_message.encode('hex')
                vals = {
                    'phone': str(phone),
                    'message': hex_message,
                    'partner_id': partner.id,
                    'name': record.title,
                    'text_message': message,
                }
                sms_message = self.pool.get('sms.message').create(cr, uid, vals)
                message_obj = self.pool.get('sms.message').browse(cr, uid, sms_message, context=context)
                if message_obj.status == 'success':
                    sms_status = 'success'  
                    data = message
                else:
                    sms_status = 'fail'   
            except Exception as e:         
                error_msg = 'Error Message: %s' % (e) 
                sms_status = 'fail'                 
                data = error_msg            
                if error_msg:
                    error_log = error_msg
            cr.execute("SELECT now()::timestamp;")    
            current_datetime_data = cr.fetchall()
            for time_data in current_datetime_data:
                current_datetime = time_data[0] 
            cr.execute("""insert into sms_message(name,partner_id,phone,text_message,error_log,status,create_date,create_uid) 
                        values(%s,%s,%s,%s,%s,%s,%s,%s)""",('SMS by Customer',partner.id,str(phone),message,error_log,sms_status,current_datetime,1,))
        if sms_status == 'success':
            self.write(cr, uid, ids, {'state': 'send'}, context=context) 
        else:
            self.write(cr, uid, ids, {'state': 'failed'},context=context)   
        