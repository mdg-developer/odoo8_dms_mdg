from openerp.osv import osv, fields
from openerp import netsvc
from openerp.tools.translate import _
from openerp import tools
import logging
from pyfcm import FCMNotification
 
####
# LOGGER = netsvc.Logger()
LOGGER = logging.getLogger(__name__)

DEBUG = True
PRODUCT_UOM_ID = 1

ATTRIBUTES = [

    ('amount_total', 'Total Amount'),
    ('product_product', 'Product Code'),
    ('product_cat', 'Product Category'),
    ('prod_qty', 'Product Quantity combination'),
    ('prods_qty', 'Multiple Product Quantity combination'),
    ('prods_multi_uom_qty', 'Multiple Product UOM Combination'),
    ('multi_prod_sale_amt', 'Multiple Product SubTotal combination'),
    # ('prod_unit_price', 'Product UnitPrice combination'),
    ('prod_sub_total', 'Product SubTotal combination'),
    ('promo_already_exit', 'Promotion Already Applied'),
    ('cat_qty', 'Product Category Quantity combination'),  
    ('cat_total', 'Product Category Sale Total'),   
    ('fix_prods_qty', 'Fix Quantity Total combination'),

]

COMPARATORS = [
    ('==', _('equals')),
    ('!=', _('not equal to')),
    ('>', _('greater than')),
    ('>=', _('greater than or equal to')),
    ('<', _('less than')),
    ('<=', _('less than or equal to')),
    ('in', _('is in')),

    ('not in', _('is not in')),
]

ACTION_TYPES = [
    ('prod_disc_perc', _('Discount % on Product')),
    ('prod_disc_fix', _('Fixed amount on Product')),
    
  #  ('cart_disc_perc', _('Discount % on Sub Total')),
    ('cart_disc_fix', _('Fixed amount on Sub Total')),
    ('disc_perc_on_grand_total', _('Discount % on Grand Total')),
    ('fix_amt_on_grand_total', _('Fix Amount on Grand Total')),
    ('discount_on_categ', _('Discount % on Product Category')),

   # ('foc_on_categ', _('FOC on Product Category')),
    # ('discount_on_total', _('Fixed amount on Sub Total')),
    ('prod_x_get_y', _('Buy X get Y free')),
    ('buy_cat_get_x', _('Buy Category get X free')),
    ('buy_cat_get_x_cat', _('Buy Category get X Category free')),

    ('prod_x_get_x', _('Buy X get X free')),
    ('prod_multi_get_x', _('Buy Multi Products get X free')),
    ('prod_multi_get_x_conds', _('Buy Multi Products get X free by Condition')),
    ('prod_multi_uom_get_x', _('Buy Multi UOM get X free')),
    ('prod_multi_ratio_x',_('Buy Multi Product Ratio get X free')),
    ('fix_qty_on_product_code', _('FOC Products on Qty')),
    ('prod_foc_smallest_unitprice', _('FOC Products on smallest Unitprice')),
    ('foc_any_product', _('FOC Any Products by Ratio')),
	('prod_fix_amt_disc_subtotal', _('Product Fix Amount on Sub Total')),
    ('prod_dis_double', _('Double Discount % on SubTotal')),
    ('prod_multi_get_x_by_limit', _('Buy Multi Products get X free By Limit')),
    ('foc_any_prod_fix', _('FOC Any Product by Fix')),
]




# ##sale.order call that apply_promotions 
class PromotionsRules(osv.Model):
    "Promotion Rules"
    _name = "promos.rules"
    _description = __doc__
    _order = 'sequence'

    def _check_positive_number(self, cr, uid, ids, context=None):
        record = self.browse(cr, uid, ids, context=context)
        for data in record:
            if data.coupon_used < 0:
                return False
        return True
    
    def count_coupon_use(self, cursor, user, ids,
                          name, arg, context=None):
        '''
        This function count the number of sale orders(not in cancelled state)
        that are linked to a particular coupon.
        @param cursor: Database Cursor
        @param user: ID of User
        @param ids: ID of Current record.
        @param name: Name of the field which calls this function.
        @param arg: Any argument(here None).
        @param context: Context(no direct use).
        @return: No. of of sale orders(not in cancelled state)
                that are linked to a particular coupon
        '''
        sales_obj = self.pool.get('sale.order')
        res = {}
        for promotion_rule in self.browse(cursor, user, ids, context):
            matching_ids = []
            if promotion_rule.coupon_code:
                # If there is uses per coupon defined check if its overused
                if promotion_rule.uses_per_coupon > -1:
                    matching_ids = sales_obj.search(cursor, user,
                            [
                            ('coupon_code', '=', promotion_rule.coupon_code),
                            ('state', '<>', 'cancel')
                            ], context=context)
                    
            res[promotion_rule.id] = len(matching_ids)
        return res
    
    _columns = {
        
        'name':fields.char('Promo Name', size=50, required=True),
        'description':fields.text('Description'),
        'active':fields.boolean('Active'),
        
        'special':fields.boolean('Special'),
        'special1':fields.boolean('Special 1'),
        'special2':fields.boolean('Special 2'),
        'special3':fields.boolean('Special 3'),
        'stop_further':fields.boolean('Stop Checks',
                              help="Stops further promotions being checked"),
        # 'main_group': fields.many2one('product_product.maingroup','Main Group'),
        'monthly_promotion':fields.boolean('Monthly Promotion'),
        'promotion_count':fields.integer('Number Of Promotion Count'),
        'category_ids': fields.many2many('res.partner.category', 'promotion_rule_category_rel', 'promotion_id', 'category_id', 'Customer Tags'),
        'partner_categories':fields.many2many(
                  'res.partner.category',
                  'rule_partner_cat_rel',
                  'category_id',
                  'rule_id',
                  string="Partner Categories",
                  help="Applicable to all if none is selected"
                                              ),
        'coupon_code':fields.char('Coupon Code', size=20),
        'uses_per_coupon':fields.integer('Uses per Coupon'),
        'uses_per_partner':fields.integer('Uses per Partner'),
        'coupon_used':fields.integer('Number of Coupon Uses', required=True),
        'from_date':fields.datetime('From Date'),
        'to_date':fields.datetime('To Date'),
        'sequence':fields.integer('Sequence'),
        'sale_channel_id':fields.many2many('sale.channel', 'promo_sale_channel_rel', 'promo_id', 'sale_channel_id', string='Sale Channel'),
        'logic':fields.selection([
                            ('and', 'All'),
                            ('or', 'Any'),
                                  ], string="Logic", required=True),
        'expected_logic_result':fields.selection([
                            ('True', 'True'),
                            ('False', 'False')
                                    ], string="Output", required=True),
  'expressions':fields.one2many(
                            'promos.rules.conditions.exps',
                            'promotion',
                            string='Expressions/Conditions',copy=True
                            ),
        'actions':fields.one2many(
                    'promos.rules.actions',
                    'promotion',
                    string="Actions",copy=True
                        ),
        'main_group':fields.many2one('product.maingroup', 'Main Group'),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('approve', 'Approved'),
            ], 'Status', readonly=True, copy=False, help="Gives the status of the quotation or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True),
        'outlettype_id':fields.many2many('outlettype.outlettype', 'promos_rules_outlettype_rel' , 'promos_rules_id' ,'outlettype_id' , string='Outlet Type'),
        'branch_id':fields.many2many('res.branch', string='Branch'),
        'customer_ids':fields.many2many('res.partner'),
        'product_ids':fields.many2many('product.product', 'promos_rules_product_rel' , 'promos_rules_id' ,'product_id' , string='Product'),
        'join_promotion_ids':fields.many2many('promos.rules', 'promos_rules_join_rel' , 'promos_rules_id' ,'join_promotion_id' , string='Monthly Join Promotions'),
#         'promotion_id_a':fields.many2one('promos.rules','Other Promotion A'),
#         'promotion_id_b':fields.many2one('promos.rules' ,'Other Promotion B'),
#         'promotion_id_c':fields.many2one('promos.rules' ,'Other Promotion C'),
        
    }
    _defaults = {
        'logic':lambda * a:'and',
        'expected_logic_result':lambda * a:'True',
        'coupon_used': '0',
        'state':'draft',
    }
    _constraints = [(_check_positive_number, 'Coupon Use must be Positive', ['coupon_used'])]
	
    def approve(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'approve'})


    def publish(self, cr, uid, ids, context=None):
        fcm_api_key = self.pool.get('ir.config_parameter').get_param(cr, uid, 'fcm_api_key', default=False, context=context)
        push_service = FCMNotification(api_key=fcm_api_key)
        # data = self.browse(cr, uid, ids)[0]
        crm_obj = self.pool.get('crm.case.section')
        tablet_obj = self.pool.get('tablets.information')
        # title = data.title
        #  body = data.body
        #  tag = data.reason
        result = {}
        msg_title = "Promotion has be chage"
        message = "Ready to update"
        msg_tag = ""
        
        if ids:
            cr.execute("select id from crm_case_section ")
            team_id = cr.fetchall()

            registration_ids=[]
            for data in team_id:
                tablet_ids = tablet_obj.search(cr,uid,[('sale_team_id','in',data)])
                for tablet_id in tablet_ids:
                    tablet_data = tablet_obj.browse(cr,uid,tablet_id,context)
                    if tablet_data.token:
                        registration_ids.append(tablet_data.token);                
            result = push_service.notify_multiple_devices(registration_ids=registration_ids,  message_body=message, message_title= msg_title, tag=msg_tag)
        return True        
    
    def promotion_date(self, str_date):
        "Converts string date to date"
        import time
        try:
            return time.strptime(str_date, '%Y-%m-%d %H:%M:%S') 
        except:
            try:
                return time.strptime(str_date, '%Y-%m-%d')
            except:
                return str_date
            
        
    # Check the Condition
    def check_primary_conditions(self, cursor, user,
                                  promotion_rule, order, expression, context):
        
        """
        Checks the conditions for 
            Coupon Code
            Validity Date
        @param cursor: Database Cursor
        @param user: ID of User
        @param promotion_rule: Browse record sent by calling func. 
        @param order: Browse record sent by calling func.
        @param context: Context(no direct use).
        """
        # Check if the customer is in the specified partner cats
        if promotion_rule.partner_categories:
                applicable_ids = [
                                  category.id \
                                  for category in promotion_rule.partner_categories
                                  ]
                partner_categories = [
                        category.id \
                            for category in order.partner_id.category_id
                                ]
                if not set(applicable_ids).intersection(partner_categories):
                    raise Exception("Not applicable to Partner Category")
                if promotion_rule.coupon_code:
                # If the codes don't match then this is not the promo 
                # if not order.coupon_code == promotion_rule.coupon_code:
                #   raise Exception("Coupon codes do not match")
                # Calling count_coupon_use to check whether no. of 
                # uses is greater than allowed uses.
                    count = self.count_coupon_use(cursor, user, [promotion_rule.id],
                                           True, None, context).values()[0]
                if count > promotion_rule.uses_per_coupon:
                    raise Exception("Coupon is overused")
            # If a limitation exists on the usage per partner
