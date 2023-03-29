from openerp.osv import fields,osv
import requests
import json
import logging
import random
from datetime import timedelta,datetime
import base64
from openerp.addons.connector.queue.job import job, related_action
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.exception import FailedJobError
from openerp.addons.connector.jobrunner.runner import ConnectorRunner

@job(default_channel='root.woosaleorder')
def automation_woo_sale_order(session, original_pre_sale_order_no):
    res_partner_obj = session.pool['res.partner']
    context = session.context.copy()
    cr = session.cr
    uid = session.uid
    res_partner_obj.create_woo_sale_order(cr, uid, original_pre_sale_order_no, context=None)
    return True

class res_partner(osv.osv):
    _inherit = 'res.partner'

    def _get_total_credit_app_data(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x,0), ids))
        credit_obj=self.pool.get('credit.application')
        # The current user may not have access rights for sale orders
        try:
            for partner in self.browse(cr, uid, ids, context):
                credit_app_ids = credit_obj.search(cr, uid, [('customer_id','=',partner.id)], context=context) 
                res[partner.id] = len(credit_app_ids)
        except:
            pass
        return res
            
    _columns = {
                'birthday': fields.date('Birthday'),
                'gender': fields.selection([('Male', 'Male'), ('Female', 'Female')], 'Gender'),
                'shop_name': fields.char('Shop/Business Name'),
                'credit_applications': fields.function(_get_total_credit_app_data,string='Credit Application'),
                'mobile': fields.char('Main Phone No'),
                'phone': fields.char('Secondary Phone No'),
                'woo_register_date': fields.date('Woo Register Date'),
                'is_email_generated':fields.boolean('Is email generated' , default=False),
                'deleted': fields.boolean('Delete from app', default=False),
            }   
          
    def check_maintenance_mode(self, cr, uid, ids, context=None):
        
        maintenance_mode = self.pool.get('ir.config_parameter').get_param(cr, uid, 'maintenance_mode')
        if maintenance_mode:
            return maintenance_mode.lower()
        else:
            return "false"
        
    def send_otp_code(self, cr, uid, ids, mobile_phone, context=None):
        
        if mobile_phone:
            data = None     
            error_msg = None       
            try: 
                boom_sms_key = self.pool.get('ir.config_parameter').get_param(cr, uid, 'boom_sms_key', default=False, context=context)
                number = random.randint(1000,9999)  
                message = 'Valued Customer, your OTP Code is ' + str(number) + '. Please use this for your Burmart account.'
                headers = {
                           'Accept': 'application/json',
                           'Authorization' : 'Bearer {0}'.format(boom_sms_key),
                           }
                # url = 'https://boomsms.net/api/sms/json'
                # data = {
                #         'from' : 'Burmart',
                #         'text' : message,
                #         'to'   : mobile_phone,
                #         }
                url = 'https://staging-api.boomsms.net/api/sms'
                data = {
                        'text' : message,
                        'sender' : 'Burmart',
                        'phone' : mobile_phone,
                        }
                response = requests.post(url,json=data, headers=headers, timeout=60, verify=False)
                if response.status_code == 200:                
                    sms_status = 'success'  
                    data = number    
                else:
                    sms_status = 'fail'   
            except Exception as e:         
                error_msg = 'Error Message: %s' % (e) 
                logging.error(error_msg)
                sms_status = 'fail'                 
                data = error_msg            
            if error_msg:
                error_log = error_msg
            else:
                error_log = None            
            cr.execute("SELECT now()::timestamp;")    
            current_datetime_data = cr.fetchall()
            for time_data in current_datetime_data:
                current_datetime = time_data[0] 
            cr.execute("""insert into sms_message(name,phone,message,error_log,status,create_date,create_uid) 
                        values(%s,%s,%s,%s,%s,%s,%s)""",('Burmart OTP',mobile_phone,message,error_log,sms_status,current_datetime,1,))  
            return data   
        
    def create_or_update_woo_customer(self, cr, uid, ids, mdg_customer=False, customer_code=None, name=None,street=None,street2=None,township=None,state=None,mobile=None,phone=None,gender=None,birthday=None,email=None,partner_latitude=None,partner_longitude=None,sms=None,viber=None,shop_name=None,woo_customer_id=None,image=None,sale_channel=None,context=None):
        vals = {}
        contact_township = contact_city = contact_state = None
        township_obj = self.pool.get('res.township')
        city_obj = self.pool.get('res.city')
        partner_obj = self.pool.get('res.partner')
        outlettype_obj = self.pool.get('outlettype.outlettype')
        sale_channel_obj = self.pool.get('sale.channel')
        res_branch_obj = self.pool.get('res.branch')
        state_obj = self.pool.get('res.country.state')
        if not mdg_customer:            
            vals['name']= shop_name if shop_name else name
            vals['street']= street
            vals['street2']= street2
            if township:
                township_value = township_obj.search(cr, uid, [('name', '=ilike', township)], context=context)
                if township_value:
                    township_data = township_obj.browse(cr, uid, township_value, context=context)
                    vals['township']= township_data.id
                    vals['branch_id'] = township_data.branch_id.id                 
                    city = city_obj.search(cr, uid, [('id', '=', township_data.city.id)], context=context)
                    if city:
                        city_data = city_obj.browse(cr, uid, city, context=context)
                        vals['city']= city_data.id
                    if township_data.delivery_team_id:
                        vals['delivery_team_id']= township_data.delivery_team_id.id
                    else:
                        if city_data.delivery_team_id:
                            vals['delivery_team_id']= city_data.delivery_team_id.id
            if state:                
                state_value = state_obj.search(cr, uid, [('name', '=ilike', state)], context=context)
                if state_value:
                    state_data = state_obj.browse(cr, uid, state_value, context=context)
                    vals['state_id'] = state_data.id
            if woo_customer_id:
                instances=self.pool.get('woo.instance.ept').search(cr, uid, [('state','=','confirmed')], context=context, limit=1)
                if instances:
                    woo_customer_id = "%s_%s"%(instances[0],woo_customer_id) if woo_customer_id else False
                    vals['woo_customer_id'] = woo_customer_id
            if image:
                vals['image'] = image
            vals['sms'] = sms
            vals['viber'] = viber
            vals['shop_name'] = shop_name
            vals['partner_latitude'] = partner_latitude
            vals['partner_longitude'] = partner_longitude
            vals['mobile']= mobile
            vals['phone'] = phone
            vals['gender'] = gender
            vals['birthday'] = birthday
            vals['email'] = email
            vals['customer'] = True
            vals['date_partnership'] = datetime.today()             
            vals['temp_customer'] = name
            vals['woo_register_date'] = datetime.today()
