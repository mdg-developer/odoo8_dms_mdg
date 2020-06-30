from decimal import Decimal
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate('/Users/phyo936/Downloads/mdg_live.json')
firebase_admin.initialize_app(cred)

cr = None

def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    result = [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]
    for record in result:
        for key in record:
            if(isinstance(record[key], Decimal)):
                value = float(record[key])
                record[key] = value
    return result

def insert_products(cr):
    
    firebase_admin.get_app()        
    db = firestore.client()
     
    query = """select concat(pp.id,ccs.id,rel.sale_group_id) seq,pp.id,pt.list_price,coalesce(replace(pt.description,',',';'), ' ') as description,pt.categ_id,pc.name as categ_name,pp.default_code, 
            pt.name,convert_from(image_small,'utf8') as image_small,pt.main_group,pt.uom_ratio,
            pp.product_tmpl_id,pt.is_foc,pp.sequence,pt.type,pt.uom_id,ccs.id team_id,
            concat(ccs.id,'-',rel.sale_group_id)::character varying product_key
            from product_sale_group_rel rel ,
            crm_case_section ccs ,product_template pt, product_product pp , product_category pc
            where pp.id = rel.product_id
            and pt.id = pp.product_tmpl_id
            and pt.active = true
            and pp.active = true
            and ccs.sale_group_id = rel.sale_group_id
            and pc.id = pt.categ_id;"""
    cr.execute(query)
    resultMap = dictfetchall(cr)
    for row in resultMap:
        node = str(row['seq'])
        print ('product node',node)
        print ('product name',row['name'])
        doc_ref = db.collection('product_product').document(node)
        doc_ref.set(row)        
    print ('inserted product')
    return True

def insert_customers(cr):
    
    firebase_admin.get_app()        
    db = firestore.client()
     
    query = """select A.seq,A.id,A.name,A.image,A.is_company, A.image_small,replace(A.street,',',';') street, replace(A.street2,',',';') street2,A.city,A.website,
                replace(A.phone,',',';') phone,A.township, replace(A.mobile,',',';') mobile,A.email,A.company_id,A.customer, 
                A.customer_code,A.mobile_customer,A.shop_name ,
                A.address,
                A.zip,A.state_name,A.partner_latitude,A.partner_longitude,A.sale_plan_day_id,A.image_medium,
                A.image_one,A.image_two,A.image_three,A.image_four,A.image_five,A.credit_limit,
                A.credit_allow,A.sales_channel,A.branch_id,A.pricelist_id,A.payment_term_id,A.outlet_type ,
                A.city_id,A.township_id,A.country_id,A.state_id,A.unit,A.class_id,A.chiller,A.frequency_id,A.temp_customer,
                A.is_consignment,A.hamper,A.is_bank,A.is_cheque,A.sale_team team_id,customer_tags
                from (
                select concat(RP.id,SPD.id,SPD.sale_team) seq,RP.id,RP.name,'' as image,RP.is_company,RPS.line_id as sale_plan_day_id,
                '' as image_small,RP.street,RP.street2,RC.name as city,RP.website,
                RP.phone,RT.name as township,RP.mobile,RP.email,RP.company_id,RP.customer, 
                RP.customer_code,RP.mobile_customer,OT.name as shop_name,RP.address,RP.zip ,RP.partner_latitude,RP.partner_longitude,RS.name as state_name,
                convert_from(image_medium,'utf8') as image_medium,convert_from(image_one,'utf8') as image_one,
                convert_from(image_two,'utf8') as image_two,convert_from(image_three,'utf8') as image_three,
                convert_from(image_four,'utf8') as image_four,convert_from(image_five,'utf8') as image_five,RP.credit_limit,RP.credit_allow,
                RP.sales_channel,RP.branch_id,RP.pricelist_id,RP.payment_term_id,RP.outlet_type,RP.city as city_id,RP.township as township_id,
                RP.country_id,RP.state_id,RP.unit,RP.class_id,RP.chiller,RP.frequency_id,RP.temp_customer,RP.is_consignment,RP.hamper,
                RP.is_bank,RP.is_cheque,SPD.sale_team,
                (select ARRAY_AGG(a.category_id) partner_category_id
                from res_partner_res_partner_category_rel a,res_partner_category b
                where a.category_id = b.id
                and partner_id=RP.id) customer_tags
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
                where A.customer_code is not null"""
    cr.execute(query)
    resultMap = dictfetchall(cr)
    print ('ready to insert customers')
    for row in resultMap:
        node = str(row['seq'])
        print ('customer node',node)
        print ('customer name',row['name'])
        doc_ref = db.collection('res_partner').document(node)
        doc_ref.set(row)        
    print ('inserted customers')
    return True