#         if promotion_rule.uses_per_partner > -1:
#                 matching_ids = sales_obj.search(cursor, user,
#                          [
#                           ('partner_id', '=', order.partner_id.id),
#                           ('coupon_code', '=', promotion_rule.coupon_code),
#                           ('state', '<>', 'cancel')
#                           ], context=context)
        print '10 Mile Causine10 Mile Causine10 Mile Causine',promotion_rule.name
        is_branch=False
        is_outlet=False
        is_channel=False
        is_customer=False
        partner_id=order.partner_id.id
        team_id=order.section_id.id
        cursor.execute("select res_branch_id from promos_rules_res_branch_rel where promos_rules_id = %s",(promotion_rule.id,))
        promo_branch_id=cursor.fetchall()
        cursor.execute("select outlettype_id from promos_rules_outlettype_rel where promos_rules_id =%s",(promotion_rule.id,))
        promo_outlet_type=cursor.fetchall()
        cursor.execute("select sale_channel_id  from promo_sale_channel_rel  where promo_id=%s",(promotion_rule.id,))
        promo_sale_channel_id=cursor.fetchall()
        cursor.execute("select res_partner_id  from promos_rules_res_partner_rel where promos_rules_id = %s",(promotion_rule.id,))
        promo_res_partner_id=cursor.fetchall()
        # Check date is valid date during promotion date
        if promo_branch_id:
            cursor.execute("select branch_id from crm_case_section where id=%s and branch_id in %s",(team_id,tuple(promo_branch_id),))
            team_branch_id=cursor.fetchone()
            if team_branch_id:
                is_branch=True
        else:
            is_branch=True
            
        if promo_outlet_type:
            cursor.execute("select outlet_type from res_partner where id=%s and outlet_type in %s",(partner_id,tuple(promo_outlet_type),))
            team_outlet_type=cursor.fetchone()
            if team_outlet_type:
                is_outlet=True
        else:
            is_outlet=True  
                 
        if promo_sale_channel_id:
            cursor.execute("select sale_channel_id,sale_team_id from sale_team_channel_rel where sale_team_id =%s and sale_channel_id in %s",(team_id,tuple(promo_sale_channel_id),))
            team_channel_id=cursor.fetchone()
            if team_channel_id:
                is_channel=True
        else:
            is_channel=True      
            
        if promo_res_partner_id:
            cursor.execute("select id from res_partner where id in %s and id =%s",(tuple(promo_res_partner_id),partner_id,))          
            team_customer_id=cursor.fetchone()
            if team_customer_id:
                is_customer=True
        else:
                is_customer=True  
                          
        print 'is_branchis_branchis_branchis_branch',is_branch,is_outlet,is_channel,is_customer
                
        if is_branch==True and is_outlet ==True and is_channel==True and is_customer==True:
            # for total amount for condition expression
            cursor.execute("select attribute,value,comparator from promos_rules_conditions_exps where id=%s", (expression.id,))
            datas = cursor.fetchone()
            attribute = datas[0]
            value = datas[1]
            comparator = datas[2]
           
            # for checking product_product code
            # cursor.execute("select attribute,value,comparator from promos_rules_conditions_exps where promotion=%s",(promotion_rule.id,))
            
            # Check attribute total amount
            if attribute == 'amount_total':
                svalue = eval(value)
                if comparator == '==':
                    if order.amount_total == svalue:
                        return True
                elif comparator == '!=':    
                        if order.amount_total != svalue:
                            return True
                elif comparator == '>':
                        if order.amount_total > svalue:
                            return True
                elif comparator == '<':    
                        if order.amount_total < svalue:
                            
                            return True
                elif comparator == '>=':
                        if order.amount_total >= svalue:
                            
                            return True
                elif comparator == '<=':    
                        if order.amount_total <= svalue:
                            return True
            # Check attribute is product_product codes    
            elif attribute == 'product_product':
                svalue = eval(value)
                if comparator == 'in' or comparator == '==':
                    for order_line in order.order_line:        
                        if order_line.product_id.default_code == svalue:
                            return True  
            # Check attribute is product_product category           
            elif attribute == 'product_cat':
                svalue = eval(value)
                if comparator == 'in' or comparator == '==':
                    for order_line in order.order_line:
                        cat_name = order_line.product_id.categ_id.name
                        category_name1 = str(cat_name)
                        cat_value1 = str(svalue)
                        category_name = category_name1.strip() 
                        cat_value = cat_value1.strip() 
                       
                        if category_name == cat_value:
                            return True  
            # Check attribute is product_product quantity  
            # MMK
            elif attribute == 'prod_qty':
                svalue = value.split(":")
                print 'svaluesvalue',svalue
                product_code = eval(svalue[0])
                product_qty = eval(svalue[1])
                LOGGER.info("Product Code : %s ", product_code)
                LOGGER.info("Condition Qty : %s ", product_qty)
                con_qty = 0
                for order_line in order.order_line:   
                    if order_line.product_id.default_code == product_code:
                        if order_line.product_uom.id == order_line.product_id.product_tmpl_id.big_uom_id.id:                                                                          
                            cursor.execute("select floor(round(1/factor,2)) as ratio from product_uom where active = true and id=%s", (order_line.product_uom.id,))
                            bigger_qty = cursor.fetchone()[0]
                            bigger_qty = int(bigger_qty)
                            con_qty += bigger_qty * order_line.product_uom_qty           
                        else:             
                            con_qty += order_line.product_uom_qty
                LOGGER.info("Order Line qty : %s ", con_qty)
                if comparator == '==':
                    if con_qty == product_qty:
                        LOGGER.info("Equal")
                        return True
                     
                elif comparator == '!=':    
                    if con_qty != product_qty:
                        LOGGER.info("Not Equal")
                        return True
                elif comparator == '>':
                    if con_qty > product_qty:
                        LOGGER.info("Greater Than")
                        return True
                elif comparator == '<':    
                    if con_qty < product_qty:
                        LOGGER.info("Less Than")
                        return True
                elif comparator == '>=':
                    if con_qty >= product_qty:
                        LOGGER.info("Greater Than Or Equal")
                        return True
                elif comparator == '<=':    
                    if con_qty <= product_qty:
                        LOGGER.info("Less Than Or Equal")
                        return True
            # Check attribute is product_product category quantity  
            elif attribute == 'cat_qty':
                tota_qty = 0.0
                svalue = value.split(":")
                category_code = eval(svalue[0])
                product_qty = eval(svalue[1])
                
                for order_line in order.order_line:  
                        
                        cat_name = order_line.product_id.categ_id.name
                        category_name1 = str(cat_name)
                        cat_value1 = str(category_code)
                        category_name = category_name1.strip() 
                        cat_value = cat_value1.strip() 
                        
                        if category_name == cat_value:
                            if order_line.product_uom.id == order_line.product_id.product_tmpl_id.big_uom_id.id:                                                                          
                                cursor.execute("select floor(round(1/factor,2)) as ratio from product_uom where active = true and id=%s", (order_line.product_uom.id,))
                                bigger_qty = cursor.fetchone()[0]
                                bigger_qty = int(bigger_qty)
                                tota_qty += bigger_qty * order_line.product_uom_qty
                            else:         
                                tota_qty += order_line.product_uom_qty
                if comparator == '==':
                    if tota_qty == product_qty:
                        return True
                elif comparator == '!=':    
                    if tota_qty != product_qty:
                        return True
                elif comparator == '>':
                    if tota_qty > product_qty:
                        return True
                elif comparator == '<':    
                    if tota_qty < product_qty:
                        return True
                elif comparator == '>=':
                    if tota_qty >= product_qty:
                        return True
                elif comparator == '<=':    
                    if tota_qty <= product_qty:
                        return True                
                    
            # Check attribute is sub total amount                
            elif attribute == 'prod_sub_total':   
                svalue = value.split(":")
                product_code = eval(svalue[0])
                sub_total = eval(svalue[1])
                #big uom not change
                for order_line in order.order_line:   
                    if order_line.product_id.default_code == product_code:
                        order_subtotal = (order_line.product_uom_qty * order_line.price_unit)
                        
                        if comparator == '==':
                            if order_subtotal == sub_total:
                                return True
                             
                        elif comparator == '!=':    
                            if order_subtotal != sub_total:
                                return True
                        elif comparator == '>':
                            if order_subtotal > sub_total:
                                return True
                        elif comparator == '<':    
                            if order_subtotal < sub_total:
                                return True
                        elif comparator == '>=':
                            if order_subtotal >= sub_total:
                                return True
                        elif comparator == '<=':    
                            if order_subtotal <= sub_total:
                                return True 
            # Check Multiproduct quantity combination                   
            elif attribute == 'prods_qty':
                svalue = value.split("|")
                product_codes = svalue[0]
                product_code = product_codes.split(";")
                
                
                product_qty = eval(svalue[1])
                qtys = 0.0
                for order_line in order.order_line:  
                    for p_code in product_code: 
                        
                        if order_line.product_id.default_code == eval(p_code):
                            if order_line.product_uom.id == order_line.product_id.product_tmpl_id.big_uom_id.id:                                                                          
                                cursor.execute("select floor(round(1/factor,2)) as ratio from product_uom where active = true and id=%s", (order_line.product_uom.id,))
                                bigger_qty = cursor.fetchone()[0]
                                bigger_qty = int(bigger_qty)
                                qtys += bigger_qty * order_line.product_uom_qty
                            else:                            
                                qtys += order_line.product_uom_qty
 
                if comparator == '==':
                    if qtys == product_qty:
                        return True
                elif comparator == '!=':    
                    if qtys != product_qty:
                        return True
                elif comparator == '>':
                    if qtys > product_qty:
                        return True
                elif comparator == '<':    
                    if qtys < product_qty:
                        return True
                elif comparator == '>=':
                    if qtys >= product_qty:
                        return True
                elif comparator == '<=':    
                    if qtys <= product_qty:
                        return True
            # Check attribute is multiproduct uom qty combination
            elif(attribute == 'prods_multi_uom_qty'):
                svalue = value.split(':')
                codes = svalue[0]
                quantity = eval(svalue[1])
                pcodes = codes.split("|") 
                product_codes = pcodes[0]
                uom_qtys = pcodes[1]
                product_code = product_codes.split(";")
                uom_qty = uom_qtys.split(";")
                qtys = 0.0
                #big uom not change
                for order_line in order.order_line:  
                    for p_code in product_code: 
                        if order_line.product_id.default_code == eval(p_code):
                            LOGGER.info("Product Code is Same")
                            product_id_index = product_code.index(p_code)
                            product_qty = uom_qty[product_id_index]
                            qtys += int(order_line.product_uom_qty / int(product_qty))
                LOGGER.info("Total Quantity >>> %s ", qtys)
                if comparator == '==':
                    if qtys == quantity:
                        return True
                elif comparator == '!=':    
                    if qtys != quantity:
                        return True
                elif comparator == '>':
                    if qtys > quantity:
                        return True
                elif comparator == '<':    
                    if qtys < quantity:
                        return True
                elif comparator == '>=':
                    if qtys >= quantity:
                        return True
                elif comparator == '<=':    
                    if qtys <= quantity:
                        return True       
                    
            elif attribute == 'fix_prods_qty':
                print 'expression',expression,promotion_rule
                svalue = value.split(":")
                product_code = svalue[0] 
                #product_code = product_code.split(" ")                
                product_qty = eval(svalue[1])
                con_product_qty=0
                qtys = 0.0
                ori_qtys=0.0
                cursor.execute("select comparator,value from promos_rules_conditions_exps where promotion= %s and id!=%s and attribute='fix_prods_qty' ",(promotion_rule.id,expression.id))
                data=cursor.fetchone()
                if data:
                    data_comparator =data[0]
                    value=data[1]
                    svalue = value.split(":")
                    con_product_codes = svalue[0]
                    con_product_qty = eval(svalue[1])
                    #   con_product_codes = con_product_codes.split("'")                

                    for order_line in order.order_line:  
                            if order_line.product_id.default_code ==eval(con_product_codes):
                                if order_line.product_uom.id == order_line.product_id.product_tmpl_id.big_uom_id.id:                                                                          
                                    cursor.execute("select floor(round(1/factor,2)) as ratio from product_uom where active = true and id=%s", (order_line.product_uom.id,))
                                    bigger_qty = cursor.fetchone()[0]
                                    bigger_qty = int(bigger_qty)
                                    qtys += bigger_qty * order_line.product_uom_qty                                
                                else:
                                    qtys += order_line.product_uom_qty
                    result=False
                    total_result= False
                    if data_comparator == '==':
                        if qtys == con_product_qty:
                            result= True
                    elif data_comparator == '!=':    
                        if qtys != con_product_qty:
                            result= True
                    if data_comparator == '>':
                        if qtys > con_product_qty:
                            result= True
                    elif data_comparator == '<':    
                        if qtys < con_product_qty:
                            result= True
                    elif data_comparator == '>=':
                        if qtys >= con_product_qty:
                            result =True
                    elif data_comparator == '<=':    
                        if qtys <= con_product_qty:
                            result =True 

                total=product_qty + con_product_qty
                default=con_product_codes + ','+product_code
                default=eval(default)
                if result==True:
                    cursor.execute("select sum(sol.product_uom_qty),sol.product_id,sol.product_uom from sale_order_line sol,product_product pp where sol.product_id=pp.id and sol.order_id=%s and pp.default_code in %s",(order.id,default,))
                    data=cursor.fetchone()
                    if data:
                        prod_qty=data[0]
                        product_id=data[1]
                        product_uom=data[2]
                        product = self.pool.get('product.product').browse(cursor, user, product_id, context=context)
                        if product_uom == product.product_tmpl_id.big_uom_id.id:                                                                          
                            cursor.execute("select floor(round(1/factor,2)) as ratio from product_uom where active = true and id=%s", (product.product_tmpl_id.big_uom_id.id,))
                            bigger_qty = cursor.fetchone()[0]
                            bigger_qty = int(bigger_qty)
                            toal_prod_qty = bigger_qty * prod_qty
                        else:                        
                            toal_prod_qty=prod_qty

                    if comparator == '==':
                        if toal_prod_qty == total:
                            total_result= True
                    elif comparator == '!=':    
                        if toal_prod_qty != total:
                            total_result= True
                    if comparator == '>':
                        if toal_prod_qty > total:
                            total_result= True
                    elif comparator == '<':    
                        if toal_prod_qty < total:
                            total_result= True
                    elif comparator == '>=':
                        if toal_prod_qty >= total:
                            total_result= True
                    elif comparator == '<=':    
                        if toal_prod_qty <= total:
                            total_result= True                
                            
                if result ==True and total_result==True: 
                    for order_line in order.order_line:  
                            if order_line.product_id.default_code ==eval(product_code):
                                if order_line.product_uom.id == order_line.product_id.product_tmpl_id.big_uom_id.id:                                                                          
                                    cursor.execute("select floor(round(1/factor,2)) as ratio from product_uom where active = true and id=%s", (product.product_tmpl_id.big_uom_id.id,))
                                    bigger_qty = cursor.fetchone()[0]
                                    bigger_qty = int(bigger_qty)
                                    ori_qtys += bigger_qty * order_line.product_uom_qty      
                                else:                                 
                                    ori_qtys += order_line.product_uom_qty          
                                    
                    if comparator == '==':
                        if ori_qtys == product_qty:
                            return True
                    elif comparator == '!=':    
                        if ori_qtys != product_qty:
                            return True
                    if comparator == '>':
                        if ori_qtys > product_qty:
                            return True
                    elif comparator == '<':    
                        if ori_qtys < product_qty:
                            return True
                    elif comparator == '>=':
                        if ori_qtys >= product_qty:
                            return True
                    elif comparator == '<=':    
                        if ori_qtys <= product_qty:
                            return True                    
        return False
       
    def evaluate(self, cursor, user, promotion_rule, order, context=None):
        """
        Evaluates if a promotion is valid
        @param cursor: Database Cursor
        @param user: ID of User
        @param promotion_rule: Browse Record
        @param order: Browse Record
        @param context: Context(no direct use).
        """
        if not context:
            context = {}
            # Now to the rules checking
        expected_result = eval(promotion_rule.expected_logic_result)  # True,False
        logic = promotion_rule.logic  # All ,Any
        # MMK I'm just fix a little missing codeI'm just fix a little missing code
        condition = False
        # Evaluate each expression
        # For and logic, any False is completely false
        # MMK I'm just fix a little missing codeI'm just fix a little missing code
        if (logic == 'and' and expected_result == True):
            LOGGER.info("And Condition and Expression TRUE")
            for expression in promotion_rule.expressions:
                result = self.check_primary_conditions(
                                        cursor, user,
                                        promotion_rule, order, expression,
                                        context)
                
                if result == True:
                    condition = result
                else:
                    condition = result
                    break
            if condition == True:
                return True
            else:
                return False

        if (logic == 'or' and expected_result == True):
            LOGGER.info("Or Condition and Expression TRUE")
            for expression in promotion_rule.expressions:
                result = self.check_primary_conditions(
                                        cursor, user,
                                        promotion_rule, order, expression,
                                        context)
                
                if result == True:
                    return True
                
        if (logic == 'and' and expected_result == False):
            LOGGER.info("And Condition and Expression False")
            for expression in promotion_rule.expressions:
                result = self.check_primary_conditions(
                                        cursor, user,
                                        promotion_rule, order, expression,
                                        context)
                
                if result == True:
                    condition = False
                    break
                else:
                    condition = True
            if condition == True:
                return True
            else:
                return False
            
        if (logic == 'or' and expected_result == False):
            LOGGER.info("Or Condition and Expression FALSE")
            for expression in promotion_rule.expressions:
                result = self.check_primary_conditions(
                                        cursor, user,
                                        promotion_rule, order, expression,
                                        context)
                
                if result == False:
                    return True
        
    def execute_actions(self, cursor, user, promotion_rule,
                            order_id, context):
        """
        Executes the actions associated with this rule
        @param cursor: Database Cursor
        @param user: ID of User
        @param promotion_rule: Browse Record
        @param order_id: ID of sale order
        @param context: Context(no direct use).
        """
        
        action_obj = self.pool.get('promos.rules.actions')
        if DEBUG:
            LOGGER.debug('Promotions Applying promo %s to %s',
                         promotion_rule.id, order_id)
        order = self.pool.get('sale.order').browse(cursor, user,
                                                   order_id, context)
        for action in promotion_rule.actions:
            # try:
            
            data=action_obj.execute(cursor, user, action.id,
                                   order, context=None)
            if data!=True:
                data=data
            else:
                data=True

        return data
        
        
    def apply_promotions(self, cursor, user, order_id, context=None):
        """
        Applies promotions
        @param cursor: Database Cursor
        @param user: ID of User
        @param order_id: ID of sale order
        @param context: Context(no direct use).
        """
        ####saleorder promotion line 
        # 1.promo_line_id
        # 2.pro_id
        result = {}
        # flag=True
        # cursor.execute('update sale_order set promo_state=True where id = %s', (order_id,))
        order = self.pool.get('sale.order').browse(cursor, user,
                                                   order_id, context=context)
        date_order=order.date_order
        partner_id=order.partner_id
        team_id=order.section_id
        branch_id=order.section_id.branch_id.id
        active_promos=[]