#             if sale_channel == 'consumer':
            outlettype = outlettype_obj.search(cr, uid, [('name', '=ilike', 'Site Registered')],context=context)            
            if outlettype:
                outlettype_data = outlettype_obj.browse(cr, uid, outlettype, context=context)
                vals['outlet_type'] = outlettype_data.id
            sale_channel = sale_channel_obj.search(cr, uid, [('code', '=', 'CS')], context=context)
            if sale_channel:
                sale_channel_data = sale_channel_obj.browse(cr, uid, sale_channel, context=context)
                vals['sales_channel'] = sale_channel_data.id  
#             if sale_channel == 'retailer':
#                 outlettype = outlettype_obj.search(cr, uid, [('name', '=ilike', 'Verify Retailer')],context=context)            
#                 if outlettype:
#                     outlettype_data = outlettype_obj.browse(cr, uid, outlettype, context=context)
#                     vals['outlet_type'] = outlettype_data.id
#                 sale_channel = sale_channel_obj.search(cr, uid, [('code', '=', 'RT')], context=context)
#                 if sale_channel:
#                     sale_channel_data = sale_channel_obj.browse(cr, uid, sale_channel, context=context)
#                     vals['sales_channel'] = sale_channel_data.id                     
                 
            result = partner_obj.create(cr, uid, vals, context=context)                    
            if result:           
                one_signal_values = {
                                     'partner_id': result,
                                     'contents': "Thank you for registration in Burmart E-commerce.",
                                     'headings': "Burmart"
                                    }     
                self.pool.get('one.signal.notification.messages').create(cr, uid, one_signal_values, context=context)
                fcm_noti_values = {
                    'partner_id': result,
                    'title': "Burmart",
                    'body': "Thank you for registration in Burmart E-commerce.",
                }
                self.pool.get('fcm.notification.messages').create(cr, uid, fcm_noti_values, context=context)
            partner = partner_obj.search(cr, uid, [('id', '=', result)])
            if partner:
                partner_data = partner_obj.browse(cr, uid, partner, context=context)
                partner_obj.generate_customercode(cr, uid, [partner_data.id],partner_data,context=context)
            return result
        else:
            partner = partner_obj.search(cr, uid, [('customer_code', '=', customer_code)])
            if partner:
                partner_data = partner_obj.browse(cr, uid, partner, context=context)
#                 vals['street'] = street
#                 vals['street2'] = street2
                if township:
                    township_value = township_obj.search(cr, uid, [('name', '=ilike', township)], context=context, limit=1)
                    if township_value:
                        township_data = township_obj.browse(cr, uid, township_value, context=context)
                        contact_township = township_data.id
                        vals['branch_id'] = township_data.branch_id.id 
                        city = city_obj.search(cr, uid, [('id', '=', township_data.city.id)], context=context)
                        if city:
                            city_data = city_obj.browse(cr, uid, city, context=context)
                            contact_city = city_data.id
                if state:                
                    state_value = state_obj.search(cr, uid, [('name', '=ilike', state)], context=context, limit=1)
                    if state_value:
                        state_data = state_obj.browse(cr, uid, state_value, context=context)
                        contact_state = state_data.id
                
#                 vals['name'] = name             
                vals['phone'] = phone
#                 vals['mobile'] = mobile
                vals['email'] = email
                vals['sms'] = sms
                vals['viber'] = viber
                vals['shop_name'] = shop_name
                vals['partner_latitude'] = partner_latitude
                vals['partner_longitude'] = partner_longitude
                vals['gender'] = gender
                vals['birthday'] = birthday
                vals['woo_register_date'] = datetime.today()
#                 vals['temp_customer'] = name
#                 if sale_channel == 'consumer':
#                 outlettype = outlettype_obj.search(cr, uid, [('name', '=ilike', 'Consumer')],context=context)            
#                 if outlettype:
#                     outlettype_data = outlettype_obj.browse(cr, uid, outlettype, context=context)
#                     vals['outlet_type'] = outlettype_data.id
#                 sale_channel = sale_channel_obj.search(cr, uid, [('code', '=', 'CS')], context=context)
#                 if sale_channel:
#                     sale_channel_data = sale_channel_obj.browse(cr, uid, sale_channel, context=context)
#                     vals['sales_channel'] = sale_channel_data.id  
#                 if sale_channel == 'retailer':
#                     outlettype = outlettype_obj.search(cr, uid, [('name', '=ilike', 'Verify Retailer')],context=context)            
#                     if outlettype:
#                         outlettype_data = outlettype_obj.browse(cr, uid, outlettype, context=context)
#                         vals['outlet_type'] = outlettype_data.id
#                     sale_channel = sale_channel_obj.search(cr, uid, [('code', '=', 'RT')], context=context)
#                     if sale_channel:
#                         sale_channel_data = sale_channel_obj.browse(cr, uid, sale_channel, context=context)
#                         vals['sales_channel'] = sale_channel_data.id      
                if woo_customer_id:
                    instances=self.pool.get('woo.instance.ept').search(cr, uid, [('state','=','confirmed')], context=context, limit=1)
                    if instances:
                        woo_customer_id = "%s_%s"%(instances[0],woo_customer_id) if woo_customer_id else False
                        vals['woo_customer_id'] = woo_customer_id
                
                new_partner_obj = self.pool.get('res.partner')
                old_vals = {}
                old_vals['name'] = name
                old_vals['street'] = street
                old_vals['street2'] = street2
                old_vals['township'] = contact_township
                old_vals['city'] = contact_city
                old_vals['state_id'] = contact_state
                old_vals['mobile'] = mobile
                old_vals['phone'] = partner_data.phone
                old_vals['partner_latitude'] = partner_data.partner_latitude
                old_vals['partner_longitude'] = partner_data.partner_longitude
                old_vals['sms'] = partner_data.sms
                old_vals['viber'] = partner_data.viber
                old_vals['shop_name'] = partner_data.shop_name
                old_vals['email'] = email