def insert_product_pricelists(cr):
    firebase_admin.get_app()
    db = firestore.client()

    # get product pricelists
    cr.execute("""select ppl.id,ppl.name,ppl.type, ppl.active , cpr.is_default,cpr.team_id
                            from price_list_line cpr , product_pricelist ppl
                            where ppl.id = cpr.property_product_pricelist 
                            and ppl.active = true""")
    resultMap = dictfetchall(cr)

    for row in resultMap:
        node = str(row['id'])
        doc_ref = db.collection('product_pricelist').document(node)
        doc_ref.set(row)
        cr.execute("""select pv.id,date_end::character varying date_end,date_start::character varying date_start,pv.active,pv.name,pv.pricelist_id 
                                from product_pricelist_version pv, product_pricelist pp where pv.pricelist_id = pp.id   
                                and pv.active = true
                                and pp.id=%s""", (row['id'],))
        resultPricelistVersionMap = dictfetchall(cr)

        for version_row in resultPricelistVersionMap:
            version_node = str(version_row['id'])
            version_ref = doc_ref.collection('product_pricelist_version').document(version_node)
            version_ref.set(version_row)
            cr.execute("""select pi.id,pi.price_discount,pi.sequence,pi.product_tmpl_id,pi.name,pp.id base_pricelist_id,
                                    pi.product_id,pi.base,pi.price_version_id,pi.min_quantity,
                                    pi.categ_id,pi.new_price price_surcharge,pi.product_uom_id
                                    from product_pricelist_item pi, product_pricelist_version pv, product_pricelist pp
                                    where pv.pricelist_id = pp.id                             
                                    and pv.id = pi.price_version_id
                                    and pv.id=%s""", (version_row['id'],))
            resultPricelistItemMap = dictfetchall(cr)

            for item_row in resultPricelistItemMap:
                item_node = str(item_row['id'])
                item_ref = version_ref.collection('product_pricelist_item').document(item_node)
                item_ref.set(item_row)
    return True

def insert_sale_plan_day(cr):
    firebase_admin.get_app()
    db = firestore.client()

    # get sale plan day
    cr.execute("""select p.id,p.date::character varying date,p.sale_team team_id,p.name,p.principal,p.week ,
                            (select ARRAY_AGG(line.partner_id ORDER BY line.sequence) from sale_plan_day_line line where line.line_id=p.id) res_partner_id
                            from sale_plan_day p
                            join crm_case_section c on p.sale_team=c.id
                            where p.active = true
                            """)
    resultSalePlanDayMap = dictfetchall(cr)

    for row in resultSalePlanDayMap:
        node = str(row['id'])
        doc_ref = db.collection('sale_plan_day').document(node)
        doc_ref.set(row)
    return True


def insert_sale_plan_trip(cr):
    firebase_admin.get_app()
    db = firestore.client()

    # get sale plan trip
    cr.execute("""select distinct p.id,p.date::character varying date,p.sale_team team_id,p.name,p.principal,
                            (select ARRAY_AGG(partner_id order by rp.name) 
                            from res_partner_sale_plan_trip_rel rel,res_partner rp
                            where rel.partner_id=rp.id
                            and sale_plan_trip_id=p.id) res_partner_id
                            from sale_plan_trip p,crm_case_section c,res_partner_sale_plan_trip_rel d, res_partner e
                            where  p.sale_team=c.id
                            and p.active = true 
                            and p.id = d.sale_plan_trip_id
                            and e.id = d.partner_id                            
                            """)
    resultSalePlanTripMap = dictfetchall(cr)

    for row in resultSalePlanTripMap:
        node = str(row['id'])
        doc_ref = db.collection('sale_plan_trip').document(node)
        doc_ref.set(row)
    return True

