from openerp.osv import fields, osv
from datetime import datetime
import ast

class mobile_sale_order(osv.osv):
    
    _name = "mobile.sale.order"
    _description = "Mobile Sales Order"
   
    _columns = {
        'name': fields.char('Order Reference', size=64),
        'partner_id':fields.many2one('res.partner', 'Customer'),
        'customer_code':fields.char('Customer Code'),
        'outlet_type':fields.many2one('outlettype.outlettype', 'Outlet Type'),
        'user_id':fields.many2one('res.users', 'Saleman Name'),
        'sale_plan_name':fields.char('Sale Plan Name'),
        'mso_latitude':fields.float('Geo Latitude'),
        'mso_longitude':fields.float('Geo Longitude'),
        'amount_total':fields.float('Total Amount'),
        'type':fields.selection([
                ('credit', 'Credit'),
                ('cash', 'Cash'),
                ('consignment', 'Consignment'),
                ('advanced', 'Advanced')
            ], 'Payment Type'),
        'delivery_remark':fields.selection([
                ('partial', 'Partial'),
                ('delivered', 'Delivered'),
                ('none', 'None')
            ], 'Deliver Remark'),
        'additional_discount':fields.float('Discount'),
        'deduction_amount':fields.float('Deduction Amount'),
        'net_amount':fields.float('Net Amount'),
        'change_amount':fields.float('Change Amount'),
        'remaining_amount':fields.float('Remaining Amount'),
        'balance':fields.float('Balance'),
        'paid_amount':fields.float('Paid Amount'),
        'paid':fields.boolean('Paid'),
          'void_flag':fields.selection([
                ('voided', 'Voided'),
                ('none', 'Unvoid')
            ], 'Void'),
      'date':fields.datetime('Date'),
        'note':fields.text('Note'),
        'order_line': fields.one2many('mobile.sale.order.line', 'order_id', 'Order Lines', copy=True),
        'delivery_order_line': fields.one2many('products.to.deliver', 'sale_order_id', 'Delivery Order Lines', copy=True),
        'tablet_id':fields.many2one('tablets.information', 'Tablet ID'),
        'sale_plan_day_id':fields.many2one('sale.plan.day', 'Sale Plan Day'),
        'sale_plan_trip_id':fields.many2one('sale.plan.trip', 'Sale Plan Trip'),
        'warehouse_id' : fields.many2one('stock.warehouse', 'Warehouse'),
        'sale_team':fields.many2one('crm.case.section', 'Sale Team'),
        'location_id'  : fields.many2one('stock.location', 'Location'),
        'm_status':fields.char('Status'),
        'due_date':fields.date('Due Date'),
        'payment_term': fields.many2one('account.payment.term', 'Payment Term'),
       'promos_line_ids':fields.one2many('mso.promotion.line', 'promo_line_id', 'Promotion Lines')                
    }
    _order = 'id desc'
    _defaults = {
        'date': datetime.now(),
        'm_status' : 'draft',
       
    } 
    
    def create_massive(self, cursor, user, vals, context=None):
        print 'vals',vals
        sale_order_name_list = []
        try : 
            mobile_sale_order_obj=self.pool.get('mobile.sale.order')
            mobile_sale_order_line_obj=self.pool.get('mobile.sale.order.line')
            str ="{"+vals+"}"
            str = str.replace(":''",":'")#change Order_id
            str = str.replace("'',","',")#null
            str = str.replace(":',",":'',")#due to order_id
            str = str.replace("}{", "}|{")
            new_arr = str.split('|')
            result = []
            for data in new_arr:
                x = ast.literal_eval(data)
                result.append(x)
            sale_order=[]
            sale_order_line = []
            for r in result:
                print "length", len(r)
                if len(r)>=28:
                    sale_order.append(r)
                else:
                    sale_order_line.append(r)
            
            if sale_order:
                for so in sale_order:
                    print 'Sale Man Id',so['user_id']
                    cursor.execute('select id From res_users where partner_id  = %s ',(so['user_id'],))
                    data = cursor.fetchall()
                    if data:
                        saleManId = data[0][0]
                    else:
                        saleManId = None
                    mso_result={
                        'customer_code':so['customer_code'],
                        'sale_plan_day_id':so['sale_plan_day_id'],
                        'sale_plan_trip_id':so['sale_plan_trip_id'] ,
                        'paid': True,
                        'warehouse_id':so['warehouse_id'],
                        'tablet_id':so['tablet_id'],
                        'delivery_remark':so['delivery_remark'],
                        'location_id':so['location_id'],
                        'deduction_amount':so['deduction_amount'],
                        'user_id':so['user_id'],
                        'name':so['name'],
                        'paid_amount':so['paid_amount'],
                        'partner_id':so['partner_id'],
                        'sale_plan_name':so['sale_plan_day_name'],
                        'additional_discount':so['additional_discount'],
                        'amount_total':so['amount_total'],
                        'type':so['type'],
                        'void_flag':so['void_flag'],
                        'sale_team':so['sale_team'],
                        'date':so['date'],
                        'due_date':so['due_date'],
                        'payment_term':so['payment_term'],
                        'mso_longitude':so['mso_longitude'],
                        'mso_latitude':so['mso_latitude']
                    }
                    s_order_id = mobile_sale_order_obj.create(cursor, user, mso_result, context=context)
                    print "Create Sale Order",so['name']
                    for sol in sale_order_line:
                        if sol['so_name'] == so['name']:
                                cursor.execute('select id From product_product where product_tmpl_id  = %s ',(sol['product_id'],))
                                data = cursor.fetchall()
                                if data:
                                    productId = data[0][0]
                                else:
                                    productId = None
                                mso_line_res={                                                            
                                  'order_id':s_order_id,
                                  'product_id':productId,
                                  'price_unit':sol['price_unit'],   
                                  'product_uos_qty':sol['product_uos_qty'],   
                                  'discount':sol['discount'],
                                  'sub_total':sol['sub_total'],
                                }
                                mobile_sale_order_line_obj.create(cursor, user, mso_line_res, context=context) 
                                print 'Create Order line',sol['so_name']                     
                    sale_order_name_list.append(so['name'])
            print 'True'
            return True       
        except Exception, e:
            print 'False'
            return False 
        
    def geo_location(self, cr, uid, ids, context=None):
        result = {
                 'name'     : 'Go to Report',
                 'res_model': 'ir.actions.act_url',
                 'type'     : 'ir.actions.act_url',
                 'target'   : 'new',
               }
        data = self.browse(cr, uid, ids)[0]
        latitude = data.mso_latitude
        longitude = data.mso_longitude
        print 'latitude',latitude
        print 'longitude',longitude
        print 'https://www.google.com/maps/@'+ str(latitude) + ',' + str(longitude)+',18z'
        result['url']='https://www.google.com/maps/@'+ str(latitude) + ',' + str(longitude)+',18z'
             
        return result
  #  def action_convert_so(self, cr, uid, ids, context=None):
  #      for saleorder in self.browse(cr, uid, ids, context=context):            
   #         cr.execute('SELECT import_data_from_mobile_to_server(%s,%s)', (saleorder['id'], saleorder['name']))
  #          cr.execute("update mobile_sale_order set m_status='done' where id = %s and name = %s ", (saleorder['id'], saleorder['name'],))
    def action_convert_so(self, cr, uid, ids, context=None):
        #for saleorder in self.browse(cr, uid, ids, context=context):  
        mobile_sale_order_obj=self.pool.get('mobile.sale.order')
        mobile_sale_order_line_obj=self.pool.get('mobile.sale.order.line')

        sale_order_obj=self.pool.get('sale.order')
        sale_order_line_obj=self.pool.get('sale.order.line')


 
        if ids:
            so_value = mobile_sale_order_obj.browse(cr,uid,ids[0],context=context)             
            reference=so_value.name
            s_id=so_value.id
            customer_code=so_value.customer_code#char
            sale_plan_day_id=so_value.sale_plan_day_id.id#integer
            sale_plan_trip_id=so_value.sale_plan_trip_id.id#integer
            paid=so_value.paid#boolean
            warehouse_id=so_value.warehouse_id.id#integer
            tablet_id=so_value.tablet_id.id#integer
            delivery_remark=so_value.delivery_remark#char
            location_id=so_value.location_id.id
            deduction_amount=so_value.deduction_amount#double_precision
            user_id=so_value.user_id.id#integer
            paid_amount=so_value.paid_amount#double_precision
            partner_id=so_value.partner_id.id#integer
            sale_plan_name=so_value.sale_plan_name#char
            note=so_value.note#text
            additional_discount=so_value.additional_discount#double_precision
            amount_total=so_value.amount_total#double_precision
            type=so_value.type#char
            m_status=so_value.m_status#char
            void_flag=so_value.void_flag#char
            sale_team=so_value.sale_team.id#integer
            date=so_value.date#date
            due_date=so_value.due_date#date
            payment_term=so_value.payment_term.id#integer
            mso_longitude=so_value.mso_longitude#double_precision 
            mso_latitude=so_value.mso_latitude#double_precision 
            cr.execute("select id from product_pricelist where type = 'sale'")
            price_list_id=cr.fetchone()[0]
            cr.execute("select TI.sale_team_id from  mobile_sale_order msol,tablets_information TI where msol.tablet_id=TI.id and msol.id=%s",(s_id,))
            sale_team_id=cr.fetchone()
            if sale_team_id:
                sale_team_id=sale_team_id[0]
            else:
                sale_team_id='',
            #print 'data',partner_id
            cr.execute("select cc.analytic_account_id from crm_case_section cc,mobile_sale_order mso where mso.sale_team=cc.id and mso.id=%s",(s_id,))
            analytic_id=cr.fetchone()
            if analytic_id:
                analytic_id=analytic_id[0]
            else:
                analytic_id=False
            if void_flag=='voided':
                state='cancel'
            elif void_flag=='none':
                state='draft'
            so_result={
                       'date_order':date,
                       'partner_id':partner_id,
                       'amount_untaxed':amount_total ,
                       'partner_invoice_id':partner_id,
                       'user_id':user_id,
                       'date_confirm':date,
                       'amount_total':amount_total,
                       'order_policy':'manual',
                       'company_id':1,
                       'payment_term':payment_term,
                        'state':state,
                        'pricelist_id':price_list_id,
                        'picking_policy':'direct',
                        'warehouse_id':warehouse_id,
                        'project_id':analytic_id,
                        'partner_shipping_id':partner_id,
                        #'shipped':'f',
                        'tb_ref_no':reference,
                        'sale_plan_name':sale_plan_name,
                        'payment_type':type,
                        'section_id':sale_team_id,
                        'due_date':due_date,
                        'so_latitude':mso_latitude,
                        'so_longitude':mso_longitude,
                        #'total_dis':additional_discount,
                        'deduct_amt':deduction_amount,    
                        'delivery_remark':delivery_remark,
                        'sale_plan_day_id':sale_plan_day_id,
                        'sale_plan_trip_id':sale_plan_trip_id,
                        'customer_code':customer_code    
                       }
            s_order_id = sale_order_obj.create(cr, uid, so_result, context=context)
            order_line_ids = mobile_sale_order_line_obj.search(cr, uid, [('order_id', 'in', ids)], context=context) 
             
            for line in mobile_sale_order_line_obj.browse(cr, uid, order_line_ids, context=context):
                #print 'line',line
                #print 'line.product_id.id',line.product_id
                cr.execute('select default_code,name_template from product_product where id = %s',(line.product_id.id,))
                #product_tmpl_id=cr.fetchone()[0]
                #print 'product_tmpl_id',product_tmpl_id
                #cr.execute('select default_code,name from product_template where id=%s',(product_tmpl_id,))
                result_data=cr.fetchone()
                product_code = result_data[0]
                print 'Product_code',product_code
                products =result_data[1]
                print 'Product',products
                products_name='['+product_code+'] '+products
                print 's_order_id',s_order_id,line.product_id.id,line.price_unit
                if line.price_unit ==0.0:
                    foc=True
                    products_name='FOC'
                else:
                    foc=False
                    
                so_line_res={                                                            
                                      'order_id':s_order_id,
                                      'product_id':line.product_id.id,
                                      'name':products_name,
                                      'price_unit':line.price_unit,   
                                      'product_uom':1,      
                                      'product_uom_qty':line.product_uos_qty,   
                                      'discount':line.discount,
                                      'discount_amt':float(line.discount) *(float(line.price_unit*line.product_uos_qty)) / 100,
                                      'company_id':1,#company_id,
                                      'state':'draft',
                                      'net_total':line.sub_total,
                                      'sale_foc':foc,
                    
                                    
                             }
                print 'so_line_res',so_line_res
                sale_order_line_obj.create(cr, uid, so_line_res, context=context)

        cr.execute("update mobile_sale_order set m_status='done' where id = %s and name = %s ", (s_id, reference,))
    


    
    def get_products_by_sale_team(self, cr, uid, section_id , context=None, **kwargs):
        cr.execute('''select  pp.product_tmpl_id,pt.list_price , pt.description,pt.categ_id,pc.name as categ_name,pp.default_code, pt.name from crm_case_section_product_product_rel crm_real ,
                        crm_case_section ccs ,product_template pt, product_product pp , product_category pc
                        where pp.id = crm_real.product_product_id
                        and pt.id = pp.product_tmpl_id
                        and ccs.id = crm_real.crm_case_section_id
                        and pc.id = pt.categ_id
                        and ccs.id = %s ''', (section_id,))
        datas = cr.fetchall()
        cr.execute
        return datas
    
    def get_salePlanDays_by_sale_team(self, cr, uid, section_id , context=None, **kwargs):
        cr.execute('''select id,name,date,sale_team from sale_plan_day where sale_team=%s ''', (section_id,))
        datas = cr.fetchall()
        cr.execute
        return datas
    
    # get promotion datas from database
    def get_products_categ_by_sale_team(self, cr, uid, section_id , context=None, **kwargs):
        cr.execute('''select distinct categ_id,categ_name from (
                        select pp.product_tmpl_id,pt.list_price , pt.description,pt.categ_id,pc.name as categ_name from crm_case_section_product_product_rel crm_real ,
                        crm_case_section ccs ,product_template pt, product_product pp , product_category pc
                        where pp.id = crm_real.product_product_id
                        and pt.id = pp.product_tmpl_id
                        and ccs.id = crm_real.crm_case_section_id
                        and pc.id = pt.categ_id
                        and ccs.id = %s
                        )A ''', (section_id,))
        datas = cr.fetchall()
        cr.execute
        return datas
    # get promotion datas from database
    
    def get_promos_datas(self, cr, uid ,section_id , context=None, **kwargs):
        cr.execute('''select id,sequence as seq,from_date ,to_date,active,name as p_name,
                        logic ,expected_logic_result ,special, special1, special2, special3 
                        from promos_rules pr where pr.active = true and main_group in 
                        (select product_maingroup_id 
                        from crm_case_section_product_maingroup_rel mg,crm_case_section cs 
                        where cs.id = mg.crm_case_section_id and cs.id = %s)
                        ''', (section_id,))
        datas = cr.fetchall()
        cr.execute
        return datas
    def get_promos_act_datas(self, cr, uid , section_id , context=None, **kwargs):
        cr.execute('''select act.id,act.promotion,act.sequence as act_seq ,act.arguments,act.action_type,act.product_code
                            from promos_rules r ,promos_rules_actions act
                            where r.id = act.promotion
                            and r.active = 't'
                            and r.main_group in
                            (select product_maingroup_id 
                            from crm_case_section_product_maingroup_rel mg,crm_case_section cs 
                            where cs.id = mg.crm_case_section_id and cs.id = %s)
                    ''', (section_id,))
        datas = cr.fetchall()
        cr.execute
        return datas
    def get_promos_cond_datas(self, cr, uid , section_id ,context=None, **kwargs):
        cr.execute('''select cond.id,cond.promotion,cond.sequence as cond_seq,
                            cond.attribute as cond_attr,cond.comparator as cond_comparator,
                            cond.value as comp_value
                            from promos_rules r ,promos_rules_conditions_exps cond
                            where r.id = cond.promotion
                            and r.active = 't'
                            and r.main_group in
                            (select product_maingroup_id 
                            from crm_case_section_product_maingroup_rel mg,crm_case_section cs 
                            where cs.id = mg.crm_case_section_id and cs.id = %s)
                    ''', (section_id,))
        datas = cr.fetchall()
        cr.execute
        return datas
    def get_promos_rule_partner_datas(self, cr, uid ,section_id , context=None, **kwargs):
        cr.execute('''select category_id,rule_id from rule_partner_cat_rel''')
        datas = cr.fetchall()
        cr.execute
        return datas
    def get_promos_category_datas(self, cr, uid ,section_id , context=None, **kwargs):
        cr.execute('''select id,name from res_partner_category''')
        datas = cr.fetchall()
        cr.execute
        return datas
    #get Mobile Sale Order Datas
    def get_mobile_so_datas(self, cr, uid, todayDateNormal,saleTeamId,saleorderList, context=None, **kwargs):
        saleOrderName = ', '.join(saleorderList) 
        print "sale",str(tuple(saleorderList))
        saleorder = str(tuple(saleorderList))
        mobile_sale_order_obj =self.pool.get('mobile.sale.order')
        list_val = None
        list_val = mobile_sale_order_obj.search(cr,uid,[('due_date','>',todayDateNormal),('sale_team','=',saleTeamId),('name','not in',saleorderList)])
        print 'list_val',list_val
        list = []
        if list_val:
            for val in list_val:
                cr.execute('select id,void_flag,name,create_date,date,partner_id,customer_code,sale_plan_trip_id,sale_plan_day_id,user_id,amount_total,type,delivery_remark,additional_discount,deduction_amount,paid_amount,paid,tablet_id,warehouse_id,location_id,sale_team,due_date,payment_term,mso_latitude,mso_longitude from mobile_sale_order where id=%s',(val,))
                result = cr.fetchall()
                list.append(result)
                print' list',list
        return list
    #get Mobile Sale Order Line Datas
    def get_mobile_soline_datas(self, cr, uid, todayDateNormal,so_ids,context=None, **kwargs):
        print 'So_ids', so_ids
        order_ids = so_ids
