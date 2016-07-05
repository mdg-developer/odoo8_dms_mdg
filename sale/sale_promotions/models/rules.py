from openerp.osv import osv, fields
from openerp import netsvc
from openerp.tools.translate import _
from openerp import tools
import logging

 
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
    # ('prod_unit_price', 'Product UnitPrice combination'),
    ('prod_sub_total', 'Product SubTotal combination'),
    ('promo_already_exit', 'Promotion Already Applied'),
    ('cat_qty', 'Product Category Quantity combination'),
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
     ('prod_multi_uom_get_x', _('Buy Multi UOM get X free')),
    ('fix_qty_on_product_code', _('FOC Products on Qty')),
    ('prod_foc_smallest_unitprice', _('FOC Products on smallest Unitprice')),
    ('foc_any_product', _('FOC Any Products')),
	('prod_fix_amt_disc_subtotal', _('Product Fix Amount on Sub Total')),
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
                            string='Expressions/Conditions'
                            ),
        'actions':fields.one2many(
                    'promos.rules.actions',
                    'promotion',
                    string="Actions"
                        ),
        'main_group':fields.many2one('product.maingroup', 'Main Group'),
    }
    _defaults = {
        'logic':lambda * a:'and',
        'expected_logic_result':lambda * a:'True',
        'coupon_used': '0',
    }
    _constraints = [(_check_positive_number, 'Coupon Use must be Positive', ['coupon_used'])]
     
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
            
        
    def check_primary_conditions(self, cursor, user,
                                  promotion_rule, order, expression, context):
        
        print 'PROMOTION RULES >>>> ', promotion_rule
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
        sales_obj = self.pool.get('sale.order')
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
        if promotion_rule.uses_per_partner > -1:
                matching_ids = sales_obj.search(cursor, user,
                         [
                          ('partner_id', '=', order.partner_id.id),
                          ('coupon_code', '=', promotion_rule.coupon_code),
                          ('state', '<>', 'cancel')
                          ], context=context)
#                 if len(matching_ids) > promotion_rule.uses_per_partner:
#                     raise Exception("Customer already used coupon")
       
        print "check primary promotion id", promotion_rule.id
        date_order = order.date_order
        from_date = promotion_rule.from_date
        to_date = promotion_rule.to_date
        print "date_order", date_order
        print "from_date", from_date
        print "to_date", to_date
        # Check date is valid date during promotion date
        if date_order >= from_date and date_order <= to_date:
            
            # for total amount for condition expression
            cursor.execute("select attribute,value,comparator from promos_rules_conditions_exps where id=%s", (expression.id,))
            datas = cursor.fetchone()
            print "datas", datas

            attribute = datas[0]
            value = datas[1]
            comparator = datas[2]
           
            print "value", value
            print "attribute", attribute
            print "comparator", comparator
            # for checking product_product code
            # cursor.execute("select attribute,value,comparator from promos_rules_conditions_exps where promotion=%s",(promotion_rule.id,))
            
            # Check attribute total amount
            if attribute == 'amount_total':
                svalue = eval(value)
                print "amount_total"
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
                        print "order_line.product_id.id" , order_line.product_id.id       
                        
                       
                        product_obj = self.pool.get('product_product.product_product').search(cursor, user, [('id', '=', order_line.product_id.id)], context=context)
                        product_lst = self.pool.get('product_product.product_product').search(cursor, user, [('id', '=', product_obj[0])], context=context)
                        prod_obj = self.pool.get('product_product.product_product').browse(cursor, user, product_lst[0], context)
                        # print "product_lst.product_tmpl_id.id",prod_obj.product_tmpl_id.id
                        product_template_lst = self.pool.get('product_product.template').search(cursor, user, [('id', '=', prod_obj.product_tmpl_id.id)], context=context)
                        tmpl_obj = self.pool.get('product_product.template').browse(cursor, user, product_template_lst[0], context)
                        # print "tmpl_obj.categ_id.id",tmpl_obj.categ_id.id
                        
                        product_categ_lst = self.pool.get('product_product.category').search(cursor, user, [('id', '=', tmpl_obj.categ_id.id)], context=context)
                        categ_obj = self.pool.get('product_product.category').browse(cursor, user, product_categ_lst[0], context)
                        cat_name = categ_obj.name
                        category_name1 = str(cat_name)
                        cat_value1 = str(svalue)
                        category_name = category_name1.strip() 
                        cat_value = cat_value1.strip() 
                        print"category_name--", type(category_name)
                        print"cat_value--", type(cat_value)
                        print"category_str-length-", category_name.__len__()
                        print"cat_str-length-", cat_value.__len__()
                        print"category_", category_name
                        print"cat_str", cat_value
                        print category_name == cat_value
                       
                        if category_name == cat_value:
                            
                            print "Same category", category_name
                            return True  
            # Check attribute is product_product quantity  
            elif attribute == 'prod_qty':
                svalue = value.split(":")
                print svalue[0]
                print svalue[1]
                product_code = eval(svalue[0])
                print "product_product code for prod_qty", product_code
                product_qty = eval(svalue[1])
                print "product_product qty for prod_qty", product_qty
                for order_line in order.order_line:   
                    if order_line.product_id.default_code == product_code:
                        print "order_line.product_uom_qty", order_line.product_uom_qty
                        
                        if comparator == '==':
                            print 'EQUAL'
                            if order_line.product_uom_qty == product_qty:
                                return True
                             
                        elif comparator == '!=':    
                            if order_line.product_uom_qty != product_qty:
                                return True
                        elif comparator == '>':
                            if order_line.product_uom_qty > product_qty:
                                return True
                        elif comparator == '<':    
                            if order_line.product_uom_qty < product_qty:
                                return True
                        elif comparator == '>=':
                            print 'GREATER THAN OF EQUAL'
                            if order_line.product_uom_qty >= product_qty:
                                return True
                        elif comparator == '<=':    
                            if order_line.product_uom_qty <= product_qty:
                                return True
            # Check attribute is product_product category quantity  
            elif attribute == 'cat_qty':
                svalue = value.split(":")
                print svalue[0]
                print svalue[1]
                category_code = eval(svalue[0])
                print "product_product code for prod_qty", category_code
                product_qty = eval(svalue[1])
                print "product_product qty for prod_qty", product_qty
                for order_line in order.order_line:  
