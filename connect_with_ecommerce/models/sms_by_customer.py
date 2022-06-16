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
        boom_sms_key = self.pool.get('ir.config_parameter').get_param(cr, uid, 'boom_sms_key', default=False, context=context)
        headers = {
                   'Accept': 'application/json',
                   'Authorization' : 'Bearer {0}'.format(boom_sms_key),
                   }
        url = 'https://boomsms.net/api/sms/json'
        for partner in record.partner_ids:
            try: 
                mobile = partner.mobile
                data = {
                        'from' : 'Burmart',
                        'text' : message,
                        'to'   : mobile,
                        }
                response = requests.post(url,json=data, headers=headers, timeout=60, verify=False)
                if response.status_code == 200:                
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
            cr.execute("""insert into sms_message(name,phone,message,error_log,status,create_date,create_uid) 
                        values(%s,%s,%s,%s,%s,%s,%s)""",('SMS by Customer',mobile,message,error_log,sms_status,current_datetime,1,))          
        if sms_status == 'success':
            self.write(cr, uid, ids, {'state': 'send'}, context=context) 
        else:
            self.write(cr, uid, ids, {'state': 'failed'},context=context)   
        