def insert_promotions(cr):
    
    firebase_admin.get_app()        
    db = firestore.client()
     
    query = """select distinct id,sequence as seq,from_date::character varying from_date,to_date::character varying to_date,active,name as p_name,
                logic ,expected_logic_result ,special, special1, special2, special3 ,description,
                pr.promotion_count, pr.monthly_promotion ,code as p_code,manual,main_group,
                (select ARRAY_AGG(sale_channel_id) from promo_sale_channel_rel where promo_id=pr.id) sale_channel,
                (select ARRAY_AGG(category_id) from promotion_rule_category_rel where promotion_id=pr.id) customer_tags,
                (select ARRAY_AGG(join_promotion_id) from promos_rules_join_rel rel where promos_rules_id=pr.id) join_promotion,
                (select ARRAY_AGG(res_branch_id) from promos_rules_res_branch_rel where promos_rules_id=pr.id) res_branch,
                (select ARRAY_AGG(outlettype_id) from promos_rules_outlettype_rel where promos_rules_id=pr.id) outlettype_outlettype,
                (select ARRAY_AGG(res_partner_id) from promos_rules_res_partner_rel where promos_rules_id=pr.id) res_partner,
                (select ARRAY_AGG(product_id) from promos_rules_product_rel rel where promos_rules_id=pr.id) product_product
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
                )"""
    cr.execute(query)
    resultMap = dictfetchall(cr)
    for row in resultMap:
        node = str(row['id'])
        print ('promotion node',node)
        print ('promotion name',row['p_name'])
        doc_ref = db.collection('promos_rules').document(node)
        doc_ref.set(row)  
        
        if doc_ref:
            #add promotion actions
            action_query = """select act.id,act.promotion,act.sequence as act_seq ,act.arguments,act.action_type,act.product_code,
                            act.discount_product_code,pro_br_rel.res_branch_id,act.promotion
                            from promos_rules r ,promos_rules_actions act,promos_rules_res_branch_rel pro_br_rel
                            where r.id = act.promotion
                            and r.active = 't'                            
                            and r.id = pro_br_rel.promos_rules_id
                            and r.id=%s"""  
            cr.execute(action_query,(row['id'],))
            actionresultMap = dictfetchall(cr)
            for action_row in actionresultMap:     
                promo_action_node = str(action_row['id'])    
                promo_action_ref = doc_ref.collection('promotion_action').document(promo_action_node)    
                promo_action_ref.set(action_row)  
                
            #add promotion conditions  
            condition_query = """select cond.id,cond.promotion,cond.sequence as cond_seq,
                            cond.attribute as cond_attr,cond.comparator as cond_comparator,
                            cond.value as comp_value,pro_br_rel.res_branch_id,cond.promotion
                            from promos_rules r ,promos_rules_conditions_exps cond,promos_rules_res_branch_rel pro_br_rel
                            where r.id = cond.promotion
                            and r.active = 't'                           
                            and r.id = pro_br_rel.promos_rules_id
                            and r.id=%s"""  
            cr.execute(condition_query,(row['id'],))
            conditionresultMap = dictfetchall(cr)
            for condition_row in conditionresultMap:     
                promo_condition_node = str(condition_row['id'])    
                promo_condition_ref = doc_ref.collection('promotion_condition').document(promo_condition_node)    
                promo_condition_ref.set(condition_row)        
    print ('inserted promotions')
    return True

def insert_product_category(cr):
    firebase_admin.get_app()
    db = firestore.client()

    # get product category
    cr.execute("""select distinct categ_id,categ_name,section_id team_id from (
                            select pp.product_tmpl_id,pt.list_price , pt.description,pt.categ_id,pc.name as categ_name,ccs.id section_id 
                            from product_sale_group_rel rel,
                            crm_case_section ccs ,product_template pt, product_product pp , product_category pc
                            where pp.id = rel.product_id
                            and pt.id = pp.product_tmpl_id
                            and ccs.sale_group_id = rel.sale_group_id
                            and pc.id = pt.categ_id   
                        )A""")
    resultMap = dictfetchall(cr)

    for row in resultMap:
        node = str(row['categ_id'])
        doc_ref = db.collection('product_category').document(node)
        doc_ref.set(row)
    return True

def insert_partner_category(cr):
    firebase_admin.get_app()
    db = firestore.client()
    # get partner category
    cr.execute("""select id,name from res_partner_category""")
    resultMap = dictfetchall(cr)

    for row in resultMap:
        node = str(row['id'])
        doc_ref = db.collection('partner_category').document(node)
        doc_ref.set(row)
    return True

import psycopg2
try:
    connection = psycopg2.connect(user = "odoo",
                                  password = "jack123$",
                                  host = "mdgtest.ctwxzwpgho6b.ap-southeast-1.rds.amazonaws.com",
                                  port = "5432",
                                  database = "mdg_uat")

    cursor = connection.cursor()
    # Print PostgreSQL Connection properties
    print ( connection.get_dsn_parameters(),"\n")

    # Print PostgreSQL version
    cursor.execute("SELECT version();")
    record = cursor.fetchone()
    print("You are connected to - ", record,"\n")
    
#     insert_products(cursor)
#     insert_customers(cursor)
#    insert_promotions(cursor)
    insert_product_pricelists(cursor)
    insert_sale_plan_day(cursor)
    insert_sale_plan_trip(cursor)
    insert_partner_category(cursor)
    insert_product_category(cursor)

except (Exception, psycopg2.Error) as error :
    print ("Error while connecting to PostgreSQL", error)
finally:
    #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")            