#                     product_obj = self.pool.get('product_product.product_product').search(cursor, user, [('id', '=', order_line.product_id.id)], context=context)
#                     product_template_lst = self.pool.get('product_product.template').search(cursor, user, [('id', '=', product_obj[0])], context=context)
#                     tmpl_obj = self.pool.get('product_product.template').browse(cursor, user, product_template_lst[0], context)
#                     print tmpl_obj.categ_id
#                     product_categ_lst = self.pool.get('product_product.category').search(cursor, user, [('id', '=', tmpl_obj.categ_id.id)], context=context)
#                     categ_obj = self.pool.get('product_product.category').browse(cursor, user, product_categ_lst[0], context)
                        product_obj = self.pool.get('product_product.product_product').search(cursor, user, [('id', '=', order_line.product_id.id)], context=context)
                        product_lst = self.pool.get('product_product.product_product').search(cursor, user, [('id', '=', product_obj[0])], context=context)
                        prod_obj = self.pool.get('product_product.product_product').browse(cursor, user, product_lst[0], context)
                        # print "product_lst.product_tmpl_id.id",prod_obj.product_tmpl_id.id
                        product_template_lst = self.pool.get('product_product.template').search(cursor, user, [('id', '=', prod_obj.product_tmpl_id.id)], context=context)
                        tmpl_obj = self.pool.get('product_product.template').browse(cursor, user, product_template_lst[0], context)
                        # print "tmpl_obj.categ_id.id",tmpl_obj.categ_id.id
                        
                        product_categ_lst = self.pool.get('product_product.category').search(cursor, user, [('id', '=', tmpl_obj.categ_id.id)], context=context)
                        categ_obj = self.pool.get('product_product.category').browse(cursor, user, product_categ_lst[0], context)
                        cat_name = categ_obj.name
                        category_name1 = str(cat_name)
                        cat_value1 = str(category_code)
                        category_name = category_name1.strip() 
                        cat_value = cat_value1.strip() 
                        print"category_name--", type(category_name)
                        print"cat_value--", type(cat_value)
                        print"category_str-length-", category_name.__len__()
                        print"cat_str-length-", cat_value.__len__()
                        print"category_", category_name
                        print"cat_str", cat_value
                        print category_name == cat_value
                        if category_name == cat_value:
                            print "order_line.product_uom_qty", order_line.product_uom_qty
                            if comparator == '==':
                                if order_line.product_uom_qty == product_qty:
                                    return True
                            elif comparator == '!=':    
                                if order_line.product_uom_qty != product_qty:
                                    return True
                            elif comparator == '>':
                                if order_line.product_uom_qty > product_qty:
                                    return True
                            elif comparator == '<':    
                                if order_line.product_uom_qty < product_qty:
                                    return True
                            elif comparator == '>=':
                                if order_line.product_uom_qty >= product_qty:
                                    return True
                            elif comparator == '<=':    
                                if order_line.product_uom_qty <= product_qty:
                                    return True                
            # Check attribute is sub total amount                
            elif attribute == 'prod_sub_total':   
                svalue = value.split(":")
                print svalue[0]
                print svalue[1]
                product_code = eval(svalue[0])
                print "product_product code for prod_qty", product_code
                sub_total = eval(svalue[1])
                print "sub_total for sub_total", sub_total
                for order_line in order.order_line:   
                    if order_line.product_id.default_code == product_code:
                        print "order_line.product_uom_qty", order_line.product_uom_qty
                        print "unit price", order_line.price_unit
                        order_subtotal = (order_line.product_uom_qty * order_line.price_unit)
                        print "order subtotal", order_subtotal
                        
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
                print svalue[0]
                print svalue[1]
                product_codes = svalue[0]
                print "product_product code for prod_qty", product_codes
                product_code = product_codes.split(";")
                
                
                product_qty = eval(svalue[1])
                print "product_product qty for prod_qty", product_qty
                qtys = 0.0
                for order_line in order.order_line:  
                    for p_code in product_code: 
                        
                        if order_line.product_id.default_code == eval(p_code):
                            print "order_line.product_uom_qty", order_line.product_uom_qty
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
                for order_line in order.order_line:  
                    for p_code in product_code: 
                        if order_line.product_id.default_code == eval(p_code):
                            print "order_line.product_id.default_code", order_line.product_id.default_code
                            print "eval(p_code)", eval(p_code)
                            product_id_index = product_code.index(p_code)
                            print "product_id_index", product_id_index
                            product_qty = uom_qty[product_id_index]
                            qtys += int(order_line.product_uom_qty / int(product_qty))
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
        print "primary condition check1"
        if not context:
            context = {}
        expression_obj = self.pool.get('promos.rules.conditions.exps')
        print "primary condition check2"
        
