from openerp import models,fields,api,_
import openerp.addons.decimal_precision  as dp
from .. import woocommerce
import time
import requests
from datetime import timedelta,datetime
import dateutil.parser
import logging

class sale_order(models.Model):
    _inherit="sale.order"
    
    @api.one
    def _get_woo_order_status(self):
        for order in self:
            flag=False
            for picking in order.picking_ids:
                if picking.state!='cancel':
                    flag=True
                    break   
            if not flag:
                continue
            if order.picking_ids:
                order.updated_in_woo=True
            else:
                order.updated_in_woo=False
            for picking in order.picking_ids:
                if picking.state =='cancel':
                    continue
                if picking.picking_type_id.code!='outgoing':
                    continue
                if not picking.updated_in_woo:
                    order.updated_in_woo=False
                    break

    @api.one
    def _get_woo_customer_id(self):
        for order in self:
            if order.partner_id.woo_customer_id:
                woo_customer_id = order.partner_id.woo_customer_id.split("_")[1]                
                order.woo_customer_id = woo_customer_id
            else:
                pass
    
    def create(self, cursor, user, vals, context=None):
        partner = self.pool.get('res.partner').browse(cursor, user, [vals['partner_id']], context=context)
        if partner.woo_customer_id:
            woo_customer_id = partner.woo_customer_id.split("_")[1]
            vals.update(woo_customer_id=woo_customer_id)
        return super(sale_order, self).create(cursor, user, vals, context=context)                               

    def _search_woo_order_ids(self,operator,value):
        print("_search_woo_order_ids")
        query="""
                    select sale_order.id from stock_picking
                    inner join sale_order on sale_order.procurement_group_id=stock_picking.group_id                    
                    inner join stock_picking_type on stock_picking.picking_type_id=stock_picking_type.id
                    inner join stock_location on stock_location.id=stock_picking_type.default_location_dest_id and stock_location.usage='customer'
                    where stock_picking.updated_in_woo=False and stock_picking.state='done'"""
        self._cr.execute(query)
        results = self._cr.fetchall()
        order_ids=[]
        for result_tuple in results:
            order_ids.append(result_tuple[0])
        order_ids = list(set(order_ids))
        return [('id','in',order_ids)]

    @api.multi
    def visible_transaction_id(self):
        for order in self:
            if order.woo_instance_id.woo_version == "new":
                order.visible_trans_id=True
            else:
                order.visible_trans_id=False 
                
    woo_order_id=fields.Char("Woo Order Ref")
    woo_order_number=fields.Char("Woo Order Number")
    auto_workflow_process_id=fields.Many2one("sale.workflow.process.ept","Auto Workflow")           
    updated_in_woo=fields.Boolean("Updated In woo",compute=_get_woo_order_status,search='_search_woo_order_ids')
    woo_instance_id=fields.Many2one("woo.instance.ept","Instance")
    woo_trans_id=fields.Char("Transaction Id")
    woo_customer_ip=fields.Char("Customer IP")
    woo_customer_id=fields.Char('Woo Customer ID')
    visible_trans_id=fields.Boolean("trans_id_avail",compute=visible_transaction_id,store=False)
    payment_gateway_id=fields.Many2one("woo.payment.gateway","Payment Gateway")
    barcode=fields.Char('Barcode')
    delivery_address=fields.Text('Delivery Address')
    delivery_contact_no=fields.Char('Delivery Contact No')
    delivery_township_id=fields.Many2one("res.township","Delivery Township")
        
    @api.multi
    def create_or_update_woo_customer(self,woo_cust_id,vals,is_company=False,parent_id=False,type=False,instance=False):
        country_obj=self.env['res.country']
        state_obj=self.env['res.country.state']        
        partner_obj=self.env['res.partner']
        account = self.env['account.account']

        township = None
        property_account_payable = account.search([('type', '=', 'payable')],limit=1)
        property_account_payable_clearing = account.search([('type', '=', 'liquidity')],limit=1)
                
        first_name=vals.get('first_name')
        last_name=vals.get('last_name')
        
        if not first_name and not last_name:
            return False
        
        city=vals.get('city')
        
        name = "%s %s"%(first_name,last_name)
        
        company_name=vals.get("company")
        if company_name:
            is_company=True
        
        email=vals.get('email')                      
        phone=vals.get("phone")                                  
        zip=vals.get('postcode')            
        
        
        address1=vals.get('address_1')
        address2=vals.get('address_2')
        country_name=vals.get('country')
        state_name = vals.get('state')
        
        woo_customer_id = woo_cust_id
        woo_customer_id = "%s_%s"%(instance.id,woo_customer_id) if woo_customer_id else False 
                             
        country=country_obj.search([('code','=',country_name)])
        if not country:
            country=country_obj.search([('name','=',country_name)],limit=1)
            
        if not country:
            state=state_obj.search([('name','=',state_name)],limit=1)            
        else:
            state = state_obj.search(["|", ('code', '=', state_name), ('name', '=', state_name), ('country_id', '=', country.id)],limit=1)
        
        if city:  
            self.env.cr.execute("""select rc.id
                                from res_township rt,res_city rc
                                where rt.city=rc.id
                                and lower(rt.name)=lower(%s)
                                """, (city,))    
            city_data = self.env.cr.fetchall()    
            if city_data:
                city = city_data[0][0]  
                
            self.env.cr.execute("""select id
                                from res_township rt
                                where lower(name)=lower(%s)
                                """, (vals.get('city'),))    
            township_data = self.env.cr.fetchall()    
            
            if township_data:
                township = township_data[0][0]    
                        
        partner=partner_obj.search([('woo_customer_id','=',woo_customer_id)]) if woo_customer_id else False
        if not partner:
            partner=partner_obj.search([('name','=',name),('city','=',city),('township','=',township),('street','=',address1),('street2','=',address2),('email','=',email),('phone','=',phone),('zip','=',zip),('country_id','=',country.id),('state_id','=',state.id)],limit=1)
        if not partner:
            partner=partner_obj.search([('name','=',name),('city','=',city),('township','=',township),('street','=',address1),('street2','=',address2),('zip','=',zip),('country_id','=',country.id)],limit=1)
           
        if partner:
            partner.write({'state_id':state and state.id or False,'is_company':is_company,'woo_company_name_ept':company_name or partner.woo_company_name_ept,
                           'phone':phone or partner.phone,'woo_customer_id':woo_customer_id or partner.woo_customer_id,
                           'lang':instance.lang_id.code,
                           'property_product_pricelist':instance.pricelist_id.id,
                           'property_account_position':instance.fiscal_position_id and instance.fiscal_position_id.id or False,
                           'property_payment_term':instance.payment_term_id and instance.payment_term_id.id or False,
                           'property_account_payable':property_account_payable.id,
                           'property_account_payable_clearing':property_account_payable_clearing.id,
                           })          
        else:    
            partner=partner_obj.create({'type':type,'parent_id':parent_id,'woo_customer_id':woo_customer_id or '',
                                        'name':name,'state_id':state and state.id or False,'city':city,'township':township,
                                        'street':address1,'street2':address2,
                                        'phone':phone,'zip':zip,'email':email,
                                        'country_id':country.id and country.id or False,'is_company':is_company,
                                        'lang':instance.lang_id.code,
                                        'property_product_pricelist':instance.pricelist_id.id,
                                        'property_account_position':instance.fiscal_position_id.id and instance.fiscal_position_id.id or False,
                                        'property_payment_term':instance.payment_term_id.id and instance.payment_term_id.id or False,
                                        'woo_company_name_ept':company_name,
                                        'property_account_payable':property_account_payable.id,
                                        'property_account_payable_clearing':property_account_payable_clearing.id,                                        
                                        })
        return partner        

    @api.model
    def createWooAccountTax(self,value,price_included,company,title):
        accounttax_obj = self.env['account.tax']
        
        if price_included:
            name='%s_(%s %s included %s)_%s'%(title,str(value),'%',price_included and 'T' or 'F',company.name)
        else:
            name='%s_(%s %s excluded %s)_%s'%(title,str(value),'%',price_included and 'F' or 'T',company.name)            

        accounttax_id = accounttax_obj.create({'name':name,'amount':float(value),'type_tax_use':'sale','price_include':price_included,'company_id':company.id})
        
        return accounttax_id

    @api.model
    def get_woo_tax_id_ept(self,instance,tax_datas,tax_included):
        tax_id=[]        
        taxes=[]
        for tax in tax_datas:
            rate=float(tax.get('rate',0.0))
            if rate!=0.0:
                rate = rate / 100.0 if rate >= 1 else rate                
                acctax_id = self.env['account.tax'].search([('price_include','=',tax_included),('type_tax_use', '=', 'sale'), ('company_id','=',instance.warehouse_id.company_id.id)],limit=1)
                if not acctax_id:
                    acctax_id = self.createWooAccountTax(rate,tax_included,instance.warehouse_id.company_id,tax.get('name'))
                    if acctax_id:
                        transaction_log_obj=self.env["woo.transaction.log"]
                        message="""Tax was not found in ERP ||
                        Automatic Created Tax,%s ||
                        tax rate  %s ||
                        Company %s"""%(acctax_id.name,rate,instance.company_id.name)                                                                                                                                                                                                                                 
                        transaction_log_obj.create(
                                                    {'message':message,
                                                     'mismatch_details':True,
                                                     'type':'sales',
                                                     'woo_instance_id':instance.id
                                                    })                    
                if acctax_id:
                    taxes.append(acctax_id.id)
        if not tax_datas:
            acctax_id = self.env['account.tax'].search([('description','=','CT Inc 5%'), ('company_id','=',instance.warehouse_id.company_id.id)],limit=1)
            if acctax_id:
                taxes.append(acctax_id.id)
        if taxes:
            tax_id = [(6, 0, taxes)]
        return tax_id

    @api.model
    def check_woo_mismatch_details(self,lines,instance,order_number):
        transaction_log_obj=self.env["woo.transaction.log"]
        odoo_product_obj=self.env['product.product']
        woo_product_obj=self.env['woo.product.product.ept']
        mismatch=False
        for line in lines:
            line_product_id=False
            if instance.woo_version == 'old':
                line_product_id=line.get('product_id',False)
            elif instance.woo_version == 'new':
                line_product_id=line.get('variation_id',False) or line.get('product_id',False)
            
            barcode=0
            odoo_product=False
            woo_variant=False
            if line_product_id:
                woo_variant=woo_product_obj.search([('variant_id','=',line_product_id),('woo_instance_id','=',instance.id)],limit=1)                
                if woo_variant:
                    continue
                try:
                    if line_product_id:
                        wcapi = instance.connect_in_woo()
                        res=wcapi.get('products/%s'%line_product_id)
                        if not isinstance(res,requests.models.Response):               
                            transaction_log_obj.create({'message': "Get Product \nResponse is not in proper format :: %s"%(res),
                                                         'mismatch_details':True,
                                                         'type':'sales',
                                                         'woo_instance_id':instance.id
                                                        })
                            mismatch=True
                            break                        
                        woo_variant = res.json()                        
                        if instance.woo_version == 'old':
                            errors = woo_variant.get('errors','')
                            if errors:
                                message = errors[0].get('message')
                                transaction_log_obj.create(
                                                            {'message':"Product Removed from WooCommerce site,  %s"%(message),
                                                             'mismatch_details':True,
                                                             'type':'product',
                                                             'woo_instance_id':instance.id
                                                            })
                    else:
                        woo_variant = False
                except:
                    woo_variant=False
                    message="Variant Id %s not found in woo || default_code %s || order ref %s"%(line_product_id,line.get('sku'),order_number)
                    log=transaction_log_obj.search([('woo_instance_id','=',instance.id),('message','=',message)])
                    if not log:
                        transaction_log_obj.create(
                                                    {'message':message,
                                                     'mismatch_details':True,
                                                     'type':'sales',
                                                     'woo_instance_id':instance.id
                                                    })

                if woo_variant:
                    if instance.woo_version == 'old':                    
                        barcode=woo_variant.get('product').get('sku')
                    elif instance.woo_version == 'new':
                        barcode=woo_variant.get('sku')
                else:
                    barcode=0
            sku=line.get('sku') or ''
            woo_variant=barcode and woo_product_obj.search([('product_id.default_code','=',barcode),('woo_instance_id','=',instance.id)],limit=1)
            if not woo_variant:
                odoo_product=barcode and odoo_product_obj.search([('default_code','=',barcode)],limit=1) or False
            if not odoo_product and not woo_variant:
                woo_variant=sku and woo_product_obj.search([('default_code','=',sku),('woo_instance_id','=',instance.id)],limit=1)
                if not woo_variant:
                    odoo_product=sku and odoo_product_obj.search([('default_code','=',sku.split("!")[0])],limit=1)

            if not woo_variant and not odoo_product:
                message="%s Product Code Not found for order %s"%(sku,order_number)
                log=transaction_log_obj.search([('woo_instance_id','=',instance.id),('message','=',message)])
                if not log:
                    transaction_log_obj.create(
                                                {'message':message,
                                                 'mismatch_details':True,
                                                 'type':'sales',
                                                 'woo_instance_id':instance.id
                                                })
                mismatch=True
                break
        return mismatch

    @api.model
    def get_promotion_data(self,odoo_discount_id):
        
        product_id = None
        promotion_id = None
        if odoo_discount_id:
            odoo_promotion = self.env['promos.rules'].search([('ecommerce','=',True),
                                                              ('id','=',odoo_discount_id)])
            if odoo_promotion and odoo_promotion.main_group:                                                           
                self.env.cr.execute('''select pp.id product_id,name_template product_name
                                    from product_product pp,product_template pt
                                    where pp.product_tmpl_id=pt.id
                                    and main_group=%s
                                    and pp.active=true
                                    and pt.active=true
                                    and pt.type='service'                                                
                                    and lower(name_template) like %s
                                    limit 1''',(odoo_promotion.main_group.id,'%discount',))
                product_record = self.env.cr.dictfetchall() 
                if product_record:                           
                    for p_data in product_record:  
                        product_id = p_data.get('product_id')
                        promotion_id = odoo_promotion.id    
            return product_id,promotion_id
        
    @api.model
    def assign_promotions(self,sale_order,woo_promotions):
        
        promo_list = []
        if sale_order and woo_promotions:
            for promo in woo_promotions:
                discounted_price = promo.get("discounted_price")
                foc_quantity = promo.get("quantity")
                odoo_discount_id = promo.get('odoo_discount_id',False)
                promo_list.append({
                                    'discounted_price': float(discounted_price),
                                    'quantity': float(foc_quantity),
                                    'odoo_discount_id': odoo_discount_id,
                                })     
            if len(promo_list) > 0:                    
                sale_order_lines = self.env['sale.order.line'].search([('promotion_id','!=', False),('order_id','=', sale_order.id)], order="id asc")        
                for so_line in sale_order_lines:
                    if float(so_line.price_unit) < 0:
                        resultlist = [p for p in promo_list if p.get('discounted_price', '') == float(so_line.price_unit)]
                        if resultlist:
                            odoo_discount_id = int(resultlist[0].get('odoo_discount_id'))
                            if odoo_discount_id:
                                product_id,promotion_id = self.get_promotion_data(odoo_discount_id)
                                so_line.update({'product_id': product_id,
                                                'promotion_id': promotion_id})
                    if so_line.sale_foc == True:
                        resultlist = [p for p in promo_list if p.get('quantity', '') == float(so_line.product_uom_qty)]
                        if resultlist:
                            odoo_discount_id = int(resultlist[0].get('odoo_discount_id'))
                            if odoo_discount_id:
                                product_id,promotion_id = self.get_promotion_data(odoo_discount_id)
                                so_line.update({'promotion_id': promotion_id})
                                   
    @api.model
    def create_woo_sale_order_line(self,line,tax_ids,product,woo_product_uom,quantity,fiscal_position,partner,pricelist_id,name,order,price):
        sale_order_line_obj=self.env['sale.order.line']
        uom_id=product and product.uom_id and product.uom_id.id or False
        product_data=sale_order_line_obj.product_id_change(pricelist_id,product and product.ids[0] or False,quantity,uom_id
                                                                         ,quantity,False,product and product.name or None,partner.ids[0]
                                                                         ,False,True,time.strftime('%Y-%m-%d'),False,
                                                                         fiscal_position.id,False)
        product_data=product_data.get('value')
                                
        delivery_product = discount_product = fees_product = False
        promotion_id = None
        
        promotion = self.env['promos.rules'].search([('ecommerce', '=', True)], limit=1)
                    
        if product.product_tmpl_id.type == 'service':
            delivery_obj = self.env['delivery.carrier']
            delivery = delivery_obj.search([('product_id', '=', product.id)])
            if delivery:    
                for deli in delivery:            
                    if product.id == deli.product_id.id:                    
                        delivery_product = True 
                        break
        woo_setting = self.env['woo.instance.ept'].search([])
        if woo_setting:            
            for woo in woo_setting:
                if woo.discount_product_id:
                    woo_discount_product = self.env['product.product'].search([('id', '=', woo.discount_product_id.id)])
                    if woo_discount_product:
                        if product.id == woo_discount_product.id: 
                            discount_product = True 
                            if promotion:
                                promotion_id = promotion.id
                if woo.fee_line_id:
                    woo_fee_product = self.env['product.product'].search([('id', '=', woo.fee_line_id.id)])
                    if woo_fee_product:
                        if product.id == woo_fee_product.id:
                            fees_product = True                             
                            if promotion:
                                promotion_id = promotion.id                                                                      
        
        if price == 0:
            if promotion:
                promotion_id = promotion.id
        
        sol_name = product.name or name
        sol_product_id = product and product.ids[0] or False
        
        if float(price) == 0:
            sale_foc = True
        else:
            sale_foc = False 
        
        if woo_product_uom and product.type == 'product':
            product_uom = self.env['product.uom'].search([('id', '=', woo_product_uom)])
            if product_uom:
                product_data.update({'product_uom': product_uom.id})   
                                                        
        product_data.update(
                            {
                            'name':sol_name,
                            'product_id':sol_product_id,
                            'order_id':order.id,
                            'product_uom_qty':quantity,
                            'product_uos_qty':quantity,
                            'price_unit':price,
                            'woo_line_id':line.get('id'),
                            'th_weight':float(line.get('grams',0.0))*quantity/1000,
                            'tax_id':tax_ids,
                            'delivery_product':delivery_product,
                            'discount_product':discount_product,
                            'fees_product':fees_product,   
                            'promotion_id':promotion_id,
                            'discount_amt':0,   
                            'sale_foc':sale_foc,                              
                            }                                    
                            )
        sale_order_line_obj.create(product_data)         
        return True

    @api.model
    def create_or_update_woo_product(self,line,instance,wcapi):
        transaction_log_obj=self.env["woo.transaction.log"]
        woo_product_tmpl_obj=self.env['woo.product.template.ept']
        woo_product_obj=self.env['woo.product.product.ept']        
        variant_id=False
        if instance.woo_version == 'old':
            variant_id=line.get('product_id')
        elif instance.woo_version == 'new':
            variant_id=line.get('variation_id',False) or line.get('product_id',False)
        woo_product=False
        if variant_id:
            woo_product=woo_product_obj.search([('woo_instance_id','=',instance.id),('variant_id','=',variant_id)],limit=1)
            if woo_product:
                return woo_product
            product_code = line.get('sku').split("!")[0]
            woo_product=woo_product_obj.search([('woo_instance_id','=',instance.id),('default_code','=',product_code)],limit=1)
            woo_product and woo_product.write({'variant_id':variant_id})
            if woo_product:
                return woo_product
            response=wcapi.get('products/%s'%(variant_id))
            if not isinstance(response,requests.models.Response):               
                transaction_log_obj.create({'message': "Get Product \nResponse is not in proper format :: %s"%(response),
                                             'mismatch_details':True,
                                             'type':'sales',
                                             'woo_instance_id':instance.id
                                            })
                return False           
            res = response.json()
            
            parent_id = False
            if instance.woo_version == 'old':
                result = res.get('product')
                parent_id = result.get('parent_id',False)
                if not parent_id:
                    parent_id = variant_id
                woo_product_tmpl_obj.sync_products(instance,parent_id,update_templates=True)
            elif instance.woo_version == 'new':
                parent_id = res.get('parent_id',False)
                if not parent_id:
                    parent_id = variant_id
                woo_product_tmpl_obj.sync_new_products(instance,parent_id,update_templates=True)                        
            woo_product=woo_product_obj.search([('woo_instance_id','=',instance.id),('variant_id','=',variant_id)],limit=1)
        else:
            product_code = line.get('sku').split("!")[0]
            woo_product=woo_product_obj.search([('woo_instance_id','=',instance.id),('default_code','=',product_code)],limit=1)
            if woo_product:
                return woo_product
        return woo_product

    @api.multi
    def create_or_update_payment_gateway(self,instance,result):
        payment_gateway_obj=self.env["woo.payment.gateway"]
        payment_gateway = False
        vals=""    
        payment_data = ""
        code = ""
        name = ""
        
        if instance.woo_version == "old":
            payment_data = result.get("payment_details")
            code = payment_data.get("method_id")
            name = payment_data.get("method_title")
        else:
            code = result.get("payment_method")
            name = result.get("payment_method_title")
            
        if not code:
            return False
        payment_gateway = payment_gateway_obj.search([("code","=",code),("woo_instance_id","=",instance.id)],limit=1)
        if payment_gateway:
            vals={"name":name}
            payment_gateway.write(vals)
        else:
            vals={"code":code,"name":name,"woo_instance_id":instance.id}
            payment_gateway = payment_gateway_obj.create(vals)
        return payment_gateway
    
    @api.multi
    def get_woo_order_vals(self,result,workflow,invoice_address,instance,partner,shipping_address,pricelist_id,fiscal_position,payment_term,payment_gateway):
            woo_order_number = ''
            note = ''
            created_at = False
            woo_trans_id=""
            woo_customer_ip=""
            getting_point = 0
            barcode_value = None
            branch_id = None
            
            if instance.woo_version == 'old':
                woo_order_number = result.get('order_number')
                note = result.get('note') or result.get('customer_note')
                created_at = result.get('created_at')
                woo_trans_id = ""
                woo_customer_ip = result.get("customer_ip")
            elif instance.woo_version == 'new':
                woo_order_number = result.get('number')
                note = result.get('customer_note')
                created_at = result.get('date_created')
                woo_trans_id = result.get("transaction_id")
                woo_customer_ip = result.get("customer_ip_address")
                        
            if instance.order_prefix:
                name="%s%s"%(instance.order_prefix,woo_order_number)
            else:
                name=woo_order_number
            
            delivery_id = woo_warehouse = None
            
            shipping_partner = self.env['res.partner'].search([('id','=',shipping_address.ids[0])])           
                        
            if shipping_partner.township.delivery_team_id:        
                woo_warehouse = shipping_partner.township.delivery_team_id.warehouse_id.id       
                delivery_id = shipping_partner.township.delivery_team_id.id
            elif shipping_partner.city.delivery_team_id:
                delivery_id = shipping_partner.city.delivery_team_id.id
               
            woo_instance_obj=self.env['woo.instance.ept']
            instance=woo_instance_obj.search([('state','=','confirmed')], limit=1)
            if instance:
                wcapi = instance.connect_for_point_in_woo()   
                point_response = wcapi.get('point')      
                point_response_data = point_response.json()                
                for point in point_response_data:
                    woo_order_id = point.get('order_id',False)     
                    woo_point = point.get('amount',False)                      
                    if woo_order_number == str(woo_order_id) and int(woo_point) > 0:
                        getting_point = int(woo_point)                        
                        break                
                
                barcode_response = wcapi.get('post-barcode/%s'%(woo_order_number))    
                if barcode_response.status_code in [200,201]:              
                    barcode_response_data = barcode_response.json()   
                    if barcode_response_data:                                   
                        for barcode in barcode_response_data:                            
                            barcode_value = barcode.get('meta_value',False)  
                else:
                    message = "Error in Import Barcode for Order %s %s"%(woo_order_number,barcode_response.content)                        
                    self.env["woo.transaction.log"].create(
                                                            {'message':message,
                                                             'mismatch_details':True,
                                                             'type':'sales',
                                                             'woo_instance_id':instance.id
                                                            })           
                        
            if result.get('payment_details'):                
                if result.get('payment_details').get('method_title',False) == 'Credit Application Amount':
                    payment_type = "credit"
                else:
                    payment_type = "cash"     
                          
            if delivery_id:
                user_obj = self.env['res.users'].search([('default_section_id','=',delivery_id)])  
                if user_obj:
                    sales_person = user_obj.id
                    
            if partner:
                partner_obj = self.env['res.partner'].search([('id','=',partner.id)])  
                if partner_obj:
                    if partner_obj.township:
                        if partner_obj.township.delivery_team_id:
                            if partner_obj.township.delivery_team_id.branch_id:
                                branch_id = partner_obj.township.delivery_team_id.branch_id.id
                    
            ordervals = {
                'name' :name,                
                'picking_policy' : workflow.picking_policy,
                'order_policy' : workflow.invoice_on,                        
                'partner_invoice_id' : invoice_address.ids[0],
                'date_order' :created_at,
                'warehouse_id' : woo_warehouse,
                'partner_id' : partner.ids[0],
                'partner_shipping_id' : shipping_address.ids[0],
                'state' : 'draft',
                'pricelist_id' : pricelist_id or instance.pricelist_id.id or False,
                'fiscal_position': fiscal_position and fiscal_position.id  or False,
                'payment_term':payment_term or False, 
                'note':note,       
                'woo_order_id':result.get('id'),
                'woo_order_number':woo_order_number,
                'auto_workflow_process_id':workflow.id,
                'woo_instance_id':instance.id,
                'section_id':delivery_id,
                'user_id':sales_person,
                'company_id':instance.company_id.id,  
                'payment_gateway_id':payment_gateway and payment_gateway.id or False,
                'woo_trans_id':woo_trans_id,
                'woo_customer_ip':woo_customer_ip,
                'delivery_id':delivery_id,
                'pre_order':True,
                'getting_point':getting_point,
                'payment_type':payment_type,
                'barcode':barcode_value,
                'ecommerce':True,
                'tb_ref_no':woo_order_number,
                'branch_id': branch_id,
            }            
            return ordervals

    def import_all_woo_orders(self,wcapi,instance,transaction_log_obj,order_status,page):
        if instance.woo_version == 'new':
            res = wcapi.get('orders?status=%s&per_page=100&page=%s'%(order_status.status,page))        
        else:
            res = wcapi.get('orders?status=%s&filter[limit]=1000&page=%s'%(order_status.status,page))
        if not isinstance(res,requests.models.Response):               
            transaction_log_obj.create({'message': "Import All Orders \nResponse is not in proper format :: %s"%(res),
                                         'mismatch_details':True,
                                         'type':'sales',
                                         'woo_instance_id':instance.id
                                        })
            return []
        response = res.json()
        if instance.woo_version == 'old':
            errors = response.get('errors','')
            if errors:
                message = errors[0].get('message')
                transaction_log_obj.create(
                                            {'message':message,
                                             'mismatch_details':True,
                                             'type':'sales',
                                             'woo_instance_id':instance.id
                                            })
                return []
            return response.get('orders')
        elif instance.woo_version == 'new':
            return response
    
    @api.model
    def auto_import_woo_sale_order_ept(self):
        woo_instance_obj=self.env['woo.instance.ept']
        ctx = dict(self._context) or {}
        woo_instance_id = ctx.get('woo_instance_id',False)
        #if woo_instance_id:
        instance=woo_instance_obj.search([('state','=','confirmed')],limit=1)
        if instance and instance.woo_version == 'old':
            self.import_woo_orders(instance)
        elif instance and instance.woo_version == 'new':
            self.import_new_woo_orders(instance)
        return True
    
    @api.model
    def update_woo_cancel_sale_order_ept(self):
        woo_instance_obj=self.env['woo.instance.ept']
        instance=woo_instance_obj.search([('state','=','confirmed')],limit=1)
        if instance:
            wcapi = instance.connect_in_woo() 
            if wcapi:                
                order_response = wcapi.get('orders')      
                order_response_data = order_response.json()
                if instance.woo_version == 'old':                
                    woo_orders = order_response_data.get("orders")                
                elif instance.woo_version == 'new':
                    woo_orders = order_response_data.get("orders")      
                
                for order in woo_orders:
                    woo_order_number = order.get('order_number',False)     
                    woo_order_status = order.get('status',False)                                    
                    if woo_order_status == 'cancelled' or woo_order_status == 'cancel-request': 
                        sale_order = self.env['sale.order'].search([('woo_order_number', '=', woo_order_number),
                                                                    ('state', 'in', ('draft','sent','manual'))])
                        if sale_order:
                            sale_order.action_cancel()
        return True

    @api.model
    def verify_order(self,instance,order):
        payment_method = ""
        total = 0
        discount = 0
        
        if instance.woo_version == 'old':
            payment_method = order.get("payment_details").get("method_id")
            total = order.get("total")
            discount = order.get("total_discount")
        
        if instance.woo_version == 'new':
            payment_method = order.get("payment_method")
            total = order.get("total")
            if order.get("coupon_lines"):
                discount = order.get("coupon_lines")[0].get("discount")
                
        if not payment_method and float(total) == 0 and float(discount) > 0:
            return True
        else:
            return False 

    @api.model
    def import_woo_orders(self,instance=False):        
        instances=[]
        woo_product_uom=None
        shipping_phone = None
        pricelist_id=False
        current_point=0
        transaction_log_obj=self.env["woo.transaction.log"]
        if not instance:
            instances=self.env['woo.instance.ept'].search([('order_auto_import','=',True),('state','=','confirmed')])
        else:
            instances.append(instance)
        for instance in instances:
            wcapi = instance.connect_in_woo()
            order_ids = []
            tax_included  = wcapi.get('').json().get('store').get('meta').get('tax_included') or False
            for order_status in instance.import_order_status_ids:
                response = wcapi.get('orders?status=%s&filter[limit]=1000'%(order_status.status))
                if not isinstance(response,requests.models.Response):                
                    transaction_log_obj.create({'message': "Import Orders \nResponse is not in proper format :: %s"%(response),
                                                 'mismatch_details':True,
                                                 'type':'sales',
                                                 'woo_instance_id':instance.id
                                                })
                    continue                                    
                if response.status_code not in [200,201]:
                    message = "Error in Import Orders %s"%(response.content)                        
                    transaction_log_obj.create(
                                        {'message':message,
                                         'mismatch_details':True,
                                         'type':'sales',
                                         'woo_instance_id':instance.id
                                        })
                    continue
                order_response=response.json()
                order_ids = order_ids + order_response.get('orders')
                total_pages = response.headers.get('X-WC-TotalPages')
                if total_pages >=2:
                    for page in range(2,int(total_pages)+1):            
                        order_ids = order_ids + self.import_all_woo_orders(wcapi,instance,transaction_log_obj,order_status,page)            
            
            import_order_ids=[]            
            if instance:
                discount_label_wcapi = instance.connect_for_point_in_woo()   
                discount_label_info = {"discount": "foc"}                              
                discount_label_wcapi.put('put-discount-label-for-null/1',discount_label_info) 
                
            for order in order_ids: 
                logging.warning("Check order: %s", order.get('order_number'))                                                            
                if self.search([('woo_instance_id','=',instance.id),('woo_order_id','=',order.get('id')),('woo_order_number','=',order.get('order_number'))]):
                    continue
                lines=order.get('line_items')
                if self.check_woo_mismatch_details(lines,instance,order.get('order_number')):
                    continue
                financial_status = 'paid'
                if order.get('payment_details').get('paid'):
                    financial_status = 'paid'
                else:
                    financial_status = 'not_paid'
                
                no_payment_gateway = False
                payment_gateway=self.create_or_update_payment_gateway(instance, order)
                
                if not payment_gateway:
                    no_payment_gateway = self.verify_order(instance,order)
                    if not no_payment_gateway:
                        message="Payment Gateway not found for this order %s and financial status is %s"%(order.get('order_number'),financial_status)
                        log=transaction_log_obj.search([('woo_instance_id','=',instance.id),('message','=',message)])
                        if not log:
                            transaction_log_obj.create(
                                                {'message':message,
                                                 'mismatch_details':True,
                                                 'type':'sales',
                                                 'woo_instance_id':instance.id
                                                })                    
                        continue
                
                workflow = False
                
                if not no_payment_gateway and payment_gateway:
                    workflow_config=self.env['woo.sale.auto.workflow.configuration'].search([('woo_instance_id','=',instance.id),('financial_status','=',financial_status),('payment_gateway_id','=',payment_gateway.id)],limit=1)
                    workflow=workflow_config and workflow_config.auto_workflow_id or False
    
                    if not workflow and not no_payment_gateway:                    
                        message="Workflow Configuration not found for this order %s, financial status is %s and Payment Gateway is %s"%(order.get('order_number'),financial_status,order.get('payment_details').get('method_id'))
                        log=transaction_log_obj.search([('woo_instance_id','=',instance.id),('message','=',message)])
                        if not log:
                            transaction_log_obj.create(
                                                {'message':message,
                                                 'mismatch_details':True,
                                                 'type':'sales',
                                                 'woo_instance_id':instance.id
                                                })                    
                        continue
                woo_customer_id = order.get('customer',{}).get('id',False)
                if not woo_customer_id:                    
                    message="Customer Not Available In %s Order"%(order.get('order_number'))
                    log=transaction_log_obj.search([('woo_instance_id','=',instance.id),('message','=',message)])
                    if not log:
                        transaction_log_obj.create(
                                                    {'message':message,
                                                     'mismatch_details':True,
                                                     'type':'sales',
                                                     'woo_instance_id':instance.id
                                                    })
                    continue
                partner=order.get('billing_address',False) and self.create_or_update_woo_customer(woo_customer_id,order.get('billing_address'), False, False,False,instance)
                
                if not partner:                    
                    message="Customer Not Available In %s Order"%(order.get('order_number'))
                    log=transaction_log_obj.search([('woo_instance_id','=',instance.id),('message','=',message)])
                    if not log:
                        transaction_log_obj.create(
                                                    {'message':message,
                                                     'mismatch_details':True,
                                                     'type':'sales',
                                                     'woo_instance_id':instance.id
                                                    })
                    continue
                shipping_address=order.get('shipping_address',False) and self.create_or_update_woo_customer(False,order.get('shipping_address'), False,partner.id,'delivery',instance) or partner
                partner_result=self.onchange_partner_id(partner.ids[0])
                partner_result=partner_result.get('value')
                
                fiscal_position=partner.property_account_position
                 
                woo_partner = self.env['res.partner'].search([('id','=',partner.id)]) 
                if woo_partner:   
                    if woo_partner.sales_channel:
                        if woo_partner.sales_channel.code == 'CS' or woo_partner.sales_channel.code == 'RT':
                            if woo_partner.sales_channel.code == 'CS':
                                product_pricelist = self.env['product.pricelist'].sudo().search([('consumer','=',True)], limit=1)
                                if product_pricelist:
                                    pricelist_id = product_pricelist.id
                                else:
                                    message="Consumer pricelist is not found for %s."%(order.get('order_number'))
                                    log=transaction_log_obj.search([('woo_instance_id','=',instance.id),('message','=',message)])
                                    if not log:
                                        transaction_log_obj.create(
                                                                    {'message':message,
                                                                     'mismatch_details':True,
                                                                     'type':'sales',
                                                                     'woo_instance_id':instance.id
                                                                    })
                                    continue
                            if woo_partner.sales_channel.code == 'RT':
                                product_pricelist = self.env['product.pricelist'].sudo().search([('retail','=',True)], limit=1)
                                if product_pricelist:
                                    pricelist_id = product_pricelist.id
                                else:
                                    message="Retail pricelist is not found for %s."%(order.get('order_number'))
                                    log=transaction_log_obj.search([('woo_instance_id','=',instance.id),('message','=',message)])
                                    if not log:
                                        transaction_log_obj.create(
                                                                    {'message':message,
                                                                     'mismatch_details':True,
                                                                     'type':'sales',
                                                                     'woo_instance_id':instance.id
                                                                    })
                                    continue
                        else:
                            message="Customer %s's sale channel must be 'Consumer' or 'Retail' for %s."%(partner.name,order.get('order_number'))
                            log=transaction_log_obj.search([('woo_instance_id','=',instance.id),('message','=',message)])
                            if not log:
                                transaction_log_obj.create(
                                                            {'message':message,
                                                             'mismatch_details':True,
                                                             'type':'sales',
                                                             'woo_instance_id':instance.id
                                                            })
                            continue
                    else:                    
                        message="Sale channel is not found for customer %s in %s."%(partner.name,order.get('order_number'))
                        log=transaction_log_obj.search([('woo_instance_id','=',instance.id),('message','=',message)])
                        if not log:
                            transaction_log_obj.create(
                                                        {'message':message,
                                                         'mismatch_details':True,
                                                         'type':'sales',
                                                         'woo_instance_id':instance.id
                                                        })
                        continue
