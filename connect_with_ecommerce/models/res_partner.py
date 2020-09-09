from openerp.osv import fields,osv
import requests
import json
import logging
import random

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


    def create_or_update_woo_customer(self, cr, uid, ids, mdg_customer=False, customer_code=None, name=None,street=None,street2=None,township=None,state=None,mobile=None,phone=None,gender=None,birthday=None,email=None,partner_latitude=None,partner_longitude=None,sms=None,viber=None,shop_name=None,woo_customer_id=None,context=None):
        vals = {}
        township_obj = self.pool.get('res.township')
        city_obj = self.pool.get('res.city')
        partner_obj = self.pool.get('res.partner')
        outlettype_obj = self.pool.get('outlettype.outlettype')
        sale_channel_obj = self.pool.get('sale.channel')
        res_branch_obj = self.pool.get('res.branch')
        state_obj = self.pool.get('res.country.state')
        if not mdg_customer:
            vals['name']= name
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
                instances=self.pool.get('woo.instance.ept').search(cr, uid, [('order_auto_import','=',True),('state','=','confirmed')], context=context)
                if instances:
                    woo_customer_id = "%s_%s"%(instances[0],woo_customer_id) if woo_customer_id else False
                    vals['woo_customer_id'] = woo_customer_id
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
            outlettype = outlettype_obj.search(cr, uid, [('name', '=ilike', 'site registered')],context=context)            
            if outlettype:
                outlettype_data = outlettype_obj.browse(cr, uid, outlettype, context=context)
                vals['outlet_type'] = outlettype_data.id
            sale_channel = sale_channel_obj.search(cr, uid, [('code', '=', 'RT')], context=context)
            if sale_channel:
                sale_channel_data = sale_channel_obj.browse(cr, uid, sale_channel, context=context)
                vals['sales_channel'] = sale_channel_data.id                
            res_branch = res_branch_obj.search(cr, uid, [('branch_code', '=', 'TMW')], context=context)
            if res_branch:
                res_branch_data = res_branch_obj.browse(cr, uid, res_branch, context=context)
                vals['branch_id'] = res_branch_data.id                      
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
                vals['street'] = street
                vals['street2'] = street2
                if township:
                    township_value = township_obj.search(cr, uid, [('name', '=ilike', township)], context=context, limit=1)
                    if township_value:
                        township_data = township_obj.browse(cr, uid, township_value, context=context)
                        vals['township']= township_data.id
                        vals['branch_id'] = township_data.branch_id.id 
                if state:                
                    state_value = state_obj.search(cr, uid, [('name', '=ilike', state)], context=context, limit=1)
                    if state_value:
                        state_data = state_obj.browse(cr, uid, state_value, context=context)
                        vals['state_id'] = state_data.id
                vals['name'] = name
                vals['street'] = street
                vals['street2'] = street2                
                vals['phone'] = phone
                vals['mobile'] = mobile
                vals['email'] = email
                vals['sms'] = sms
                vals['viber'] = viber
                vals['shop_name'] = shop_name
                vals['partner_latitude'] = partner_latitude
                vals['partner_longitude'] = partner_longitude
                vals['gender'] = gender
                vals['birthday'] = birthday
                
                new_partner_obj = self.pool.get('res.partner')
                old_vals = {}
                old_vals['name'] = partner_data.name
                old_vals['street'] = partner_data.street
                old_vals['street2'] = partner_data.street2
                old_vals['township'] = partner_data.township.id
                old_vals['city'] = partner_data.city.id
                old_vals['state_id'] = partner_data.state_id.id
                old_vals['mobile'] = partner_data.mobile
                old_vals['phone'] = partner_data.phone
                old_vals['partner_latitude'] = partner_data.partner_latitude
                old_vals['partner_longitude'] = partner_data.partner_longitude
                old_vals['sms'] = partner_data.sms
                old_vals['viber'] = partner_data.viber
                old_vals['shop_name'] = partner_data.shop_name
                old_vals['email'] = partner_data.email
                old_vals['outlet_type'] = partner_data.outlet_type.id
                old_vals['sales_channel'] = partner_data.sales_channel.id
                old_vals['branch_id'] = partner_data.branch_id.id
                old_vals['gender'] = partner_data.gender
                old_vals['birthday'] = partner_data.birthday
                vals['customer'] = True
                result = partner_obj.write(cr, uid,partner_data.id, vals, context=context)                
                old_vals['parent_id'] = partner_data.id
                new_one = new_partner_obj.create(cr, uid, old_vals, context=context)                
                if result:           
                    one_signal_values = {
                                         'partner_id': partner_data.id,
                                         'contents': "Thank you for registration in MDG Retailer E-commerce.",
                                         'headings': "MDG Retailer"
                                        }     
                    self.pool.get('one.signal.notification.messages').create(cr, uid, one_signal_values, context=context)  
                return result        