#         active_promos = self.search(cursor, user,
#                                     [('active', '=', True),('from_date', '<=', date_order),('to_date', '>=', date_order)],
#                                     context=context)
        cursor.execute("select id from promos_rules where active=True and from_date <= %s and  to_date >=%s order by sequence asc",(date_order,date_order,))
        active_data=cursor.fetchall()
        print 'active_promos',
        for data_pro in active_data:
            print ' data_pro',data_pro
            active_promos.append(data_pro[0])
        print 'active_promos',active_promos
        for promotion_rule in self.browse(cursor, user,
                                          active_promos, context):
            result = self.evaluate(cursor, user,
                                   promotion_rule, order,
                                   context)
            data=True
            
            # MMK I'm just fix a little missing codeI'm just fix a little missing code
            # Apply Promotions Here
            # And so yin result ka true phit ya mal
            # OR so yin result ka false phit ya mal   
            if result:
                data=self.execute_actions(cursor, user,
                                  promotion_rule, order_id,
                                  context)
                
            if  data!=True:
                return data
                # If stop further is true
            if promotion_rule.stop_further:
                    return True
                
                
        return False
            

PromotionsRules()


class PromotionsRulesConditionsExprs(osv.Model):
    "Expressions for conditions"
    _name = 'promos.rules.conditions.exps'
    _description = __doc__
    _order = "sequence"
    _rec_name = 'serialised_expr'
   
   
   
    
    def on_change(self, cursor, user, ids=None,
                   attribute=None, value=None, context=None):
        """
        Set the value field to the format if nothing is there
        @param cursor: Database Cursor
        @param user: ID of User
        @param ids: ID of current record.
        @param attribute: attribute sent by caller.
        @param value: Value sent by caller.
        @param context: Context(no direct use).
        """
        # If attribute is not there then return.
        # Will this case be there?
        if not attribute:
            return {}
        # If value is not null or one of the defaults
        if not value in [
                         False,
                         "'product_code'",
                         "'product_code',0.00",
                         "['product_code','product_code2']|0.00",
                         "0.00",
                         ]:
            return {}
        # Case 1
        if attribute == 'product_product':
            return {
                    'value':{
                             'value':"'product_code'"
                             }
                    }
            
            # Case 2
        if attribute == 'product_cat':
            return {
                    'value':{
                             'value':"'category_code'"
                             }
                    }
    
            
        # Case 3
        if attribute in [
                         'prod_qty',
                         'prod_unit_price',
                         'prod_sub_total',
                         'prod_discount',
                         'prod_weight',
                         'prod_net_price',                          

                         ]:
            return {
                    'value':{
                             'value':"'product_code':0.00"
                             }
                    }
        # Case 4
        if attribute in [
                         'promo_already_exit',
                         
                         ]:
            return {
                    'value':{
                             'value':"'promo_name'"
                             }
                    }
        # Case 5    
        if attribute in ['prods_qty']:
            return{
                    'value':{
                             'value':"'product_code1';'product_code2'|0.00"
                             }
               }
            
        if attribute in ['multi_prod_sale_amt']:
            return{
                    'value':{
                             'value':"'product_code1';'product_code2'|0.00"
                             }
               }
        
        # Case 6   
        if attribute in ['prods_multi_uom_qty']:
            return {
                    'value':{
                              'value':"'p1';'p2';'p3'|p1_uom;p2_uom;p3_uom:0.00"

                             }
                    }
        # Case 7
        if attribute in [
                         'comp_sub_total',
                         'comp_sub_total_x',
                         ]:
            return {
                    'value':{
                             'value':"['product_code','product_code2']|0.00"
                             }
                    }
        # Case 8
        if attribute in [
                         'amount_untaxed',
                         'amount_tax',
                         'amount_total',
                         ]:
            return {
                    'value':{
                             'value':"0.00"
                             }
                    }
            
            # Case 9
        if attribute in [
                         'cat_qty',
                        
                         ]:
            return {
                    'value':{
                             'value':"'category_code':0.00"
                             }
                    }
            
        if attribute in [
                         'cat_total',
                        
                         ]:
            return {
                    'value':{
                             'value':"'category_code':0.00"
                             }
                    }
            
            
            
        if attribute == 'fix_prods_qty':
            return {
                    'value':{
                             'value':"'product_code1';'product_code2':0.00|'product_code3':0.00"
                             }
                    }                  
            
        return {}
    _columns = {
        'sequence':fields.integer('Sequence'),
        'attribute':fields.selection(ATTRIBUTES, 'Attribute', size=50, required=True),
        'comparator':fields.selection(COMPARATORS, 'Comparator', required=True),
        'value':fields.char('Value'),
        'serialised_expr':fields.char('Expression', size=255),
        'promotion': fields.many2one('promos.rules', 'Promotion'),
        'stop_further':fields.boolean('Stop further checks')
    }

    _defaults = {
        'comparator': lambda * a:'==',
        'stop_further': lambda * a: '1'
    }
 
    def validate(self, cursor, user, vals, context=None):
        LOGGER.info("Validate")
        """
        Checks the validity
        @param cursor: Database Cursor
        @param user: ID of User
        @param vals: Values of current record.
        @param context: Context(no direct use).
        """
        NUMERCIAL_COMPARATORS = ['==', '!=', '<=', '<', '>', '>=']
        attribute = vals['attribute']
        comparator = vals['comparator']
        value = vals['value']
        # Check for condition for promotions
          
          
     
        # Mismatch 1:
        if attribute in [
                         'amount_untaxed',
                         'amount_tax',
                         'product_product' ,
                         'amount_total',
                         'prod_qty',
                         'prods_qty',
                         'product_cat',
                         'prod_unit_price',
                         'prod_sub_total',
                         'prod_discount',
                         'prod_weight',
                         'prod_net_price',
                         'comp_sub_total',
                         'comp_sub_total_x',
                         'fix_prods_qty',
                         ] and \
            not comparator in NUMERCIAL_COMPARATORS:
            
            raise Exception(
                            "Only %s can be used with %s"
                            % ",".join(NUMERCIAL_COMPARATORS), attribute
                            )
        # Mismatch 4:
        if attribute in [
                         # 'prods_qty',
                         'prod_qty',
                         'fix_prods_qty',
                         'prod_unit_price',
                         'prod_sub_total',
                         'prod_discount',
                         'prod_weight',
                         'prod_net_price',
                         ]:
            try:
                product_code, quantity = value.split(":")
                if not (type(eval(product_code)) == str \
                    and type(eval(quantity)) in [int, long, float]):
                    
                    raise
            except:
                raise Exception(
                        "Value for %s combination is invalid\n"
                        "Eg for right format is `'PC312',120.50`" % attribute)
        # Mismatch 5:
        if attribute in [
                         'comp_sub_total',
                         'comp_sub_total_x',
                         ]:
            try:
                product_codes_iter, quantity = value.split("|")
                if not (type(eval(product_codes_iter)) in [tuple, list] \
                    and type(eval(quantity)) in [int, long, float]):
                    
                    raise
            except:
                raise Exception(
                        "Value for computed subtotal combination is invalid\n"
                        "Eg for right format is `['code1,code2',..]|120.50`")
        # Mismatch 6:        
        if attribute in [
                         'prods_multi_uom_qty',
                        ]:
            try:
                svalue = value.split(':')
                codes = svalue[0]
                quantity = svalue[1]
                pcodes = codes.split("|") 
                product_codes = pcodes[0]
                uom_qtys = pcodes[1]
                product_code = product_codes.split(";")
                uom_qty = uom_qtys.split(";")
 
                for product in product_code:
                    if not(type(eval(product)) == str):
                        raise
                for qty in uom_qty:
                    if not(type(eval(qty))in [int, long, float]):
                        raise     

                if not (type(eval(quantity)) in [int, long, float]):
                    raise
            except:
                raise Exception(
                        "Value for %s combination is invalid\n"
                        "Eg for right format is `'DC-0006';'DC-0001';'DC-0003'|24;60;60:5`" % attribute)  
   
   
        # Mismatch 7:
        if attribute in [
                         'prods_qty',
   
                         ]:
            try:
                # divide product_product code and quatity
                product_codes, quantity = value.split("|")
                # divide product_product code one by one
                product = product_codes.split(";")
                for product_code in product:
                    # Check product_product code is string
                    if not (type(eval(product_code)) == str):
                        raise
                # Check quantity is integer,float,long    
                if not type(eval(quantity) in [int, long, float]):
                    raise
            except:
                raise Exception(
                        "Value for %s combination is invalid\n"
                        "Eg for right format is `'DC-0006';'DC-0000'|50" % attribute)
                    
        # After all validations say True
        return True
    
  
    def serialise(self, attribute, comparator, value):
        """
        Constructs an expression from the entered values
        which can be quickly evaluated
        @param attribute: attribute of promo expression
        @param comparator: Comparator used in promo expression.
        @param value: value according which attribute will be compared
        """
        if attribute == 'custom':
            return value
        if attribute in [
                         'promo_already_exit',
                         ]:
            return '%s %s products' % (value,
                                       comparator)
        if attribute == 'product_product':
            return '%s %s products' % (value,
                                       comparator)
        if attribute == 'product_cat':
            return '%s %s products' % (value,
                                       comparator)    
        if attribute in [ 
                      
                         # 'prods_qty',
                         'prod_qty',
                         'prod_unit_price',
                         'prod_sub_total',
                         'prod_discount',
                         'prod_weight',
                         'prod_net_price',
                         'cat_qty',
                          'fix_prods_qty',
                         ]:
            product_code, quantity = value.split(":")
            return '(%s in products) and (%s["%s"] %s %s)' % (
                                                           product_code,
                                                           attribute,
                                                           eval(product_code),
                                                           comparator,
                                                           quantity
                                                           )
        if attribute in [ 
                      
                        'prods_qty',
                         
                         ]:
            product_codes, quantity = value.split("|")
            product_code = product_codes.split(";")
            return '(%s in products) and (%s["%s"] %s %s)' % (
                                                           product_code,
                                                           attribute,
                                                           product_code,
                                                           comparator,
                                                           quantity
                                                           )
        if attribute == 'comp_sub_total':
            product_codes_iter, value = value.split("|")
            return """sum(
                [prod_sub_total.get(prod_code,0) for prod_code in %s]
                ) %s %s""" % (
                               eval(product_codes_iter),
                               comparator,
                               value
                               )
        if attribute == 'comp_sub_total_x':
            product_codes_iter, value = value.split("|")
            return """(sum(prod_sub_total.values()) - sum(
                [prod_sub_total.get(prod_code,0) for prod_code in %s]
                )) %s %s""" % (
                               eval(product_codes_iter),
                               comparator,
                               value
                               )
        return "order.%s %s %s" % (
                                    attribute,
                                    comparator,
                                    value) 
        if attribute in [ 
                         'prods_multi_uom_qty',
                          
                         ]:
            svalue = value.split(':')
            codes = svalue[0]
            quantity = svalue[1]
            pcodes = codes.split("|") 
            product_codes = pcodes[0]
            uom_qtys = pcodes[1]
            product_code = product_codes.split(";")
            uom_qty = uom_qtys.split(";")
            return '(%s in products) and (%s in qtys) and (%s["%s"]["%s"] %s %s)' % (
                                                           product_code,
                                                           uom_qty,
                                                           attribute,
                                                           eval(product_code),
                                                           eval(uom_qty),
                                                           comparator,
                                                           quantity
                                                           )
        
    def evaluate(self, cursor, user,
                 expression, order, context=None):
        """
        Evaluates the expression in given environment
        @param cursor: Database Cursor
        @param user: ID of User
        @param expression: Browse record of expression
        @param order: Browse Record of sale order
        @param context: Context(no direct use).
        @return: True if evaluation succeeded
        """
        products = []  # List of product_product Codes
        prod_qty = {}  # Dict of product_code:quantity
        prod_unit_price = {}
        prod_sub_total = {}
        prod_discount = {}
        prod_weight = {}
        prod_lines = {}
        for line in order.order_line:
            if line.product_id:
                product_code = line.product_id.code
                products.append(product_code)
                prod_lines[product_code] = line.product_id
                prod_qty[product_code] = prod_qty.get(
                                            product_code, 0.00
                                                    ) + line.product_uom_qty
                prod_unit_price[product_code] = prod_unit_price.get(
                                                    product_code, 0.00
                                                    ) + line.price_unit
                prod_sub_total[product_code] = prod_sub_total.get(
                                                    product_code, 0.00
                                                    ) + line.price_subtotal
                prod_discount[product_code] = prod_discount.get(
                                                    product_code, 0.00
                                                    ) + line.discount
                prod_weight[product_code] = prod_weight.get(
                                                    product_code, 0.00
                                                    ) + line.th_weight 
        return eval(expression.serialised_expr)     
    
