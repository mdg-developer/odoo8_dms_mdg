from openerp.osv import fields,osv
import requests
import json
import logging
import random
from datetime import timedelta,datetime

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
            }   
          
    def send_otp_code(self, cr, uid, ids, mobile_phone, context=None):
        
        if mobile_phone:
            try: 
                headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}            
                sms_user= 'mdgpro'
                password= 'fcdaa533-e23d-4f9e-8480-416454b2dfc2'
                url='https://mpg-ids.mytel.com.mm/auth/realms/eis/protocol/openid-connect/token'
                payload = {'grant_type': 'client_credentials'}
                response = requests.post(url,headers=headers,auth=(sms_user, password), data=payload, verify=False)
                number = random.randint(1000,9999)         
                message = 'Dear customer,your OTP for registration is ' + str(number) + '.Use this code to register your account.'
                if response.status_code == 200:                
                    content = json.loads(response.content)
                    token = content['access_token'] 
                    header = {'Content-Type': 'application/json',
                              'Authorization': 'Bearer {0}'.format(token)}                    
                    sms_url = 'https://mytelapigw.mytel.com.mm/msg-service/v1.3/smsmt/sent'
                    sms_payload = {
                                   "source": "MDG",
                                   "dest": mobile_phone,
                                   "content": message 
                            }                 
                    response = requests.post(sms_url,  json = sms_payload, headers = header,verify=False)                
                    if response.status_code == 200:
                        return number              
            except Exception as e:         
                error_msg = 'Error Message: %s' % (e) 
                logging.error(error_msg)  
                return error_msg


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
                                     'contents': "Thank you for registration in MDG Retailer E-commerce.",
                                     'headings': "MDG Retailer"
                                    }     
                self.pool.get('one.signal.notification.messages').create(cr, uid, one_signal_values, context=context)     
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
                                         'contents': "Thank you for registration in MDG Retailer E-commerce.",
                                         'headings': "MDG Retailer"
                                        }     
                    self.pool.get('one.signal.notification.messages').create(cr, uid, one_signal_values, context=context)  
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
            
    def delete_delivery_address(self, cr, uid, ids, delivery_address_id=None, context=None):  
        
        partner_obj = self.pool.get('res.partner')
        if delivery_address_id:
            delivery_data = partner_obj.browse(cr, uid, delivery_address_id, context=context)
            if delivery_data:
                delivery_data.unlink()
                
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
                'email': email,
                'phone': phone,
                'temp_customer': name,  
                'shop_name': shop_name, 
                'birthday': birthday, 
                'gender': gender,           
            })
            return partner_id       
                