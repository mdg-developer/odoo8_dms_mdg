#from firebase import firebase
from firebase.firebase import FirebaseApplication, FirebaseAuthentication
from openerp import models, fields, api
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

class product_product(models.Model):
    _inherit = 'product.product' 
    
    def sync_cloud_filestore(self):
        cred = credentials.Certificate('/opt/odoo/customs/custom_addons_new/firebase_cloud_filestore_sync/json/tabletsales-1373-firebase-adminsdk-12xpb-9cafccb3de.json')
        firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        
        #get product
        self._cr.execute("""select  pp.id,pt.list_price,coalesce(replace(pt.description,',',';'), ' ') as description,pt.categ_id,pc.name as categ_name,pp.default_code, 
            pt.name,substring(replace(cast(pt.image_small as text),'/',''),1,5) as image_small,pt.main_group,pt.uom_ratio,
            pp.product_tmpl_id,pt.is_foc,pp.sequence,pt.type,pt.uom_id,ccs.id section_id
            from product_sale_group_rel rel ,
            crm_case_section ccs ,product_template pt, product_product pp , product_category pc
            where pp.id = rel.product_id
            and pt.id = pp.product_tmpl_id
            and pt.active = true
            and pp.active = true
            and ccs.sale_group_id = rel.sale_group_id
            and pc.id = pt.categ_id""")
        for row in self._cr.dictfetchall():
            node = 'product_product_id_' + str(row['id'])
            doc_ref = db.collection('product_product').document(node)
            doc_ref.set(row)
        
        #get uom
        self._cr.execute("""select distinct uom_id,uom_name,ratio,template_id,product_id from(
                    select  pu.id as uom_id,pu.name as uom_name ,floor(round(1/factor,2)) as ratio,
                    pur.product_template_id as template_id,pp.id as product_id,ccs.id as section_id
                    from product_uom pu , product_template_product_uom_rel pur ,
                    product_product pp,
                    product_sale_group_rel rel,crm_case_section ccs
                    where pp.product_tmpl_id = pur.product_template_id
                    and rel.product_id = pp.id
                    and pu.id = pur.product_uom_id
                    and rel.sale_group_id=ccs.sale_group_id)A""")
        for row in self._cr.dictfetchall():
            node = 'uom_uom_id_' + str(row['uom_id'])
            doc_ref = db.collection('uom_uom').document(node)
            doc_ref.set(row)  
            
        #get customers
        self._cr.execute("""select A.id,A.name,A.image,A.is_company, A.image_small,replace(A.street,',',';') street, replace(A.street2,',',';') street2,A.city,A.website,
                            replace(A.phone,',',';') phone,A.township, replace(A.mobile,',',';') mobile,A.email,A.company_id,A.customer, 
                            A.customer_code,A.mobile_customer,A.shop_name ,
                            A.address,
                            A.zip,A.state_name,A.partner_latitude,A.partner_longitude,A.sale_plan_day_id,A.image_medium,A.credit_limit,
                            A.credit_allow,A.sales_channel,A.branch_id,A.pricelist_id,A.payment_term_id,A.outlet_type ,
                            A.city_id,A.township_id,A.country_id,A.state_id,A.unit,A.class_id,A.chiller,A.frequency_id,A.temp_customer,
                            A.is_consignment,A.hamper,A.is_bank,A.is_cheque
                            from (
                            select RP.id,RP.name,'' as image,RP.is_company,RPS.line_id as sale_plan_day_id,
                            '' as image_small,RP.street,RP.street2,RC.name as city,RP.website,
                            RP.phone,RT.name as township,RP.mobile,RP.email,RP.company_id,RP.customer, 
                            RP.customer_code,RP.mobile_customer,OT.name as shop_name,RP.address,RP.zip ,RP.partner_latitude,RP.partner_longitude,RS.name as state_name,
                            substring(replace(cast(RP.image_medium as text),'/',''),1,5) as image_medium,RP.credit_limit,RP.credit_allow,
                            RP.sales_channel,RP.branch_id,RP.pricelist_id,RP.payment_term_id,RP.outlet_type,RP.city as city_id,RP.township as township_id,
                            RP.country_id,RP.state_id,RP.unit,RP.class_id,RP.chiller,RP.frequency_id,RP.temp_customer,RP.is_consignment,RP.hamper,
                            RP.is_bank,RP.is_cheque
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
            node = 'res_partner_id_' + str(row['id'])
            doc_ref = db.collection('res_partner').document(node)
            doc_ref.set(row)                
