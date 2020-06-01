#from firebase import firebase
from firebase.firebase import FirebaseApplication, FirebaseAuthentication
from openerp import models, fields, api
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate('/opt/odoo/customs/custom_addons_new/firebase_cloud_filestore_sync/json/tabletsales-1373-firebase-adminsdk-12xpb-9cafccb3de.json')
firebase_admin.initialize_app(cred)
            
class product_product(models.Model):
    _inherit = 'product.product' 
    
    def sync_cloud_filestore(self):
        
        firebase_admin.get_app()        
        db = firestore.client()
        
        #get product
        self._cr.execute("""select  pp.id,pt.list_price,coalesce(replace(pt.description,',',';'), ' ') as description,pt.categ_id,pc.name as categ_name,pp.default_code, 
            pt.name,substring(replace(cast(pt.image_small as text),'/',''),1,5) as image_small,pt.main_group,pt.uom_ratio,
            pp.product_tmpl_id,pt.is_foc,pp.sequence,pt.type,pt.uom_id,ccs.id team_id
            from product_sale_group_rel rel ,
            crm_case_section ccs ,product_template pt, product_product pp , product_category pc
            where pp.id = rel.product_id
            and pt.id = pp.product_tmpl_id
            and pt.active = true
            and pp.active = true
            and ccs.sale_group_id = rel.sale_group_id
            and pc.id = pt.categ_id""")
        for row in self._cr.dictfetchall():
            node = str(row['id'])
            doc_ref = db.collection('product_product').document(node)
            doc_ref.set(row)
        
    def sync_product_uom(self):
        
        firebase_admin.get_app()        
        db = firestore.client()
        
        #get uom
        self._cr.execute("""select distinct uom_id,uom_name,ratio,template_id,product_id,team_id from(
                    select  pu.id as uom_id,pu.name as uom_name ,floor(round(1/factor,2)) as ratio,
                    pur.product_template_id as template_id,pp.id as product_id,ccs.id as team_id
                    from product_uom pu , product_template_product_uom_rel pur ,
                    product_product pp,
                    product_sale_group_rel rel,crm_case_section ccs
                    where pp.product_tmpl_id = pur.product_template_id
                    and rel.product_id = pp.id
                    and pu.id = pur.product_uom_id
                    and rel.sale_group_id=ccs.sale_group_id)A""")
        for row in self._cr.dictfetchall():
            node = str(row['uom_id'])
            doc_ref = db.collection('uom_uom').document(node)
            doc_ref.set(row)  
            
    def sync_customers(self):
        
        firebase_admin.get_app()        
        db = firestore.client()
        
        #get customers
        self._cr.execute("""select A.id,A.name,A.image,A.is_company, A.image_small,replace(A.street,',',';') street, replace(A.street2,',',';') street2,A.city,A.website,
                            replace(A.phone,',',';') phone,A.township, replace(A.mobile,',',';') mobile,A.email,A.company_id,A.customer, 
                            A.customer_code,A.mobile_customer,A.shop_name ,
                            A.address,
                            A.zip,A.state_name,A.partner_latitude,A.partner_longitude,A.sale_plan_day_id,A.image_medium,A.credit_limit,
                            A.credit_allow,A.sales_channel,A.branch_id,A.pricelist_id,A.payment_term_id,A.outlet_type ,
                            A.city_id,A.township_id,A.country_id,A.state_id,A.unit,A.class_id,A.chiller,A.frequency_id,A.temp_customer,
                            A.is_consignment,A.hamper,A.is_bank,A.is_cheque,A.sale_team team_id
                            from (
                            select RP.id,RP.name,'' as image,RP.is_company,RPS.line_id as sale_plan_day_id,
                            '' as image_small,RP.street,RP.street2,RC.name as city,RP.website,
                            RP.phone,RT.name as township,RP.mobile,RP.email,RP.company_id,RP.customer, 
                            RP.customer_code,RP.mobile_customer,OT.name as shop_name,RP.address,RP.zip ,RP.partner_latitude,RP.partner_longitude,RS.name as state_name,
                            substring(replace(cast(RP.image_medium as text),'/',''),1,5) as image_medium,RP.credit_limit,RP.credit_allow,
                            RP.sales_channel,RP.branch_id,RP.pricelist_id,RP.payment_term_id,RP.outlet_type,RP.city as city_id,RP.township as township_id,
                            RP.country_id,RP.state_id,RP.unit,RP.class_id,RP.chiller,RP.frequency_id,RP.temp_customer,RP.is_consignment,RP.hamper,
                            RP.is_bank,RP.is_cheque,SPD.sale_team
                            from sale_plan_day SPD ,outlettype_outlettype OT,
                                                sale_plan_day_line RPS , res_partner RP ,res_country_state RS, res_city RC,res_township RT
                                                where SPD.id = RPS.line_id 
                                                and  RS.id = RP.state_id
                                                and RP.township =RT.id
                                                and RP.city = RC.id
                                                and RP.active = true
                                                and RP.outlet_type = OT.id
                                                and RPS.partner_id = RP.id                        
                                                order by  RPS.sequence asc                         
                            
                            )A 
                            where A.customer_code is not null""")
        for row in self._cr.dictfetchall():
            node = str(row['id'])
            doc_ref = db.collection('res_partner').document(node)
            doc_ref.set(row) 
            self._cr.execute("""select a.category_id partner_category_id,b.name partner_category_name
                                    from res_partner_res_partner_category_rel a,res_partner_category b
                                    where a.category_id = b.id
                                    and partner_id=%s""",(row['id'],))
            for partner_categ_row in self._cr.dictfetchall(): 
                partner_categ_node = str(partner_categ_row['partner_category_id'])            
                partner_categ_ref = doc_ref.collection('customer_tags').document(partner_categ_node)    
                partner_categ_ref.set(partner_categ_row)                 
                    
    def sync_users(self):
        
        firebase_admin.get_app()        
        db = firestore.client()                 
                       
        #get users
        self._cr.execute("""select ru.id,ru.active,login,password,partner_id,ru.branch_id ,
                            (select uid from res_groups_users_rel where gid in (select id from res_groups  
                            where name='Allow To Active') and uid=ru.id) allow_to_active,allow_collection_team,allow_product,allow_promotion,allow_customer,allow_sale_plan_day,
                            allow_sale_plan_trip,allow_stock_request,allow_stock_exchange,allow_visit_record,allow_pending_delivery,allow_credit_collection,allow_daily_order_report,
                            allow_daily_sale_report,allow_pre_sale,allow_direct_sale,allow_assets,allow_customer_location_update,allow_stock_check,allow_rental,allow_feedback,allow_customer_create,allow_customer_edit,allow_visit_photo_taken,
                            ccs.id team_id
                            from res_users ru,section_users_rel rel,crm_case_section ccs
                            where ru.id=rel.uid
                            and rel.section_id=ccs.id""")
        for row in self._cr.dictfetchall():
            node = str(row['id'])
            doc_ref = db.collection('res_users').document(node)
            doc_ref.set(row)                
                       
    def sync_promotions(self):    
                
        firebase_admin.get_app()
        db = firestore.client()    
                                   
        #get promotions
        self._cr.execute("""select distinct id,sequence as seq,from_date::character varying from_date,to_date::character varying to_date,active,name as p_name,
                            logic ,expected_logic_result ,special, special1, special2, special3 ,description,
                            pr.promotion_count, pr.monthly_promotion ,code as p_code,manual,main_group,
                            (select ARRAY_AGG(sale_channel_id) from promo_sale_channel_rel where promo_id=pr.id) sale_channel
                            from promos_rules pr
                            left join promos_rules_res_branch_rel pro_br_rel on (pr.id = pro_br_rel.promos_rules_id)
                            left join promos_rules_product_rel pro_pp_rel on (pr.id=pro_pp_rel.promos_rules_id)
                            where pr.active = true                    
                            and now()::date  between from_date::date and to_date::date
                            and pr.id in (
                                select a.promo_id from promo_sale_channel_rel a
                                inner join sale_team_channel_rel b
                                on a.sale_channel_id = b.sale_channel_id    
                            )
                            and pro_pp_rel.product_id in (
                                select product_id
                                from crm_case_section ccs,product_sale_group_rel rel
                                where ccs.sale_group_id=rel.sale_group_id    
                            )""")
        for row in self._cr.dictfetchall():
            node = str(row['id'])            
            doc_ref = db.collection('promos_rules').document(node) 
            doc_ref.set(row)           

            if doc_ref:
                
                #add promotion actions                       
                self._cr.execute("""select act.id,act.promotion,act.sequence as act_seq ,act.arguments,act.action_type,act.product_code,
                                act.discount_product_code,pro_br_rel.res_branch_id,act.promotion
                                from promos_rules r ,promos_rules_actions act,promos_rules_res_branch_rel pro_br_rel
                                where r.id = act.promotion
                                and r.active = 't'                            
                                and r.id = pro_br_rel.promos_rules_id
                                and r.id=%s""",(row['id'],))
                for action_row in self._cr.dictfetchall():     
                    promo_action_node = str(action_row['id'])            
                    promo_action_ref = doc_ref.collection('promotion_action').document(promo_action_node)    
                    promo_action_ref.set(action_row)            
            
                #add promotion conditions
                self._cr.execute("""select cond.id,cond.promotion,cond.sequence as cond_seq,
                                cond.attribute as cond_attr,cond.comparator as cond_comparator,
                                cond.value as comp_value,pro_br_rel.res_branch_id,cond.promotion
                                from promos_rules r ,promos_rules_conditions_exps cond,promos_rules_res_branch_rel pro_br_rel
                                where r.id = cond.promotion
                                and r.active = 't'                           
                                and r.id = pro_br_rel.promos_rules_id
                                and r.id=%s""",(row['id'],))
                for condition_row in self._cr.dictfetchall():                
                    promo_condition_node = str(condition_row['id'])            
                    promo_condition_ref = doc_ref.collection('promotion_condition').document(promo_condition_node)    
                    promo_condition_ref.set(condition_row)
                
                #add sale channel
                self._cr.execute("""select sale_channel_id,channel.name sale_channel_name
                                from promo_sale_channel_rel rel,sale_channel channel
                                where rel.sale_channel_id=channel.id
                                and promo_id=%s""",(row['id'],))
                for sale_channel_row in self._cr.dictfetchall():                
                    sale_channel_node = str(sale_channel_row['sale_channel_id'])            
                    sale_channel_ref = doc_ref.collection('sale_channel').document(sale_channel_node)    
                    sale_channel_ref.set(sale_channel_row)
                
                #add partner category
                self._cr.execute("""select category_id partner_category_id,categ.name partner_category_name
                                from promotion_rule_category_rel rel,res_partner_category categ
                                where rel.category_id=categ.id
                                and promotion_id=%s""",(row['id'],))
                for partner_category_row in self._cr.dictfetchall():                
                    partner_category_node = str(partner_category_row['partner_category_id'])            
                    partner_category_ref = doc_ref.collection('customer_tags').document(partner_category_node)    
                    partner_category_ref.set(partner_category_row)
                
                #add join promotion
                self._cr.execute("""select join_promotion_id,promo.name join_promotion_name
                                from promos_rules_join_rel rel,promos_rules promo
                                where rel.join_promotion_id=promo.id
                                and promos_rules_id=%s""",(row['id'],))
                for join_promo_row in self._cr.dictfetchall():                
                    join_promo_node = str(join_promo_row['join_promotion_id'])            
                    join_promo_ref = doc_ref.collection('join_promotion').document(join_promo_node)    
                    join_promo_ref.set(join_promo_row) 
                    
                #add branch
                self._cr.execute("""select res_branch_id branch_id,rb.name branch_name
                                from promos_rules_res_branch_rel rel,res_branch rb
                                where rel.res_branch_id=rb.id
                                and promos_rules_id=%s""",(row['id'],))
                for branch_row in self._cr.dictfetchall():                
                    branch_node = str(branch_row['branch_id'])            
                    branch_ref = doc_ref.collection('res_branch').document(branch_node)    
                    branch_ref.set(branch_row)  
                    
                #add outlet type
                self._cr.execute("""select outlettype_id,outlet.name outlettype_name
                                from promos_rules_outlettype_rel rel,outlettype_outlettype outlet
                                where rel.outlettype_id=outlet.id
                                and promos_rules_id=%s""",(row['id'],))
                for outlet_row in self._cr.dictfetchall():                
                    outlet_node = str(outlet_row['outlettype_id'])            
                    outlet_ref = doc_ref.collection('outlettype_outlettype').document(outlet_node)    
                    outlet_ref.set(outlet_row)  
                    
                #add customer
                self._cr.execute("""select res_partner_id,rp.name res_partner_name
                                from promos_rules_res_partner_rel rel,res_partner rp
                                where rel.res_partner_id=rp.id
                                and promos_rules_id=%s""",(row['id'],))
                for customer_row in self._cr.dictfetchall():                
                    customer_node = str(customer_row['res_partner_id'])            
                    customer_ref = doc_ref.collection('res_partner').document(customer_node)    
                    customer_ref.set(customer_row)
                      
                    self._cr.execute("""select a.category_id partner_category_id,b.name partner_category_name
                                    from res_partner_res_partner_category_rel a,res_partner_category b
                                    where a.category_id = b.id
                                    and partner_id=%s""",(customer_row['res_partner_id'],))
                    for partner_categ_row in self._cr.dictfetchall(): 
                        partner_categ_node = str(partner_categ_row['partner_category_id'])            
                        partner_categ_ref = customer_ref.collection('customer_tags').document(partner_categ_node)    
                        partner_categ_ref.set(partner_categ_row)         
                        
                #add product
                self._cr.execute("""select product_id,name_template product_name
                                    from promos_rules_product_rel rel,product_product pp
                                    where rel.product_id=pp.id
                                    and promos_rules_id=%s""",(row['id'],))
                for product_row in self._cr.dictfetchall():                
                    product_node = str(product_row['product_id'])            
                    product_ref = doc_ref.collection('product_product').document(product_node)    
                    product_ref.set(product_row) 
                                                                       
    def sync_product_category(self):    
        
        firebase_admin.get_app()        
        db = firestore.client()
        
        #get product category
        self._cr.execute("""select distinct categ_id,categ_name,section_id team_id from (
                            select pp.product_tmpl_id,pt.list_price , pt.description,pt.categ_id,pc.name as categ_name,ccs.id section_id 
                            from product_sale_group_rel rel,
                            crm_case_section ccs ,product_template pt, product_product pp , product_category pc
                            where pp.id = rel.product_id
                            and pt.id = pp.product_tmpl_id
                            and ccs.sale_group_id = rel.sale_group_id
                            and pc.id = pt.categ_id    
                        )A""")
        for row in self._cr.dictfetchall():
            node = str(row['categ_id'])
            doc_ref = db.collection('product_category').document(node)
            doc_ref.set(row)  
            
    def sync_monthly_promotion_history(self):    
        
        firebase_admin.get_app()        
        db = firestore.client()
                            
        #get monthly promotion history
        self._cr.execute("""select h.id,promotion_id,date::character varying date,partner_id,section_id team_id,user_id sale_man_id
                            from sales_promotion_history h,promos_rules r 
                            where h.promotion_id=r.id
                        """)
        for row in self._cr.dictfetchall():
            node = str(row['id'])
            doc_ref = db.collection('monthly_promotion_history').document(node)
            doc_ref.set(row)            
                               
    def sync_product_pricelists(self):    
        
        firebase_admin.get_app()        
        db = firestore.client()
        
        #get product pricelists
        self._cr.execute("""select ppl.id,ppl.name,ppl.type, ppl.active , cpr.is_default,cpr.team_id
                            from price_list_line cpr , product_pricelist ppl
                            where ppl.id = cpr.property_product_pricelist 
                            and ppl.active = true""")
        for row in self._cr.dictfetchall():
            node = str(row['id'])
            doc_ref = db.collection('product_pricelist').document(node)
            doc_ref.set(row) 
            self._cr.execute("""select pv.id,date_end::character varying date_end,date_start::character varying date_start,pv.active,pv.name,pv.pricelist_id 
                                from product_pricelist_version pv, product_pricelist pp where pv.pricelist_id = pp.id   
                                and pv.active = true
                                and pp.id=%s""",(row['id'],))
            for version_row in self._cr.dictfetchall(): 
                version_node = str(version_row['id'])            
                version_ref = doc_ref.collection('product_pricelist_version').document(version_node)    
                version_ref.set(version_row)  
                self._cr.execute("""select pi.id,pi.price_discount,pi.sequence,pi.product_tmpl_id,pi.name,pp.id base_pricelist_id,
                                    pi.product_id,pi.base,pi.price_version_id,pi.min_quantity,
                                    pi.categ_id,pi.new_price price_surcharge,pi.product_uom_id
                                    from product_pricelist_item pi, product_pricelist_version pv, product_pricelist pp
                                    where pv.pricelist_id = pp.id                             
                                    and pv.id = pi.price_version_id
                                    and pv.id=%s""",(version_row['id'],))
                for item_row in self._cr.dictfetchall(): 
                    item_node = str(item_row['id'])            
                    item_ref = version_ref.collection('product_pricelist_item').document(item_node)    
                    item_ref.set(item_row)             
                           
    def sync_sale_plan_day(self):    
        
        firebase_admin.get_app()        
        db = firestore.client()
        
        #get sale plan day
        self._cr.execute("""select p.id,p.date::character varying date,p.sale_team team_id,p.name,p.principal,p.week from sale_plan_day p
                            join  crm_case_section c on p.sale_team=c.id
                            where p.active = true""")
        for row in self._cr.dictfetchall():
            node = str(row['id'])
            doc_ref = db.collection('sale_plan_day').document(node)
            doc_ref.set(row) 
            
    def sync_sale_plan_trip(self):    
        
        firebase_admin.get_app()        
        db = firestore.client()
        
        #get sale plan trip
        self._cr.execute("""select distinct p.id,p.date::character varying date,p.sale_team team_id,p.name,p.principal from sale_plan_trip p
                            ,crm_case_section c,res_partner_sale_plan_trip_rel d, res_partner e
                            where  p.sale_team=c.id
                            and p.active = true 
                            and p.id = d.sale_plan_trip_id
                            and e.id = d.partner_id""")
        for row in self._cr.dictfetchall():
            node = str(row['id'])
            doc_ref = db.collection('sale_plan_trip').document(node)
            doc_ref.set(row) 
            
    def sync_tablet_info(self):    
        
        firebase_admin.get_app()        
        db = firestore.client()
        
        #get tablet info
        self._cr.execute("""select id as tablet_id,date::character varying date,create_uid,name,note,mac_address,model,type,storage_day
                            ,replace(hotline,',',';') hotline,sale_team_id team_id,is_testing
                            from tablets_information """)
        for row in self._cr.dictfetchall():
            node = str(row['tablet_id'])
            doc_ref = db.collection('tablet').document(node)
            doc_ref.set(row) 
            
    def sync_branch(self):    
        
        firebase_admin.get_app()        
        db = firestore.client()
        
        #get branch
        self._cr.execute("""select id,name,branch_code from res_branch where active = true""")
        for row in self._cr.dictfetchall():
            node = str(row['id'])
            doc_ref = db.collection('res_branch').document(node)
            doc_ref.set(row) 
            
    def sync_sale_channel(self):    
        
        firebase_admin.get_app()        
        db = firestore.client()
        
        #get sale channel
        self._cr.execute("""select id,name from sale_channel""")
        for row in self._cr.dictfetchall():
            node = str(row['id'])
            doc_ref = db.collection('sale_channel').document(node)
            doc_ref.set(row) 
            
    def sync_payment_term(self):    
        
        firebase_admin.get_app()        
        db = firestore.client()
        
        #get payment term
        self._cr.execute("""select id,name from account_payment_term where active = true""")
        for row in self._cr.dictfetchall():
            node = str(row['id'])
            doc_ref = db.collection('account_payment_term').document(node)
            doc_ref.set(row) 
            
    def sync_city(self):    
        
        firebase_admin.get_app()        
        db = firestore.client()
        
        #get city
        self._cr.execute("""select id,code,name,state_id from res_city""")
        for row in self._cr.dictfetchall():
            node = str(row['id'])
            doc_ref = db.collection('res_city').document(node)
            doc_ref.set(row) 
            
    def sync_township(self):    
        
        firebase_admin.get_app()        
        db = firestore.client()
        
        #get township
        self._cr.execute("""select id,code,name,city from res_township""")
        for row in self._cr.dictfetchall():
            node = str(row['id'])
            doc_ref = db.collection('res_township').document(node)
            doc_ref.set(row) 
            
    def sync_outlet_type(self):    
        
        firebase_admin.get_app()        
        db = firestore.client()
        
        #get outlet type
        self._cr.execute("""select id,name from outlettype_outlettype""")
        for row in self._cr.dictfetchall():
            node = str(row['id'])
            doc_ref = db.collection('outlettype_outlettype').document(node)
            doc_ref.set(row) 
            
    def sync_sale_demarcation(self):    
        
        firebase_admin.get_app()        
        db = firestore.client()
        
        #get sale demarcation
        self._cr.execute("""select id,name from sale_demarcation""")
        for row in self._cr.dictfetchall():
            node = str(row['id'])
            doc_ref = db.collection('sale_demarcation').document(node)
            doc_ref.set(row) 
            
    def sync_sale_class(self):    
        
        firebase_admin.get_app()        
        db = firestore.client()
        
        #get sale class
        self._cr.execute("""select id,name from sale_class""")
        for row in self._cr.dictfetchall():
            node = str(row['id'])
            doc_ref = db.collection('sale_class').document(node)
            doc_ref.set(row) 
            
    def sync_division_state(self):    
        
        firebase_admin.get_app()        
        db = firestore.client()
        
        #get division state
        self._cr.execute("""select id,name from res_country_state""")
        for row in self._cr.dictfetchall():
            node = str(row['id'])
            doc_ref = db.collection('res_country_state').document(node)
            doc_ref.set(row) 
            
    def sync_frequency(self):    
        
        firebase_admin.get_app()        
        db = firestore.client()
        
        #get frequency
        self._cr.execute("""select id,name from plan_frequency""")
        for row in self._cr.dictfetchall():
            node = str(row['id'])
            doc_ref = db.collection('plan_frequency').document(node)
            doc_ref.set(row) 
            
    def sync_stock_check_setting(self):    
        
        firebase_admin.get_app()        
        db = firestore.client()
        
        #get stock check setting
        self._cr.execute("""select scl.id ,sc.outlet_type,scl.product_id,scl.product_uom_qty as quantity,scl.available,scl.facing, scl.chiller from stock_check_setting sc ,stock_check_setting_line scl where sc.id=scl.stock_setting_ids""")
        for row in self._cr.dictfetchall():
            node = str(row['id'])
            doc_ref = db.collection('stock_check_setting').document(node)
            doc_ref.set(row)    
            
    def sync_partner_category(self):    
        
        firebase_admin.get_app()        
        db = firestore.client()
        
        #get partner category
        self._cr.execute("""select id,name from res_partner_category""")
        for row in self._cr.dictfetchall():
            node = str(row['id'])
            doc_ref = db.collection('partner_category').document(node)
            doc_ref.set(row)  
            
    def sync_team_group_product(self):    
        
        firebase_admin.get_app()        
        db = firestore.client()
        
        #get team group product
        self._cr.execute("""select ROW_NUMBER () OVER (ORDER BY ccs.id) id,ccs.id team_id,rel.sale_group_id,product_id
                            from crm_case_section ccs
                            left join sales_group sg on (ccs.sale_group_id=sg.id)
                            left join product_sale_group_rel rel on (rel.sale_group_id=sg.id)""")
        for row in self._cr.dictfetchall():
            node = str(row['id'])
            doc_ref = db.collection('team_group_product').document(node)
            doc_ref.set(row)
               