#                 pricelist_id=partner_result.get('pricelist_id',False)
                payment_term=partner_result.get('payment_term')                
                
                woo_order_vals=self.get_woo_order_vals(order, workflow, partner, instance, partner, shipping_address, pricelist_id, fiscal_position, payment_term, payment_gateway)
                sale_order = self.create(woo_order_vals) if woo_order_vals else False
                
                if sale_order:
                    if sale_order.partner_shipping_id:
                        delivery_address = ''
                        if sale_order.partner_shipping_id.street:
                            delivery_address += sale_order.partner_shipping_id.street
                        if sale_order.partner_shipping_id.street2:
                            delivery_address += ' ' + sale_order.partner_shipping_id.street2
                        if sale_order.partner_shipping_id.township:
                            delivery_address += ' ' + sale_order.partner_shipping_id.township.name
                        if sale_order.partner_shipping_id.city:
                            delivery_address += ' ' + sale_order.partner_shipping_id.city.name
                                           
                    phone_wcapi = instance.connect_for_product_in_woo()                    
                    phone_response = phone_wcapi.get('orders/%s'%(order.get('id')))                    
                    phone_res = phone_response.json()                   
                    phone_meta_data = phone_res.get('meta_data')
                    if phone_meta_data:
                        for phone_meta_data in phone_meta_data:
                            if phone_meta_data.get('key') == '_shipping_phone':                       
                                shipping_phone = phone_meta_data.get('value')
                                
                    sale_order.write({ 
                                      'delivery_address' : delivery_address,
                                      'delivery_contact_no' : shipping_phone,
                                      'delivery_township_id' : sale_order.partner_shipping_id.township.id if sale_order.partner_shipping_id.township else None,
                                    })
                    
                if sale_order and sale_order.getting_point != 0:
                    point_date = dateutil.parser.parse(sale_order.date_order).date()
                    self.env.cr.execute("select COALESCE(sum(getting_point),0) from point_history where partner_id=%s", (partner.id,))    
                    point_data = self.env.cr.fetchall()
                    if point_data:
                        current_point = point_data[0][0]
                    self.env['point.history'].create({'partner_id': sale_order.partner_id.id,
                                                      'date': point_date,
                                                      'order_id': sale_order.id,
                                                      'membership_id': sale_order.partner_id.membership_id.id,                                                      
                                                      'balance_point': current_point + sale_order.getting_point,
                                                      'getting_point': sale_order.getting_point,
                                                    })
                    
                if not sale_order:
                    continue

                def calclulate_line_discount(line):
                    return (float(line.get('subtotal')) - float(line.get('total'))) + (float(line.get('subtotal_tax')) - float(line.get('total_tax')))
                
                order_discount = False
                discount_value = 0.0
                total_discount=float(order.get('total_discount',0.0))
                if float(total_discount)>0.0:
                    order_discount = True
                    if not tax_included:
                        discount_value = float(total_discount)
                                                       
                
                import_order_ids.append(sale_order.id)                
                shipping_taxable = False
                tax_datas = []
                tax_ids = []
                for tax_line in order.get('tax_lines'):
                    tax_data = {}
                    rate_id = tax_line.get('rate_id')
                    if rate_id:
                        res_rate = wcapi.get('taxes/%s'%(rate_id))
                        rate = res_rate.json()
                        tax_data = rate.get('tax',{})
                        tax_datas.append(tax_data)
                        shipping_taxable = tax_data.get('shipping')                       
                tax_ids = self.get_woo_tax_id_ept(instance,tax_datas,tax_included)
                for line in lines:                    
                    woo_product=self.create_or_update_woo_product(line,instance,wcapi)
                    if not woo_product:
                        continue
                    product=woo_product.product_id
                    woo_product_id=line.get('product_id')
                    product_wcapi = instance.connect_for_product_in_woo()                    
                    product_response=product_wcapi.get('products/%s'%(woo_product_id))                    
                    product_res = product_response.json()                   
                    product_meta_data = product_res.get('meta_data')
                    if product_meta_data:
                        for meta_data in product_meta_data:
                            if meta_data.get('key') == '_woo_uom_input':                            
                                woo_product_uom = meta_data.get('value')
                            
                    actual_unit_price = 0.0                    
                    if tax_included:
                        actual_unit_price=(float(line.get('subtotal_tax')) + float(line.get('subtotal'))) / float(line.get('quantity'))                            
                    else:
                        actual_unit_price = float(line.get('subtotal')) / float(line.get('quantity'))
                    if tax_included and float(total_discount)>0.0:
                        discount_value += calclulate_line_discount(line) if order_discount else 0.0                                                                            
                    self.create_woo_sale_order_line(line,tax_ids,product,woo_product_uom,line.get('quantity'),fiscal_position,partner,pricelist_id,product.name,sale_order,actual_unit_price)                  
    
                shipping_product=instance.shipment_charge_product_id 
                product_id=shipping_product and shipping_product.ids[0] or False
                shipping_tax_ids = []                     
                for line in order.get('shipping_lines',[]):
                    if shipping_taxable and float(order.get('shipping_tax')) > 0.0:                        
                        shipping_tax_ids =  self.get_woo_tax_id_ept(instance,tax_datas,False)
                    else:
                        shipping_tax_ids = []
                        
                    delivery_method=line.get('method_title')
                    if delivery_method:
                        carrier=self.env['delivery.carrier'].search(['|',('name','=',delivery_method),('woo_code','=',delivery_method)],limit=1)
                        if not carrier:
                            carrier=self.env['delivery.carrier'].search(['|',('name','ilike',delivery_method),('woo_code','ilike',delivery_method)],limit=1)
                        if not carrier:
                            carrier=self.env['delivery.carrier'].create({'name':delivery_method,'woo_code':delivery_method,'partner_id':self.env.user.company_id.partner_id.id,'product_id':shipping_product.id,'normal_price':line.get('total')})
                        sale_order.write({'carrier_id':carrier.id})
                        if carrier.product_id:
                            shipping_product=carrier.product_id
                    self.create_woo_sale_order_line(line,shipping_tax_ids,shipping_product,woo_product_uom,1,fiscal_position,partner,pricelist_id,shipping_product and shipping_product.name or line.get('method_title'),sale_order,line.get('total'))
                if order_discount and discount_value:                                                                                                                            
                    self.create_woo_sale_order_line({},tax_ids,instance.discount_product_id,woo_product_uom,1,fiscal_position,partner,pricelist_id,instance.discount_product_id.name,sale_order,discount_value*-1)
                fee_lines = order.get("fee_lines",[])
                for fee_line in fee_lines:
                    fee_value = fee_line.get("total")
                    fee = fee_line.get("title")
                    fee_line_tax_ids = []
                    fee_line_tax_ids =  self.get_woo_tax_id_ept(instance,tax_datas,False)
                    if fee_value:
                        self.create_woo_sale_order_line({},fee_line_tax_ids,instance.fee_line_id,woo_product_uom,1,fiscal_position,partner,pricelist_id,fee,sale_order,fee_value)
                woo_promotions = order.get("related_promotion",[]) 
                if woo_promotions:  
                    self.assign_promotions(sale_order,woo_promotions)        
                if sale_order:
                    noti_message = "Your order " + sale_order.name + " is created successfully."
                    messages =self.env['one.signal.notification.messages'].search([('contents','=', noti_message)])
                    if not messages:           
                        one_signal_values = {
                                             'partner_id': sale_order.partner_id.id,
                                             'contents': noti_message,
                                             'headings': "Burmart"
                                            }                          
                        self.env['one.signal.notification.messages'].create(one_signal_values)    
            if import_order_ids:
                self.env['sale.workflow.process.ept'].auto_workflow_process(ids=import_order_ids)
        return True
    
    @api.model
    def import_new_woo_orders(self,instance=False):        
        instances=[]
        woo_product_uom = None
        transaction_log_obj=self.env["woo.transaction.log"]
        if not instance:
            instances=self.env['woo.instance.ept'].search([('order_auto_import','=',True),('state','=','confirmed')])
        else:
            instances.append(instance)
        for instance in instances:
            wcapi = instance.connect_in_woo()             
            order_ids = []
            for order_status in instance.import_order_status_ids:
                response = wcapi.get('orders?status=%s&per_page=100'%(order_status.status))
                if not isinstance(response,requests.models.Response):                
                    transaction_log_obj.create({'message': "Import Orders \nResponse is not in proper format :: %s"%(response),
                                                 'mismatch_details':True,
                                                 'type':'sales',
                                                 'woo_instance_id':instance.id
                                                })
                    continue                                    
                if response.status_code not in [200,201]:
                    message = "Error in Import Orders %s"%(response.content)                        
                    transaction_log_obj.create(
                                        {'message':message,
                                         'mismatch_details':True,
                                         'type':'sales',
                                         'woo_instance_id':instance.id
                                        })
                    continue
                order_ids = order_ids + response.json()
                total_pages = response.headers.get('x-wp-totalpages')
                if total_pages >=2:
                    for page in range(2,int(total_pages)+1):            
                        order_ids = order_ids + self.import_all_woo_orders(wcapi,instance,transaction_log_obj,order_status,page)            
            
            import_order_ids=[]
            
            for order in order_ids:
                tax_included  = order.get('prices_include_tax')                                                             
                if self.search([('woo_instance_id','=',instance.id),('woo_order_id','=',order.get('id')),('woo_order_number','=',order.get('number'))]):
                    continue
                lines=order.get('line_items')
                if self.check_woo_mismatch_details(lines,instance,order.get('number')):
                    continue
                financial_status = 'paid'
                if order.get('transaction_id'):
                    financial_status = 'paid'
                else:
                    financial_status = 'not_paid'
                
                no_payment_gateway = False
                payment_gateway=self.create_or_update_payment_gateway(instance, order)
                
                if not payment_gateway:
                    no_payment_gateway = self.verify_order(instance,order)
                    if not no_payment_gateway:
                        message="Payment Gateway not found for this order %s and financial status is %s"%(order.get('number'),financial_status)
                        log=transaction_log_obj.search([('woo_instance_id','=',instance.id),('message','=',message)])
                        if not log:
                            transaction_log_obj.create(
                                                {'message':message,
                                                 'mismatch_details':True,
                                                 'type':'sales',
                                                 'woo_instance_id':instance.id
                                                })  
                        continue 
                workflow = False
                if not no_payment_gateway and payment_gateway: 
                    workflow_config=self.env['woo.sale.auto.workflow.configuration'].search([('woo_instance_id','=',instance.id),('financial_status','=',financial_status),('payment_gateway_id','=',payment_gateway.id)],limit=1)
                    workflow=workflow_config and workflow_config.auto_workflow_id or False
    
                    if not workflow and not no_payment_gateway:                    
                        message="Workflow Configuration not found for this order %s, financial status is %s and Payment Gateway is %s"%(order.get('number'),financial_status,order.get('payment_method'))
                        log=transaction_log_obj.search([('woo_instance_id','=',instance.id),('message','=',message)])
                        if not log:
                            transaction_log_obj.create(
                                                {'message':message,
                                                 'mismatch_details':True,
                                                 'type':'sales','woo_instance_id':instance.id
                                                })                    
                        continue
                woo_customer_id = order.get('customer_id',False)
                partner=order.get('billing',False) and self.create_or_update_woo_customer(woo_customer_id,order.get('billing'), False, False,False,instance)
                if not partner:                    
                    message="Customer Not Available In %s Order"%(order.get('number'))
                    log=transaction_log_obj.search([('woo_instance_id','=',instance.id),('message','=',message)])
                    if not log:
                        transaction_log_obj.create(
                                                    {'message':message,
                                                     'mismatch_details':True,
                                                     'type':'sales',
                                                     'woo_instance_id':instance.id
                                                    })
                    continue
                shipping_address=order.get('shipping',False) and self.create_or_update_woo_customer(False,order.get('shipping'), False,partner.id,'delivery',instance) or partner                                                
                partner_result=self.onchange_partner_id(partner.ids[0])
                partner_result=partner_result.get('value')
                
                fiscal_position=partner.property_account_position
                pricelist_id=partner_result.get('pricelist_id',False)
                payment_term=partner_result.get('payment_term')                
                
                woo_order_vals=self.get_woo_order_vals(order,workflow, partner, instance, partner, shipping_address, pricelist_id, fiscal_position, payment_term,payment_gateway)
                sale_order = self.create(woo_order_vals) if woo_order_vals else False
                
                if not sale_order:
                    continue
                                                              
                total_discount=float(order.get('discount_total',0.0)) + float(order.get('discount_tax',0.0))                                                                      
                
                import_order_ids.append(sale_order.id)                
                shipping_taxable = False
                tax_datas = []
                tax_ids = []
                for tax_line in order.get('tax_lines'):                    
                    rate_id = tax_line.get('rate_id')
                    if rate_id:
                        res_rate = wcapi.get('taxes/%s'%(rate_id))
                        rate = res_rate.json()                        
                        tax_datas.append(rate)
                        shipping_taxable = rate.get('shipping')                       
                tax_ids = self.get_woo_tax_id_ept(instance,tax_datas,tax_included)
                for line in lines:                    
                    woo_product=self.create_or_update_woo_product(line,instance,wcapi)
                    if not woo_product:
                        continue
                    product=woo_product.product_id
                    actual_unit_price = 0.0                    
                    if tax_included:
                        actual_unit_price=(float(line.get('subtotal_tax')) + float(line.get('subtotal'))) / float(line.get('quantity'))                            
                    else:
                        actual_unit_price = float(line.get('subtotal')) / float(line.get('quantity'))                                                                                                
                    self.create_woo_sale_order_line(line,tax_ids,product,woo_product_uom,line.get('quantity'),fiscal_position,partner,pricelist_id,product.name,sale_order,actual_unit_price)                  
    
                shipping_product=instance.shipment_charge_product_id 
                product_id=shipping_product and shipping_product.ids[0] or False
                shipping_tax_ids = []                     
                for line in order.get('shipping_lines',[]):
                    if shipping_taxable and float(order.get('shipping_tax')) > 0.0:                        
                        shipping_tax_ids =  self.get_woo_tax_id_ept(instance,tax_datas,False)
                    else:
                        shipping_tax_ids = []
                        
                    delivery_method=line.get('method_title')
                    if delivery_method:
                        carrier=self.env['delivery.carrier'].search(['|',('name','=',delivery_method),('woo_code','=',delivery_method)])
                        if not carrier:
                            carrier=self.env['delivery.carrier'].search(['|',('name','ilike',delivery_method),('woo_code','ilike',delivery_method)])
                        if not carrier:
                            carrier=self.env['delivery.carrier'].create({'name':delivery_method,'woo_code':delivery_method,'partner_id':self.env.user.company_id.partner_id.id,'product_id':shipping_product.id,'normal_price':line.get('total')})
                        sale_order.write({'carrier_id':carrier.id})
                        if carrier.product_id:
                            shipping_product=carrier.product_id
                    self.create_woo_sale_order_line(line,shipping_tax_ids,shipping_product,woo_product_uom,1,fiscal_position,partner,pricelist_id,shipping_product and shipping_product.name or line.get('method_title'),sale_order,line.get('total'))
                if total_discount > 0.0:                                                                                                                            
                    self.create_woo_sale_order_line({},tax_ids,instance.discount_product_id,woo_product_uom,1,fiscal_position,partner,pricelist_id,instance.discount_product_id.name,sale_order,total_discount*-1)
                
                fee_lines = order.get("fee_lines",[])
                for fee_line in fee_lines:
                    fee_value = fee_line.get("total")
                    fee = fee_line.get("name")
                    fee_line_tax_ids = []
                    fee_line_tax_ids =  self.get_woo_tax_id_ept(instance,tax_datas,False)
                    if fee_value:
                        self.create_woo_sale_order_line({},fee_line_tax_ids,instance.fee_line_id,woo_product_uom,1,fiscal_position,partner,pricelist_id,fee,sale_order,fee_value)    
            if import_order_ids:
                self.env['sale.workflow.process.ept'].auto_workflow_process(ids=import_order_ids)
        return True
   
    @api.model
    def auto_update_woo_order_status_ept(self):
        woo_instance_obj=self.env['woo.instance.ept']
        ctx = dict(self._context) or {}
        woo_instance_id = ctx.get('woo_instance_id',False)
        if woo_instance_id:
            instance=woo_instance_obj.search([('id','=',woo_instance_id),('state','=','confirmed')])
            instance and self.update_woo_order_status(instance)
        return True   
       
    @api.model
    def update_woo_order_status(self,instance):
        transaction_log_obj=self.env["woo.transaction.log"]
        instances=[]
        current_point=0
        if not instance:
            instances=self.env['woo.instance.ept'].search([('order_auto_update','=',True),('state','=','confirmed')])
        else:
            instances.append(instance)
        for instance in instances:
            wcapi = instance.connect_in_woo()    
            sales_orders = self.search([('warehouse_id','=',instance.warehouse_id.id),
                                                         ('woo_order_id','!=',False),
                                                         ('woo_instance_id','=',instance.id),                                                     
                                                         ('updated_in_woo','=',False)],order='date_order')
            
            for sale_order in sales_orders:                
                for picking in sale_order.picking_ids:
                    """Here We Take only done picking and  updated in woo false"""
                    if picking.updated_in_woo or picking.state!='done':
                        continue
                    info = {"status": "completed"}
                    data = info
                    if instance.woo_version == 'old':                    
                        data = {"order":info}
                    response = wcapi.put('orders/%s'%(sale_order.woo_order_id),data)
                    if not isinstance(response,requests.models.Response):
                        message = "Update Orders %s Status \nResponse is not in proper format :: %s"%(sale_order.name,response)
                        log=transaction_log_obj.search([('woo_instance_id','=',instance.id),('message','=',message)])
                        if not log:
                            transaction_log_obj.create({'message': message,
                                                         'mismatch_details':True,
                                                         'type':'sales',
                                                         'woo_instance_id':instance.id
                                                        })
                            continue
                    if response.status_code not in [200,201]:
                        message = "Error in update order %s status,  %s"%(sale_order.name,response.content)
                        log=transaction_log_obj.search([('woo_instance_id','=',instance.id),('message','=',message)])
                        if not log:
                            transaction_log_obj.create(
                                                {'message':message,
                                                 'mismatch_details':True,
                                                 'type':'sales',
                                                 'woo_instance_id':instance.id
                                                })
                            continue
                    result = response.json()
                    if instance.woo_version == 'old':
                        errors = result.get('errors','')
                        if errors:
                            message = errors[0].get('message')
                            transaction_log_obj.create(
                                                        {'message':"Error in update order %s status,  %s"%(sale_order.name,message),
                                                         'mismatch_details':True,
                                                         'type':'sales',
                                                         'woo_instance_id':instance.id
                                                        })
                            continue
                        else:
                            picking.write({'updated_in_woo':True})
                    elif instance.woo_version == 'new':
                        picking.write({'updated_in_woo':True})
                        
            order_response = wcapi.get('orders')      
            order_response_data = order_response.json()
            if instance.woo_version == 'old':                
                woo_orders = order_response_data.get("orders")                
            elif instance.woo_version == 'new':
                woo_orders = order_response_data.get("orders")      
            
            for order in woo_orders:
                woo_order_id = order.get('order_number',False)     
                woo_order_status = order.get('status',False)                  
                if woo_order_status == 'cancelled' or woo_order_status == 'cancel-request':       
                    draft_sale_orders = self.search([('woo_order_number','=',woo_order_id),
                                                     ('state','in',('draft','sent','manual'))])
                    if draft_sale_orders:                        
                        draft_sale_orders.action_cancel()
                        woo_instance_obj=self.env['woo.instance.ept']
                        instance=woo_instance_obj.search([('state','=','confirmed')], limit=1)
                        if instance:
                            wcapi = instance.connect_for_point_in_woo()   
                            point_response = wcapi.get('point')      
                            point_response_data = point_response.json()                
                            for point in point_response_data:
                                woo_order_id = point.get('order_id',False)     
                                woo_point = point.get('amount',False)   
                                if draft_sale_orders.woo_order_number == str(woo_order_id) and int(woo_point) < 0:
                                    getting_point = int(woo_point)
                                    draft_sale_orders.write({'getting_point': getting_point})
                                    point_date = datetime.today()
                                    self.env.cr.execute("select COALESCE(sum(getting_point),0) from point_history where partner_id=%s", (draft_sale_orders.partner_id.id,))    
                                    point_data = self.env.cr.fetchall()
                                    if point_data:
                                        current_point = point_data[0][0]
                                    self.env['point.history'].create({'partner_id': draft_sale_orders.partner_id.id,
                                                                      'date': point_date,
                                                                      'order_id': draft_sale_orders.id,
                                                                      'membership_id': draft_sale_orders.partner_id.membership_id.id,                                                      
                                                                      'balance_point': current_point + draft_sale_orders.getting_point,
                                                                      'getting_point': draft_sale_orders.getting_point,
                                                                    })
                                    break   
                        print ('odoo order cancelled')  
        return True                       

    #Update action from quotation to woo
    @api.model
    def update_woo_order_status_action(self,status):
        transaction_log_obj=self.env['woo.transaction.log']      
        instance=self.env['woo.instance.ept'].search([('state','=','confirmed')],limit=1)    
        if instance:
            wcapi = instance.connect_in_woo()            
            for sale_order in self: 
                if sale_order.woo_order_id:
                    info = {'status': status}
                    data = info
                    if instance.woo_version == 'old':                    
                        data = {'order':info}
                    response = wcapi.put('orders/%s'%(sale_order.woo_order_id),data)
                    if response.status_code not in [200,201]:
                        message = 'Error in update order %s status,  %s'%(sale_order.name,response.content)
                        log=transaction_log_obj.search([('woo_instance_id','=',instance.id),('message','=',message)])
                        if not log:
                            transaction_log_obj.create({'message':message,'mismatch_details':True,'type':'sales','woo_instance_id':instance.id})
        return True
    
    def update_sale_order_point(self, cr, uid, ids, context=None):
        
        for order in self.browse(cr, uid, ids, context=context):
            if order.woo_order_number or order.original_ecommerce_number:
                woo_instance_obj = self.pool.get('woo.instance.ept')
                instance_obj = woo_instance_obj.search(cr, uid, [('state', '=', 'confirmed')], limit=1)
                if instance_obj:
                    instance = woo_instance_obj.browse(cr, uid, instance_obj, context=context)
                    wcapi = instance.connect_for_product_in_woo()   
                    if order.woo_order_number: 
                        woo_order_id = order.woo_order_id
                        order_response = wcapi.get('orders/%s'%(woo_order_id))                    
                        order_res = order_response.json()                   
                        order_meta_data = order_res.get('meta_data')
                        if order_meta_data:
                            for order_meta in order_meta_data:
                                if order_meta.get('key') == 'ywpar_points_from_cart':                       
                                    getting_point = int(order_meta.get('value'))
                                    order.write({'getting_point': getting_point})   
                                    cr.execute("select COALESCE(sum(getting_point),0) from point_history where partner_id=%s", (order.partner_id.id,))    
                                    point_data = cr.fetchall()
                                    if point_data:
                                        history_point = point_data[0][0]
                                    point_vals = {  'partner_id': order.partner_id.id,
                                                    'date': datetime.today(),
                                                    'order_id': order.id,
                                                    'membership_id': order.partner_id.membership_id.id,                                                      
                                                    'balance_point': history_point + order.getting_point,
                                                    'getting_point': order.getting_point,
                                                }
                                    self.pool.get('point.history').create(cr, uid, point_vals, context=context)
                                    
    def create_sale_order_in_woo(self, cr, uid, ids, context=None):
        
        logging.warning("Check ids: %s", ids)  
        product_lists = []
        shipping_lists = []
        fee_lines_lists = []
        free_shipping_values = ''
        index = 0
        for order in self.browse(cr, uid, ids, context=context):
            if order.original_ecommerce_number:
                
                #change revised state of old woo sale order
                sale_order_obj = self.pool.get('sale.order').search(cr, uid, [('woo_order_id', '=', order.original_ecommerce_number)],context=context)
                if sale_order_obj:
                    sale_order = self.pool.get('sale.order').browse(cr, uid, sale_order_obj, context=context)
                    sale_order.update_woo_order_status_action('revised')
                
                woo_instance_obj = self.pool.get('woo.instance.ept')
                instance_obj = woo_instance_obj.search(cr, uid, [('state', '=', 'confirmed')], limit=1)
                if instance_obj:
                    instance = woo_instance_obj.browse(cr, uid, instance_obj, context=context)
                    wcapi = instance.connect_for_product_in_woo()  
                    
                    #calculate points for new woo sale order
                    point_wcapi = instance.connect_for_point_in_woo()
                    point_response = point_wcapi.get('points-conversion-rate-and-shipping-info')                    
                    point_data = point_response.json()  
                    money = point_data.get('money')
                    
                    getting_points = int(round(order.amount_total / float(money),0))
                    logging.warning("Check money: %s", money) 
                    logging.warning("Check getting_points: %s", getting_points) 
                    
                    #find free shipping to add shipping_lines
                    shipping_info = point_data.get('shipping_info')
                    logging.warning("Check shipping_info: %s", shipping_info)
                    if shipping_info:
                        shipping_title = shipping_info[1].get('title')
                        min_amount = shipping_info[1].get('min_amount')
                        
                        logging.warning("Check shipping_title: %s", shipping_title)
                        logging.warning("Check min_amount: %s", min_amount)
                        if shipping_title == 'Free Delivery' and order.amount_total >= float(min_amount):
                            sale_order_lines = self.pool.get('sale.order.line').search(cr, uid, [('order_id', '=', order.id),
                                                                                                 ('promotion_id', '=', False),
                                                                                                 ('sale_foc', '!=', True)],context=context)
                            logging.warning("Check sale_order_lines: %s", sale_order_lines)      
                            for so_line in sale_order_lines:
                                sol = self.pool.get('sale.order.line').browse(cr, uid, so_line, context=context)
                                index += 1
                                if index < len(sale_order_lines): 
                                    free_shipping_values +=  sol.product_id.name_template + ' &times; ' + str(sol.product_uom_qty) + ','
                                else:
                                    free_shipping_values +=  sol.product_id.name_template + ' &times; ' + str(sol.product_uom_qty)
                            logging.warning("Check free_shipping_values: %s", free_shipping_values) 
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
                            
                    #find fee_lines to add fee_lines for discount amount
                    discount_lines = self.pool.get('sale.order.line').search(cr, uid, [('order_id', '=', order.id),
                                                                                       ('promotion_id', '!=', False),
                                                                                       ('price_unit', '<', 0)],context=context)
                    logging.warning("Check discount_lines: %s", discount_lines)      
                    for discount_line in discount_lines:
                        discount_sol = self.pool.get('sale.order.line').browse(cr, uid, discount_line, context=context)
                        #to do
                        fee_lines_lists.append({
                                                "name": "Milo-UHT-180ml Buy 12 to 179 Get 3% Off",
                                                "tax_class": "0",
                                                "tax_status": "taxable",
                                                "amount": str(int(discount_sol.price_unit)),
                                                "total": str(int(discount_sol.price_unit))
                                            })
                    logging.warning("Check fee_lines_lists: %s", fee_lines_lists)
                    
                    #get old woo sale order info
                    woo_order_id = order.original_ecommerce_number
                    logging.warning("Check woo_order_id: %s", woo_order_id)  
                    order_response = wcapi.get('orders/%s'%(woo_order_id))                    
                    woo_order = order_response.json()                   
                    customer_id = woo_order.get('customer_id')
                    
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
                                        
                    logging.warning("Check customer_id: %s", customer_id) 
                    logging.warning("Check billing_first_name: %s", billing_first_name)  
                    logging.warning("Check shipping_first_name: %s", shipping_first_name) 
                    logging.warning("Check payment_method: %s", payment_method) 
                    
                    #find woo products to add line_items  
                    for line in order.order_line:
                        product_code = line.product_id.default_code
                        product_wcapi = instance.connect_for_point_in_woo()
                        if line.sale_foc == True:
                            product_code = product_code + "!"                            
                        product_response = product_wcapi.get('get-product-id-by-sku/%s' %product_code)
                        if product_response.status_code in [200,201]:                         
                            product_data = product_response.json()  
                            logging.warning("Check product_data: %s", product_data) 
                            if product_data:
                                logging.warning("Check product_data[0]: %s", product_data[0])
                                woo_product_id = product_data[0].get('id')
                                if line.sale_foc == True:
                                    product_lists.append({
                                                          "product_id": woo_product_id,
                                                          "quantity": line.product_uom_qty,
                                                          "price": 0
                                                        })
                                else:
                                    product_lists.append({
                                                          "product_id": woo_product_id,
                                                          "quantity": line.product_uom_qty                                                          
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
                                            }
                                        ],  
                            "line_items": product_lists,
                            "shipping_lines": shipping_lists,    
                            "fee_lines": fee_lines_lists                                                                           
                        }        
                    logging.warning("Check product_lists: %s", product_lists)
                    logging.warning("Check data: %s", data)                
                    create_order_response = wcapi.post("orders", data)
                    logging.warning("Check create_order_response status code: %s", create_order_response.status_code)
                    if create_order_response.status_code in [200,201]:     
                        created_order_data = create_order_response.json()
                        logging.warning("Check created_order_data: %s", created_order_data) 
                        order.write({'woo_order_id': created_order_data.get('id')})    
    
    #Add cancel_woo_order_action into order cancel action
    def action_cancel(self, cr, uid, ids, context=None):
        customer_id = None
        result = super(sale_order, self).action_cancel(cr, uid, ids, context=context)       
        if result:
            woo_instance_obj=self.pool.get('woo.instance.ept')
            instance=woo_instance_obj.search(cr, uid, [('state','=','confirmed')], context=context, limit=1)
            if instance:                
                woo_instance = woo_instance_obj.browse(cr, uid, instance[0], context=context)
                wcapi = woo_instance.connect_for_point_in_woo()   
            for sale in self.browse(cr, uid, ids, context=context):                
                if sale.woo_order_number:
                    update = sale.update_woo_order_status_action('cancelled')                    
                    one_signal_values = {
                                            'partner_id': sale.partner_id.id,
                                            'contents': "Your order " + sale.name + " is cancelled.",
                                            'headings': "Burmart"
                                        }     
                    self.pool.get('one.signal.notification.messages').create(cr, uid, one_signal_values, context=context)
                if sale.getting_point > 0:
                    getting_point = -sale.getting_point
                    sale.write({'getting_point':getting_point})
                    cr.execute("select COALESCE(sum(getting_point),0) from point_history where partner_id=%s", (sale.partner_id.id,))    
                    point_data = cr.fetchall()
                    if point_data:
                        history_point = point_data[0][0]
                    vals = { 'partner_id': sale.partner_id.id,
                             'date': datetime.today(),
                             'order_id': sale.id,
                             'membership_id': sale.partner_id.membership_id.id,                                                      
                             'balance_point': history_point + sale.getting_point,
                             'getting_point': sale.getting_point,
                            }
                    self.pool.get('point.history').create(cr, uid, vals, context=context)
                    if wcapi:
                        order_response = wcapi.get('point')      
                        order_response_data = order_response.json()                
                        for order in order_response_data:
                            woo_order_number = order.get('number',False)     
                            if sale.woo_order_number == woo_order_number:
                                customer_id = order.get('customer_id',False) 
                                break
                        data = { 'user_id': customer_id,
                                 'action': 'order_cancelled',
                                 'order_id': sale.woo_order_number,
                                 'amount': sale.getting_point,                                                                 
                                }                        
                        wcapi.post("point", data)
        return result
    
    #Fix Order Confirm Fail For Local
    def action_button_confirm(self, cr, uid, ids, context=None):
        result = super(sale_order, self).action_button_confirm(cr, uid, ids, context=context)
        self.write(cr, uid, ids, {'state':'manual'})