#     def write(self, cursor, user, ids, vals, context):
#         """
#         Serialise before Write
#         @param cursor: Database Cursor
#         @param user: ID of User
#         @param  ids: ID of current record.
#         @param vals: Values of current record.
#         @param context: Context(no direct use).
#         """
#         # Validate before save
#         if type(ids) in [list, tuple] and ids:
#             ids = ids[0]
#         try:
#             old_vals = self.read(cursor, user, ids,
#                                  ['attribute', 'comparator', 'value'],
#                                  context)
#             old_vals.update(vals)
#             old_vals.has_key('id') and old_vals.pop('id')
#             self.validate(cursor, user, old_vals, context)
#         except Exception, e:
#             LOGGER.info(e)
#         # only value may have changed and client gives only value
#             vals = old_vals 
#             vals['serialised_expr'] = self.serialise(vals['attribute'],
#                                                  vals['comparator'],
#                                                  vals['value'])
#             super(PromotionsRulesConditionsExprs, self).write(cursor, user, ids,
#                                                            vals, context)
        
PromotionsRulesConditionsExprs()

class PromotionsRulesActions(osv.Model):
    "Promotions actions"
    _name = 'promos.rules.actions'
    _description = __doc__
    _rec_name = 'action_type'
    

    def on_change(self, cursor, user, ids=None,
                   action_type=None, product_code=None,
                   arguments=None, context=None):
        """
        Sets the arguments as templates according to action_type
        @param cursor: Database Cursor
        @param user: ID of User
        @param ids: ID of current record
        @param action_type: type of action to be taken
        @product_code: Product on which action will be taken.
                (Only in cases when attribute in expression is product_product.)
        @param arguments: Values that will be used in implementing of actions
        @param context: Context(no direct use).
        """
        if not action_type:
            return {}
        if not arguments in [
                             False,
                             "0.00",
                             "1:1",
                             ] and product_code in [
                                        "'product_code'",
                                        "'product_code_of_y'"
                                        "'product_code_x':'product_code_y'"
                                                  ]:
            return {}
        if action_type in [
                           'prod_disc_perc',
                           'prod_disc_fix',
                           ] :
            return {
                    'value':{
                             'product_code':"'product_code'",
                             'arguments':"0.00",
                             }
                    }
        if action_type in [
                           'cart_disc_perc',
                           'cart_disc_fix',
                           ] :
            return {
                    'value':{
                             'product_code':False,
                             'arguments':"0.00",
                             }
                    }
        
        if action_type in [
                           'prod_x_get_y',
                           ] :
            return {
                    'value':{
                         'product_code':"'product_code_x':'product_code_y'",
                         'arguments':"1:1",
                             }
                    }
        if action_type in [
                           'buy_cat_get_x_cat',
                           ] :
            return {
                    'value':{
                         'product_code':"'product_category':'product_category_x'",
                         'arguments':"1:1",
                             }
                    }
       
        if action_type in [
                           'buy_cat_get_x',
                          
                           ] :
            return {
                    'value':{
                          'product_code':"'product_category':'product_code_x'",
                         'arguments':"1:1",
                             }
                    }
        if action_type in [
                           'prod_x_get_x',
                           ] :
            return {
                    'value':{
                         'product_code':"'product_code_x1':'product_code_x2'",
                         'arguments':"1:1",
                             }
                    }
        if action_type in ['prod_multi_get_x','prod_multi_get_x_conds', ] :
            return{
                   'value' : {
                              'product_code':"'product_code_x1';'product_code_x2':'product_code_x'",
                              'arguments':"1:1",
                              }
                   }
            
        if action_type in ['prod_multi_ratio_x' ] :
            return{
                   'value' : {
                              'product_code':"'code_1';'code_2';'code_3';|3;3;1:'given_product_code'",
                         'arguments':"1:1",
                              }
                   }
            
            
        if action_type in ['prod_multi_uom_get_x', ]:
            return{
                   'value' : {
                              'product_code':"'code_1';'code_2';'code_3'|24;60;60:'code_x'",
                         'arguments':"1:1",
                              }
                   }
        if action_type in ['fix_qty_on_product_code']:
            return{
                   'value':{
                            'product_code':"'product_code'",
                            'arguments':"1",
                            }
                   }
        if action_type in ['discount_on_categ', ]:
            return{
                   'value':{
                           'product_code':"'product_categ'",
                             'arguments':"0.00",
                            }
                   }
        
        if action_type in ['foc_on_categ', ]:
            return{
                   'value':{
                           'product_code':"'product_categ':'foc_product'",
                             'arguments':"0.00",
                            }
                   }
            
        if action_type in ['prod_foc_smallest_unitprice', ] :
            return{
                   'value' : {
                              'product_code':"'product_code_x1':'product_code_x2':'product_code_x3'",
                              'arguments':"0.00",
                              }
                   }          

        if action_type in ['prod_fix_amt_disc_subtotal', ] :
            return{
                   'value' : {
                              'product_code':"'product_code'",
                              'arguments':"1",
                              }
                   }
        if action_type in ['prod_dis_double', ] :
            return{
                   'value' : {
                              'product_code':"'product_code'",
                              'arguments':"1",
                              }
                   }
        
        if action_type in ['prod_multi_get_x_by_limit', ] :
            return{
                   'value' : {
                              'product_code':"'product_code_x1';'product_code_x2':'product_code_x'",
                              'arguments':"1:1;1",
                              }
                   }