#                 old_vals['outlet_type'] = outlettype_data.id
#                 old_vals['sales_channel'] = sale_channel_data.id
                old_vals['branch_id'] = partner_data.branch_id.id
                old_vals['gender'] = partner_data.gender
                old_vals['birthday'] = partner_data.birthday
                if image:
                    old_vals['image'] = image
                vals['customer'] = True
                vals['date_partnership'] = datetime.today()
                result = partner_obj.write(cr, uid,partner_data.id, vals, context=context)                
                old_vals['parent_id'] = partner_data.id
                old_vals['customer'] = False
                old_vals['branch_id'] = partner_data.branch_id.id if partner_data.branch_id else None
                new_one = new_partner_obj.create(cr, uid, old_vals, context=context)                
                if result:           
                    one_signal_values = {
                                         'partner_id': partner_data.id,
                                         'contents': "Thank you for registration in Burmart E-commerce.",
                                         'headings': "Burmart"
                                        }     
                    self.pool.get('one.signal.notification.messages').create(cr, uid, one_signal_values, context=context)
                    fcm_noti_values = {
                        'partner_id': partner_data.id,
                        'title': "Burmart",
                        'body': "Thank you for registration in Burmart E-commerce.",
                    }
                    self.pool.get('fcm.notification.messages').create(cr, uid, fcm_noti_values, context=context)
                return result          

    def create_or_update_woo_customer_with_city(self, cr, uid, ids, mdg_customer=False, customer_code=None, name=None,street=None,street2=None,township=None,city=None,state=None,mobile=None,phone=None,gender=None,birthday=None,email=None,partner_latitude=None,partner_longitude=None,sms=None,viber=None,shop_name=None,woo_customer_id=None,image=None,sale_channel=None,is_email_generated=None,context=None):
        vals = {}
        contact_township = contact_city = contact_state = None
        township_obj = self.pool.get('res.township')
        city_obj = self.pool.get('res.city')
        partner_obj = self.pool.get('res.partner')
        outlettype_obj = self.pool.get('outlettype.outlettype')
        sale_channel_obj = self.pool.get('sale.channel')
        res_branch_obj = self.pool.get('res.branch')
        state_obj = self.pool.get('res.country.state')
        if not mdg_customer:            
            vals['name']= shop_name if shop_name else name
            vals['street']= street
            vals['street2']= street2            
            if state:                
                state_value = state_obj.search(cr, uid, [('name', '=ilike', state)], context=context)
                if state_value:
                    state_data = state_obj.browse(cr, uid, state_value, context=context)
                    vals['state_id'] = state_data.id
                    if city:
                        city = city_obj.search(cr, uid, [('name', '=ilike', city),('state_id', '=', state_data.id)], context=context)
                        if city:
                            city_data = city_obj.browse(cr, uid, city, context=context)
                            vals['city']= city_data.id
                            if township:
                                township_value = township_obj.search(cr, uid, [('name', '=ilike', township),('city', '=', city_data.id)], context=context)
                                if township_value:
                                    township_data = township_obj.browse(cr, uid, township_value, context=context)
                                    vals['township']= township_data.id
                                    vals['branch_id'] = township_data.branch_id.id                 
                                    if township_data.delivery_team_id:
                                        vals['delivery_team_id']= township_data.delivery_team_id.id
                                    else:
                                        if city_data.delivery_team_id:
                                            vals['delivery_team_id']= city_data.delivery_team_id.id
            if woo_customer_id:
                instances=self.pool.get('woo.instance.ept').search(cr, uid, [('state','=','confirmed')], context=context, limit=1)
                if instances:
                    woo_customer_id = "%s_%s"%(instances[0],woo_customer_id) if woo_customer_id else False
                    vals['woo_customer_id'] = woo_customer_id
            if image:
                vals['image'] = image
            vals['sms'] = sms
            vals['viber'] = viber
            vals['shop_name'] = shop_name
            vals['partner_latitude'] = partner_latitude
            vals['partner_longitude'] = partner_longitude
            vals['mobile']= mobile
            vals['phone'] = phone
            vals['gender'] = gender
            vals['birthday'] = birthday
            vals['email'] = email
            vals['customer'] = True
            vals['date_partnership'] = datetime.today()             
            vals['temp_customer'] = name
            vals['woo_register_date'] = datetime.today()
            vals['is_email_generated'] = is_email_generated
#             if sale_channel == 'consumer':
            outlettype = outlettype_obj.search(cr, uid, [('name', '=ilike', 'Site Registered')],context=context)            
            if outlettype:
                outlettype_data = outlettype_obj.browse(cr, uid, outlettype, context=context)
                vals['outlet_type'] = outlettype_data.id
            sale_channel = sale_channel_obj.search(cr, uid, [('code', '=', 'CS')], context=context)
            if sale_channel:
                sale_channel_data = sale_channel_obj.browse(cr, uid, sale_channel, context=context)
                vals['sales_channel'] = sale_channel_data.id  