#         if result:
#             for sale in self.browse(cr, uid, ids, context=context):                
#                 if sale.woo_order_number:    
#                     update = sale.update_woo_order_status_action('processing')         
#                     one_signal_values = {
#                                          'partner_id': sale.partner_id.id,
#                                          'contents': "Your order " + sale.name + " is confirmed.",
#                                          'headings': "Burmart"
#                                         }                          
#                     self.pool.get('one.signal.notification.messages').create(cr, uid, one_signal_values, context=context)                  
        return result

    #update woo order status when update 'is_generate' and 'shipped' 
    def write(self, cursor, user, ids, vals, context=None):
        result = super(sale_order, self).write(cursor, user, ids, vals, context=context)
        if result:
            current_so = self.browse(cursor, user, ids, context=context)
            if vals.get('is_generate') == True and current_so.woo_order_number:
                current_so.update_woo_order_status_action('misha-shipment')           
        return result
    
    @api.multi
    def update_order_status_from_woo(self,woo_order_id,state):
        instance=self.env['woo.instance.ept'].search([('state','=','confirmed')],limit=1)    
        current_so = self.search([('woo_order_id','=',woo_order_id)])
        if not current_so:
            result = {"error_descrip": "Sale Order Not Found!", "error": "invalid_woo_order_id"}
        elif current_so.state not in ['done']:
            result = current_so.write({'state':state})        
        return result

class sale_order_line(models.Model):
    _inherit="sale.order.line"
    
    woo_line_id=fields.Char("woo Line")
    
class import_order_status(models.Model):
    _name="import.order.status"
    
    name=fields.Char("Name")
    status=fields.Char("Status")