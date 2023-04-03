from openerp.osv import fields, osv

class noti_by_customer(osv.osv):

    _name = "noti.by.customer"
        
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
        
        data = self.browse(cr, uid, ids)[0]       
        message = data.message        
        try:            
            for partner in data.partner_ids:            
                one_signal_values = {
                                        'partner_id': partner.id,
                                        'contents': message,
                                        'headings': "Burmart"
                                    }     
                self.pool.get('one.signal.notification.messages').create(cr, uid, one_signal_values, context=context)
                partner_id = partner.id
                device_token = self.pool.get('fcm.notification.messages').get_device_token(cr, uid, partner_id)
                fcm_noti_values = {
                    'partner_id': partner_id,
                    'title': "Burmart",
                    'body': message,
                    'device_token': device_token
                }
                self.pool.get('fcm.notification.messages').create(cr, uid, fcm_noti_values, context=context)
            self.write(cr, uid, ids, {'state': 'send'}, context=context)
        except Exception, e:
            self.write(cr, uid, ids, {'state': 'failed'},context=context)
        return True  