#             if sale_channel == 'retailer':
#                 outlettype = outlettype_obj.search(cr, uid, [('name', '=ilike', 'Verify Retailer')],context=context)            
#                 if outlettype:
#                     outlettype_data = outlettype_obj.browse(cr, uid, outlettype, context=context)
#                     vals['outlet_type'] = outlettype_data.id
#                 sale_channel = sale_channel_obj.search(cr, uid, [('code', '=', 'RT')], context=context)
#                 if sale_channel:
#                     sale_channel_data = sale_channel_obj.browse(cr, uid, sale_channel, context=context)
#                     vals['sales_channel'] = sale_channel_data.id                     
                 
            result = partner_obj.create(cr, uid, vals, context=context)                    
            if result:           
                one_signal_values = {
                                     'partner_id': result,
                                     'contents': "Thank you for registration in Burmart E-commerce.",
                                     'headings': "Burmart"
                                    }     
                self.pool.get('one.signal.notification.messages').create(cr, uid, one_signal_values, context=context)
                fcm_noti_values = {
                    'partner_id': result,
                    'title': "Burmart",
                    'body': "Thank you for registration in Burmart E-commerce."
                }
                self.pool.get('fcm.notification.messages').create(cr, uid, fcm_noti_values, context=context)
            partner = partner_obj.search(cr, uid, [('id', '=', result)])
            if partner:
                partner_data = partner_obj.browse(cr, uid, partner, context=context)
                partner_obj.generate_customercode(cr, uid, [partner_data.id],partner_data,context=context)
                if not partner_data.woo_customer_id or partner_data.woo_customer_id is None:
                    return False
            return result
        else:
            partner = partner_obj.search(cr, uid, [('customer_code', '=', customer_code)])
            if partner:
                partner_data = partner_obj.browse(cr, uid, partner, context=context)
#                 vals['street'] = street
#                 vals['street2'] = street2
                                        
                if state:                
                    state_value = state_obj.search(cr, uid, [('name', '=ilike', state)], context=context, limit=1)
                    if state_value:
                        state_data = state_obj.browse(cr, uid, state_value, context=context)
                        contact_state = state_data.id
                        if city:
                            city = city_obj.search(cr, uid, [('name', '=ilike', city),('state_id', '=', state_data.id)], context=context)
                            if city:
                                city_data = city_obj.browse(cr, uid, city, context=context)
                                contact_city = city_data.id
                                if township:
                                    township_value = township_obj.search(cr, uid, [('name', '=ilike', township),('city', '=', city_data.id)], context=context, limit=1)
                                    if township_value:
                                        township_data = township_obj.browse(cr, uid, township_value, context=context)
                                        contact_township = township_data.id
                                        vals['branch_id'] = township_data.branch_id.id 
                
#                 vals['name'] = name             
                vals['phone'] = phone
#                 vals['mobile'] = mobile
                vals['email'] = email
                vals['sms'] = sms
                vals['viber'] = viber
                vals['shop_name'] = shop_name
                vals['partner_latitude'] = partner_latitude
                vals['partner_longitude'] = partner_longitude
                vals['gender'] = gender
                vals['birthday'] = birthday
                vals['woo_register_date'] = datetime.today()
                vals['is_email_generated'] = is_email_generated
#                 vals['temp_customer'] = name
#                 if sale_channel == 'consumer':
#                 outlettype = outlettype_obj.search(cr, uid, [('name', '=ilike', 'Consumer')],context=context)            
#                 if outlettype:
#                     outlettype_data = outlettype_obj.browse(cr, uid, outlettype, context=context)
#                     vals['outlet_type'] = outlettype_data.id
#                 sale_channel = sale_channel_obj.search(cr, uid, [('code', '=', 'CS')], context=context)
#                 if sale_channel:
#                     sale_channel_data = sale_channel_obj.browse(cr, uid, sale_channel, context=context)
#                     vals['sales_channel'] = sale_channel_data.id  
#                 if sale_channel == 'retailer':
#                     outlettype = outlettype_obj.search(cr, uid, [('name', '=ilike', 'Verify Retailer')],context=context)            
#                     if outlettype:
#                         outlettype_data = outlettype_obj.browse(cr, uid, outlettype, context=context)
#                         vals['outlet_type'] = outlettype_data.id
#                     sale_channel = sale_channel_obj.search(cr, uid, [('code', '=', 'RT')], context=context)
#                     if sale_channel:
#                         sale_channel_data = sale_channel_obj.browse(cr, uid, sale_channel, context=context)
#                         vals['sales_channel'] = sale_channel_data.id      
                if woo_customer_id:
                    instances=self.pool.get('woo.instance.ept').search(cr, uid, [('state','=','confirmed')], context=context, limit=1)
                    if instances:
                        woo_customer_id = "%s_%s"%(instances[0],woo_customer_id) if woo_customer_id else False
                        vals['woo_customer_id'] = woo_customer_id
                
                new_partner_obj = self.pool.get('res.partner')
                old_vals = {}
                old_vals['name'] = name
                old_vals['street'] = street
                old_vals['street2'] = street2
                old_vals['township'] = contact_township
                old_vals['city'] = contact_city
                old_vals['state_id'] = contact_state
                old_vals['mobile'] = mobile
                old_vals['phone'] = partner_data.phone
                old_vals['partner_latitude'] = partner_data.partner_latitude
                old_vals['partner_longitude'] = partner_data.partner_longitude
                old_vals['sms'] = partner_data.sms
                old_vals['viber'] = partner_data.viber
                old_vals['shop_name'] = partner_data.shop_name
                old_vals['email'] = email
