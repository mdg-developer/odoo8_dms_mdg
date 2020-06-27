from decimal import Decimal
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate('/tmp/json/tabletsales-1373-firebase-adminsdk-12xpb-9cafccb3de.json')
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
     
    query = """select  pp.id,pt.list_price,coalesce(replace(pt.description,',',';'), ' ') as description,pt.categ_id,pc.name as categ_name,pp.default_code, 
            pt.name,convert_from(image_small,'utf8') as image_small,pt.main_group,pt.uom_ratio,
            pp.product_tmpl_id,pt.is_foc,pp.sequence,pt.type,pt.uom_id,ccs.id team_id,
            concat(pp.id,'-',ccs.id,'-',rel.sale_group_id)::character varying product_key
            from product_sale_group_rel rel ,
            crm_case_section ccs ,product_template pt, product_product pp , product_category pc
            where pp.id = rel.product_id
            and pt.id = pp.product_tmpl_id
            and pt.active = true
            and pp.active = true
            and ccs.sale_group_id = rel.sale_group_id
            and pc.id = pt.categ_id"""
    cr.execute(query)
    resultMap = dictfetchall(cr)
    print ('ready to insert product')
    for row in resultMap:
        node = str(row['id'])
        print ('product node',node)
        print ('product name',row['name'])
        doc_ref = db.collection('product_product').document(node)
        doc_ref.set(row)        
    print ('inserted product')
    return True

def insert_customers(cr):
    
    firebase_admin.get_app()        
    db = firestore.client()
     
    query = """select A.id,A.name,A.image,A.is_company, A.image_small,replace(A.street,',',';') street, replace(A.street2,',',';') street2,A.city,A.website,
                replace(A.phone,',',';') phone,A.township, replace(A.mobile,',',';') mobile,A.email,A.company_id,A.customer, 
                A.customer_code,A.mobile_customer,A.shop_name ,
                A.address,
                A.zip,A.state_name,A.partner_latitude,A.partner_longitude,A.sale_plan_day_id,A.image_medium,
                A.image_one,A.image_two,A.image_three,A.image_four,A.image_five,A.credit_limit,
                A.credit_allow,A.sales_channel,A.branch_id,A.pricelist_id,A.payment_term_id,A.outlet_type ,
                A.city_id,A.township_id,A.country_id,A.state_id,A.unit,A.class_id,A.chiller,A.frequency_id,A.temp_customer,
                A.is_consignment,A.hamper,A.is_bank,A.is_cheque,A.sale_team team_id,customer_tags
                from (
                select RP.id,RP.name,'' as image,RP.is_company,RPS.line_id as sale_plan_day_id,
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
        node = str(row['id'])
        print ('customer node',node)
        print ('customer name',row['name'])
        doc_ref = db.collection('res_partner').document(node)
        doc_ref.set(row)        
    print ('inserted customers')
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
    print ('ready to insert promotions')
    for row in resultMap:
        node = str(row['id'])
        print ('promotion node',node)
        print ('promotion name',row['p_name'])
        doc_ref = db.collection('promos_rules').document(node)
        doc_ref.set(row)        
    print ('inserted promotions')
    return True
    
import psycopg2
try:
    connection = psycopg2.connect(user = "odoo",
                                  password = "jack123$",
                                  host = "mdgtest.ctwxzwpgho6b.ap-southeast-1.rds.amazonaws.com",
                                  port = "5432",
                                  database = "mdg_testing_new")

    cursor = connection.cursor()
    # Print PostgreSQL Connection properties
    print ( connection.get_dsn_parameters(),"\n")

    # Print PostgreSQL version
    cursor.execute("SELECT version();")
    record = cursor.fetchone()
    print("You are connected to - ", record,"\n")
    
#     insert_products(cursor)
#     insert_customers(cursor)
    insert_promotions(cursor)

except (Exception, psycopg2.Error) as error :
    print ("Error while connecting to PostgreSQL", error)
finally:
    #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")            