#         order_ids = map(int, so_ids)
#         print 'Map Order Id',order_ids
        mobile_so_line_obj =self.pool.get('mobile.sale.order.line')
        list_val = None
        list_val = mobile_so_line_obj.search(cr,uid,[('create_date','>',todayDateNormal),('order_id','in',order_ids)])
        print 'list_val',list_val
        list = []
        if list_val:
            for val in list_val:
                cr.execute('select id,product_id,product_uos_qty,price_unit,discount,sub_total,order_id from mobile_sale_order_line where id=%s',(val,))
                result = cr.fetchall()
                list.append(result)
                print' list',list
        return list
#         cr.execute("select id,product_id,product_uos_qty,price_unit,discount,sub_total,order_id from mobile_sale_order_line where create_date > %s and order_id in(%s)",(todayDateNormal,order_ids,))
# #                             where due_date > %s''',(todayDateNormal,))
#         datas = cr.fetchall()
#         cr.execute
#         return datas
    
    # get pricelsit datas
    def get_pricelist_datas(self, cr, uid ,section_id, context=None, **kwargs):
        cr.execute('''select id,name,type,active from product_pricelist where active = 't' and main_group_id in (select product_maingroup_id 
                        from crm_case_section_product_maingroup_rel mg,crm_case_section cs 
                        where cs.id = mg.crm_case_section_id and cs.id = %s) or main_group_id is null''', (section_id,))
        datas = cr.fetchall()
        cr.execute
        return datas
    def get_pricelist_version_datas(self, cr, uid,section_id , context=None, **kwargs):
        cr.execute('''select pv.id,date_end,date_start,pv.active,pv.name,pv.pricelist_id 
                        from product_pricelist_version pv, product_pricelist pp where pv.pricelist_id = pp.id 
                        and (pp.main_group_id in (select product_maingroup_id 
                        from crm_case_section_product_maingroup_rel mg,crm_case_section cs 
                        where cs.id = mg.crm_case_section_id and cs.id =%s) or pp.main_group_id is null)''', (section_id,))
        datas = cr.fetchall()
        cr.execute
        return datas
    def get_pricelist_item_datas(self, cr, uid,section_id , context=None, **kwargs):
        cr.execute('''select pi.id,pi.price_discount,pi.sequence,pi.product_tmpl_id,pi.name,pi.base_pricelist_id,
                    pi.product_id,pi.base,pi.price_version_id,pi.min_quantity,
                    pi.categ_id,pi.price_surcharge from product_pricelist_item pi, product_pricelist_version pv, product_pricelist pp where pv.pricelist_id = pp.id 
                    and pv.id = pi.price_version_id and (pp.main_group_id in (select product_maingroup_id 
                    from crm_case_section_product_maingroup_rel mg,crm_case_section cs 
                    where cs.id = mg.crm_case_section_id and cs.id = %s) or pp.main_group_id is null)''', (section_id,))
        datas = cr.fetchall()
        cr.execute
        return datas
    
    def get_product_uoms(self, cr, uid , context=None, **kwargs):
        cr.execute('''
                    select distinct pu.id as uom_id,pu.name as uom_name ,1/pu.factor as ratio,pur.product_template_id as  product_template_id
                from product_uom pu , product_template_product_uom_rel pur , product_template pt,product_product pp
                where pt.id = pur.product_template_id
                and pu.id = pur.product_uom_id''')
        datas = cr.fetchall()
        cr.execute
        return datas
    #Get Res Partner and Res Partner Category res_partner_res_partner_category_rel
    def get_res_partner_category_datas(self, cr, uid , context=None, **kwargs):
        cr.execute('''select category_id,partner_id from res_partner_res_partner_category_rel''')
        datas = cr.fetchall()
        cr.execute
        return datas
    
    def get_sale_team_members_datas(self, cr, uid ,member_id,saleteam_id, context=None, **kwargs):
        cr.execute('''select u.id as id,u.active as active,u.login as login,u.password as password,u.partner_id as partner_id,p.name as name from res_users u, res_partner p
                   where u.partner_id = p.id and u.id in(select member_id from crm_case_section cr, sale_member_rel sm where sm.section_id = cr.id and cr.id =%s)''', (saleteam_id,)) 
        datas = cr.fetchall()
        cr.execute
        return datas
    def sale_team_return(self, cr, uid, section_id , saleTeamId, context=None, **kwargs):
        cr.execute('''select DISTINCT cr.id,cr.complete_name,cr.warehouse_id,cr.name,sm.member_id,cr.code,pr.product_product_id,cr.location_id
                    from crm_case_section cr, sale_member_rel sm,crm_case_section_product_product_rel pr where sm.section_id = cr.id and cr.id=pr.crm_case_section_id  
                    and sm.member_id =%s 
                    and cr.id = %s
            ''', (section_id,saleTeamId,))
        datas = cr.fetchall()
        cr.execute
        return datas

    def sale_plan_day_return(self, cr, uid, section_id , context=None, **kwargs):
     