#         try:
#         self.check_primary_conditions(cursor, user,
#                                            promotion_rule, order,
#                                            context)
#             
#         return True    
#         except Exception, e:
#                 LOGGER.debug('Error %s', e)
#                 return False
       
            # Now to the rules checking
        expected_result = eval(promotion_rule.expected_logic_result)  # True,False
        logic = promotion_rule.logic  # All ,Any
        # MMK
        condition = False
            # Evaluate each expression

#                     result = expression_obj.evaluate(cursor, user,
#                                               expression, order, context)
                    # For and logic, any False is completely false
                    # MMK
#                     if (result == expected_result) and (logic == 'and'):
#                         return True
        if (logic == 'and' and expected_result == True):
            for expression in promotion_rule.expressions:
                print 'expression >>> ', expression.value
#                 result = 'Execution Failed'
#            
#             
#                 try:
                result = self.check_primary_conditions(
                                        cursor, user,
                                        promotion_rule, order, expression,
                                        context)
#                
                print "output condition result------------------------", result
                print' expected result >>>> ', expected_result
                
                if result == True:
                    condition = result
                else:
                    condition = result
                    break
            if condition == True:
                return True
            else:
                return False
                        
                        # OLD
#                     if (not (result == expected_result)) and (logic == 'and'):
#                         return False
                    # For OR logic any True is completely True
                    # OLD
#                     if (result == expected_result) and (logic == 'or'):
#                         return True
                    # For AND logic all True is completely True
#                     if (result == expected_result) and (logic == 'and'):
#                         return True
                    # If stop_further is given, then execution stops  if the
                    # condition was satisfied
#                     if (result == expected_result) and expression.stop_further:
#                         return True
#                 except Exception,e:
#                         LOGGER.debug('Error %s', e)
#                         return False
#                         print "Codes is in exception................................................."
# #                raise osv.except_osv("Expression Error", e)
#         
# #                 finally:
#                     if DEBUG:
#                         LOGGER.debug('Promotions %s evaluated to %s', expression.serialised_expr, result)
#                         if logic == 'and':
#                             # If control comes here for and logic, then all conditions were 
#                             # satisfied
#                             return True
        # if control comes here for OR logic, none were satisfied
#         return False
        
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
            action_obj.execute(cursor, user, action.id,
                                   order, context=None)
            # except Exception, error:
                # raise error
        return True
        
        
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
        vals = {}
        so_promotion_obj = self.pool.get('so.promotion.line')
        promo_line_id = pro_id = None
        # flag=True
        # cursor.execute('update sale_order set promo_state=True where id = %s', (order_id,))
        order = self.pool.get('sale.order').browse(cursor, user,
                                                   order_id, context=context)
        print "order----", order
        active_promos = self.search(cursor, user,
                                    [('active', '=', True)],
                                    context=context)
        print "active_promos------ ", active_promos
        for promotion_rule in self.browse(cursor, user,
                                          active_promos, context):
            result = self.evaluate(cursor, user,
                                   promotion_rule, order,
                                   context)
            
            # MMK
            # Apply Promotions Here
            print "result------------------------------" , result          
            # And so yin result ka true phit ya mal
            # OR so yin result ka false phit ya mal   
            if result:
#                 try:
                    # #in this case ,I add promotion id to the promotion line :)MMK
                    # promotion rule id
#                     pro_id = promotion_rule.id
#                     order_id = order.id
#                     if pro_id:
#                         promo_id = so_promotion_obj.search(cursor, user, [('promo_line_id', '=', order_id), ('pro_id', '=', pro_id)], context)
#                         vals = {
#                                            'pro_id':pro_id,
#                                            'promo_line_id':order_id,
#                                            'from_date':promotion_rule.from_date,
#                                            'to_date':promotion_rule.to_date
#                                   }
#                         if promo_id:
#                             so_promotion_obj.write(cursor, user, promo_id[0], vals)
#                         else:
#                             so_promotion_obj.create(cursor, user, vals, context=context)
#                             
#                     print "promotion_rule id-------------", promotion_rule.id
#                     print "promotion_rule id-....name--------------", promotion_rule.name
                     self.execute_actions(cursor, user,
                                      promotion_rule, order_id,
                                      context)
                    