#kzo 
        if action_type in ['foc_any_product', ] :
            return{
                   'value' : {
                              'product_code':"'product_code_x1':'product_code_x2':'product_code_x3'",
                              'arguments':"0.00",
                              }
                   }    
            
        if action_type in ['foc_any_prod_fix', ] :
            return{
                   'value' : {
                              'product_code':"'product_code_x1':'product_code_x2':'product_code_x3'",
                              'arguments':"0.00",
                              }
                   }            
        # Finally if nothing works prod_dis_double
        return {}
    
    _columns = {
        'sequence':fields.integer('Sequence', required=True),
        'action_type':fields.selection(ACTION_TYPES, 'Action', required=True),
        'product_code':fields.char('Product Code'),
        'arguments':fields.char('Arguments', size=100),
        'promotion':fields.many2one('promos.rules', 'Promotion'),
    }
 
    def clear_existing_promotion_lines(self, cursor, user,
                                        order, context=None):
        """
        Deletes existing promotion lines before applying
        @param cursor: Database Cursor
        @param user: ID of User
        @param order: Sale order
        @param context: Context(no direct use).
        """
        order_line_obj = self.pool.get('sale.order.line')
        # Delete all promotion lines
        order_line_ids = order_line_obj.search(cursor, user,
                                            [
                                             ('order_id', '=', order.id),
                                             ('promotion_line', '=', True),
                                            ], context=context
                                            )
        if order_line_ids:
            order_line_obj.unlink(cursor, user, order_line_ids, context)
        # Clear discount column
        order_line_ids = order_line_obj.search(cursor, user,
                                            [
                                             ('order_id', '=', order.id),
                                            ], context=context
                                            )
        if order_line_ids:
            order_line_obj.write(cursor, user,
                                 order_line_ids,
                                 {'discount':0.00},
                                 context=context)
        return True
 
    # MMK I'm just fix a little missing code
    def action_fix_amt_on_grand_total(self, cursor, user,
                               action, order, context=None):
        LOGGER.info("Fix amount on Grand Total")
        order_obj = self.pool.get('sale.order')
        order.discount_total = eval(action.arguments)
      
 
        if action.action_type == 'fix_amt_on_grand_total':
            order_obj.write(cursor, user, order.id,
                                         {
                                          'deduct_amt':eval(action.arguments),
                                          }, context)
            order_obj.button_dummy(cursor, user, [order.id], context)
        return True
    
    # MMK I'm just fix a little missing code  
    def action_prod_disc_perc(self, cursor, user,
                               action, order, context=None):
        """
        Action for 'Discount % on Product'
        @param cursor: Database Cursor
        @param user: ID of User
        @param action: Action to be taken on sale order
        @param order: sale order
        @param context: Context(no direct use).
        """
        LOGGER.info("Discount % on Product")
        orderline_ids = []
        order_obj = self.pool.get('sale.order')
        order_line_obj = self.pool.get('sale.order.line')
        discount_amt = 0.0
        for order_line in order.order_line:
            if order_line.product_id.default_code == eval(action.product_code):
                orderline_ids.append(order_line.id)
                # MMK I'm just fix a little missing codeI'm just fix a little missing code
                discount_amt = float(eval(action.arguments)) * (float(order_line.price_unit * order_line.product_uom_qty)) / 100
                order_line_obj.write(cursor,
                                     user,
                                    order_line.id,
                                     {
                                      'discount':eval(action.arguments), 'discount_amt':discount_amt
                                      },
                                     context
                                     )
        order_obj.button_dummy(cursor, user, [order.id], context)
        return True
    
    def action_prod_disc_fix(self, cursor, user,
                              action, order, context=None):
        """
        Action for 'Fixed amount on Product'
        @param cursor: Database Cursor
        @param user: ID of User
        @param action: Action to be taken on sale order
        @param order: sale order
        @param context: Context(no direct use).
        """
        LOGGER.info('Fixed Amount on Product')
        order_line_obj = self.pool.get('sale.order.line')
        product_obj = self.pool.get('product.product')
        product_id = product_obj.search(cursor, user,
                       [('default_code', '=', eval(action.product_code))],
                       context=context)
        if not product_id:
            raise Exception("No product_product with the product_product code")
        if len(product_id) > 1:
            raise Exception("Many products with same code")
        for order_line in order.order_line:
            if order_line.product_id.default_code == eval(action.product_code):
                # MMK I'm just fix a little missing codeI'm just fix a little missing code
                order_line_obj.write(cursor,
                                                     user,
                                                     order_line.id,
                                                     {
                                                    'discount_amt':eval(action.arguments) * order_line.product_uom_qty,
                                                      },
                                                     context
                                                     )
        return True

    # MMK I'm just fix a little missing code
    def action_disc_perc_on_grand_total(self, cursor, user,
                               action, order, context=None):

        LOGGER.info("Discount % on Grand Total")
        order_obj = self.pool.get('sale.order')
        if action.action_type == 'disc_perc_on_grand_total':
            discount_amt = 0
            discount_amt = (order.amount_untaxed * eval(action.arguments)) / 100
            order_obj.write(cursor, user, order.id,
                                         {
                                          'total_dis':discount_amt,
                                          'deduct_amt':discount_amt,
                                          }, context)
            order_obj.button_dummy(cursor, user, [order.id], context)  # update the SO fields
        return True
            

    def action_cart_disc_perc(self, cursor, user,
                               action, order, context=None):
        """
        'Discount % on Sub Total'
        @param cursor: Database Cursor
        @param user: ID of User
        @param action: Action to be taken on sale order
        @param order: sale order
        @param context: Context(no direct use).
        """
        order_line_obj = self.pool.get('sale.order.line')
        return order_line_obj.create(cursor,
                                  user,
                                  {
                      'order_id':order.id,
                      'name':action.promotion.name,
                      'price_unit':-(order.amount_untaxed \
                                    * eval(action.arguments) / 100),
                      'product_uom_qty':1,
                      'promotion_line':True,
                      'product_uom':PRODUCT_UOM_ID
                                  },
                                  context
                                  )
        
    # MMK I'm just fix a little missing code 
    def action_prod_fix_amt_disc_subtotal(self, cursor, user,
                              action, order, context=None):
        LOGGER.info("Fixed amount on Sub Total")
        """
        'Product Fix Amount on Sub Total'
        @param cursor: Database Cursor
        @param user: ID of User
        @param action: Action to be taken on sale order
        @param order: sale order
        @param context: Context(no direct use).
        """
        orderline_ids = []
        order_line_obj = self.pool.get('sale.order.line')
        try:
            action_product_code = eval(action.product_code)
        except Exception, e:
            LOGGER.info(e)
            raise osv.except_osv(_('Wrong Product Code'), _('In promotion %s , Action : %s  ') % (action.promotion.name, action.action_type))
        for order_val in order.order_line:
            if order_val.product_id.default_code == action_product_code:
                orderline_ids.append(order_val.id)
                order_line_obj.write(cursor, user, orderline_ids,
                                                 {
                                                  'discount_amt': eval(action.arguments),
                                                  }, context)
        return True
    # MMK I'm just fix a little missing code
    def action_cart_disc_fix(self, cursor, user,
                              action, order, context=None):
        LOGGER.info("Fixed amount on Sub Total")
        """
        'Fixed amount on Sub Total'
        @param cursor: Database Cursor
        @param user: ID of User
        @param action: Action to be taken on sale order
        @param order: sale order
        @param context: Context(no direct use).
        """
        orderline_ids = []
        order_line_obj = self.pool.get('sale.order.line')
        exist_order = self.pool.get('sale.order')
        if action.action_type == 'cart_disc_fix':
            existing_order_line_ids = order_line_obj.search(cursor, user,
                                           [
                                ('order_id', '=', order.id)
                                            ],
                                           context=context
                                                )
            for exist_order in existing_order_line_ids:
                update_order = order_line_obj.browse(cursor, user,
                                            exist_order,
                                            context)
                orderline_ids.append(update_order.id)
            order_line_obj.write(cursor, user, orderline_ids,
                                         {
                                          'discount_amt': eval(action.arguments),
                                          }, context)
        return True
    
    # MMK I'm just fix a little missing codeI'm just fix a little missing code I'm just fix a little missing code
    def create_y_line(self, cursor, user, action,
                       order, quantity, product_id, context=None):
        """
        Create new order line for product_product
        @param cursor: Database Cursor
        @param user: ID of User
        @param action: Action to be taken on sale order
        @param order: sale order
        @param quantity: quantity of new free product_product
        @param product_id: product_product to be given free
        @param context: Context(no direct use).
        """
        """ 
            Buy X get Y free
        """
        if product_id:
            order_line_obj = self.pool.get('sale.order.line')
            product_obj = self.pool.get('product.product')
            product_y = product_obj.browse(cursor, user, product_id[0])
            return order_line_obj.create(cursor, user, {
                                 'order_id':order.id,
                                 'product_id':product_y.id,
                                 'name':'[%s]%s (%s)' % (
                                             product_y.default_code,
                                             product_y.name,
                                             action.promotion.name),
                                  'price_unit':0.00, 'promotion_line':True,
                                  'product_uom_qty':quantity,
                                  'sale_foc':True,
                                  'product_uom':product_y.uom_id.id
                                  }, context)
    
    def create_x_line(self, cursor, user, action,
                       order, quantity, product_id, context=None):
        """
        Create new order line for product_product
        @param cursor: Database Cursor
        @param user: ID of User
        @param action: Action to be taken on sale order
        @param order: sale order
        @param quantity: quantity of new free product_product
        @param product_id: product_product to be given free
        @param context: Context(no direct use).
        """
        order_line_obj = self.pool.get('sale.order.line')
        product_obj = self.pool.get('product.product')
        product_x = product_obj.browse(cursor, user, product_id[0])
        return order_line_obj.create(cursor, user, {
                             'order_id':order.id,
                             'product_id':product_x.id,
                             'name':'[%s]%s (%s)' % (
                                         product_x.default_code,
                                         product_x.name,
                                         action.promotion.name),
                              'price_unit':0.00, 'promotion_line':True,
                              'sale_foc':True,  # sale_foc_discount
                              'product_uom_qty':quantity,
                              'product_uom':product_x.uom_id.id
                              }, context)
     
    # MMK I'm just fix a little missing code
    def action_buy_cat_get_x_cat(self, cursor, user,
                             action, order, context=None):
        """
        'Buy Category get X Category free:[Only for integers]'
        @param cursor: Database Cursor
        @param user: ID of User
        @param action: Action to be taken on sale order
        @param order: sale order
        @param context: Context(no direct use).
        
        Note: The function is too long because if it is split then there 
                will a lot of arguments to be passed from one function to
                another. This might cause the function to get slow and 
                hamper the coding standards.
        """
        LOGGER.info('Buy Category get X Category free')
        product_obj = self.pool.get('product.product')
        order_line_obj = self.pool.get('sale.order.line')
        # Get Product
        product_x_cat, product_y_cat = [eval(code) \
                                for code in action.product_code.split(":")]
        qtys = tot_free_y = 0
        qty_x, qty_y = [eval(arg) \
                                for arg in action.arguments.split(":")]
        existing_id = None
        # Build a dictionary of product_code to quantity 
        for order_line in order.order_line:
            category_name = order_line.product_id.categ_id.name
            cat_value_x = str(product_x_cat)
            cat_value_y = str(product_y_cat)
            category_name = category_name.strip() 
            cat_value_x = cat_value_x.strip() 
            cat_value_y = cat_value_y.strip() 
            if category_name == cat_value_x:
                # check sale category is same with category in promotions x value
                if category_name == cat_value_y:
                    
                    # to add sale product_product code for promotion
                    product_code = order_line.product_id.default_code
                    existing_id = order_line_obj.search(cursor, user, [('product_id.default_code', '=', product_code), ('price_unit', '=', 0), ('sale_foc', '=', True), ('order_id', '=', order.id)], context)
                    if existing_id:
                        order_line_obj.unlink(cursor, user, existing_id, context)
                    else:
                        # to add quantity from sale order for qty promotions
                        qtys += order_line.product_uom_qty
                        # to add code id for product_product code for promo
                        product_x2_code_id = product_obj.search(cursor, user,
                                        [('default_code', '=', product_code)], context=context)
                        # Total number of free units of y to give
                        tot_free_y = int((qtys / qty_x) * qty_y)
                    
        if tot_free_y:
            LOGGER.info("FOC : %s ", tot_free_y)
            # return next line if promotion exists
            self.create_y_line(cursor, user, action,
                               order, tot_free_y, product_x2_code_id, context)
        return True
    
    # MMK I'm just fix a little missing code
    def action_buy_cat_get_x(self, cursor, user,
                             action, order, context=None):
        """
        'Buy Category get X free:[Only for integers]'
        @param cursor: Database Cursor
        @param user: ID of User
        @param action: Action to be taken on sale order
        @param order: sale order
        @param context: Context(no direct use).
        
        Note: The function is too long because if it is split then there 
                will a lot of arguments to be passed from one function to
                another. This might cause the function to get slow and 
                hamper the coding standards.
        """
        
        order_line_obj = self.pool.get('sale.order.line')
        product_obj = self.pool.get('product.product')
        
        qtys = tot_free_y = 0
        # Get Product
        product_cat, product_y_code = [eval(code) \
                                for code in action.product_code.split(":")]

        product_x2_code_id = product_obj.search(cursor, user,
                                    [('default_code', '=', product_y_code)], context=context)
        qty_x, qty_y = [eval(arg) \
                                for arg in action.arguments.split(":")]
        LOGGER.info("""Product Category >>> %s""", product_cat)
        LOGGER.info("""Free Y Code >>> %s """, product_y_code)
        existing_id = None
        if product_y_code:
            existing_id = order_line_obj.search(cursor, user, [('order_id', '=', order.id), ('product_id.default_code', '=', product_y_code), ('price_unit', '=', 0), ('sale_foc', '=', True)], context)
            if existing_id:
                order_line_obj.unlink(cursor, user, existing_id, context)
            # Build a dictionary of product_code to quantity 
            for order_line in order.order_line:
                
                cat_name = order_line.product_id.categ_id.name
                category_name1 = str(cat_name)
                cat_value1 = str(product_cat)
                category_name = category_name1.strip() 
                cat_value = cat_value1.strip() 
                LOGGER.info("""Product Category >>> %s""", category_name)
                LOGGER.info("""Action Product Category >>> %s""", cat_value)
                if category_name == cat_value:
                    
                    qtys += order_line.product_uom_qty
                    # Total number of free units of y to give
                tot_free_y = int((qtys / qty_x) * qty_y)
            if tot_free_y > 0:
                LOGGER.info("FOC : %s ", tot_free_y)
                self.create_y_line(cursor, user, action,
                                       order, tot_free_y, product_x2_code_id, context)
        return True
        
 
        
    # MMK I'm just fix a little missing codeI'm just fix a little missing code
    def action_prod_x_get_y(self, cursor, user,
                             action, order, context=None):
        """
        'Buy X get Y free:[Only for integers]'
        @param cursor: Database Cursor
        @param user: ID of User
        @param action: Action to be taken on sale order
        @param order: sale order
        @param context: Context(no direct use).
        
        Note: The function is too long because if it is split then there 
                will a lot of arguments to be passed from one function to
                another. This might cause the function to get slow and 
                hamper the coding standards.
        """
        LOGGER.info('Buy X get Y free')
        order_line_obj = self.pool.get('sale.order.line')
        product_obj = self.pool.get('product.product')
        qtys = tot_free_y = 0
        prod_qty = {}
        # Get Product
        product_x_code, product_y_code = [eval(code) \
                                for code in action.product_code.split(":")]
        product_x_code_id = product_obj.search(cursor, user,
                                    [('default_code', '=', product_x_code)], context=context)
        product_x2_code_id = product_obj.search(cursor, user,
                                    [('default_code', '=', product_y_code)], context=context)
        qty_x, qty_y = [eval(arg) \
                                for arg in action.arguments.split(":")]
        if product_x_code_id:
            # Build a dictionary of product_code to quantity 
            for order_line in order.order_line:
                if order_line.product_id.id == product_x_code_id[0]:
                    #                 product_code = order_line.product_id.default_code
                    #                 prod_qty[product_code] = prod_qty.get(
                    #                                         product_code, 0.00
                    #                                                 ) + order_line.product_uom_qty
                        qtys += order_line.product_uom_qty       
            # Total number of free units of y to give
            tot_free_y = int((qtys / qty_x) * qty_y)
            # If y is already in the cart discount it?
            qty_y_in_cart = prod_qty.get(product_y_code, 0)
            existing_order_line_ids = order_line_obj.search(cursor, user,
                                               [
                                    ('order_id', '=', order.id),
                                    ('product_id.default_code',
                                                '=', product_y_code), ('price_unit', '=', 0), ('sale_foc', '=', True)
                                                ],
                                               context=context
                                                    )
            if existing_order_line_ids:
                update_order_line = order_line_obj.browse(cursor, user,
                                                existing_order_line_ids[0],
                                                context)
                # Update that line
                # The replace is required because on secondary update 
                # the name may be repeated
                if tot_free_y:
                    if qty_y_in_cart <= tot_free_y:
                            # Quantity in cart is less then increase to total free
                        order_line_obj.write(cursor, user, update_order_line.id,
                                             {
                                             
                                              'product_uom_qty': tot_free_y,
                                              'discount': 100,
                                              }, context)
                            
                    else:
                            # If the order has come for 5 and only 3 are free
                            # then convert paid order to 2 units and rest free
                        order_line_obj.write(cursor, user, update_order_line.id,
                                             {
                                        'product_uom_qty': qty_y_in_cart - tot_free_y,
                                              }, context)
                        self.create_y_line(cursor, user, action,
                                                order,
                                                tot_free_y,
                                                product_x2_code_id,
                                                context
                                                )
                        # delete the other lines
                    existing_order_line_ids.remove(existing_order_line_ids[0])  # remove the existing foc line
                    if existing_order_line_ids:
                        order_line_obj.unlink(cursor, user,
                                              existing_order_line_ids, context)
                    return True
            else:
                # Dont create line if quantity is not there
                if not tot_free_y:
                    return True
                return self.create_y_line(cursor, user, action,
                                           order, tot_free_y, product_x2_code_id, context)
            
    # for buy x get x
    # MMK I'm just fix a little missing code
    def action_fix_qty_on_product_code(self, cursor, user,
                             action, order, context=None):
        """
        'FOC Products on Qty'
        @param cursor: Database Cursor
        @param user: ID of User
        @param action: Action to be taken on sale order
        @param order: sale order
        @param context: Context(no direct use).
        
        Note: The function is too long because if it is split then there 
                will a lot of arguments to be passed from one function to
                another. This might cause the function to get slow and 
                hamper the coding standards.
        """
        LOGGER.info("FOC Products on Qty")
        product_obj = self.pool.get('product.product')
        order_line_obj = self.pool.get('sale.order.line')
        # Get Product
        product_x_code = eval(action.product_code)
        product_id_for_x1_code = product_obj.search(cursor, user,
                                [('default_code', '=', product_x_code)], context=context)
        existing_id = None
        if product_id_for_x1_code:
            existing_id = order_line_obj.search(cursor, user, [('order_id', '=', order.id), ('product_id', '=', product_id_for_x1_code[0]), ('price_unit', '=', 0), ('sale_foc', '=', True)], context)
            if existing_id:
                order_line_obj.unlink(cursor, user, existing_id, context)
            # get Quantity
            qty_x = eval(action.arguments)
            LOGGER.info("FOC : %s ", qty_x)
            self.create_x_line(cursor, user, action,
                                   order, qty_x, product_id_for_x1_code, context)       
        return True
  
            
            

        
    # MMK I'm just fix a little missing code
    def action_prod_x_get_x(self, cursor, user,
                             action, order, context=None):
        """
        'Buy X get X free:[Only for integers]'
        @param cursor: Database Cursor
        @param user: ID of User
        @param action: Action to be taken on sale order
        @param order: sale order
        @param context: Context(no direct use).
        
        Note: The function is too long because if it is split then there 
                will a lot of arguments to be passed from one function to
                another. This might cause the function to get slow and 
                hamper the coding standards.
        """
        LOGGER.info('Buy X get X free')
        product_obj = self.pool.get('product.product')
        order_line_obj = self.pool.get('sale.order.line')
        # Get Product
        # prod_qty = {}
        qtys = free_qty = 0
        # get Product code
        product_x1_code, product_x2_code = [eval(code) \
                                for code in action.product_code.split(":")]
        product_id_for_x1_code = product_obj.search(cursor, user,
                                [('default_code', '=', product_x1_code)], context=context)
        product_id_for_x2_code = product_obj.search(cursor, user,
                                [('default_code', '=', product_x2_code)], context=context)
        # get Quantity
        qty_x, qty_y = [eval(arg) \
                                for arg in action.arguments.split(":")]
        existing_id = None
        if product_id_for_x2_code:
            existing_id = order_line_obj.search(cursor, user, [('order_id', '=', order.id), ('product_id', '=', product_id_for_x2_code[0]), ('price_unit', '=', 0), ('sale_foc', '=', True)], context)
            if existing_id:
                order_line_obj.unlink(cursor, user, existing_id, context)
            # Build a dictionary of product_code to quantity 
            for order_line in order.order_line:
                LOGGER.info('Order Line Product Code : ', order_line.product_id.id)
                LOGGER.info('Conditional Product Code : ', product_id_for_x1_code[0])
                if order_line.product_id.id == product_id_for_x1_code[0]:
                    # To add qty from sale order line
                    qtys += order_line.product_uom_qty
                    # Calculate for free qty
                    free_qty = int((qtys / qty_x) * qty_y)                               
            LOGGER.info("FOC : %s ", free_qty)
            if free_qty >= 1:
                self.create_x_line(cursor, user, action,
                                   order, free_qty, product_id_for_x2_code, context)
        return True
    # prod_multi_uom_get_x
    # MMK I'm just fix a little missing code
    def action_prod_multi_uom_get_x(self, cursor, user,
                             action, order, context=None):
        LOGGER.info('Buy Multi UOM get X free')
        product_qtys = []
        qty = 0
        product_obj = self.pool.get('product.product')
        order_line_obj = self.pool.get('sale.order.line')
        existing_id = None
        # split entered product_product code with split function
        product_codes = self.tsplit1(action.product_code, (':', '|', ';'))
        final_code = product_codes[len(product_codes) - 1]
        product_x2_code_id = product_obj.search(cursor, user,
                                     [('default_code', '=', eval(final_code))], context=context)         