#         cr.execute('''            
#             select p.id,p.date,p.sale_team,p.name,p.main_group from sale_plan_day p
#             join  crm_case_section c on p.sale_team=c.id
#             where p.sale_team=%s
#             ''', (section_id, ))        
        cr.execute('''            
            select p.id,p.date,p.sale_team,p.name,p.principal from sale_plan_day p
            join  crm_case_section c on p.sale_team=c.id
            where p.sale_team=%s
            ''', (section_id, ))
        datas = cr.fetchall()
        cr.execute      
        return datas    
    def sale_plan_trip_return(self, cr, uid, section_id , context=None, **kwargs):
     
        cr.execute('''            
            select p.id,p.date,p.sale_team,p.name,p.principal from sale_plan_trip p
            join  crm_case_section c on p.sale_team=c.id
            where p.sale_team=%s
            ''', (section_id, ))
        datas = cr.fetchall()
        cr.execute
      
        return datas
        
        #kzo
    def stock_picking_type(self, cr, uid , context=None, **kwargs):
        cr.execute('''select id,code from stock_picking_type''')            
        datas = cr.fetchall()        
        return datas
    
    def stock_move_return(self, cr, uid, section_id , context=None, **kwargs):
        cr.execute('''select id,product_qty,product_id,picking_id,state,origin,picking_type_id,location_dest_id,partner_id from stock_move where location_dest_id in(select cr.location_id from crm_case_section cr, sale_member_rel sm where sm.section_id = cr.id and sm.member_id=%s)
            ''', (section_id,))
        datas = cr.fetchall()        
        return datas
    
    def tablet_info(self, cr, uid, tabetId, context=None, **kwargs):    
        cr.execute('''
            select id as tablet_id,date,create_uid,name,note,mac_address,model,type,storage_day,hotline,sale_team_id 
            from tablets_information 
            where name = %s
            ''', (tabetId,))
        datas = cr.fetchall()
        return datas
    
    def get_company_datas(self, cr, uid ,context=None):        
        cr.execute('''select id,name from res_company''')
        datas = cr.fetchall()        
        return datas
    
    def get_res_users(self, cr, uid, sale_team_id , context=None, **kwargs):
        cr.execute('''
            select id,active,login,password,partner_id from res_users where id = %s
            ''', (sale_team_id,))
        datas = cr.fetchall()        
        return datas
    
    def check_account(self, cr, uid, login, pwd, sale_team_id, context=None, **kwargs):
        cr.execute('''
            select c.name as TabletName,D.userid,D.login,D.password from(
            select name,sale_team_id from tablets_information
            )C inner join(
            select A.userid,A.login,A.password,B.id as saleTeamId from(
            select id as userid,login,password from res_users
            )A inner join(
            select DISTINCT cr.id as id,cr.complete_name,cr.warehouse_id,cr.name,sm.member_id,cr.code,cr.location_id
                    from crm_case_section cr, sale_member_rel sm,crm_case_section_product_product_rel pr
                    where sm.section_id = cr.id and cr.id=pr.crm_case_section_id
            ) B on A.userid = B.member_id
            )D on c.sale_team_id = D.saleTeamId
            where c.name = %s
            and D.login= %s
            and d.password = %s
            ''', (sale_team_id, login, pwd,))
        datas = cr.fetchall()            
        return datas  
       