#                     except Exception, e:
#                                     raise osv.except_osv(
#                                           "Promotions",
#                                           tools.ustr(e)
#                                           )
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
        # Case 6   
        if attribute in ['prods_multi_uom_qty']:
            return {
                    'value':{
#                             'value':"'p1';'p2';'p3'|p1_uom;p2_uom;p3_uom:0.00"
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
        """
        Checks the validity
        @param cursor: Database Cursor
        @param user: ID of User
        @param vals: Values of current record.
        @param context: Context(no direct use).
        """
        print "validate in Expression "
        NUMERCIAL_COMPARATORS = ['==', '!=', '<=', '<', '>', '>=']
        ITERATOR_COMPARATORS = ['in', 'not in']
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
                         ] and \
            not comparator in NUMERCIAL_COMPARATORS:
            
            raise Exception(
                            "Only %s can be used with %s"
                            % ",".join(NUMERCIAL_COMPARATORS), attribute
                            )
        # Mismatch 2:
#         if attribute in [
#                          'product_product' ,
#                         
#                         ] and \
#             not comparator in ITERATOR_COMPARATORS:
#             
#             raise Exception(
#                             "Only %s can be used with Product Code" 
#                             % ",".join(ITERATOR_COMPARATORS)
#                             )
        # Mismatch 3:
#         if attribute == 'product_cat' and \
#             not comparator in ITERATOR_COMPARATORS:
#             
#             raise Exception(
#                             "Only %s can be used with Product Category" 
#                             % ",".join(ITERATOR_COMPARATORS)
#                             )  
#         if attribute == 'product_cat' and \
#             not comparator in NUMERCIAL_COMPARATORS:
#             
#             raise Exception(
#                             "Only %s can be used with Product Category" 
#                             % ",".join(NUMERCIAL_COMPARATORS)
#                             )        
        # Mismatch 4:
        if attribute in [
                         # 'prods_qty',
                         'prod_qty',
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
                    print "product_code", product_code
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
        print "validate in Expression "
                    
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
            print "product_product codes in serialize", product_codes
            product_code = product_codes.split(";")
            # print "product_product codes in serialize",product_code
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
        prod_net_price = {}
        prod_lines = {}
        for line in order.order_line:
            if line.product_id:
                product_code = line.product_id.code
                products.append(product_code)
                prod_lines[product_code] = line.product_id
                prod_qty[product_code] = prod_qty.get(
                                            product_code, 0.00
                                                    ) + line.product_uom_qty
#                prod_net_price[product_code] = prod_net_price.get(
#                                                    product_code, 0.00
#                                                    ) + line.price_net
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
#     def create(self, cursor, user, vals,context):
#         """
#         Serialise before save
#         @param cursor: Database Cursor
#         @param user: ID of User
#         @param vals: Values of current record.
#         @param context: Context(no direct use).
#         """
# #         try:
# #             self.validate(cursor, user, vals, context)
# #             print  ''
# #         except Exception, e:
# #             raise osv.except_osv("Invalid Expression", tools.ustr(e))
#         vals['serialised_expr'] = self.serialise(vals['attribute'],
#                                                  vals['comparator'],
#                                                  vals['value'])
#         super(PromotionsRulesConditionsExprs, self).create(cursor, user,
#                                                            vals, context)
    
#     def create(self, cursor, user, vals, context):
#         """
#         Serialise before save
#         @param cursor: Database Cursor
#         @param user: ID of User
#         @param vals: Values of current record.
#         @param context: Context(no direct use).
#         """
#         print vals
#         auto = self.pool.get('ir.sequence').get(cursor, user,
#             'sq_line.code') or '/'
#         vals['sequence'] = auto
#         self.validate(cursor, user, vals, context)
# #         try:
# #             self.validate(cursor, user, vals, context)
# #             print  ''
# #         except Exception, e:
# #             raise osv.except_osv("Invalid Expression", tools.ustr(e))
#         vals['serialised_expr'] = self.serialise(vals['attribute'],
#                                                  vals['comparator'],
#                                                  vals['value'])
#         super(PromotionsRulesConditionsExprs, self).create(cursor, user,
#                                                            vals, context)
    
    def write(self, cursor, user, ids, vals, context):
        """
        Serialise before Write
        @param cursor: Database Cursor
        @param user: ID of User
        @param  ids: ID of current record.
        @param vals: Values of current record.
        @param context: Context(no direct use).
        """
        # Validate before save
        if type(ids) in [list, tuple] and ids:
            ids = ids[0]
        try:
            old_vals = self.read(cursor, user, ids,
                                 ['attribute', 'comparator', 'value'],
                                 context)
            old_vals.update(vals)
            old_vals.has_key('id') and old_vals.pop('id')
            self.validate(cursor, user, old_vals, context)
        except Exception, e:
        # raise osv.except_osv("Invalid Expression", tools.ustr(e))
        # only value may have changed and client gives only value
            vals = old_vals 
            vals['serialised_expr'] = self.serialise(vals['attribute'],
                                                 vals['comparator'],
                                                 vals['value'])
            super(PromotionsRulesConditionsExprs, self).write(cursor, user, ids,
                                                           vals, context)
        
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
        if action_type in ['prod_multi_get_x', ] :
            return{
                   'value' : {
                              'product_code':"'product_code_x1';'product_code_x2':'product_code_x'",
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
		 # kzo
        if action_type in ['foc_any_product', ] :
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
        # Finally if nothing works
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
 
       
    def action_fix_amt_on_grand_total(self, cursor, user,
                               action, order, context=None):

        order_obj = self.pool.get('sale.order')
        print "total amount", order.amount_total
        print "parameter", eval(action.arguments)
        order.discount_total = eval(action.arguments)
      
 
        if action.action_type == 'fix_amt_on_grand_total':
            return order_obj.write(cursor, user, order.id,
                                         {
                                          'discount_total':eval(action.arguments),
                                          }, context)
        
                
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
        orderline_ids = []
        order_obj = self.pool.get('sale.order')
        order_line_obj = self.pool.get('sale.order.line')
        for order_line in order.order_line:
            print "order_line.product_id.default_code", order_line.product_id.default_code
            print "eval(action.product_code)", eval(action.product_code)
            if order_line.product_id.default_code == eval(action.product_code):
                print "order line id", order_line.id
                discount_amt = 0.0
                orderline_ids.append(order_line.id)
                # MMK
                order_line_obj.write(cursor,
                                     user,
                                    orderline_ids,
                                     {
                                      'discount':eval(action.arguments),
                                      },
                                     context
                                     )
                if order_line.price_unit:
                    discount_amt = float(order_line.discount) * (float(order_line.price_unit * order_line.product_uom_qty)) / 100
                    order_line_obj.write(cursor,
                                         user,
                                        orderline_ids,
                                         {
                                          'discount_amt':discount_amt,
                                          },
                                         context
                                         )
                for a in range(0, 7):
                    print 'update...'
                    order_obj.button_dummy(cursor, user, [order.id], context=context) 
                    order_obj._amount_all_wrapper(cursor, user, order.id, ['amount_untaxed', 'total_dis', 'amount_tax', 'amount_total'], None, context=context)
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
        print 'Fixed Amount on Product'
        orderline_ids = []
        order_line_obj = self.pool.get('sale.order.line')
        product_obj = self.pool.get('product.product')
        line_name = '%s on %s' % (action.promotion.name,
                                     eval(action.product_code))
        product_id = product_obj.search(cursor, user,
                       [('default_code', '=', eval(action.product_code))],
                       context=context)
        print 'Product Code is >>>> ', product_id
        if not product_id:
            raise Exception("No product_product with the product_product code")
        if len(product_id) > 1:
            raise Exception("Many products with same code")
        product = product_obj.browse(cursor, user, product_id[0], context)
        print' product OBJ >>> ', product
        for order_line in order.order_line:
            if order_line.product_id.default_code == eval(action.product_code):
                orderline_ids.append(order_line.id)
                # MMK
            
                order_line_obj.write(cursor,
                                                     user,
                                                     orderline_ids,
                                                     {
                #                                       'price_unit':order_line.price_unit - eval(action.arguments),
                                                    # MMK #multiply the product qty with product discount amt [example: fixed amount for product is 10=> 10*product_uom_qty=subtotal
                                                    'discount_amt':eval(action.arguments) * order_line.product_uom_qty,
                                                      },
                                                     context
                                                     )
        return True

     
    def action_disc_perc_on_grand_total(self, cursor, user,
                               action, order, context=None):

        order_obj = self.pool.get('sale.order')
        if action.action_type == 'disc_perc_on_grand_total':
            return order_obj.write(cursor, user, order.id,
                                         {
                                          'discount_total': eval(action.arguments),
                                          }, context)
            
            
  

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
        
    def action_cart_disc_fix(self, cursor, user,
                              action, order, context=None):
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
                                          'promotion_amt': eval(action.arguments),
                                          }, context)
        return True

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
        order_line_obj = self.pool.get('sale.order.line')
        product_obj = self.pool.get('product_product.product_product')
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
                              'product_uom_qty':quantity,
                              'product_uom':product_x.uom_id.id
                              }, context)
     
     
    def action_buy_cat_get_x_cat(self, cursor, user,
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
        
        order_line_obj = self.pool.get('sale.order.line')
        product_obj = self.pool.get('product_product.product_product')
        # Get Product
        product_x_cat, product_y_cat = [eval(code) \
                                for code in action.product_code.split(":")]
        qtys = 0
        qty_x, qty_y = [eval(arg) \
                                for arg in action.arguments.split(":")]
        # Build a dictionary of product_code to quantity 
        for order_line in order.order_line:
            
#             product1_obj = self.pool.get('product_product.product_product').search(cursor, user, [('id', '=', order_line.product_id.id)], context=context)
#             print "product_obj",product1_obj
#             product_template_lst = self.pool.get('product_product.template').search(cursor, user, [('id', '=', product1_obj[0])], context=context)
#             tmpl_obj = self.pool.get('product_product.template').browse(cursor, user, product_template_lst[0], context)
#             print "product_id",order_line.product_id.id
#             print tmpl_obj.categ_id
#             product_categ_lst = self.pool.get('product_product.category').search(cursor, user, [('id', '=', tmpl_obj.categ_id.id)], context=context)
#             categ_obj = self.pool.get('product_product.category').browse(cursor, user, product_categ_lst[0], context) 
#             print "Category Name", product_x_cat
#             # check sale category is same with category in promotions x value
#             print "product_categ_lst",product_categ_lst
#             print "categ_obj.name",categ_obj.name
            product_obj1 = self.pool.get('product_product.product_product').search(cursor, user, [('id', '=', order_line.product_id.id)], context=context)
            product_lst = self.pool.get('product_product.product_product').search(cursor, user, [('id', '=', product_obj1[0])], context=context)
            prod_obj = self.pool.get('product_product.product_product').browse(cursor, user, product_lst[0], context)
            print "product_lst.product_tmpl_id.id", prod_obj.product_tmpl_id.id
                        
            product_template_lst = self.pool.get('product_product.template').search(cursor, user, [('id', '=', prod_obj.product_tmpl_id.id)], context=context)
            tmpl_obj = self.pool.get('product_product.template').browse(cursor, user, product_template_lst[0], context)
                        
            print "tmpl_obj.categ_id.id", tmpl_obj.categ_id.id
                        
            product_categ_lst = self.pool.get('product_product.category').search(cursor, user, [('id', '=', tmpl_obj.categ_id.id)], context=context)
            categ_obj = self.pool.get('product_product.category').browse(cursor, user, product_categ_lst[0], context)
            cat_name = categ_obj.name
            category_name1 = str(cat_name)
            cat_value_x = str(product_x_cat)
            cat_value_y = str(product_y_cat)
            category_name = category_name1.strip() 
            cat_value_x = cat_value_x.strip() 
            cat_value_y = cat_value_y.strip() 
            print "category_name", category_name
            print "cat_value", cat_value_x
            print category_name == cat_value_x
            if category_name == cat_value_x:
                # check sale category is same with category in promotions x value
                if category_name == cat_value_y:
                    # to add sale product_product code for promotion
                    product_code = order_line.product_id.default_code
                    print "product_product code", product_code
                    # to add quantity from sale order for qty promotions
                    qtys += order_line.product_uom_qty
                    # to add code id for product_product code for promo
                    product_x2_code_id = product_obj.search(cursor, user,
                                    [('default_code', '=', product_code)], context=context)
                    # Total number of free units of y to give
                    tot_free_y = int((qtys / qty_x) * qty_y)
                    print "tot_free_y", tot_free_y
                    # return next line if promotion exists
                    return self.create_y_line(cursor, user, action,
                                       order, tot_free_y, product_x2_code_id, context)

    
        
    def action_buy_cat_get_x(self, cursor, user,
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
        
        order_line_obj = self.pool.get('sale.order.line')
        product_obj = self.pool.get('product_product.product_product')
        
        orderline_ids = []
        vals = prod_qty = {}
        qtys = 0
        # Get Product
        product_cat, product_y_code = [eval(code) \
                                for code in action.product_code.split(":")]

        product_x2_code_id = product_obj.search(cursor, user,
                                    [('default_code', '=', product_y_code)], context=context)
        qty_x, qty_y = [eval(arg) \
                                for arg in action.arguments.split(":")]
        print "product_cat", product_cat
        print "product_y_code", product_y_code
        # Build a dictionary of product_code to quantity 
        for order_line in order.order_line:
            
#             product1_obj = self.pool.get('product_product.product_product').search(cursor, user, [('id', '=', order_line.product_id.id)], context=context)
#             product_template_lst = self.pool.get('product_product.template').search(cursor, user, [('id', '=', product1_obj[0])], context=context)
#             tmpl_obj = self.pool.get('product_product.template').browse(cursor, user, product_template_lst[0], context)
#             print tmpl_obj.categ_id
#             product_categ_lst = self.pool.get('product_product.category').search(cursor, user, [('id', '=', tmpl_obj.categ_id.id)], context=context)
#             categ_obj = self.pool.get('product_product.category').browse(cursor, user, product_categ_lst[0], context) 
#             print "Category Name", product_cat
            product_obj1 = self.pool.get('product_product.product_product').search(cursor, user, [('id', '=', order_line.product_id.id)], context=context)
            product_lst = self.pool.get('product_product.product_product').search(cursor, user, [('id', '=', product_obj1[0])], context=context)
            prod_obj = self.pool.get('product_product.product_product').browse(cursor, user, product_lst[0], context)
            print "product_lst.product_tmpl_id.id", prod_obj.product_tmpl_id.id
                        
            product_template_lst = self.pool.get('product_product.template').search(cursor, user, [('id', '=', prod_obj.product_tmpl_id.id)], context=context)
            tmpl_obj = self.pool.get('product_product.template').browse(cursor, user, product_template_lst[0], context)
                        
            print "tmpl_obj.categ_id.id", tmpl_obj.categ_id.id
                        
            product_categ_lst = self.pool.get('product_product.category').search(cursor, user, [('id', '=', tmpl_obj.categ_id.id)], context=context)
            categ_obj = self.pool.get('product_product.category').browse(cursor, user, product_categ_lst[0], context)
            cat_name = categ_obj.name
            category_name1 = str(cat_name)
            cat_value1 = str(product_cat)
            category_name = category_name1.strip() 
            cat_value = cat_value1.strip() 
            print "category_name", category_name
            print "cat_value", cat_value
            print category_name == cat_value
            if category_name == cat_value:
                
                qtys += order_line.product_uom_qty
                # Total number of free units of y to give
            tot_free_y = int((qtys / qty_x) * qty_y)
            print "tot_free_y", tot_free_y
            return self.create_y_line(cursor, user, action,
                                       order, tot_free_y, product_x2_code_id, context)
        
 
        
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
        
        order_line_obj = self.pool.get('sale.order.line')
        product_obj = self.pool.get('product_product.product_product')
        qtys = 0
        vals = prod_qty = {}
        # Get Product
        product_x_code, product_y_code = [eval(code) \
                                for code in action.product_code.split(":")]
        product_x_code_id = product_obj.search(cursor, user,
                                    [('default_code', '=', product_x_code)], context=context)
        product_x2_code_id = product_obj.search(cursor, user,
                                    [('default_code', '=', product_y_code)], context=context)
        qty_x, qty_y = [eval(arg) \
                                for arg in action.arguments.split(":")]
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
                                            '=', product_y_code)
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
                line_name = "%s (%s)" % (
                                        update_order_line.name.replace(
                                            '(%s)' % action.promotion.name,
                                                                ''),
                                        action.promotion.name
                                                )
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
                existing_order_line_ids.remove(existing_order_line_ids[0])
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
    def action_fix_qty_on_product_code(self, cursor, user,
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
        product_obj = self.pool.get('product.product')
        # Get Product
        product_x_code = eval(action.product_code)
        product_id_for_x1_code = product_obj.search(cursor, user,
                                [('default_code', '=', product_x_code)], context=context)
        # get Quantity
        qty_x = eval(action.arguments)
        # Build a dictionary of product_code to quantity 
        for order_line in order.order_line:
            if order_line.product_id.id:
                return self.create_x_line(cursor, user, action,
                                       order, qty_x, product_id_for_x1_code, context)       
  
            
    # for buy x get x
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
        product_obj = self.pool.get('product_product.product_product')
        # Get Product
        # prod_qty = {}
        qtys = 0
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
        # Build a dictionary of product_code to quantity 
        for order_line in order.order_line:
            if order_line.product_id.id == product_id_for_x1_code[0]:
                print "order_line.product_id.default_code", order_line.product_id.default_code
                print "order_line.product_uom_qty", order_line.product_uom_qty
                # To add qty from sale order line
                qtys += order_line.product_uom_qty
                # Calculate for free qty
                free_qty = int((qtys / qty_x) * qty_y)                               
                print "free qty", free_qty
                # return next line for promotion
                return self.create_x_line(cursor, user, action,
                                       order, free_qty, product_id_for_x2_code, context)
    # prod_multi_uom_get_x
    def action_prod_multi_uom_get_x(self, cursor, user,
                             action, order, context=None):
        product_qtys = []
        qty = 0
        product_obj = self.pool.get('product_product.product_product')
 
        # split entered product_product code with split function
        product_codes = self.tsplit1(action.product_code, (':', '|', ';'))

        print 'product_codes .....', product_codes
        print 'product_product codes length', len(product_codes)
        
        final_code = product_codes[len(product_codes) - 1]
        print "final_code", final_code
        product_x2_code_id = product_obj.search(cursor, user,
                                     [('default_code', '=', eval(final_code))], context=context)         
        print "product_x2_code_id", product_x2_code_id
        product_codes.remove(final_code)
        print 'product_product codes length', len(product_codes)
        # To add promotion uom quantity to product_product qtys array
        x = int(len(product_codes) - 1)
        y = int(len(product_codes) / 2)
        print "xx", x
        print "yy", y
        while y <= x:
            print "x", x
            pcode = eval(product_codes[y])
            print "pcode", pcode
            product_qtys.append(pcode)
            y += 1
        print "product_qty", product_qtys 
        
        # for order line     
        for order_line in order.order_line:
            if order_line.product_id: 
                for product_code in product_codes:
                    print eval(product_code)
                    # Check product_product code with promo product_product codes
                    if order_line.product_id.default_code == eval(product_code):
                            # Get index of product_product codes
                            product_id_index = product_codes.index(product_code,)
                            # Get product_product qty from above product_id
                            product_qty = product_qtys[product_id_index]
                            
                            # division for to get product_product UOM quantity
                            qty += int(order_line.product_uom_qty / int(product_qty))
                            
                            # GEt quantity from promotion rules
                            qty_x, qty_y = [eval(arg) \
                                            for arg in action.arguments.split(":")]
                            
                            if qty >= qty_x:
                           
                                # division for to get free qty UOM
                                free_qty = int((qty / qty_x) * qty_y)
                                print "free_qty", free_qty
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
    def action_prod_foc_smallest_unitprice(self, cursor, user,
                             action, order, context=None):
            product_obj = self.pool.get('product_product.product_product')
            # product_codes = [eval(code) \
            #                    for code in action.product_code.split("::")]
            
        
            product_codes = self.tsplit(action.product_code, ('::'))
           
            new_codes_list = []
            print 'product_codes 1.....', product_codes
            free_qty = eval(action.arguments)
            print "free_qty" , free_qty
        
            prices = []
        
        
            for order_line in order.order_line:        
                if order_line.product_id:
                        print "ok"
                        print "order_line.product_id.id", order_line.product_id.id
                        print 'product_codes', product_codes
                        print 'order_line.product_id.default_code...', order_line.product_id.default_code
                        
                        # if product_codes.__contains__(order_line.product_id.default_code):
                        for p in product_codes:
                                print eval(p)
                                if eval(p) == order_line.product_id.default_code:
                                    new_codes_list.append(order_line.product_id.default_code)
                                    prices.append(order_line.price_unit)
                                    print "new_codes_list", new_codes_list
                                    print "prices", prices
                        
                       
            sort_prices = sorted(prices)     
            print 'sort_prices' , sort_prices
            print 'smallest' , sort_prices[0] 
            sprice = sort_prices[0]
            index = prices.index(sprice,)
            print "index", index
            product_x_code = new_codes_list[index]  
            print product_x_code
            product_x2_code = product_obj.search(cursor, user,
                                [('default_code', '=', product_x_code)], context=context)
            return self.create_y_line(cursor, user, action,
                                       order, free_qty, product_x2_code, context)
            
         
    
    # for buy prod_multi_get_x
    def action_prod_multi_get_x(self, cursor, user,
                             action, order, context=None):
     
        product_obj = self.pool.get('product_product.product_product')
        print "action product_product codes", action.product_code
        product_codes = self.tsplit(action.product_code, (':', ';'))

        print 'product_codes .....', product_codes
        qty = 0
        final_code = product_codes[len(product_codes) - 1]
        print "final_code", final_code
        product_x2_code_id = product_obj.search(cursor, user,
                                    [('default_code', '=', eval(final_code))], context=context)
        print "product_x2_code_id", product_x2_code_id
        product_codes.remove(final_code)

        qty_x, qty_y = [eval(arg) \
                                            for arg in action.arguments.split(":")]
        
              
        for order_line in order.order_line:        
                if order_line.product_id:
                    # print "order_line.product_id", order_line.product_id
                    for product_code in product_codes:
                        print eval(product_code)
                        if order_line.product_id.default_code == eval(product_code):    
                            qty += order_line.product_uom_qty
                            print "qty", qty
                            print "qty_x", qty_x
                            print "qty_y", qty_y
        if qty >= qty_x:
            free_qty = int((qty / qty_x) * qty_y)
            print "free qty", free_qty
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
        # get Quantity
        for order_line in order.order_line:
#             product_obj = self.pool.get('product_product.product_product').search(cursor, user, [('id', '=', order_line.product_id.id)], context=context)
#         
#             product_template_lst = self.pool.get('product_product.template').search(cursor, user, [('id', '=', product_obj[0])], context=context)
#             tmpl_obj = self.pool.get('product_product.template').browse(cursor, user, product_template_lst[0], context)
#             print tmpl_obj.categ_id
#             product_categ_lst = self.pool.get('product_product.category').search(cursor, user, [('id', '=', tmpl_obj.categ_id.id)], context=context)
#             categ_obj = self.pool.get('product_product.category').browse(cursor, user, product_categ_lst[0], context)
            product_obj = self.pool.get('product_product.product_product').search(cursor, user, [('id', '=', order_line.product_id.id)], context=context)
            product_lst = self.pool.get('product_product.product_product').search(cursor, user, [('id', '=', product_obj[0])], context=context)
            prod_obj = self.pool.get('product_product.product_product').browse(cursor, user, product_lst[0], context)
            # print "product_lst.product_tmpl_id.id",prod_obj.product_tmpl_id.id
            product_template_lst = self.pool.get('product_product.template').search(cursor, user, [('id', '=', prod_obj.product_tmpl_id.id)], context=context)
            tmpl_obj = self.pool.get('product_product.template').browse(cursor, user, product_template_lst[0], context)
            # print "tmpl_obj.categ_id.id",tmpl_obj.categ_id.id
            product_categ_lst = self.pool.get('product_product.category').search(cursor, user, [('id', '=', tmpl_obj.categ_id.id)], context=context)
            categ_obj = self.pool.get('product_product.category').browse(cursor, user, product_categ_lst[0], context)
            cat_name = categ_obj.name
            category_name1 = str(cat_name)
            cat_value1 = str(eval(action.product_code))
            category_name = category_name1.strip() 
            cat_value = cat_value1.strip() 
            print"category_name--", type(category_name)
            print"cat_value--", type(cat_value)
            print"category_str-length-", category_name.__len__()
            print"cat_str-length-", cat_value.__len__()
            print"category_", category_name
            print"cat_str", cat_value
            print category_name == cat_value
            if category_name == cat_value:
                orderline_ids.append(order_line.id)
                print 'orderline_ids ', orderline_ids  
        print 'order_line.id ', order_line.id     
        return order_line_obj.write(cursor,
                                     user,
                                     orderline_ids,
                                     {
                                      'discount':eval(action.arguments),
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
#         product_obj = self.pool.get('product_product.product_product')
#         product_template_id = self.pool.get('product_product.template').search(cursor,user,[('categ_id','=',product_categ_id[0])],context=context)
#         product_id = self.pool.get('product_product.product_product').search(cursor,user,[('product_tmpl_id','=',product_template_id[0])],context=context)
#        
#        
#         product_categ_id = self.pool.get('product_product.category').search(cursor, user,
#                                         [('name', '=', eval(action.product_code))], context=context)
#         for order_line in order.order_line:
#            
#           
#             if order_line.product_id.id == product_id[0]:
#                 return self.create_x_line(cursor, user, action,
#                                                    order, foc_qty, foc_product_id, context)
        return True
    
    
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
        print 'action >>> ', action
        print 'method >>> ', method_name
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
    
    def write(self, cursor, user, ids, vals, context):
        """
        Validate before Write
        @param cursor: Database Cursor
        @param user: ID of User
        @param vals: Values of current record.
        @param context: Context(no direct use).
        """
        # Validate before save
        if type(ids) in [list, tuple] and ids:
            ids = ids[0]
        try:
            old_vals = self.read(cursor, user, ids,
                                 ['action_type', 'product_code', 'arguments'],
                                 context)
            old_vals.update(vals)
            old_vals.has_key('id') and old_vals.pop('id')
            self.validate(cursor, user, old_vals, context)
        except Exception, e:
            raise osv.except_osv("Invalid Expression", tools.ustr(e))
        # only value may have changed and client gives only value
        vals = old_vals 
        super(PromotionsRulesActions, self).write(cursor, user, ids,
                                                           vals, context)
    
PromotionsRulesActions()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