#         product_codes.remove(final_code)
        # To add promotion uom quantity to product_product qtys array
        x = int(len(product_codes) - 1)
        y = int(len(product_codes) / 2)
        while y <= x:
            pcode = eval(product_codes[y])
            product_qtys.append(pcode)
            y += 1
        
        # for order line     
        for order_line in order.order_line:
            if order_line.product_id: 
                for product_code in product_codes:
                    # Check product_product code with promo product_product codes
                    if order_line.product_id.default_code == eval(product_code):
                            # Get index of product_product codes
                            product_id_index = product_codes.index(product_code,)
                            # Get product_product qty from above product_id
                            product_qty = product_qtys[product_id_index]
                            # division for to get product_product UOM quantity
                            qty += int(order_line.product_uom_qty / int(product_qty))
                            LOGGER.info("Total Qty : %s ", qty)
                            # GEt quantity from promotion rules
                            qty_x, qty_y = [eval(arg) \
                                            for arg in action.arguments.split(":")]
                            if qty >= qty_x:
                                LOGGER.info("Promotion product : %s " , product_x2_code_id)
                                existing_id = order_line_obj.search(cursor, user, [('order_id', '=', order.id), ('product_id', '=', product_x2_code_id[0]), ('price_unit', '=', 0), ('sale_foc', '=', True)], context)
                                if existing_id:
                                    order_line_obj.unlink(cursor, user, existing_id, context)
                                # division for to get free qty UOM
                                free_qty = int((qty / qty_x) * qty_y)
                                LOGGER.info("Free QTY : %s ", free_qty)
                                return self.create_x_line(cursor, user, action,
                                                   order, free_qty, product_x2_code_id, context)

      

    def tsplit1(self, string, delimiters):
        """Behaves str.split but supports multiple delimiters."""
        
        delimiters = tuple(delimiters)
        stack = [string, ]
        
        for delimiter in delimiters:
            for i, substring in enumerate(stack):
                substack = substring.split(delimiter)
                stack.pop(i)
                for j, _substring in enumerate(substack):
                    stack.insert(i + j, _substring)
            
        return stack
    # for buy prod_foc_smallest_unitprice
    # MMK I'm just fix a little missing code
    def action_prod_foc_smallest_unitprice(self, cursor, user,
                             action, order, context=None):
        
        LOGGER.info("FOC Products on Smallest Unitprice")
        product_obj = self.pool.get('product.product')
        order_line_obj = self.pool.get('sale.order.line')
        
    
        product_codes = self.tsplit(action.product_code, ('::'))
       
        new_codes_list = []
        free_qty = eval(action.arguments)
        product_x_code = product_x2_code = None
        prices = []
        
        
        for order_line in order.order_line:        
            if order_line.product_id:
                    # if product_codes.__contains__(order_line.product_id.default_code):
                    for p in product_codes:
                            if eval(p) == order_line.product_id.default_code:
                                new_codes_list.append(order_line.product_id.default_code)
                                prices.append(order_line.price_unit)
                    
        if prices:           
            sort_prices = sorted(prices)     
            sprice = sort_prices[0]
            index = prices.index(sprice,)
            product_x_code = new_codes_list[index]  
            product_x2_code = product_obj.search(cursor, user,
                                [('default_code', '=', product_x_code)], context=context)
        existing_id = None
        if product_x2_code:
            existing_id = order_line_obj.search(cursor, user, [('order_id', '=', order.id), ('product_id', '=', product_x2_code[0]), ('price_unit', '=', 0), ('sale_foc', '=', True)], context)
            if existing_id:
                order_line_obj.unlink(cursor, user, existing_id, context)
            self.create_y_line(cursor, user, action,
                                   order, free_qty, product_x2_code, context)
        return True
         
    
    # for buy prod_multi_get_x
    # MMK I'm just fix a little missing code
    def action_prod_multi_get_x(self, cursor, user,
                             action, order, context=None):
        # MMK
        existing_id = None
        LOGGER.info("Buy Multi Products get X free")
        product_obj = self.pool.get('product.product')
        order_line_obj = self.pool.get('sale.order.line')
        
        product_codes = self.tsplit(action.product_code, (':', ';'))
        LOGGER.info("Action Product Codes : %s ", product_codes)
        qty = free_qty = 0
        final_code = product_codes[len(product_codes) - 1]
        product_x2_code_id = product_obj.search(cursor, user,
                                    [('default_code', '=', eval(final_code))], context=context)