mobile_sale_order()

class mobile_sale_order_line(osv.osv):
    
    _name = "mobile.sale.order.line"
    _description = "Mobile Sales Order"

    _columns = {
        'product_id':fields.many2one('product.product', 'Products'),
        'product_uos_qty':fields.float('Quantity'),
        'uom_id':fields.many2one('product.uom', 'UOM'),
        'price_unit':fields.float('Unit Price'),
        'discount':fields.float('Discount (%)'),
        'order_id': fields.many2one('mobile.sale.order', 'Sale Order'),
        'sub_total':fields.float('Sub Total'),
        'foc':fields.boolean('FOC'),
    }
    _defaults = {
       'product_uos_qty':1.0,
    }   
    
mobile_sale_order_line()

class sale_group(osv.osv):
    _inherit = 'res.users' 
 
    
sale_group()

class mso_promotion_line(osv.osv):
    _name = 'mso.promotion.line'
    _columns = {
              'promo_line_id':fields.many2one('mobile.sale.order', 'Promotion line'),
              'pro_id': fields.many2one('promos.rules', 'Promotion Rule', change_default=True, readonly=False),
              'from_date':fields.datetime('From Date'),
              'to_date':fields.datetime('To Date')
              }
    
def onchange_promo_id(self, cr, uid, ids, pro_id, context=None):
        result = {}
        promo_pool = self.pool.get('promos.rules')
        datas = promo_pool.read(cr, uid, pro_id, ['from_date', 'to_date'], context=context)

        if datas:
            result.update({'from_date':datas['from_date']})
            result.update({'to_date':datas['to_date']})
        return {'value':result}
            
mso_promotion_line()

class mobile_product_yet_to_deliver_line(osv.osv):
    
    _name = "products.to.deliver"
    _description = "Product Yet To Deliver"

    _columns = {
        'product_id':fields.many2one('product.product', 'Products'),
        'uom':fields.many2one('product.uom', 'UOM'),
        'product_qty':fields.float('Quantity'),
        'product_qty_to_deliver':fields.float('Quantity To Deliver'),
        'sale_order_id': fields.many2one('mobile.sale.order', 'Sale Order'),
                }
mobile_product_yet_to_deliver_line()