#                 old_vals['outlet_type'] = outlettype_data.id
#                 old_vals['sales_channel'] = sale_channel_data.id
                old_vals['branch_id'] = partner_data.branch_id.id
                old_vals['gender'] = partner_data.gender
                old_vals['birthday'] = partner_data.birthday
                if image:
                    old_vals['image'] = image
                vals['customer'] = True
                vals['date_partnership'] = datetime.today()
                result = partner_obj.write(cr, uid,partner_data.id, vals, context=context)                
                old_vals['parent_id'] = partner_data.id
                old_vals['customer'] = False
                old_vals['branch_id'] = partner_data.branch_id.id if partner_data.branch_id else None
                new_one = new_partner_obj.create(cr, uid, old_vals, context=context)                
                if result:           
                    one_signal_values = {
                                         'partner_id': partner_data.id,
                                         'contents': "Thank you for registration in Burmart E-commerce.",
                                         'headings': "Burmart"
                                        }     
                    self.pool.get('one.signal.notification.messages').create(cr, uid, one_signal_values, context=context)
                    fcm_noti_values = {
                        'partner_id': partner_data.id,
                        'title': "Burmart",
                        'body': "Thank you for registration in Burmart E-commerce.",
                    }
                    self.pool.get('fcm.notification.messages').create(cr, uid, fcm_noti_values, context=context)
                    partner_data = partner_obj.browse(cr, uid, partner_data.id, context=context)
                    if not partner_data.woo_customer_id or partner_data.woo_customer_id is None:
                        return False
                return result 
            
    def create_or_update_delivery_address(self, cr, uid, ids, customer_code=None, woo_customer_id=None, name=None, contact_note=None, street=None,street2=None,township=None,state=None, delivery_address_id=None, image=None, type=None, address_title=None, context=None):
        
        vals = {}
        township_id = city_id = state_id = None
        partner_obj = self.pool.get('res.partner')
        township_obj = self.pool.get('res.township')
        state_obj = self.pool.get('res.country.state')
        city_obj = self.pool.get('res.city')
        if delivery_address_id:
            vals['image'] = image
            vals['name'] = name
            vals['contact_note'] = contact_note
            vals['address_title'] = address_title
            vals['street'] = street
            vals['street2'] = street2
            if township:
                township_value = township_obj.search(cr, uid, [('name', '=ilike', township)], context=context)
                if township_value:
                    township_data = township_obj.browse(cr, uid, township_value, context=context)
                    vals['township']= township_data.id
                    city = city_obj.search(cr, uid, [('id', '=', township_data.city.id)], context=context)
                    if city:
                        city_data = city_obj.browse(cr, uid, city, context=context)
                        vals['city']= city_data.id
            if state:                
                state_value = state_obj.search(cr, uid, [('name', '=ilike', state)], context=context)
                if state_value:
                    state_data = state_obj.browse(cr, uid, state_value, context=context)
                    vals['state_id'] = state_data.id
            result = partner_obj.write(cr, uid, delivery_address_id, vals, context=context) 
            return result
        else:
            domain = []
            if customer_code:                
                domain += [('customer_code', '=', customer_code)]
            if woo_customer_id:
                instances = self.pool.get('woo.instance.ept').search(cr, uid, [('order_auto_import','=',True),('state','=','confirmed')], context=context)
                woo_customer_code = "%s_%s"%(instances[0],woo_customer_id) if woo_customer_id else False
                domain += [('woo_customer_id', '=', woo_customer_code)]
            partner = partner_obj.search(cr, uid, domain, context=context)
            if partner:
                partner_data = partner_obj.browse(cr, uid, partner, context=context)
                partner_id = partner_data.id
                if township:
                    township_value = township_obj.search(cr, uid, [('name', '=ilike', township)], context=context)
                    if township_value:
                        township_data = township_obj.browse(cr, uid, township_value, context=context)
                        township_id = township_data.id
                        city = city_obj.search(cr, uid, [('id', '=', township_data.city.id)], context=context)
                        if city:
                            city_data = city_obj.browse(cr, uid, city, context=context)
                            city_id = city_data.id
                if state:                
                    state_value = state_obj.search(cr, uid, [('name', '=ilike', state)], context=context)
                    if state_value:
                        state_data = state_obj.browse(cr, uid, state_value, context=context)
                        state_id = state_data.id
                existing_delivery_address = partner_obj.search(cr, uid, [('parent_id', '=', partner_id),
                                                                        ('type', '=', type),
                                                                        ('image', '=', image),
                                                                        ('name', '=', name),
                                                                        ('contact_note', '=', contact_note),
                                                                        ('address_title', '=', address_title),
                                                                        ('street', '=', street),
                                                                        ('street2', '=', street2),
                                                                        ('township', '=', township),
                                                                        ('city', '=', city),
                                                                        ('state_id', '=', state_id),
                                                                        ], context=context)
                if not existing_delivery_address:
                    partner_values = {
                                        'parent_id': partner_id,
                                        'type': type,
                                        'image': image,
                                        'name': name,
                                        'contact_note': contact_note,
                                        'address_title': address_title,
                                        'street': street,
                                        'street2': street2,
                                        'township': township_id,
                                        'city': city_id,
                                        'state_id': state_id,
                                        'branch_id': partner_data.branch_id.id if partner_data.branch_id else None
                                    }     
                    new_partner = partner_obj.create(cr, uid, partner_values, context=context)
                    return new_partner
                
    def create_or_update_delivery_address_with_city(self, cr, uid, ids, customer_code=None, woo_customer_id=None, name=None, contact_note=None, street=None,street2=None,township=None,city=None,state=None, delivery_address_id=None, image=None, type=None, address_title=None, context=None):
        
        vals = {}
        township_id = city_id = state_id = None
        partner_obj = self.pool.get('res.partner')
        township_obj = self.pool.get('res.township')
        state_obj = self.pool.get('res.country.state')
        city_obj = self.pool.get('res.city')
        if delivery_address_id:
            vals['image'] = image
            vals['name'] = name
            vals['contact_note'] = contact_note
            vals['address_title'] = address_title
            vals['street'] = street
            vals['street2'] = street2                             
            if state:                
                state_value = state_obj.search(cr, uid, [('name', '=ilike', state)], context=context)
                if state_value:
                    state_data = state_obj.browse(cr, uid, state_value, context=context)
                    vals['state_id'] = state_data.id
                    if city:
                        city = city_obj.search(cr, uid, [('name', '=ilike', city),('state_id', '=', state_data.id)], context=context)
                        if city:
                            city_data = city_obj.browse(cr, uid, city, context=context)
                            vals['city']= city_data.id
                            if township:
                                township_value = township_obj.search(cr, uid, [('name', '=ilike', township),('city', '=', city_data.id)], context=context)
                                if township_value:
                                    township_data = township_obj.browse(cr, uid, township_value, context=context)
                                    vals['township']= township_data.id   
                        
            result = partner_obj.write(cr, uid, delivery_address_id, vals, context=context) 
            return result
        else:
            domain = []
            if customer_code:                
                domain += [('customer_code', '=', customer_code)]
            if woo_customer_id:
                instances = self.pool.get('woo.instance.ept').search(cr, uid, [('order_auto_import','=',True),('state','=','confirmed')], context=context)
                woo_customer_code = "%s_%s"%(instances[0],woo_customer_id) if woo_customer_id else False
                domain += [('woo_customer_id', '=', woo_customer_code)]
            partner = partner_obj.search(cr, uid, domain, context=context)
            if partner:
                partner_data = partner_obj.browse(cr, uid, partner, context=context)
                partner_id = partner_data.id                                        
                if state:                
                    state_value = state_obj.search(cr, uid, [('name', '=ilike', state)], context=context)
                    if state_value:
                        state_data = state_obj.browse(cr, uid, state_value, context=context)
                        state_id = state_data.id
                        if city:
                            city = city_obj.search(cr, uid, [('name', '=ilike', city),('state_id', '=', state_data.id)], context=context)
                            if city:
                                city_data = city_obj.browse(cr, uid, city, context=context)
                                city_id = city_data.id
                                if township:
                                    township_value = township_obj.search(cr, uid, [('name', '=ilike', township),('city', '=', city_data.id)], context=context)
                                    if township_value:
                                        township_data = township_obj.browse(cr, uid, township_value, context=context)
                                        township_id = township_data.id
                                                                
                existing_delivery_address = partner_obj.search(cr, uid, [('parent_id', '=', partner_id),
                                                                        ('type', '=', type),
                                                                        ('image', '=', image),
                                                                        ('name', '=', name),
                                                                        ('contact_note', '=', contact_note),
                                                                        ('address_title', '=', address_title),
                                                                        ('street', '=', street),
                                                                        ('street2', '=', street2),
                                                                        ('township', '=', township),
                                                                        ('city', '=', city),
                                                                        ('state_id', '=', state_id),
                                                                        ], context=context)
                if not existing_delivery_address:
                    partner_values = {
                                        'parent_id': partner_id,
                                        'type': type,
                                        'image': image,
                                        'name': name,
                                        'contact_note': contact_note,
                                        'address_title': address_title,
                                        'street': street,
                                        'street2': street2,
                                        'township': township_id,
                                        'city': city_id,
                                        'state_id': state_id,
                                        'branch_id': partner_data.branch_id.id if partner_data.branch_id else None
                                    }     
                    new_partner = partner_obj.create(cr, uid, partner_values, context=context)
                    return new_partner  
            
    def delete_delivery_address(self, cr, uid, ids, delivery_address_id=None, context=None):  
        
        if delivery_address_id:
            cr.execute("""update res_partner set active=false,deleted=true where id=%s;""",(delivery_address_id,))

    def edit_customer_profile(self, cr, uid, ids, customer_code=None, woo_customer_id=None, mobile=None, email=None, phone=None, name=None, shop_name=None, gender=None, birthday=None, image=None, sale_channel=None, context=None): 
        
        vals = {}
        outlet_type = None
        partner_obj = self.pool.get('res.partner')
        outlettype_obj = self.pool.get('outlettype.outlettype')
        domain = []
        if customer_code:                
            domain += [('customer_code', '=', customer_code)]
        if woo_customer_id:
            instances = self.pool.get('woo.instance.ept').search(cr, uid, [('order_auto_import','=',True),('state','=','confirmed')], context=context)
            woo_customer_code = "%s_%s"%(instances[0],woo_customer_id) if woo_customer_id else False
            domain += [('woo_customer_id', '=', woo_customer_code)]
        if sale_channel == 'consumer':
            outlettype = outlettype_obj.search(cr, uid, [('name', '=ilike', 'Site Registered')],context=context)            
            if outlettype:
                outlettype_data = outlettype_obj.browse(cr, uid, outlettype, context=context)
                outlet_type = outlettype_data.id
        if sale_channel == 'retailer':
            outlettype = outlettype_obj.search(cr, uid, [('name', '=ilike', 'Verify Retailer')],context=context)            
            if outlettype:
                outlettype_data = outlettype_obj.browse(cr, uid, outlettype, context=context)
                outlet_type = outlettype_data.id
        partner = partner_obj.search(cr, uid, domain, context=context)
        if partner:
            partner_data = partner_obj.browse(cr, uid, partner, context=context)
            partner_id = partner_data.id            
            partner_data.write({
                'phone': phone,
                'temp_customer': name,  
                'shop_name': shop_name, 
                'birthday': birthday, 
                'gender': gender,           
            })
            if email and len(email) > 4:
                partner_data.write({
                    'email': email,
                    'is_email_generated': False,
                })
            return partner_id  
        
    def send_delivered_noti(self, cr, uid, sale_order_number, context=None, **kwargs):
        
        if sale_order_number:            
            sale_order_obj = self.pool.get('sale.order').search(cr, uid, [('woo_order_id', '=', sale_order_number)],context=context)
            if sale_order_obj:
                sale_order = self.pool.get('sale.order').browse(cr, uid, sale_order_obj, context=context)
                if sale_order and sale_order.woo_order_number:                
                    one_signal_values = {
                                            'partner_id': sale_order.partner_id.id,
                                            'contents': "Your order " + sale_order.name + " is shipped.",
                                            'headings': "Burmart"
                                        }     
                    self.pool.get('one.signal.notification.messages').create(cr, uid, one_signal_values, context=context)
                    fcm_noti_values = {
                        'partner_id': sale_order.partner_id.id,
                        'title': "Burmart",
                        'body': "Your order " + sale_order.name + " is shipped.",
                    }
                    self.pool.get('fcm.notification.messages').create(cr, uid, fcm_noti_values, context=context)
                    sale_order.update_woo_order_status_action('completed')      
                    return True
        else:
            return False

    def create_woo_sale_order(self, cr, uid, ids, original_pre_sale_order_no=None, context=None):

        product_lists = []
        shipping_lists = []
        fee_lines_lists = []
        free_shipping_values = ''
        index = 0
        if original_pre_sale_order_no:
            original_pre_sale_order_obj = self.pool.get('sale.order').search(cr, uid, [
                ('name', '=', original_pre_sale_order_no)], context=context)
            if original_pre_sale_order_obj:
                original_pre_sale_order = self.pool.get('sale.order').browse(cr, uid, original_pre_sale_order_obj, context=context)
                sale_order_obj = self.pool.get('sale.order').search(cr, uid, [
                    ('pre_sale_order_id', '=', original_pre_sale_order.id)], context=context)
                if sale_order_obj:
                    sale_order = self.pool.get('sale.order').browse(cr, uid, sale_order_obj, context=context)

                    woo_instance_obj = self.pool.get('woo.instance.ept')
                    instance_obj = woo_instance_obj.search(cr, uid, [('state', '=', 'confirmed')], limit=1)
                    if instance_obj:
                        instance = woo_instance_obj.browse(cr, uid, instance_obj, context=context)
                        wcapi = instance.connect_for_product_in_woo()

                        # calculate points for new woo sale order
                        point_wcapi = instance.connect_for_point_in_woo()
                        point_response = point_wcapi.get('points-conversion-rate-and-shipping-info')
                        point_data = point_response.json()
                        money = point_data.get('money')

                        getting_points = int(round(sale_order.amount_total / float(money), 0))

                        # find free shipping to add shipping_lines
                        shipping_info = point_data.get('shipping_info')
                        if shipping_info:
                            shipping_title = shipping_info[1].get('title')
                            min_amount = shipping_info[1].get('min_amount')

                            if shipping_title == 'Free Delivery' and sale_order.amount_total >= float(min_amount):
                                sale_order_lines = self.pool.get('sale.order.line').search(cr, uid,
                                                                                           [('order_id', '=', sale_order.id),
                                                                                            ('promotion_id', '=', False),
                                                                                            ('sale_foc', '!=', True)],
                                                                                           context=context)
                                for so_line in sale_order_lines:
                                    sol = self.pool.get('sale.order.line').browse(cr, uid, so_line, context=context)
                                    index += 1
                                    if index < len(sale_order_lines):
                                        free_shipping_values += sol.product_id.name_template + ' &times; ' + str(
                                            sol.product_uom_qty) + ','
                                    else:
                                        free_shipping_values += sol.product_id.name_template + ' &times; ' + str(
                                            sol.product_uom_qty)

                                shipping_lists.append({
                                    "method_title": "Free shipping",
                                    "method_id": "free_shipping",
                                    "total": "0",
                                    "meta_data": [
                                        {
                                            "key": "Items",
                                            "value": free_shipping_values,
                                            "display_key": "Items",
                                            "display_value": free_shipping_values
                                        }
                                    ]
                                })

                        # find fee_lines to add fee_lines for discount amount
                        discount_lines = self.pool.get('sale.order.line').search(cr, uid, [('order_id', '=', sale_order.id),
                                                                                           ('promotion_id', '!=', False),
                                                                                           ('price_unit', '<', 0)],
                                                                                 context=context)
                        for discount_line in discount_lines:
                            discount_sol = self.pool.get('sale.order.line').browse(cr, uid, discount_line,
                                                                                   context=context)
                            promotion_wcapi = instance.connect_for_point_in_woo()
                            promotion_response = promotion_wcapi.get(
                                'get-valid-promotion/%s' % discount_sol.promotion_id.id)
                            if promotion_response.status_code in [200, 201]:
                                promotion_data = promotion_response.json()
                                if promotion_data != False:
                                    fee_lines_lists.append({
                                        "name": promotion_data,
                                        "tax_class": "0",
                                        "tax_status": "taxable",
                                        "amount": str(int(discount_sol.price_unit)),
                                        "total": str(int(discount_sol.price_unit))
                                    })

                        # get old woo sale order info
                        woo_order_id = sale_order.original_ecommerce_number
                        order_response = wcapi.get('orders/%s' % (woo_order_id))
                        woo_order = order_response.json()
                        customer_id = woo_order.get('customer_id')
                        old_order_id = woo_order.get('id')
                        old_order_number = woo_order.get('number')

                        billing_address = woo_order.get('billing')
                        billing_first_name = billing_address.get('first_name')
                        billing_last_name = billing_address.get('last_name')
                        billing_company = billing_address.get('company')
                        billing_address_1 = billing_address.get('address_1')
                        billing_address_2 = billing_address.get('address_2')
                        billing_city = billing_address.get('city')
                        billing_state = billing_address.get('state')
                        billing_postcode = billing_address.get('postcode')
                        billing_country = billing_address.get('country')
                        billing_email = billing_address.get('email')
                        billing_phone = billing_address.get('phone')

                        shipping_address = woo_order.get('shipping')
                        shipping_first_name = shipping_address.get('first_name')
                        shipping_last_name = shipping_address.get('last_name')
                        shipping_company = shipping_address.get('company')
                        shipping_address_1 = shipping_address.get('address_1')
                        shipping_address_2 = shipping_address.get('address_2')
                        shipping_city = shipping_address.get('city')
                        shipping_state = shipping_address.get('state')
                        shipping_postcode = shipping_address.get('postcode')
                        shipping_country = shipping_address.get('country')
                        shipping_phone = shipping_address.get('phone')

                        payment_method = woo_order.get('payment_method')
                        payment_method_title = woo_order.get('payment_method_title')

                        # find woo products to add line_items
                        product_lines = self.pool.get('sale.order.line').search(cr, uid, [('order_id', '=', sale_order.id),
                                                                                          ('service_product', '=', False)],
                                                                                context=context)
                        for p_line in product_lines:
                            line = self.pool.get('sale.order.line').browse(cr, uid, p_line, context=context)
                            product_code = line.product_id.default_code
                            product_wcapi = instance.connect_for_point_in_woo()
                            if line.sale_foc == True:
                                product_code = product_code + "!"

                            product_response = product_wcapi.put('get-product-id-by-sku', product_code)
                            if product_response.status_code in [200, 201]:
                                product_data = product_response.json()
                                if product_data:
                                    woo_product_id = product_data[0].get('id')
                                    woo_product_uom_name = line.product_uom.name
                                    if not woo_product_id:
                                        woo_product_id = 11111111111111
                                        woo_product_name = line.product_id.name_template + "(" + woo_product_uom_name + ")"
                                    woo_product_wcapi = instance.connect_in_woo()
                                    woo_product_response = woo_product_wcapi.get('products/%s' % woo_product_id)
                                    if woo_product_response.status_code in [200, 201]:
                                        woo_product_data = woo_product_response.json()
                                        if woo_product_data != False:
                                            woo_product_value = woo_product_data.get('product')
                                            woo_product_name = woo_product_value.get(
                                                'title') + "(" + woo_product_uom_name + ")"
                                    product_lists.append({
                                        "product_id": int(woo_product_id),
                                        "name": woo_product_name,
                                        "quantity": line.product_uom_qty,
                                        "price": str(line.price_unit),
                                        "subtotal": str(line.product_uom_qty * line.price_unit),
                                        "total": str(line.product_uom_qty * line.price_unit)
                                    })

                        data = {
                            "status": "completed",
                            "currency": "MMK",
                            "customer_id": customer_id,
                            "billing": {
                                "first_name": billing_first_name,
                                "last_name": billing_last_name,
                                "company": billing_company,
                                "address_1": billing_address_1,
                                "address_2": billing_address_2,
                                "city": billing_city,
                                "state": billing_state,
                                "postcode": billing_postcode,
                                "country": billing_country,
                                "email": billing_email,
                                "phone": billing_phone
                            },
                            "shipping": {
                                "first_name": shipping_first_name,
                                "last_name": shipping_last_name,
                                "company": shipping_company,
                                "address_1": shipping_address_1,
                                "address_2": shipping_address_2,
                                "city": shipping_city,
                                "state": shipping_state,
                                "postcode": shipping_postcode,
                                "country": shipping_country,
                                "phone": shipping_phone
                            },
                            "payment_method": payment_method,
                            "payment_method_title": payment_method_title,
                            "meta_data": [
                                {
                                    "key": "is_vat_exempt",
                                    "value": "no"
                                },
                                {
                                    "key": "_ywpar_conversion_points",
                                    "value": {
                                        "money": money,
                                        "points": "1"
                                    }
                                },
                                {
                                    "key": "ywpar_points_from_cart",
                                    "value": getting_points
                                },
                                {
                                    "key": "parent_order_id",
                                    "value": old_order_id
                                },
                                {
                                    "key": "parent_order",
                                    "value": old_order_number
                                }
                            ],
                            "line_items": product_lists,
                            "shipping_lines": shipping_lists,
                            "fee_lines": fee_lines_lists,
                        }
                        create_order_response = wcapi.post("orders", data)
                        logging.warning("Check create_order_response status code: %s", create_order_response.status_code)
                        if create_order_response.status_code not in [200, 201]:
                            one_signal_values = {
                                'partner_id': sale_order.partner_id.id,
                                'contents': "Your order " + sale_order.name + " does not create properly.Please Check!",
                                'headings': "Burmart"
                            }
                            self.pool.get('one.signal.notification.messages').create(cr, uid, one_signal_values, context=context)
                            fcm_noti_values = {
                                'partner_id': sale_order.partner_id.id,
                                'title': "Burmart",
                                'body': "Your order " + sale_order.name + " does not create properly.Please Check!",
                            }
                            self.pool.get('fcm.notification.messages').create(cr, uid, fcm_noti_values, context=context)
                            # put to queue.job
                            session = ConnectorSession(cr, uid, context)
                            # this code will try after priority 30 , if success , it will succes, if not it will fail
                            jobid = automation_woo_sale_order.delay(session, original_pre_sale_order_no , priority=30)
                            runner = ConnectorRunner()
                            runner.run_jobs()
                        if create_order_response.status_code in [200, 201]:
                            one_signal_values = {
                                'partner_id': sale_order.partner_id.id,
                                'contents': "Your order " + sale_order.name + " is created successfully.",
                                'headings': "Burmart"
                            }
                            self.pool.get('one.signal.notification.messages').create(cr, uid, one_signal_values, context=context)
                            fcm_noti_values = {
                                'partner_id': sale_order.partner_id.id,
                                'title': "Burmart",
                                'body': "Your order " + sale_order.name + " is created successfully.",
                            }
                            self.pool.get('fcm.notification.messages').create(cr, uid, fcm_noti_values, context=context)
                            one_signal_values = {
                                'partner_id': sale_order.partner_id.id,
                                'contents': "Your order " + sale_order.name + " is completed.",
                                'headings': "Burmart"
                            }
                            self.pool.get('one.signal.notification.messages').create(cr, uid, one_signal_values, context=context)
                            fcm_noti_values = {
                                'partner_id': sale_order.partner_id.id,
                                'title': "Burmart",
                                'body': "Your order " + sale_order.name + " is completed.",
                            }
                            self.pool.get('fcm.notification.messages').create(cr, uid, fcm_noti_values, context=context)

    def get_customer_addresses_info(self, cr, uid, ids, parent_id=None, type=None, woo_customer_id=None, context=None):
        records = {}
        if not type:
            type = 'delivery'
        SQL = """
            SELECT rp.id, rp.name as contact_name, rp.type, rp.address_title as address_title, rp.street as street, rp.street2 as street2,township.name as township, 
            city.name as city, country.name as country, state.name as state, rp.contact_note as contact_note, rp.image as image
            FROM res_partner rp 
            LEFT JOIN res_township township on rp.township = township.id 
            LEFT JOIN res_city city on rp.city = city.id 
            LEFT JOIN res_country country on rp.country_id = country.id 
            LEFT JOIN res_country_state state on rp.state_id = state.id 
            WHERE(township.code is not null
                AND rp.parent_id in %s
                AND rp.type= %s
                OR rp.woo_customer_id = %s) 
                AND rp.active= True;
        """
        if woo_customer_id:
            woo_customer = '1_' + woo_customer_id
            parent_ids = self.pool.get('res.partner').search(cr, uid, [('woo_customer_id', '=', woo_customer)],context=context)
            cr.execute(SQL,(tuple(parent_ids), str(type), woo_customer))
            records = cr.dictfetchall()
            for record in records:
                image = record.get('image')
                if image:
                    image = base64.b64encode(image)
                    record.update({'image':image})
        return records