#         product_codes.remove(final_code)

        qty_x, qty_y = [eval(arg) \
                                            for arg in action.arguments.split(":")]
        
        
        LOGGER.info("Product Code : %s ", product_x2_code_id[0])
        existing_id = order_line_obj.search(cursor, user, [('order_id', '=', order.id), ('product_id', '=', product_x2_code_id[0]), ('price_unit', '=', 0), ('sale_foc', '=', True)], context)
        if existing_id:
            order_line_obj.unlink(cursor, user, existing_id, context)
        for order_line in order.order_line:        
            for product_code in product_codes:
                if order_line.product_id.default_code == eval(product_code):    
                    qty += order_line.product_uom_qty
        if qty >= qty_x:
            free_qty = int((qty / qty_x) * qty_y)
            LOGGER.info("Free Quantity : %s ", free_qty)
            return self.create_x_line(cursor, user, action,
                                                   order, free_qty, product_x2_code_id, context)
  
        return False

    def action_prod_multi_get_x_by_limit(self, cursor, user,
                             action, order, context=None):
        # MMK
        existing_id = None
        LOGGER.info("Buy Multi Products get X free Limit")
        product_obj = self.pool.get('product.product')
        order_line_obj = self.pool.get('sale.order.line')
        
        product_codes = self.tsplit(action.product_code, (':', ';'))
        LOGGER.info("Action Product Codes : %s ", product_codes)
        qty = free_qty = 0
        final_code = product_codes[len(product_codes) - 1]
        print ' final_code',final_code
        product_x2_code_id = product_obj.search(cursor, user,
                                    [('default_code', '=', eval(final_code))], context=context)
#         product_codes.remove(final_code)
        qty_column = self.tsplit(action.arguments, (':', ';'))
        print ' qty_columnqty_columnqty_column',qty_column
        qty_x=eval(qty_column[0])#24
        qty_y =eval(qty_column[1])#1
        limit=eval(qty_column[2])#240
        LOGGER.info("Product Code : %s ", product_x2_code_id[0], qty_x, qty_y,limit )
#         existing_id = order_line_obj.search(cursor, user, [('order_id', '=', order.id), ('product_id', '=', product_x2_code_id[0]), ('price_unit', '=', 0), ('sale_foc', '=', True)], context)
#         if existing_id:
#             order_line_obj.unlink(cursor, user, existing_id, context)
        for order_line in order.order_line:        
            for product_code in product_codes:
                print 'product_codeproduct_code',product_code
                if order_line.product_id.default_code == eval(product_code):    
                    qty += order_line.product_uom_qty
        if  qty>limit:
            qty=limit
        if qty >= qty_x:
            free_qty = int((qty / qty_x) * qty_y)
            LOGGER.info("Free Quantity : %s ", free_qty)
            return self.create_x_line(cursor, user, action,
                                                   order, free_qty, product_x2_code_id, context)
  
        return False
        
    def tsplit(self, string, delimiters):
        """Behaves str.split but supports multiple delimiters."""
        
        delimiters = tuple(delimiters)
        stack = [string, ]
        
        for delimiter in delimiters:
            for i, substring in enumerate(stack):
                substack = substring.split(delimiter)
                stack.pop(i)
                for j, _substring in enumerate(substack):
                    stack.insert(i + j, _substring)
            
        return stack
    
    
    
    # MMK I'm just fix a little missing code
    def action_discount_on_categ(self, cursor, user,
                               action, order, context=None):
        """
        Action for 'Discount % on Product'
        @param cursor: Database Cursor
        @param user: ID of User
        @param action: Action to be taken on sale order
        @param order: sale order
        @param context: Context(no direct use).
        select * from sale_order_line

        select * from product_product

        select * from product_template


        select * from product_categor
        """
        orderline_ids = []
        order_line_obj = self.pool.get('sale.order.line')
        
        for order_line in order.order_line:
            cat_name = order_line.product_id.categ_id.name
            category_name = cat_name.strip()  # remove the whitespace
            cat_value1 = str(eval(action.product_code))  # get category value from promotion action
            cat_value = cat_value1.strip()  # remove the whitespace
            
            LOGGER.info("product category >>> %s", cat_name)
            LOGGER.info("action category >>> %s", cat_value)
            if category_name == cat_value:
                orderline_ids.append(order_line.id)
        return order_line_obj.write(cursor,
                                     user,
                                     orderline_ids,
                                     {
                                      'discount':eval(action.arguments),
                                      'discount_amt':(order_line.price_unit * order_line.product_uos_qty) * eval(action.arguments) / 100
                                      },
                                    
                                     context
                                     )
    
        return True
    
    
    def action_foc_on_categ(self, cursor, user,
                               action, order, context=None):
        """
        Action for 'FOC on category'
        @param cursor: Database Cursor
        @param user: ID of User
        @param action: Action to be taken on sale order
        @param order: sale order
        @param context: Context(no direct use).
        """
        return True
    
    # KM I'm just fix a little missing code
    def action_foc_any_product(self, cursor, user,
                             action, order, context=None):
        
        """
        'FOC Any Products'
        @param cursor: Database Cursor
        @param user: ID of User
        @param action: Action to be taken on sale order
        @param order: sale order
        @param context: Context(no direct use).
        
        Note: The function is too long because if it is split then there 
                will a lot of arguments to be passed from one function to
                another. This might cause the function to get slow and 
                hamper the coding standards.
        """
        mod_obj = self.pool.get('ir.model.data')        
        act_obj = self.pool.get('ir.actions.act_window')
        LOGGER.info("FOC Any Products")
        order_line_obj = self.pool.get('sale.order.line')
        # Get Product
        result_context = {}    
        product_codes_str = action.product_code  # there contained array list of product code
        product_codes_list = product_codes_str.split(':')
        product_obj = self.pool.get('product.product')
        temp_obj = self.pool.get('foc.any.product.temp')
        product_x_code, product_y_code = [eval(code) \
                                for code in action.product_code.split(":")]
        product_xy_code='NA'
        
        product_x_code_id = product_obj.search(cursor, user,
                                    [('default_code', '=', product_x_code)], context=context)
        product_x2_code_id = product_obj.search(cursor, user,
                                    [('default_code', '=', product_y_code)], context=context)        
        product_xy_code_id= product_obj.search(cursor, user,
                                    [('default_code', '=', product_xy_code)], context=context)  
        qty_x = eval(action.arguments)              
        if product_codes_list:
            result = mod_obj.get_object_reference(cursor, user, 'sale_promotions', 'open_view_foc_any_product')
            id = result and result[1] or False
            result = act_obj.read(cursor, user, [id], context=context)[0]   
            cursor.execute("delete from foc_any_product_temp")
#             result['domain'] = str({'one_product_id', '=',product_x_code_id[0],\
#                                     'two_product_id', '=',product_x2_code_id[0],\
#                                     'three_product_id', '=',product_xy_code_id[0]})
#             result['context'] = str({'one_product_id', '=',product_x_code_id[0],\
#                                     'two_product_id', '=',product_x2_code_id[0],\
#                                     'three_product_id', '=',product_xy_code_id[0]})            
#             result['view_type'] = 'form'
    
#             if product_x_code_id:
#                 result_context.update({'one_product_id': product_x_code_id[0]})
#             if product_x2_code_id:
#                 result_context.update({'two_product_id': product_x2_code_id[0]})
#     
        if product_x_code_id and product_x2_code_id :
            temp_obj.create(cursor, user, {
                                     'order_id':order.id,
                                     'one_product_id':product_x_code_id[0],
                                      'two_product_id':product_x2_code_id[0],
                                      'three_product_id':False,
                                      'qty':qty_x,
                                      }, context)    
        return result        
#             try:
#                 product_x_code = ([eval(x) for x in product_codes_list])
#             except Exception, e:
#                 LOGGER.info(e)
#                 product_x_code = None
#         if product_x_code:
#             for order_line in order.order_line:
#                 if order_line.product_id.default_code in product_x_code:
#                     LOGGER.info("Same Default Code : %s ", order_line.product_id.default_code)
#                     LOGGER.info("Index :: %s ", product_x_code.index(order_line.product_id.default_code))
#                     same_product_id_list.append(order_line.product_id.id)
#                     
#             if same_product_id_list:  # if there contained already foc product from product list, firstly 
#                 for check_product_id in same_product_id_list:
#                     foc_product_id = check_product_id
#                     existing_id = order_line_obj.search(cursor, user, [('order_id', '=', order.id), ('product_id', '=', check_product_id), ('price_unit', '=', 0), ('sale_foc', '=', True)], context)
#                     if existing_id:
#                         order_line_obj.unlink(cursor, user, existing_id, context)
#                 if foc_product_id:
#                     LOGGER.info("Default Code :: %s ", foc_product_id)
#                 # get Quantity
#                     qty_x = eval(action.arguments)
#                     LOGGER.info("FOC : %s ", qty_x)
#                     self.create_x_line(cursor, user, action,
#                                        order, qty_x, [foc_product_id], context)  
#        return True  
    
    def execute(self, cursor, user, action_id,
                                   order, context=None):
        """
        Executes the action into the order
        @param cursor: Database Cursor
        @param user: ID of User
        @param action_id: Action to be taken on sale order
        @param order: sale order
        @param context: Context(no direct use).
        """
#         self.clear_existing_promotion_lines(cursor, user, order, context)
        action = self.browse(cursor, user, action_id, context)
        method_name = 'action_' + action.action_type
        return getattr(self, method_name).__call__(cursor, user, action,
                                                   order, context)
        
    def validate(self, cursor, user, vals, context):
        """
        Validates if the values are coherent with
        attribute
        @param cursor: Database Cursor
        @param user: ID of User
        @param vals: Values of current record.
        @param context: Context(no direct use).
        """
        if vals['action_type'] in [
                           'prod_disc_perc',
                           'prod_disc_fix',
                           ] :
            if not type(eval(vals['product_code'])) == str:
                raise Exception(
                        "Invalid product_product code\nHas to be 'product_code'"
                            ) 
            if not type(eval(vals['arguments'])) in [int, long, float]:
                raise Exception("Argument has to be numeric. eg: 10.00")
        if vals['action_type'] in [
                           
                           'prod_disc_fix',
                           ] :
            if not type(eval(vals['product_code'])) == str:
                raise Exception(
                        "Invalid product_product code\nHas to be 'product_code'"
                            ) 
            if not type(eval(vals['arguments'])) in [int, long, float]:
                raise Exception("Argument has to be numeric. eg: 10.00")  
        if vals['action_type'] in [
                           'fix_amt_on_grand_total',
                             ] :
            if not type(eval(vals['arguments'])) in [int, long, float]:
                raise Exception("Argument has to be numeric. eg: 10.00")   
        
        if vals['action_type'] in [
                           'cart_disc_perc',
                           'cart_disc_fix',
                           ]:
#             if vals['product_code']:
#                 raise Exception("Product code is not used in cart actions") 
            if not type(eval(vals['arguments'])) in [int, long, float]:
                raise Exception("Argument has to be numeric. eg: 10.00")
        
        if vals['action_type'] in ['prod_x_get_y', ]:
            try:
                code_1, code_2 = vals['product_code'].split(":")
                assert (type(eval(code_1)) == str)
                assert (type(eval(code_2)) == str)
            except: 
                raise Exception(
                  "Product codes have to be of form 'product_x','product_y'"
                            )
            try:
                qty_1, qty_2 = vals['arguments'].split(':')
                assert (type(eval(qty_1)) in [int, long])
                assert (type(eval(qty_2)) in [int, long])
            except:
                raise Exception("Argument has to be qty of x,y eg.`1, 1`")
        
        return True
    
#     def write(self, cursor, user, ids, vals, context):
#         """
#         Validate before Write
#         @param cursor: Database Cursor
#         @param user: ID of User
#         @param vals: Values of current record.
#         @param context: Context(no direct use).
#         """
#         # Validate before save
#         if type(ids) in [list, tuple] and ids:
#             ids = ids[0]
#         try:
#             old_vals = self.read(cursor, user, ids,
#                                  ['action_type', 'product_code', 'arguments'],
#                                  context)
#             old_vals.update(vals)
#             old_vals.has_key('id') and old_vals.pop('id')
#             self.validate(cursor, user, old_vals, context)
#         except Exception, e:
#             raise osv.except_osv("Invalid Expression", tools.ustr(e))
#         # only value may have changed and client gives only value
#         vals = old_vals 
#         super(PromotionsRulesActions, self).write(cursor, user, ids,
#                                                            vals, context)
    
PromotionsRulesActions()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
